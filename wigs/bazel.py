class bazel(Wig):
	uri = 'https://github.com/bazelbuild/bazel/releases/download/{VERSION}/bazel-{VERSION}-installer-linux-x86_64.sh'
	tar_uri = 'https://github.com/bazelbuild/bazel/archive/{VERSION}.tar.gz'
	git_uri = 'https://github.com/bazelbuild/bazel'
	version = '0.5.0'
	
	def configure(self):
		return ''

	def build(self):
		return ''
	
	def install(self):
		return [S.export('HOME', '$PREFIX'), 'bash bazel-*-installer*.sh --user']
