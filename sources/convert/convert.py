from config import *
from .pipelines import *

# -------------------- EXTERNAL FUNCTIONS -------------------- #

FORMATS_PIPELINE = {
	'markdown' : PipeMd,
	'html' : PipeMd2Html,
	'pdf' : PipeMd2Html2Pdf,
	'docx' : PipeMd2DocxPandoc,
	'odt' : PipeMd2OdtPandoc,
	'epub' : PipeMd2EpubPandoc,
	'txt' : PipeAny2txtPandoc,
}

def convertBook(code, target):
	code = MarkdownCode(code)
	pipeline = FORMATS_PIPELINE[target.format]
	code = pipeline(code).execute(target)

	file_name = target['name'] + '.' + code.EXT
	out_file = target.compile_dir / file_name
	code.output(out_file)

	return out_file