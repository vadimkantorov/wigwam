class matio(AutogenWig):
	tar_uri = 'https://github.com/tbeu/matio/releases/download/v{version}/matio-{version}.tar.gz'
	git_uri = 'https://github.com/tbeu/matio'
	version = '1.5.10'
	dependencies = ['zlib', 'hdf5', 'libtool', 'automake']
