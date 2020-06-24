from parsing_base import Parser
from bs4 import BeautifulSoup
import re

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

    def update_textures_colors(self):
        for categorie in self.categories:
            for subcategorie in categorie['subcategories']:
                resps = self.requests.get([subsubcategorie['url'] for subsubcategorie in subcategorie['subsubcategories']])
                self.parse_texture_colors(resps, subcategorie['subsubcategories'])

    def parse_texture_colors(self, resps, subcategories):
        for resp in resps:
            index = resps.index(resp)
            textures = self.parse_textures(resp)
            subcategories[index]['textures'] = textures
            colors = self.parse_colors(resp)
            subcategories[index]['colors'] = colors

    def parse_colors(self, resp):
        soup = BeautifulSoup(resp, 'lxml')
        divs = soup.select('div')
        target = False
        colors = []
        for div in divs:
            if 'class' not in div.attrs:
                continue
            if 'titolo' in div['class']:
                if target:
                    break
                if div.text == 'COLOUR PALETTE':
                    target = True
            if target:
                if 'aspect-ratio-div' in div['class']:
                    if not div.select_one('div'):
                        continue
                    color_name = div.select_one('div').text
                    color_url = div['style']
                    color_url = self.host + re.findall('background-image:url\((.*)\)', color_url)[0]
                    colors.append({'name': color_name, 'url': color_url})
        return colors

    def parse_textures(self, resp):
        soup = BeautifulSoup(resp, 'lxml')
        divs = soup.select('div')
        target = False
        textures = []
        for div in divs:
            if 'class' not in div.attrs:
                continue
            if 'titolo' in div['class']:
                if target:
                    break
                if div.text == 'TEXTURE':
                    target = True
            if target:
                if 'aspect-ratio-div' in div['class']:
                    texture_name = div.select_one('div').text
                    image_url = div['style']
                    image_url = re.findall('background-image:url\((.*)\)', image_url)[0]
                    textures.append({'name': texture_name, 'url': image_url})
        return textures

    def parsing_subcategories(self, resps):
        for category in self.categories:
            index = self.categories.index(category)
            category['subcategories'] = []
            soup = BeautifulSoup(resps[index], 'lxml')
            content = soup.select_one('.pb-5')
            divs = content.select('div')
            subcategorie = None
            for div in divs:
                if 'titolo' in div['class']:
                    if subcategorie:
                        category['subcategories'].append(subcategorie)
                    name_subcategorie = div.text
                    subcategorie = {'name': name_subcategorie, 'subsubcategories': []}
                elif 'col-6' in div['class']:
                    url_subsubcategorie = self.host + div.select_one('a')['href']
                    name_subsubcategorie = div.select_one('.m-1').text.replace('\n', '').strip()
                    subsubcategorie = {'name': name_subsubcategorie, 'url': url_subsubcategorie}
                    subcategorie['subsubcategories'].append(subsubcategorie)
            category['subcategories'].append(subcategorie)

if __name__ == '__main__':
    parser = DecorParser()
    parser.update_categories()
    parser.update_subcategories()
    parser.update_textures_colors()