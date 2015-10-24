class fbtorch(LuarocksWig):
	git_uri = 'https://github.com/facebook/fbtorch.git'
	rockspec_path = 'rocks/fbtorch-scm-1.rockspec'
	dependencies = ['torch', 'fblualib', 'fbnn', 'fbcunn']
