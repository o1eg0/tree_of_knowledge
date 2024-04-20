import re
from enum import Enum
from typing import Optional, List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


def title_format(title: str):
    if len(title) > 35:
        title = f'{title[:35]}'

    title = re.sub(r'[^a-zA-Zа-яА-Я1-9 ]', '', title).strip()
    title = re.sub(r' {2,}', ' ', title)
    title = title.replace(' ', '_')

    return title


class Book(BaseModel):
    libgen_id: int
    title: str
    lang: str
    extension: str


class SearchType(Enum):
    MD5 = 'md5'
    TITLE = 'title'


class Search:

    def __init__(self, type: SearchType = SearchType.MD5):
        self.type = type

    def search(self, query) -> Optional[List[Book]]:
        try:
            search_request = SearchRequest(query, search_type=self.type)
            return search_request.aggregate_request_data()
        except Exception as e:
            return None


class SearchRequest:
    col_names = ["ID", "Author", "Title", "Publisher", "Year", "Pages", "Language", "Size", "Extension", "Mirror_1",
                 "Mirror_2", "Mirror_3", "Mirror_4", "Mirror_5", "Edit"]

    def __init__(self, query, search_type: SearchType):
        self.query = query
        self.search_type = search_type.value

        if len(self.query) < 3:
            raise Exception("Query is too short")

    def strip_i_tag_from_soup(self, soup):
        subheadings = soup.find_all("i")
        for subheading in subheadings:
            subheading.decompose()

    def get_search_page(self):
        query_parsed = "%20".join(self.query.split(" "))
        search_url = f'https://libgen.is/search.php?req={query_parsed}&column={self.search_type}'
        search_page = requests.get(search_url)
        return search_page

    def aggregate_request_data(self):
        search_page = self.get_search_page()
        soup = BeautifulSoup(search_page.text, "lxml")
        self.strip_i_tag_from_soup(soup)

        information_table = soup.find_all("table")[2]
        raw_data = [
            [
                td.a["href"]
                if td.find("a") and td.find("a").has_attr("title") and td.find("a")["title"] != ""
                else "".join(td.stripped_strings)
                for td in row.find_all("td")
            ] for row in information_table.find_all("tr")[1:]
        ]
        output_data = [
            Book(
                libgen_id=int(row[0]),
                title=title_format(row[2]),
                lang=row[6].lower(),
                extension=row[8]
            ) for row in raw_data
        ]
        return output_data
