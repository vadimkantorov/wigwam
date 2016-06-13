class x264(Wig):
  git_uri = 'http://git.videolan.org/git/x264.git'
  
  def setup(self):
    self.configure_flags += ['--enable-static']
