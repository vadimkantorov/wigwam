class pytorch(PythonWig):
	git_uri = 'https://github.com/pytorch/pytorch'
	dependencies = ['numpy', 'cmake', 'pip-pyyaml', 'pip-cffi']
	supported_features = ['cuda']

	def switch_cuda_off(self):
		self.before_install += [S.export('NO_CUDA', '1')]
