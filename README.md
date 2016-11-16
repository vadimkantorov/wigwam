# wigwam
A humane dependency fetcher and builder for scientific projects, written in Python.

# Installation
For installation instructions please check http://wigwam.in.

# Commands
 - ```wigwam install packagename``` - fetches the package, appends it to the ```Wigwamfile``` located in the current directory and runs build
 - ```wigwam in``` - executes ```.wigwam/wigwam_activate.sh``` and makes available the installed binaries and libraries
 - ```wigwam build``` - fetches and builds all dependencies specified in the ```Wigwamfile```
 - ```wigwam clean```
 - ```wigwam init```
 
# Updating wig list on the website
```bash
git clone https://github.com/vadimkantorov/wigwam --branch gh-pages wigwam_site_update && cd wigwam_site_update && wigwam search --json > _data/wigs.json && git commit -a -m 'Update wigs.json by "wigwam search --json"' && git push && cd .. && rm -rf wigwam_site_update
```
