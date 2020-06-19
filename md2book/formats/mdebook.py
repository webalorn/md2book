import re

def preparse_ebook_markdown(code):
	RREGEX_MARK = r'(==)(.*?)=='

	def replace_mark(match):
		return '<mark>{}</mark>'.format(match.group(1))

	code = re.sub(RREGEX_MARK, replace_mark, code)
	return code