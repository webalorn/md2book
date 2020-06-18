import subprocess, os, platform, fnmatch, yaml
import random, string
from copy import deepcopy

from util.exceptions import ConfigError

# -------------------- UTILITY -------------------- #

def merge_dicts_recur(settings, overwride):
	if overwride is None:
		return settings
	for key, val in overwride.items():
		if isinstance(val, dict) and isinstance(settings.get(key, None), dict):
			merge_dicts_recur(settings[key], val)
		else:
			settings[key] = deepcopy(val)
	return settings

def rand_str(n):
	return "".join(random.choices(string.ascii_lowercase, k=n))

def is_int(n):
	try:
		m = int(n)
		return True
	except:
		return False

# -------------------- SYSYTEM -------------------- #

def sys_open(filepath):
	filepath = str(filepath)
	if platform.system() == 'Darwin':       # macOS
		subprocess.call(('open', filepath))
	elif platform.system() == 'Windows':    # Windows
		os.startfile(filepath)
	else:                                   # linux variants
		subprocess.call(('xdg-open', filepath))

# -------------------- FILES -------------------- #

def escapePath(path):
	path = str(path)
	path = path.replace(" ", "\\ ")
	return path

def find_files_matching(path, pattern):
	if path.is_file():
		if fnmatch.fnmatch(path.name, pattern):
			yield path
	elif path.is_dir():
		for sub_path in path.iterdir():
			yield from find_files_matching(sub_path, pattern)

def load_yaml_file(filepath, default=None):
	filepath = str(filepath)
	try:
		with open(filepath, "r") as f:
			try:
				return yaml.load(f, Loader=yaml.FullLoader)
			except:
				raise ConfigError("Invalid yaml format", filepath)
	except FileNotFoundError:
		if default is None:
			raise ConfigError("This file doesn't exists", filepath)
	return default