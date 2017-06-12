class cmake(Wig):
	tar_uri = 'https://cmake.org/files/v3.5/cmake-{RELEASE_VERSION}.tar.gz'
	last_release_version = '3.5.1'

	def configure(self):
		return ['./bootstrap %s' % ' '.join(self.configure_flags)]
