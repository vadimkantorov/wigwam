class lmdb(Wig):
	tar_uri = 'https://github.com/LMDB/lmdb/archive/LMDB_{RELEASE_VERSION}.tar.gz'
	git_uri = 'https://github.com/LMDB/lmdb'
	working_directory = 'libraries/liblmdb'
	last_release_version = '0.9.15'

	def setup(self):
		self.skip('configure')
		self.before_install += [S.mkdir_p('$PREFIX/man')]
		self.make_install_flags += ['prefix="$PREFIX"']
