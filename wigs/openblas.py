class openblas(Wig):
	tarball_uri = 'https://github.com/xianyi/OpenBLAS/archive/v$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v0.2.19'
	supported_features = ['debug', 'threads']
	default_features = ['+threads']

	def setup(self):
		self.skip('configure')
		self.make_flags += ['FC=gfortran', 'NO_AFFINITY=1']
		self.make_install_flags += [S.PREFIX_MAKE_INSTALL_FLAG]
	
	def switch_debug_on(self):
		self.make_flags += ['DEBUG=1']
	
	def switch_threads(self, on):
		self.make_flags += ['USE_OPENMP=1'] if on else ['USE_OPENMP=0', 'USE_THREAD=0']
