class libedit(Wig):		
	tar_uri = 'http://thrysoee.dk/editline/libedit-{VERSION}.tar.gz'		
	version = '20160903-3.1'
	dependencies = ['ncurses']
	before_configure = [S.export_prepend_paths(S.CPATH, ['$PREFIX/include/ncurses'])]
	before_build = [S.export_prepend_paths(S.CPATH, ['$PREFIX/include/ncurses'])]
	#configure_flags = ['--disable-shared']
