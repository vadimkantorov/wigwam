class tensorflow(Wig):
	git_uri = 'https://github.com/tensorflow/tensorflow'
	tarball_uri = 'https://github.com/tensorflow/tensorflow/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '1.0.1'
	dependencies = ['bazel', 'pip', 'numpy']
