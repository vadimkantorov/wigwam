class readline(Wig):
	tar_uri = 'http://ftp.gnu.org/gnu/readline/readline-{VERSION}.tar.gz'
	version = '6.3'
	configure_flags = ['--disable-shared']
	before_configure = [S.export(S.CFLAGS, '-fPIC')]
	before_make = [S.export(S.CFLAGS, '-fPIC')]
