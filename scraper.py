#!/usr/bin/python
import argparse
import csv
import pprint

import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description="Scrapes candidate issue info")
parser.add_argument("name", metavar="N", type=str, help="Name of candidate")
parser.add_argument("url", metavar="U", type=str, help="URL of candidate")
parser.add_argument(
    "issue_pattern",
    metavar="I",
    type=str,
    help="HTML Element pattern of the issue element, see README for pattern explanation",
)
parser.add_argument(
    "description_pattern",
    metavar="D",
    type=str,
    help="HTML Element pattern of the description element, see README for pattern explanation",
)
parser.add_argument(
    "-fl",
    "--follow-link",
    dest="follow_link",
    type=str,
    required=False,
    help="If issue element is link to a page with the description",
)

parser.add_argument(
    "-f",
    "--force",
    dest="force",
    action='store_true',
    help="Force write to csv"
)

parser.add_argument(
    "-i",
    "--invalid",
    dest="invalid",
    action='store_true',
    help="Force to make invalid HTTP request"
)

args = parser.parse_args()
pp = pprint.PrettyPrinter(indent=4)

# Generates beautiful soup object
def get_page_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    if not args.invalid:
        page = requests.get(url, headers=headers).content
    else:
        page = requests.get(url, headers=headers,verify=False).content

    return BeautifulSoup(page, "html.parser")


# Gets the innermost children of the passed elements given the names where
# names is a list of pairs of strings (element_name, element_class)
def get_children(names, elements):
    for pair in names:
        children = []
        for i in range(0, len(elements)):
            if elements[i] is not None:
                if pair[1]:
                    elements[i] = elements[i].findChildren(
                        pair[0], {"class", pair[1]}, recursive=False
                    )
                else:
                    elements[i] = elements[i].findChildren(pair[0], recursive=False)
                if elements[i] is not None:
                    children.extend(elements[i])
                else:
                    elements[i] = None
        elements = children

    return elements


# Returns either the text elements or links in a given soup object by pattern
def get_text_by_pattern(soup, pattern, get_link=False):
    element_names_unformatted = pattern.split(">")
    element_names = []
    for el_name in element_names_unformatted:
        if "#" in el_name:
            el_parts = el_name.split("#")
            element_names.append((el_parts[0], el_parts[1]))
        else:
            element_names.append((el_name, None))

    elements = None
    if element_names[0][1]:
        elements = soup.find_all(element_names[0], {"class": element_names[0][1]})
    else:
        elements = soup.find_all(element_names[0])

    elements = list(get_children(element_names[1:], elements))
    elements = list(filter(lambda x: x is not None and len(x) != 0, elements))

    wanted = []
    for el in elements:
        if not get_link:
            wanted.append(el.text.strip())
        else:
            wanted.append(el["href"])
    return list(dict.fromkeys(wanted))


def get_issues(soup):
    issues = get_text_by_pattern(soup, args.issue_pattern)
    return issues


def get_descriptions(soup,url):
    descriptions = []
    if args.follow_link:
        links = get_text_by_pattern(soup, args.follow_link, get_link=True)
        print(links)
        for link in links:
            if link[0] == "/":
                link= url.rsplit('/', 1)[0] + link
            soup = get_page_soup(link)
            description = get_text_by_pattern(soup, args.description_pattern)
            description = "\n".join(description)
            descriptions.append(description.strip())
    else:
        descriptions = get_text_by_pattern(soup, args.description_pattern)
    return descriptions


def main():
    soup = get_page_soup(args.url)
    issues = list(filter(None, get_issues(soup)))
    descriptions = list(filter(None, get_descriptions(soup,args.url)))
    print(issues)
    for i,desc in enumerate(descriptions):
        print(f"======= {i} =======")
        print(desc)
    if len(issues) != len(descriptions) and not args.force:
        print(f"Error: Issue length({len(issues)}) does not match description length({len(descriptions)})")
        return
    filename = 'out/'+args.name.replace(' ', '_') + '.csv'
    length = len(issues)
    if len(issues) < len(descriptions):
        length = len(descriptions)
        while len(issues) < length:
            issues.append("")
    else:
        while len(descriptions) < length:
            descriptions.append("")
    

    with open(filename,'w') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(length):
            writer.writerow([args.name.encode('utf-8'), issues[i].encode('utf-8'), descriptions[i].encode('utf-8'),args.url.encode('utf-8')])


main()
