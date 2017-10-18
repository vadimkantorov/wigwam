class pytorch(PythonWig):
	git_uri = 'https://github.com/pytorch/pytorch'
	git_init_submodules = True
	dependencies = ['numpy', 'cmake', 'pip-pyyaml', 'pip-cffi'] #, 'pip']
	optional_dependencies = ['magma']
	supported_features = ['cuda']
	default_features = ['+cuda']
	
	# TODO: set env CUDA_HOME for custom CUDA path

	def switch_cuda(self, on):
		if on:
			self.require('magma')
		else:
			self.before_install += [S.export('NO_CUDA', '1')]
