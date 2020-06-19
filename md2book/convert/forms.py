import shutil

from md2book.util.common import rand_str
from md2book.templates import TemplateFiller
from md2book.config import *

# -------------------- CODE CLASSES -------------------- #

class CodeData:
	EXT = "txt"
	REF_DOC = False

	def assertLang(self, *langsCls):
		for lang in langsCls:
			if isinstance(self, lang):
				return True
		raise exception("Code {} is not in {}".format(self.lang, str(langs)))

	def getStorageFile(self):
		filepath = TMP_DIRS[0] / (rand_str(10) + '.' + self.EXT)
		filepath.parent.mkdir(parents=True, exist_ok=True)
		return filepath

	def getStrPath(self):
		return str(self.getStorageFile())

	def getPandocOutputOptions(self):
		return []

	def set_conf(self, target):
		self.target = target

	def load_from(self, path):
		raise Exception("Not implemented")

	def output(self, dest=None):
		raise Exception("Not implemented")

# ----- Pure code

class PureCodeData(CodeData):
	def __init__(self, code=""):
		self.code = code

	def fill_template(self, target):
		self.code = TemplateFiller(target).fill(self.code)

	def get(self):
		return self.code

	def output(self, dest=None):
		if not dest:
			dest = self.getStorageFile()
		with open(str(dest), 'w') as f:
			f.write(self.get())
		return dest

	def load_from(self, path):
		with open(str(path)) as f:
			self.code = f.read()

# ----- File-based

class OutFileCode(CodeData):
	def __init__(self):
		self.filepath = self.getStorageFile()

	def get(self):
		return self.filepath

	def getStrPath(self):
		return str(self.filepath.resolve())

	def output(self, dest=None):
		if dest:
			shutil.copy(str(self.filepath), str(dest))
			return dest
		return self.filepath

	def load_from(self, path):
		self.filepath = path

	def getPandocOutputOptions(self):
		params = super().getPandocOutputOptions()
		if self.REF_DOC:
			params.append('--reference-doc=' + str(DATA_PATH / 'templates' / ('ref.' + self.EXT)))
		for mod in self.target.modules:
			params.extend(mod.pandoc_options(self.EXT))

		return params