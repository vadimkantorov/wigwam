class opencv(CmakeWig):
	tar_uri = 'https://github.com/itseez/opencv/archive/{version}.tar.gz'
	git_uri = 'https://github.com/itseez/opencv'
	version = '3.2.0'
	dependencies = ['pkg-config']
	#default_features = ['+shared', '-tests', '-examples', '-cuda', '-python', '+ffmpeg', '-ipp']

	def switch_ipp(self, on):
		self.cmake_flags += ['-DWITH_IPP={}'.format(S.ONOFF(on))]

	def switch_contrib_on(self):
		self.require('opencv_contrib')
		self.cmake_flags += ['-DOPENCV_EXTRA_MODULES_PATH="{}"'.format(os.path.join(self.paths.src_dir, '../opencv_contrib/modules'))]

	def switch_ffmpeg_on(self):
		self.require('ffmpeg')
		self.before_configure += [S.export(S.PKG_CONFIG_PATH, "$PREFIX/lib/pkgconfig")]

	def switch_python_on(self):
		self.require('numpy')
		self.cmake_flags += ['-DBUILD_opencv_python2={}'.format(S.ONOFF(True))]
		#self.cmake_flags += ['-DPYTHON2_PACKAGES_PATH="%s"' % os.path.join(P.prefix_python, P.python_prefix_scheme[0])]
	
	def switch_cuda(self, on):
		self.cmake_flags += ['-DWITH_CUDA={}'.format(S.ONOFF(on))]

	def switch_shared(self, on):
		self.cmake_flags += ['-DBUILD_SHARED_LIBS={}'.format(S.ONOFF(on))]

	def switch_tests(self, on):
		self.cmake_flags += ['-DBUILD_{}={}'.format(feat_name, S.ONOFF(on)) for feat_name in ['TESTS', 'PERF_TESTS']]

	def switch_examples(self, on):
		self.cmake_flags += ['-DBUILD_EXAMPLES={}'.format(S.ONOFF(on))]
