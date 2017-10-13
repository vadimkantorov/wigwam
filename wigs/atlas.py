class atlas(Wig):
	tar_uri = 'http://downloads.sourceforge.net/project/math-atlas/Stable/{version}/atlas{version}.tar.bz2'
	tar_strip_components = 1
	version = '3.10.2'
	before_make = [S.CD_BUILD]
	default_features = ['+lapack']

	def configure(self):
		return [S.MKDIR_BUILD, S.CD_BUILD, '.' + S.configure(self.configure_flags)]

	def switch_threads_off(self):
		self.configure_flags += ['-t 0']

	def switch_lapack_on(self):
		self.require('lapack')
		self.configure_flags += ['--with-netlib-lapack-tarfile="%s"'.format(os.path.abspath(os.path.join(P.tar_tree, 'lapack.tgz')))]
