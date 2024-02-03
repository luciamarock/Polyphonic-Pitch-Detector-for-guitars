
objects = tinyxml2.o main.o PolyphonicDetection.o fft_funct.o resonators.o streamer.o envFollower.o filters.o audioPlayer.o LogicPiano.o freqMatch.o
INCL = ../include/

# -I (path)
LDFLAGS = -L.

    UNAME_S := $(shell uname -s)

    ifeq ($(UNAME_S),Linux)
        LFLAGS += -L../lib/linux
    endif
    ifeq ($(UNAME_S),Darwin)
        LFLAGS += -L../lib/mac
    endif

# Add -std=c++11 to enable C++11 support
CXXFLAGS = -std=c++11

PitchDetector : $(objects)
	gcc -g -o PitchDetector $(objects) -lm -lsndfile -lstdc++ $(LDFLAGS) -lportaudio -lpthread
	mv *.o obj/

main.o : $(INCL)streamer.h $(INCL)resonators.h $(INCL)fft_funct.h
	g++ $(CXXFLAGS) -c -o main.o main.cpp

PolyphonicDetection.o : $(INCL)streamer.h $(INCL)resonators.h $(INCL)fft_funct.h $(INCL)tinyxml2.h $(INCL)LogicPiano.h $(INCL)freqMatch.h

fft_funct.o : $(INCL)fft_funct.h

resonators.o : $(INCL)resonators.h 

filters.o : $(INCL)filters.h 

streamer.o : $(INCL)streamer.h 

envFollower.o : $(INCL)envFollower.h

tinyxml2.o : $(INCL)tinyxml2.h

audioPlayer.o : $(INCL)audioPlayer.h

LogicPiano.o : $(INCL)LogicPiano.h 

freqMatch.o : $(INCL)freqMatch.h 

run:
#	./PitchDetector  ../../audioFiles/piano/songs/Beat_It_cut.wav ../../midiFiles/BeatIt.xml 0
	./PitchDetector /home/luciamarock/Documents/AudioAnalyzer/audioFiles/Prs/F175.wav ../../midiFiles/BeatIt.xml 0

.PHONY : clean 

clean:
	rm *.out PitchDetector obj/*

