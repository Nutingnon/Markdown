# Introduction to Markdown syntax

***Markdown*** is a plain-text editor, which makes normal text easier to read through simple markdown syntax. There are multiple platforms support markdown format, such as Github, jupyterlab, and Quora.

---

# 1. Set up a Title

Example: 

```
# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6
```

##### Effects are as follows:

# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6

----

# 2. Fonts setting

- **Italic**: put the text inside one asterisk *
- **Bold**: put the text inside two asterisk **
- **Italic and Bold**: put the text inside three asterisk ***
- **strikethrough**: put the text inside two tilde ~~

Example:

```
**This is the bold text**
*This is the italic text*
***This is the bold and italic text***
~~this is the strikethrough text~~
```

##### Effects are as follows:

**This is the bold text**
*This is the italic text*
***This is the bold and italic text***
~~this is the strikethrough text~~

### Font Settings: Font type, size and color:

```
<font face="黑体">我是黑体字</font>
<font face="微软雅黑">This is Microsoft YaHei</font>
<font face="STCAIYUN">This font is STCAIYUN</font>
<font color=red>This color is red</font>
<font color=#008000>This color is green using color code</font>
<font color=Blue>This color is Blue</font>
<font size=5>This fontsize is 5</font>
<font face="黑体" color=green size=5>我是黑体，绿色，尺寸为5</font>
```

<font face="黑体">我是黑体字</font>
<font face="微软雅黑">This is Microsoft YaHei</font>
<font face="STCAIYUN">This font is STCAIYUN</font>
<font color=red>This color is red</font>
<font color=#008000>This color is green using color code</font>
<font color=Blue>This color is Blue</font>
<font size=5>This fontsize is 5</font>
<font face="黑体" color=green size=5>我是黑体，绿色，尺寸为5</font>

---

# 3. Reference

Add right arrow symbol in front of the text to refer. 

Example: 

```
>this is referring contents.
>>this is referring contents.
>>>this is referring contents.
```

### Effects are as follows

>this is referring contents.
>
>>this is referring contents.
>>
>>>this is referring contents.

---

# 4. Split Line

Use tripple or more hyphen or asterisk.

Example:

```
---
----
***
****
```

---
----

***

****

### Syntax:

`![Image Annotation](ImageAddress ''Image title '')`

The Image annotation is to help you understand the image. The title is the pop-up text when pointer hovering on the image.

Example:

```
![Cat](https://img.webmd.com/dtmcms/live/webmd/consumer_assets/site_images/article_thumbnails/other/cat_weight_other/1800x1200_cat_weight_other.jpg?resize=600px:* '' A cute CAT'')
```

### Effect

![This is a cute cat](https://img.webmd.com/dtmcms/live/webmd/consumer_assets/site_images/article_thumbnails/other/cat_weight_other/1800x1200_cat_weight_other.jpg?resize=600px:*` ''A cute CAT'')

When you hover the pointer over the image:

![image-20200329235514259](/Users/kadima/Library/Application Support/typora-user-images/image-20200329235514259.png)

---

# 5. Hyperlinks

### Syntax

`[Hyperlink name](hyperlinkAddress "hyperlink title")`

Example:

```
[Google](https://www.google.com)
[My favorite website](https://github.com/)
```

[Google](https://www.google.com)
[My favorite website](https://github.com/)

Note: the syntax of Markdown itself does not support links to be opened in new pages. However, some platforms do something and make it possible. If you'd like to open it in a new page, you can use the a tag in HTML instead. 

`<a href="hyperlinkAddress" target="_blank">hyperlinkName</a>`

Example

```
<a href="https://www.baidu.com" target="_blank">百度</a>
```

<a href="https://www.baidu.com" target="_blank">百度</a>

----

# 6. Listing

Syntax: you can use anyone of: - + and *  

For numbers, there will be automatically indentation.

```
- content1
+ content2
* content3
1. content4
2. content5
```

- content1
+ content2

* content3

1. content4
2. content5

Or you can use those listing symbols interchangeably

```
* firstlevel 1
	1. second level 1
	2. second level 2
* firstlevel 2
	1. second level 3
	1. second level 3
```

* firstlevel 1
	1. second level 1
	2. second level 2
* firstlevel 2
	1. second level 3
	1. second level 3

----

# 7. Table

Syntax:

```
Header1|Header2|Header3
--|:--:|--:|
content|content|content
content|content|content

The second paragraph is to segment header and body
needs only 1 "-" hyphen
the content is on the left in default
":-:" makes it in the middle
"-:" makes it on the right 
```



Example:

```
Ranking|Programming Language|No. ppl using it
--|:--:|--:
1|Python|1,120,000
2|Java|15,000
3|Scala|9,000
4|JavaScript|3,300
```

| Ranking | Programming Language | No. ppl using it |
| ------- | :------------------: | ---------------: |
| 1       |        Python        |        1,120,000 |
| 2       |         Java         |           15,000 |
| 3       |        Scala         |            9,000 |
| 4       |      JavaScript      |            3,300 |

---

# 8. Coding

Syntax:

One-line code: use single quote mark

Multi-line code: use tripple quote mark, each tripple occupy one paragraph

```
# one-line code:
`df = pd.DataFrame(data)`

# multi-line code:
​```
data = pd.read_csv("this.csv")
data.loc[:,["user_id"]].dropna(inplace=True)
​```
```

Demo code:

`df = pd.DataFrame(data)`

```
data = pd.read_csv("this.csv")
data.loc[:,["user_id"]].dropna(inplace=True)
```

------

# 10. Emoji

you can use 2 colons with key word in the middle to output a emoji, such as:

`:horse:`

:horse:

`:girl:`

:girl:

---

# 11. Formula

Similarly, you can type formula with latex as you did in other platform. Let's type the famous **Mass energy equation**

`$$E=mc^{2}$$`
$$
E = mc^{2}
$$


---

# 12. Flowchart

Flowchart is also easy in markdown. Like coding, you only need to define some variables and their names and then setup the rules of flow chart

Example:

```
​```flow
st=>start: 打开游戏
op=>operation: 一顿操作猛如虎
op2=>operation: 一看战绩零杠五
cond=>condition: 游戏胜利？
cond2=>condition: 再来一把？
e=>end: 吹一年
e2=>end: 裂开来

st->op->op2->cond
cond(yes)->e
cond(no)->cond2
cond2(yes)->op
cond2(no)=>e2
​```
```

```flow
st=>start: 打开游戏
op=>operation: 一顿操作猛如虎
op2=>operation: 一看战绩零杠五
cond=>condition: 游戏胜利？
cond2=>condition: 再来一把？
e=>end: 吹一年
e2=>end: 裂开来

st->op->op2->cond
cond(yes)->e
cond(no)->cond2
cond2(yes)->op
cond2(no)->e2
```

