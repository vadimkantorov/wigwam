class fftw(Wig):
	tar_uri = 'http://www.fftw.org/fftw-{VERSION}.tar.gz'
	version = '3.3.4'
	configure_flags = ['--enable-sse2', '--enable-shared', '--with-pic', 'F77=gfortran']
