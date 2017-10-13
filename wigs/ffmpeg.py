class ffmpeg(Wig):
	tar_uri = 'http://ffmpeg.org/releases/ffmpeg-{version}.tar.gz'
	version = '3.1.2'
	optional_dependencies = ['yasm', 'x264']
	dependencies = ['bzip2', 'lzma', 'zlib']

	def switch_yasm_on(self):
		self.require('yasm')
		self.configure_flags += ['--yasmexe="$PREFIX/bin/yasm"', '--enable-shared']

	def switch_x264_on(self):
		self.require('x264')
		self.configure_flags += ['--enable-gpl', '--enable-libx264']
