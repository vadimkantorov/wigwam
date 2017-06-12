class atlas(Wig):
	tar_uri = 'http://downloads.sourceforge.net/project/math-atlas/Stable/{RELEASE_VERSION}/atlas{RELEASE_VERSION}.tar.bz2'
	tar_strip_components = 1
	last_release_version = '3.10.2'
	supported_features = ['threads', 'lapack']
	default_features = ['+lapack']

	def setup(self):
		self.before_make += [S.CD_BUILD]

	def configure(self):
		return [S.MKDIR_CD_BUILD, '.' + S.configure(self.configure_flags)]

	def switch_threads_off(self):
		self.configure_flags += ['-t 0']

	def switch_lapack_on(self):
		self.require('lapack')
		self.configure_flags += ['--with-netlib-lapack-tarfile="%s"' % os.path.abspath(os.path.join(P.tar_tree, 'lapack.tgz'))]
