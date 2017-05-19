class double_conversion(CmakeWig):
	git_uri = 'https://github.com/google/double-conversion'
	tarball_uri = 'https://github.com/google/double-conversion/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '1.1.5'

	def setup(self):
		self.cmake_flags += ['-DBUILD_SHARED_LIBS=ON']
