class libedit(Wig):		
	tarball_uri = 'http://thrysoee.dk/editline/libedit-$RELEASE_VERSION$.tar.gz'		
	last_release_version = 'v20160903-3.1'
	dependencies = ['ncurses']
			
	def setup(self):		
		#self.configure_flags += ['--disable-shared']
		self.before_configure += [S.export_prepend_paths(S.CPATH, ['$PREFIX/include/ncurses'])]
		self.before_make += [S.export_prepend_paths(S.CPATH, ['$PREFIX/include/ncurses'])]
