class ncurses(Wig):
	tar_uri = 'http://ftp.gnu.org/pub/gnu/ncurses/ncurses-{VERSION}.tar.gz'
	version = '6.0'
	configure_flags = ['--enable-overwrite']
	before_configure = [S.export(S.CFLAGS, '-fPIC'), S.export(S.CPPFLAGS, '-P')]
	before_build = [S.export(S.CFLAGS, S.FPIC_FLAG)]
