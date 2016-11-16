class yael(Wig):
	tarball_uri = 'https://gforge.inria.fr/frs/download.php/file/33810/yael_v$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v438'
	supported_features = ['python', 'atlas']
	optional_dependencies = ['atlas', 'swig']

	def setup(self):
		self.skip('make install', 'prefix')

	def gen_configure_snippet(self):
		return 'bash configure.sh %s' % ' '.join(self.configure_flags)

	def switch_python_on(self):
		self.require('swig')
		self.configure_flags += ['--enable-numpy']
	
	def switch_atlas_on(self):
		self.require('atlas')
		self.before_configure += [S.export(S.LDFLAGS, '-lf77blas -llapack')]
