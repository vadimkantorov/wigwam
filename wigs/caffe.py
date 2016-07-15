class caffe(Wig):
	git_uri = 'https://github.com/BVLC/caffe'
	config_acces = ['PATH_TO_NVCC', 'PATH_TO_CUDNN_SO']
	dependencies = ['boost', 'protobuf', 'glog', 'gflags', 'hdf5', 'snappy']
	optional_dependencies = ['openblas', 'leveldb', 'lmdb', 'opencv']
	supported_features = ['openblas', 'python', 'cuda', 'cudnn', 'lmdb', 'leveldb', 'opencv']
	default_features = ['+openblas', '+python', '-leveldb', '-lmdb', '+opencv']
	
	def setup(self):
		self.skip('make parallel')

		self.python_dirs += [os.path.join(self.paths.src_dir, 'python')]
		self.config_fixes = ''

	def switch_openblas_on(self):
		self.require('openblas')
		self.config_fixes += '''| sed 's$BLAS := atlas$BLAS := open# BLAS := atlas$' '''
		self.config_fixes += '''| sed 's$# BLAS_INCLUDE := /path/to/your/blas$BLAS_INCLUDE := '$PREFIX'/include# BLAS_INCLUDE := /path/to/your/blas$' '''
		self.config_fixes += '''| sed 's$# BLAS_LIB := /path/to/your/blas$BLAS_LIB := '$PREFIX'/lib# BLAS_LIB := /path/to/your/blas$' '''
		
	def switch_opencv(self, on):
		self.require('opencv')
		self.config_fixes += '''| sed 's$# USE_OPENCV$USE_OPENCV := %d# USE_OPENCV$' ''' % (1 if on else 0)
		self.config_fixes += '''| sed 's$# OPENCV_VERSION$OPENCV_VERSION := 3# OPENCV_VERSION$' '''
		
	def switch_lmdb(self, on):
		self.require('lmdb')
		self.config_fixes += '''| sed 's$# USE_LMDB$USE_LMDB := %d# USE_LMDB$' ''' % (1 if on else 0)
		
	def switch_leveldb(self, on):
		self.require('leveldb')
		self.config_fixes += '''| sed 's$# USE_LEVELDB$USE_LEVELDB := %d# USE_LEVELDB$' ''' % (1 if on else 0)

	def switch_cudnn_on(self):
		self.lib_dirs += [os.path.dirname(self.cfg('PATH_TO_CUDNN_SO'))]
		self.config_fixes += '''| sed 's$# USE_CUDNN$USE_CUDNN := 1# USE_CUDNN$' '''
		
	def switch_cuda_on(self):
		self.lib_dirs += [os.path.join(os.path.dirname(self.cfg('PATH_TO_NVCC')), '../lib64')]
		self.config_fixes += '''| sed 's$CUDA_DIR := /usr/local/cuda$CUDA_DIR := %s#CUDA_DIR := /usr/local/cuda$' ''' % os.path.join(os.path.dirname(self.cfg('PATH_TO_NVCC')), '..')
	
	def switch_python_on(self):
		self.after_make += [S.make(self.make_flags + ['pycaffe'])]
		self.config_fixes += '''| sed 's$# WITH_PYTHON_LAYER$WITH_PYTHON_LAYER := 1# WITH_PYTHON_LAYER$' '''

	def gen_configure_snippet(self):
		return ['cat Makefile.config.example %s > Makefile.config' % self.config_fixes]

	def gen_install_snippet(self):
		return [S.ln('$(pwd)/build/lib/libcaffe.so', '$PREFIX/lib/libcaffe.so'), 
				S.ln('$(pwd)/build/lib/libcaffe.a', '$PREFIX/lib/libcaffe.a'),
				S.ln('$(pwd)/build/tools/caffe', '$PREFIX/bin/caffe')]
