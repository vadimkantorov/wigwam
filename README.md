# wigwam
A humane dependency fetcher and builder for scientific projects, written in Python.

# Installation
**Prerequisites:** bash, Python 2.7, curl/wget installed and discoverable.

Append to your ```~/.bashrc``` the alias:

```alias wigwam='python <($([ -z "$(which curl)" ] && echo "wget -qO -" || echo "curl -s") https://raw.githubusercontent.com/vadimkantorov/wigwam/master/wigwam.py) --repo https://github.com/vadimkantorov/wigwam/tree/master/wigs'```

Test wigwam by installing Torch with Facebook extensions (requires CUDA and CUDNN):

```wigwam install torch fbtorch -DPATH_TO_CUDNN="/home/kantorov/cudnn-6.5-linux-x64-v2" -DPATH_TO_NVCC="/usr/local/cuda-6.5/bin/nvcc"```

or by installing Caffe:

```wigwam install caffe -DPATH_TO_CUDNN="/home/kantorov/cudnn-6.5-linux-x64-v2" -DPATH_TO_NVCC="/usr/local/cuda-6.5/bin/nvcc"```

# Commands
 - ```wigwam init``` - initializes an empty ```Wigwamfile```, an empty ```.wigwam``` directory structure in the current directory
 - ```wigwam lint``` - verifies that all mandatory and optional dependencies are explicitly listed in ```Wigwamfile``` and appends the missing ones upon user's wish. Useful after manual modification of ```Wigwamfile``` and modifying feaures of certain libraries and before making the ```Wigwamfile``` public
 - ```wigwam build``` - fetches and builds all dependencies specified in the ```Wigwamfile``` located in the current directory into ```.wigwam```
 - ```wigwam install packagename``` - fetches the package, appends it to the ```Wigwamfile``` located in the current directory and runs build
 - ```wigwam clean``` - cleans ```.wigwam/src``` and ```.wigwam/prefix``` and removes ```.wigwam/download_configure_build.generated.sh```
 - ```wigwam enter``` - executes ```.wigwam/setup.sh``` and makes available the installed binaries and libraries

# Wigwamfile

# Special files and directories
 - ```Wigwamfile``` - specifies the packages Wigwam will fetch and build
 - ```.wigwam``` - the hidden directory containing all Wigwam artifacts
 - ```wigs``` - where user-provided wigs live
 - ```.wigwam/prefix``` - where all packages binaries get installed
 - ```.wigwam/src``` - where the package source trees get unpacked
 - ```.wigwam/logs``` - where detailed package installation logs go
 - ```.wigwam/build.generated.sh``` - the generated script that downloads, unpacks, configures, makes and make installs the packages
 - ```.wigwam/setup.sh```- the generated script that modifies PATH, LD_LIBRARY_PATH, PYTHONPATH, MATLABPATH, LUA_PATH environment variables making the packages and their Python, Matlab, Lua extensions discoverable
 
# Wigs
Python-scripts that contain the know-how about downloading, configuring and building a package.

# Enjoy!

![KAIVOPUISTO. Copyright by BENJAMIN SUOMELA](http://www.helsinkistreet.fi/wp-content/uploads/2014/05/Benjamin-Suomela-Kaivopuist.jpg)
