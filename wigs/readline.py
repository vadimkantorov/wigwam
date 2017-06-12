class readline(Wig):
	tar_uri = 'http://ftp.gnu.org/gnu/readline/readline-{RELEASE_VERSION}.tar.gz'
	last_release_version = '6.3'

	def setup(self):
		self.configure_flags += ['--disable-shared']
		self.before_configure += [S.export(S.CFLAGS, '-fPIC')]
		self.before_make += [S.export(S.CFLAGS, '-fPIC')]
