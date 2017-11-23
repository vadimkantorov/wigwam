class ffmpeg(Wig):
	tar_uri = 'http://ffmpeg.org/releases/ffmpeg-{version}.tar.gz'
	version = '3.1.2'
	dependencies = ['bzip2', 'lzma', 'zlib']

	def yasm(self, on = True):
		self.require('yasm')
		self.configure_flags += ['--yasmexe="$PREFIX/bin/yasm"', '--enable-shared']

	def x264(self, on = True):
		self.require('x264')
		self.configure_flags += ['--enable-gpl', '--enable-libx264']
