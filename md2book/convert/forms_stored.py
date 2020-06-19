from .forms import OutFileCode
from md2book.util.common import escapePath

class PdfFileCode(OutFileCode):
	EXT = "pdf"

class DocxFileCode(OutFileCode):
	EXT = "docx"
	REF_DOC = True

class OdtFileCode(OutFileCode):
	EXT = "odt"
	REF_DOC = True

class EpubFileCode(OutFileCode):
	EXT = "epub"