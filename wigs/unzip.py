class unzip(Wig):
	tarball_uri = 'http://downloads.sourceforge.net/infozip/unzip{RELEASE_VERSION}.tar.gz'
	last_release_version = '60'
  
	def setup(self):
		self.skip('configure')
		makefile_path = '"unix/Makefile"'
		self.make_flags += ['-f', makefile_path, 'generic']
		self.make_install_flags += [S.prefix_MAKE_INSTALL_FLAG, '-f', makefile_path]
