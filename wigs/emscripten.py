class emscripten(Wig):
	git_uri = 'https://github.com/kripken/emscripten'
  dependencies = ['cmake', 'nodejs', 'deb-default-jre']
  
  def setup(self):
    self.skip('make')
