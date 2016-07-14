class protobuf(AutogenWig):
	tarball_uri = 'https://github.com/google/protobuf/archive/v$RELEASE_VERSION$.tar.gz'
	git_uri = 'https://github.com/google/protobuf'
	last_release_version = 'v3.0.0-beta-3.1'

	def setup(self):
		self.after_install += ['cd python', S.python_setup_install]
		#self.after_install += PipWig('pip-protobuf==3.0.0a3').gen_install_snippet()
