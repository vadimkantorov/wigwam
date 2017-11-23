class yael(Wig):
	tar_uri = 'https://gforge.inria.fr/frs/download.php/file/33810/yael_v{version}.tar.gz'
	version = '438'
	install = None

	def configure(self):
		return 'bash configure.sh {}'.format(' '.join(self.configure_flags))

	def atlas(self, on = True):
		self.require('atlas')
		self.before_configure += [S.export(S.LDFLAGS, '-lf77blas -llapack')]

	def python(self, on):
		self.require('swig')
		self.configure_flags += ['--enable-numpy']
