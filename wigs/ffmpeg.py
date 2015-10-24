class ffmpeg(Wig):
	tarball_uri = 'http://ffmpeg.org/releases/ffmpeg-$RELEASE_VERSION$.tar.bz2'
	last_release_version = 'v2.4'
	supported_features = ['yasm']
	optional_dependencies = ['yasm']

	def setup(self):
		self.require(features = ['+yasm'])
	
	def switch_yasm_on(self):
		self.require('yasm')
		self.configure_flags += ['--yasmexe="$PREFIX/bin/yasm"', '--enable-shared']
