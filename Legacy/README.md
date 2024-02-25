## README.md

This project investigates the use of a combination of two vectors, `dataRTFI` and `logic_final`, for melody detection. The goal is to find logical conditions that can be used to reliably detect notes in a musical signal.

### Current Status

1. The C++ and Python logic classes produce identical results.
2. The prints from `logic_main` are identical to those from `study_poly` (function `process`) for both `dataRTFI` and `logic_final` (which is equivalent to `weights_current`).

### Next Steps

1. Use expected notes, plotting capabilities, and the following clues to find good logical conditions for detecting results:
    - A good combination of the two vectors under investigation may provide good detection output.
2. Investigate solutions to the following problems:
    - Spectral matching tends to concentrate around peaks, neglecting other existing notes.
    - Melodic notes can be misinterpreted as third harmonics of non-existent fundamentals and given energy through the simple averaging process (fft_simple_avg).
    - The scoring mechanism fails for more than 3 notes to be detected, and it is necessary to rely on RTFI again (pink peaks of existing notes are lower than peaks of harmonics, this does not happen in RTFI).

### Potential Solutions

1. Separation based on registers (e.g., for very high notes, find the change point).
2. Use memory and its inverse, exist and its inverse, and existsum to discriminate between mono and poly.
3. Use bluemax to set a threshold (a very crude solution).

### Further Work

1. Implement and test the proposed solutions.
2. Evaluate the performance of the system using a variety of musical signals.
3. Explore other methods for melody detection and compare their performance to the proposed approach.

