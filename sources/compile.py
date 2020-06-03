import yaml, fnmatch, argparse, tempfile
import subprocess, os, platform, re
from pathlib import Path
from copy import deepcopy as copy
from .convert import *
from .config import *
from .mdhtml import pre_parse_md
from .templates import get_titlepage_template, TemplateError
from datetime import datetime

# -------------------- UTILITY --------------------

class ConfigError(Exception):
	def __init__(self, where, error):
		self.where = where
		self.error = error
		super().__init__(self.error)

	def __str__(self):
		return "\u001b[31m[ERROR] \u001b[35m{} \u001b[0m: {}".format(str(self.where), str(self.error))

def merge_settings(settings, overwride):
	for key, val in overwride.items():
		if isinstance(val, dict) and isinstance(settings.get(key, None), dict):
			merge_settings(settings[key], val)
		else:
			settings[key] = val
	return settings

def load_settings():
	try:
		f = open(DEFAULT_SETTINGS, "r")
		try:
			settings = yaml.load(f, Loader=yaml.FullLoader)
		except:
			raise ConfigError(DEFAULT_SETTINGS, "Invalid yaml format in settings")
	except FileNotFoundError:
		settings = {}

	# Check the settings
	if not isinstance(settings, dict):
		settings = {}

	settings["default_target"] = settings.get("default_target", {})
	def_target = settings["default_target"]

	for key, val in DEFAULT_TARGET.items():
		if isinstance(val, dict) and not isinstance(def_target.get(key, None), dict):
			def_target[key] = {}
		elif isinstance(val, list) and not isinstance(def_target.get(key, None), list):
			def_target[key] = []

	# Merge settings, and save the file
	DEFAULT_SETTINGS.touch()
	with open(GENERATED_SETTINGS_FILE, 'w') as f:
		yaml.dump({'default_target': DEFAULT_TARGET}, f)
	merge_settings(DEFAULT_TARGET, def_target)


def create_css_file(content):
	filepath = str(TMP_DIRS[0] / ("font-" + rand_str(10) + ".css"))
	with open(filepath, 'w') as f:
		f.write(content)
	return filepath

def create_default_font_file(default_font):
	return create_css_file(FONT_CSS.replace('FONT-HERE', default_font))

def ensure_with_unit(val, default_unit='px'):
	try:
		return str(int(val)) + default_unit
	except:
		return val

# -------------------- FIND AND LOAD FILES --------------------

def get_cmd_args():
	parser = argparse.ArgumentParser(description='Compile books from CLI')
	targets = " | ".join(list(ALLOWED_FORMATS))
	parser.add_argument('-t', '--target', type=str, help='Target to be compiled [main, user defined, or {}]'.format(targets), default='main')
	parser.add_argument('-o', '--output', type=str, help='Output directory', default=None)
	parser.add_argument('--open', help='Open newly created files', action='store_true', default=False)
	parser.add_argument('--remove-images', help='Remove all images in the document', action='store_true', default=False)

	parser.add_argument('path', nargs='?', type=str, help='Path from where to search for the books (optional, the default path is the current directory)', default='.')

	return parser.parse_args()

def find_files_matching(path, pattern):
	if path.is_file():
		if fnmatch.fnmatch(path.name, pattern):
			yield path
	elif path.is_dir():
		for sub_path in path.iterdir():
			yield from find_files_matching(sub_path, pattern)

def find_all_books(path):
	path = Path(path)
	return list(find_files_matching(path, BOOK_FILE_NAMES))

# -------------------- GENERATE METADATA - COMPLETE INFORMATIONS --------------------

def create_final_target(conf, book_path):
	meta = conf['metadata']

	# Main datas
	if conf.get('title', None) is None:
		conf['title'] = conf['name']

	# Styles applied
	custom_css = ""
	conf['css'] = [str((book_path.parent / p).resolve()) for p in conf['css']]
	if conf['theme']:
		conf['theme'] = SCRIPT_PATH / 'styles' / 'themes' / '{}.css'.format(conf['theme'])
	if conf['center-blocks']:
		conf['css'].append(str(SCRIPT_PATH / 'styles' / 'centerblocks.css'))
	if conf['chapter-level']:
		custom_css += "h" + str(conf['chapter-level']).strip() + " { page-break-before: always;}"

	# Fonts
	if conf['default-font']:
		default_font_path = Path(SCRIPT_PATH / 'styles' / 'fonts' / ('web-' + conf['default-font'] + '.css'))
		if conf['default-font'] not in conf['fonts'] and default_font_path.exists():
			conf['fonts'].append(conf['default-font'])

	fonts = [str((SCRIPT_PATH / 'styles' / 'fonts' / ('web-' + f + '.css'))) for f in conf['fonts']]
	if conf['default-font']:
		custom_css += FONT_CSS.replace('FONT-HERE', conf['default-font'])
		# fonts.append(create_default_font_file(conf['default-font']))

	if conf['font-size']:
		custom_css += 'body { font-size: ' + ensure_with_unit(conf['font-size'], 'px') + ';}'
		# fonts.append(create_css_file('body { font-size: ' + conf['font-size'] + ';}'))
	if conf['indent']:
		custom_css += 'body > p, section > p {text-indent : ' + ensure_with_unit(conf['indent'], 'em') + ';}'
	if conf['paragraph-spacing'] is not True:
		spacing = conf['paragraph-spacing']
		if not spacing:
			spacing = "0px"
		custom_css += 'body > p, section > p {margin : ' + ensure_with_unit(spacing, 'px') + ' 0px;}'

	if custom_css:
		fonts.append(create_css_file(custom_css))
	conf['css'] = fonts + conf['css']

	# Metadatas
	if conf['cover']:
		meta['cover-image'] = str((book_path.parent / conf['cover']).resolve())
		meta['image'] = meta['cover-image']
	# if conf['title']:
		# meta['title'].append({'type' : 'main', 'text' : conf['title']})
	meta['title'] = conf['title'].strip()
	if conf['subtitle']:
		# meta['title'].append({'type' : 'subtitle', 'text' : conf['subtitle']})
		meta['subtitle'] = conf['subtitle'].strip()
	if meta.get('author', None) is None and conf['by']:
		meta['author'] = conf['by']
	if meta.get('date', None) == 'current':
		# meta['date'] = datetime.now().strftime("%Y/%m/%d")
		meta['date'] = datetime.now().strftime("%d/%m/%Y")

	# conf['metadata'] = {key : val for key, val in meta.items() if val is not None}
	conf['metadata'] = meta
	return conf

# -------------------- COMPILE --------------------

def get_real_book_path(p):
	p = Path(p)
	if p.is_file() and p.name.endswith(".md") and p.exists():
		conf = p.with_suffix(".book.yml")
		print("Markdown file detected. The configuration file {} will be used instead".format(str(conf)))
		if not conf.exists():
			name = p.with_suffix("").name
			title = re.findall(r"[a-zA-Z0-9']+", name)
			title = " ".join(title).capitalize()

			print("{} doesn't exists and will be created".format(str(conf)))
			print("- title =", title)
			print("- file name =", name)

			conf_content = {'targets' : {'main' : {
				**SIMPLE_TARGET, **{
				'chapters' : [str(p.parts[-1])],
				'name' : name,
				'title' : title,
			}}}}
			with open(str(conf), 'w') as file:
				yaml.dump(conf_content, file)
		return conf
	return p

def merge_targets(t1, t2):
	new_target = copy(t1)
	for key in t2:
		if key not in ['metadata', 'variables']:
			new_target[key] = copy(t2[key])
		else:
			for sub_key in t2[key]:
				new_target[key][sub_key] = copy(t2[key][sub_key])

	return new_target

def get_target(targets_list, target, root=False):
	conf = DEFAULT_TARGET
	if targets_list[target].get('current', False):
		return {}
	targets_list[target]['current'] = True

	inherit = conf.get('inherit', [])
	if root and target != 'main':
		inherit = inherit + ['main']

	for t in inherit:
		conf = merge_targets(conf, get_target(targets_list, t))

	conf = merge_targets(conf, targets_list[target])
	del targets_list[target]['current']

	return conf

def get_target_md_code(book_path, target):
	path = book_path.resolve().parent
	chapters = []
	for chap_name in target['chapters']:
		try:
			with open(str(path / chap_name), "r", encoding="utf-8") as f:
				content = f.read().strip()
		except FileNotFoundError as e:
			raise ConfigError(book_path, "Chapter {} not found".format(chap_name))

		content = pre_parse_md(content, (path / chap_name).parent.resolve())
		chapters.append(content)
	md_code = target['between-chapters'].join(chapters)
	return md_code

def compile_book(book_path, target_name='main', output_dir=None, alt_target={}):
	with open(str(book_path), "r", encoding="utf-8") as f:
		try:
			config = yaml.load(f, Loader=yaml.FullLoader)
		except:
			raise ConfigError(book_path, 'Invalid yaml format')
	
	# Extract informations from the config

	compile_dir = book_path.parent / config.get('compile_in', DEFAULT_GEN_DIR)
	if output_dir:
		compile_dir = Path(output_dir)
	targets_dict = config.get('targets', {})

	for form in ALLOWED_FORMATS: # Allow to specify an output format as a target
		if form not in targets_dict:
			targets_dict[form] = {'format' : form}
		else:
			targets_dict[form]['format'] = form

	compile_dir.mkdir(parents=True, exist_ok=True)

	# Check if the config is valid

	for t in targets_dict:
		for key in targets_dict[t]: # This can help if a key is mispelled
			if key not in DEFAULT_TARGET:
				raise ConfigError(book_path, 'The configuration field "{}" doesn\'t exists (target "{}")'.format(key, t))
	if 'main' not in targets_dict:
		raise ConfigError(book_path, 'The target \'main\' must be defined')
	if target_name not in targets_dict:
		raise ConfigError(book_path, 'The target {} is to be built but is not defined'.format(target_name))

	# Get the target

	target = get_target(targets_dict, target_name, root=True)
	target = merge_targets(target, alt_target)
	target = create_final_target(target, book_path)

	code = get_target_md_code(book_path, target)
	out_format = target['format']

	if out_format not in ALLOWED_FORMATS:
		raise ConfigError(book_path, 'The format {} doesn\' exists'.format(target_name))

	target['base_path'] = book_path
	print('========== Compile {} to {}'.format(str(book_path), out_format))
	try:
		out_file = convertBook(code, target, out_format, compile_dir)
		print('Success : ', out_file)
	except ParsingError as e:
		e.where = book_path
		raise e
	return out_file

# -------------------- MAIN --------------------

def main():
	with tempfile.TemporaryDirectory() as tmpdirname:
		TMP_DIRS.append(Path(tmpdirname).resolve())
		try:
			load_settings()
			args = get_cmd_args()
			path = get_real_book_path(args.path)
			books = find_all_books(path)

			alt_target = {}
			if args.remove_images:
				alt_target['remove-images'] = True

			for book in books:
				filepath = compile_book(book, args.target, args.output, alt_target)
				if args.open:
					if platform.system() == 'Darwin':       # macOS
						subprocess.call(('open', filepath))
					elif platform.system() == 'Windows':    # Windows
						os.startfile(filepath)
					else:                                   # linux variants
						subprocess.call(('xdg-open', filepath))

		except ConfigError as e:
			print(str(e))
		except ParsingError as e:
			print(str(e))
		except TemplateError as e:
			print(str(e))