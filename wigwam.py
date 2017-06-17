import os
import re
import sys
import time
import json
import pipes
import shutil
import urllib2
import urlparse
import argparse
import itertools
import traceback
import subprocess
import multiprocessing

class P:
	bugreport_page = 'http://github.com/vadimkantorov/wigwam/issues'
	wigwamdirname = '.wigwam'
	wigwamfilename = 'Wigwamfile'
	userwigdir = 'wigs'
	python_prefix_scheme = ('lib/python{0}.{1}/site-packages'.format(*sys.version_info), 'bin', 'include/python{0}.{1}'.format(*sys.version_info))
	
	@staticmethod
	def init(root, wigwamfile, extra_repos):
		P.root = root
		p = lambda x: os.path.join(P.root, x)

		P.wigwamfile = wigwamfile
		P.src_tree = p('src')
		P.prefix = p('prefix')
		P.prefix_deb = os.path.join(P.prefix, 'deb')
		P.prefix_python = os.path.join(P.prefix, 'python')
		P.log_root = p('log')
		P.tar_root = p('tar')
		P.deb_root = p('deb')
		P.debug_root = p('debug')
		
		P.activate_sh = p('wigwam_activate.sh')
		P.build_script = p('build.generated.sh')
		P.wigwamfile_installed = p(P.wigwamfilename + '.installed')
				
		python_module_path,  python_bin_path, python_include_path = [os.path.join(P.prefix_python, path_component) for path_component in P.python_prefix_scheme]
		P.prefix_bin_dirs = [os.path.join(P.prefix, 'bin'), os.path.join(P.prefix_deb, 'usr/bin'), python_bin_path]
		P.prefix_lib_dirs = [os.path.join(P.prefix, 'lib64'), os.path.join(P.prefix, 'lib'), os.path.join(P.prefix_deb, 'usr/lib'), os.path.join(P.prefix_deb, 'usr/lib/x86_64-linux-gnu')]
		P.prefix_include_dirs = [os.path.join(P.prefix, 'include'), os.path.join(P.prefix_deb, 'usr/include'), python_include_path]
		P.prefix_python_dirs = [python_module_path]
		
		P.artefact_dirs = [P.src_tree, P.prefix, P.log_root, P.tar_root, P.deb_root, P.debug_root] + [python_module_path, python_bin_path, python_include_path]
		P.generated_files = [P.build_script, P.wigwamfile_installed, P.activate_sh]
		P.all_dirs = [P.root] + P.artefact_dirs
		P.repos = [P.userwigdir] + extra_repos

		P.log_base = staticmethod(lambda wig_name: os.path.join(P.log_root, wig_name))
		P.debug_script = staticmethod(lambda wig_name: os.path.join(P.debug_root, wig_name + '.sh'))
		
class S:
	LDFLAGS = 'LDFLAGS'
	CFLAGS = 'CFLAGS'
	CXXFLAGS = 'CXXFLAGS'
	CPPFLAGS = 'CPPFLAGS'
	LIBS = 'LIBS'
	PATH = 'PATH'
	LD_LIBRARY_PATH = 'LD_LIBRARY_PATH'
	CPATH = 'CPATH'
	PKG_CONFIG_PATH = 'PKG_CONFIG_PATH'
	LIBRARY_PATH = 'LIBRARY_PATH'
	PYTHONPATH = 'PYTHONPATH'
	MATLABPATH = 'MATLABPATH'
	DESTDIR = 'DESTDIR'
	CMAKE_PREFIX_PATH = 'CMAKE_PREFIX_PATH'
	PREFIX_PYTHON = '$PREFIX/python'
	PREFIX_CONFIGURE_FLAG = '--prefix="$PREFIX"'
	prefix_MAKE_INSTALL_FLAG = 'prefix="$PREFIX"'
	PREFIX_MAKE_INSTALL_FLAG = 'PREFIX="$PREFIX"'
	DESTDIR_MAKE_INSTALL_FLAG = 'DESTDIR="$PREFIX"'
	WIGWAM_PREFIX = 'WIGWAM_PREFIX'
	FPIC_FLAG = '-fPIC'
	CMAKE_INSTALL_PREFIX_FLAG = '-DCMAKE_INSTALL_PREFIX="$PREFIX"'
	CMAKE_PREFIX_PATH_FLAG = '-DCMAKE_PREFIX_PATH="$PREFIX"'
	MKDIR_CD_BUILD = 'mkdir -p build && cd build'
	CD_BUILD = 'cd build'
	CD_PARENT = 'cd ..'
	MAKEFLAGS = 'MAKEFLAGS'
	
	download = staticmethod(('wget {} -O "{}"' if 0 == subprocess.call(['which', 'wget'], stdout = subprocess.PIPE, stderr = subprocess.PIPE) else 'curl {} -o "{}"').format)
	mkdir_p = staticmethod('mkdir -p "{}"'.format)
	make_jobs = staticmethod('-j{}'.format)
	export = staticmethod('export {}="{}"'.format)
	export_prepend_paths = staticmethod(lambda var_name, paths: S.export(var_name, os.path.pathsep.join(paths + ['$' + var_name])))
	configure = staticmethod(lambda flags: './configure {}'.format(' '.join(flags)))
	onoff = staticmethod({True : 'on', False : 'off'}.get)
	ONOFF = staticmethod({True : 'ON', False : 'OFF'}.get)
	make = staticmethod(lambda flags: 'make {}'.format(' '.join(flags)))
	makeflags = staticmethod(lambda flags: '{}="{} {}"'.format(S.MAKEFLAGS, ' '.join(flags), os.getenv(S.MAKEFLAGS, '')) if flags else '')
	make_install = staticmethod(lambda flags: 'make install {}'.format(' '.join(flags)))
	python_setup_install = 'python setup.py install --prefix="{}"'.format(PREFIX_PYTHON)
	ln = staticmethod('ln -f -s "{}" "{}"'.format)
	qq = staticmethod('"{}"'.format)
	rm_rf = staticmethod(lambda *args: 'rm -rf {}'.format(' '.join(map(S.qq, args))))

class Wig(object):
	git_branch = None
	git_commit = None
	git_init_submodules = None
	tar_strip_components = None
	working_directory = '.'
	fetch_method = None
	version = None

	config_access = []
	dependencies = []
	optional_dependencies = []
	supported_features = []
	skip_stages = []

	all_installation_stages = ['fetch', 'configure', 'build', 'install']
	
	def __init__(self, name):
		self.name = name

		self.bin_dirs = []
		self.lib_dirs = []
		self.include_dirs = []
		self.python_dirs = []

		self.configure_flags = [S.PREFIX_CONFIGURE_FLAG]
		self.make_flags = [S.make_jobs(multiprocessing.cpu_count())]
		self.make_install_flags = self.make_flags[:]

		self.before_fetch = []
		self.after_fetch = []
		self.before_configure = []
		self.after_configure = []
		self.before_make = []
		self.after_make = []
		self.before_install = []
		self.after_install = []

		self.env = {}
		self.enabled_features = []
		self.disabled_features = []
		self.dependencies_ = set()
		self.fetch_method = self.fetch_method or ('tar' if hasattr(self, 'tar_uri') else 'git' if hasattr(self, 'git_uri') else None)
		self.paths = type('', None, dict(src_dir = os.path.join(P.src_tree, wig.name)))()

	def dict_config(self):
		if self.fetch_method == 'tar':
			return dict(fetch_params = dict(fetch_method = self.fetch_method, version = self.version))
		elif self.fetch_method == 'git':
			find_last_git_commit = lambda: [commit for commit, head in map(str.split, filter(bool, subprocess.check_output(['git', 'ls-remote', self.git_uri]).split('\n'))) if (self.git_branch or 'HEAD') in head][0][:7]
			return dict(fetch_params = dict(fetch_method = self.fetch_method, git_commit = self.git_commit or find_last_git_commit(), git_branch = self.git_branch))
		else:
			return {}
	
	def load_dict_config(self, dict_config, dict_env):
		self.env = dict_env
		self.enabled_features += dict_config['enabled_features']
		self.disabled_features += dict_config['disabled_features']
		self.fetch_params = dict(self.__dict__.items() + dict_config['fetch_params'].items())

	def trace(self):
		return dict(self.fetch_params.items() + dict(enabled_features = self.enabled_features, disabled_features = self.disabled_features).items())
	
	def fetch(self):
		def git(target_dir, git_uri, git_commit = None, git_branch = None, git_tag = None, **ignored):
			tag = git_tag or git_commit or git_branch
			return [S.rm_rf(target_dir), 'git clone --recursive "{}" "{}"'.format(git_uri, target_dir)] + (['cd "{}"'.format(target_dir), 'git checkout "{}"'.format(tag)] if tag is not None else [])

		def tar(target_dir, tar_uri, tar_strip_components = 1, **ignored):
			downloaded_file_path = os.path.join(P.tar_root, os.path.basename(target_dir) + [e for e in ['.tar', '.tar.gz', '.tar.bz2', '.tgz'] if uri.endswith(e)][0])
			return [S.rm_rf(target_dir), S.mkdir_p(target_dir), S.download(uri, downloaded_file_path), 'tar -xf "{}" -C "{}" --strip-components={}'.format(downloaded_file_path, target_dir, tar_strip_components]

		def uri(target_dir, uri, **ignored):
			downloaded_file_path = os.path.join(target_dir, os.path.basename(uri))
			return [S.rm_rf(target_dir), S.mkdir_p(target_dir), S.download(uri, downloaded_file_path)]

		return locals()[fetch_params['fetch_method']](self.paths.src_dir, **self.fetch_params)
	
	def configure(self):
		return S.configure(self.configure_flags)

	def build(self):
		return S.make(self.make_flags)

	def install(self):
		return S.make_install(self.make_install_flags) if 'install' not in self.skip_stages else []

	def setup(self):
		pass

	def switch(self, feat_name, on):
		pass

	def process_feature_hooks(self):
		for on, feat_name in zip(itertools.repeat(True), self.enabled_features) + zip(itertools.repeat(False), self.disabled_features):
			f1, f2 = 'switch_{}_{}'.format(feat_name, S.onoff(on)), 'switch_{}'.format(feat_name)
			if hasattr(self, f1):
				getattr(self, f1)()
			else:
				getattr(self, f2)(on)

	def getenv(self, name):
		return self.env.get(name)

	def require(self, wig_name):
		self.dependencies_.append(wig_name)

class DictConfig(dict):
	@staticmethod
	def read(path):
		with open(path, 'r') as f:
			return DictConfig(json.load(f) if os.path.exists(path) else {})

	def save(self, path):
		with open(path, 'w') as f:
			json.dump(dict(self), f, indent = 2, sort_keys = True)

	def patch(self, diff):
		dict_config = self.copy()
		if '_config' in diff:
			dict_config['_config'] = dict(dict_config.get('_config', {}).items() + diff.pop('_config', {}).items())
		for wig_name, y in diff.items():
			if wig_name not in dict_config:
				dict_config[wig_name] = y
			else:
				if DictConfig.SOURCES in y:
					dict_config[wig_name][DictConfig.SOURCES] = y[DictConfig.SOURCES]
				if DictConfig.FEATURES in y:
					dict_config[wig_name][DictConfig.FEATURES] = dict_config[wig_name].get(DictConfig.FEATURES, '') + ' ' + y.get(DictConfig.FEATURES, '')
		
		return dict_config
	
	def copy(self):
		return DictConfig(self.copy())

class WigConfig:
	def __init__(self, dict_config):
		dict_config = dict_config.copy()
		self.env = dict_config.pop('_config', {})

		self.wigs = {}
		for wig_name, wig_dict_config in dict_config.items():
			wig = WigConfig.find_and_construct_wig(wig_name)
			wig.load_dict_config(wig_dict_config, self.env)
			for dep_wig_name in wig.dependencies:
				wig.require(dep_wig_name)
			wig.setup()
			wig.require(enabled_features = wig.enabled_features + wig_dict_config['enabled_features'])
			wig.require(disabled_features = wig.disabled_features + wig_dict_config['disabled_features'])
			self.wigs[wig_name] = wig

		for wig_name in self.wigs.keys():
			self.wigs[wig_name].process_feature_hooks()

		flatten = lambda xs: list(itertools.chain(*xs))
		self.bin_dirs = P.prefix_bin_dirs + flatten(map(lambda wig: wig.bin_dirs, self.wigs.values()))
		self.lib_dirs = P.prefix_lib_dirs + flatten(map(lambda wig: wig.lib_dirs, self.wigs.values()))
		self.include_dirs = P.prefix_include_dirs + flatten(map(lambda wig: wig.include_dirs, self.wigs.values()))
		self.python_dirs = P.prefix_python_dirs + flatten(map(lambda wig: wig.python_dirs, self.wigs.values()))

	@staticmethod
	def find_and_construct_wig(wig_name):
		shortcut = [s for k, s in {'deb-' : DebWig, 'lua-' : LuarocksWig, 'pip-' : PipWig}.items() if wig_name.startswith(k)]
		if shortcut:
			return shortcut[0](wig_name)

		find_class = lambda: {cls.__name__ : cls for cls in globals().values() if isinstance(cls, type) and issubclass(cls, Wig) and cls != Wig}.get(wig_name.replace('-', '_'))
		cls = None

		for repo in P.repos:
			opener = open if 'github.com' not in repo else urllib2.urlopen
			try:
				content = opener(os.path.join(repo.replace('github.com', 'raw.githubusercontent.com').replace('/tree/', '/'), wig_name + '.py')).read()
			except:
				content = ''

			if content and content != 'Not Found':
				exec content in globals(), globals()
				cls = find_class()
				break

		if cls == None:
			print 'Package [{}] cannot be found. Quitting.'.format(wig_name)
			sys.exit(1)

		return cls(wig_name)

	@staticmethod
	def dfs(graph, seeds, on_black = lambda wig_name: None):
		visited = set()
		installation_order = []
		def dfs_(u):
			visited.add(u)
			for v in graph[u]:
				if v not in visited:
					dfs_(v)
			on_black(u)
		
		for	u in seeds:
			if u not in visited:
				dfs_(u)
		return visited

	@staticmethod
	def topological_sort(graph):
		installation_order = []
		WigConfig.dfs(graph, graph.keys(), lambda wig_name: installation_order.append(wig_name))
		return installation_order

	def compute_installation_order(self, reconfigured, up = False, down = False, wig_name_subset = None):
		if wig_name_subset == None:
			wig_name_subset = self.wigs.keys()

		if up:
			graph = {wig_name: [k for k in wig_name_subset if wig_name in self.wigs[k].dependencies_] for wig_name in wig_name_subset}
		else:
			graph = {wig_name: filter(lambda x: x in wig_name_subset, self.wigs[wig_name].dependencies_) for wig_name in wig_name_subset}
		
		to_install = WigConfig.dfs(graph, reconfigured)
		graph = {wig_name : filter(lambda x: x in to_install, self.wigs[wig_name].dependencies_) for wig_name in to_install}
		return WigConfig.topological_sort(graph)
	
	def get_immediate_unsatisfied_dependencies(self):
		return {x : [] for x in set((dep_wig_name for wig in self.wigs.values() for dep_wig_name in wig.dependencies_ if dep_wig_name not in self.wigs.keys()))}

	def diff(self, graph):
		s = lambda e: set(e) if isinstance(e, list) else set([e])
		fingerprint = lambda w: set(filter(bool, set.union(*map(s, map(w.trace().get, [DictConfig.URI, DictConfig.VERSION, DictConfig.GIT_COMMIT, DictConfig.FEATURES, DictConfig.DEPENDS_ON]))))) if w != None else set(['N/A'])

		to_install = {}
		for wig_name, wig in self.wigs.items():
			other = graph.wigs.get(wig_name)
			other_fingerprint = fingerprint(other)
			other_sources = other.sources if other != None else None
			other_features_on_off = other.features_on_off if other != None else []
			
			if fingerprint(wig) != other_fingerprint:
				to_install[wig_name] = {}
				features_on_off = [feat for feat in wig.features_on_off if feat not in other_features_on_off]
				if len(features_on_off) > 0:
					to_install[wig_name][DictConfig.FEATURES] = ' '.join(features_on_off)
				if wig.sources != other_sources:
					to_install[wig_name][DictConfig.SOURCES] = wig.sources
			
		return DictConfig(to_install)

class CmakeWig(Wig):
	def __init__(self, name):
		Wig.__init__(self, name)
		self.cmake_flags = [S.CMAKE_INSTALL_PREFIX_FLAG, S.CMAKE_PREFIX_PATH_FLAG]
		self.before_make = [S.CD_BUILD]
		self.before_install = [S.CD_BUILD]
		self.dependencies_ += ['cmake']

	def configure(self):
		return [S.MKDIR_CD_BUILD, 'cmake {} ..'.format(' '.join(self.cmake_flags))]

	def switch_debug(self, on):
		self.cmake_flags += ['-D CMAKE_BUILD_TYPE={}'.format('DEBUG' if on else 'RELEASE')]

class AutogenWig(Wig):
	def __init__(self, name):
		Wig.__init__(self, name)
		self.before_configure += ['bash autogen.sh']

class LuarocksWig(Wig):
	skip_stages = ['fetch', 'configure', 'build']
	LUAROCKS_PATH = '$PREFIX/bin/luarocks'
	rockspec_path = None
	
	def __init__(self, name, rockspec_path = None):
		Wig.__init__(self, name)
		if rockspec_path != None:
			self.rockspec_path = rockspec_path
	
	def install(self):
		return [S.export(S.CMAKE_PREFIX_PATH, '$PREFIX'), '{} {} make {}'.format(S.makeflags(self.make_flags), LuarocksWig.LUAROCKS_PATH, self.rockspec_path)] if self.rockspec_path else [S.export(S.CMAKE_PREFIX_PATH, '$PREFIX'), '{} {} install {}'.format(S.makeflags(self.make_flags), LuarocksWig.LUAROCKS_PATH, self.name[len('lua-'):])]

class DebWig(Wig):
	skip_stages = ['build']
	APT_GET_OUTPUT_CACHE = {}

	def __init__(self, name):
		Wig.__init__(self, name)
		if self.name not in DebWig.APT_GET_OUTPUT_CACHE:
			DebWig.APT_GET_OUTPUT_CACHE[self.name] = subprocess.check_output(['apt-get', '--print-uris', '--yes', '--reinstall', 'install', self.name[len('deb-'):]])

		self.deb_uris = re.findall("'(http.+)'", DebWig.APT_GET_OUTPUT_CACHE[self.name]) or []
		self.cached_deb_paths = [os.path.join(P.deb_root, os.path.basename(uri)) for uri in self.deb_uris]
		if len(self.deb_uris) == 0:
			self.skip_stages += Wig.all_installation_stages

	def load_dict_config(self, *ignored):
		self.fetch_params = dict(uri = ', '.join(self.deb_uris))
	
	def fetch(self):
		return [S.download(uri, downloaded_file_path) for uri, downloaded_file_path in zip(self.deb_uris, self.cached_deb_paths)]
	
	def install(self):
		return ['dpkg -x "{}" "{}"'.format(downloaded_file_path, P.prefix_deb) for downloaded_file_path in self.cached_deb_paths]

class PythonWig(Wig):
	skip_stages = ['configure', 'build']

	def install(self):
		return [S.python_setup_install]

class PipWig(Wig):
	skip_stages = ['fetch', 'configure', 'build']
	PIP_PATH = 'pip' # '$PREFIX/bin/pip'
	wheel_path = None

	def install(self):
		return [S.export('PYTHONUSERBASE', S.PREFIX_PYTHON), '"{}" install --force-reinstall --ignore-installed --user {}'.format(PipWig.PIP_PATH, self.name[len('pip-'):] if self.wheel_path is None else self.wheel_path)]

def install(wig_names, enable, disable, git, version, dry, config, reinstall, only, dangerous, verbose):
	init()

	assert not only or dangerous
	
	old = DictConfig.read(P.wigwamfile)
	end = old.patch(dict(_config = dict(map(lambda x: x.split('='), config))))
	for wig_name in wig_names:
		dict_config = WigConfig.find_and_construct_wig(wig_name).dict_config()
		if enable:
			dict_config['enabled_features'] = enable
		if disable:
			dict_config['disabled_features'] = disable
		if git:
			dict_config['fetch_params']['git_tag'] = git
		if version:
			dict_config['fetch_params']['version'] = version
		end = end.patch({wig_name : dict_config})
	
	end.save(P.wigwamfile)
	build(dry = dry, old = old, seeds = wig_names, force_seeds_reinstall = reinstall, install_only_seeds = only, verbose = verbose)

def upgrade(wig_names, dry, only, dangerous):
	init()

	assert not only or dangerous

	old = DictConfig.read(P.wigwamfile)
	end = old.copy()

	if not wig_names:
		wig_names = filter(lambda x: x != '_config', old.keys())

	for wig_name in wig_names:
		if wig_name not in old:
			print 'Package [{}] not installed or requested. Cannot upgrade, call install first.'.format(wig_name)
			return

		dict_config = WigConfig.find_and_construct_wig(wig_name).dict_config()
		if dict_config.get(DictConfig.SOURCES, None) != old[wig_name].get(DictConfig.SOURCES, None):
			print 'Going to upgrade package [{}]: {} -> {}'.format(wig_name, old[wig_name].get(DictConfig.SOURCES, None), dict_config.get(DictConfig.SOURCES, None))
			end.patch({wig_name : {DictConfig.SOURCES : dict_config[DictConfig.SOURCES]}})

	end.save(P.wigwamfile)
	build(dry = dry, old = old, seeds = wig_names, install_only_seeds = only)

def build(dry, old = None, seeds = [], force_seeds_reinstall = False, install_only_seeds = False, verbose = False):
	dump_env = '''function dump_env {
	echo "PWD=$PWD"
	echo "PATH=$PATH"
	echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
	echo "CPATH=$CPATH"
	echo "LIBRARY_PATH=$LIBRARY_PATH"
	echo "g++ -print-search-dirs: $(g++ -print-search-dirs)"
}'''
	def gen_installation_script(installation_script_path, wigs, env, installation_order):
		if os.path.exists(installation_script_path):
			os.remove(installation_script_path)

		if not installation_order:
			return

		print '{} packages to be installed in the order below:'.format(len(installation_order))
		for wig_name in installation_order:
			print ('%10s' % wig_name) + ('    requires  {}'.format(', '.join(wigs[wig_name].dependencies_)) if wigs[wig_name].dependencies_ else '')
		print ''

		with open(installation_script_path, 'w') as out:
			def w(x, prepend = '', stream = out):
				if x != []:
					print >> stream, '\n'.join([prepend + y for y in x]) if isinstance(x, list) else prepend + x
		
			w(''''set -e # set -evx for debugging
			trap show_log EXIT')
			trap on_ctrl_c SIGINT')
			exec 3>&1')
			source "{}"
			TIC="$(date +%s)"
	function show_log {
		exec 1>&3
		if [ -z $ALLOK ] || [ $CTRLCPRESSED ]
		then
			printf "error!\n\n"
			echo "Error occurred while installing [$PACKAGE_NAME]. Press <ENTER> to open [$LOG], press <ESC> to quit."
			read -s -n1 key
			case $key in
				$'\e') echo Quitting;;
				$'') less $LOG;;
			esac
			reset
			exit 1
		fi
		exit 0
	}
	
	function on_ctrl_c {
		exec 1>&3
		echo "<CTRL+C> pressed. Aborting"
		CTRLCPRESSED=1
		reset
		exit 1
	}
	function update_wigwamfile_installed {
		python -c "import sys, json; installed, diff = map(json.load, [open(sys.argv[-1]), sys.stdin]); installed.update(diff); json.dump(installed, open(sys.argv[-1], 'w'), indent = 2, sort_keys = True)" $@
	}
	'''.replace('{}', P.activate.sh))
			w(dump_env)
			w(S.rm_rf(*[P.log_base(wig_name) for wig_name in installation_order]))

			def update_wigwamfile_installed(d):
				w('''cat <<"EOF" | update_wigwamfile_installed "{}"
	{}
	EOF
	'''.format(os.path.abspath(P.wigwamfile_installed), json.dumps(d)))
			update_wigwamfile_installed(dict(_config = env))
			class Stage:
				def __init__(self, name, file_name, skip, hook = lambda x, prepend: None):
					self.name = name
					self.file_name = file_name
					self.skip = skip
					self.hook = hook
				
				def __enter__(self):
					if self.skip:
						return lambda x: None
					else:
						w('printf "%%14s...  " {}'.format(self.name))
						w('LOG="$LOGBASE/{}"'.format(self.file_name))
						w('(')
						self.hook('(', '')
						def inner(x):
							w(x, '\t')
							self.hook(x, '\t')
						return inner

				def __exit__(self, type, value, traceback):
					if not self.skip:
						w(') > "$LOG" 2>&1')
						self.hook(')', '')
						w('TOC="$(($(date +%s)-TIC))"; echo "ok [elapsed $((TOC/60%60))m$((TOC%60))s]"')
			for wig_name in installation_order:
				wig = wigs[wig_name]
				s = lambda *xs: any([x in wig.skip_stages for x in xs])
				debug_script_path = P.debug_script(wig_name)

				w('')
				w('PACKAGE_NAME={}'.format(wig_name))
				w('printf "\\n$PACKAGE_NAME:\\n"')
				if not s('all'):
					w('cd "{}"'.format(P.root))
					w('PREFIX="{}"'.format(P.prefix))
					w('LOGBASE="{}"'.format(P.log_base(wig_name)))
					w(S.mkdir_p('$LOGBASE'))
		
				with Stage('Fetching', 'fetch.txt', s('all', 'fetch')) as u:
					u(wig.before_fetch)
					u('dump_env')
					u(wig.fetch())
					u(wig.after_fetch)
				
				w(S.mkdir_p(wig.paths.src_dir))
				w(S.ln(os.path.abspath(debug_script_path), os.path.join(wig.paths.src_dir, 'wigwam_debug.sh')))
				with open(debug_script_path, 'w') as out_debug:
					d = lambda x, prepend = '': x != 'dump_env' and w(x, prepend, out_debug)
					if not s('all', 'fetch'):
						w('cd "{}"'.format(os.path.join(wig.paths.src_dir, wig.working_directory)))
						d('cd "{}"'.format(os.path.abspath(os.path.join(wig.paths.src_dir, wig.working_directory))))

					d('''PREFIX="{}"'''.format(os.path.abspath(P.prefix)))
					d('source "{}"'.format(P.activate_sh))
					d([dump_env])

					with Stage('Configuring', 'configure.txt', s('all', 'fetch', 'configure'), hook = d) as u:
						u(wig.before_configure)
						u('dump_env')
						u(wig.configure())
						u(wig.after_configure)

					with Stage('Compiling', 'build.txt', s('all', 'fetch', 'build'), hook = d) as u:
						u(wig.before_make)
						u('dump_env')
						u(wig.build())
						u(wig.after_make)

					with Stage('Installing', 'install.txt', s('all', 'install'), hook = d) as u:
						u(wig.before_install)
						u('dump_env')
						u(wig.install())
						u(wig.after_install)

				update_wigwamfile_installed({wig_name : wig.trace()})
			w('ALLOK=1')
		
		print 'ok [{}]'.format(installation_script_path)

	def gen_activate_files(bin_dirs, lib_dirs, include_dirs, python_dirs):
		with open(P.activate_sh, 'w') as out:
			print >> out, S.export_prepend_paths(S.PATH, bin_dirs)
			print >> out, S.export_prepend_paths(S.LD_LIBRARY_PATH, lib_dirs)
			print >> out, S.export_prepend_paths(S.LIBRARY_PATH, lib_dirs)
			print >> out, S.export_prepend_paths(S.CPATH, include_dirs)
			print >> out, S.export_prepend_paths(S.PYTHONPATH, python_dirs)
			print >> out, S.export(S.WIGWAM_PREFIX, os.path.abspath(P.prefix))

	def lint(old = None):
		begin = DictConfig.read(P.wigwamfile)
		end = begin.copy()
		if old is None:
			old = begin

		while True:
			to_install = DictConfig({wig_name : WigConfig.find_and_construct_wig(wig_name).dict_config() for wig_name in WigConfig(end).get_immediate_unsatisfied_dependencies()})
			if len(to_install) == 0:
				break
			end = end.patch(to_install)

		to_install = WigConfig(end).diff(WigConfig(begin))

		if len(to_install) > 0:
			end = begin.patch(to_install)
			end.save(P.wigwamfile)

		return end

	init()

	assert lint(old = old) is not None

	requested = WigConfig(DictConfig.read(P.wigwamfile))
	installed = WigConfig(DictConfig.read(P.wigwamfile_installed))
	requested_installed_diff = set(requested.diff(installed).keys())
	seeds = set(seeds)
	wig_name_subset = seeds if install_only_seeds else (requested_installed_diff | (seeds if force_seeds_reinstall else set([])))

	to_install = requested.compute_installation_order(seeds, down = True, wig_name_subset = wig_name_subset) if seeds and seeds <= requested_installed_diff else requested_installed_diff

	installation_order = requested.compute_installation_order(to_install, up = True, wig_name_subset = wig_name_subset)
	gen_activate_files(requested.bin_dirs, requested.lib_dirs, requested.include_dirs, requested.python_dirs)
	gen_installation_script(P.build_script, requested.wigs, requested.env, installation_order)

	if dry:
		print 'Dry run. Quitting.'
		return

	if len(installation_order) == 0:
		print '0 packages to be reconfigured. Quitting.'
	else:
		print 'Running installation script now:'
		if 0 == subprocess.call(['bash', P.build_script] if not verbose else ['bash', '-xv', P.build_script]):
			print ''
			print 'ALL OK. KTHXBAI!'

def remove(wig_names):
	init()
	
	requested = DictConfig.read(P.wigwamfile)
	installed = DictConfig.read(P.wigwamfile_installed)
	
	for wig_name in wig_names:
		if wig_name in installed:
			print 'Package [{}] is already installed, artefacts will not be removed.'.format(wig_name)
		requested.pop(wig_name, None)
		installed.pop(wig_name, None)
		src_dir = os.path.join(P.src_tree, wig_name)
		if os.path.exists(src_dir):
			shutil.rmtree(src_dir)
			
	requested.save(P.wigwamfile)
	installed.save(P.wigwamfile_installed)
	
def which(wigwamfile):
	print os.path.abspath(P.wigwamfile) if wigwamfile else os.path.dirname(P.root)

def status(verbose):
	init()
	
	traces = lambda wigwamfile_path: {wig_name : wig.trace() for wig_name, wig in WigConfig(DictConfig.read(wigwamfile_path)).wigs.items()}
	requested, installed = map(traces, [P.wigwamfile, P.wigwamfile_installed])

	format_version = lambda traces_dic, wig_name: traces_dic[wig_name][DictConfig.FORMATTED_VERSION] if wig_name in traces_dic else ''	
	fmt = '%9s\t%-20s\t%-10s\t' + {True: '%s', False: '%.0s'}[verbose]

	print fmt % ('INSTALLED', 'WIG_NAME', 'VERSION', 'URI')
	for wig_name in sorted(set(requested.keys()) | set(installed.keys())):
		requested_version, installed_version = [format_version(t, wig_name) for t in [requested, installed]]
		is_installed, is_conflicted = wig_name in installed
		is_conflicted = requested_version != installed_version
		version = requested_version if not is_installed else (installed_version if not is_conflicted else '*CONFLICT*')
		uri = '' if is_conflicted else (installed[wig_name][DictConfig.URI] if DictConfig.URI in installed[wig_name] else 'N/A')
		print fmt % ('*' if is_installed else '', wig_name, version, uri)

def clean(wigwamfile):
	print 'Removing wigwam artefacts... ',
	for f in P.generated_files + ([P.wigwamfile] if wigwamfile else []):
		if os.path.exists(f):
			os.remove(f)
	for d in P.artefact_dirs:
		if os.path.exists(d):
			shutil.rmtree(d)
	print 'ok'

def init(wigwamfile = None):
	for d in P.all_dirs:
		if not os.path.exists(d):
			os.makedirs(d)
	
	for wigwamfile_to_init, filler in [(P.wigwamfile, ((urllib2.urlopen if urlparse.urlparse(wigwamfile).netloc else open)(wigwamfile).read()) if wigwamfile else '{}'), (P.wigwamfile_installed, '{}')]:
		if not os.path.exists(wigwamfile_to_init):
			with open(wigwamfile_to_init, 'w') as f:
				json.dump(json.loads(filler), f)

def log(wig_name, fetch, configure, build, install):
	stages = filter(locals().get, Wig.all_installation_stages) or Wig.all_installation_stages
	subprocess.call('cat "{}" | less'.format('" '.join([os.path.join(P.log_base(wig_name), stage + '.txt') for stage in stages]), shell = True))

def search(wig_name, print_json):
	filter_wig_names = lambda file_names: [file_name for file_name, ext in map(os.path.splitext, file_names) if ext == '.py']
	to_json = lambda wig: {'name' : wig.name, 'dependencies' : wig.dependencies, 'optional_dependencies' : wig.optional_dependencies, 'supported_features' : wig.supported_features, 'config_access' : wig.config_access, 'formatted_version' : wig.trace()[DictConfig.FORMATTED_VERSION], 'uri' : wig.trace().get(DictConfig.URI, 'N/A')}

	if wig_name:
		wig_names = [wig_name]
	else:
		wig_names = []
		for repo in P.repos:
			if 'github' in repo:
				github_api_clues = re.search('.*github.com/(?P<repo_owner>.+)/(?P<repo_name>.+)/tree/(?P<ref>.+)/(?P<path>.+)', repo).groupdict()
				github_api_uri = 'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={ref}'.format(**github_api_clues)
				wig_names += filter_wig_names([github_file_info['name'] for github_file_info in json.load(urllib2.urlopen(github_api_uri))])
			else:
				wig_names += filter_wig_names(os.listdir(repo)) if os.path.exists(repo) else []

	def w(wig_name):
		wig = WigConfig.find_and_construct_wig(wig_name)
		return wig

	wigs = map(w, sorted(set(wig_names)))

	if not print_json:
		fmt = '%-20s\t%-10s\t%s'
		print fmt % ('WIG_NAME', 'VERSION', 'DEPENDENCIES')
		for wig in wigs:
			print fmt % (wig.name, wig.trace()[DictConfig.FORMATTED_VERSION], ', '.join(wig.dependencies))
	else:
		print json.dumps(map(to_json, wigs), indent = 2, sort_keys = True)

def run(dry, verbose, cmds = []):
	if os.path.exists(P.activate_sh):
		cmd = ('''bash --rcfile <(cat "$HOME/.bashrc"; cat "%s") -ci%s %s''' % (P.activate_sh, 'x' if verbose else '', pipes.quote(' '.join(map(pipes.quote, cmds))))) if cmds else ('''bash %s --rcfile <(cat "$HOME/.bashrc"; cat "%s"; echo 'export PS1="$PS1/\ $ "') -i''' % ('-xv' if verbose else '', P.activate_sh))
		if dry:
			print cmd
			print '# {}:'.format(P.activate_sh)
			for line in open(P.activate_sh, 'r'):
				print '# ' + line[:-1]
		else:
			subprocess.call(['bash', '-cx' if verbose else '-c', cmd])
	else:
		print 'The activate shell script doesn''t exist yet. Run "wigwam build" first.'

if __name__ == '__main__':
	def unhandled_exception_hook(exc_type, exc_value, exc_traceback):
		if issubclass(exc_type, KeyboardInterrupt):
			print '<CTRL-C> pressed. Aborting.'
			return

		print 'Unhandled exception occured! Please consider filing a bug report at {} along with the stack trace below:'.format(P.bugreport_page)
		print ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
		sys.exit(1)
	sys.excepthook = unhandled_exception_hook

	parser = argparse.ArgumentParser(prog = 'wigwam')
	parser.add_argument('--root')
	parser.add_argument('--repo', action = 'append', default = [])
	parser.add_argument('--global', action = 'store_true')
	subparsers = parser.add_subparsers()
	
	cmd = subparsers.add_parser('init')
	cmd.add_argument('--wigwamfile')
	cmd.set_defaults(func = init)
	
	cmd = subparsers.add_parser('install')
	cmd.set_defaults(func = install)
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('wig_names', nargs = '+')
	cmd.add_argument('--enable', nargs = '+', default = [])
	cmd.add_argument('--disable', nargs = '+', default = [])
	group = cmd.add_mutually_exclusive_group()
	group.add_argument('--git', nargs = '?', const = True)
	group.add_argument('--version')
	cmd.add_argument('--config', '-D', action = 'append', default = [])
	cmd.add_argument('--reinstall', action = 'store_true')
	cmd.add_argument('--only', action = 'store_true')
	cmd.add_argument('--dangerous', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')
	
	cmd = subparsers.add_parser('build')
	cmd.set_defaults(func = build)
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')

	cmd = subparsers.add_parser('upgrade')
	cmd.set_defaults(func = upgrade)
	cmd.add_argument('wig_names', nargs = '*')
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--only', action = 'store_true')
	cmd.add_argument('--dangerous', action = 'store_true')
	
	cmd = subparsers.add_parser('run')
	cmd.set_defaults(func = run)
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')
	cmd.add_argument('cmds', nargs = argparse.REMAINDER)
	
	cmd = subparsers.add_parser('in')
	cmd.set_defaults(func = run)
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')
		
	cmd = subparsers.add_parser('which')
	cmd.add_argument('--wigwamfile', action = 'store_true')
	cmd.set_defaults(func = which)
	
	cmd = subparsers.add_parser('status')
	cmd.set_defaults(func = status)
	cmd.add_argument('--verbose', action = 'store_true')
	
	cmd = subparsers.add_parser('log')
	cmd.set_defaults(func = log)
	cmd.add_argument('wig_name')
	cmd.add_argument('--fetch', action = 'store_true')
	cmd.add_argument('--configure', action = 'store_true')
	cmd.add_argument('--make', action = 'store_true')
	cmd.add_argument('--install', action = 'store_true')

	cmd = subparsers.add_parser('search')
	cmd.set_defaults(func = search)
	cmd.add_argument('wig_name', default = None, nargs = '?')
	cmd.add_argument('--json', action = 'store_true', dest = 'print_json')

	cmd = subparsers.add_parser('remove')
	cmd.set_defaults(func = remove)
	cmd.add_argument('wig_names', nargs = '+')
	
	cmd = subparsers.add_parser('clean')
	cmd.add_argument('--wigwamfile', action = 'store_true')
	cmd.set_defaults(func = clean)

	args = vars(parser.parse_args())
	cmd, use_global, extra_repos, arg_root = args.pop('func'), args.pop('global'), args.pop('repo'), args.pop('root')

	local_root_dir = os.path.abspath(arg_root or '.')
	global_root_dir = os.path.expanduser('~')
	use_local = lambda local_file_name, local_cond: ((os.path.exists(os.path.join(local_root_dir, local_file_name)) or cmd == init or local_cond)) and not use_global
	
	root_dir = local_root_dir if use_local(P.wigwamdirname, arg_root != None) else global_root_dir
	wigwamfile_dir = local_root_dir if use_local(P.wigwamfilename, False) else global_root_dir
	P.init(root = os.path.join(root_dir, P.wigwamdirname), wigwamfile = os.path.join(root_dir, P.wigwamfilename), extra_repos = extra_repos)
	
	cmd(**args)
