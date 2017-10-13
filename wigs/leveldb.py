class leveldb(Wig):
	tar_uri = 'https://github.com/google/leveldb/archive/v{version}.tar.gz'
	git_uri = 'https://github.com/google/leveldb'
	version = '1.18'
	configure = None

	def install(self):
		return ['cp --preserve=links libleveldb.* "$PREFIX/lib"', 'cp -r include/leveldb "$PREFIX/include"']
