#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import argparse
import pprint
parser = argparse.ArgumentParser(description='Scrapes candidate issue info')
parser.add_argument('link', metavar='L', type=str, help="Link of candidate")
parser.add_argument('issue_pattern', metavar='I', type=str,
                    help='HTML Element pattern of the issue element e.g. h1>p>a#classname a#classname, or just a#')
parser.add_argument('description_pattern', metavar='D', type=str,
                    help='HTML Element pattern of the description element')
parser.add_argument('--link', action='store',
                    help='If issue element is link to a page with the description')
args = parser.parse_args()
pp = pprint.PrettyPrinter(indent=4)


def get_page_soup():
    url = args.link
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    page = requests.get(url, headers=headers).content
    return BeautifulSoup(page, 'html.parser')


def get_text_by_pattern(soup, pattern):
    element_names = pattern.split('>')
    print("Element names ", element_names)
    class_name = element_names[-1].split('#')[1]
    element_names[-1] = element_names[-1].split('#')[0]
    text = []
    if len(element_names) == 1:
        elements = soup.find_all(element_names[0], {"class": class_name})
        for el in elements:
            el = el.text
            print(el)
            text.append(el)
    else:
        elements = soup.find_all(element_names[0])
        for name in element_names[1:-1]:
            for i in range(0, len(elements)):
                if elements[i] is not None:
                    elements[i] = elements[i].findChildren(
                        name, recursive=False)
                    if elements[i] is not None and len(elements[i]) > 0:
                        elements[i] = elements[i][0]
                    else:
                        elements[i] = None

        elements = list(
            filter(lambda x: x is not None and len(x) != 0, elements))
        for el in elements:
            text_elements = None
            if not class_name:
                text_elements = el.findChildren(
                    element_names[-1], recusive=False)
            else:
                text_elements = el.findChildren(
                    element_names[-1], {'class', class_name}, recursive=False)
            for text_element in text_elements:
                text_element = text_element.text
                text.append(text_element)

    return text


def main():
    soup = get_page_soup()
    issues = get_text_by_pattern(soup, args.issue_pattern)
    descriptions = get_text_by_pattern(soup, args.description_pattern)
    if len(issues) != len(descriptions):
        print("Error: Issue length does not match description length")
    print(len(issues))
    print(len(descriptions))


main()
