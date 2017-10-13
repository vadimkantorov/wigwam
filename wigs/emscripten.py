class emscripten(CmakeWig):
	git_uri = 'https://github.com/kripken/emscripten'
	dependencies = ['nodejs', DebWig('default-jre')]
	working_directory = 'emscripten-fastcomp'
	cmake_flags = ['-DCMAKE_BUILD_TYPE=Release', '-DLLVM_TARGETS_TO_BUILD="X86;JSBackend"', '-DLLVM_INCLUDE_EXAMPLES=OFF', '-DLLVM_INCLUDE_TESTS=OFF', '-DCLANG_INCLUDE_EXAMPLES=OFF', '-DCLANG_INCLUDE_TESTS=OFF']

	def fetch(self):
		return super(emscripten, self).fetch() + [S.git_clone_recursive(self.git_uri + '-fastcomp', os.path.join(self.paths.src_dir, self.working_directory)), S.git_clone_recursive(self.git_uri + '-fastcomp-clang', os.path.join(self.paths.src_dir, self.working_directory, 'tools', 'clang'))]
