# wigwam install 
 - Parsing Wigwamfile.installed should not break if features/config values are not there. Parsing should be light-weight
 - change way of specifyinng version and features, so that quotes are note needed
 - Check wigwam install manen-rp --reinstall
 
# wigwam upgrade
 - implement "wigwam upgrade package_name" and "wigwam upgrade" (script to be saved in upgrade.generated.sh)
 - use configure flags / installation snippets in fingerprint, possibly save fingerprint in Wigwamfile.installed

# wigwam build
 - OperationScope for updating Wigwamfile / Wigwamfile.config, instead of passing "old"
 - fixed installation order
 - setup.* writes should be transactional
 - wigwam_activate.m: Should set the env vars + be called in S.matlab
 - wigwam_activate.py
 - wigwam_activate.lua

# Wig API
- a way to provision a package/feature from another package feature trigger
- build_dependencies, no_shared
- checking for other wigs features

# Other
 - gentle terminal reset on CTRL-C. Possible at all? Related to Linux kill signal interception
 - test on python 2.6, 2.7, 3.x
 - loading Wigwamfile.installed should not break if a newly added default feature is not configured properly
 - Wigwamfile should list installed features
 - test protobuf wig
 - if wigwam_activate.sh changed, suggest exiting a wigwam session and entering again to reload wigwam
 - OpenBLAS should depend on gfortran for a static library
 - wigwam should have a command that shows its defined env directories
 - add a verbose mode that prints executed bash script

# Website
 - add wig package uri to details
 - add wig source uri to details
