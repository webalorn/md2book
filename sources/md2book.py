import importlib
from shutil import which
from util.exceptions import BaseError, ModuleImportError, MissingDependencyError

dependencies = ['pandoc', 'wkhtmltopdf']
python_modules = {
	'pyyaml' : 'yaml',
	'markdown' : 'markdown',
	'pdfkit' : 'pdfkit',
	'python-docx' : 'docx',
}

def check_dependency(name):
	if which(name) is None:
		raise MissingDependencyError(name=name)

def check_module(name, module):
	if not importlib.util.find_spec(module):
		raise ModuleImportError(name=name)

if __name__ == '__main__':
	error = None

	try:
		for name in dependencies:
			check_dependency(name)
		for name, module in python_modules.items():
			check_module(name, module)

		from main import main
		main()
	except BaseError as e:
		print(e)