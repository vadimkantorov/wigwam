class git(Wig):
	tar_uri = 'https://github.com/git/git/archive/v{version}.tar.gz'
	git_uri = 'https://github.com/git/git'
	version = '2.10.1'
	before_configure = [S.make(['configure'])]
	configure_flags = ['--without-tcltk']
