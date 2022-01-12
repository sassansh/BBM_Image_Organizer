# BBM_Image_Organizer

Python script to analyze and sort Beaty Biodiversity Museum's pictures of animals.

# Setup Instructions

1. Based on you system architecture install Conda.

   Recommended: https://github.com/conda-forge/miniforge
   | OS | Architecture | Download |
   | --------|-----------------------|-----------|
   | Linux | x86_64 (amd64) | [Miniforge3-Linux-x86_64](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh) |
   | Linux | aarch64 (arm64) | [Miniforge3-Linux-aarch64](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-aarch64.sh) |
   | Linux | ppc64le (POWER8/9) | [Miniforge3-Linux-ppc64le](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-ppc64le.sh) |
   | OS X | x86_64 | [Miniforge3-MacOSX-x86_64](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-x86_64.sh) |
   | OS X | arm64 (Apple Silicon) | [Miniforge3-MacOSX-arm64](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh) |
   | Windows | x86_64 | [Miniforge3-Windows-x86_64](https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe) |

2. Create an environment by

   ```
   conda env create -f beaty_env.yml
   ```

3. Activate the environment with
   ```
   conda activate beaty
   ```
   After a successful activation, something like `(beaty)` should show up in the terminal.
