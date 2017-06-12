class swig(AutogenWig):
	tar_uri = 'https://github.com/swig/swig/archive/rel-{RELEASE_VERSION}.tar.gz'
	last_release_version = '3.0.10'
	git_uri = 'https://github.com/swig/swig'
	dependencies = ['autoconf', 'automake'] # libpcre, yacc/bison
