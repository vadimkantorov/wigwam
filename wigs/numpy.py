class numpy(PythonWig):
	tar_uri = 'https://github.com/numpy/numpy/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '1.11.2'
	git_uri = 'https://github.com/numpy/numpy'
	dependencies = ['cython'] # 'setuptools'
	optional_dependencies = ['openblas']

	def switch_openblas_on(self):
		self.require('openblas')
		self.configure_flags += [
			'[openblas]',
			'libraries = openblas',
			'include_dirs = {}'.format(os.path.pathsep.join(map(os.path.abspath, P.prefix_include_dirs))),
			'library_dirs = {}'.format(os.path.pathsep.join(map(os.path.abspath, P.prefix_lib_dirs))),
			'runtime_library_dirs = {}'.format(os.path.pathsep.join(lib_dirs))
		]

	def configure(self):
		return ['cat <<- EOF > site.cfg'] + self.configure_flags + ['EOF']
