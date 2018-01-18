class pytorch(PythonWig):
	git_uri = 'https://github.com/pytorch/pytorch'
	git_init_submodules = True
	dependencies = ['numpy', 'cmake', 'pip-pyyaml', 'pip-cffi'] #, 'pip']
	optional_dependencies = ['magma']
	supported_features = ['cuda', 'cudnn']
	default_features = ['+cuda', '+cudnn']
	config_access = ['PATH_TO_CUDNN_SO']
	
	# TODO: set env CUDA_HOME for custom CUDA path

	def switch_cuda(self, on):
		if on:
			self.require('magma')
		else:
			self.before_install += [S.export('NO_CUDA', '1')]

	def switch_cudnn(self, on):
		if on:
			self.before_install += [S.export('CUDNN_LIBRARY', self.cfg('PATH_TO_CUDNN_SO')), S.export('CUDNN_INCLUDE_DIR',  os.path.join(os.path.dirname(self.cfg('PATH_TO_CUDNN_SO')), '../include'))]
