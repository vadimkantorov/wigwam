class skimage(PythonWig):
	tarball_uri = 'https://github.com/scikit-image/scikit-image/archive/v$RELEASE_VERSION$.tar.gz'
	last_release_version = '0.12.3'
	git_uri = 'https://github.com/scikit-image/scikit-image'

	dependencies = ['numpy', 'cython', 'pillow', 'matplotlib']
