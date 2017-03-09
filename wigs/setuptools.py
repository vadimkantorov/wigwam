#class pypa(PythonWig):
#	git_uri = 'https://github.com/pypa/packaging'
#	tarball_uri = 'https://github.com/pypa/packaging/archive/$RELEASE_VERSION$.tar.gz'
#	last_release_version = '16.8'

#class pyparsing(PythonWig):
#	tarball_uri = 'https://sourceforge.net/projects/pyparsing/files/pyparsing/pyparsing-$RELEASE_VERSION$/pyparsing-$RELEASE_VERSION$.tar.gz'
#	last_release_version = 'v2.2.0'

#class appdirs(PythonWig):
#	git_uri = 'http://github.com/ActiveState/appdirs'
#	tarball_uri = 'https://github.com/ActiveState/appdirs/archive/$RELEASE_VERSION$.tar.gz'
#	last_release_version = 'v1.4.3'
	
#class runwiththis(PythonWig):
#	git_uri = 'https://github.com/jaraco'
#	tarball_uri = 'https://github.com/jaraco/rwt/archive/$RELEASE_VERSION$.tar.gz'
#	last_release_version = 'v2.14'

class setuptools(PythonWig):
	git_uri = 'https://github.com/pypa/setuptools'
	tarball_uri = 'https://github.com/pypa/setuptools/archive/v$RELEASE_VERSION$.tar.gz'
	dependencies = ['pypa', 'pyparsing', 'appdirs', 'runwiththis']
	last_release_version = 'v34.3.1'
	
	def setup(self):
		self.before_install += ['rwt -- bootstrap.py']
