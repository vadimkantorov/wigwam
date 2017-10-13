class scipy(PythonWig):
	tar_uri = 'https://github.com/scipy/scipy/releases/download/v{version}/scipy-{version}.tar.gz'
	git_uri = 'https://github.com/scipy/scipy'
	version = '0.18.1'
	dependencies = ['numpy']

	def switch_openblas_on(self):
		#default_features = ['+openblas']
		self.require('openblas')
		include_dirs = os.path.pathsep.join(map(os.path.abspath, P.prefix_include_dirs))
		lib_dirs = os.path.pathsep.join(map(os.path.abspath, P.prefix_lib_dirs))
		self.configure_flags += ['[openblas]', 'libraries = openblas', 'include_dirs = {}'.format(include_dirs), 'library_dirs = {}'.format(lib_dirs), 'runtime_library_dirs = {}'.format(lib_dirs)]

	def configure(self):
		return ['cat <<- EOF > site.cfg'] + self.configure_flags + ['EOF']
