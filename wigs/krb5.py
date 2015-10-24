class krb5(Wig):
	tarball_uri = 'https://github.com/krb5/krb5/archive/krb5-$RELEASE_VERSION$-final.tar.gz'
	working_directory = 'src'
	last_release_version = 'v1.13.2'
	dependencies = ['openssl']

	def setup(self):
		ldl = [S.export(S.LIBS, '-ldl'), S.export(S.LDFLAGS, '-ldl'), S.export(S.CFLAGS, '-ldl')] # for static linking with OpenSSL
		self.before_configure += ['./util/reconf --force'] + ldl
		self.before_make += ldl
		self.make_install_flags = [S.DESTDIR_MAKE_INSTALL_FLAG]
