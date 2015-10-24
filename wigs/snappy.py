class snappy(Wig):
	tarball_uri = 'http://snappy.googlecode.com/files/snappy-$RELEASE_VERSION$.tar.gz'
	git_uri = 'https://github.com/google/snappy'
	last_release_version = 'v1.1.1'

	def setup(self):
		self.before_make += [S.export('CXXFLAGS', '-fPIC -shared')]
