class tensorflow(PipWig):
	git_uri = 'https://github.com/tensorflow/tensorflow'
	tarball_uri = 'https://github.com/tensorflow/tensorflow/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '1.0.1'
	dependencies = ['bazel', 'numpy']
	config_access = ['PATH_TO_NVCC', 'PATH_TO_CUDNN_SO']
	supported_features = ['cuda']
	default_features = ['+cuda']
	
	def setup(self):
		self.before_configure += [
			S.export('GCC_HOST_COMPILER_PATH', '$(which gcc)'),
			S.export('CC_OPT_FLAGS', '-march=native'),
			S.export('PYTHON_BIN_PATH', '$(which python)'),
			S.export('USE_DEFAULT_PYTHON_LIB_PATH', 1),
			S.export('TF_NEED_JEMALLOC', 0),
			S.export('TF_NEED_GCP', 0),
			S.export('TF_NEED_HDFS', 0),
			S.export('TF_NEED_OPENCL', 0),
			S.export('TF_ENABLE_XLA', 1)
		]
		self.wheel_path = 'build/tensorflow-*.whl'
		
	def switch_cuda(self, on):
		if on:	
			self.before_configure += [
				S.export('TF_NEED_CUDA', 1),
				S.export('TF_CUDA_COMPUTE_CAPABILITIES', '3.5,5.2'),
				S.export('CUDA_TOOLKIT_PATH', os.path.dirname(os.path.dirname(self.cfg('PATH_TO_NVCC')))),
				S.export('CUDNN_INSTALL_PATH', os.path.dirname(os.path.dirname(self.cfg('PATH_TO_CUDNN_SO')))),
				S.export('TF_CUDA_VERSION', '8.0'),
				S.export('TF_CUDNN_VERSION', 5)
			]
		else:
			self.before_configure += [S.export('TF_NEED_CUDA', 0)]
		
	def gen_make_snippet(self):
		return ['bazel build --config=opt --config=cuda //tensorflow/tools/pip_package:build_pip_package', S.mkdir_p('build'), 'bash bazel-bin/tensorflow/tools/pip_package/build_pip_package "$PWD/build"']
