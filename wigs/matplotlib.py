class matplotlib(PythonWig):
	tarball_uri = 'https://github.com/matplotlib/matplotlib/archive/v{RELEASE_VERSION}.tar.gz'
	last_release_version = '2.0.0b4'
	git_uri = 'https://github.com/matplotlib/matplotlib'
	dependencies = ['numpy', 'freetype', 'pkg-config', 'libpng']
