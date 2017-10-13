class pkg_config(Wig):
	tar_uri = 'http://pkgconfig.freedesktop.org/releases/pkg-config-{VERSION}.tar.gz'
	version = '0.28'
	configure_flags = ['--with-internal-glib']
