import string
from copy import deepcopy as copy
from datetime import datetime

class TemplateError(Exception):
	def __init__(self, error):
		self.error = error
		super().__init__(self.error)

	def __str__(self):
		return "\u001b[31m[ERROR IN TEMPLATE] \u001b[0m {}".format(str(self.error))

class TemplateEngine(string.Formatter):
	"""
		Template engine : replace things like {{...}}
			- "?" indicates an optional parameter
			- <...> indicates an arbitrary value <=int>, <=str>, <=function> if there is a type

		Syntax :
			{{<var_name>}} -> python default behavior, prints the variable
			{{<fct=function>:call:?param1:?...}} -> call the function 'fct'
			{{<var_name>:set:<value>}} -> set the variable "var_name" with "value"
			{{<var_name>:counter:?start-value}} -> Print the counter value and add 1.
					If is doesnt exists, create a variable containing 1, or "start-value"
			{{<file_path>:include} -> Include the file located at file_path
		
	"""
	def __init__(self, values):
		super().__init__()
		self.values = copy(values)

	def get_field(self, field_name, args, kwargs):
		return field_name, field_name

	def get_value_of(self, val):
		d = self.values
		val_tab = val.lower().split('.')[::-1]
		while val_tab:
			if 'variables' in d and val_tab[-1] in d['variables']:
				d = d['variables'][val_tab.pop()]
			elif val_tab[-1] in d:
				d = d[val_tab.pop()]
			else:
				raise TemplateError("Variable does not exists: " + str(val))
		return d

	def get_path_file_content(self, path):
		sys_path = self.values['base_path'].parent / path
		try:
			content = open(str(sys_path), "r").read()
		except FileNotFoundError:
			raise TemplateError("The path {} doesn't exists".format(str(path)))
		content = self.format(content)
		return content

	def format_field(self, val, spec):
		params = [s.strip() for s in spec.split(':')][::-1]
		action = params.pop().lower() if params else ''
		
		if action == 'call':
			return self.get_value_of(val)(*params)
		elif action == 'set':
			self.values[val] = params.pop()
		elif action == 'counter':
			if val not in self.values:
				self.values[val] = int(params.pop())-1 if params else 0
			self.values[val] = int(self.values[val]) + 1
			return str(self.values[val])
		elif action == 'include':
			return self.get_path_file_content(val)
		elif not spec:
			v = self.get_value_of(val)
			if isinstance(v, list):
				v = ", ".join([str(e) for e in v])
			return str(v)
		else:
			raise TemplateError("Template invalide")
		return ''

	def format(self, txt):
		txt = txt.replace("{{", "𓀀").replace("}}", "𓀁")
		txt = txt.replace("{", "𓂴").replace("}", "𓂶")
		txt = txt.replace("𓀀", "{").replace("𓀁", "}")
		txt = super().format(txt)
		txt = txt.replace("𓂴", "{").replace("𓂶", "}")
		return txt

def template_filler(code, values):
	values = copy(values)

	now = datetime.now()
	values['date'] = now.strftime("%d/%m/%Y")
	values['datetime'] = now.strftime("%d/%m/%Y %H:%M:%S")
	values['time'] = now.strftime("%H:%M:%S")
	values['hour'] = now.strftime("%H:%M")

	values['skip'] = '<div class="pageBreak"></div>'
	values['sep'] = '<div class="sep">' + values['sep'] + '</div>'

	return TemplateEngine(values).format(code)

# -------------------- GENERATED TEMPLATES --------------------

def get_titlepage_template(target):
	if not target['titlepage']:
		return ''
	meta = target['metadata']

	titlepage = [
		'<span style="font-family: ' + target['default-font'] + '"></span>', # Workaround for issue in wkhtmltopdf
		'<div id="titlePage">'
		'<div id="bookTitle">' + str(target['title']) + '</div>'
	]
	if target['subtitle']:
		titlepage.append('<div id="bookSubtitle">' + str(target['subtitle']) + '</div>')

	if meta['author']:
		author = meta['author']
		if isinstance(author, list):
			author = ", ".join(author)
		titlepage.append('<div id="bookAuthor">' + str(author) + '</div>')

	if target['title-image']:
		path = target['base_path'].parent / target["title-image"]
		titlepage.append('<img id="bookTitleImage" src="' + str(path.resolve()) + '" alt="Title image" />')

	if meta['thanks']:
		titlepage.append('<div id="bookThanks">' + str(meta['thanks']) + '</div>')

	if meta['abstract']:
		titlepage.append('<div id="bookAbstract">' + str(meta['abstract']) + '</div>')

	titlepage.append("</div>")

	return "\n".join(titlepage)