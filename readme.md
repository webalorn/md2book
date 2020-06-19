# md2book

Md2book converts books written with markdown within multiple files into a single, standalone file, and allows exporting to pdf, ebook (epub), docx, odt, markdown or text This projects makes it easy by simply using configuration files written in yaml. You can add your own stylesheets, but the most usefull styles can be directly configured with the configuration file (eg the space between paragraphs, the font and the size of the text, etc...).

Because an example is better than words, [here is a document generated](https://github.com/webalorn/md2book/blob/master/examples/reference/generated/reference.pdf) using md2book.

Md2book is designed to be used by users that are comfortable with the command line interface and want a simple, free and fully customizale tool to manage theirs writings. If you want a more easy-to-use tool, with a GUI, check out [scrivener](https://www.literatureandlatte.com/scrivener/overview) or online alternatives. If you want to use md2book, you will only need a markdown editor, like the great [typora](https://typora.io/) editor.

This project is written in python3, and is a interface to pandoc, wkhtmltopdf and some python packages.
