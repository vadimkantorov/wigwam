class tensorflow(Wig):
	git_uri = 'https://github.com/tensorflow/tensorflow'
	tarball_uri = 'https://github.com/tensorflow/tensorflow/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '1.0.1'
	dependencies = ['bazel', 'pip', 'numpy']
	
	def setup(self):
		self.before_configure += [S.export('PYTHON_BIN_PATH', '$(which python)'),
			S.export('CC_OPT_FLAGS', '-march=default'),
			S.export('TF_NEED_JEMALLOC', 0),
			S.export('TF_NEED_GCP', 0),
			S.export('TF_NEED_HDFS', 0),
			S.export('TF_ENABLE_XLA', 1)
		]
