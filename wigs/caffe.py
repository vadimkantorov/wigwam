class caffe(Wig):
	git_uri = 'https://github.com/BVLC/caffe'
	config_access = ['PATH_TO_NVCC', 'PATH_TO_CUDNN_SO', 'PATH_TO_MATLAB']
	dependencies = ['boost', 'protobuf', 'glog', 'gflags', 'hdf5', 'snappy']
	optional_dependencies = ['openblas', 'leveldb', 'lmdb', 'opencv']
	supported_features = ['openblas', 'python', 'cuda', 'cudnn', 'lmdb', 'leveldb', 'opencv', 'matlab']
	default_features = ['+openblas', '-leveldb', '-lmdb', '+opencv', '+cuda', '+cudnn']
	
	def setup(self):
		self.skip('make parallel')
		self.config_fixes = ''
		
	def set_makefile_config_var_commented(self, var_name, var_value):
		self.config_fixes += '''| sed 's$# %s :=$%s := %s# %s :=$' ''' % (var_name, var_name, var_value, var_name)

	def set_makefile_config_var_uncommented(self, var_name, var_prepend, comment_rest = False):
		self.config_fixes += '''| sed 's$%s :=$%s := %s%s$' ''' % (var_name, var_name, var_prepend, '#' if comment_rest else '')

	def switch_openblas_on(self):
		self.require('openblas')
		self.set_makefile_config_var_uncommented('BLAS', 'open', comment_rest = True)
		self.set_makefile_config_var_commented('BLAS_INCLUDE', "'$PREFIX'/include")
		self.set_makefile_config_var_commented('BLAS_LIB', "'$PREFIX'/lib")
		
	def switch_opencv(self, on):
		if on:
			self.require('opencv')
			self.set_makefile_config_var_commented('OPENCV_VERSION', 3)
		self.set_makefile_config_var_commented('USE_OPENCV', 1 if on else 0)
		
	def switch_lmdb(self, on):
		if on:
			self.require('lmdb')
		self.set_makefile_config_var_commented('USE_LMDB', 1 if on else 0)
		
	def switch_leveldb(self, on):
		if on:
			self.require('leveldb')
		self.set_makefile_config_var_commented('USE_LEVELDB', 1 if on else 0)
		
	def switch_cudnn_on(self):
		self.lib_dirs += [os.path.dirname(self.cfg('PATH_TO_CUDNN_SO'))]
		self.set_makefile_config_var_commented('USE_CUDNN', 1)
		self.set_makefile_config_var_uncommented('LIBRARY_DIRS', os.path.dirname(self.cfg('PATH_TO_CUDNN_SO')))
		self.set_makefile_config_var_uncommented('INCLUDE_DIRS', os.path.join(os.path.dirname(self.cfg('PATH_TO_CUDNN_SO')), '../include'))
		
	def switch_cuda_on(self):
		self.lib_dirs += [os.path.join(os.path.dirname(self.cfg('PATH_TO_NVCC')), '../lib64')]
		self.set_makefile_config_var_commented('CUDA_DIR', os.path.join(os.path.dirname(self.cfg('PATH_TO_NVCC')), '..'))

	def switch_matlab_on(self):
		self.after_make += [S.make(self.make_flags + ['matcaffe'])]
		self.set_makefile_config_var_commented('MATLAB_DIR', os.path.join(os.path.dirname(self.cfg('PATH_TO_MATLAB')), '..'))
		
	def switch_python_on(self):
		self.python_dirs += [os.path.join(self.paths.src_dir, 'python')]
		self.after_make += [S.make(self.make_flags + ['pycaffe'])]
		self.set_makefile_config_var_commented('WITH_PYTHON_LAYER', 1)

	def gen_configure_snippet(self):
		return ['cat Makefile.config.example %s > Makefile.config' % self.config_fixes]

	def gen_install_snippet(self):
		return [S.ln('$(pwd)/build/lib/libcaffe.so', '$PREFIX/lib/libcaffe.so'), 
				S.ln('$(pwd)/build/lib/libcaffe.a', '$PREFIX/lib/libcaffe.a'),
				S.ln('$(pwd)/build/tools/caffe', '$PREFIX/bin/caffe')]
