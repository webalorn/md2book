import string
from copy import deepcopy as copy
from datetime import datetime

from util.exceptions import TemplateError
from util.common import is_int, rand_str

FONT_CSS_TEMPLATE = "\
<style>\
#{id} {{ display : none; }}\
#{id} ~ * {{ {prop} : {val}; }}\
</style>\
<div id='{id}'></div>"
CSS_FONT_PROPERTIES = {
	'font' : 'font-family',
	'color' : 'color',
	'size' : 'font-size',
}

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

			{{<var_name>:get}} Try to guess the type and return the value with a good type
			{{?<var_name>:eval:<expr>}} -> eval the expression, store it if <var_name> is non-empty. Otherwise, return the value
			{{?<var_name>:if:<cond>:<expr>}}, {{<var_name>:if:<cond>:<expr>:else:<expr>}}
			{{<rel_path>:relpath}} -> Path relative to the target directory
			{{<font-name>:font}} -> Change the font used
				{{<font-name>:font}}, {{<font-size>:size}}, {{<color>:color}} [SIZE MUST HAVE A UNIT]
			{{<var-name>?:format:<code>}} -> In <code> : replace newlines by <br/>
		
	"""
	def __init__(self, values, path):
		super().__init__()
		self.values = copy(values)
		self.path = path.resolve()

	def vformat(self, format_string, args, kwargs):
		used_args = set()
		result, _ = self._vformat(format_string, args, kwargs, used_args, 200)
		self.check_unused_args(used_args, args, kwargs)
		return result

	def get_field(self, field_name, args, kwargs):
		if is_int(field_name):
			return '', ''
		field_name = field_name.strip()
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
				raise TemplateError("Variable does not exists: " + repr(val))
		return d

	def get_path_file_content(self, path):
		sys_path = self.path / path
		try:
			content = open(str(sys_path), "r").read()
		except FileNotFoundError:
			raise TemplateError("The path {} doesn't exists".format(str(path)))
		content = self.format(content)
		return content

	def end_expr(self, val, result):
		result = str(result)
		if val:
			self.values[val] = result
			return ''
		return result

	def guess_type_convert(self, val):
		if not isinstance(val, str):
			return str(val)
		v = val.strip()
		if v in ['True', 'true', 'yes']:
			return 'True'
		if v in ['False', 'false', 'no', 'None', 'null']:
			return 'False'
		if v in ['None', 'null', 'none']:
			return 'None'
		if v.startswith("[") and v.endswith("]"):
			return v
		try:
			return str(int(v))
		except:
			pass
		try:
			return str(float(v))
		except:
			pass
		return '"{}"'.format(val)

	def set_font(self, val, prop):
		# if prop == 'font' and val:
		# 	val = '"' + val + '"'
		if not prop in CSS_FONT_PROPERTIES:
			raise TemplateError("The font property '{}' doesn't exists".format(prop))
		prop = CSS_FONT_PROPERTIES[prop]

		val = val or 'inherit'
		block_id = rand_str(15)
		return FONT_CSS_TEMPLATE.format(val=val, id=block_id, prop=prop)

	def split_delimiters(self, params, delims=None, ensure_size=None):
		if not isinstance(delims, list):
			delims = [delims]
		parts = [[]]
		for p in params[::-1]:
			if p in delims:
				if ensure_size is None or len(parts) < ensure_size:
					parts.append([])
			else:
				parts[-1].append(p)
		while len(parts) < ensure_size:
			parts.append([])
		return [':'.join(l) for l in parts]

	def format_html(self, code):
		code = code.replace("\n", "\n<br/>")
		return code

	def format_field(self, val, spec):
		params = [s.strip() for s in spec.split(':')][::-1]
		action = params.pop().lower().strip() if params else ''
		
		if action == 'call':
			return str(self.get_value_of(val)(*params))

		elif action == 'set':
			self.values[val] = params.pop()

		elif action == 'get':
			return str(self.guess_type_convert(self.get_value_of(val)))

		elif action == 'counter':
			if val not in self.values:
				self.values[val] = int(params.pop())-1 if params else 0
			self.values[val] = int(self.values[val]) + 1
			return str(self.values[val])

		elif action == 'include':
			return self.get_path_file_content(val)

		elif action == 'format':
			txt = ':'.join(params)
			return self.end_expr(val, self.format_html(txt))

		elif action in ['font', 'color', 'size']:
			return self.set_font(val, action)

		elif action == 'relpath':
			path = self.get_value_of(val)
			if path is None:
				return ''
			return str(self.path / path)

		elif action == 'eval':
			result = eval(':'.join(params))
			return self.end_expr(val, result)

		elif action == 'if':
			condition = params.pop().strip()
			if_expr, else_expr = self.split_delimiters(params, 'else', 2)

			cond = eval(condition, self.values)
			if isinstance(cond, str):
				cond = cond.strip()
			return self.end_expr(val, if_expr if cond else else_expr)

		elif not spec: # Simple variable
			v = self.get_value_of(val)
			if isinstance(v, list):
				v = ", ".join([str(e) for e in v])
			return str(v)
		
		else:
			raise TemplateError("Invalid template : {{{}}}".format(val+":"+spec))
		return ''

	def format(self, txt):
		txt = txt.replace("{{", "𓀀").replace("}}", "𓀁")
		txt = txt.replace("{", "𓂴").replace("}", "𓂶")
		txt = txt.replace("𓀀", "{").replace("𓀁", "}")
		self.openedFont = None

		txt = super().format(txt)

		# if self.openedFont:
		# 	txt += '\n\n</div>'

		txt = txt.replace("𓂴", "{").replace("𓂶", "}")
		return txt

class TemplateFiller(TemplateEngine):
	def __init__(self, target):
		values = copy(target.conf)

		now = datetime.now()
		values['date'] = now.strftime("%d/%m/%Y")
		values['datetime'] = now.strftime("%d/%m/%Y %H:%M:%S")
		values['time'] = now.strftime("%H:%M:%S")
		values['hour'] = now.strftime("%H:%M")

		sep_string = values['sep']

		values['skip'] = '<div class="pageBreak"></div>'
		values['sep'] = '<div class="sep"><span>' + sep_string + '</span></div>'

		if target.format in ['epub']:
			if '*' in sep_string or '_' in sep_string:
				values['sep'] = '<div class="sep"><span class="sepcontent"></span></div>'

		if target.format in ['docx', 'txt']:
			values['skip'] = '[[SKIP-ITEM]]'
			values['sep'] = '[[SEP-ITEM]]'

		super().__init__(values, target.path.parent)

	def fill(self, code):
		return self.format(code)