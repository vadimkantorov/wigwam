class libjpegturbo(Wig):
	git_uri = 'https://github.com/libjpeg-turbo/libjpeg-turbo'
	tarball_uri = 'https://github.com/libjpeg-turbo/libjpeg-turbo/archive/$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v1.5.1'
	dependencies = ['autoconf', 'automake', 'libtool', 'yasm']
