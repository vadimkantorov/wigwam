class double_conversion(CmakeWig):
	tar_uri = 'https://github.com/google/double-conversion/archive/v{VERSION}.tar.gz'
	git_uri = 'https://github.com/google/double-conversion'
	version = '1.1.5'
	cmake_flags = ['-DBUILD_SHARED_LIBS=ON']
