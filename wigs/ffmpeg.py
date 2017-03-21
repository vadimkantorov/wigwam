class ffmpeg(Wig):
	tarball_uri = 'http://ffmpeg.org/releases/ffmpeg-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v3.1.2'
	optional_dependencies = ['yasm', 'x264']
	supported_features = ['yasm', 'x264']
	dependencies = ['bzip2', 'lzma', 'zlib']
	default_features = ['+yasm']

	def switch_yasm_on(self):
		self.require('yasm')
		self.configure_flags += ['--yasmexe="$PREFIX/bin/yasm"', '--enable-shared']

	def switch_x264_on(self):
		self.require('x264')
		self.configure_flags += ['--enable-gpl', '--enable-libx264']
