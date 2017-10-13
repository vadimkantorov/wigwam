class boost(Wig):
	tar_uri = 'https://github.com/boostorg/boost/archive/boost-{version}.tar.gz'
	git_uri = 'https://github.com/boostorg/boost'
	version = '1.65.1'
	build = None
	bootstrap_flags = ['--without-libraries=python']

	def install(self):
		return ['./bootstrap.sh ' + ' '.join(self.bootstrap_flags), './b2 {} install {}'.format(' '.join(self.make_flags), S.PREFIX_CONFIGURE_FLAG)]	
