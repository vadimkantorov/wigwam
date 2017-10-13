class bzip2(Wig):
	tar_uri = 'http://www.bzip.org/1.0.6/bzip2-{VERSION}.tar.gz'
	version = '1.0.6'
	make_flags = [S.CFLAGS + '=' + S.FPIC_FLAG]
	make_install_flags = [S.PREFIX_MAKE_INSTALL_FLAG]
	configure = None
