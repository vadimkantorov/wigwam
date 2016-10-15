class scipy(PythonWig):
	tarball_uri = 'https://github.com/scipy/scipy/releases/download/v$RELEASE_VERSION$/scipy-$RELEASE_VERSION$.tar.gz'
	last_release_version = 'v0.18.1'
	git_uri = 'https://github.com/scipy/scipy'
	dependencies = ['numpy']
