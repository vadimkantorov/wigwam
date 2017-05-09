# wigwam install 
 - Parsing Wigwamfile.installed should not break if features/config values are not there. Parsing should be light-weight
 - Check wigwam install manen-rp/torch --reinstall
 - Should not add features that do not exist, even in dry mode
 - Should check sources format
 - Install git automatically, even before a find_last_commit.
 - Pip-wigs should use wigwam-installed pip if available
```
 CUDNN_URL="http://developer.download.nvidia.com/compute/redist/cudnn/v5.1/cudnn-8.0-linux-x64-v5.1.tgz"
wget ${CUDNN_URL}
sudo tar -xzf cudnn-8.0-linux-x64-v5.1.tgz -C /usr/local
```

# wigwam run / in
- should be one method
- For every directory on LIBRARY_PATH: make dummy sub-directory sym-linking $(gcc -print-multi-os-directory, often ../lib64; gcc -print-multiarch, the latter doesn't exist on old gcc) to itself
- export also LD_RUN_PATH (what's the difference with LIBRARY_PATH?)
 
# wigwam upgrade
 - use configure flags / installation snippets in fingerprint, possibly save fingerprint in Wigwamfile.installed
 - right now upgrade does not lead to reinstalling of all dependent libraries, but it should
 - fail gracefully if a wig from Wigwamfile.installed has been removed

# wigwam build
 - OperationScope for updating Wigwamfile / Wigwamfile.config, instead of passing "old"
 - fixed installation order
 - setup.* writes should be transactional
 - Install lua/pip* wigs at last (because we don't know dependencies for them)

# Wig API
 - a way to provision a package/feature from another package feature trigger
 - build_dependencies, no_shared, skip_stages
 - wig.SOURCES, URI should be set once
 - checking for other wigs features and version
 - support adding exports to wigwam_activate.sh
 - support saving options, making them available to other packages if needed

# Other
 - gentle terminal reset on CTRL-C (reproduce by hitting CTRL-C during wig fetch). Possible at all? Related to Linux kill signal interception. Q: how does trap on EXIT works if we do "exit 1" from SIGINT trap? read apparently fails there.
 - test on python 2.6, 2.7, 3.x
 - loading Wigwamfile.installed should not break if a newly added default feature is not configured properly
 - Wigwamfile should list installed features
 - if wigwam_activate.sh changed, suggest exiting a wigwam session and entering again to reload wigwam
 - remove v* prefix from versions
 - when adding symlinks to the library, also add symlink to the actual library (some software will link against the final library, not the symlinked .so)
 
# wigs
 - py-lmdb wig
 - glib wig + ref from pkg-config
 - OpenBLAS should depend on gfortran for a static library
 - install git before doing find_last_git_commit
 - put dependencies for git
 - for opencv support python2 and python3
 - wigwam command should work in bash scripts (aliases break)
