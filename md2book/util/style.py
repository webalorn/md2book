from pathlib import Path

from md2book.config import *
from .common import rand_str, is_int
from .exceptions import ConfigError

# -------------------- CSS -------------------- #

def create_css_file(content):
	filepath = str(TMP_DIRS[0] / ("style-" + rand_str(10) + ".css"))
	with open(filepath, 'w') as f:
		f.write(content)
	return filepath

def ensure_with_unit(val, default_unit='px'):
	try:
		return str(int(val)) + default_unit
	except:
		return val

# -------------------- FONTS -------------------- #

class FontFamily:
	HTML_PATH = "{syspath}"
	EPUB_PATH = "../fonts/{file}"

	def __init__(self, name):
		basepath = Path(name)
		if '/' not in name and '\\' not in name:
			basepath = EMBED_FONTS_PATH / name
		name = basepath.name

		self.font_path = basepath.resolve()
		self.name = name

		if not self.font_path.exists() or not self.font_path.is_dir():
			raise ConfigError("Font {} ({}) doesn't exists".format(self.name, str(self.font_path)))

		font_files = [p for p in self.font_path.iterdir() if p.stem.startswith(self.name)]
		self.font_files = []

		for file in font_files:
			try:
				name, style, weight = file.stem.split('-')
			except ValueError as e:
				raise ConfigError('A font file should be name using the format "fontname-style-weight"')
			if style not in ['normal', 'italic']:
				raise ConfigError("{} is not a valid style for a font (first parameter)".format(style))
			if weight not in ['normal', 'bold'] and not is_int(weight):
				raise ConfigError("{} is not a valid weight for a font (second parameter)".format(weight))

			self.font_files.append((file, style, str(weight)))

	def get_css(self, form):
		if form in ['epub']:
			src_template = self.EPUB_PATH
		else:
			src_template = self.HTML_PATH

		css = []
		for file, style, weight in self.font_files:
			src = src_template.format(
				file=file.name,
				syspath=str(file),
			)
			css.append(FONT_FAMILY_CSS.format(
				font=self.name,
				style=style,
				weight=weight,
				src=src
			))
		return css
