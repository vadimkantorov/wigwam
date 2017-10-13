class lmdb(Wig):
	tar_uri = 'https://github.com/LMDB/lmdb/archive/LMDB_{version}.tar.gz'
	git_uri = 'https://github.com/LMDB/lmdb'
	version = '0.9.15'
	working_directory = 'libraries/liblmdb'
	configure = None
	before_install = [S.mkdir_p('$PREFIX/man')]
	make_install_flags = [S.prefix_MAKE_INSTALL_FLAG]
