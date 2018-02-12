class magma(Wig):
	tarball_uri = 'http://icl.cs.utk.edu/projectsfiles/magma/downloads/magma-{RELEASE_VERSION}.tar.gz'
	dependencies = ['openblas']
	last_release_version = '2.3.0'
	config_access = ['PATH_TO_NVCC']
	
	def setup(self):
		self.make_install_flags += [S.prefix_MAKE_INSTALL_FLAG]

	def gen_configure_snippet(self):
		config_fixes = '''| sed 's$#OPENBLASDIR ?=$OPENBLASDIR ?= '$PREFIX'#OPENBLASDIR ?=$' '''
		config_fixes += '''| sed 's$#CUDADIR ?=$CUDADIR ?= '%s'#CUDADIR ?=$' ''' % os.path.join(os.path.dirname(self.cfg('PATH_TO_NVCC')), '..')
		config_fixes += '''| sed '$aLIB += -lm' '''
		config_fixes += '''| sed '$aNVCC = $(CUDADIR)/bin/nvcc' '''
		config_fixes += '''| sed '$aCFLAGS += -D_GLIBCXX_USE_C99 -D_GLIBCXX_USE_C99_MATH' '''
		return ['cat make.inc-examples/make.inc.openblas %s > make.inc' % config_fixes]
