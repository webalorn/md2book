class BaseError(Exception):
	COLORS = {
		'red' : '\u001b[31m',
		'magenta' : '\u001b[35m',
		'default' : '\u001b[0m',
		'white' : '\u001b[97m',
		'green' : '\u001b[92m',
	}
	TEMPLATE = "{red}[ERROR]"

	def __init__(self, **variables):
		self.variables = {key : str(v) for key, v in variables.items()}
		super().__init__(self.TEMPLATE)

	def format(self, **variables):
		variables = {**variables, **self.COLORS}
		template = self.TEMPLATE + "{default}"
		return template.format(**variables)

	def __str__(self):
		return self.format(**self.variables)


# -------------------- CUSTOM EXCEPTIONS -------------------- #

class ModuleImportError(BaseError):
	TEMPLATE = "{red}[ERROR] The following python module is not installed : {name}"

class MissingDependencyError(BaseError):
	TEMPLATE = "{red}[ERROR] The following command is required but has not been found : {name}"

class TemplateError(BaseError):
	TEMPLATE = "{red}[ERROR IN TEMPLATE] {white}{error}"
	def __init__(self, error):
		super().__init__(error=error)

# Located errors

class LocatedError(BaseError):
	def set_location(self, path):
		if not self.variables.get('where', ''):
			self.variables['where'] = str(path)

class ConfigError(LocatedError):
	TEMPLATE = "{red}[ERROR] {magenta}{where} {white}: {error}"

	def __init__(self, error, where=''):
		super().__init__(where=where, error=error)

class ParsingError(LocatedError):
	TEMPLATE =  "{red}[ERROR] {magenta}{where} {white} {error}"
	def __init__(self, error):
		super().__init__(error=error, where='')
	
# -------------------- WARNING -------------------- #

class Warning(BaseError):
	def show(self):
		print(str(self))

class WarningNoBookFound(BaseError):
	TEMPLATE = "{red}[WARNING] No book found under: {white}{path}"

	def __init__(self, path):
		super().__init__(path=str(path))