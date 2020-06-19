import importlib, traceback
from shutil import which

from md2book.util.exceptions import BaseError, ModuleImportError, MissingDependencyError

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

def main():
	try:
		for name in dependencies:
			check_dependency(name)
		for name, module in python_modules.items():
			check_module(name, module)

		# Import here to load modules AFTER checkin dependencies
		from md2book.main import main
		main()
	except BaseError as e:
		print(e)
	except Exception as e:
		traceback.print_exc()
		print("\u001b[31m[ERROR] An unexpected exception occured in md2book. If you can't solve the problem, please open an issue on https://github.com/webalorn/md2book/issues\nIf possible, copy the error message, the configuration file and the markdown code that created the problem.\u001b[0m")

if __name__ == '__main__':
	main()