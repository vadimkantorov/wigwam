# wigwam install 
 - Parsing Wigwamfile.installed should not break if features/config values are not there. Parsing should be light-weight
 - change way of specifyinng version and features, so that quotes are note needed
 - Check wigwam install manen-rp/torch --reinstall

# wigwam upgrade
 - use configure flags / installation snippets in fingerprint, possibly save fingerprint in Wigwamfile.installed
 - right now upgrade does not lead to reinstalling of all dependent libraries, but it should

# wigwam build
 - CMAKE_PREFIX_PATH in wigwam_activate.sh
 - OperationScope for updating Wigwamfile / Wigwamfile.config, instead of passing "old"
 - fixed installation order
 - setup.* writes should be transactional
 - wigwam_activate.m: Should set the env vars + be called in S.matlab
 - wigwam_activate.py
 - wigwam_activate.lua

# Wig API
 - a way to provision a package/feature from another package feature trigger
 - build_dependencies, no_shared, skip_stages
 - wig.SOURCES, URI should be set once
 - checking for other wigs features and version
 - support adding exports to wigwam_activate.sh

# Other
 - gentle terminal reset on CTRL-C. Possible at all? Related to Linux kill signal interception
 - test on python 2.6, 2.7, 3.x
 - loading Wigwamfile.installed should not break if a newly added default feature is not configured properly
 - Wigwamfile should list installed features
 - test protobuf wig
 - if wigwam_activate.sh changed, suggest exiting a wigwam session and entering again to reload wigwam
 - OpenBLAS should depend on gfortran for a static library
 - wigwam should have a command that shows its defined env directories
 - make torch depend on libjpeg8
 - remove v* prefix from versions

# Website
 - add wig package uri to details
 - add wig source uri to details
