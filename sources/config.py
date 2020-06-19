from pathlib import Path
from formats.mdhtml import MarkdownExtended, TasklistExtension
# -------------------- PATHS -------------------- #

TMP_DIRS = []
SCRIPT_PATH = Path(__file__).parent.parent.resolve()

DEFAULT_SETTINGS = SCRIPT_PATH / "default_settings.yml"
GENERATED_SETTINGS_FILE = SCRIPT_PATH / "generated_default_settings.yml"
EMBED_FONTS_PATH = SCRIPT_PATH / 'fonts'

# -------------------- MAIN -------------------- #

BOOK_FILE_NAMES = "*book.yml"
DEFAULT_GEN_DIR = "generated"

BASE_STYLES = {
	"default" : ["default.css"],
	"html" : ["html.css"],
	"pdf" : ["pdf.css"],
	"epub" : ["epub.css"],
}
BASE_STYLES = {key : [str(SCRIPT_PATH / "styles" / p) for p in val] for key, val in BASE_STYLES.items()}

DEFAULT_TARGET = {
	'inherit' : [],
	'chapters' : [],
	'variables' : {},

	'name' : 'book', # Name of the file created
	'title' : None, # Displayed name or title. Default is the name
	'subtitle' : None, # Displayed name or title. Default is the name
	'by' : None,

	'format' : 'pdf',

	'theme' : 'github', # Set 'no' for no theme.
	'css' : [],
	'js' : [],
	'between-chapters' : "\n\n",
	'chapter-level' : 1, # or 2, 3 : level where to split into chapters

	# Modules : 
	'sep' : "✶   ✶   ✶",
	'titlepage' : {
		'enable' : True,
		'image' : None,
	},
	'images' : {
		'remove' : False,
		'cover' : None,
	},
	'font': {
		'default' : 'opensans',
		'include' : [], # Additional fonts
		'size' : None,
	},
	'toc' : {
		'enable' : None, # If not set, enabled if [TOC] is found in the document
		'level' : 3,
	},
	'style' : {
		'align' : 'justify',
		'center-blocks' : True,
		'indent' : False,
		'paragraph-spacing' : True,
	},
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
	'theme' : 'github',

	'font' : {
		'default' : 'opensans',
		'size' : None,

	},
}

# -------------------- TEMPLATES -------------------- #

HTML_TEMPLATE = SCRIPT_PATH / 'templates' / 'structure.html'
TITLE_PAGE_TEMPLATE = SCRIPT_PATH / 'templates' / 'titlepage.html'
FONT_FAMILY_CSS = """
@font-face {{
  font-family: "{font}";
  font-style: {style};
  font-weight: {weight};
  font-display: swap;
  src: url("{src}");
}}"""

AVAILABLE_SCRIPTS = {
	'jquery' : "https://code.jquery.com/jquery-3.5.1.min.js",
}

# -------------------- CONVERTING -------------------- #

BASE_FORMATS = ['markdown', 'html', 'pdf', 'docx', 'odt', 'epub', 'txt']
FORMAT_ALIASES = {
	'word' : 'docx',
	'libreoffice' : 'odt',
	'ebook' : 'epub',
	'md' : 'markdown',
	'web' : 'html',
	'text' : 'txt',
}
ALLOWED_FORMATS = list(BASE_FORMATS) + list(FORMAT_ALIASES)

MD_EXTENSIONS = [
	'extra', 'nl2br', 'sane_lists', 'smarty', 'toc',
	MarkdownExtended(), TasklistExtension()
]
MD_CONFIG = {
	'toc' : {
		'toc_depth' : 6,
	}
}

PDF_OPTIONS = { # https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
	'margin-top': '0.75in',
	'margin-right': '0.7in',
	'margin-bottom': '0.7in',
	'margin-left': '0.75in',
	'encoding': "UTF-8",
	'quiet': '',
}