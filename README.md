# Polyphonic Pitch Detector for Guitars

This repository hosts a pitch detection application designed for Linux systems, specifically tailored for guitar input. The underlying methodology is based on complex resonators and is optimized for accurate pitch estimation. The theoretical foundation of complex resonators can be found in the article titled "A Computationally Efficient Method for Polyphonic Pitch Estimation" authored by Ruohua Zhou, Joshua D. Reiss, Marco Mattavelli, and Giorgio Zoia.

The system is currently in a developmental phase to incorporate frequency domain effects as demonstrated on the page ["My Project Showcase"](http://lushmaroon.altervista.org/my-project.html?cb=1495296000881).  
  
## About the Algorithm

The Polyphonic Pitch Detection algorithm was developed in collaboration with Benti SA and REDS (Reconfigurable Embedded Systems) in Yverdon-les-Bains, Switzerland. This algorithm boasts remarkable efficiency in detecting polyphonic pitches for guitar sounds.

The algorithm achieves an average latency of approximately 10 ms, even for lower frequencies. This impressive speed is achieved through a novel approach to analysis that is currently undergoing patent application.

The innovation lies in a combined frequency and time domain analysis approach. The time domain analysis leverages the physical properties of vibrating guitar strings to recognize specific features of the incoming signal. A robust logical algorithm then deduces the pitch of incoming notes, even with less than a full wave period.

This algorithm is lightweight enough to run on devices like a Raspberry Pi. It can convert real-time audio input into MIDI sequences with an error possibility of just 0.7% in a 10 ms latency window. By extending the latency to 16 ms, the error potential decreases significantly, approaching 0%.

The versatility of this algorithm opens up numerous musical applications. One prominent use case involves extracting note information from incoming sound to apply real-time signal processing techniques. These techniques can manipulate the spectral content of the sound without any perceivable latency, enhancing the expressive connection between musician and instrument.

The repository aims to make this innovative algorithm accessible and has the potential to reshape sound possibilities, making the dream of creating unique and distinctive guitar sounds a reality. The system's compact form factor allows for interaction with smartphones and online communities, ushering in new realms of sonic exploration.

For a visual demonstration of the algorithm controlling external synthesizers, [watch this video](https://www.youtube.com/watch?v=R00SUzQEruI&ab_channel=Lu%C3%A7ianodelosCimarrones).

A C++ version of the algorithm is currently being prepared and is available within this GitHub repository. Stay tuned for updates! For the latest news, visit [my Telegram channel](https://t.me/luciamarockmood).
