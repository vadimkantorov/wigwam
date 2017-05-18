# wigwam
A humane dependency fetcher and builder for scientific projects, written in Python.

# Installation
For installation instructions please check http://wigwam.in.

# Commands
 - `wigwam install packagename` - fetches the package, appends it to the `Wigwamfile` located in the current directory and runs build
  * `wigwam install packagename --disable feature1 feature2 --git development` - forces install from git branch `development` with disabled `feature1` and `feature2`
 - `wigwam in` - executes `.wigwam/wigwam_activate.sh` and makes available the installed binaries and libraries
 - `wigwam run python``` - executes a command from within wigwam, without creating an interactive sub-shell
 - `wigwam build` - fetches and builds all dependencies specified in the `Wigwamfile`
 - `wigwam status` - lists installed packages
 - `wigwam remove packagename --dangerous` - removes ONLY the reference from `Wigwamfile`
 - `wigwam clean` - removes all installed packages
 - `wigwam which`- prints the path to `.wigwam` directory
 
# Updating wig list on the website
```shell
git clone https://github.com/vadimkantorov/wigwam --branch gh-pages wigwam_site_update && cd wigwam_site_update && wigwam search --json > _data/wigs.json && git commit -a -m 'Update wigs.json by "wigwam search --json"' && git push && cd .. || rm -rf wigwam_site_update
```

# License
MIT
