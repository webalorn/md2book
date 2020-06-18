import re
from pathlib import Path
from urllib.request import urlopen

from .forms import PureCodeData
from util.exceptions import ParsingError
from config import *

class MarkdownCode(PureCodeData):
	EXT = "md"
	
	def __init__(self, code=""):
		self.code = code
		self.meta_code = ""

	def set_conf(self, target):
		super().set_conf(target)
		self.fill_template(target)

		if target.mods['metadata']:
			self.meta_code = target.mods['metadata'].get_yaml_intro()

	def clear_for(self, target_format):
		""" Remove parts that are not needed in some documents """
		if target_format in ['docx']:
			self.purify_code()

	def get(self):
		return self.meta_code + self.code

	def get_base_code_only(self):
		return self.code

	def purify_code(self):
		""" Change some HTML element into markdown """
		REGEX_IMG_HTML = r"<img(.*?)src=['\"](.*?)['\"](.*?)>"
		def replace_image(match):
			attributes = match.group(1) + " " + match.group(3)
			return '![]({})'.format(match.group(2))

		self.code = re.sub(REGEX_IMG_HTML, replace_image, self.code)

class TxtCode(PureCodeData):
	EXT = "txt"

class HtmlCode(PureCodeData):
	EXT = "html"
	def __init__(self, code, title, headers=[]):
		self.code = code
		self.title = title
		self.headers = headers

	def set_conf(self, target):
		super().set_conf(target)
		for style in target.stylesheets:
			self.addStyle(style)

	def getHtmlTag(self, tag, content, **keys_vals):
		keys = ''.join([' {}="{}"'.format(key, val) for key, val in keys_vals.items()])
		if content == None:
			htmltag = '<{tag}{keys} />'
		else:
			htmltag = '<{tag}{keys}>{content}</{tag}>'
		return htmltag.format(tag=tag, content=str(content), keys=keys)

	def addHeader(self, tag, content, **keys_vals):
		self.headers.append(self.getHtmlTag(tag, content, **keys_vals))

	def addStyle(self, path, base_path=""):
		path = str(path)
		try:
			f = urlopen(path)
		except ValueError:
			try:
				f = open(str(Path(base_path) / path))
			except:
				if 'styles/themes/' in path:
					theme = path.split('/')[-1].split('.')[0]
					raise ParsingError('The theme "{}" doesn\'t exists'.format(theme))
				raise ParsingError('Can\'t find the stylesheet {}'.format(path))
		self.addHeader('style', f.read())

	def get(self):
		with open(HTML_TEMPLATE) as f:
			html_struct = f.read()
		code = html_struct.format(
			headers="\n".join(self.headers),
			title=self.title,
			body=self.code
		)
		return code