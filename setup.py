import setuptools, os
from pathlib import Path
import importlib.util

cur_dir = Path(__file__).parent
FILES_BLACK_LIST = ['data/default_settings.yml']

try:
	with open("readme.md", "r") as readme_file:
		readme_content = readme_file.read()
except:
	readme_content = '[error] readme.md unavailable'

def find_data_files(root_path, parent_dir):
	parent_dir = (cur_dir / parent_dir).resolve()
	files = []
	def find_sub_data(path):
		if path.is_dir():
			for p in path.iterdir():
				find_sub_data(p)
		elif not path.name.startswith('.'):
			files.append(path.resolve().relative_to(parent_dir))
	find_sub_data(cur_dir / root_path)

	files = [str(f) for f in files]
	files = [f for f in files if f not in FILES_BLACK_LIST]
	return files

def import_module_file(name, path):
	path = str(cur_dir / path)
	spec = importlib.util.spec_from_file_location(name, path)
	mod = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(mod)
	return mod

md2book_module = import_module_file("m2b", "md2book/__init__.py")
md2book_conf = import_module_file("conf", "md2book/config.py")

setuptools.setup(
	name=md2book_conf.M2B_NAME,
	version=md2book_module.__version__,
	author=md2book_module.__author__,
	author_email=md2book_conf.M2B_EMAIL,
	description="Convert markdown files to beautiful books using a simple configuration file",
	long_description=readme_content,
	long_description_content_type="text/markdown",
	url="https://github.com/webalorn/md2book",
	packages=setuptools.find_packages(),
	entry_points={
		'console_scripts': [
			'md2book=md2book.start:main',
		],
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	project_urls={
		"Documentation": "https://github.com/webalorn/md2book/wiki",
		"Source": "https://github.com/webalorn/md2book",
	},
	include_package_data=True,
 	package_data={'md2book': find_data_files('md2book/data', 'md2book')},
	install_requires=['pyyaml>=5.2', 'markdown>=3.2', 'pdfkit>=0.6.1', 'python-docx>-0.8.10'],
	python_requires='>=3',
)