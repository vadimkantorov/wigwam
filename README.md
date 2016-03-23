# wigwam
A humane dependency fetcher and builder for scientific projects, written in Python.

# Installation
For installation instructions please check http://wigwam.in.

# Commands
 - ```wigwam init``` - initializes an empty ```Wigwamfile```, an empty ```.wigwam``` directory structure in the current directory
 - ```wigwam lint``` - verifies that all mandatory and optional dependencies are explicitly listed in ```Wigwamfile``` and appends the missing ones upon user's wish. Useful after manual modification of ```Wigwamfile``` and modifying feaures of certain libraries and before making the ```Wigwamfile``` public
 - ```wigwam build``` - fetches and builds all dependencies specified in the ```Wigwamfile``` located in the current directory into ```.wigwam```
 - ```wigwam install packagename``` - fetches the package, appends it to the ```Wigwamfile``` located in the current directory and runs build
 - ```wigwam clean``` - cleans ```.wigwam/src``` and ```.wigwam/prefix``` and removes ```.wigwam/download_configure_build.generated.sh```
 - ```wigwam in``` - executes ```.wigwam/wigwam_activate.sh``` and makes available the installed binaries and libraries

# Wigwamfile

# Special files and directories
 - ```Wigwamfile``` - specifies the packages Wigwam will fetch and build
 - ```.wigwam``` - the hidden directory containing all Wigwam artifacts
 - ```wigs``` - where user-provided wigs live
 - ```.wigwam/prefix``` - where all packages binaries get installed
 - ```.wigwam/src``` - where the package source trees get unpacked
 - ```.wigwam/logs``` - where detailed package installation logs go
