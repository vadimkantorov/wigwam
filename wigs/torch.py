class torch(CmakeWig):
	git_uri = 'https://github.com/torch/distro'
	dependencies = ['openblas', 'readline', 'ncurses', 'gnuplot', 'libjpeg', 'unzip', 'cmake']
	
	@staticmethod
	def luarocks_make(rockspec_path):
		splitted = rockspec_path.split('/')
		pkg_name = splitted[1]
		working_directory = os.path.join(*splitted[:2])
		rockspec_path = os.path.join(*splitted[2:])
		return '( cd "%s"; %s )' % (working_directory, '; '.join(LuarocksWig(pkg_name, rockspec_path).install()))

	cmake_flags = ['-DWITH_LUAJIT21=ON', '-DLIBS="-lreadline -lncurses"']
	after_install = [S.CD_PARENT] + map(torch.luarocks_make, [
		# Installing common lua packages
		'extra/luafilesystem/rockspecs/luafilesystem-1.6.3-1.rockspec',
		'extra/penlight/penlight-scm-1.rockspec',
		'extra/lua-cjson/lua-cjson-2.1devel-1.rockspec',
		
		# Installing core Torch packages
		'extra/luaffifb/luaffi-scm-1.rockspec',
		'pkg/sundown/rocks/sundown-scm-1.rockspec',
		'pkg/cwrap/rocks/cwrap-scm-1.rockspec',
		'pkg/paths/rocks/paths-scm-1.rockspec',
		'pkg/torch/rocks/torch-scm-1.rockspec',
		'pkg/dok/rocks/dok-scm-1.rockspec',
		'exe/trepl/trepl-scm-1.rockspec',
		'pkg/sys/sys-1.1-0.rockspec',
		'pkg/xlua/xlua-1.0-0.rockspec',
		'extra/nn/rocks/nn-scm-1.rockspec',
		'extra/graph/rocks/graph-scm-1.rockspec',
		'extra/nngraph/nngraph-scm-1.rockspec',
		'pkg/image/image-1.1.alpha-0.rockspec',
		'pkg/optim/optim-1.0.5-0.rockspec',
		
		# Installing optional Torch packages
		'pkg/gnuplot/rocks/gnuplot-scm-1.rockspec',
		'exe/env/env-scm-1.rockspec',
		'extra/nnx/nnx-0.1-1.rockspec',
		'extra/threads/rocks/threads-scm-1.rockspec',
		'extra/argcheck/rocks/argcheck-scm-1.rockspec',
	])

	def cuda(self, on = True):
		self.require('magma')
		CUDA_BIN_PATH = os.path.dirname(self.getenv('PATH_TO_NVCC'))
		self.lib_dirs += [os.path.join(CUDA_BIN_PATH, '../lib64')]
		self.after_install += [S.export('CUDA_BIN_PATH', CUDA_BIN_PATH)]
		self.after_install += map(torch.luarocks_make, [
			'extra/cutorch/rocks/cutorch-scm-1.rockspec',
			'extra/cunn/rocks/cunn-scm-1.rockspec',
			'extra/cudnn/cudnn-scm-1.rockspec'
		])

	def cudnn(self, on = True):
		self.lib_dirs += [os.path.dirname(self.getenv('PATH_TO_CUDNN_SO'))]
	
	def qt(self, on = True):
		self.after_install += map(torch.luarocks_make, [
			'exe/qtlua/rocks/qtlua-scm-1.rockspec',
			'pkg/qttorch/rocks/qttorch-scm-1.rockspec'
		])
