import re

from .mdhtml import purify_remove_html

TXT_LARG = 72

def center_txt(text):
	if isinstance(text, list):
		return [center_txt(l) for l in text]
	left = max(0, TXT_LARG - len(text)) // 2
	return ' ' * left + text

def purify_for_txt(code):
	REGEX_HTML_LINK = r'<a.*?href=([\'"])(.*?)\1.*?>(.*?)</.*?a.*?>'
	REGEX_HTML_ELEM = r'</?[a-zA-Z].*?>'

	def convert_link(match):
		return '[{text}]({url})'.format(text=match.group(3), url=match.group(2))

	code = purify_remove_html(code)
	code = re.sub(REGEX_HTML_LINK, convert_link, code)
	code = re.sub(REGEX_HTML_ELEM, '', code)

	return code

def post_process_txt(code, target):
	sep = center_txt(target['sep'])

	code = code.replace('\\[', '[')
	code = code.replace('\\]', ']')
	code = code.replace('\\]', ']')

	REGEX_IMAGE = r'!\[(.*?)\]\((.*?)\)'
	REGEX_LINK = r'\[(.*?)\]\((.*?)\)'
	# REGEX_MARKDOWN_EL = r'(\*|\*\*|_|__|`|```|~~|~|\^)(\S.*?)\1'
	REGEX_MARKDOWN_EL_2 = r'(\*\*|__|``|~~)(\S.*?)\1'
	REGEX_MARKDOWN_EL = r'(\*|_|`|~|\^)(\S.*?)\1'

	def convert_image(match):
		text = match.group(1).strip()
		if text:
			text =' (' + text + ')'
		return '[Image{}: {}] '.format(text, match.group(2))
	def convert_link(match):
		return '{} ({})'.format(match.group(1), match.group(2))
	def convert_md_el(match):
		return match.group(2)

	code = re.sub(REGEX_IMAGE, convert_image, code)
	code = re.sub(REGEX_LINK, convert_link, code)
	code = re.sub(REGEX_MARKDOWN_EL_2, convert_md_el, code)
	code = re.sub(REGEX_MARKDOWN_EL, convert_md_el, code)

	code = code.replace('[[SEP-ITEM]]', sep)

	return code