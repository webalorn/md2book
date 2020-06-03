from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import SimpleTagPattern
from markdown.extensions import Extension

from .imports.tasklist import TasklistExtension

from pathlib import Path
import re

# -------------------- EXTEND MARKDOWN SYNTAX --------------------

	
class MarkdownExtended(Extension):
	REGEX_DEL = r'(~~)(.*?)~~'
	REGEX_MARK = r'(==)(.*?)=='
	REGEX_SUP = r'(\^)(.*?)\^'
	REGEX_SUB = r'(~)(.*?)~'
	REGEX_SKIP = r'\[SKIP\]'

	def extendMarkdown(self, md):
		del_tag = SimpleTagPattern(self.REGEX_DEL, 'del')
		md.inlinePatterns.register(del_tag, 'del', 15)

		mark_tag = SimpleTagPattern(self.REGEX_MARK, 'mark')
		md.inlinePatterns.register(mark_tag, 'mark', 15)

		sup_tag = SimpleTagPattern(self.REGEX_SUP, 'sup')
		md.inlinePatterns.register(sup_tag, 'sup', 10)

		sub_tag = SimpleTagPattern(self.REGEX_SUB, 'sub')
		md.inlinePatterns.register(sub_tag, 'sub', 10)

# -------------------- PRE-PROCESS MARKDOWN --------------------

REGEX_IMG_MD = r'!\[(.*?)\]\((.*?)\)'
REGEX_IMG_HTML1 = r'<img(.*?)src="(.*?)"'
REGEX_IMG_HTML2 = r"<img(.*?)src='(.*?)'"

def pre_parse_md(content, dir_path):
	# Change relative paths to absolute
	def complete_path(path):
		if not Path(path).is_absolute() and (dir_path / path).exists():
			return str(dir_path / path)
		return path
	def replace_md_images(match):
		return "![{}]({})".format(match.group(1), complete_path(match.group(2)))
	def replace_html_images1(match):
		return '<img{}src="{}"'.format(match.group(1), complete_path(match.group(2)))
	def replace_html_images2(match):
		return '<img{}src="{}"'.format(match.group(1), complete_path(match.group(2)))

	content = re.sub(REGEX_IMG_MD, replace_md_images, content)
	content = re.sub(REGEX_IMG_HTML1, replace_html_images1, content)
	content = re.sub(REGEX_IMG_HTML2, replace_html_images2, content)

	return content

# -------------------- POST PROCESS THE HTML --------------------

POST_RE_IMG_HTML = r'<img(.*?)/?>'
POST_RE_EMPTY_ALT = r'alt=([\'"])\1'
POST_RE_BR = r'<br(.*?)>'

def post_process_html(html):
	def replace_html_images(match):
		code = match.group(1)
		if not " alt=" in code:
			code = code + ' alt="Image" '
		return '<img{}/>'.format(code)

	html = re.sub(POST_RE_IMG_HTML, replace_html_images, html)
	html = re.sub(POST_RE_EMPTY_ALT, 'alt="Image"', html)
	html = re.sub(POST_RE_BR, '<br />', html)
	return html