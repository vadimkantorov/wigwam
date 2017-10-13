class pip(Wig):
	uri = 'https://bootstrap.pypa.io/get-pip.py'
	git_uri = 'https://github.com/pypa/get-pip'

	def configure(self):
		return ''

	def build(self):
		return ''

	def install(self):
		return [S.export('PYTHONUSERBASE', S.PREFIX_PYTHON), 'python "{}" --force-reinstall --ignore-installed --user pip setuptools wheel'.format(os.path.join(self.paths.src_dir, os.path.basename(self.uri)))]
