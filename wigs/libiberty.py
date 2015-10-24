class libiberty(Wig):
	git_uri = 'git://sourceware.org/git/binutils-gdb.git'
	tarball_uri = 'http://ftp.gnu.org/gnu/binutils/binutils-$RELEASE_VERSION$.tar.gz'
	working_directory = 'libiberty'
	last_release_version = 'v2.25'

	def setup(self):
		self.before_configure += [S.export(S.CFLAGS, '-fPIC')]
		self.configure_flags += ['--enable-install-libiberty']
