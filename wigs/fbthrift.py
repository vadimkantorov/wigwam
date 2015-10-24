class fbthrift(Wig):
	git_uri = 'https://github.com/facebook/fbthrift'
	tarball_uri = 'https://github.com/facebook/fbthrift/archive/v$RELEASE_VERSION$.tar.gz'
	working_directory = 'thrift'
	dependencies = ['folly', 'wangle', 'sasl', 'flex', 'bison', 'krb5', 'numactl', 'pkg-config', 'openssl']
	last_release_version = 'v0.31.0'

	def setup(self):
		self.before_configure += ['autoreconf --install', S.export('LIBS', '-lcrypto -ldl'), S.export('PY_PREFIX', S.PREFIX_PYTHON_PREFIXSCHEME), S.export('PY_INSTALL_HOME', S.PREFIX_PYTHON_HOMESCHEME)]
		self.configure_flags += ['--with-folly="$PREFIX"']
