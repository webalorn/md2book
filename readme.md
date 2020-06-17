# md2book

The md2book projet aims to convert books written with markdown within multiple files into a single standalone file, and to allow exporting in markdown, pdf, docx, odt or epub... This projects makes it easy by simply using configuration files written in yaml. You can add your own stylesheets, but the most usefull styles can be directly configured with the configuration file (eg the space between paragraphs, the font and the size of the text, etc...)

Md2book is designed to be used by users that are comfortable with the command line interface and want a simple, free and fully customizale tool to manage theirs writings. If you want a more easy-to-use tool, with a GUI, check out [scrivener](https://www.literatureandlatte.com/scrivener/overview) or fr online alternatives. If you want to use md2book, you will only need a markdown editor, like the great [typora](https://typora.io/) editor.

This project is written in python3, and is a interface to pandoc, wkhtmltopdf and some python packages.

<!-- TODO : [TOC] -->

## Installation

To get started, download the repository, for example with `git clone https://github.com/webalorn/md2book`. Under linux / MacOS, if you want to use this tool, it is recommended to add an alias in your `.bashrc`, `.zshrc` or any other configuration file. In this readme, I will use `md2book` instead of `python3 /..path../md2book.py`.

```
alias md2book = "python3 /path/where/you/downloaded/md2book.py"
```

md2book requires the following python packages : `pyyaml`, `markdown`, `pdfkit`. You must also install `wkhtmltopdf` and `pandoc`.

### Mac OS

```
python3 -m pip install --upgrade pyyaml markdown pdfkit

brew install Caskroom/cask/wkhtmltopdf
brew install pandoc
```

## Quick start

Create an empty directory and create a file name `my_super_book.md`, and put [this content](https://raw.githubusercontent.com/webalorn/md2book/master/examples/quick_start/my_super_book.md) in the file. Then use:
```bash
md2book my_super_book.md -t html --open
```

(You might have to replace `md2book` by `python3 path/to/md2book/md2book.py`)

A configuration file has been created, named `my_super_book.book.yml`, and the preview of you book is opened in your browser. Your first book has been compiled, congratulations ! The html file is located in a subfolder named `generated`.

You can simply rename `my_super_book.book.yml` into `book.yml`. Now, create another file named 'chapter2.md', and put [this content](https://raw.githubusercontent.com/webalorn/md2book/master/examples/quick_start/chapter2.md) in it. Replace the content of `book.yml` by :

```yaml
targets:
  main:
    chapters:
      - my_super_book.md
      - chapter2.md
    name : my_super_book
    title : "My super book"
    font-size : 14px
    theme : github
    default-font: opensans
```

Then, use ```md2book -t html --open```. You will have a book containing both `my_super_book.md` and `chapter2.md`. You can add as many files as you want. You can also compile into another format, by changing the target (`-t`).

```
md2book -t pdf # To generate in pdf. Add --open to open it automaticly
md2book -t docx # Microsoft office word document
md2book -t ebook # epub document
```

This documents contains a reference of most of the styles and templates you can use in a document, and is the rendered version is available here. For more informations, read the next sections.

## Usage notes

- The markdown and html documents generated are not always portable, because they reference the fonts and images that are external files on your system.
- Generating pdf takes some time, this is the expected behavior, because they are generated using webkit from the html document.

## Supported formats

The following formats are supported, and are given with the format name(s) you can use in the configuration files or as targets.

- PDF (default format) : `pdf`
- HTML : `html`, `web`
- Markdown : `md`, `markdown`
- Microsoft Office Word documents : `docx`, `word`
- LibreOffice document : `odt`, `libreoffice`
- EBook with epub3 : `ebook`, `epub`
- Text file : `txt`, `text`

## Command line reference

The command line interface is made to be very easy to use. All parameters are optionals. When you launch the script in a directory, it will compile any file ending in `book.yml` (files matching `*book.yml`) that are located in the directory or the subdirectories. Here are the options you can use :

Giving a path to the command (`md2book some/path/`) will compile all the files in the given directory (or the file if you use `md2book some/path/book.yml`), instead of the files in the current directory.

`-h`, `--help` : Show the help message and exit

`-t [TARGET]`, `--target [TARGET]` : select the target for the compilation. `main` is the default target. You can use any target defined in the `book.yml` document, and any format supported by md2book (See supported formats). If the target is a valid format but is not defined in the configuration file, it will the `main` target, where the format is replaced by the one you gave. For exemple, if you use `md2book -t ebook`, it will compile the `main` target, but into an ebook instead of pdf or any other format.

`-o [OUTPUT]`, `--output [OUTPUT]` : Change the output directory of md2book, and create the files in this directory.
 
`--open` : Automaticly open the document created by md2book with the default software of your system. Usefull to have a quick preview of the documents or of the changes.

### Compiling directly a markdown file

If the path given to the command is a markdown file, a simple configuration file with the same name, ending in ".book.yml" will be created and used the first time. You can simply change the settings in this file and add new settings.

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
compile_in : generated # Subdirectory where the generated files will be placed

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
    titlepage : yes # Add a first page in html / pdf including the title and the author(s)
    title-image : /some/path/to/an/image
    fonts : ['allura', ...] # Additional fonts to be included if you want to use them in custom css
    default-font : 'opensans', # Font used as default font (See the fonts section for all base fonts)
    font-size : "12px" # You can set the font size with "??px", "??pt", "??em"...
    between-chapters : "\n\n" # Text inserted between each chapter
    css : # Add css files
      - "custom1.css"
      - "custom2.css"
    theme : 'github' # The theme set the majority of the styles. Write 'no' for no theme. See the "themes" section.
    enable-toc : null # See below
    toc-level : 2 # Depth of titles included in the table of contents
    cover : relative/path/to/the/image/cover
    chapter-level : 1 # 1, 2, or 3 : level of titles where to split into chapters
    center-blocks : yes # Center the images and tables (yes / no)
    indent : 2em # remove to disable ; You can use ??px, ??em, etc...
    paragraph-spacing : 2px # Control the space between paragraphs. You can set ??px, ??em, or yes to leave it as it's default value, and no to remove any space between paragraphs

    remove-images : no # Remove all images in the content of the document
    sep : "* * *" # Text used as separator when using {{sep}}

    metadata : # Used in ebooks and to create cover pages
      author : [ "name of author 1", "name of author 2", ...] # if not set, it takes the value of the "by" parameter
      keywords : ["keyword1", "keyword2", ...]
      abstract : "Content of the abstract"
      date : current # current will be replaced by the current date. Otherwise you can use null (no date), or a date in the format DD-MM-YYYY, MM-YYYY, or YYYY.
      lang : "en" # If null, it will use the system default lang
      subject : "...."
      description : "...."
      rights : "This may be a copyright or something more fun"
      thanks : "Thnks to this person, etc..."

  # Examples of other targets :
  pdf: # Because it has the name of a format, the format will be automaticly pdf
    format : pdf # You can remove this, it is added automaticly. If you set another format, it won't be used.
    css:
      - style_for_pdf.css
  another_target:
    format : ebook # Here, it is usefull
    toc-level : 3
  target2:
    inherit: # It will include all settings of the targets. 'main' is always inherited.
      - main # You can remove this, it is added automaticly
      - pdf
      - another_target
```

- `enable-toc` : A table of content will be inserted in the documents if `[TOC]` is found in the file. This field overwrite this behavior if set to `yes` or `no`.
- `toc-level` can be 0 (disable TOC), 1, 2, 3, 4, 5 or 6. If it is lower, more titles are included int the table of cotent.
- `chapter-level` is used in ebooks to split the book into chapters. The chapters are NOT split

### Default settings

The file `generated_default_settings.yml`, located at the root of the project, contains all default settings, and is generated the first time you use the `md2book` command. Do not change this file, it will be overwride every time you use md2book !

Instead, you can overwride these settings by writting your own configuration into `default_settings.yml`. It will replace the default file. For examples, this kind of settings can be usefull :

```yaml
default_target:
  format: ebook
  by: "Your name"
```

You can always remove this file, it will be regenerated.

## Fonts

You can use the fonts that are installed on your system (like `Merriweather`), or one of the following fonts. The name between brackets is the name of the police you must use in the configuration file. It is case-sensitive. If you want to disbale the default font, simply write `no` in the `default-font` field.

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

If you want to disable the theme, set the theme to `no`. Otherwise, simply set `theme` to the name of the theme you want to use. 

- `minimal`
- `github` (default theme)
- `splendor` (Try with `default-font: no` for better results)
- `retro` (Try with `default-font: no` for better results)
  - Has some problems due to the dark background - see "Known issues"
- `air` (Try with `default-font: opensans` for better results)
- `modest` (Try with `default-font: no` for better results)

## Markdown support

The markdown syntax supported is :
- The basic markdown syntax
- The additional simple syntax used by [typora](https://typora.io/) :
  - `==hihighlighted text==`
  - `~~striked~~`
  - `inline code`
  - `sub~script~` and `super^script^`
  - (Underlined with HTML : `<u>underlined</u>`)
- Tables
- HTML elements
- Simple line break are kept (transformed into the `<br />` HTML element)

## Templates

You can use templates into your documents. The templates elements are surrounded by `{{` and `}}`, and replaced during the compilation. It includes a system to create and assign variables, create counters, etc...

### Simple usage

#### Predefined variables

Simply write the `code` into your markdown file, and they will be replaced by the specified value.

- `{{skip}}` : inserting this code will force a page break in pdf and ebooks
- `{{sep}}` : create a simple separation in the text
  - The default separator is `*   *   *`, but here are other great symbols you can use, by setting `sep` in the configuration file : `✧ ✦ ♢ ♦︎ ☓ ・ ● ■ ✶ ✷ ✸ ✽`
- Date and time
  - `{{date}}` : insert current date in the format "DAY/MONTH/YEAR"
  - `{{datetime}}` : format "DAY/MONTH/YEAR HOUR:MINUTES:SECONDS"
  - `{{time}}` : format "HOUR:MINUTES:SECONDS"
  - `{{hour}}` : format "HOUR:MINUTES"

#### Using your configuration file

You can insert any variable defined into your configuration file. For example, `{{title}}` will insert the title of the book, and `{{metadata.abstract}}` will insert the absctract.

You can also add a field `variables` in your `default_settings.yml` or your `book.yml` files :

```yaml
default_target:
  ...
  variables:
    variable1 : 42
    another_variable : "The value of the variable"
```

Here are some usage examples :

  - `{{title}}` (titre), `{{by}}` (name of the author), `{{subtitle}}`
  - `{{metadata.abstract}}`, `{{metadata.keywords}}`
  - `{{variables.variable1}}` (with the previous configuration, it should print 42)

#### Simple use cases

- Auto numbering chapter : put `{{chapter:counter}}` and it will increase each time it is used. For example, `c{{chapter:counter}} c{{chapter:counter}} c{{chapter:counter}}` will print `c1 c2 c3`

### Complete reference

emplate engine : replace templates formated as `{{...}}`
- "?" indicates an optional parameter
- <...> indicates an arbitrary value <=int>, <=str>, <=function> if there is a type

Syntax :
- {{<var_name>}} -> Print the variable
- {{<var_name>:set:<value>}} -> set the variable "var_name" with "value"
- {{<var_name>:counter:?start-value}} -> Print the counter value and add 1. If is doesnt exists, create a variable containing 1, or "start-value"
- {{<file_path>:include}} -> Include the given file

## Known issues

- LaTeX is not currently supported
- Tables width in docx documents is too small (width of 1 character in each column)
- odt documents have strange grey areas and are not well formated
- Problems with background color if the background is not white in pdf and ebook. It is recomended to use a white / transparent background for better support by ebook readers.