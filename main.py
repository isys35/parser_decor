from parsing_base import Parser
from bs4 import BeautifulSoup


class DecorParser(Parser):
    def __init__(self):
        super().__init__()
        self.host = 'https://www.oikos-paint.com'
        self.categories = []

    def update_categories(self):
        print(self.host)
        resp = self.request.get(self.host)
        self.parsing_category(resp.text)

    def parsing_category(self, resp):
        soup = BeautifulSoup(resp, 'lxml')
        dropdown_menu = soup.select_one('.dropdown-menu')
        self.categories = [{'name': a.text, 'url': self.host + a['href']} for a in dropdown_menu.select('a')]

    def update_subcategories(self):
        resps = self.requests.get([categorie['url'] for categorie in self.categories])
        self.parsing_subcategories(resps)

    def parsing_subcategories(self, resps):
        for category in self.categories:
            index = self.categories.index(category)
            category['subcategories'] = []
            soup = BeautifulSoup(resps[index], 'lxml')
            divs = soup.select('div')
            for div in divs:
                if 'titolo' in div['class']:
                    name_subcategorie = div.text
                    subcategorie = {'name': name_subcategorie, 'subsubcategories': []}
                elif 'col-6' in div['class']:
                    url_subsubcategorie = self.host + div.select_one('a')['href']
                    name_subsubcategorie = div.select_one('.m-1').text
                    subsubcategorie = {'name': name_subsubcategorie, 'url': url_subsubcategorie}
                    subcategorie['subsubcategories'].append(subsubcategorie)
            category['subcategories'].append(subcategorie)















if __name__ == '__main__':
    parser = DecorParser()
    parser.update_categories()
    parser.update_subcategories()
    print(parser.categories)