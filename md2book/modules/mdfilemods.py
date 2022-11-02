import datetime, yaml, re
import urllib, hashlib

from .base import BaseModule
from md2book.config import *
from md2book.templates import TemplateFiller
from md2book.formats.mdhtml import extract_toc
from md2book.util.exceptions import SimpleWarning, ConfigError
from md2book.util.common import download_url, load_yaml_file

class MetadataModule(BaseModule):
	NAME = 'metadata'
	def __init__(self, conf, target):
		super().__init__(conf, target)
		meta = self.conf

		meta['title'] = target.conf['title'].strip()

		if target.conf['subtitle']:
			meta['subtitle'] = target.conf['subtitle'].strip()

		if meta.get('author', None) is None and target.conf['by']:
			meta['author'] = target.conf['by']

		if meta.get('date', None) == 'current':
			meta['date'] = datetime.now().strftime("%d/%m/%Y")

	def get_yaml_intro(self):
		metadata = {key : val for key, val in self.conf.items() if val is not None}
		content = "---\n" + yaml.dump(metadata) + "\n---\n"
		content = content.replace("_", "\\_")
		return content

class ImagesModule(BaseModule):
	NAME = 'images'

	REGEX_RM_IMG = r"<img.*?>|!\[.*?\]\(.*?\)"
	RE_IMG_HTML = r'<img(.*?)/?>'
	RE_EMPTY_ALT = r'alt=([\'"])\1'

	def __init__(self, conf, target):
		super().__init__(conf, target)

		conf['remove'] = bool(conf['remove'])

		if conf['cover']:
			conf['cover'] = str((target.path.parent / conf['cover']).resolve())
			target.conf['metadata']['cover-image'] = conf['cover']

	def replace_html_images(self, match):
		code = match.group(1)
		if not " alt=" in code:
			code = code + ' alt="Image" '
		return '<img{}/>'.format(code)

	def alter_md(self, code):
		if self.conf['remove']:
			code.code = re.sub(self.REGEX_RM_IMG, '', code.code)

	def alter_html(self, code):
		code.code = re.sub(self.RE_IMG_HTML, self.replace_html_images, code.code)
		code.code = re.sub(self.RE_EMPTY_ALT, 'alt="Image"', code.code)

class TitlePageModule(BaseModule):
	NAME = 'titlepage'

	def alter_html(self, code):
		if self.format != 'epub':
			with open(TITLE_PAGE_TEMPLATE, 'r') as f:
				titlepage = f.read()
			titlepage = TemplateFiller(self.target).fill(titlepage)
			code.code = titlepage + code.code

class TocModule(BaseModule):
	NAME = 'toc'

	def pandoc_options(self, dest_format):
		options = super().pandoc_options(dest_format)
		chapter_level = 1
		if self.conf['enable']:
			chapter_level = min(3, max(1, int(self.conf['enable'])))
			options.append("--toc")
			options.append('--toc-depth=' + str(self.conf['level']))

		if dest_format == 'epub':
			options.append("--epub-chapter-level=" + str(chapter_level))
		return options

	def alter_md(self, code):
		if self.format in ['html', 'pdf', 'markdown', 'txt'] and self.conf['enable']:
			code.code = '[TOC]\n\n' + code.code

		if self.format in ['epub'] and '[TOC]' in code.code:
			toc_html = extract_toc(code.code, self.conf['level'], self.format)
			code.code = code.code.replace('[TOC]', toc_html)

		if self.format in ['odt', 'epub', 'docx', 'html_light']:
			if self.conf['enable'] is None:
				self.conf['enable'] = '[TOC]' in code.code
			code.code = code.code.replace('[TOC]', '')

	def get_stylesheets(self):
		styles = []
		style = self.conf['style'].strip()
		if style:
			styles.append(DATA_PATH / 'styles/toc/base.css')
			if style != 'base':
				styles.append(DATA_PATH / 'styles/toc/{}.css'.format(style))
		return styles

class HtmlBlocksModule(BaseModule):
	RE_BR = r'<br(.*?)>'
	REGEX_COMMENTS = r"<!--([\s\S]*?)-->"
	RE_SVG_IMAGE = r'(<img .*?src="(.*?\.svg)".*?>)'

	def __init__(self, conf, target):
		super().__init__(conf, target)
		self.alter_svg = target.format in ['html', 'pdf']

	def alter_html(self, code):
		code.code = re.sub(self.REGEX_COMMENTS, '', code.code)
		code.code = re.sub(self.RE_BR, '<br />', code.code)
		if self.alter_svg:
			code.code = re.sub(self.RE_SVG_IMAGE, self.svg_inserter, code.code)

	def svg_inserter(self, match):
		path = match.group(2)
		if path.startswith('http://') or path.startswith('https://'):
			return match.group(1)
		with open(str(path)) as f:
			xml = f.readlines()[2:]
		xml = ''.join(xml)
		return xml


class LatexModule(BaseModule):
	NAME = 'latex'
	TEX_BLOCKS = r'\$\$([\s\S]*?)\$\$'
	TEX_INLINE = r'\$(.*?)\$'
	SVG_SIZE= r'width="(.*?)" height="(.*?)"'
	# XML_PROP_RE = r'[\s\S]*?<svg.*?width="(.*?)".*?height="(.*?)".*?role="img"[\s\S]*?'
	# IMAGE_TEMPLATE = '![]({url})'
	IMAGE_INLINE = '<img src="{}" style="width:{}; height: {};" />'
	IMAGE_BLOCK = '<p class="centerblock"><img src="{}" style="width:{}; height: {};" /></p>'

	def __init__(self, conf, target):
		super().__init__(conf, target)
		self.enabled = self.conf['enable']
		self.download_status = None
		self.equations_names = set()
		self.relative_path = target.format in ['md']

		if self.enabled:
			self.download_dir = target.compile_dir / 'latex'
			self.download_dir.mkdir(parents=True, exist_ok=True)

	def get_latex_image_code(self, path, inline=True):
		with open(str(path)) as f:
			xml = f.readlines()
		xml = ''.join(xml)
		sizes = re.search(self.SVG_SIZE, xml)

		template = self.IMAGE_INLINE if inline else self.IMAGE_BLOCK
		path = ('latex/' + path.name) if self.relative_path else str(path)
		return template.format(path, sizes.group(1), sizes.group(2))

	def clean_cache(self):
		for file in self.download_dir.iterdir():
			if not file.name in self.equations_names:
				file.unlink()
	
	def load_aliases(self, filepath):
		aliases = load_yaml_file(filepath)
		if type(aliases) is not dict:
			raise ConfigError("LaTeX alias file should be a dict", where=filepath)
		for key, val in aliases.items():
			if type(key) is not str or type(val) is not str:
				raise ConfigError("LaTeX aliases should be strings", where=filepath)
		
		return list(aliases.items())

	def preprocess_text(self, texcode):
		a = texcode
		aliases = []
		if self.conf['aliases_file']:
			aliases.extend(self.load_aliases(self.conf['aliases_file']))
		if self.conf['default_aliases']:
			aliases.extend(self.load_aliases(DATA_PATH / 'default_aliases.yml'))
		
		for alias_from, alias_to in aliases:
			alias_from = alias_from.replace('\\', '\\\\')
			alias_to = alias_to.replace('\\', '\\\\')
			texcode = re.sub(alias_from + r'(?=([^a-zA-Z\d]|$))', alias_to, texcode)
		return texcode

	def get_inserter(self, argname):
		def match_latex(match):
			if self.download_status == 'offline':
				return ''

			texcode = match.group(1).strip()
			texcode = self.preprocess_text(texcode)
			args = urllib.parse.urlencode({'color' : 'black', argname : texcode})
			url = 'https://math.vercel.app?' + args
			filename = hashlib.md5(url.encode('utf-8')).hexdigest()

			path = self.download_dir / (filename + '.svg')
			if not path.resolve().is_file():
				if self.download_status is None:
					print("Download LaTeX images from math.vercel.app...")
				result_path = download_url(url, path=str(path))
				if result_path is None:
					self.download_status = 'offline'
					return ''
				else:
					self.download_status = 'ok'

			# path = path.relative_to(self.target.compile_dir)
			path = path.resolve()
			self.equations_names.add(path.name)
			return self.get_latex_image_code(path, inline=(argname == 'inline'))

		return match_latex

	def alter_md(self, code):
		if self.enabled:
			code.code = re.sub(self.TEX_BLOCKS, self.get_inserter('from'), code.code)
			code.code = re.sub(self.TEX_INLINE, self.get_inserter('inline'), code.code)

			if self.download_status == 'offline':
				SimpleWarning('The math.vercel.app API is not accessible, LaTeX may not be rendered').show()
			elif self.download_status == 'ok':
				print("LaTeX download complete")
			if self.download_status != 'offline':
				self.clean_cache()