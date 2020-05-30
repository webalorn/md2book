# md2book

The md2book projet aims to convert books written with markdown within multiple files into a single standalone file, and to allow exporting in markdown, pdf, docx, odt or epub (and in the future, maybe some other types). This projects makes it easy by simply using configuration files written in yaml.

This project is written in python3, and is a interface to pandoc, wkhtmltopdf and some python packages.

[TOC]

## Installation

To get started, download the repository, for example with `git clone [URL]`. Undex linux / MacOS, if you want to use this tool, it is recommended to add an alias in your `.bashrc`, `.zshrc` or any other configuration file. In this readme, I will use `md2book` instead of `python3 /.../compile.py`.

```
alias md2book = "python3 /path/where/you/downloaded/compile.py"
```

md2book requires the following python packages : `pyyaml`, `markdown`, `pdfkit`. You must also install `wkhtmltopdf` and `pandoc`.

### Mac OS

```
python3 -m pip install --upgrade pyyaml markdown pdfkit

brew install Caskroom/cask/wkhtmltopdf
brew install pandoc
```

<!-- ## Quick start -->

## Usage notes

- The markdown and html documents are not portable, because they reference the fonts and images.

## Supported formats

The following formats are supported, and are given with the format name(s) you can use in the configuration files or as targets.

- PDF (default format) : `pdf`
- HTML : `html`, `web`
- Markdown : `md`, `markdown`
- Microsoft Office Word documents : `docx`, `word`
- LibreOffice document : `odt`, `libreoffice`
- EBook with epub3 : `ebook`, `epub`

## Command line reference

The command line interface is made to be very easy to use. All parameters are optionals. When you launch the script in a directory, it will compile any file ending in `book.yml` (files matching `*book.yml`) that are located in the directory or the subdirectories. Here are the options you can use :

Giving a path to the command (`md2book some/path/`) will compile all the files in the given directory (or the file if you use `md2book some/path/book.yml`), instead of the files in the current directory.

`-h`, `--help` : Show the help message and exit

`-t [TARGET]`, `--target [TARGET]` : select the target for the compilation. `main` is the default target. You can use any target defined in the `book.yml` document, and any format supported by md2book (See supported formats). If the target is a valid format but is not defined in the configuration file, it will the `main` target, where the format is replaced by the one you gave. For exemple, if you use `md2book -t ebook`, it will compile the `main` target, but into an ebook instead of pdf or any other format.

`-o [OUTPUT]`, `--output [OUTPUT]` : Change the output directory of md2book, and create the files in this directory.
 
`--open` : Automaticly open the document created by md2book with the default software of your system. Usefull to have a quick preview of the documents or of the changes.
	

## Configuration reference

To create a new book, simple create a document `book.yml`. You can also use any name that end in `book.yml`. For instance, you can have a configuration file named `my_super_book.yml`. The content of the file must be written in yaml. If you are not familiar with this language, don't worry ! It is made to be easealy readable by any human. In md2book, you only need the most basic syntax. If you want a more complete reference, [there is plenty of tutorials online](https://learnxinyminutes.com/docs/yaml/).

All paths in the configuration files must be relative to the book.yml file itself.

### Minial configuration

As md2book is meant to be easy to use, the default configuration file is very short : Simply add the files you want to include in your book in the "chapters" section.

```yaml
targets:
  main:
    chapters:
      - chapters/chapter1.md
      - chapters/chapter2.md
```

To have a good-looking book, you might want to add some informations:

```yaml
targets:
  main:
    name : "name_of_the_file"
    by : "Your name"
    format : pdf # Can be docx, ebook, etc...
    title : "The title of your book"
    subtitle: "You can even add a subtitle"
    cover : "relative/path/to/image"
    css : []
    default-font: sansmono
    font-size : 12px
    chapters:
      - chapter1.md
      - chapter2.md
      - And so on...
```

### Configuration reference

All fields can be removed and ignored. You can split your documents into as many files as you want, the chapters displayed do not necessarily match the "chapter" files.

```yaml
targets:
  main: # This target MUST be present
    chapters :
      - chapter1.md
      - "other chapters..."
    name : 'name_of_the_book' # Name of the file created
    title : "The super title of my book !" # The title displayed
    subtitle : "a subtitle" # You can remove this field
    by : 'Your name'

    format : 'pdf' # Can be any format listed in "Supported formats"
    fonts' : ['allura', ...] # Additional fonts to be included if you want to use them in custom css
    default-font : 'opensans', # Font used as default font (See the fonts section for all base fonts)
    font-size : "12px" # You can set the font size with "??px", "??pt", "??em"...
    between_chapters : "\n\n" # Text inserted between each chapter
    css : # Add css files
      - "custom1.css"
      - "custom2.css"
    theme : 'github' # The theme set the majority of the styles. Write 'no' for no theme. See the "themes" section.
    enable-toc : null # See below
    toc-level : 6
    cover : relative/path/to/the/image/cover
    chapter-level : 1 # 1, 2, or 3 : level of titles where to split into chapters

    metadata : # Used in ebooks and to create cover pages
      author : [ "name of author 1", "name of author 2", ...] # if not set, it takes the value of the "by" parameter
      keywords : ["keyword1", "keyword2", ...]
      abstract : "Content of the abstract"
      date : current # current will be replaced by the current date. Otherwise you can use null (no date), or a date in the format YYYY-MM-DD, YYYY-MM, or YYYY.
      lang : "en" # If null, it will use the system default lang
      subject : "...."
      description : "...."
      rights : "This may be a copyright or something more fun"
```

- `enable-toc` : A table of content will be inserted in the documents if `[TOC]` is found in the file. This field overwrite this behavior if set to `yes` or `no`.
- `toc-level` can be 0 (disable TOC), 1, 2, 3, 4, 5 or 6. If it is lower, more titles are included int the table of cotent.
- `chapter-level` is used in ebooks to split the book into chapters. The chapters are NOT split 

### Default configuration file

```yaml
targets:
  main:
    inherit : []
    chapters : []

    name : 'book'
    title : null
    subtitle : null
    by : 'Unknown'

    format : 'pdf'
    fonts' : []
    default-font : 'opensans',
    font-size : null
    between_chapters : "\n\n"
    css : []
    theme : 'github'
    enable-toc : null
    toc-level : 6
    cover : null
    chapter-level : 1

    metadata :
      author : null
      keywords : null
      abstract : null
      date : current
      lang : null
      subject : null
      description : nul
      rights : null
```

## Fonts

You can use the fonts that are on all systems, or one of the following fonts. The name between brackets is the name of the police you must use in the configuration file. It is case-sensitive.

![](https://imgs3.fontbrain.com/imgs/62/9a/55a7e793da068dc580d184cc0e31/fsl-720-30-333333@2x.png)

Opens Sans [`opensans`], sans serif

![](https://imgs1.fontbrain.com/imgs/2c/00/68c933abb9208794c1a27db997ad/fsl-720-30-333333@2x.png)

EB Garamond [`garamond`]

![](https://imgs2.fontbrain.com/imgs/2f/8e/fe1daf177284441a0e53072875e4/fsl-720-30-333333@2x.png)

Libre Caslon [`caslon`]

![](https://imgs4.fontbrain.com/imgs/3c/a5/06812a54b579c0cee97888915956/fsl-720-30-333333@2x.png)

Playfair [`playfair`]

![](https://imgs2.fontbrain.com/imgs/c7/fd/b3ed6f5d1b76c7defaae70bda2b3/fsl-720-30-333333@2x.png)

Allura [`allura`] (italic and bold are not supported)

![](https://imgs2.fontbrain.com/imgs/f7/b5/e589f88206b4bd5cb1408c5362e6/fsl-720-30-333333@2x.png)

Metropolis [`metropolis`]

### Custom fonts

To add a font, you must choose a `fontname`. You can add the font by putting the files in the `scripts/fonts/fontname` directory, and by creating a css file `scripts/styles/fonts/fontname.css`. For the css file, follow the example of `opensans.css`. The font must be in `.ttf` or `.otf`.

## Themes

Currently, only the `github` theme is available. If you want to disable the theme, set the theme to `no`.

## Known issues

- LaTeX is not currently supported
- Tables width in docx documents is too small (width of 1 character in each column)
- odt documents have strange grey areas