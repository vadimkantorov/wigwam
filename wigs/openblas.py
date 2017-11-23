class openblas(Wig):
	tar_uri = 'https://github.com/xianyi/OpenBLAS/archive/v{version}.tar.gz'
	version = '0.2.19'
	configure = None
	make_flags = ['FC=gfortran', 'NO_AFFINITY=1']
	make_install_flags = [S.PREFIX_MAKE_INSTALL_FLAG]
	
	def debug(self, on):
		self.make_flags += ['DEBUG=1']
	
	def threads(self, on):
		#default_features = ['+threads']
		self.make_flags += ['USE_OPENMP=1'] if on else ['USE_OPENMP=0', 'USE_THREAD=0']
