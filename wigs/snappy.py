class snappy(Wig):
	tar_uri = 'https://github.com/google/snappy/releases/download/{version}/snappy-{version}.tar.gz'
	git_uri = 'https://github.com/google/snappy'
	version = '1.1.3'
	before_buld = [S.export('CXXFLAGS', ' '.join([S.FPIC_FLAG, S.SHARED_FLAG]))]
