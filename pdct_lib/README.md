
## Files Description  
  
1. **pdct_config.h.in:**
   This file is a configuration template for the pdct project. It defines version numbers, project name, and some platform-specific settings.

2. **log_config.h.in:**
   Similar to pdct_config.h.in, this file is a configuration template specifically for logging settings in the project.

3. **CMakeLists.txt:**
   This is the main CMake configuration file for the project. Here's a summary of what it does:

   - It sets the minimum required CMake version to 2.6.
   - It defines the project name as "pdct."
   - It defines various options such as debugging, release, and logging options.
   - It sets the version numbers for the project.
   - It configures hardware-related settings such as SSE and threading.
   - It sets compiler flags for different build types (Debug, Release, RelWithDebInfo).
   - It checks for the existence of certain libraries (pthread, asound) using CMake's `CHECK_LIBRARY_EXISTS` macro.
   - It finds and includes the wxWidgets library.
   - It configures header files (`pdct_config.h` and `log_config.h`) using the corresponding template files.
   - It includes directories and subdirectories for building the project.
   - It creates an executable named "pdct" and links it with various libraries.
   - It sets up installation targets and packaging information for CPack.
   - It defines custom targets for cleaning CMake files and cleaning all.

The CMakeLists.txt file essentially provides instructions to CMake on how to generate the build files, compile the project, and install the resulting executable.

## Build Instructions

To build and compile the application, follow these steps:

1. Open a terminal and navigate to the project directory:
   ```sh
   $ cd pdct_lib
   ```

2. Create a 'build' directory:
   ```sh
   $ mkdir build
   ```

3. Move into the 'build' directory:
   ```sh
   $ cd build
   ```

4. Run CMake to configure the build:
   ```sh
   $ cmake ..
   ```

5. Compile the project using 'make':
   ```sh
   $ make
   ```

## Running the Application

Once built, you can run the application with the following commands:

1. Move to the 'build' directory:
   ```sh
   $ cd build
   ```

2. Execute the application:
   ```sh
   $ ./pdct
   ```

