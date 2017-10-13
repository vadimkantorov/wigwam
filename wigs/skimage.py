class skimage(PythonWig):
	tar_uri = 'https://github.com/scikit-image/scikit-image/archive/v{version}.tar.gz'
	git_uri = 'https://github.com/scikit-image/scikit-image'
	version = '0.12.3'
	dependencies = ['numpy', 'cython', 'pillow', 'matplotlib']
