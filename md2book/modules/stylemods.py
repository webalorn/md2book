from .base import BaseModule
from md2book.config import *
from md2book.util.style import ensure_with_unit, FontFamily
from md2book.util.common import escapePath, load_yaml_file
from md2book.util.exceptions import ConfigError

class StyleModule(BaseModule):
	NAME = 'style'
	def get_stylesheets(self):
		styles = []
		if self.conf.get("center-blocks", None):
			styles.append(DATA_PATH / 'styles' / 'centerblocks.css')

		return styles

	def get_custom_css(self):
		css = []
		chappter_level = self.target.conf['chapter-level']
		if chappter_level:
			css.append("h" + str(chappter_level).strip() + " { page-break-before: always;}")

		if self.conf['indent']:
			indent = ensure_with_unit(self.conf['indent'], 'em')
			css.append('body > p, section > p {text-indent : ' + indent + ';}')

		if self.conf['align']:
			css.append('body {text-align : ' + self.conf['align'] + ';}')

		if self.conf['paragraph-spacing'] is not True:
			spacing = self.conf['paragraph-spacing'] or '0px'
			spacing = ensure_with_unit(spacing, 'px')
			css.append('body > p, section > p {margin : ' + spacing + ' 0px;}')

		return css
	
class SepModule(BaseModule):
	NAME = 'sep'
	def __init__(self, conf, target):
		self.sep = str(conf)
		super().__init__(conf, target)

	def get_custom_css(self):
		sep = self.sep.replace('"', '\\"')
		return [".sepcontent::before{content : \"" + sep + "\"}"]

class FontModule(BaseModule):
	NAME = 'font'
	FONT_CSS = 'body {{ font-family: "{font}","Clear Sans","Helvetica Neue",Helvetica,Arial,sans-serif;}}'

	def __init__(self, conf, target):
		super().__init__(conf, target)
		self.try_add_font(self.conf['default'])

	def get_fonts(self):
		return [FontFamily(font) for font in self.conf['include']]

	def try_add_font(self, name):
		base_font_dir = DATA_PATH / 'fonts' / str(name)
		if name not in self.conf['include'] and base_font_dir.exists():
			self.conf['include'].append(name)

	def get_custom_css(self):
		css = []
		for font in self.get_fonts():
			css.extend(font.get_css(self.format))
		if self.conf['default']:
			css.append(self.FONT_CSS.format(font=self.conf['default']))
		if self.conf['size']:
			size = ensure_with_unit(self.conf['size'], 'px')
			css.append('body { font-size: ' + size + ';}')
		return css

	def pandoc_options(self, dest_format):
		options = super().pandoc_options(dest_format)
		if dest_format == 'epub':
			for font in self.get_fonts():
				path = escapePath(font.font_path / (font.name + "*"))
				options.append("--epub-embed-font=" + path)
		return options

class ThemeModule(BaseModule):
	NAME = 'theme'

	def __init__(self, conf, target):
		super().__init__(conf, target)
		self.theme = conf
		self.styles = []
		self.settings = {}

		if self.theme:
			theme_path = DATA_PATH / 'themes' / (self.theme + '.yml')
			if not (theme_path.exists() and theme_path.is_file()):
				raise ConfigError("The theme {} doesn't exists".format(self.theme))

			self.settings = load_yaml_file(theme_path)
			self.styles = [DATA_PATH / 'styles' / s for s in self.settings.get('css', [])]

			if 'toc' in self.settings and not self.target.is_user_defined('toc.style'):
				self.target.conf['toc']['style'] = self.settings['toc']

			if 'font' in self.settings and not self.target.is_user_defined('font.default'):
				self.target.conf['font']['default'] = self.settings['font']
