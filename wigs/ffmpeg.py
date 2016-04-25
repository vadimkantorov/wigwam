class ffmpeg(Wig):
	tarball_uri = 'http://ffmpeg.org/releases/ffmpeg-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v3.0.1'
	optional_dependencies = ['yasm']
	supported_features = ['yasm']
	default_features = ['+yasm']

	def switch_yasm_on(self):
		self.require('yasm')
		self.configure_flags += ['--yasmexe="$PREFIX/bin/yasm"', '--enable-shared']
