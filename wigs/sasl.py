class sasl(Wig):
	tarball_uri = 'ftp://ftp.cyrusimap.org/cyrus-sasl/cyrus-sasl-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v2.1.26'

	def setup(self):
		self.skip('make parallel')

		self.configure_flags += ['--without-des']
