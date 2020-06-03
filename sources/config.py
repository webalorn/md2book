from pathlib import Path
from .mdhtml import MarkdownExtended, TasklistExtension
# -------------------- PATHS --------------------

TMP_DIRS = []
SCRIPT_PATH = Path(__file__).parent.parent.resolve()
DEFAULT_SETTINGS = SCRIPT_PATH / "default_settings.yml"
EMBED_FONTS_REL = {
	'opensans' : 'opensans/OpenSans-*.ttf',
}
EMBED_FONTS_PATH = SCRIPT_PATH / 'fonts'
EMBED_FONTS = {name : str(SCRIPT_PATH / 'fonts' / path) for name, path in EMBED_FONTS_REL.items()}

# -------------------- MAIN --------------------

BOOK_FILE_NAMES = "*book.yml"
DEFAULT_GEN_DIR = "generated"

BASE_STYLES = {
	"default" : ["default.css"],
	"pure_html" : ["pure_html.css"],
	"pdf" : ["pdf.css"],
	"epub" : ["epub.css"],
}
BASE_STYLES = {key : [str(SCRIPT_PATH / "styles" / p) for p in val] for key, val in BASE_STYLES.items()}

FONT_CSS = 'body { font-family: "FONT-HERE","Clear Sans","Helvetica Neue",Helvetica,Arial,sans-serif;}'

DEFAULT_TARGET = {
	'inherit' : [],
	'chapters' : [],

	'name' : 'book', # Name of the file created
	'title' : None, # Displayed name or title. Default is the name
	'subtitle' : None, # Disaplayed name or title. Default is the name
	'by' : "Unknown",

	'format' : 'pdf',
	'titlepage' : True,
	'title-image' : None,
	'fonts' : [], # Additional fonts
	'default-font' : 'opensans', # Font used as default font
	'font-size' : None, # or ??px, ??em, ??pt, ...
	'between-chapters' : "\n\n",
	'css' : [],
	'theme' : 'github', # Set 'no' for no theme. Available : github
	'enable-toc' : None, # If not set, enabled if [TOC] is found in the document
	'toc-level' : 3,
	'cover' : None,
	'chapter-level' : 1, # or 2, 3 : level where to split into chapters
	'center-blocks' : True,
	'indent' : False,
	'paragraph-spacing' : True,

	'remove-images' : False,

	'metadata' : {
		# 'title' : [], # Title and subtitle from the config. You can add short, collection, edition, extended
		# 'subtitle' : "",
		'author' : None, # [ author1, author2, ...]
		'keywords' : None, # [...]
		'abstract' : None, # Text
		'date' : None, # current will be replaced by the current date. Otherwise, None, or YYYY-MM-DD.
		'lang' : None,
		'subject' : None, # [...]
		'description' : None, # Or text
		'rights' : None,
		'thanks' : None,
	}
}

SIMPLE_TARGET = { # Field in a generated configuration file
	'name' : 'book',
	'title' : None,
	'subtitle' : None,
	'by' : None,

	'default-font' : 'opensans',
	'font-size' : None,
	'theme' : 'github',
}

# -------------------- CONVERTING --------------------

MD_EXTENSIONS = [
	'extra', 'nl2br', 'sane_lists', 'smarty', 'toc',
	MarkdownExtended(), TasklistExtension()
]
MD_CONFIG = {
	'toc' : {
		'toc_depth' : 6,
	}
}

HTML_STRUCTURE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<!-- <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,600;0,700;0,800;1,300;1,400;1,600;1,700;1,800&display=swap" rel="stylesheet"> -->
<title>{title}</title>
{headers}
</head>
<body>
{body}
</body>
</html>
"""

PDF_OPTIONS = { # https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
	'margin-top': '0.75in',
	'margin-right': '0.7in',
	'margin-bottom': '0.7in',
	'margin-left': '0.75in',
	'encoding': "UTF-8",
	'quiet': '',
}