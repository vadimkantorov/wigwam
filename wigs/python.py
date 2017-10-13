class python(Wig):
	tar_uri = 'https://github.com/python/cpython/archive/v{version}.tar.gz'
	git_uri = 'https://github.com/python/cpython'
	version = '2.7.13'
	dependencies = ['openssl', 'ncurses', 'readline', 'zlib', 'bzip2']
