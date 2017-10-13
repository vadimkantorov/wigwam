class gflags(CmakeWig):
	tar_uri = 'https://github.com/gflags/gflags/archive/v{VERSION}.tar.gz'
	git_uri = 'https://github.com/gflags/gflags'
	version = '2.1.2'
	cmake_flags = ['-DBUILD_SHARED_LIBS=ON']
