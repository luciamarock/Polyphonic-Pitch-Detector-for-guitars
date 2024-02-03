
#include "../include/PolyphonicDetection.h"
#include <math.h>
#include <string.h>
#include <sstream>
#include <stdio.h>
#include <algorithm>
#include <stdlib.h>
#include <unistd.h>
#include <thread>
#include "../include/consts.h"
#include "../include/streamer.h"
#include "../include/fft_funct.h"
#include "../include/envFollower.h"
#include "../include/filters.h"
#include "../include/PolyphonicDetection.h"
#include "../include/freqMatch.h"
using namespace std;
using namespace tinyxml2;


void sub_timespec(struct timespec t1, struct timespec t2, struct timespec *td)
{
    td->tv_nsec = t2.tv_nsec - t1.tv_nsec;
    td->tv_sec  = t2.tv_sec - t1.tv_sec;
    if (td->tv_sec > 0 && td->tv_nsec < 0)
    {
        td->tv_nsec += BILLION;
        td->tv_sec--;
    }
    else if (td->tv_sec < 0 && td->tv_nsec > 0)
    {
        td->tv_nsec -= BILLION;
        td->tv_sec++;
    }
}

int MidiEvent::ticksPerBeat = 0;
std::vector<MidiEvent> MidiEvent::tempoEvent;

MidiEvent::MidiEvent(unsigned int value, unsigned int absolute, unsigned int trackNum)
 : m_value(value), m_absolute(absolute),m_trackNum(trackNum)
{
//    printf(" m_value: \%d absolute:\%d m_trackNum:\%d \n",m_value,m_absolute,m_trackNum);
}

float MidiEvent::getTimestamp()  {
    float totalTime = 0;
    for (int i = 0 ; i < tempoEvent.size(); i++ )
    {
        float timestamp = (float(SECONDS) / (float(TEMPO_CONST) / tempoEvent[i].getValue())) / float(ticksPerBeat);
        int currentAbs = tempoEvent[i].getAbsolute();
        if (i + 1 < tempoEvent.size()  && currentAbs <= m_absolute) {
            int nextAbs = tempoEvent[i+1].getAbsolute();
            if ( nextAbs <= m_absolute) {
                totalTime += (nextAbs-currentAbs) * timestamp;
            }
            else if (i > 0 && m_absolute > currentAbs) {
                totalTime += (m_absolute-currentAbs) * timestamp;
            }
        }
        else if (totalTime == 0)  {
            totalTime = m_absolute * timestamp;
        }
    }
    return totalTime;
}

ExpectedNote::ExpectedNote(unsigned int value, unsigned int velocity, unsigned int absolute, unsigned int trackNum)
:MidiEvent(value,absolute,trackNum),m_velocity(velocity)
{
}



PolyphonicDetection::PolyphonicDetection(int frames, int samplerate, int channels, std::string filePath, std::string midiPath, std::string FFTs_DB_path, float speed, bool strictMode) : matcher(FFTs_DB_path) {
    
    scaling = SCALING;
    memset( dataRTFI, 0, NNOTES*sizeof(float) );
    memset( dataFFT, 0, NHARMS*sizeof(float) );
    m_FilePath = filePath;
    m_MidiPath = midiPath;
    m_frames = frames;
    m_samplerate = samplerate;
    m_channels = channels;
    m_begin_time.tv_sec = 0;
    m_speed = speed;
    m_strictMode = strictMode;
    m_handsMode = 0;
    m_rangeStart = 0;
    m_performance = 0;
    m_rangeEnd = NNOTES;
    clearExpectedNotes();
    m_expectedNotesCount = 0;
    m_detectedNotesCount = 0;
    if (matcher.loadDatabase()) {
        //printf("Loaded Database \n");
    } else {
        printf("Database not found \n");
    }
}

void PolyphonicDetection::init(unsigned int handsMode) {
    m_handsMode = handsMode;
    //printf("frames %d samplerate: %d channels: %d m_speed: %f strictMode %d handsMode : %d\n",m_frames,m_samplerate,m_channels,m_speed,m_strictMode,m_handsMode);
    
#if WRITE_TO_FILE
    if (!m_FilePath.empty()) {
        std::string str1 = m_FilePath+"/integer.out";
        std::string str2 = m_FilePath+"/monodet.out";

        integral = fopen(str1.c_str(),"w");
        monodet = fopen(str2.c_str(),"w");
    }
#endif
#if SAVE_INPUT_TO_FILE
    if (!m_FilePath.empty()) {
        std::string str3 = m_FilePath+"/input_file.out";
        input_file = fopen(str3.c_str(),"w");
    }
#endif
    loadMidi();
    /** coefficients is a tuple returned by the init function of resonators.cpp
     * the tuple contains 3 coefficents for calculating the RTFI resonators and the list
     * of notes which are the center frequency of the resonators */
    coefficents.init(m_samplerate);
}

void PolyphonicDetection::setSampleRate(int samplerate) {
    m_samplerate = samplerate;
    coefficents.init(m_samplerate);
}

bool compareNotes(ExpectedNote note1, ExpectedNote note2)
{
    return (note1.getAbsolute() < note2.getAbsolute());
}

void PolyphonicDetection::loadMidi() {
    // loading an XML document from the specified MIDI file path using the tinyxml2 library
    xmlDocument.LoadFile( m_MidiPath.c_str());
    // retrieving the root element of the XML document, which is expected to be named "MIDIFile"
    XMLElement* pRoot =  xmlDocument.FirstChildElement("MIDIFile");
    if (pRoot == NULL) {
        printf("----- Failed loadMidi ------ input file: %s\n",m_MidiPath.c_str());

        return;
    }
    // extracting  the ticks per beat value from the MIDI file if root is not NULL
    XMLElement* pTicksPerBeat = pRoot->FirstChildElement("TicksPerBeat");
    pTicksPerBeat->QueryIntText(&ExpectedNote::ticksPerBeat);
    // retrieving and iterating over the tracks in the MIDI file
    XMLElement* track = pRoot->FirstChildElement("Track");
    int trackId = 0;

    while(track)
    {
        track->QueryIntAttribute("Number",&trackId);
        XMLElement* event =  track->FirstChildElement( "Event" );
        int absoluteVal = 0;
        // For each track, iterating over the events and processing them
        while(event)
        {
            XMLElement* absolute =  event->FirstChildElement( "Absolute" );
            absolute->QueryIntText(&absoluteVal);
            XMLElement* noteOn =  event->FirstChildElement( "NoteOn" );
            XMLElement* noteOff =  event->FirstChildElement( "NoteOff" );
            // Within each event, checking for various types of events such as "NoteOn", "NoteOff", and "SetTempo". 
            // For "NoteOn" and "NoteOff" events, extracting the note value, velocity, and absolute timestamp
            if (noteOn || noteOff) {
                int note = 0;
                XMLElement* pNoteEvent = noteOn ? noteOn : noteOff;
                pNoteEvent->QueryIntAttribute("Note",&note);
                int velocity = 0;
                pNoteEvent->QueryIntAttribute("Velocity",&velocity);
                ExpectedNote expectedNote(note,velocity,absoluteVal,trackId);
                if (noteOn && velocity > 0 ) {
                    m_NotesOnVec.push_back(expectedNote);
                }
                else {
                    m_NotesOffVec.push_back(expectedNote);
                }
            }
            // For "SetTempo" events, extracting the tempo value and storing it for later use in timestamp calculations
            else  {
                XMLElement* tempoElement =  event->FirstChildElement( "SetTempo" );
                if (tempoElement) {
                    int tempo;
                    tempoElement->QueryIntAttribute("Value",&tempo);
                    MidiEvent::tempoEvent.push_back(MidiEvent(tempo,absoluteVal,0));
                }
            }
            event = event->NextSiblingElement("Event");
        }
        track = track->NextSiblingElement("Track");
    }
    // sorting the m_NotesOnVec and m_NotesOffVec vectors based on their timestamps
    sort(m_NotesOnVec.begin(), m_NotesOnVec.end(), compareNotes);
    sort(m_NotesOffVec.begin(), m_NotesOffVec.end(), compareNotes);
//    vector<ExpectedNote>::iterator it;
//    for (it = m_NotesOnVec.begin(); it < m_NotesOnVec.end(); it++) {
//        printf("Note On : %d absolute:%d time: %f\n", it->getValue(),it->getAbsolute(), it->getTimestamp());
//    }
//    for (it = m_NotesOffVec.begin(); it < m_NotesOffVec.end(); it++) {
//        printf("Note Off : %d absolute:%d time: %f\n", it->getValue(),it->getAbsolute(), it->getTimestamp());
//    }
//    for (auto x : m_NotesOffVec)
//        printf("Note Off : %d absolute:%d time: %f\n", x.getValue(),x.getAbsolute(), x.getTimestamp());

}


PolyphonicDetection::~PolyphonicDetection() {
#if WRITE_TO_FILE
    if (!m_FilePath.empty()) {
        fclose(monodet);
        fclose(integral);
    }
#endif
#if SAVE_INPUT_TO_FILE
    if (!m_FilePath.empty()) {
        fclose(input_file);
    }
#endif
}


float PolyphonicDetection::allowance = 0.0;
float PolyphonicDetection::envprev = integer_threshold;

int PolyphonicDetection::counter = 0;

void PolyphonicDetection::onNoteOn(const ExpectedNote& noteOn) {
    int found = 0;
    for (int i = 0 ; i < MAX_EXPECTED ; i++)
    {
        if (m_expectedNotes[i] == noteOn.getValue())
        {
            found = m_expectedNotes[i];
            break;
        }
    }
    if (!found) {
        m_expectedNotesCount++;
        for (int i = 0 ; i < MAX_EXPECTED ; i++)
        {
            if (m_expectedNotes[i] == 0)
            {
                if( m_handsMode == 0 || noteOn.getTrackNum() == m_handsMode  )
                {
                    m_expectedNotes[i] = noteOn.getValue();
#if !(REALTIME)
                    printf("%d \t note %d track %d\n",noteOn.getAbsolute(), noteOn.getValue(),noteOn.getTrackNum());
#endif
                }
                break;
            }
        }
    }
}
    
void PolyphonicDetection::onNoteOff(ExpectedNote& noteOff) {
    for (int i = 0 ; i < MAX_EXPECTED ; i++) {
        if (m_expectedNotes[i] == noteOff.getValue()) {
#if !(REALTIME)
            float song_time = sampvect/float(m_samplerate)*float(counter);

            printf("onNoteOff %d %d %f\n",m_expectedNotes[i],noteOff.getAbsolute(),song_time);
#endif
            m_expectedNotes[i] = 0;
            m_detectedNotesMap.erase(noteOff.getValue());
            break;
        }
    }
}

void PolyphonicDetection::refreshExpected(std::vector<ExpectedNote> newExpected) {
    clearExpectedNotes();
    int i = 0;
    for(vector<ExpectedNote>::const_iterator it = newExpected.begin(); it != newExpected.end(); ++it){
        m_expectedNotes[i] = it->getValue();
        i++;
        if ( i == MAX_EXPECTED) {
            break;
        }
    }
}

void PolyphonicDetection::setSongsNotesRange(int start, int end) {
    if (start > 12) {
        m_rangeStart = start - 12;
    }
    m_rangeEnd = end;
}

double PolyphonicDetection::performance() {
    return m_performance;
}

void PolyphonicDetection::clearExpectedNotes() {
    memset( m_expectedNotes, 0, MAX_EXPECTED*sizeof(int));
}

void PolyphonicDetection::onProcessCallback()
{
    // set buffer size
    float song_time = sampvect/float(m_samplerate)*float(counter);
    if ( m_NotesOnVec.size() > 0 ) {
        if (song_time > m_NotesOnVec.front().getTimestamp()) {
            ExpectedNote event = m_NotesOnVec.front();
            onNoteOn(event);
            
#if !(REALTIME)
            struct timespec  stop;
            clock_gettime( CLOCK_REALTIME, &stop);
            float performance = ((double)stop.tv_sec + 1.0e-9*stop.tv_nsec) -
    ((double)m_begin_time.tv_sec + 1.0e-9*m_begin_time.tv_nsec);

            printf("Expected note: %d at %d %f time :%f\n",event.getValue(),event.getAbsolute(), song_time,performance);
#endif
            m_NotesOnVec.pop_front();
        }
    }
    if ( m_NotesOffVec.size() > 0 ) {
        if (song_time > m_NotesOffVec.front().getTimestamp()) {
            onNoteOff(m_NotesOffVec.front());
            m_NotesOffVec.pop_front();
        }
    }
    //float song_time = float(accum);
    //printf("%f \t per_note %f \n",song_time, m_NotesOnVec.front().getTimestamp());
}

int PolyphonicDetection::process(float * pfCurrentBuff)
    {

     /** Iterating on the input buffer (of dimension 256 samples) in order to build the vectors to be analyzed,
      * the real data are contained in the vector buf which represent the entire audio file; the samples of the buf
      * vector are always scaled by a factor of 2147483648 which is hard-coded \n
      
      Vector myfft_buffer[] is used for the computation of the FFT with my algorithm, it is composed by the last 4 buffers
      * thus bringing the total amount of he vector equal to 1024 samples, so the fft is calculated on this vector. The fft
      * is not really used to find the peaks, in fact we should have a calculation vector of 8192 to discriminate for real the partials
      * at lowest frequencies, but it still can be relied on to find the correct amplitudes to the partials since the RTFIs take time
      * to reflect the real amplitude of the partials. \n
      * Finally integer is used to calculate the envelope of the buffers, it gets printed on a file called integer.out */
#if !(REALTIME)
    if (m_begin_time.tv_sec == 0 ) {
        clock_gettime( CLOCK_REALTIME, &m_begin_time);
    }
#endif

    struct timespec  begin_time;    // this was already here; later on remove the calculations 
    clock_gettime( CLOCK_REALTIME, &begin_time);
    // generating my own structures for working with sub_timespec
    struct timespec end_time, diff_time;

    int a_score[NNOTES] = {0};
    int scounter = 0;

    // populating a_score (the vector to be sent to "evaluation", supports the logic)
    for (int i = 0 ; i < MAX_EXPECTED ; i++) {
        scounter = m_expectedNotes[i];
        if (scounter == 0)
            continue;
        a_score[scounter-index_to_MIDI] = scounter;
    }
    
    // calculating the FFT
    float spectralCentroid = 0.0;
    //fft_funct(pfCurrentBuff, dataFFT, 4*sampvect, tet, f0, NHARMS, m_samplerate  );
    std::thread fftThread(fft_funct, pfCurrentBuff, dataFFT, m_samplerate, &spectralCentroid);
    // calculating the energy
    integer = envelope(pfCurrentBuff);
    
    // calculate filters with customized frequencies 
    float periodicity = 0.0;
    rtfi_calculation(dataRTFI, pfCurrentBuff, scaling, coefficents.a, coefficents.b, coefficents.c, coefficents.d, m_samplerate, &periodicity);
    
    fftThread.join();
    
    std::vector<int> topMatches = matcher.match(coefficents.d, dataFFT);
    
 
    float MOVING_AVARAGE_P = 0.1;
    float ATTACK_FACTOR = 0.6 ;
    if (integer > envprev){
        MOVING_AVARAGE_P = MOVING_AVARAGE_P * ATTACK_FACTOR;
    }
    envprev = MOVING_AVARAGE_P * integer + (1 - MOVING_AVARAGE_P) * envprev;
    attack = integer * integer / envprev;

    if ((attack > attack_threshold) && (integer > integer_threshold))
        allowance = integer; // allowance gets continuously updated 
    
    if (integer < allowance * 0.07){
        allowance  = 0.0;
#if !(REALTIME)
        printf("integer < allowance %d \n",counter);
#endif
    }
    counter ++; 

    memset( a_towrite, 0, NNOTES*sizeof(int) );   // a_towrite is the FINAL output 
    float ratio = periodicity / f0;
    float midi_num = 12 * log2(ratio) + index_to_MIDI;
    int midi_rounded = (int)round(midi_num);
    // insert logic here (move to LogicPiano)
    //logicPiano.processLogic(dataRTFI, dataFFT, allowance, a_score, m_strictMode, a_towrite, midi_rounded, topMatches);

    
   
#if SAVE_INPUT_TO_FILE
    for (int i = 0 ; i < sampvect ; i++) {
        fprintf(input_file,"%f",pfCurrentBuff[i]);
    }
    fflush(input_file);
#endif

#if WRITE_TO_FILE
        if (!m_FilePath.empty()) {
         fprintf(integral,"%f ", allowance); // (integer) allowance, spectralCentroid or (periodicity) midi_rounded
         fprintf(integral,"\n");
         fflush(integral);
        }
#endif

#if WRITE_TO_FILE
        if (!m_FilePath.empty()) {
	  for (int j = 0; j < MAX_EXPECTED ; ++j){   // change between  NHARMS / NNOTES / MAX_EXPECTED
            if (j == MAX_EXPECTED - 1){
            fprintf(monodet,"%d",topMatches[j]); // change between dataFFT / dataRTFI / topMatches
            fprintf(monodet,"\n");
            }
            else{
            fprintf(monodet,"%d",topMatches[j]);  
            fprintf(monodet,"\t");
            }
	  }
         fflush(monodet);
        }
#endif

/*
#if WRITE_TO_FILE
      if (!m_FilePath.empty()) {
	  for (int j = 0; j < NNOTES ; ++j){
            if (j == NNOTES - 1){
                if (a_score[j] > 0){
                   fprintf(integral,"%d",a_score[j]);  
                }
            fprintf(integral,"\n");
            }
            else{
                if (a_score[j] > 0){
                   fprintf(integral,"\t");
                   fprintf(integral,"%d",a_score[j]);  
                }
            }
	  }
         fflush(integral);
        }
#endif
    
    
#if WRITE_TO_FILE
        if (!m_FilePath.empty()) {
	  for (int j = 0; j < NNOTES ; ++j){
            if (j == NNOTES - 1){
                if (a_towrite[j] != 0){
                   fprintf(monodet,"%d",a_towrite[j]);  
                }
            fprintf(monodet,"\n");
            }
            else{
                if (a_towrite[j] != 0){
                   fprintf(monodet,"\t");
                   fprintf(monodet,"%d",a_towrite[j]); 
                }
            }
	  }
         fflush(monodet);
        }
#endif
    */
    memset( a_notesOn, 0, NNOTES*sizeof(int) );
    memset( a_notesOff, 0, NNOTES*sizeof(int) );
    int notesOn[NNOTES];
    memset( notesOn, 0, NNOTES*sizeof(int) );
    
    // Updating m_detectedNotesMap with Detected Notes
    std::map<int,int>::iterator it;
    int count = 0;
    int countOn = 0;
    
    for (int i=0; i<NNOTES; ++i){
        if (a_towrite[i] > 0 )
        {
            notesOn[countOn] = a_towrite[i];
            countOn++;
            it = m_detectedNotesMap.find( a_towrite[i]);
            if (it == m_detectedNotesMap.end()) {
                m_detectedNotesCount++;
                m_detectedNotesMap.insert( std::make_pair( a_towrite[i],a_towrite[i]));
#if !(REALTIME)
                float song_time = sampvect/float(m_samplerate)*float(counter);
                struct timespec  stop;
                clock_gettime( CLOCK_REALTIME, &stop);
                float performance = ((double)stop.tv_sec + 1.0e-9*stop.tv_nsec) -
        ((double)m_begin_time.tv_sec + 1.0e-9*m_begin_time.tv_nsec);

                printf("note on: %d %f %f\n", a_towrite[i],song_time, performance);

#endif
           }
            a_notesOn[count] = a_towrite[i];
            count++;
        }
    }
    int countOff = 0;
    // Removing Notes Not Detected Anymore
    std::vector<int> notesToRemove;
    for (it = m_detectedNotesMap.begin(); it != m_detectedNotesMap.end(); it++) {
        bool found = false;
        for (int i=0; i<countOn; ++i)
        {
            if (notesOn[i] == 0 )
                break;
            
            if( notesOn[i] == it->second )
                found = true;
        }
        if (!found) {
            notesToRemove.push_back(it->second);
            a_notesOff[countOff] = it->second ;
            countOff++;
        }
    }
    clock_gettime(CLOCK_REALTIME, &end_time);
    sub_timespec(begin_time, end_time, &diff_time);
    /*
#if WRITE_TO_FILE
        if (!m_FilePath.empty()) {
         fprintf(integral,"%ld ", diff_time.tv_nsec);
         fprintf(integral,"\n");
         fflush(integral);
        }
#endif
    */
    //printf("Time difference: %ld seconds %ld nanoseconds\n", diff_time.tv_sec, diff_time.tv_nsec);
#if !(REALTIME)
            struct timespec  stop;
            clock_gettime( CLOCK_REALTIME, &stop);
            m_performance = ((double)stop.tv_sec + 1.0e-9*stop.tv_nsec) -
    ((double)begin_time.tv_sec + 1.0e-9*begin_time.tv_nsec);
#endif

        return count;
    }

void PolyphonicDetection::printDetectionResult() {
    printf("finished analysis missed Detect %d out of %d\n" ,m_expectedNotesCount - m_detectedNotesCount,m_expectedNotesCount);
    if (m_expectedNotesCount > 0) {
        float ratio = float(m_detectedNotesCount) / float(m_expectedNotesCount) * 100 ;
        printf("detection ratio  %.2f%%\n" ,ratio);
    }
}
