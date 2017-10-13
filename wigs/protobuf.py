class protobuf(AutogenWig):
	tar_uri = 'https://github.com/google/protobuf/archive/v{version}.tar.gz'
	git_uri = 'https://github.com/google/protobuf'
	version = '3.1.0'
	
	def switch_python_on(self):
		self.after_install += ['cd python', S.python_setup_install]
