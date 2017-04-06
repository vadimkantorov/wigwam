class ncurses(Wig):
	tarball_uri = 'http://ftp.gnu.org/pub/gnu/ncurses/ncurses-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v6.0'

	def setup(self):
		self.configure_flags += ['--enable-overwrite']
		self.before_configure += [S.export(S.CFLAGS, '-fPIC'), S.export(S.CPPFLAGS, '-P')]
		self.before_make += [S.export(S.CFLAGS, '-fPIC')]
