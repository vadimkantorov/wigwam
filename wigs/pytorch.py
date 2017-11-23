class pytorch(PythonWig):
	git_uri = 'https://github.com/pytorch/pytorch'
	dependencies = ['numpy', 'cmake', PipWig('pyyaml'), PipWig('cffi')]
	
	def cuda(self, on = True):
		if on:
			self.require('magma')
			self.before_install += [S.export('CUDA_HOME', os.path.dirname(os.path.dirname(self.getenv('PATH_TO_NVCC'))))]
		else:
			self.before_install += [S.export('NO_CUDA', '1')]

	def cudnn(self, on = True):
		self.before_install += [S.export('CUDNN_LIBRARY', os.path.dirname(self.getenv('PATH_TO_CUDNN_SO'))), S.export('CUDNN_INCLUDE_DIR',  os.path.join(os.path.dirname(self.getenv('PATH_TO_CUDNN_SO')), '../include'))]
