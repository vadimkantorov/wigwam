class lz4(Wig):
	tarball_uri = 'https://github.com/Cyan4973/lz4/archive/r$RELEASE_VERSION$.tar.gz'
	git_uri = 'https://github.com/Cyan4973/lz4'
	last_release_version = 'v130'

	def setup(self):
		self.skip('configure')
		self.make_install_flags += [S.PREFIX_MAKE_INSTALL_FLAG]
