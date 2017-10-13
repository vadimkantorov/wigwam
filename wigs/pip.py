class pip(Wig):
	uri = 'https://bootstrap.pypa.io/get-pip.py'
	git_uri = 'https://github.com/pypa/get-pip'

	def configure(self):
		return ''

	def build(self):
		return ''

	def install(self):
		return [S.export('PYTHONUSERBASE', S.PREFIX_PYTHON), 'python "{}" --force-reinstall --ignore-installed --user pip setuptools wheel'.format(os.path.join(self.paths.src_dir, os.path.basename(self.uri)))]

#class pypa(PythonWig):
#	git_uri = 'https://github.com/pypa/packaging'
#	tar_uri = 'https://github.com/pypa/packaging/archive/{RELEASE_VERSION}.tar.gz'
#	last_release_version = '16.8'

#class pyparsing(PythonWig):
#	tar_uri = 'https://sourceforge.net/projects/pyparsing/files/pyparsing/pyparsing-{RELEASE_VERSION}/pyparsing-{RELEASE_VERSION}.tar.gz'
#	last_release_version = '2.2.0'

#class appdirs(PythonWig):
#	git_uri = 'http://github.com/ActiveState/appdirs'
#	tar_uri = 'https://github.com/ActiveState/appdirs/archive/{RELEASE_VERSION}.tar.gz'
#	last_release_version = '1.4.3'
	
#class runwiththis(PythonWig):
#	git_uri = 'https://github.com/jaraco'
#	tar_uri = 'https://github.com/jaraco/rwt/archive/{RELEASE_VERSION}.tar.gz'
#	last_release_version = '2.14'

class setuptools(PythonWig):
	git_uri = 'https://github.com/pypa/setuptools'
	tar_uri = 'https://github.com/pypa/setuptools/archive/v{RELEASE_VERSION}.tar.gz'
	dependencies = ['pypa', 'pyparsing', 'appdirs', 'runwiththis']
	last_release_version = '34.3.1'
	
	def setup(self):
		self.before_install += ['rwt -- bootstrap.py']
