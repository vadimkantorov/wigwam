class gperftools(Wig):
	tar_uri = 'https://github.com/gperftools/gperftools/releases/download/gperftools-{version}/gperftools-{version}.tar.gz'
	git_uri = 'https://github.com/gperftools/gperftools'
	version = '2.4'
	dependencies = ['libunwind']
