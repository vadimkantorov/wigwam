class pytorch(PythonWig):
	git_uri = 'https://github.com/pytorch/pytorch'
	dependencies = ['numpy', 'cmake', 'magma'] #, 'pip-pyyaml', 'pip-cffi', 'setuptools']
	supported_features = ['cuda']

	def switch_cuda_off(self):
		self.before_install += [S.export('NO_CUDA', '1')]
