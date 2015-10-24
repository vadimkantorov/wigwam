class wangle(CmakeWig):
	git_uri = 'https://github.com/facebook/wangle'
	tarball_uri = 'https://github.com/facebook/wangle/archive/v$RELEASE_VERSION$.tar.gz'
	working_directory = 'wangle'
	last_release_version = 'v0.13.0'
	dependencies = ['folly']

	def setup(self):
		self.after_fetch += ['sed -i "s/sExecutor->/singleton->/g" "%s"' % os.path.join(self.paths.src_dir, self.working_directory, 'concurrent/GlobalExecutor.cpp')]
