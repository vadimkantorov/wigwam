class readline(Wig):
	tarball_uri = 'ftp://ftp.cwru.edu/pub/bash/readline-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v6.3'

	def setup(self):
		self.configure_flags += ['--disable-shared']
		self.before_configure += [S.export(S.CFLAGS, '-fPIC')]
		self.before_make += [S.export(S.CFLAGS, '-fPIC')]
