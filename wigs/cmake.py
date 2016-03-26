class cmake(Wig):
	tarball_uri = 'https://cmake.org/files/v3.5/cmake-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v3.5.1'

	def gen_configure_snippet(self):
		return ['./bootstrap %s' % ' '.join(self.configure_flags)]
