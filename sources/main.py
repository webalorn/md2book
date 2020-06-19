import argparse, tempfile
from pathlib import Path

from config import *
from formats.mdhtml import md_make_paths_absolute
from util.common import sys_open, load_yaml_file, find_files_matching
from util.settings import Target, create_default_book_config, load_settings
from util.exceptions import LocatedError, ConfigError, WarningNoBookFound
from convert.convert import convertBook

def get_cmd_args():
	parser = argparse.ArgumentParser(description='Compile books from CLI')
	targets = " | ".join(list(ALLOWED_FORMATS))
	parser.add_argument('-t', '--target', type=str, help='Target to be compiled [main, user defined, or {}]'.format(targets), default='main')
	parser.add_argument('-o', '--output', type=str, help='Output directory', default=None)
	parser.add_argument('--open', help='Open newly created files', action='store_true', default=False)
	parser.add_argument('--remove-images', help='Remove all images in the document', action='store_true', default=False)

	parser.add_argument('path', nargs='?', type=str, help='Path from where to search for the books (optional, the default path is the current directory)', default='.')

	return parser.parse_args()

# -------------------- BOOKS -------------------- #

def get_real_book_path(path):
	path = Path(path)
	if path.is_file() and path.name.endswith(".md") and path.exists():
		conf = path.with_suffix(".book.yml")
		print("Markdown file detected. The configuration file {} will be used instead".format(str(conf)))
		if not conf.exists():
			create_default_book_config(path, conf)
		return conf
	return path

def find_all_books(path):
	path = Path(path)
	return list(find_files_matching(path, BOOK_FILE_NAMES))

def get_target_md_code(target):
	path = target.path.resolve().parent
	chapters = []
	for chap_name in target['chapters']:
		try:
			with open(str(path / chap_name), "r", encoding="utf-8") as f:
				content = f.read().strip()
		except FileNotFoundError as e:
			raise ConfigError("Chapter {} not found".format(chap_name))

		content = md_make_paths_absolute(content, (path / chap_name).parent.resolve())
		chapters.append(content)
	md_code = target['between-chapters'].join(chapters)
	return md_code

# -------------------- COMPILE -------------------- #

def check_targets_validity(targets_dict, target_name):
	for t in targets_dict:
		for key in targets_dict[t]: # This can help if a key is mispelled
			if key not in DEFAULT_TARGET:
				raise ConfigError('The configuration field "{}" doesn\'t exists (target "{}")'.format(key, t))
	if 'main' not in targets_dict:
		raise ConfigError('The target \'main\' must be defined')
	if target_name not in list(targets_dict) + ALLOWED_FORMATS:
		raise ConfigError('The target {} is to be built but is not defined'.format(target_name))

def compile_book(book_path, target_name='main', output_dir=None, overwrite_target={}):
	config = load_yaml_file(book_path)
	
	# Extract informations from the config

	if output_dir:
		compile_dir = Path(output_dir)
	else:
		compile_dir = book_path.parent / config.get('compile_in', DEFAULT_GEN_DIR)
	compile_dir.mkdir(parents=True, exist_ok=True)

	targets_dict = config.get('targets', {})
	check_targets_validity(targets_dict, target_name)

	# Load the target
	target = Target(path=book_path, compile_dir=compile_dir)
	target.load_from_settings(targets_dict, target_name)
	target.merge(overwrite_target)
	target.complete()

	print('========== Compile {} to {}'.format(str(book_path), target.format))
	
	code = get_target_md_code(target)
	out_file = convertBook(code, target)

	print('Success : ', out_file)
	return out_file

# -------------------- MAIN -------------------- #

def main():
	with tempfile.TemporaryDirectory() as tmpdirname:
		TMP_DIRS.append(Path(tmpdirname).resolve())

		load_settings()
		args = get_cmd_args()
		path = get_real_book_path(args.path)
		books = find_all_books(path)

		if not books:
			raise WarningNoBookFound(path)

		overwrite_target = {}
		if args.remove_images:
			overwrite_target['remove-images'] = True

		for book in books:
			try:
				filepath = compile_book(book, args.target, args.output, overwrite_target)
				if args.open:
					sys_open(filepath)
			except LocatedError as e:
				e.set_location(book)
				raise e