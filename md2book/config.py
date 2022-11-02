from pathlib import Path
import md2book

# -------------------- PATHS -------------------- #

TMP_DIRS = []
SCRIPT_PATH = Path(__file__).parent.resolve()
DATA_PATH = (Path(__file__).parent / 'data').resolve()

GENERATED_SETTINGS_FILE = DATA_PATH / 'generated_default_settings.yml'
EMBED_FONTS_PATH = DATA_PATH / 'fonts'

# In user directory

CONFIG_PATH = (Path.home() / '.md2book').resolve()
DEFAULT_SETTINGS = CONFIG_PATH / 'settings.yml'

try:
	CONFIG_PATH.mkdir(parents=True, exist_ok=True)
	if not DEFAULT_SETTINGS.exists():
		DEFAULT_SETTINGS.touch()
except:
	pass

# -------------------- MAIN -------------------- #

M2B_NAME = 'md2book'
M2B_EMAIL = 'webalorn@gmail.com'
M2B_SHORT_DESCRIPTION = 'md2book (version {}) : Compile markdown book with a simple \
command and a configuration file. - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  \
Documentation available at https://github.com/webalorn/md2book/wiki - - - - -  \
Repport bugs on https://github.com/webalorn/md2book/issues -- - - - - - - - -  \
'.format(md2book.__version__)
M2B_EPILOG = 'Settings : {}\
'.format(str(DEFAULT_SETTINGS))


# -------------------- TARGETS -------------------- #

BOOK_FILE_NAMES = "*book.yml"
DEFAULT_GEN_DIR = "generated"

BASE_STYLES = {
	"default" : ["default.css"],
	"html" : ["html.css"],
	"pdf" : ["pdf.css"],
	"epub" : ["epub.css"],
}
BASE_STYLES = {key : [str(DATA_PATH / "styles" / p) for p in val] for key, val in BASE_STYLES.items()}

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
	'between-chapters' : '\n\n',
	'chapter-level' : 1, # or 2, 3 : level where to split into chapters

	# Modules : 
	'sep' : '✶   ✶   ✶',
	'latex' : {
		'enable': True,
		'aliases_file': None,
		'default_aliases': True,
	},
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
		'enable' : True, # Generate a TOC at the begening of the file
		'level' : 3,
		'style' : 'base',
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

HTML_TEMPLATE = DATA_PATH / 'templates' / 'structure.html'
TITLE_PAGE_TEMPLATE = DATA_PATH / 'templates' / 'titlepage.html'
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

def get_markdown_default_extensions():
	# Import is done here to keep minimal depencies for this file
	from md2book.formats.mdhtml import MarkdownExtended, TasklistExtension
	return [
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
	'enable-local-file-access': '',
  'no-outline': None,
}