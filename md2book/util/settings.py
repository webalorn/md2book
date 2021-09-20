import yaml, re
from copy import deepcopy

from md2book.config import *
from .common import merge_dicts_recur, load_yaml_file
from .style import create_css_file
from .exceptions import ConfigError
from md2book.modules import ALL_MODULES

# -------------------- MAIN SETTINGS -------------------- #

def merge_settings(settings, overrride):
	for key, val in overrride.items():
		if isinstance(val, dict) and isinstance(settings.get(key, None), dict):
			merge_settings(settings[key], val)
		else:
			settings[key] = deecopy(val)
	return settings

def load_settings():
	settings = load_yaml_file(DEFAULT_SETTINGS, {})

	# Check the settings
	if not isinstance(settings, dict):
		settings = {}

	def_target = settings.get("default_target", {})

	for key, val in DEFAULT_TARGET.items():
		if isinstance(val, dict) and not isinstance(def_target.get(key, None), dict):
			def_target[key] = {}
		elif isinstance(val, list) and not isinstance(def_target.get(key, None), list):
			def_target[key] = []

	# Merge settings, and save the file
	try:
		with open(GENERATED_SETTINGS_FILE, 'w') as f:
			yaml.dump({'default_target': DEFAULT_TARGET}, f)
	except: # If the user can't write to this location
		pass
	merge_dicts_recur(DEFAULT_TARGET, def_target)

# -------------------- BOOK CONFIG -------------------- #

def create_default_book_config(path, conf_path):
	name = path.with_suffix("").name
	title = re.findall(r"[a-zA-Z0-9']+", name)
	title = " ".join(title).capitalize()

	print("{} doesn't exists and will be created".format(str(conf_path)))
	print("- title =", title)
	print("- file name =", name)

	conf_content = {'targets' : {'main' : {
		**SIMPLE_TARGET, **{
		'chapters' : [str(path.parts[-1])],
		'name' : name,
		'title' : title,
	}}}}
	with open(str(conf_path), 'w') as file:
		yaml.dump(conf_content, file)

# -------------------- BOOK TARGETS -------------------- #

class Target:
	def __init__(self, conf=None, path='.', compile_dir='.'):
		self.conf = conf or deepcopy(DEFAULT_TARGET)
		self.loaded_conf = {}
		self.loaded = set()
		self.path = Path(path)
		self.compile_dir = Path(compile_dir)
		self.is_linked_loaded = False

		self.modules = []
		self.mods = {} # Modules with a name

		self.stylesheets = []
		self.scripts = []

	def __getitem__(self, key):
		return self.conf.get(key)

	def load_from_settings(self, config, form):
		self.conf = {}
		self._load_settings_recur(config, form)
		self.loaded_conf = deepcopy(self.conf)
		self.conf = merge_dicts_recur(deepcopy(DEFAULT_TARGET), self.conf)

	def _load_settings_recur(self, config, form):
		if form in ALLOWED_FORMATS:
			config[form] = config.get(form, {})
			config[form]['format'] = form

		if form in self.loaded:
			return {}
		self.loaded.add(form)

		inherit = ['main'] + config.get('inherit', [])
		for subtarget in inherit:
			self._load_settings_recur(config, subtarget)

		self.merge(config[form])

	def is_user_defined(self, key):
		if isinstance(key, str):
			key = key.split('.')
		key = key[::-1]
		arg = self.loaded_conf
		while key and arg is not None:
			arg = arg.get(key.pop(), None)
		return (arg is not None)

	def merge(self, overrride):
		self.conf = merge_dicts_recur(self.conf, overrride)

	def resolve_format(self):
		self.format = self.conf['format']
		while self.format in FORMAT_ALIASES:
			self.format = FORMAT_ALIASES[self.format]
		if not self.format in BASE_FORMATS:
			raise ConfigError("Format {} doesn't exists".format(self.format))

	def load_modules(self):
		for module_cls in ALL_MODULES:
			if module_cls.NAME is None:
				self.modules.append(module_cls(None, self))
			elif module_cls.NAME in self.conf:
				self.modules.append(module_cls(self.conf.get(module_cls.NAME), self))
				self.mods[module_cls.NAME] = self.modules[-1]
			else:
				self.mods[module_cls.NAME] = None

	def complete(self):
		self.resolve_format()
		self.load_modules()

	def load_linked_files(self):
		custom_css = []
		if self.is_linked_loaded:
			return
		self.is_linked_loaded = True

		for mod in self.modules:
			if mod.get_conf_name():
				self.conf[mod.get_conf_name()] = mod.conf

			self.stylesheets.extend(mod.get_stylesheets())
			self.scripts.extend(mod.get_scripts())
			custom_css.extend(mod.get_custom_css())

		self.stylesheets.append(create_css_file("\n".join(custom_css)))

		for mod in self.modules:
			mod.alter_target()

		self.stylesheets = [str(p) for p in self.stylesheets]
