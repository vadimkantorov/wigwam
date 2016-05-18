class openblas(Wig):
	tarball_uri = 'https://github.com/xianyi/OpenBLAS/archive/v$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v0.2.18'

	def setup(self):
		self.skip('configure')
		self.make_flags += ['FC=gfortran']
		self.make_install_flags += [S.PREFIX_MAKE_INSTALL_FLAG]
