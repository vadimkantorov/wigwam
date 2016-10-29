import os
import re
import sys
import time
import json
import pipes
import shutil
import inspect
import urllib2
import argparse
import itertools
import traceback
import subprocess
import collections
import multiprocessing

class P:
	bugreport_page = 'http://github.com/vadimkantorov/wigwam/issues'
	wigwamdirname = '.wigwam'
	wigwamfilename = 'Wigwamfile'
	userwigdir = 'wigs'
	python_prefix_schemes = [
		('python/PREFIXSCHEME', 'lib/python%d.%d/site-packages' % (sys.version_info.major, sys.version_info.minor), 'bin', 'include/python%d.%d' % (sys.version_info.major, sys.version_info.minor)),
		('python/HOMESCHEME', 'lib/python', 'bin', 'include/python'),
		('python/USERSCHEME', 'lib/python%d.%d/site-packages' % (sys.version_info.major, sys.version_info.minor), 'bin', 'include/python%d.%d' % (sys.version_info.major, sys.version_info.minor))
	] # https://docs.python.org/2/install/

	@staticmethod
	def init(root, wigwamfile, extra_repos):
		P.root = root
		P.wigwamfile = wigwamfile
		p = lambda x: os.path.join(P.root, x)

		P.src_tree = p('src')
		P.prefix = p('prefix')
		P.prefix_deb = os.path.join(P.prefix, 'deb')
		P.log_root = p('log')
		P.tar_root = p('tar')
		P.deb_root = p('deb')
		P.debug_root = p('debug')

		P.activate_sh = p('wigwam_activate.sh')
		P.activate_m = p('wigwam_activate.m')
		P.build_script = p('build.generated.sh')
		P.install_script = p('install.generated.sh')
		P.upgrade_script = p('upgrade.generated.sh')
		P.wigwamfile_installed = p(P.wigwamfilename + '.installed')
		P.wigwamfile_old = p(P.wigwamfilename + '.old')

		P.artifact_dirs = [P.src_tree, P.prefix, P.log_root, P.tar_root, P.deb_root, P.prefix_deb, P.debug_root]

		P.generated_installation_scripts = [P.build_script, P.install_script]
		P.generated_files = P.generated_installation_scripts + [P.wigwamfile_installed, P.wigwamfile_old, P.activate_sh, P.activate_m]

		P.all_dirs = [P.root] + P.artifact_dirs

		P.prefix_bin_dirs = [os.path.join(P.prefix, 'bin'), os.path.join(P.prefix_deb, 'usr/bin')]
		P.prefix_lib_dirs = [os.path.join(P.prefix, 'lib64'), os.path.join(P.prefix, 'lib'), os.path.join(P.prefix_deb, 'usr/lib'), os.path.join(P.prefix_deb, 'usr/lib/x86_64-linux-gnu')]
		P.prefix_include_dirs = [os.path.join(P.prefix, 'include'), os.path.join(P.prefix_deb, 'usr/include')]
		P.prefix_python_dirs = []
		
		for root_relative_path, module_path, bin_path, include_path in P.python_prefix_schemes:
			root_full_path = os.path.join(P.prefix, root_relative_path)
			module_full_path = os.path.join(root_full_path, module_path)
			bin_path = os.path.join(root_full_path, bin_path)
			include_full_path = os.path.join(root_full_path, include_path)
			
			P.prefix_python_dirs += [module_full_path]
			P.artifact_dirs += [root_full_path]
			P.all_dirs += [module_full_path, bin_path, include_full_path]

		P.repos = [P.userwigdir] + extra_repos

		P.log_base = staticmethod(lambda wig_name: os.path.join(P.log_root, wig_name))
		P.debug_script = staticmethod(lambda wig_name: os.path.join(P.debug_root, wig_name + '.sh'))
		P.download = staticmethod(('wget {0} -O "{1}"' if subprocess.call(['which', 'wget'], stdout = subprocess.PIPE, stderr = subprocess.PIPE) == 0 else 'curl {0} -o "{1}"').format)

class W:
	CONFIG = '_config'
	FEATURES = 'features'
	SOURCES = 'sources'
	FORMATTED_VERSION = 'formatted_version'
	GIT_BRANCH = 'git_branch'
	GIT_COMMIT = 'git_commit'
	GIT_INIT_SUBMODULES = 'git_init_submodules'
	VERSION = 'version'
	URI = 'uri'
	TAR_STRIP_COMPONENTS = 'tar_strip_components'
	DEPENDS_ON = 'depends_on'

class S:
	LDFLAGS = 'LDFLAGS'
	CFLAGS = 'CFLAGS'
	CXXFLAGS = 'CXXFLAGS'
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
	PREFIX_PYTHON_PREFIXSCHEME = '$PREFIX/python/PREFIXSCHEME'
	PREFIX_PYTHON_HOMESCHEME = '$PREFIX/python/HOMESCHEME'
	PREFIX_PYTHON_USERSCHEME = '$PREFIX/python/USERSCHEME'
	PYTHON_DEFAULT_MODULE_PATH = os.path.join('$PREFIX', P.python_prefix_schemes[0][0], P.python_prefix_schemes[0][1])
	PYTHON_DEFAULT_BIN_PATH = os.path.join('$PREFIX', P.python_prefix_schemes[0][0], P.python_prefix_schemes[0][2])
	PYTHON_DEFAULT_INCLUDE_PATH = os.path.join('$PREFIX', P.python_prefix_schemes[0][0], P.python_prefix_schemes[0][3])
	PREFIX_CONFIGURE_FLAG = '--prefix="$PREFIX"'
	prefix_MAKE_INSTALL_FLAG = 'prefix="$PREFIX"'
	PREFIX_MAKE_INSTALL_FLAG = 'PREFIX="$PREFIX"'
	DESTDIR_MAKE_INSTALL_FLAG = 'DESTDIR="$PREFIX"'
	FPIC_FLAG = '-fPIC'
	CMAKE_INSTALL_PREFIX_FLAG = '-DCMAKE_INSTALL_PREFIX="$PREFIX"'
	CMAKE_PREFIX_PATH_FLAG = '-DCMAKE_PREFIX_PATH="$PREFIX"'
	MKDIR_CD_BUILD = 'mkdir -p build && cd build'
	CD_BUILD = 'cd build'
	CD_PARENT = 'cd ..'
	MAKEFLAGS = 'MAKEFLAGS'
	
	mkdir_p = staticmethod('mkdir -p "{}"'.format)
	make_jobs = staticmethod('-j{}'.format)
	export = staticmethod('export {0}="{1}"'.format)
	configure = staticmethod(lambda flags: './configure %s' % ' '.join(flags))
	onoff = staticmethod({True : 'on', False : 'off'}.get)
	ONOFF = staticmethod({True : 'ON', False : 'OFF'}.get)
	make = staticmethod(lambda flags: 'make %s' % ' '.join(flags))
	makeflags = staticmethod(lambda flags: '%s="%s %s"' % (S.MAKEFLAGS, ' '.join(flags), os.environ.get(S.MAKEFLAGS, '')) if flags else '')
	make_install = staticmethod(lambda flags: 'make install %s' % ' '.join(flags))
	python_setup_install = 'python setup.py install --prefix="%s"' % PREFIX_PYTHON_PREFIXSCHEME
	ln = staticmethod('ln -f -s "{}" "{}"'.format)
	qq = staticmethod('"{0}"'.format)
	rm_rf = staticmethod(lambda *args: 'rm -rf %s' % ' '.join(map(S.qq, args)))

	matlab = staticmethod(lambda matlab_path, script_path: '''"%s" -nodesktop -nosplash -r "addpath('%s'); try, %s; catch exception, disp(exception); disp(exception.message); exit(1); end; exit(0)"''' % (matlab_path, os.path.dirname(script_path), os.path.splitext(os.path.basename(script_path))[0]))

	dump_env = '''function dump_env {
	echo "BEGIN_ENV"
	echo "PATH=$PATH"
	echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
	echo "CPATH=$CPATH"
	echo "LIBRARY_PATH=$LIBRARY_PATH"
	echo ""
	echo "g++ -print-search-dirs:"
	echo "$(g++ -print-search-dirs)"
	echo ""
	echo "PWD=$PWD"
	echo "END_ENV"
	echo ""
}'''

	@staticmethod
	def fetch_tarball(uri, target_dir, strip_components = 0):
		original_file_name = uri.split('/')[-1]
		ext = [e for e in ['.tar', '.tar.gz', '.tar.bz2', '.tgz'] if original_file_name.endswith(e)]
		assert len(ext) == 1
		downloaded_file_path = os.path.join(P.tar_root, os.path.basename(target_dir) + ext[0])

		return [P.download(uri, downloaded_file_path),
				S.mkdir_p(target_dir),
'tar -xf %s -C "%s"%s' % (downloaded_file_path, target_dir, ' --strip-components=%d' % strip_components),
		]
	
	@staticmethod
	def fetch_git(uri, target_dir, init_submodules = None, tag = None):
		opts = [uri, '"%s"' % target_dir] + (['--recursive'] if init_submodules else [])
		snippet = ['git clone %s' % ' '.join(opts)]
		if tag != None:
			snippet += ['cd "%s"' % target_dir, 'git checkout %s' % tag]
		return snippet

class SourceFetcher:
	def __init__(self):
		self.clues = {}

	def make_gen_snippet_git(self, wig, sources):
		self.clues.update({W.URI : wig.git_uri, W.GIT_INIT_SUBMODULES : wig.git_init_submodules if wig.git_init_submodules != None else False})
		if wig.git_branch:
			self.clues[W.GIT_BRANCH] = wig.git_branch
		if wig.git_commit:
			self.clues[W.GIT_COMMIT] = wig.git_commit

		splitted = sources.split('@')
		if len(splitted[0]) > 0:
			self.clues[W.GIT_COMMIT] = splitted[0].strip()
		if len(splitted) > 1:
			self.clues[W.GIT_BRANCH] = splitted[1].strip()

		return lambda target_dir: [S.rm_rf(target_dir)] + S.fetch_git(self.clues[W.URI], target_dir, init_submodules = self.clues[W.GIT_INIT_SUBMODULES], tag = self.clues.get(W.GIT_COMMIT) or self.clues.get(W.GIT_BRANCH))

	def make_gen_snippet_tarball(self, wig, sources):
		version = sources.strip() or wig.last_release_version or wig.find_last_release_version()
		self.clues.update({W.URI : wig.compute_release_url(version), W.VERSION : version, W.TAR_STRIP_COMPONENTS : wig.tar_strip_components if wig.tar_strip_components != None else 1})
		return lambda target_dir: [S.rm_rf(target_dir)] + S.fetch_tarball(self.clues[W.URI], target_dir, strip_components = self.clues[W.TAR_STRIP_COMPONENTS])

	def configure(self, wig, sources):
		if sources.startswith('git'):
			self.gen_snippet = self.make_gen_snippet_git(wig, sources[len('git'):])
		elif sources.startswith('tarball'):
			self.gen_snippet = self.make_gen_snippet_tarball(wig, sources[len('tarball'):])
		else:
			self.gen_snippet = lambda target_dir: None

class Wig:
	git_branch = None
	git_commit = None
	git_init_submodules = None
	tar_strip_components = None
	working_directory = '.'
	matlab_root = None
	sources = None

	config_access = []
	dependencies = []
	optional_dependencies = []
	supported_features = []
	default_features = []
	last_release_version = None

	all_installation_stages = ['fetch', 'configure', 'make', 'install']
	
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
		self.features_on_off = []
		self.depends_on = []
		self.skip_stages = []
		self.sources = self.sources or ('tarball' if hasattr(self, 'tarball_uri') else 'git' if hasattr(self, 'git_uri') else None)
		self.source_fetcher = SourceFetcher()

		class WigPaths:
			def __init__(self, wig):
				self.src_dir = os.path.join(P.src_tree, wig.name)
		self.paths = WigPaths(self)

	def default_dict_config(self):
		if self.sources == 'tarball':
			return {W.SOURCES : 'tarball ' + (self.last_release_version or self.find_last_release_version()) }
		elif self.sources == 'git':
			return {W.SOURCES : ('git %s' % (self.git_commit or self.find_last_git_commit())) + ('@%s' % self.git_branch if self.git_branch else '')}
		else:
			return {}
	
	def setup(self):
		pass
	
	def switch(self, feat_name, on):
		pass

	def find_last_release_version(self):
		return None

	def find_last_git_commit(self):
		branch = self.git_branch or 'HEAD'
		lines = filter(bool, subprocess.check_output(['git', 'ls-remote', self.git_uri]).split('\n'))
		refs = [commit for commit, head in map(str.split, lines) if branch in head]
		assert len(refs) == 1
		return refs[0][:7]

	def compute_release_url(self, source_version):
		return self.tarball_uri.replace('$RELEASE_VERSION$', source_version.lstrip('v'))

	def gen_configure_snippet(self):
		return S.configure(self.configure_flags)

	def gen_fetch_snippet(self):
		return self.source_fetcher.gen_snippet(self.paths.src_dir)

	def gen_make_snippet(self):
		return S.make(self.make_flags)

	def gen_install_snippet(self):
		return S.make_install(self.make_install_flags) if 'make install' not in self.skip_stages else []

	def provision_features(self, extra_features_on_off):
		effective_on_off = collections.defaultdict(list)
		features_on_off = self.features_on_off + extra_features_on_off
		for feat in features_on_off:
			feat_name = feat.lstrip('+-')
			effective_on_off[feat_name].append(feat[0])
		self.features_on_off = [effective_on_off[feat_name][-1] + feat_name for feat_name in sorted(effective_on_off.keys())]

	def switch_features_on_off(self):
		for feat in self.features_on_off:
			on = feat[0] == '+'
			feat_name = feat.lstrip('+-')
			assert feat_name in self.supported_features, ('%s not in %s' % (feat_name, self.supported_features))
			f1 = 'switch_%s_%s' % (feat_name, S.onoff(on))
			f2 = 'switch_%s' % feat_name
			if hasattr(self, f1):
				getattr(self, f1)()
			elif hasattr(self, f2):
				getattr(self, f2)(on)
			else:
				self.switch(feat_name, on)

	def configure_with_dict_config(self, dict_config, dict_env):
		self.env = dict_env
		self.provision_features(dict_config.get(W.FEATURES, '').split())
		self.sources = dict_config.get(W.SOURCES) or self.sources
		assert self.sources != None
		self.source_fetcher.configure(self, self.sources)

	def trace(self):
		t = {W.DEPENDS_ON : self.depends_on,
			W.FEATURES : ' '.join(self.features_on_off),
			W.SOURCES : self.sources,
			W.FORMATTED_VERSION : (self.sources.split() + ['N/A'])[1]
		}
		t.update(self.source_fetcher.clues)
		return t

	def cfg(self, name):
		assert name in self.config_access
		return self.env[name]

	def getcfg(self, name):
		assert name in self.config_access
		return self.env.get(name)

	def skip(self, *args):
		for stage in args:
			if stage == 'prefix':
				self.configure_flags = filter(lambda x: x is not S.PREFIX_CONFIGURE_FLAG, self.configure_flags)
			elif stage == 'make parallel':
				self.make_flags = filter(lambda x: not x.startswith(S.make_jobs('')), self.make_flags)
				self.make_install_flags = filter(lambda x: not x.startswith(S.make_jobs('')), self.make_install_flags)
			else:
				self.skip_stages += [stage]

	def require(self, wig_name = None, features = []):
		if wig_name:
			deps = self.optional_dependencies + [x[0] if isinstance(x, tuple) else x for x in self.dependencies]
			assert wig_name in deps, 'Dependency [%s] is not found in wig.dependencies [%s] or in wig.optional_dependencies [%s]' % (wig_name, self.dependencies, self.optional_dependencies)
			if wig_name not in self.depends_on:
				self.depends_on.append(wig_name)

		if features:
			self.provision_features(features)

class CmakeWig(Wig):
	def __init__(self, name):
		Wig.__init__(self, name)

		self.cmake_flags = [S.CMAKE_INSTALL_PREFIX_FLAG, S.CMAKE_PREFIX_PATH_FLAG]
		self.before_make.insert(0, S.CD_BUILD)
		self.before_install.insert(0, S.CD_BUILD)

	def skip(self, stage):
		Wig.skip(self, stage)
		if stage == 'prefix':
			self.cmake_flags = filter(lambda x: x is not S.CMAKE_INSTALL_PREFIX_FLAG and x is not S.CMAKE_PREFIX_PATH_FLAG, self.cmake_flags)
		
	def gen_configure_snippet(self):
		return [S.MKDIR_CD_BUILD, 'cmake %s ..' % (' '.join(self.cmake_flags))]

	def switch_debug(self, on):
		self.cmake_flags += ['-D CMAKE_BUILD_TYPE=%s' % ('DEBUG' if on else 'RELEASE')]

class AutogenWig(Wig):
	def __init__(self, name):
		Wig.__init__(self, name)

		self.before_configure += ['bash autogen.sh']

class LuarocksWig(Wig):
	LUAROCKS_PATH = '$PREFIX/bin/luarocks'
	sources = 'luarocks'
	rockspec_path = None
	
	def __init__(self, name, rockspec_path = None):
		Wig.__init__(self, name)
		if rockspec_path != None:
			self.rockspec_path = rockspec_path
		self.skip('fetch', 'configure', 'make')
	
	def gen_install_snippet(self):
		return [S.export(S.CMAKE_PREFIX_PATH, '$PREFIX'), '%s %s make %s' % (S.makeflags(self.make_flags), LuarocksWig.LUAROCKS_PATH, self.rockspec_path)] if self.rockspec_path else [S.export(S.CMAKE_PREFIX_PATH, '$PREFIX'), '%s %s install %s' % (S.makeflags(self.make_flags), LuarocksWig.LUAROCKS_PATH, self.name)]

class DebWig(Wig):
	APT_GET_OUTPUT_CACHE = {}

	def __init__(self, name):
		Wig.__init__(self, name)

		self.sources = None
		self.skip('make')
		
		if self.name not in DebWig.APT_GET_OUTPUT_CACHE:
			DebWig.APT_GET_OUTPUT_CACHE[self.name] = subprocess.check_output(['apt-get', '--print-uris', '--yes', '--reinstall', 'install', self.name[len('deb-'):]])

		self.deb_uris = re.findall("'(http.+)'", DebWig.APT_GET_OUTPUT_CACHE[self.name]) or []
		self.cached_deb_paths = [os.path.join(P.deb_root, os.path.basename(uri)) for uri in self.deb_uris]
	
		if len(self.deb_uris) == 0:
			self.skip(*Wig.all_installation_stages)

	def find_last_release_version(self):
		return 'v1.0'

	def configure_with_dict_config(self, *args):
		self.source_fetcher.clues = {W.URI : ', '.join(self.deb_uris), W.VERSION: self.find_last_release_version()}
	
	def gen_fetch_snippet(self):
		return [P.download(uri, downloaded_file_path) for uri, downloaded_file_path in zip(self.deb_uris, self.cached_deb_paths)]
	
	def gen_install_snippet(self):
		return ['dpkg -x "%s" "%s"' % (downloaded_file_path, P.prefix_deb) for downloaded_file_path in self.cached_deb_paths]

class PythonWig(Wig):
	def __init__(self, name):
		Wig.__init__(self, name)
		self.skip('make')

	def gen_configure_snippet(self):
		return []

	def gen_install_snippet(self):
		return [S.python_setup_install]

class PipWig(Wig):
	PIP_PATH = 'pip' # '$PREFIX/bin/pip'
	sources = 'pip'

	def setup(self):
		self.skip('fetch', 'configure', 'make')
		#self.require('pip')

	def gen_install_snippet(self):
		return [S.export('PYTHONUSERBASE', S.PREFIX_PYTHON_USERSCHEME), '"%s" install --force-reinstall --ignore-installed --user %s' % (PipWig.PIP_PATH, self.name[len('pip-'):])]

class DictConfig(dict):
	@staticmethod
	def read(path):
		with open(path, 'r') as f:
			return DictConfig(json.load(f) if os.path.exists(path) else {})

	def save(self, path):
		with open(path, 'w') as f:
			json.dump(dict(self), f, indent = 2, sort_keys = True)

	def patch(self, diff):
		dict_config = self.clone()
		if W.CONFIG in diff:
			dict_config[W.CONFIG] = dict_config.get(W.CONFIG, {})
			dict_config[W.CONFIG].update(diff.pop(W.CONFIG))
		for wig_name, y in diff.items():
			if wig_name not in dict_config:
				dict_config[wig_name] = y
			else:
				if W.SOURCES in y:
					dict_config[wig_name][W.SOURCES] = y[W.SOURCES]
				if W.FEATURES in y:
					dict_config[wig_name][W.FEATURES] = dict_config[wig_name].get(W.FEATURES, '') + ' ' + y.get(W.FEATURES, '')
		
		return dict_config
	
	def clone(self):
		return DictConfig(self.copy())

class WigConfig:
	def __init__(self, dict_config):
		dict_config = dict_config.clone()
		self.env = dict_config.pop(W.CONFIG, {})

		self.wigs = {}
		for wig_name, y in dict_config.items():
			wig = WigConfig.find_and_construct_wig(wig_name)
			wig.configure_with_dict_config(y, self.env)
			features_in_dict_config = wig.features_on_off
			for dep_wig_name in wig.dependencies:
				wig.require(dep_wig_name)
			wig.setup()
			wig.require(features = wig.default_features)
			wig.require(features = features_in_dict_config)
			self.wigs[wig_name] = wig

		for wig_name in self.wigs.keys():
			self.wigs[wig_name].switch_features_on_off()

		flatten = lambda xs: list(itertools.chain(*xs))
		self.bin_dirs = P.prefix_bin_dirs + flatten(map(lambda wig: wig.bin_dirs, self.wigs.values()))
		self.lib_dirs = P.prefix_lib_dirs + flatten(map(lambda wig: wig.lib_dirs, self.wigs.values()))
		self.include_dirs = P.prefix_include_dirs + flatten(map(lambda wig: wig.include_dirs, self.wigs.values()))
		self.python_dirs = P.prefix_python_dirs + flatten(map(lambda wig: wig.python_dirs, self.wigs.values()))
		self.matlab_dirs = {wig_name : os.path.join(wig.paths.src_dir, wig.matlab_root) for wig_name, wig in self.wigs.items() if wig.matlab_root != None}

	@staticmethod
	def find_and_construct_wig(wig_name):
		shortcut = [s for k, s in {'deb-' : DebWig, 'lua-' : LuarocksWig, 'pip-' : PipWig}.items() if wig_name.startswith(k)]
		if shortcut:
			return shortcut[0](wig_name)

		find_class = lambda: {cls.__name__ : cls for cls in globals().values() if inspect.isclass(cls) and issubclass(cls, Wig) and cls != Wig}.get(wig_name.replace('-', '_'))
		
		cls = None	
		for repo in P.repos:
			opener = open
			if 'github' in repo:
				repo = repo.replace('github.com', 'raw.githubusercontent.com').replace('/tree/', '/')
				opener = urllib2.urlopen
		
			content = ''
			try:
				path = os.path.join(repo, '%s.py' % wig_name)
				content = opener(path).read()
			except:
				pass

			if content and content != 'Not Found':
				exec content in globals(), globals()
				cls = find_class()
				break

		if cls == None:
			print 'Wig [%s] cannot be found. Quitting.' % wig_name
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
			graph = {wig_name: [k for k in wig_name_subset if wig_name in self.wigs[k].depends_on] for wig_name in wig_name_subset}
		else:
			graph = {wig_name: filter(lambda x: x in wig_name_subset, self.wigs[wig_name].depends_on) for wig_name in wig_name_subset}
		
		to_install = WigConfig.dfs(graph, reconfigured)
		graph = {wig_name : filter(lambda x: x in to_install, self.wigs[wig_name].depends_on) for wig_name in to_install}
		return WigConfig.topological_sort(graph)
	
	def get_immediate_unsatisfied_dependencies(self):
		return {x : [] for x in set((dep_wig_name for wig in self.wigs.values() for dep_wig_name in wig.depends_on if dep_wig_name not in self.wigs.keys()))}

	def diff(self, graph):
		s = lambda e: set(e) if isinstance(e, list) else set([e])
		fingerprint = lambda w: set(filter(bool, set.union(*map(s, map(w.trace().get, [W.URI, W.VERSION, W.GIT_COMMIT, W.FEATURES, W.DEPENDS_ON]))))) if w != None else set(['N/A'])

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
					to_install[wig_name][W.FEATURES] = ' '.join(features_on_off)
				if wig.sources != other_sources:
					to_install[wig_name][W.SOURCES] = wig.sources
			
		return DictConfig(to_install)

def lint(old = None):
	init()

	begin = DictConfig.read(P.wigwamfile)
	end = begin.clone()
	if old != None:
		old.save(P.wigwamfile_old)
	else:
		old = begin

	while True:
		to_install = DictConfig({wig_name : WigConfig.find_and_construct_wig(wig_name).default_dict_config() for wig_name in WigConfig(end).get_immediate_unsatisfied_dependencies()})
		if len(to_install) == 0:
			break
		end = end.patch(to_install)

	to_install = WigConfig(end).diff(WigConfig(begin))

	if len(to_install) > 0:
		end = begin.patch(to_install)
		end.save(P.wigwamfile)
		print 'Lint reconfigured %d packages (backup in "%s").' % (len(to_install), P.wigwamfile_old)

	return end

def install(wig_strings, dry, config, reinstall, only, dangerous, verbose):
	init()

	assert (not only) or (only and dangerous)
	
	old = DictConfig.read(P.wigwamfile)
	end = old.patch({W.CONFIG : dict(map(lambda x: x.split('='), config))})
	
	wig_names = []
	for wig_string in wig_strings:
		args = re.search(r"(?P<wig_name>.+?)(?:\[(?P<sources>.+)\])?(?:\((?P<features>[+-].+)\))?$", wig_string).groupdict()
		wig_name = args['wig_name']
		dict_config = WigConfig.find_and_construct_wig(wig_name).default_dict_config()
		dict_config.update({arg: args[arg] for arg in ['sources', 'features'] if args[arg] != None})
		end = end.patch({ wig_name : dict_config })
		wig_names.append(wig_name)

	end.save(P.wigwamfile)
	build(dry = dry, old = old, script_path = P.install_script, seeds = wig_names, force_seeds_reinstall = reinstall, install_only_seeds = only, verbose = verbose)

def upgrade(wig_names, dry, only, dangerous):
	init()

	assert (not only) or (only and dangerous)

	old = DictConfig.read(P.wigwamfile)
	end = old.clone()

	if not wig_names:
		wig_names = filter(lambda x: x != W.CONFIG, old.keys())

	for wig_name in wig_names:
		if wig_name not in old:
			print 'Package [%s] not installed or requested. Cannot upgrade, call install first.'
			return

		dict_config = WigConfig.find_and_construct_wig(wig_name).default_dict_config()
		if dict_config.get(W.SOURCES, None) != old[wig_name].get(W.SOURCES, None):
			print 'Going to upgrade package [%s]: %s -> %s' % (wig_name, old[wig_name].get(W.SOURCES, None), dict_config.get(W.SOURCES, None))
			end.patch({wig_name : {W.SOURCES : dict_config[W.SOURCES]}})

	end.save(P.wigwamfile)
	build(dry = dry, old = old, script_path = P.upgrade_script, seeds = wig_names, install_only_seeds = only)


def build(dry, old = None, script_path = None, seeds = [], force_seeds_reinstall = False, install_only_seeds = False, verbose = False):
	init()

	if lint(old = old) == None:
		print 'Lint check failed. Quitting.'
		return

	requested = WigConfig(DictConfig.read(P.wigwamfile))
	installed = WigConfig(DictConfig.read(P.wigwamfile_installed))
	requested_installed_diff = set(requested.diff(installed).keys())
	seeds = set(seeds)
	wig_name_subset = seeds if install_only_seeds else (requested_installed_diff | (seeds if force_seeds_reinstall else set([])))

	if seeds and seeds <= requested_installed_diff:
		to_install = requested.compute_installation_order(seeds, down = True, wig_name_subset = wig_name_subset)
	else:
		to_install = requested_installed_diff

	installation_order = requested.compute_installation_order(to_install, up = True, wig_name_subset = wig_name_subset)
	script_path = script_path or P.build_script
	gen_activate_star_files(requested.bin_dirs, requested.lib_dirs, requested.include_dirs, requested.python_dirs, requested.matlab_dirs)
	gen_installation_script(script_path, requested.wigs, requested.env, installation_order)

	if not dry:
		if len(installation_order) == 0:
			print '0 packages to be reconfigured. Quitting.'
		else:
			print 'Running installation script now:'
			return_code = subprocess.call(['bash', script_path] if not verbose else ['bash', '-xv', script_path])
			if return_code == 0:
				print ''
				print 'ALL OK. KTHXBAI!'
	else:
		print 'Dry run. Quitting.'

def remove(wig_names, dangerous):
	init()
	
	requested = DictConfig.read(P.wigwamfile)
	installed = DictConfig.read(P.wigwamfile_installed)
	for wig_name in wig_names:
		requested.pop(wig_name, None)
		installed.pop(wig_name, None)
	requested.save(P.wigwamfile)
	installed.save(P.wigwamfile_installed)
	
def path():
	print os.path.dirname(P.root)

def status(verbose):
	init()
	
	traces = lambda wigwamfile_path: {wig_name : wig.trace() for wig_name, wig in WigConfig(DictConfig.read(wigwamfile_path)).wigs.items()}
	requested, installed = map(traces, [P.wigwamfile, P.wigwamfile_installed])

	format_version = lambda traces_dic, wig_name: traces_dic[wig_name][W.FORMATTED_VERSION] if wig_name in traces_dic else ''	
	fmt = '%9s\t%-20s\t%-10s\t' + {True: '%s', False: '%.0s'}[verbose]

	print fmt % ('INSTALLED', 'WIG_NAME', 'VERSION', 'URI')
	for wig_name in sorted(set(requested.keys()) | set(installed.keys())):
		requested_version = format_version(requested, wig_name)
		installed_version = format_version(installed, wig_name)
		is_installed = wig_name in installed
		is_conflicted = requested_version != installed_version
		version = requested_version if not is_installed else (installed_version if not is_conflicted else '*CONFLICT*')
		uri = '' if is_conflicted else (installed[wig_name][W.URI] if W.URI in installed[wig_name] else 'N/A')
		print fmt % ('*' if is_installed else '', wig_name, version, uri)

def clean():
	for d in P.artifact_dirs:
		if os.path.exists(d):
			try:
				shutil.rmtree(d)
			except:
				print 'shutil.rmtree(%s) failed. Waiting 1 sec and trying one more time.' % repr(d)
				time.sleep(1)
				shutil.rmtree(d)
				
			os.makedirs(d)

	for f in P.generated_files:
		if os.path.exists(f):
			os.remove(f)

def init():
	for d in P.all_dirs:
		if not os.path.exists(d):
			os.makedirs(d)
	
	for wigwamfile in [P.wigwamfile, P.wigwamfile_installed]:
		if not os.path.exists(wigwamfile):
			with open(wigwamfile, 'w') as f:
				json.dump({}, f)

def log(wig_name, fetch = False, configure = False, make = False, install = False):
	arg_stages = locals()
	stages = filter(lambda stage: arg_stages[stage] == True, Wig.all_installation_stages) or Wig.all_installation_stages
	paths = ['"%s.txt"' % os.path.join(P.log_base(wig_name), stage) for stage in stages]
	subprocess.call('cat %s | less' % ' '.join(paths), shell = True)

def search(wig_name, output_json):
	filter_wig_names = lambda file_names: [file_name for file_name, ext in map(os.path.splitext, file_names) if ext == '.py']
	to_json = lambda wig: {'name' : wig.name, 'dependencies' : wig.dependencies, 'optional_dependencies' : wig.optional_dependencies, 'supported_features' : wig.supported_features, 'config_access' : wig.config_access, 'formatted_version' : wig.trace()[W.FORMATTED_VERSION]}

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
		wig.sources = wig.default_dict_config().get(W.SOURCES)
		return wig

	wigs = map(w, sorted(set(wig_names)))

	if not output_json:
		fmt = '%-20s\t%-10s\t%s'
		print fmt % ('WIG_NAME', 'VERSION', 'DEPENDENCIES')
		for wig in wigs:
			print fmt % (wig.name, wig.trace()[W.FORMATTED_VERSION], ', '.join(wig.dependencies))
	else:
		print json.dumps(map(to_json, wigs), indent = 2, sort_keys = True)

def enter(dry, verbose):
	if dry:
		if os.path.exists(P.activate_sh):
			print 'The activate shell script is located at [%s]. Contents:' % P.activate_sh
			print ''
			with open(P.activate_sh, 'r') as f:
				print f.read()
		else:
			print 'The activate shell script doesn''t exist yet.'
	else:
		cmd = '''bash %s --rcfile <(cat "$HOME/.bashrc"; cat "%s"; echo 'export PS1="$PS1/\ $ "') -i''' % ('-xv' if verbose else '', P.activate_sh)
		subprocess.call(['bash', '-cx' if verbose else '-c', cmd])

def run(cmds, verbose):
	cmd = '''bash --rcfile <(cat "$HOME/.bashrc"; cat "%s") -ci%s %s''' % (P.activate_sh, 'x' if verbose else '', pipes.quote(' '.join(cmds)))
	subprocess.call(['bash', '-cx' if verbose else '-c', cmd])

def gen_installation_script(installation_script_path, wigs, env, installation_order):
	for script_path in P.generated_installation_scripts:
		if os.path.exists(script_path):
			os.remove(script_path)

	if not installation_order:
		return

	print '%d packages to be installed in the order below:' % len(installation_order)
	for wig_name in installation_order:
		if wigs[wig_name].depends_on:
			print '%10s    requires  %s' % (wig_name, ', '.join(wigs[wig_name].depends_on))
		else:
			print '%10s' % wig_name
	print ''

	sys.stdout.write('Updating installation script...  ')

	with open(installation_script_path, 'w') as out:
		def w(x, prepend = '', stream = out):
			if x != []:
				print >> stream, '\n'.join([prepend + y for y in x]) if isinstance(x, list) else prepend + x
	
		w('set -e') # set -evx for debugging
		w('trap show_log EXIT')
		w('trap on_ctrl_c SIGINT')
		w('exec 3>&1')
		w('source "%s"' % P.activate_sh)
		w('TIC="$(date +%s)"')
		w('')
		w('''function show_log {
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
''')
		w('''function on_ctrl_c {
	exec 1>&3
	echo "<CTRL+C> pressed. Aborting"
	CTRLCPRESSED=1
	reset
	exit 1
}
''')
		w('''function update_wigwamfile_installed {
	python -c "import sys, json; installed, diff = map(json.load, [open(sys.argv[-1]), sys.stdin]); installed.update(diff); json.dump(installed, open(sys.argv[-1], 'w'), indent = 2, sort_keys = True)" $@
}
''')
		w(S.dump_env)
		w(S.rm_rf(*[P.log_base(wig_name) for wig_name in installation_order]))

		def update_wigwamfile_installed(d):
			w('''cat <<"EOF" | update_wigwamfile_installed "%s"
%s
EOF
''' % (os.path.abspath(P.wigwamfile_installed), json.dumps(d)))
		update_wigwamfile_installed({W.CONFIG : env})
		class Stage:
			def __init__(self, name, file_name, skip, hook = lambda x, prepend: None):
				self.name = name
				self.file_name = file_name
				self.skip = skip
				self.hook = hook
			
			def __enter__(self):
				w('printf "%%14s...  " %s' % self.name)
				if self.skip:
					w('echo skipped')
					return lambda x: None
				else:
					w('LOG="$LOGBASE/%s"' % self.file_name)
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

			w('')
			w('PACKAGE_NAME=%s' % wig_name)
			w('printf "\\n$PACKAGE_NAME:\\n"')

			def s(*xs):
				return any([x in wig.skip_stages for x in xs])

			if not s('all'):
				w('cd "%s"' % P.root)
				w('PREFIX="%s"' % P.prefix)
				w('LOGBASE="%s"' % P.log_base(wig_name))
				w(S.mkdir_p('$LOGBASE'))
	
			with Stage('Fetching', 'fetch.txt', s('all', 'fetch')) as u:
				u(wig.before_fetch)
				u('dump_env')
				u(wig.gen_fetch_snippet())
				u(wig.after_fetch)
			
			debug_script_path = P.debug_script(wig_name)
			w('[ -d "%s" ] && %s' % (wig.paths.src_dir, S.ln(os.path.abspath(debug_script_path), os.path.join(wig.paths.src_dir, 'wigwam_debug.sh'))))
			with open(debug_script_path, 'w') as out_debug:
				def d(x, prepend = ''):
					if x != 'dump_env':
						w(x, prepend, out_debug)
				if not s('all', 'fetch'):
					w('cd "%s"' % os.path.join(wig.paths.src_dir, wig.working_directory))
					d('cd "%s"' % os.path.abspath(os.path.join(wig.paths.src_dir, wig.working_directory)))

				d('''PREFIX="%s"''' % os.path.abspath(P.prefix))
				d('source "%s"' % P.activate_sh)
				d('')
				d(['# ' + line for line in S.dump_env.split('\n')[1:-1]])
				d('')

				with Stage('Configuring', 'configure.txt', s('all', 'fetch', 'configure', 'make'), hook = d) as u:
					u(wig.before_configure)
					u('dump_env')
					u(wig.gen_configure_snippet())
					u(wig.after_configure)

				with Stage('Compiling', 'make.txt', s('all', 'fetch', 'make'), hook = d) as u:
					u(wig.before_make)
					u('dump_env')
					u(wig.gen_make_snippet())
					u(wig.after_make)

				with Stage('Installing', 'install.txt', s('all', 'install'), hook = d) as u:
					u(wig.before_install)
					u('dump_env')
					u(wig.gen_install_snippet())
					u(wig.after_install)

			update_wigwamfile_installed({wig_name : wig.trace()})
		w('ALLOK=1')
	
	print 'ok [%s]' % installation_script_path

def gen_activate_star_files(bin_dirs, lib_dirs, include_dirs, python_dirs, matlab_dirs):
	export_PATH = lambda var, val: S.export(var, ':'.join(map(os.path.abspath, val) + ['$%s' % var]))
	with open(P.activate_sh, 'w') as out:
		print >> out, export_PATH(S.PATH, bin_dirs)
		print >> out, export_PATH(S.LD_LIBRARY_PATH, lib_dirs)
		print >> out, export_PATH(S.LIBRARY_PATH, lib_dirs)
		print >> out, export_PATH(S.CPATH, include_dirs)
		print >> out, export_PATH(S.PYTHONPATH, python_dirs)

	with open(P.activate_m, 'w') as out:
		for wig_name, matlab_root in matlab_dirs.items():
			print >> out, "%s_ROOT = '%s';" % (wig_name.upper().replace('-', '_'), os.path.abspath(matlab_root))

def unhandled_exception_hook(exc_type, exc_value, exc_traceback):
	if issubclass(exc_type, KeyboardInterrupt):
		print '<CTRL-C> pressed. Aborting.'
		return

	filename, line, dummy, dummy = traceback.extract_tb(exc_traceback).pop()
	filename = os.path.basename(filename)
	error = '%s: %s' % (exc_type.__name__, exc_value)

	print ''
	print 'Unhandled exception occured!'
	print ''
	print 'Please consider filing a bug report at %s' % P.bugreport_page
	print 'Please paste the stack trace below into the issue.'
	print ''
	print '==STACK_TRACE_BEGIN=='
	print ''
	print ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
	print '===STACK_TRACE_END==='
	sys.exit(1)

if __name__ == '__main__':
	sys.excepthook = unhandled_exception_hook

	parser = argparse.ArgumentParser()
	parser.add_argument('--root')
	parser.add_argument('--repo', action = 'append', default = [])
	parser.add_argument('--global', action = 'store_true')
	subparsers = parser.add_subparsers()
	
	subparsers.add_parser('clean').set_defaults(func = clean)
	subparsers.add_parser('lint').set_defaults(func = lint)
	subparsers.add_parser('init').set_defaults(func = init)
	
	cmd = subparsers.add_parser('in')
	cmd.set_defaults(func = enter)
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')
	
	cmd = subparsers.add_parser('status')
	cmd.set_defaults(func = status)
	cmd.add_argument('--verbose', action = 'store_true')

	cmd = subparsers.add_parser('install')
	cmd.set_defaults(func = install)
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('wig_strings', nargs = '+')
	cmd.add_argument('--config', '-D', action = 'append', default = [])
	cmd.add_argument('--reinstall', action = 'store_true')
	cmd.add_argument('--only', action = 'store_true')
	cmd.add_argument('--dangerous', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')
	
	cmd = subparsers.add_parser('build')
	cmd.set_defaults(func = build)
	cmd.add_argument('--dry', action = 'store_true')
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
	cmd.add_argument('--json', action = 'store_true', dest = 'output_json')

	cmd = subparsers.add_parser('run')
	cmd.set_defaults(func = run)
	cmd.add_argument('--verbose', action = 'store_true')
	cmd.add_argument('cmds', nargs = '+')
	
	cmd = subparsers.add_parser('upgrade')
	cmd.set_defaults(func = upgrade)
	cmd.add_argument('wig_names', nargs = '*')
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--only', action = 'store_true')
	cmd.add_argument('--dangerous', action = 'store_true')

	cmd = subparsers.add_parser('remove')
	cmd.set_defaults(func = remove)
	cmd.add_argument('wig_names', nargs = '+')
	cmd.add_argument('--dangerous', action = 'store_true', required = True)
	
	subparsers.add_parser('path').set_defaults(func = path)

	args = vars(parser.parse_args())
	cmd, use_global, extra_repos, arg_root = args.pop('func'), args.pop('global'), args.pop('repo'), args.pop('root')

	local_root_dir = os.path.abspath(arg_root or '.')
	global_root_dir = os.path.expanduser('~')
	use_local = lambda local_file_name, local_cond: ((os.path.exists(os.path.join(local_root_dir, local_file_name)) or cmd == init or local_cond)) and not use_global
	
	root_dir = local_root_dir if use_local(P.wigwamdirname, arg_root != None) else global_root_dir
	wigwamfile_dir = local_root_dir if use_local(P.wigwamfilename, False) else global_root_dir
	P.init(root = os.path.join(root_dir, P.wigwamdirname), wigwamfile = os.path.join(root_dir, P.wigwamfilename), extra_repos = extra_repos)
	
	cmd(**args)
