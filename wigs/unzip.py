class unzip(Wig):
	tar_uri = 'http://downloads.sourceforge.net/infozip/unzip{VERSION}.tar.gz'
	version = '60'
	makefile_path = 'unix/Makefile'
	make_flags = ['-f', makefile_path, 'generic']
	make_install_flags = [S.prefix_MAKE_INSTALL_FLAG, '-f', makefile_path]
 
	def configure(self):
		return '' 
