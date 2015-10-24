class manen_rp(Wig):
	git_uri = 'https://github.com/smanenfr/rp'
	matlab_root = 'matlab'
	config_access = ['PATH_TO_MATLAB']	

	def setup(self):
		self.skip('configure', 'install')
	
	def gen_make_snippet(self):
		return [S.matlab(self.cfg('PATH_TO_MATLAB'), 'setup.m')]
