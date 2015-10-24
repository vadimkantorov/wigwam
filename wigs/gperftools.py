class gperftools(Wig):
	tarball_uri = 'https://github.com/gperftools/gperftools/releases/download/gperftools-$RELEASE_VERSION$/gperftools-$RELEASE_VERSION$.tar.gz'
	git_uri = 'https://github.com/gperftools/gperftools'
	last_release_version = 'v2.4'
	dependencies = ['libunwind']
