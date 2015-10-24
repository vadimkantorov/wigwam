class fblualib(CmakeWig):
	git_uri = 'https://github.com/facebook/fblualib'
	working_directory = 'fblualib'
	dependencies = ['folly', 'glog', 'torch', 'thpp', 'fbthrift', 'libedit']
	
	def luarocks_make(self, path):
		splitted = path.split('/')
		wig = LuarocksWig(splitted[0], os.path.join(*splitted[1:]))
		wig.make_flags = self.make_flags
		return '( cd "%s"; %s )' % (splitted[0], '; '.join(wig.gen_make_snippet()))

	def setup(self):
		#self.require('deb-libmatio-dev') 
		#self.require('deb-libpython-dev')
		#self.require('deb-python-numpy')
		workaround_dir = 'fblualib_rockspec_workaround'
		#self.after_make += [S.CD_PARENT, S.export(S.DESTDIR, workaround_dir)]
		self.after_make += [S.CD_PARENT] + map(lambda x: self.luarocks_make('%s/rockspec/fb%s-0.1-1.rockspec' % (x, x)), [
			'util',
			'luaunit',
			'complex',
			'ffivector',
			'editline',
			'trepl',
			'debugger',
			#'mattorch',
			#'python',
			#'thrift'
		])

		#self.after_install += [
		#	'''LUA_LIB_DIR="$PREFIX/lib/lua/5.1"''',
		#	'''LUA_MODULE_DIR="$PREFIX/share/lua/5.1"''',
		#	'''CMAKE_INSTALL_PREFIX_ASSUMED="/usr/local/lib"''',
		#	'''AWK_SCRIPT='{ system("mkdir -p \\"$(dirname \\"" TARGET $NF "\\")\\" && cp \\"" $0 "\\" \\"" TARGET $NF "\\"") }' ''',
		#	'''find .. | grep "build/%s.*\.lua$" | awk -F"/lua/" -v TARGET="$LUA_MODULE_DIR/" "$AWK_SCRIPT"''' % workaround_dir,
		#	'''find .. | grep "build/%s.*\.so$" | awk -F"$CMAKE_INSTALL_PREFIX_ASSUMED/" -v TARGET="$LUA_LIB_DIR/" "$AWK_SCRIPT"''' % workaround_dir,
		#	#'''sed -i s:\\'$CMAKE_INSTALL_PREFIX_ASSUMED/fblualib/util/libcpp.so\\':\\'$LUA_LIB_DIR/fblualib/util/libcpp.so\\':g "$LUA_MODULE_DIR/fb/util/_config.lua"'''
		#]

