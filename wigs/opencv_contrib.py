class opencv_contrib(Wig):
	git_uri = 'https://github.com/opencv/opencv_contrib'

	def setup(self):
		self.skip('configure', 'make', 'install')
