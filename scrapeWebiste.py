"""
    File name: scrapeWebsite.py
    Author: Luc Blassel
    email: luc[dot]blassel[at]pasteur[dot]fr
    Date created: 14 Sept. 2020
    Python Version: 3.8.5
"""
import json
import re

import requests
from bs4 import BeautifulSoup

BASE_URL = "http://www.ccmrd.org"


def parseTable(table):
    headers, tableContent = [], []
    for cell in table.find("thead").find("tr").children:
        if cell != "\n":
            headers.append(list(cell.children)[0].strip())
    for row in table.find("tbody").find_all("tr"):
        tableContent.append(dict())
        for header, cell in zip(headers, row.find_all("td")):
            if (img := cell.find("img")) is not None:
                tableContent[-1][header] = parse_image(img)
            elif len(atoms := cell.find_all(attrs={"class": "atoms"})) > 0:
                tableContent[-1][header] = parse_atoms(cell)
            else:
                tableContent[-1][header] = (
                    cell.contents[0] if len(cell.contents) > 0 else ""
                )
    return tableContent


def parse_atoms(row):
    shifts = {}
    for i in range(1, len(row.contents), 2):
        carbon = row.contents[i].contents[0]
        shifts[carbon] = re.match(
            r":\s*([0-9\.]*)\s*;", row.contents[i + 1].strip()
        ).groups()[0]
    return shifts


def parse_image(img):
    return f"{BASE_URL}{img.attrs.get('src', 'invalid')}"


def parse_representation(table):
    return f"{BASE_URL}{table.find('img').get('src', 'invalid')}"


def parseReference(reference):
    doi = reference.find("a").attrs.get("href", " no DOI ")
    reference.find("a").decompose()

    authors, year, title, journal, pages, *rest = reference.find(
        attrs={"class": "article-ref"}
    ).contents

    authorList = [x.strip() for x in authors.split("\n")][1:-1]
    parsedYear = re.match(r"<strong>(\d+)<\/strong>", str(year)).groups()[0]
    parsedJournal = re.match(r"<strong>(.+)<\/strong>", str(journal)).groups()[0]
    parsedTitle = title.replace(").", "").strip()[:-1]

    return {
        "doi": doi,
        "authors": authorList,
        "year": parsedYear,
        "title": parsedTitle,
        "journal": parsedJournal,
        "pages": "".join([x.strip() for x in pages.split("\n")]),
    }


def parsePage(content):
    res = {}
    for subpart in content.find_all(attrs={"class": "compound-subpart"}):
        key = subpart.find(attrs={"class": "compound-subtitle"}).contents[0].strip()
        if key == "Reference":
            res["reference"] = parseReference(subpart)
        elif key == "SNFG representation of Compound":
            res["representation"] = parse_representation(subpart)
        else:
            table = subpart.find(attrs={"class": "subpart-table"})
            try:
                res[key] = parseTable(table)
            except:
                res[key] = "error"
    return res


if __name__ == "__main__":
    total_res = {}
    for id_ in range(1000):
        page = BeautifulSoup(
            requests.get(f"{BASE_URL}/compound/{id_}").content, features="lxml"
        )
        if page.find("title").contents[0] == "500 Error":
            continue
        print(f"processing compound {id_}")
        total_res[id_] = parsePage(page)

    print(f"found {len(total_res)} records")
    json.dump(total_res, open("CCMRD_scraped.json", "w"))
