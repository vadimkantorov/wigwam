class cmake(Wig):
	tar_uri = 'https://cmake.org/files/v3.5/cmake-{version}.tar.gz'
	version = '3.5.1'

	def configure(self):
		return './bootstrap {}'.format(' '.join(self.configure_flags))
