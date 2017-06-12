class gperftools(Wig):
	tar_uri = 'https://github.com/gperftools/gperftools/releases/download/gperftools-{RELEASE_VERSION}/gperftools-{RELEASE_VERSION}.tar.gz'
	git_uri = 'https://github.com/gperftools/gperftools'
	last_release_version = '2.4'
	dependencies = ['libunwind']
