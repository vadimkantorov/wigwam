class openssl(Wig):
	tar_uri = 'https://github.com/openssl/openssl/archive/OpenSSL_{version}.tar.gz'
	git_uri = 'https://github.com/openssl/openssl'
	version = '1_1_0e'

	def configure(self):
		return './config {}'.format(' '.join([[S.PREFIX_CONFIGURE_FLAG, S.FPIC_FLAG]))
