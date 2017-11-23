class caffe(Wig):
	git_uri = 'https://github.com/BVLC/caffe'
	dependencies = ['boost', 'protobuf', 'glog', 'gflags', 'hdf5', 'snappy']
	install = None
	
	def setup(self):
		self.lib_dirs += [os.path.join(self.paths.src_dir, 'build', 'lib')]
		self.bin_dirs += [os.path.join(self.paths.src_dir, 'build', 'tools')]

	def configure(self):
		return ['cat Makefile.config.example %s > Makefile.config' % self.configure_flags]

	def build(self):
		return S.make(self.make_flags)
		
	def cudnn(self, on = True):
		self.lib_dirs += [os.path.dirname(self.getenv('PATH_TO_CUDNN_SO'))]
		self.set_makefile_config_var_commented('USE_CUDNN', 1)
		self.set_makefile_config_var_uncommented('LIBRARY_DIRS', os.path.dirname(self.getenv('PATH_TO_CUDNN_SO')))
		self.set_makefile_config_var_uncommented('INCLUDE_DIRS', os.path.join(os.path.dirname(self.getenv('PATH_TO_CUDNN_SO')), '../include'))
		
	def cuda(self, on = True):
		self.lib_dirs += [os.path.join(os.path.dirname(self.getenv('PATH_TO_NVCC')), '../lib64')]
		self.set_makefile_config_var_commented('CUDA_DIR', os.path.join(os.path.dirname(self.getenv('PATH_TO_NVCC')), '..'))

	def openblas(self, on = True):
		self.require('openblas')
		self.set_makefile_config_var_uncommented('BLAS', 'open', comment_rest = True)
		self.set_makefile_config_var_commented('BLAS_INCLUDE', "'$PREFIX'/include")
		self.set_makefile_config_var_commented('BLAS_LIB', "'$PREFIX'/lib")
		
	def opencv(self, on = True):
		if on:
			self.require('opencv')
			self.set_makefile_config_var_commented('OPENCV_VERSION', 3)
		self.set_makefile_config_var_commented('USE_OPENCV', 1 if on else 0)
		
	def lmdb(self, on):
		if on:
			self.require('lmdb')
		self.set_makefile_config_var_commented('USE_LMDB', 1 if on else 0)
		
	def leveldb(self, on):
		if on:
			self.require('leveldb')
		self.set_makefile_config_var_commented('USE_LEVELDB', 1 if on else 0)
		
	def matlab(self, on):
		self.after_make += [S.make(self.make_flags + ['matcaffe'])]
		self.set_makefile_config_var_commented('MATLAB_DIR', os.path.join(os.path.dirname(self.getenv('PATH_TO_MATLAB')), '..'))
		
	def python(self, on):
		self.require('skimage')
		self.python_dirs += [os.path.join(self.paths.src_dir, 'python')]
		self.after_make += [S.make(self.make_flags + ['pycaffe'])]
		self.set_makefile_config_var_commented('WITH_PYTHON_LAYER', 1)

	def set_makefile_config_var_commented(self, var_name, var_value):
		self.configure_flags += '''| sed 's$# %s :=$%s := %s# %s :=$' ''' % (var_name, var_name, var_value, var_name)

	def set_makefile_config_var_uncommented(self, var_name, var_prepend, comment_rest = False):
		self.configure_flags += '''| sed 's$%s :=$%s := %s%s$' ''' % (var_name, var_name, var_prepend, '#' if comment_rest else '')
