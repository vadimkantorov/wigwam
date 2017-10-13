class vlfeat(Wig):
	tar_uri = 'https://github.com/vlfeat/vlfeat/archive/v{version}.tar.gz'
	git_uri = 'https://github.com/vlfeat/vlfeat'
	version = '0.9.20'
	config_access = ['PATH_TO_MATLAB']
	configure = None
	install = None

	def setup(self):
		self.after_make = ['make MEX="{}"'.format(os.path.join(os.path.dirname(self.getenv('PATH_TO_MATLAB')), 'mex'))]
		#self.matlab('.')
