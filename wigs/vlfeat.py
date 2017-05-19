class vlfeat(Wig):
	tarball_uri = 'https://github.com/vlfeat/vlfeat/archive/v{RELEASE_VERSION}.tar.gz'
	git_uri = 'https://github.com/vlfeat/vlfeat'
	last_release_version = '0.9.20'
	config_access = ['PATH_TO_MATLAB']

	def setup(self):
		self.skip('configure', 'make install')
		PATH_TO_MEX = os.path.join(os.path.dirname(self.cfg('PATH_TO_MATLAB')), 'mex')
		self.after_make += ['make MEX="%s"' % PATH_TO_MEX]
		self.matlab('.')
