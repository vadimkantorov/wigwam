class git(Wig):
	tar_uri = 'https://github.com/git/git/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '2.10.1'
	git_uri = 'https://github.com/git/git'

	def setup(self):
		self.before_configure += [S.make(['configure'])]
		self.configure_flags += ['--without-tcltk']
