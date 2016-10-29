class unzip(Wig):
	tarball_uri = 'http://downloads.sourceforge.net/infozip/unzip$RELEASE_VERSION$.tar.gz'
  last_release_version = 'v60'
  
  def setup(self):
    self.skip('configure')
    self.make_flags += ['-f', 'unix/Makefile']
