import re
from pathlib import Path
from urllib.request import urlopen

from .forms import PureCodeData
from md2book.util.exceptions import ParsingError
from md2book.config import *
from md2book.formats.mddocx import purify_for_docx
from md2book.formats.mdtxt import purify_for_txt

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
			self.code = purify_for_docx(self.code)
		elif target_format in ['txt']:
			self.code = purify_for_txt(self.code)

	def get(self):
		return self.meta_code + self.code

	def get_base_code_only(self):
		return self.code

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
		for script in target.scripts:
			self.addScript(script)

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

	def addScript(self, path, base_path=""):
		base_path = Path(base_path or self.target.path.parent)
		path = str(path)
		try:
			f = urlopen(path)
			self.addHeader('script', '', src=path)
		except ValueError:
			try:
				f = open(str(base_path / path))
			except:
				raise ParsingError('Can\'t find the script {}'.format(path))
			self.addHeader('script', f.read())

	def get(self):
		with open(HTML_TEMPLATE) as f:
			html_struct = f.read()
		code = html_struct.format(
			headers="\n".join(self.headers),
			title=self.title,
			body=self.code
		)
		return code