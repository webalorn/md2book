import argparse, tempfile, glob
from pathlib import Path

from md2book.config import *
from md2book.formats.mdhtml import md_make_paths_absolute
from md2book.util.common import sys_open, load_yaml_file, find_files_matching
from md2book.util.settings import Target, create_default_book_config, load_settings
from md2book.util.exceptions import LocatedError, ConfigError, WarningNoBookFound, SimpleWarning
from md2book.convert.convert import convertBook

def get_cmd_args():
	parser = argparse.ArgumentParser(
		prog=M2B_NAME,
		description=M2B_SHORT_DESCRIPTION,
		epilog=M2B_EPILOG,
	)

	targets = " | ".join(list(ALLOWED_FORMATS))
	parser.add_argument('-t', '--target', action='append', type=str, help='Target to be compiled [main, defined in book.yml, or {}]'.format(targets), default=[])
	parser.add_argument('-o', '--output', type=str, help='Output directory', default=None)
	parser.add_argument('--open', help='Open newly created files', action='store_true', default=False)
	parser.add_argument('--remove-images', help='Remove all images in the document', action='store_true', default=False)
	parser.add_argument('-a', '--all', help='Build all targets defined in the "all" field in the configuration file', action='store_true', default=False)

	parser.add_argument('path', nargs='?', type=str, help='Path from where to search for the books (optional, the default path is the current directory). Can also be a book.yml file or a markdown file.', default='.')

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
		chap_path = str(path / chap_name)
		files = [chap_path]
		if not Path(chap_path).exists():
			files = glob.glob(chap_path)
			if not files:
				raise ConfigError("Chapter(s) {} not found(s)".format(chap_name))
			# TODO : sort

		for file_path in files:
			with open(file_path, "r", encoding="utf-8") as f:
				content = f.read().strip()

			content = md_make_paths_absolute(content, (path / chap_name).parent.resolve())
			chapters.append(content)
	md_code = target['between-chapters'].join(chapters)
	return md_code

def get_all_targets(book_path):
	config = load_yaml_file(book_path)
	all_targets = config.get('all', None)

	if all_targets is None or not isinstance(all_targets, list):
		raise ConfigError(
			'The field "all" must be defined in the configuration file and be a list to use -a or --all',
			book_path
		)
	if all_targets == []:
		raise SimpleWarning('The "all" field is empty', book_path)

	return [str(t) for t in all_targets]

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
	target = Target(path=book_path, compile_dir=compile_dir, conf={})
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
	args = get_cmd_args()
	with tempfile.TemporaryDirectory() as tmpdirname:
		TMP_DIRS.append(Path(tmpdirname).resolve())

		load_settings()
		path = get_real_book_path(args.path)
		books = find_all_books(path)
		target_list = args.target or ['main']

		if not books:
			raise WarningNoBookFound(path)

		overwrite_target = {}
		if args.remove_images:
			overwrite_target['remove-images'] = True

		for book in books:
			if args.all:
				target_list = get_all_targets(book)
				print('=> Compile all targets for {} : {}'.format(str(book), ', '.join(target_list)))

			for target in target_list:
				try:
					filepath = compile_book(book, target, args.output, overwrite_target)
					if args.open:
						sys_open(filepath)
				except LocatedError as e:
					e.set_location(book)
					raise e