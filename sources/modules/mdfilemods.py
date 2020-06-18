import datetime, yaml, re

from .base import BaseModule
from config import *
from templates import get_titlepage_template

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
		return "---\n" + yaml.dump(metadata) + "\n---\n"

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
		code.code = get_titlepage_template(self.target) + code.code

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
		if self.conf['enable'] is None:
			self.conf['enable'] = '[TOC]' in code.code

		if self.format in ['odt', 'epub', 'docx', 'html_light']:
			code.code = code.code.replace("[TOC]", "")

class HtmlBlocksModule(BaseModule):
	RE_BR = r'<br(.*?)>'
	REGEX_COMMENTS = r"<!--.*?-->"

	def alter_html(self, code):
		code.code = re.sub(self.REGEX_COMMENTS, '', code.code)
		code.code = re.sub(self.RE_BR, '<br />', code.code)