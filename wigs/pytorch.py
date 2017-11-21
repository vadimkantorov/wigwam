class pytorch(PythonWig):
	git_uri = 'https://github.com/pytorch/pytorch'
	dependencies = ['numpy', 'cmake', PipWig('pyyaml'), PipWig('cffi')]
	
	def switch_cuda(self, on):
		# TODO: set env CUDA_HOME for custom CUDA path
		#default_features = ['+cuda']
		if on:
			self.require('magma')
		else:
			self.before_install += [S.export('NO_CUDA', '1')]

	def switch_cudnn(self, on):
		if on:
			self.before_install += [S.export('CUDNN_LIBRARY', os.path.dirname(self.getenv('PATH_TO_CUDNN_SO'))), S.export('CUDNN_INCLUDE_DIR',  os.path.join(os.path.dirname(self.getenv('PATH_TO_CUDNN_SO')), '../include'))]
