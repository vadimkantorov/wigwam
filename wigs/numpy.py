class numpy(PythonWig):
	tarball_uri = 'https://github.com/numpy/numpy/archive/v$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v1.11.2'
	git_uri = 'https://github.com/numpy/numpy'
	dependencies = ['cython']
	optional_dependencies = ['openblas']
	supported_features = ['openblas']
	default_features = ['+openblas']

	def setup(self):
		self.site_cfg = []

	def switch_openblas_on(self):
		self.require('openblas')
		include_dirs = map(os.path.abspath, P.prefix_include_dirs)
		lib_dirs = map(os.path.abspath, P.prefix_lib_dirs)
		self.site_cfg += [
			'[openblas]',
			'libraries = openblas',
			'include_dirs = %s' % os.path.pathsep.join(include_dirs),
			'library_dirs = %s' % os.path.pathsep.join(lib_dirs),
			'runtime_library_dirs = %s' % os.path.pathsep.join(lib_dirs)
		]

	def gen_configure_snippet(self):
		return ['cat <<- EOF > site.cfg'] + self.site_cfg + ['EOF']
