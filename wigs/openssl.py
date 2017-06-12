class openssl(Wig):
	tar_uri = 'https://github.com/openssl/openssl/archive/OpenSSL_{RELEASE_VERSION}.tar.gz'
	git_uri = 'https://github.com/openssl/openssl'
	last_release_version = '1_1_0e'
	

	def setup(self):
		self.configure_flags += [S.FPIC_FLAG]

	def configure(self):
		return './config %s' % ' '.join(self.configure_flags)
