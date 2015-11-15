class ffmpeg(Wig):
	tarball_uri = 'http://ffmpeg.org/releases/ffmpeg-$RELEASE_VERSION$.tar.bz2'
	last_release_version = 'v2.4'
	optional_dependencies = ['yasm']
	supported_features = ['yasm']
	default_features = ['+yasm']

	def switch_yasm_on(self):
		self.require('yasm')
		self.configure_flags += ['--yasmexe="$PREFIX/bin/yasm"', '--enable-shared']
