# wigwam install 
 - should fail when a requested feature doesnt exist
 - change way of specifyinng version and features, so that quotes are note needed
 
# wigwam upgrade
 - implement "wigwam upgrade package_name" and "wigwam upgrade" (script to be saved in upgrade.generated.sh)
 - use configure flags / installation snippets in fingerprint, possibly save fingerprint in Wigwamfile.installed

# wigwam build
 - support for setup.m, setup.lua, setup.py
 - OperationScope for updating Wigwamfile / Wigwamfile.config, instead of passing "old"
 - fixed installation order

# Wig API
- a way to provision a package/feature from another package feature trigger
- default_features, build_dependencies, no_shared
- checking for other wigs features

# Other
 - If no wigwam found in current dir, use the global one (in home). Enforce using the global one by using --global for all commands.
 - gentle terminal reset on CTRL-C. Possible at all? Related to Linux kill signal interception
 - test on python 2.6, 2.7, 3.x
 - loading Wigwamfile.installed should not break if a newly added default feature is not configured properly
 - move the website to an orphan branch of this repo
 - add detailed drop-down for every wig on the website
 - Wigwamfile should list installed features
