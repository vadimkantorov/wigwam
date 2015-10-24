class autoconf_archive(Wig):
	git_uri = 'git://git.sv.gnu.org/autoconf-archive.git'
	dependencies = ['texinfo']

	def setup(self):
		self.before_configure += ['bash bootstrap.sh --copy']
		self.before_make += [S.make([]) + 'maintainer-all']
