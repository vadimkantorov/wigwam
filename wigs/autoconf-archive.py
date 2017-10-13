class autoconf_archive(Wig):
	git_uri = 'git://git.sv.gnu.org/autoconf-archive.git'
	dependencies = ['texinfo']
	before_configure = ['bash bootstrap.sh --copy']
	before_build = [S.make(['maintainer-all'])]
