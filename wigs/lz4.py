class lz4(Wig):
	tar_uri = 'https://github.com/Cyan4973/lz4/archive/r{VERSION}.tar.gz'
	git_uri = 'https://github.com/Cyan4973/lz4'
	version = '130'
	make_install_flags = [S.PREFIX_MAKE_INSTALL_FLAG]
	configure = None
