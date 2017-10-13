class swig(AutogenWig):
	tar_uri = 'https://github.com/swig/swig/archive/rel-{version}.tar.gz'
	git_uri = 'https://github.com/swig/swig'
	version = '3.0.10'
	dependencies = ['autoconf', 'automake'] # libpcre, yacc/bison
