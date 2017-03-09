class pytorch(PythonWig):
	git_uri = 'https://github.com/pytorch/pytorch'
	dependencies = ['numpy', 'cmake'] #, 'pip-pyyaml', 'pip-cffi', 'setuptools']
	optional_dependencies = ['magma']
	supported_features = ['cuda']
	default_features = ['+cuda']

	def switch_cuda(self, on):
		if on:
			self.require('magma')
		else:
			self.before_install += [S.export('NO_CUDA', '1')]
