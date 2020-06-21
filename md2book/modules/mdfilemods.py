import datetime, yaml, re
import urllib, hashlib

from .base import BaseModule
from md2book.config import *
from md2book.templates import TemplateFiller
from md2book.formats.mdhtml import extract_toc
from md2book.util.exceptions import SimpleWarning
from md2book.util.common import download_url

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
			toc_html = extract_toc(code.code, self.conf['level'])
			code.code = code.code.replace('[TOC]', toc_html)

		if self.format in ['odt', 'epub', 'docx', 'html_light']:
			if self.conf['enable'] is None:
				self.conf['enable'] = '[TOC]' in code.code
			code.code = code.code.replace('[TOC]', '')

class HtmlBlocksModule(BaseModule):
	RE_BR = r'<br(.*?)>'
	REGEX_COMMENTS = r"<!--([\s\S]*?)-->"

	def alter_html(self, code):
		code.code = re.sub(self.REGEX_COMMENTS, '', code.code)
		code.code = re.sub(self.RE_BR, '<br />', code.code)

class LatexModule(BaseModule):
	NAME = 'latex'
	TEX_BLOCKS = r'\$\$\$([\s\S]*?)\$\$\$'
	TEX_INLINE = r'\$(.*?)\$'
	# XML_PROP_RE = r'[\s\S]*?<svg.*?width="(.*?)".*?height="(.*?)".*?role="img"[\s\S]*?'
	# IMAGE_TEMPLATE = '![]({url})'
	IMAGE_TEMPLATE = '![]({url})'

	def __init__(self, conf, target):
		super().__init__(conf, target)
		self.enabled = bool(self.conf)
		self.download_status = None

		if self.enabled:
			self.download_dir = target.compile_dir / 'latex'
			self.download_dir.mkdir(parents=True, exist_ok=True)

	def get_latex_image_code(self, path):
		with open(str(path)) as f:
			xml = f.readlines()
			return xml[2]
		# groups = re.match(self.XML_PROP_RE, xml)
		# width, height = groups.group(1), groups.group(2)
		# return self.IMAGE_TEMPLATE.format(url=str(path))

	def get_inserter(self, argname):
		def match_latex(match):
			if self.download_status == 'offline':
				return ''

			texcode = match.group(1).strip()
			args = urllib.parse.urlencode({argname : texcode})
			url = 'https://math.now.sh?' + args
			filename = hashlib.md5(url.encode('utf-8')).hexdigest()

			path = self.download_dir / (filename + '.svg')
			if not path.resolve().is_file():
				if self.download_status is None:
					print("Download LaTeX images from math.now.sh...")
				result_path = download_url(url, path=str(path))
				if result_path is None:
					self.download_status = 'offline'
					return ''
				else:
					self.download_status = 'ok'

			# path = path.relative_to(self.target.compile_dir)
			path = path.resolve()
			return self.get_latex_image_code(path)

		return match_latex

	def try_access_api(self):
		try:
			urllib.request.urlopen('https://math.now.sh/home')
			return True
		except:
			return False

	def alter_md(self, code):
		if self.enabled:
			code.code = re.sub(self.TEX_BLOCKS, self.get_inserter('from'), code.code)
			code.code = re.sub(self.TEX_INLINE, self.get_inserter('inline'), code.code)

			if self.download_status == 'offline':
				SimpleWarning('The math.now.sh API is not accessible, LaTeX may not be rendered').show()
			elif self.download_status == 'ok':
				print("LaTeX download complete")