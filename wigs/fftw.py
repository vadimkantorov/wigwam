class fftw(Wig):
	tar_uri = 'http://www.fftw.org/fftw-{RELEASE_VERSION}.tar.gz'
	last_release_version = '3.3.4'

	def setup(self):
		self.configure_flags += ['--enable-sse2', '--enable-shared', '--with-pic', 'F77=gfortran']
