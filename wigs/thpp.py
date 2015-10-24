class thpp(CmakeWig):
	git_uri = 'https://github.com/facebook/thpp'
	working_directory = 'thpp'
	dependencies = ['folly', 'fbthrift', 'torch'] 

	def setup(self):
		gtest = 'gtest-1.7.0'
		self.after_fetch += [P.download('https://googletest.googlecode.com/files/%s.zip' % gtest, '%s.zip' % gtest), 'unzip %s.zip' % gtest]
		self.before_configure += ['ln -s ../%s %s' % (gtest, gtest)]
		self.before_make += [S.export(S.LDFLAGS, '-lfolly')]
