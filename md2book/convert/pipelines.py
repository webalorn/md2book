import pdfkit, markdown, subprocess
from copy import deepcopy

from md2book.config import *
from md2book.util.exceptions import ParsingError
from md2book.formats.mddocx import post_process_docx
from md2book.formats.mdtxt import post_process_txt
from md2book.formats.mdebook import preparse_ebook_markdown
from .forms_text import *
from .forms_stored import *

# -------------------- META-PIPELINES -------------------- #

class ConvertPipeline:
	BASE_LANG = MarkdownCode
	def __init__(self, code):
		self.code = code

	def alter_code(self, target):
		self.code.clear_for(target.format)
		for mod in target.modules:
			mod.alter_md(self.code)

	def execute(self, target):
		if self.BASE_LANG:
			self.code.assertLang(self.BASE_LANG)
		self.code.set_conf(target)
		self.alter_code(target)

		self.prepare_config(target)
		self.convert_steps(target)

		return self.code

	# Functions to overrride

	def prepare_config(self, target):
		pass

	def convert_steps(self, target):
		pass

# -------------------- PYTHON PIPELINES -------------------- #

class PipeMd(ConvertPipeline):
	pass

class PipeMd2Html(ConvertPipeline):
	def prepare_config(self, target):
		self.md_extensions_conf = deepcopy(MD_CONFIG)
		self.md_extensions = get_markdown_default_extensions()
		self.md_extensions_conf['toc']['toc_depth'] = target['toc']['level']

	def md2html(self, target):
		# First we transform the markdown into html
		html = markdown.markdown(self.code.get_base_code_only(),
			extensions=self.md_extensions,
			extension_configs=self.md_extensions_conf)

		self.code = HtmlCode(html, target['title'])

		for mod in target.modules:
			mod.alter_html(self.code)
		self.code.set_conf(target)

	def convert_steps(self, target):
		self.md2html(target)

class PipeMd2Html2Pdf(PipeMd2Html):
	def prepare_config(self, target):
		super().prepare_config(target)

		self.pdfkit_options = deepcopy(PDF_OPTIONS)
		self.pdfkit_options['title'] = target['title']

	def html2pdf(self, target):
		self.code.assertLang(HtmlCode)
		pdf_code = PdfFileCode()

		pdfkit.from_string(
			self.code.get(),
			pdf_code.getStrPath(),
			options=self.pdfkit_options
		)
		self.code = pdf_code

	def convert_steps(self, target):
		super().convert_steps(target)
		self.html2pdf(target)

# -------------------- PANDOC PIPELINES -------------------- #

class PandocPipeline(ConvertPipeline):
	DEST_FORMAT = MarkdownCode

	def pandoc(self, dest, *add_params):
		origin_out = self.code.output()
		dest_out = dest.output()
		add_params = dest.getPandocOutputOptions() + list(add_params)

		r = subprocess.run(['pandoc', origin_out, '-o', dest_out] + add_params)
		if r.returncode:
			raise ParsingError("Error while converting with pandoc : {}".format(r.stderr))

		dest.load_from(dest_out)
		self.code = dest

	def convert_steps(self, target):
		dest = self.DEST_FORMAT()
		dest.set_conf(target)
		self.pandoc(dest)

class PipeAny2txtPandoc(PandocPipeline):
	BASE_LANG = None
	DEST_FORMAT = TxtCode

class PipeMd2DocxPandoc(PandocPipeline):
	DEST_FORMAT = DocxFileCode

	def convert_steps(self, target):
		super().convert_steps(target)
		post_process_docx(self.code, target)

class PipeMd2OdtPandoc(PandocPipeline):
	DEST_FORMAT = OdtFileCode

class PipeMd2EpubPandoc(PandocPipeline):
	DEST_FORMAT = EpubFileCode

	def alter_code(self, target):
		super().alter_code(target)
		# For markdown not supported by pandoc
		self.code.code = preparse_ebook_markdown(self.code.code)

		# The markdown can contains some HTML that needs to be altered
		for mod in target.modules:
			mod.alter_html(self.code)

class PipeMd2txtPandoc(PandocPipeline):
	DEST_FORMAT = TxtCode

	def convert_steps(self, target):
		super().convert_steps(target)
		self.code.code = post_process_txt(self.code.code, target)

class PipeMd2htmlPandoc(PandocPipeline):
	DEST_FORMAT = HtmlCode

	def md2html(self, target):
		# First we transform the markdown into html
		html = markdown.markdown(self.code.get_base_code_only(),
			extensions=self.md_extensions,
			extension_configs=self.md_extensions_conf)

		self.code = HtmlCode(html, target['title'])

		for mod in target.modules:
			mod.alter_html(self.code)
		self.code.set_conf(target)

	def convert_steps(self, target):
		dest = self.DEST_FORMAT('', target['title'])
		dest.set_conf(target)
		self.pandoc(dest)

		for mod in target.modules:
			mod.alter_html(self.code)
		self.code.set_conf(target)