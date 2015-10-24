class sdl(Wig):
	tarball_uri = 'https://www.libsdl.org/release/SDL2-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v2.0.3'

	def setup(self):
		self.configure_flags += ['--enable-sse2']
		self.before_configure += [S.export(S.LDFLAGS, '-ldl')]
