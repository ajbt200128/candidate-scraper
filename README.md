- [Installation](#sec-1)
- [Basic Usage](#sec-2)
  - [Output](#sec-2-1)
  - [HTML patterns](#sec-2-2)
    - [Example](#sec-2-2-1)
    - [Tips for matching](#sec-2-2-2)
  - [Follow Link Option](#sec-2-3)
  - [Checking for errors](#sec-2-4)


# Installation<a id="sec-1"></a>

Clone this repository, then cd to the directory and run

```bash
pipenv install
chmod 777 scraper.py
```

Start the virtual environment before running the script with

```bash
pipenv shell
```

# Basic Usage<a id="sec-2"></a>

```bash
./scraper.py [-fl FOLLOW_LINK] N U I D [-o OUTPUT_PATH]
```

Where:

| Parameter          | Description                                                           | Example                                   |
|------------------  |---------------------------------------------------------------------  |-----------------------------------------  |
| N                  | Is the name of a candidate                                            | "Pete Aguilar"                            |
| U                  | Is the URL                                                            | "<https://peteaguilar.com/on-the-issues>" |
| I                  | Is the Issue HTML pattern                                             | "div#not-secret>h3"                       |
| D                  | Is the Description HTML pattern                                       | "section#article>div#insides"             |
| -fl [FOLLOW\_LINK] | Is the Description Page link HTML pattern (optional)                  | "div#tiles>div>a"                         |
| -f                 | Force the write of whatever issues/descriptions were found (optional) | -f                                        |
| -i                 | Connect to insecure websites aka http not https (optional)            | -i                                        |
| -o [OUTPUT\_PATH]  | Specify the location of the output file; default is out/ (optional)   | -o "./scraped/"                           |

The full command looks like this:

```bash
./scraper.py -fl "div#tiles>div>a" "Pete Aguilar" "https://peteaguilar.com/on-the-issues/" "div#not-secret>h3" "section#article>div#insides"
```

## Output<a id="sec-2-1"></a>

This will output both to the screen, and to `out/Candidate_Name.csv` with the first column being the issue, and the second the description

## HTML patterns<a id="sec-2-2"></a>

An HTML Pattern is made up of 3 parts, an html element type, the class name of the html element, and the separator:

`HTML_ELEMENT_NAME#CLASS_NAME>HTML_ELEMENT_NAME#CLASS_NAME>...>HTML_ELEMENT_NAME#CLASS_NAME`

Where the the seperator denotes the parent to child, I.E. the left element is the parent element, and the right is the child, the rightmost being the element that either a link or text is extracted from. Multiple matches can be returned.

Note: The `#CLASS_NAME` part is optional

### Example<a id="sec-2-2-1"></a>

```html
<html>
  <div>
    <div class="issue">
      <h3 class="underline">Climate</h3>
      <p>Save the environment!</p>
    </div>
    <div class="issue">
      <h3 class="bold">Education</h3>
      <p>Improve Education!</p>
    </div>
  </div>
  <div>
    <div>
      <h3 class="bold">Contact me</h3>
      <p>123 Sesame Street</p>
    </div>
  </div>
</html>
```

| Pattern         | Matches                                |
|--------------- |-------------------------------------- |
| h3              | `<h3 class="climate">Climate</h3>`     |
|                 | `<h3 class="education">Education</h3>` |
|                 | `<h3>Contact me</h3>`                  |
| div>h3          | `<h3 class="climate">Climate</h3>`     |
|                 | `<h3 class="education">Education</h3>` |
|                 | `<h3>Contact me</h3>`                  |
| h3#bold         | `<h3 class="bold">Education</h3>`      |
|                 | `<h3>Contact me</h3>`                  |
| div#issue>h3    | `<h3 class="climate">Climate</h3>`     |
|                 | `<h3 class="education">Education</h3>` |
| div#issue>p     | `<h3 class="climate">Climate</h3>`     |
|                 | `<h3 class="education">Education</h3>` |
| div#something>p | Nothing                                |
| div>span>div    | Nothing                                |

### Tips for matching<a id="sec-2-2-2"></a>

Open inspect element on your browser, and use the element selector to pick the issue/description. Try to pick patterns that are unique to the page, but shared only among the issue/description. Try patterns with only one or two elements/class names first, and go more specific if the program keeps over matching.

## Follow Link Option<a id="sec-2-3"></a>

If the candidate's position description is on another page, then you can specify the \`-fl\` option followed by an html pattern matching an element that contains an "href" attribute that equals the link to the page of the description. The description html pattern should match whatever the description is on that page, and if it makes multiple matches on one page, it will be combined into one text block.

## Checking for errors<a id="sec-2-4"></a>

The program will print out the list of issues it found and corresponding descriptions. If the lengths of these two lists don't match, that means you are over/under matching to many/little elements and should try to find a more explicit pattern
