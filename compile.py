import yaml, fnmatch, argparse, tempfile
import subprocess, os, platform, re
from pathlib import Path
from copy import deepcopy as copy
from convert import *
from config import *
from datetime import datetime

# -------------------- UTILITY --------------------

class ConfigError(Exception):
	def __init__(self, where, error):
		self.where = where
		self.error = error
		super().__init__(self.error)

	def __str__(self):
		return "\u001b[31m[ERROR] \u001b[35m{} \u001b[0m: {}".format(str(self.where), str(self.error))

def load_settings():
	try:
		f = open(DEFAULT_SETTINGS, "r")
	except FileNotFoundError:
		return
	try:
		settings = yaml.load(f, Loader=yaml.FullLoader)
	except:
		raise ConfigError(DEFAULT_SETTINGS, "Invalid yaml format in settings")

	for key, val in settings.get("default_target", {}).items():
		DEFAULT_TARGET[key] = val

def create_css_file(content):
	filepath = str(TMP_DIRS[0] / ("font-" + rand_str(10) + ".css"))
	with open(filepath, 'w') as f:
		f.write(content)
	return filepath

def create_default_font_file(default_font):
	return create_css_file(FONT_CSS.replace('FONT-HERE', default_font))

# -------------------- FIND AND LOAD FILES --------------------

def get_cmd_args():
	parser = argparse.ArgumentParser(description='Compile books from CLI')
	targets = " | ".join(list(ALLOWED_FORMATS))
	parser.add_argument('-t', '--target', type=str, help='Target to be compiled [main, user defined, or {}]'.format(targets), default='main')
	parser.add_argument('-o', '--output', type=str, help='Output directory', default=None)
	parser.add_argument('--open', help='Open newly created files', action='store_true', default=False)
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

# -------------------- COMPILE --------------------

def merge_targets(t1, t2):
	new_target = copy(t1)
	for key in t2:
		if key not in ['metadata']:
			new_target[key] = copy(t2[key])
		else:
			for sub_key in t2[key]:
				new_target[key][sub_key] = copy(t2[key][sub_key])

	return new_target

def complete_target(conf, book_path): # Generate metadata and complete informations
	meta = conf['metadata']

	# Main datas
	if conf.get('title', None) is None:
		conf['title'] = conf['name']
	conf['css'] = [str((book_path.parent / p).resolve()) for p in conf['css']]
	if conf['theme']:
		conf['theme'] = SCRIPT_PATH / 'styles' / 'theme-{}.css'.format(conf['theme'])

	# Fonts
	default_font_path = Path(SCRIPT_PATH / 'styles' / 'fonts' / ('web-' + conf['default-font'] + '.css'))
	if conf['default-font'] not in conf['fonts'] and default_font_path.exists():
		conf['fonts'].append(conf['default-font'])

	fonts = [str((SCRIPT_PATH / 'styles' / 'fonts' / ('web-' + f + '.css'))) for f in conf['fonts']]
	fonts.append(create_default_font_file(conf['default-font']))

	if conf['font-size']:
		fonts.append(create_css_file('body { font-size: ' + conf['font-size'] + ';}'))
	conf['css'] = fonts + conf['css']

	# Metadatas
	if conf['cover']:
		meta['cover-image'] = str((book_path.parent / conf['cover']).resolve())
		meta['image'] = meta['cover-image']
	if conf['title']:
		meta['title'].append({'type' : 'main', 'text' : conf['title']})
	if conf['subtitle']:
		meta['title'].append({'type' : 'subtitle', 'text' : conf['subtitle']})
	if meta.get('author', None) is None and conf['by']:
		meta['author'] = conf['by']
	if meta.get('date', None) == 'current':
		meta['date'] = datetime.now().strftime("%Y/%m/%d")

	conf['metadata'] = {key : val for key, val in meta.items() if val is not None}
	return conf

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

REGEX_IMG_MD = r'!\[(.*?)\]\((.*?)\)'
REGEX_IMG_HTML1 = r'<img(.*?)src="(.*?)"'
REGEX_IMG_HTML2 = r"<img(.*?)src='(.*?)'"

def pre_parse_md(content, dir_path):
	# Change relative paths to absolute
	def replace_md_images(match):
		return "![{}]({})".format(match.group(1), str(dir_path / match.group(2)))
	def replace_html_images1(match):
		return '<img{}src="{}"'.format(match.group(1), str(dir_path / match.group(2)))
	def replace_html_images2(match):
		return '<img{}src="{}"'.format(match.group(1), str(dir_path / match.group(2)))

	# <img src="cat.jpg"
	content = re.sub(REGEX_IMG_MD, replace_md_images, content)
	content = re.sub(REGEX_IMG_HTML1, replace_html_images1, content)
	content = re.sub(REGEX_IMG_HTML2, replace_html_images2, content)
	return content

def get_target_md_code(book_path, target):
	path = book_path.resolve().parent
	chapters = []
	for chap_name in target['chapters']:
		try:
			with open(str(path / chap_name), "r", encoding="utf-8") as f:
				content = f.read()
		except FileNotFoundError as e:
			raise ConfigError(book_path, "Chapter {} not found".format(chap_name))

		content = pre_parse_md(content, (path / chap_name).parent.resolve())
		chapters.append(content)
	md_code = target['between_chapters'].join(chapters)
	return md_code

def compile_book(book_path, target_name='main', output_dir=None):
	with open(str(book_path), "r", encoding="utf-8") as f:
		try:
			config = yaml.load(f, Loader=yaml.FullLoader)
		except:
			raise ConfigError(book_path, "Invalid yaml format")
	
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

	if 'main' not in targets_dict:
		raise ConfigError(book_path, "The target 'main' must be defined")
	if target_name not in targets_dict:
		raise ConfigError(book_path, "The target {} is to be built but is not defined".format(target_name))

	target = get_target(targets_dict, target_name, root=True)
	target = complete_target(target, book_path)

	code = get_target_md_code(book_path, target)
	out_format = target['format']

	if out_format not in ALLOWED_FORMATS:
		raise ConfigError(book_path, "The target {} is to be built but is not defined".format(target_name))

	target['base_path'] = book_path
	print("========== Compile {} to {}".format(str(book_path), out_format))
	try:
		out_file = convertBook(code, target, out_format, compile_dir)
		print("Success : ", out_file)
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
			books = find_all_books(args.path)

			for book in books:
				filepath = compile_book(book, args.target, args.output)
				print(filepath)
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

if __name__ == '__main__':
	main()