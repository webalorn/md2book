# Introduction

This document contains various styles and formating options. The links may not be clickable on the github pdf viewer, so you can download the pdf. You can look at the source code [in the repository](https://raw.githubusercontent.com/webalorn/md2book/master/examples/reference/book.md), and the rendered document [here in pdf](https://github.com/webalorn/md2book/blob/master/examples/reference/generated/reference.pdf). Any valid html can be inserted into the markdown code, and it will be rendered. The configuration file used here is :

```yaml
{%book.yml:include%}
```

Some other formats are supported :

- [Html document](https://github.com/webalorn/md2book/blob/master/examples/reference/generated/reference.html)
- [epub (ebook)](https://github.com/webalorn/md2book/blob/master/examples/reference/generated/reference.epub)
- [docx document](https://github.com/webalorn/md2book/blob/master/examples/reference/generated/reference.docx)
- And others...

# Markdown - Title level 1

## Markdown - Title level 2

### Markdown - Title level 3

#### Markdown - Title level 4

##### Markdown - Title level 5

###### Markdown - Title level 6

## Simple markdown

The table of contents is generated by the `[TOC]` below. This is a paragraph

This is another paragraph.
Simple lines breaks can be used, and two line breaks to create another paragraph. The next paragraph is separated by an horizontal line, using `---`.

---

You can use [markdown links](https://www.google.com) or <a href="https://www.google.com">html links</a>. Transform an url or an e-mail into a link using `<...>` : <https://google.com>, <contact@example.org>. You can use all sort of formating : *italic*, **bold**, <u>underlined (with html)</u>, ~~striked~~, `inline-code`, ==highlighted==, super^super^, inf~inf~.

- This is a dotted list
- With multiple
- Items
	- And
	- One sublist
		- Two sublists

1. This is a numbered list
2. With multiple
3. Items
	1. And
	2. One sublist
		1. Two sublists

- [ ] This is a task list
- [x] Task 2 (done)

> This is a blockquote
> with multiple lines
> 
> And paragraphs !
>> And even a nested blockquote

```
This is a multiline
code block
```

And definitions : the HTML specification is maintained by the W3C. Awesome HTML !

*[HTML]: Hyper Text Markup Language

![Picture of a cat](https://upload.wikimedia.org/wikipedia/commons/b/bb/Kittyply_edit1.jpg)

## Tables

First Header  | Second Header
:------------ | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

| header 1 | header 2 | header 3 |
| -------- | -------- | -------- |
| three    | columns  |          |
|          |          | .        |
|          |          | …        |

## LaTeX math equations

You can insert $inline-latex$ inside the text : $3+4=5=\sum_{i=0}^4 \frac{1}{2}\times 2$. For bigger equations, math blocks can be used :

$$
	\frac{1}{\Gamma(s)}\int_{0}^{\infty}\frac{u^{s-1}}{e^{u}-1}\mathrm{d}u
$$

### LaTeX aliases

This is a default alias: $\O$. Default aliases can be disabled. But this is using a custom alias set in the `aliases-latex.yml` file: $\then$.

# Templates

A template system is used by `md2boook`, and allow inserting variables, and special html elements. The variables names must be writen like this : `{` `{` `variable_name` `}` `}`.

- **Date** : {%date%}
- **Datetime** : {%datetime%}
- **Time** : {%time%}
- **Hour** : {%hour%}

## Counters

We can use counters to count occurences, for instance to auto-number chapters. You can replace `chapter` within the template by anything else.

- Chapter {%chapter:counter%}
- Chapter {%chapter:counter%}
- Chapter {%chapter:counter%}
- Chapter {%chapter:counter%}

## Variables

You can defines a variable using `{` `%` `var_name:set:value` `%` `}`. In this example, we will use is to store a name with `{` `%` `name1:set:The Great Warrior Kron` `%` `}`. {%name1:set:The Great Warrior Kron%}

It can then be used multiple times : **{%name1%}** is great, and {%name1%} is a warrior. And this paragraph doesn't even used the name of *{%name1%}*.

All the variables defined in the configuration file can be used in the document : This document used the font {%font.default%}, with the theme {%theme%}, and is writen by {%by%}. The chapters are `{%chapters%}`. Keywords are not set in the configuration file : `{%metadata.keywords%}`.

You can use your own variables, by setting them under `variables` in the configuraiton file : {%names.character1%}, and `{%todo%}`.

## Sep

It create a separation than can be customized with the configuration file.

Laboris irure culpa irure dolore dolor nostrud minim dolor ex nostrud quis mollit non in velit mollit. Lorem ipsum dolore velit sint esse laboris culpa sit sed et excepteur ullamco sint veniam duis laboris aute in deserunt commodo veniam anim in anim labore nostrud cillum laborum.

{%sep%}

Ut id tempor ut duis qui ut officia cillum deserunt. Duis dolore est sunt reprehenderit veniam ut sunt tempor deserunt ut sit ut nostrud excepteur veniam eu. Nulla incididunt cupidatat tempor cillum et amet amet enim non excepteur quis officia do ad incididunt dolor enim consectetur culpa et sit.

## Skip

Using skip will force a page break. The default behavior is to also insert a page break between every level 1 title, but it can be overwride with the configuration file.

Laboris irure culpa irure dolore dolor nostrud minim dolor ex nostrud quis mollit non in velit mollit. Reprehenderit reprehenderit nostrud commodo eu sunt aliqua in magna ut consequat voluptate incididunt quis qui velit reprehenderit incididunt laborum nostrud qui ut laboris est labore.

{%skip%}

Ut id tempor ut duis qui ut officia cillu. Consectetur sunt exercitation exercitation officia esse dolore laborum dolore cupidatat sed in sed magna enim nostrud velit dolor eu nisi adipisicing in elit dolor sit mollit anim labore. Cupidatat dolor ex excepteur aute officia nostrud ex culpa elit officia eiusmod nisi sint amet excepteur deserunt in dolore est sint.

## Include

We can include a file multiple time. This template is useful for inserting small blocks without copy-pasting. But we recommend using the chapters to split your text into multiple main files.

{%included.md:include%}

{%included.md:include%}

## Font, size and color

I want to use a more funny font. The text will now use the `calligraffiti` font. Do not insert templates to change the font, the color or the size in the middle of a paragraph, it can cause bugs. Use pure html if you really want to do it. Font template must be used on a line without leading or trailing spaces and without any other template, include font templates.

{%calligraffiti : font%}

Wow, this paragraph uses `calligraffiti` ! Now I can change the color.

{%#031594 : color%}

This text is now in blue. But I can make it bigger.

{%2em : size%}

This is a bigger text, indeed. But before going to the next section, I will reset all the text properties.

{%:font%}
{%:color%}
{%:size%}

## Conditions

This code will display the subtitle only if it extists : {%:if : subtitle : <div id="bookSubtitle">{%subtitle%}</div> %}.

- 2 + 2 = 2 ? {%:if : 2+2 == 2 : OUI ! : else : Non...%}
- 2 + 2 = 4 ? {%:if : 2+2 == 4 : OUI ! : else : Non...%}