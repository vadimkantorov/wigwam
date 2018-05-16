class opencv_contrib(Wig):
	git_uri = 'https://github.com/opencv/opencv_contrib'
	tarball_uri = 'https://github.com/opencv/opencv_contrib/archive/{RELEASE_VERSION}.tar.gz'
	last_release_version = '3.3.0'

	def setup(self):
		self.skip('configure', 'make', 'install')
