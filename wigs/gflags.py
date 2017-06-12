class gflags(CmakeWig):
	git_uri = 'https://github.com/gflags/gflags'
	tar_uri = 'https://github.com/gflags/gflags/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '2.1.2'
	
	def setup(self):
		self.cmake_flags += ['-DBUILD_SHARED_LIBS=ON']
