class snappy(Wig):
	tar_uri = 'https://github.com/google/snappy/releases/download/{RELEASE_VERSION}/snappy-{RELEASE_VERSION}.tar.gz'
	git_uri = 'https://github.com/google/snappy'
	last_release_version = '1.1.3'

	def setup(self):
		self.before_make += [S.export('CXXFLAGS', '-fPIC -shared')]
