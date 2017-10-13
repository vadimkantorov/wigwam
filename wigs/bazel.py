class bazel(Wig):
	uri = 'https://github.com/bazelbuild/bazel/releases/download/{version}/bazel-{version}-installer-linux-x86_64.sh'
	tar_uri = 'https://github.com/bazelbuild/bazel/archive/{version}.tar.gz'
	git_uri = 'https://github.com/bazelbuild/bazel'
	version = '0.5.0'
	configure = None
	build = None

	def install(self):
		return [S.export('HOME', '$PREFIX'), 'bash bazel-*-installer*.sh --user']
