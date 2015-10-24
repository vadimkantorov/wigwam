class folly(Wig):
	git_uri = 'https://github.com/facebook/folly'
	tarball_uri = 'https://github.com/facebook/folly/archive/v$RELEASE_VERSION$.tar.gz'
	working_directory = 'folly'
	dependencies = ['automake', 'autoconf', 'autoconf-archive', 'libtool', 'boost', 'libunwind', 'libiberty', 'openssl', 'libevent', 'double-conversion', 'glog', 'gflags', 'lz4', 'lzma', 'snappy', 'zlib', 'jemalloc']
	last_release_version = 'v0.57.0'
	git_commit = '68b39c3'
	sources = 'git'

	def setup(self):
		self.configure_flags += ['--with-boost-libdir="$PREFIX/lib"']
		self.before_configure += [S.export('LIBS', '-lcrypto -ldl')]
		self.before_make += [S.export(S.LDFLAGS, '-pthread -lunwind')]

	def gen_configure_snippet(self):
		return ['autoreconf -ivf', './configure %s' % ' '.join(self.configure_flags)]
