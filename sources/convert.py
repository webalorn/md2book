from pathlib import Path
from urllib.request import urlopen
from copy import deepcopy as copy
import markdown, random, string, shutil, pdfkit, yaml
import os, subprocess, re
from .config import *
from .templates import *
from .mdhtml import *

# -------------------- UTILITY --------------------

class ParsingError(Exception):
	def __init__(self, error):
		self.error = error
		self.where = ''
		super().__init__(self.error)

	def __str__(self):
		return "\u001b[31m[ERROR] \u001b[35m{} \u001b[0m {}".format(self.where, str(self.error))

def rand_str(n):
	return "".join(random.choices(string.ascii_lowercase, k=n))

def escapePath(path):
	path = str(path)
	path = path.replace(" ", "\\ ")
	return path

# -------------------- CODE CLASSES --------------------

class CodeData:
	EXT = ".txt"
	REF_DOC = False

	def assertLang(self, *langsCls):
		for lang in langsCls:
			if isinstance(self, lang):
				return True
		raise exception("Code {} is not in {}".format(self.lang, str(langs)))

	def getStorageFile(self):
		filepath = TMP_DIRS[0] / (rand_str(10) + self.EXT)
		filepath.parent.mkdir(parents=True, exist_ok=True)
		return filepath

	def getStrPath(self):
		return str(self.getStorageFile())

	def getPandocOutputOptions(self):
		return []

	def set_conf(self, target_config):
		pass

# ----- File-based

class OutFileCode(CodeData):
	def __init__(self):
		self.filepath = self.getStorageFile()

	def get(self):
		return self.filepath

	def getStrPath(self):
		return str(self.filepath.resolve())

	def output(self, dest=None):
		if dest:
			shutil.copy(str(self.filepath), str(dest))
			return dest
		return self.filepath

	def load_from(self, path):
		self.filepath = path

	def set_conf(self, target_config):
		self.toc_enabled = bool(target_config['enable-toc'])
		self.toc_depth = target_config['toc-level']

	def getPandocOutputOptions(self):
		params = super().getPandocOutputOptions()
		# params.append("--epub-chapter-level=" + str(self.chapter_level))
		if self.REF_DOC:
			params.append('--reference-doc=' + str(SCRIPT_PATH / 'templates' / ('ref' + self.EXT)))
		if self.toc_enabled:
			params.append("--toc")
			params.append('--toc-depth=' + str(self.toc_depth))
		return params

class PdfFileCode(OutFileCode):
	EXT = ".pdf"

class DocxFileCode(OutFileCode):
	EXT = ".docx"
	REF_DOC = True

class OdtFileCode(OutFileCode):
	EXT = ".odt"
	REF_DOC = True

class EpubFileCode(OutFileCode):
	EXT = ".epub"

	def set_conf(self, target_config):
		super().set_conf(target_config)
		self.base_path = target_config['base_path']
		self.fonts = target_config['fonts']

		target_css = target_config['css']
		target_css = [path.replace("fonts/web-", "fonts/epub-") for path in target_css]

		self.css_files = (BASE_STYLES['default']
						+ ([target_config['theme']] if target_config['theme'] else [])
						+ BASE_STYLES['epub']
						+ target_css)
		self.chapter_level = target_config['chapter-level']

	def getPandocOutputOptions(self):
		params = super().getPandocOutputOptions()
		params.append("--epub-chapter-level=" + str(self.chapter_level))
		for font in self.fonts:
			params.append("--epub-embed-font=" + escapePath(EMBED_FONTS_PATH / font / "*f"))
		for path in self.css_files:
			params.append("--css=" + escapePath(path))
		return params

# ----- Code-based

class PureCodeData(CodeData):
	def __init__(self, code=""):
		self.code = code

	def fill_template(self, target_config):
		self.code = template_filler(self.code, target_config)

	def get(self):
		return self.code

	def output(self, filepath=None):
		if not filepath:
			filepath = self.getStorageFile()
		with open(str(filepath), 'w') as f:
			f.write(self.get())
		return filepath

	def load_from(self, path):
		with open(str(path)) as f:
			self.code = f.read()

class MarkdownCode(PureCodeData):
	EXT = ".md"
	REGEX_IMG_HTML = r"<img(.*?)src=['\"](.*?)['\"](.*?)>"
	REGEX_RM_IMG= r"<img.*?>|!\[.*?\]\(.*?\)"
	
	def __init__(self, code=""):
		self.code = code
		self.meta_code = ""

	def extract_config(self, target_config):
		""" Complete the configuration with the document content """
		if target_config['enable-toc'] is None:
			target_config['enable-toc'] = '[TOC]' in self.code

	def set_conf(self, target_config):
		self.fill_template(target_config)
		self.extract_config(target_config)

		metadata = target_config['metadata']
		if metadata:
			metadata = {key : val for key, val in metadata.items() if val is not None}
			self.meta_code = "---\n" + yaml.dump(metadata) + "\n---\n"

		self.remove_images = bool(target_config['remove-images'])


	def clear_for(self, target_format):
		""" Remove parts that are not needed in some documents """
		if target_format in ['odt', 'epub', 'docx', 'html_light', 'txt']:
			self.code = self.code.replace("[TOC]", "")
		if target_format in ['docx']:
			self.purify_code()
		if target_format in ['epub']:
			self.code = post_process_html(self.code)

		if self.remove_images:
			self.code = re.sub(self.REGEX_RM_IMG, '', self.code)

	def get(self):
		return self.meta_code + self.code

	def get_base_code_only(self):
		return self.code

	def purify_code(self):
		""" Change some HTML element into markdown """
		def replace_image(match):
			attributes = match.group(1) + " " + match.group(3)
			return '![]({})'.format(match.group(2))

		self.code = re.sub(self.REGEX_IMG_HTML, replace_image, self.code)

class TxtCode(PureCodeData):
	EXT = ".txt"

class HtmlCode(PureCodeData):
	EXT = ".html"
	def __init__(self, code, title, headers=[]):
		self.code = code
		self.title = title
		self.headers = headers
		self.addStyleList(BASE_STYLES['default'])

	def set_conf(self, target_config):
		if target_config['theme']:
			self.addStyle(target_config['theme'])
		for style in target_config['css']:
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

	def addStyleList(self, paths, base_path=''):
		for p in paths:
			self.addStyle(p, base_path)

	def output(self, filepath=None):
		self.addStyleList(BASE_STYLES['pure_html'])
		filepath = super().output(filepath)
		self.headers.pop()
		return filepath

	def get(self):
		code = HTML_STRUCTURE.format(
			headers="\n".join(self.headers),
			title=self.title,
			body=self.code
		)
		code = code.replace("[SCRIPT_PATH]", str(SCRIPT_PATH.resolve()))
		return code

class HtmlMdCode(MarkdownCode):
	""" Represent a markdown document where most of the markdown is represented in html """
	def __init__(self, html_code, md_code):
		self.code = html_code.code
		self.meta_code = md_code.meta_code

# -------------------- CONVERSION FUNCTIONS --------------------

def md2html(code, target_config):
	code.assertLang(MarkdownCode)
	code.clear_for('html')

	extension_configs = copy(MD_CONFIG)
	extensions = MD_EXTENSIONS
	extension_configs['toc']['toc_depth'] = target_config['toc-level']

	# First we transform the markdown into html
	html = markdown.markdown(code.get_base_code_only(),
		extensions=extensions,
		extension_configs=extension_configs)
	# Then we alter the html code
	html = get_titlepage_template(target_config) + post_process_html(html)

	code = HtmlCode(html, target_config['title'])
	code.set_conf(target_config)

	return code

def html2pdf(code, target_config):
	code.assertLang(HtmlCode)
	code.addStyleList(BASE_STYLES['pdf'])
	pdf_code = PdfFileCode()

	options = copy(PDF_OPTIONS)
	options['title'] = target_config['title']
	dest = pdf_code.getStrPath()
	pdfkit.from_string(code.get(), dest, options=options)

	return pdf_code

def md2htmlmd(md_code, target_config):
	md_code.assertLang(MarkdownCode)
	md_code.clear_for('html_light')
	html = md2html(md_code, target_config)

	return HtmlMdCode(html, md_code)

# ---------- Using pandoc

def pandoc(origin, dest, *add_params):
	origin_out = origin.output()
	dest_out = dest.output()
	add_params = dest.getPandocOutputOptions() + list(add_params)

	r = subprocess.run(['pandoc', origin_out, '-o', dest_out] + add_params)
	if r.returncode:
		raise ParsingError("Error while converting with pandoc : {}".format(r.stderr))

	dest.load_from(dest_out)
	return dest

def any2txt_pandoc(code, target_config):
	# code.assertLang(MarkdownCode)
	if isinstance(code, MarkdownCode):
		code.clear_for('txt')
	txtcode = TxtCode()
	txtcode.set_conf(target_config)

	return pandoc(code, txtcode)

def md2docx_pandoc(code, target_config):
	code.assertLang(MarkdownCode)
	code.clear_for('docx')
	docx = DocxFileCode()
	docx.set_conf(target_config)

	return pandoc(code, docx)

def md2odt_pandoc(code, target_config):
	code.assertLang(MarkdownCode)
	code.clear_for('odt')
	odt = OdtFileCode()
	odt.set_conf(target_config)

	return pandoc(code, odt)

def md2epub_pandoc(code, target_config):
	code.assertLang(MarkdownCode)
	code.clear_for('epub')
	epubDoc = EpubFileCode()
	epubDoc.set_conf(target_config)

	return pandoc(code, epubDoc)

def htmlmd2epub_pandoc(code, target_config):
	code.assertLang(HtmlMdCode)
	epubDoc = EpubFileCode()
	epubDoc.set_conf(target_config)

	return pandoc(code, epubDoc)

# -------------------- EXTERNAL FUNCTIONS --------------------

ALLOWED_FORMATS = {
	'markdown' : [],
	'html' : [md2html],
	'pdf' : [md2html, html2pdf],
	'docx' : [md2docx_pandoc],
	'odt' : [md2odt_pandoc],
	'epub' : [md2epub_pandoc],
	'txt' : [any2txt_pandoc],
	# 'txt' : [any2txt_pandoc],
	# 'epub' : [md2htmlmd, htmlmd2epub_pandoc],

	'word' : 'docx',
	'libreoffice' : 'odt',
	'ebook' : 'epub',
	'md' : 'markdown',
	'web' : 'html',
	'text' : 'txt',
}

def convertBook(code, target_config, out_format, out_dir):
	code = MarkdownCode(code)
	form = out_format
	while isinstance(form, str):
		form = ALLOWED_FORMATS[form]

	code.set_conf(target_config)

	for fct in form:
		code = fct(code, target_config)

	file_name = target_config['name'] + code.EXT
	out_file = out_dir / file_name

	code.output(out_file)
	return out_file