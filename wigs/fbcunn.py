class fbcunn(LuarocksWig):
	git_uri = 'https://github.com/facebook/fbcunn.git'
	rockspec_path = 'rocks/fbcunn-scm-1.rockspec'
	dependencies = ['torch', 'fbnn']
	config_access = ['PATH_TO_CUDNN_SO']
	supported_features = ['cudnn']
	default_features = ['+cudnn']

	def switch_cudnn_on(self):
		self.lib_dirs += [os.path.dirname(self.cfg('PATH_TO_CUDNN_SO'))]
