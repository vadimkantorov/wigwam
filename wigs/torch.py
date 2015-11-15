class torch(CmakeWig):
	git_uri = 'https://github.com/torch/distro'
	git_init_submodules = True
	dependencies = ['openblas', 'readline', 'ncurses', 'sdl', 'imagemagick', 'magma']
	optional_dependencies = ['gnuplot', 'fftw', 'sox']
	config_access = ['PATH_TO_NVCC', 'PATH_TO_CUDNN_SO']
	supported_features = ['qt', 'cuda', 'dsp', 'cudnn']
	default_features = ['+dsp', '+cuda', '+qt', '+cudnn']

	def luarocks_install(self, pkg):
		wig = LuarocksWig(pkg)
		wig.make_flags = self.make_flags
		return '( %s )' % '; '.join(wig.gen_install_snippet())

	def luarocks_make(self, path):
		splitted = path.split('/')
		wig = LuarocksWig(splitted[1], os.path.join(*splitted[2:]))
		wig.make_flags = self.make_flags
		return '( cd "%s"; %s )' % (os.path.join(*splitted[:2]), '; '.join(wig.gen_make_snippet()))

	def setup(self):
		self.cmake_flags += ['-DWITH_LUAJIT21=ON', '-DLIBS="-lreadline -lncurses"']
		
		self.after_install += [S.CD_PARENT]
		self.after_install += map(self.luarocks_install, ['luafilesystem', 'penlight', 'lua-cjson'])
		self.after_install += map(self.luarocks_make, [
			'pkg/sundown/rocks/sundown-scm-1.rockspec',
			'pkg/cwrap/rocks/cwrap-scm-1.rockspec',
			'pkg/paths/rocks/paths-scm-1.rockspec',
			'pkg/torch/rocks/torch-scm-1.rockspec',
			'pkg/dok/rocks/dok-scm-1.rockspec',
			'exe/trepl/trepl-scm-1.rockspec',
			'exe/env/env-scm-1.rockspec',
			'pkg/sys/sys-1.1-0.rockspec',
			'pkg/xlua/xlua-1.0-0.rockspec',
			'extra/nn/rocks/nn-scm-1.rockspec',
			'extra/nnx/nnx-0.1-1.rockspec',
			'pkg/optim/optim-1.0.5-0.rockspec',
			'extra/threads/rocks/threads-scm-1.rockspec',
			'extra/sdl2/rocks/sdl2-scm-1.rockspec', 
			'extra/argcheck/rocks/argcheck-scm-1.rockspec',
			'pkg/image/image-1.1.alpha-0.rockspec',
			'extra/graphicsmagick/graphicsmagick-1.scm-0.rockspec'
		])
	
	def switch_qt_on(self):
		self.require('gnuplot')
		self.after_install += map(self.luarocks_make, [
			'pkg/gnuplot/rocks/gnuplot-scm-1.rockspec',
			'exe/qtlua/rocks/qtlua-scm-1.rockspec',
			'pkg/qttorch/rocks/qttorch-scm-1.rockspec'
		])

	def switch_cuda_on(self):
		CUDA_BIN_PATH = os.path.dirname(self.cfg('PATH_TO_NVCC'))
		self.lib_dirs += [os.path.join(CUDA_BIN_PATH, '../lib64')]
		self.after_install += [S.export('CUDA_BIN_PATH', CUDA_BIN_PATH)]
		self.after_install += map(self.luarocks_make, [
			'extra/cutorch/rocks/cutorch-scm-1.rockspec',
			'extra/cunn/rocks/cunn-scm-1.rockspec',
			'extra/cunnx/rocks/cunnx-scm-1.rockspec',
			'extra/cudnn/cudnn-scm-1.rockspec'
		])

	def switch_cudnn_on(self):
		self.lib_dirs += [os.path.dirname(self.cfg('PATH_TO_CUDNN_SO'))]

	def switch_dsp_on(self):
		self.require('fftw')
		self.require('sox')
		self.after_install += map(self.luarocks_make, [
			'extra/audio/audio-0.1-0.rockspec',
			'extra/fftw3/rocks/fftw3-scm-1.rockspec',
			'extra/signal/rocks/signal-scm-1.rockspec'
		])
