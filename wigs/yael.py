class yael(Wig):
	tar_uri = 'https://gforge.inria.fr/frs/download.php/file/33810/yael_v{VERSION}.tar.gz'
	version = '438'
	optional_dependencies = ['atlas', 'swig']
	install = None

	#drop prefix
	def configure(self):
		return 'bash configure.sh {}'.format(' '.join(self.configure_flags))

	def switch_python_on(self):
		self.require('swig')
		self.configure_flags += ['--enable-numpy']
	
	def switch_atlas_on(self):
		self.require('atlas')
		self.before_configure += [S.export(S.LDFLAGS, '-lf77blas -llapack')]
