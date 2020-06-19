from markdown.treeprocessors import Treeprocessor
from markdown.inlinepatterns import SimpleTagPattern
from markdown.extensions import Extension

from imports.tasklist import TasklistExtension

from pathlib import Path
import re

# -------------------- EXTEND MARKDOWN SYNTAX -------------------- #

class MarkdownExtended(Extension):
	REGEX_DEL = r'(~~)(.*?)~~'
	REGEX_MARK = r'(==)(.*?)=='
	REGEX_SUP = r'(\^)(.*?)\^'
	REGEX_SUB = r'(~)(.*?)~'
	# REGEX_SKIP = r'\[SKIP\]'

	def extendMarkdown(self, md):
		del_tag = SimpleTagPattern(self.REGEX_DEL, 'del')
		md.inlinePatterns.register(del_tag, 'del', 15)

		mark_tag = SimpleTagPattern(self.REGEX_MARK, 'mark')
		md.inlinePatterns.register(mark_tag, 'mark', 15)

		sup_tag = SimpleTagPattern(self.REGEX_SUP, 'sup')
		md.inlinePatterns.register(sup_tag, 'sup', 10)

		sub_tag = SimpleTagPattern(self.REGEX_SUB, 'sub')
		md.inlinePatterns.register(sub_tag, 'sub', 10)

# -------------------- PRE-PROCESS MARKDOWN -------------------- #

REGEX_IMG_MD = r'!\[(.*?)\]\((.*?)\)'
REGEX_IMG_HTML1 = r'<img(.*?)src="(.*?)"'
REGEX_IMG_HTML2 = r"<img(.*?)src='(.*?)'"

def md_make_paths_absolute(content, dir_path):
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

# -------------------- MAKE MARDOWN-HTML CONVERTABLE -------------------- #

def purify_remove_html(code):
	REGEX_IMG_HTML = r"<img(.*?)src=['\"](.*?)['\"](.*?)>"
	REGEX_U = r"==(.*?)=="
	REGEX_COMMENTS = r"<!--([\s\S]*?)-->"
	REGEX_STYLE = r"<style.*?>([\s\S]*?)</style.*?>"

	def replace_html_image(match):
		attributes = match.group(1) + " " + match.group(3)
		return '![]({})'.format(match.group(2))

	def replace_u(match):
		return match.group(1)

	code = re.sub(REGEX_IMG_HTML, replace_html_image, code)
	code = re.sub(REGEX_U, replace_u, code)
	code = re.sub(REGEX_COMMENTS, '', code)
	code = re.sub(REGEX_STYLE, '', code)
	return code