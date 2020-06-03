import string
from copy import deepcopy as copy
from datetime import datetime

class TemplateVar():
	pass

class TemplateEngine(string.Formatter):
	"""
		Template engine : replace things like {...}
			- "?" indicates an optional parameter
			- <...> indicates an arbitrary value <=int>, <=str>, <=function> if there is a type

		Syntax :
			{{<var_name>}} -> python default behavior, prints the variable
			{{<fct=function>:call:?param1:?...}} -> call the function 'fct'
			{{<var_name>:set:<value>}} -> set the variable "var_name" with "value"
			{{<var_name>:counter:?start-value}} -> Print the counter value and add 1.
					If is doesnt exists, create a variable containing 1, or "start-value"
		
	"""
	def __init__(self, values):
		super().__init__()
		self.values = copy(values)

	def get_field(self, field_name, args, kwargs):
		return field_name, field_name

	def format_field(self, val, spec):
		real_val, real_spec = val, spec

		params = [s.strip() for s in spec.split(':')][::-1]
		if isinstance(val, TemplateVar):
			val = params.pop()
			real_val, real_spec = val, ":".join(params[::-1])
		action = params.pop() if params else ''
		
		if action == 'call':
			return self.values[val](*params)
		elif action == 'set':
			self.values[val] = params.pop()
		elif action == 'counter':
			if val not in self.values:
				self.values[val] = int(params.pop())-1 if params else 0
			self.values[val] = int(self.values[val]) + 1
			return str(self.values[val])
		else:
			return super().format_field(self.values[real_val], real_spec)
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
	values['SKIP'] = '<div class="pageBreak"></div>'

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