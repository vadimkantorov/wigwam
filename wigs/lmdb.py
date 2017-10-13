class lmdb(Wig):
	tar_uri = 'https://github.com/LMDB/lmdb/archive/LMDB_{VERSION}.tar.gz'
	git_uri = 'https://github.com/LMDB/lmdb'
	version = '0.9.15'
	working_directory = 'libraries/liblmdb'
	before_install = [S.mkdir_p('$PREFIX/man')]
	make_install_flags = ['prefix="$PREFIX"']

	def configure(self):
		return ''
