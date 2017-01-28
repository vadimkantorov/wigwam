class emscripten(CmakeWig):
	git_uri = 'https://github.com/kripken/emscripten'
	dependencies = ['nodejs', 'deb-default-jre']
	working_directory = 'emscripten-fastcomp'

	def setup(self):
		self.after_fetch += [S.fetch_git('https://github.com/kripken/emscripten-fastcomp', os.path.join(self.paths.src_dir, self.working_directory)),
			S.fetch_git('https://github.com/kripken/emscripten-fastcomp-clang', os.path.join(self.paths.src_dir, self.working_directory, 'tools', 'clang')
		]
		self.configure_flags += ['--enable-optimized', '--disable-assertions', '--enable-targets=host,js']
