class pkg_config(Wig):
	tarball_uri = 'http://pkgconfig.freedesktop.org/releases/pkg-config-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v0.28'
	
	def setup(self):
		self.configure_flags += ['--with-internal-glib']
