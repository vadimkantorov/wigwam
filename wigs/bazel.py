class bazel(Wig):
	tarball_uri = 'https://github.com/bazelbuild/bazel/archive/{RELEASE_VERSION}.tar.gz'
	last_release_version = '0.5.0'
	git_uri = 'https://github.com/bazelbuild/bazel'
	raw_uri = 'https://github.com/bazelbuild/bazel/releases/download/{RELEASE_VERSION}/bazel-{RELEASE_VERSION}-installer-linux-x86_64.sh'
	
	def setup(self):
		self.skip('configure', 'make')
	
	def gen_fetch_snippet(self):
		uri = self.raw_uri.format(RELEASE_VERSION = self.last_release_version)
		return [S.mkdir_p(self.paths.src_dir), S.download(uri, os.path.join(self.paths.src_dir, os.path.basename(uri)))]
	
	def gen_install_snippet(self):
		return [S.export('HOME', '$PREFIX'), 'bash bazel-*-installer*.sh --user']
