import os
import re
import sys
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

		P.wigwamfile = wigwamfile
		P.src_tree = os.path.join(P.root, 'src')
		P.prefix = os.path.join(P.root, 'prefix')
		P.log_root = os.path.join(P.root, 'log')
		P.tar_root = os.path.join(P.root, 'tar')
		P.deb_root = os.path.join(P.root, 'deb')
		P.debug_root = os.path.join(P.root, 'debug')
		P.activate_sh = os.path.join(P.root, 'activate.sh')
		P.build_script = os.path.join(P.root, 'build.generated.sh')
		P.wigwamfile_installed = os.path.join(P.root, P.wigwamfilename + '.installed')
				
		P.prefix_deb = os.path.join(P.prefix, 'deb')
		P.prefix_python = os.path.join(P.prefix, 'python')
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
	
	onoff = staticmethod({True : 'on', False : 'off'}.get)
	ONOFF = staticmethod({True : 'ON', False : 'OFF'}.get)
	qq = staticmethod('"{}"'.format)
	download = staticmethod(('wget {} -O "{}"' if 0 == subprocess.call(['which', 'wget'], stdout = subprocess.PIPE, stderr = subprocess.PIPE) else 'curl {} -o "{}"').format)
	mkdir_p = staticmethod('mkdir -p "{}"'.format)
	ln = staticmethod('ln -f -s "{}" "{}"'.format)
	rm_rf = staticmethod(lambda *args: 'rm -rf {}'.format(' '.join(map(S.qq, args))))
	cd = staticmethod('cd "{}"'.format)
	export = staticmethod('export {}="{}"'.format)
	export_prepend_paths = staticmethod(lambda var_name, paths: S.export(var_name, os.path.pathsep.join(paths + ['$' + var_name])))
	configure = staticmethod(lambda flags: './configure {}'.format(' '.join(flags)))
	make = staticmethod(lambda flags: 'make {}'.format(' '.join(flags)))
	make_jobs = staticmethod('-j{}'.format)
	makeflags = staticmethod(lambda flags: '{}="{} {}"'.format(S.MAKEFLAGS, ' '.join(flags), os.getenv(S.MAKEFLAGS, '')) if flags else '')
	make_install = staticmethod(lambda flags: 'make install {}'.format(' '.join(flags)))
	python_setup_install = 'python setup.py install --prefix="{}"'.format(PREFIX_PYTHON)

class Wig(object):
	fetch_method = None
	version = None
	git_uri = None
	git_branch = None
	git_commit = None
	tar_uri = None
	tar_strip_components = None
	working_directory = '.'

	config_access = []
	dependencies = []
	optional_dependencies = []
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
		self.before_build = []
		self.after_build = []
		self.before_install = []
		self.after_install = []

		self.env = {}
		self.enabled_features = []
		self.disabled_features = []
		self.dependencies_ = set()
		self.fetch_method = self.fetch_method or ('tar' if hasattr(self, 'tar_uri') else 'git' if hasattr(self, 'git_uri') else None)
		self.paths = type('', (), dict(src_dir = os.path.join(P.src_tree, self.name)))()

	def dict_config(self):
		if self.fetch_method == 'tar':
			return dict(fetch_params = dict(fetch_method = self.fetch_method, version = self.version))
		elif self.fetch_method == 'git':
			find_last_git_commit = lambda: [commit for commit, head in map(str.split, filter(bool, subprocess.check_output(['git', 'ls-remote', self.git_uri]).split('\n'))) if (self.git_branch or 'HEAD') in head][0][:7]
			return dict(fetch_params = dict(fetch_method = self.fetch_method, git_commit = self.git_commit or find_last_git_commit(), git_branch = self.git_branch))
		else:
			return {}
	
	def load_dict_config(self, dict_config, env):
		self.env = env
		self.enabled_features += dict_config.get('enabled_features', [])
		self.disabled_features += dict_config.get('disabled_features', [])
		self.fetch_params = dict(dict(fetch_method = self.fetch_method, version = self.version, git_uri = self.git_uri, git_branch = self.git_branch, git_commit = self.git_commit, tar_uri = self.tar_uri, tar_strip_components = self.tar_strip_components).items() + dict_config.get('fetch_params', {}).items())

	def trace(self):
		return dict(self.fetch_params.items() + dict(enabled_features = self.enabled_features, disabled_features = self.disabled_features).items())
	
	def fetch(self):
		def git(target_dir, git_uri, git_commit = None, git_branch = None, git_tag = None, **ignored):
			git_tag = git_tag or git_commit or git_branch
			return [S.rm_rf(target_dir), 'git clone --recursive "{}" "{}"'.format(git_uri, target_dir)] + (['cd "{}"'.format(target_dir), 'git checkout "{}"'.format(tag)] if git_tag is not None else [])

		def tar(target_dir, tar_uri, version, tar_strip_components = 1, **ignored):
			downloaded_file_path = os.path.join(P.tar_root, os.path.basename(target_dir) + [e for e in ['.tar', '.tar.gz', '.tar.bz2', '.tgz'] if tar_uri.endswith(e)][0])
			return [S.rm_rf(target_dir), S.mkdir_p(target_dir), S.download(tar_uri.format(VERSION = version), downloaded_file_path), 'tar -xf "{}" -C "{}" --strip-components={}'.format(downloaded_file_path, target_dir, 1 if tar_strip_components is None else tar_strip_components)]

		def uri(target_dir, uri, **ignored):
			downloaded_file_path = os.path.join(target_dir, os.path.basename(uri))
			return [S.rm_rf(target_dir), S.mkdir_p(target_dir), S.download(uri, downloaded_file_path)]

		return locals()[self.fetch_params['fetch_method']](self.paths.src_dir, **self.fetch_params)
	
	def configure(self):
		return S.configure(self.configure_flags)

	def build(self):
		return S.make(self.make_flags)

	def install(self):
		return S.make_install(self.make_install_flags) if 'install' not in self.skip_stages else []

	def setup(self):
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

class WigConfig(object):
	def __init__(self, dict_config):
		dict_config = dict_config.copy()
		self.env = dict_config.pop('_env', {})
		self.dict_config = lambda: dict_config

		self.wigs = {}
		for wig_name, wig_dict_config in self.dict_config().items():
			wig = WigConfig.find_and_construct_wig(wig_name)
			wig.load_dict_config(wig_dict_config, self.env)
			for dep_wig_name in wig.dependencies:
				wig.require(dep_wig_name)
			wig.setup()
			wig.enabled_features += wig_dict_config.get('enabled_features', [])
			wig.disabled_features += wig_dict_config.get('disabled_features', [])
			self.wigs[wig_name] = wig

		for wig_name in self.wigs:
			self.wigs[wig_name].process_feature_hooks()

		flatten = lambda xs: list(itertools.chain(*xs))
		self.bin_dirs = P.prefix_bin_dirs + flatten(map(lambda wig: wig.bin_dirs, self.wigs.values()))
		self.lib_dirs = P.prefix_lib_dirs + flatten(map(lambda wig: wig.lib_dirs, self.wigs.values()))
		self.include_dirs = P.prefix_include_dirs + flatten(map(lambda wig: wig.include_dirs, self.wigs.values()))
		self.python_dirs = P.prefix_python_dirs + flatten(map(lambda wig: wig.python_dirs, self.wigs.values()))

	@staticmethod
	def read_dict_config(path):
		with open(path, 'r') as f:
			return json.load(f) if os.path.exists(path) else {}

	@staticmethod
	def save_dict_config(path, dict_config):
		with open(path, 'w') as f:
			json.dump(dict_config, f, indent = 2, sort_keys = True)

	@staticmethod
	def patch_dict_config(dict_config, diff):
		dict_config = dict_config.copy()
		if '_env' in diff:
			dict_config['_env'] = dict(dict_config.get('_env', {}).items() + diff.pop('_env', {}).items())
		for wig_name, wig_dict_config in diff.items():
			dict_config[wig_name] = wig_dict_config #if wig_name not in dict_config
		return dict_config

	@staticmethod
	def find_and_construct_wig(wig_name):
		wig_class = [s for k, s in {}.items() if wig_name.startswith(k)] # [s for k, s in {'deb-' : DebWig, 'lua-' : LuarocksWig, 'pip-' : PipWig}.items() if wig_name.startswith(k)]
		for repo in P.repos:
			try:
				content = (open if 'github.com' not in repo else urllib2.urlopen)(os.path.join(repo.replace('github.com', 'raw.githubusercontent.com').replace('/tree/', '/'), wig_name + '.py')).read()
				exec content in globals(), globals()
				wig_class += [globals().get(wig_name.replace('-', '_'))]
				break
			except:
				continue
		assert wig_class, 'Package [{}] is not found'.format(wig_name)
		return wig_class[0](wig_name)
		
	def diff(self, graph):
		to_install = {}
		for wig_name, wig in self.wigs.items():
			other = graph.wigs.get(wig_name)
			if wig.trace() != (other.trace() if other is not None else None):
				to_install[wig_name] = dict(enabled_features = wig.enabled_features, disabled_features = wig.disabled_features, fetch_params = wig.fetch_params)
		return to_install

	def compute_installation_order(self):
		transitive_closure = {wig_name : self.find_dependencies([wig_name]) for wig_name in self.wigs}
		return sorted(self.wigs, cmp = lambda l, r: -1 if l in transitive_closure[r] else 1 if r in transitive_closure[l] else cmp(l.lower(), r.lower()))

	def find_dependencies(self, wig_names, dependencies = True, dependent = False):
		graph = {wig_name : self.wigs[wig_name].dependencies_ for wig_name in self.wigs} if dependencies else {wig_name : filter(lambda w: wig_name in self.wigs[w].dependencies_, self.wigs) for wig_name in self.wigs}
		visited = set()
		def dfs(v):
			visited.add(v)
			for u in graph[v]:
				if u not in visited:
					dfs_(u)
		for v in wig_names:
			if v not in visited:
				dfs(v)
		return visited

	def find_unsatisfied_dependencies(self):
		get_immediate_unsatisfied_dependencies = lambda wig_config: {x : [] for x in set((dep_wig_name for wig in wig_config.wigs.values() for dep_wig_name in wig.dependencies_ if dep_wig_name not in wig_config.wigs))}
		end = self.dict_config().copy()
		while True:
			to_install = {wig_name : WigConfig.find_and_construct_wig(wig_name).dict_config() for wig_name in get_immediate_unsatisfied_dependencies(WigConfig(end))}
			if len(to_install) == 0:
				break
			end = WigConfig.patch_dict_config(end, to_install)
		return WigConfig(end).diff(self)

def remove(wig_names):
	init()
	
	requested = WigConfig.read_dict_config(P.wigwamfile)
	installed = WigConfig.read_dict_config(P.wigwamfile_installed)
	
	for wig_name in wig_names:
		if wig_name in installed:
			print('Package [{}] is already installed, artefacts will not be removed.'.format(wig_name))
		requested.pop(wig_name, None)
		installed.pop(wig_name, None)
		src_dir = os.path.join(P.src_tree, wig_name)
		if os.path.exists(src_dir):
			shutil.rmtree(src_dir)
			
	WigConfig.save_dict_config(P.wigwamfile, requested)
	WigConfig.save_dict_config(P.wigwamfile_installed, installed)

def install(wig_names, wigwamfile, enable, disable, git, version, env, force, verbose, dry):
	init()
	
	end = WigConfig.patch_dict_config(WigConfig.read_dict_config(P.wigwamfile), dict(_env = env))
	for wig_name in wig_names:
		dict_config = WigConfig.find_and_construct_wig(wig_name).dict_config()
		if enable:
			dict_config['enabled_features'] = enable
		if disable:
			dict_config['disabled_features'] = disable
		if git:
			dict_config['fetch_params'].update(dict(fetch_method = 'git', git_tag = git))
		if version:
			dict_config['fetch_params'].update(dict(fetch_method = 'tar', version = version))
		end = WigConfig.patch_dict_config(end, {wig_name : dict_config})
	WigConfig.save_dict_config(P.wigwamfile, WigConfig.patch_dict_config(end, WigConfig(end).find_unsatisfied_dependencies()))
	
	installed = WigConfig(WigConfig.read_dict_config(P.wigwamfile_installed))
	requested = WigConfig(end)
	dependencies = requested.find_dependencies(wig_names, dependencies = True)
	to_build = set(filter(lambda wig_name: wig_name in dependencies, requested.diff(installed)) + (wig_names if force else []))

	build(to_build, verbose = verbose, dry = dry)

def upgrade(wig_names, recursive, verbose, dry):
	init()

	old = WigConfig.read_dict_config(P.wigwamfile)
	patch = {wig_name : dict(fetch_params = fetch_params_new) for wig_name in (wig_names or sorted(old)) if wig_name != '_env' for fetch_params_new in [WigConfig.find_and_construct_wig(wig_name).dict_config().get('fetch_params')] if wig_name in old and fetch_params_new != old[wig_name].get('fetch_params')}
	print('Going to upgrade packages:' if len(patch) > 0 else '')
	for wig_name in patch:
		print('\t[{0}]: {1} -> {2}'.format(wig_name, json.dumps(old[wig_name]['fetch_params'], json.dumps(patch[wig_name]['fetch_params'])))
	end = WigConfig.patch_dict_config(old.copy(), patch)
	WigConfig.save_dict_config(P.wigwamfile, end)

	installed = WigConfig(WigConfig.read_dict_config(P.wigwamfile_installed))
	requested = WigConfig(end)
	dependencies = requested.find_dependencies(wig_names, dependencies = True) + (requested.find_dependencies(wig_names, dependent = True) if recursive else [])
	to_build = set(filter(lambda wig_name: wig_name in dependencies, requested.diff(installed)) + (wig_names if force else []))

	build(wig_names, install_only_seeds = not recursive, dry = dry, verbose = verbose)

def build(wig_names, verbose = False, dry = False):
	def write_build_script(installation_script_path, wigs, env, installation_order):
		if os.path.exists(installation_script_path):
			os.remove(installation_script_path)

		if len(installation_order) == 0:
			return

		print('{} packages to be installed in the order below:'.format(len(installation_order)))
		for wig_name in installation_order:
			print('{0:10}'.format(wig_name) + ('    requires  {}'.format(', '.join(wigs[wig_name].dependencies_)) if wigs[wig_name].dependencies_ else ''))
		print('')

		build_script = [
			'''set -e #vx
			trap show_log EXIT
			trap on_ctrl_c SIGINT
			exec 3>&1
			source "{}"
			TIC="$(date +%s)"
			show_log() {
				exec 1>&3
				if [ -z $ALLOK ] || [ $CTRLCPRESSED ]
				then
					printf "error!\\n\\n"
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
			
			on_ctrl_c() {
				exec 1>&3
				echo "<CTRL+C> pressed. Aborting"
				CTRLCPRESSED=1
				reset
				exit 1
			}
			update_wigwamfile_installed() {
				python -c "import sys, json; installed, diff = map(json.load, [open(sys.argv[-1]), sys.stdin]); installed.update(diff); json.dump(installed, open(sys.argv[-1], 'w'), indent = 2, sort_keys = True)" $@
			}
			print_ok_toc() {
				TOC="$(($(date +%s)-TIC))"
				echo "ok [elapsed $((TOC/60%60))m$((TOC%60))s]"
			}
			'''.replace('{}', P.activate_sh),
			S.rm_rf(*[P.log_base(wig_name) for wig_name in installation_order])
		]
		update_wigwamfile_installed = lambda d:	build_script.append('''cat <<"EOF" | update_wigwamfile_installed "{}"\n{}\nEOF\n'''.format(os.path.abspath(P.wigwamfile_installed), json.dumps(d)))
		coalesce_list = lambda obj: obj if isinstance(obj, list) else [obj]

		update_wigwamfile_installed(dict(_env = env))
		for wig in map(wigs.get, installation_order):
			stage_skip_stages = [('fetch', ['fetch']), ('configure', ['fetch', 'configure']), ('build', ['fetch', 'build']), ('install', ['install'])]
			debug_script, debug_script_path = [], P.debug_script(wig.name)
			debug_script += [
				'''PREFIX="{}"'''.format(os.path.abspath(P.prefix)),
				'source "{}"'.format(P.activate_sh),
				S.cd(os.path.abspath(os.path.join(wig.paths.src_dir, wig.working_directory)))
			]
			for stage, skip_stages in stage_skip_stages[1:]:
				if all([stage not in wig.skip_stages for stage in skip_stages]):
					debug_script += ['(']
					debug_script += getattr(wig, 'before_' + stage)
					debug_script += coalesce_list(getattr(wig, stage)())
					debug_script += getattr(wig, 'after_' + stage)
					debug_script += [')']

			build_script += [
				'PACKAGE_NAME={}'.format(wig.name),
				'PREFIX="{}"'.format(P.prefix),
				'LOGBASE="{}"'.format(P.log_base(wig.name)),
				'printf "\\n$PACKAGE_NAME:\\n"',
				S.mkdir_p('$LOGBASE'),
				'cd "{}"'.format(P.root)
			]
			for stage, skip_stages in stage_skip_stages:
				if all([stage not in wig.skip_stages for stage in skip_stages]):
					build_script += [
						'printf "%14s...  " {}'.format(stage.capitalize()),
						'LOG="$LOGBASE/{}.txt"'.format(stage),
						'('
					]
					build_script += getattr(wig, 'before_' + stage)
					build_script += ['WIGWAM_DUMPENV']
					build_script += coalesce_list(getattr(wig, stage)())
					build_script += getattr(wig, 'after_' + stage)
					build_script += [
						') > "$LOG" 2>&1',
						'print_ok_toc',
						S.cd(os.path.abspath(os.path.join(wig.paths.src_dir, wig.working_directory))) if stage == 'fetch' else ''
					]
			build_script += [
				S.mkdir_p(wig.paths.src_dir),
				S.ln(os.path.abspath(debug_script_path), os.path.join(wig.paths.src_dir, 'wigwam_debug.sh'))
			]
			update_wigwamfile_installed({wig_name : wig.trace()})

			with open(debug_script_path, 'w') as out:
				out.write('\n'.join(debug_script))

		build_script += ['ALLOK=1']
		with open(installation_script_path, 'w') as out:
			out.write('\n'.join(build_script))
		
		print('Installation script generated: [{}]'.format(installation_script_path))

	def write_activate_files(bin_dirs, lib_dirs, include_dirs, python_dirs):
		activate_sh = [
			S.export_prepend_paths(S.PATH, bin_dirs),
			S.export_prepend_paths(S.LD_LIBRARY_PATH, lib_dirs),
			S.export_prepend_paths(S.LIBRARY_PATH, lib_dirs),
			S.export_prepend_paths(S.CPATH, include_dirs),
			S.export_prepend_paths(S.PYTHONPATH, python_dirs),
			S.export(S.WIGWAM_PREFIX, os.path.abspath(P.prefix)),
			'''function WIGWAM_DUMPENV {
				echo "PWD=$PWD"
				echo "PATH=$PATH"
				echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
				echo "CPATH=$CPATH"
				echo "LIBRARY_PATH=$LIBRARY_PATH"
				echo "g++ -print-search-dirs: $(g++ -print-search-dirs)"
			}
			'''
		]
		with open(P.activate_sh, 'w') as out:
			out.write('\n'.join(activate_sh))

	requested = WigConfig(WigConfig.read_dict_config(P.wigwamfile))
	installation_order = filter(lambda wig_name: wig_name in wig_names, requested.compute_installation_order())
	write_activate_files(requested.bin_dirs, requested.lib_dirs, requested.include_dirs, requested.python_dirs)
	write_build_script(P.build_script, requested.wigs, requested.env, installation_order)

	if dry:
		print('Dry run. Quitting.')
		return
	print('Running installation script now:' if len(installation_order) > 0 else '0 packages to be reconfigured. Quitting.')
	if os.path.exists(P.build_script) and 0 == subprocess.call(['bash'] + (['-xv'] if verbose else []) + [P.build_script]):
		print('\nALL OK. KTHXBAI!')
	
def which(wigwamfile, prefix):
	print(os.path.abspath(P.wigwamfile if wigwamfile else P.prefix if prefix else P.root))

def status(verbose):
	init()
	
	traces = lambda wigwamfile_path: {wig_name : wig.trace() for wig_name, wig in WigConfig(WigConfig.read_dict_config(wigwamfile_path)).wigs.items()}
	requested, installed = map(traces, [P.wigwamfile, P.wigwamfile_installed])
	format_version = lambda traces_dic, wig_name: json.dumps(traces_dic[wig_name]) if wig_name in traces_dic else ''	
	
	if len(requested) == 0 and len(installed) == 0:
		print('No packages installed')
		return

	fmt = '{0:9}\t{1:>20}\t{2:>10}\t' + ('{3}' if verbose else '')
	print(fmt.format('INSTALLED', 'NAME', 'VERSION'))
	for wig_name in sorted(set(requested) | set(installed)):
		requested_version, installed_version = [format_version(t, wig_name) for t in [requested, installed]]
		is_installed, is_conflicted = wig_name in installed, requested_version != installed_version
		version = requested_version if not is_installed else (installed_version if not is_conflicted else '*CONFLICT*')
		print(fmt.format('*' if is_installed else '', wig_name, version))

def clean(wigwamfile):
	for f in P.generated_files + ([P.wigwamfile] if wigwamfile else []):
		if os.path.exists(f):
			os.remove(f)
	for d in P.artefact_dirs:
		if os.path.exists(d):
			shutil.rmtree(d)

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
	subprocess.call('cat "{}" | less'.format('" "'.join([os.path.join(P.log_base(wig_name), stage + '.txt') for stage in stages])), shell = True)

def search(wig_name):
	filter_wig_names = lambda file_names: [file_name for file_name, ext in map(os.path.splitext, file_names) if ext == '.py']
	to_json = lambda wig: {'name' : wig.name, 'dependencies' : wig.dependencies, 'optional_dependencies' : wig.optional_dependencies, 'config_access' : wig.config_access}

	def all_wig_names():
		for repo in P.repos:
			if 'github' in repo:
				github_api_clues = re.search('.*github.com/(?P<repo_owner>.+)/(?P<repo_name>.+)/tree/(?P<ref>.+)/(?P<path>.+)', repo).groupdict()
				github_api_uri = 'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{path}?ref={ref}'.format(**github_api_clues)
				yield filter_wig_names([github_file_info['name'] for github_file_info in json.load(urllib2.urlopen(github_api_uri))])
			else:
				yield filter_wig_names(os.listdir(repo)) if os.path.exists(repo) else []
		
	wigs = map(WigConfig.find_and_construct_wig, sorted(set([wig_name] if wig_name else itertools.chain(*all_wig_names()))))
	print(json.dumps(map(to_json, wigs), indent = 2, sort_keys = True))

def run(dry, verbose, cmds = []):
	if os.path.exists(P.activate_sh):
		cmd = ('''bash --rcfile <(cat "$HOME/.bashrc"; cat "{}") -ci{} {}'''.format(P.activate_sh, 'x' if verbose else '', pipes.quote(' '.join(map(pipes.quote, cmds))))) if cmds else ('''bash {} --rcfile <(cat "$HOME/.bashrc"; cat "{}"; echo 'export PS1="$PS1/\ $ "') -i'''.format('-xv' if verbose else '', P.activate_sh))
		if dry:
			print(cmd)
			print('# {}:'.format(P.activate_sh))
			print(''.join(open(P.activate_sh)))
		else:
			subprocess.call(['bash', '-cx' if verbose else '-c', cmd])
	else:
		print('The activate shell script does not exist yet. Run "wigwam build" first.')

if __name__ == '__main__':
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
	cmd.add_argument('wig_names', nargs = '*')
	cmd.add_argument('--wigwamfile')
	cmd.add_argument('--enable', nargs = '+', default = [])
	cmd.add_argument('--disable', nargs = '+', default = [])
	group = cmd.add_mutually_exclusive_group()
	group.add_argument('--git', nargs = '?', const = True)
	group.add_argument('--version')
	cmd.add_argument('--env', '-D', action = type('', (argparse.Action, ), dict(__call__ = lambda a, p, n, v, o: getattr(n, a.dest).update(dict([v.split('=')])))), default = {})
	cmd.add_argument('--force', action = 'store_true')
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')
	
	cmd = subparsers.add_parser('upgrade')
	cmd.set_defaults(func = upgrade)
	cmd.add_argument('wig_names', nargs = '*')
	cmd.add_argument('--dry', action = 'store_true')
	cmd.add_argument('--verbose', action = 'store_true')
	cmd.add_argument('--recursive', action = 'store_true')
	
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
	group = cmd.add_mutually_exclusive_group()
	group.add_argument('--wigwamfile', action = 'store_true')
	group.add_argument('--prefix', action = 'store_true')
	cmd.set_defaults(func = which)
	
	cmd = subparsers.add_parser('status')
	cmd.set_defaults(func = status)
	cmd.add_argument('--verbose', action = 'store_true')
	
	cmd = subparsers.add_parser('log')
	cmd.set_defaults(func = log)
	cmd.add_argument('wig_name')
	cmd.add_argument('--fetch', action = 'store_true')
	cmd.add_argument('--configure', action = 'store_true')
	cmd.add_argument('--build', action = 'store_true')
	cmd.add_argument('--install', action = 'store_true')

	cmd = subparsers.add_parser('search')
	cmd.set_defaults(func = search)
	cmd.add_argument('wig_name', default = None, nargs = '?')

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
	root_dir = local_root_dir if use_local(P.wigwamdirname, arg_root is not None) else global_root_dir
	wigwamfile_dir = local_root_dir if use_local(P.wigwamfilename, False) else global_root_dir

	try:
		P.init(root = os.path.join(root_dir, P.wigwamdirname), wigwamfile = os.path.join(root_dir, P.wigwamdirname, P.wigwamfilename), extra_repos = extra_repos)
		cmd(**args)
	except KeyboardInterrupt:
		print('<CTRL-C> pressed. Aborting.')
	except:
		print('Unhandled exception occured! Please consider filing a bug report at {} along with the stack trace below:'.format(P.bugreport_page))
		raise
