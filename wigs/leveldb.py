class leveldb(Wig):
	tar_uri = 'https://github.com/google/leveldb/archive/v{RELEASE_VERSION}.tar.gz'
	git_uri = 'https://github.com/google/leveldb'
	last_release_version = '1.18'

	def setup(self):
		self.skip('configure')

	def install(self):
		return ['cp --preserve=links libleveldb.* "$PREFIX/lib"',
				'cp -r include/leveldb "$PREFIX/include"']
