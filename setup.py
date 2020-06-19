import setuptools
from pathlib import Path

with open("readme.md", "r") as readme_file:
	readme_content = readme_file.read()

def find_data_files(root_path, parent_dir):
	parent_dir = Path(parent_dir).resolve()
	files = []
	def find_sub_data(path):
		if path.is_dir():
			for p in path.iterdir():
				find_sub_data(p)
		else:
			files.append(path.resolve().relative_to(parent_dir))
	find_sub_data(Path(root_path))

	return [str(f) for f in files]

setuptools.setup(
	name="md2book",
	version="0.1.6",
	author="webalorn (Théophane Vallaeys)",
	author_email="webalorn@gmail.com",
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
	install_requires=['pyyaml', 'markdown', 'pdfkit', 'python-docx'],
	python_requires='>=3',
)