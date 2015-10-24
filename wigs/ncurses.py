class ncurses(Wig):
	tarball_uri = 'http://ftp.gnu.org/pub/gnu/ncurses/ncurses-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v5.9'

	def setup(self):
		self.before_configure += [S.export(S.CFLAGS, '-fPIC')]
		self.before_make += [S.export(S.CFLAGS, '-fPIC')]
