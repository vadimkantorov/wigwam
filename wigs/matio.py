class matio(AutogenWig):
  tar_uri = 'https://github.com/tbeu/matio/releases/download/v{RELEASE_VERSION}/matio-{RELEASE_VERSION}.tar.gz'
  git_uri = 'https://github.com/tbeu/matio'
  last_release_version = '1.5.10'
  dependencies = ['zlib', 'hdf5', 'libtool', 'automake']
