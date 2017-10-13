class snappy(Wig):
	tar_uri = 'https://github.com/google/snappy/releases/download/{VERSION}/snappy-{VERSION}.tar.gz'
	git_uri = 'https://github.com/google/snappy'
	version = '1.1.3'
	before_make = [S.export('CXXFLAGS', '-fPIC -shared')]
