class protobuf(AutogenWig):
	tarball_uri = 'https://github.com/google/protobuf/archive/v{RELEASE_VERSION}.tar.gz'
	git_uri = 'https://github.com/google/protobuf'
	last_release_version = '3.1.0'
	supported_features = ['python']
	
	def switch_python_on(self):
		self.after_install += ['cd python', S.python_setup_install]
