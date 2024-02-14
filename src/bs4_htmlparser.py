# Standard modules
import os
import sys
import io
from typing import Union
import re

# Web scraping
import requests
import bs4
from bs4 import BeautifulSoup

# Logging
import logging
logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
handler_format = logging.Formatter('%(asctime)s : [%(name)s - %(lineno)d] %(levelname)-8s - %(message)s')
stream_handler.setFormatter(handler_format)
logger.addHandler(stream_handler)

# UTF-8エンコーディング
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class BeautifulSoupHTMLParser(object):
  # https://qiita.com/Chanmoro/items/db51658b073acddea4ac
  # Constructor
  def __init__(self):
    self.url = 'setme'
    self.soup = None

  # Setter
  def set_url(self, url: str) -> None:
    self.url = url
    self.response = requests.get(url)
    self.response.encoding = self.response.apparent_encoding
    self.soup = BeautifulSoup(self.response.text, features='html.parser')

  def set_soup(self, html: Union[str, None]=None) -> None:
    self.soup = BeautifulSoup(self.response.text if html is None else html, features='html.parser')

  # Getter
  def get_url(self):
    return self.url

  def get_element_by_tag(self, tag: str) -> str:
    return self.soup.find(tag)

  def get_elements_by_tag(self, tag: str) -> list[str]:
    return self.soup.find_all(tag)

  # 一致するid属性を持つ要素
  def get_element_by_id(self, id: str) -> str:
    return self.soup.select_one(f'#{id}')

  def get_elements_by_id(self, id: str) -> list[str]:
    return self.soup.select(f'{id}')

  # 一致するCSSセレクターを持つ要素
  def get_element_by_css(self, css: str) -> str:
    return self.soup.select_one(css)

  def get_elements_by_css(self, css: str) -> list[str]:
    return self.soup.select(css)

  # 一致するCSSクラスを持つ要素
  def get_element_by_css_class(self, css_class: str) -> str:
    return self.soup.select_one(f'.{css_class}')

  def get_elements_by_css_class(self, css_class: str) -> list[str]:
    return self.soup.select(f'.{css_class}')

  # 一致するタグと属性をもつ要素
  def get_element_by_tag_and_attribute(self, tag: str, attribute: str) -> str:
    return self.soup.select_one(f'{tag}[{attribute}]')

  def get_elements_by_tag_and_attribute(self, tag: str, attribute: str) -> list[str]:
    return self.soup.select(f'{tag}[{attribute}]')

  # 一致するタグと属性値をもつ要素
  def get_element_by_tag_and_attribute_value(self, tag: str, attribute: str, value: str) -> str:
    return self.soup.select_one(f'{tag}[{attribute}="{value}"]')

  def get_elements_by_tag_and_attribute_value(self, tag: str, attribute: str, value: str) -> list[str]:
    return self.soup.select(f'{tag}[{attribute}="{value}"]')

  # テキストに'text'と書かれている'adj_tag'と横並びとなっている'tag'要素
  def get_element_by_adjancent_text(self, adj_tag: str, text: str, tag: str) -> str:
    return self.soup.select_one(f'{adj_tag}.contains("{text}") ~ {tag}')

  def get_elements_by_adjancent_text(self, adj_tag: str, text: str, tag: str) -> list[str]:
    return self.soup.select(f'{adj_tag}.contains("{text}") ~ {tag}')

  # 要素からテキストのみを取得
  def get_content_from_element(self, element: str, strip: bool=False) -> str:
    return element.get_text(strip=strip)

  def get_contents_from_elements(self, elements: list[str], strip: bool=False) -> list[str]:
    return [element.get_text(strip=strip) for element in elements]

  # 要素から属性値のみを取得
  def get_attribute_from_element(self, element: str, attr_name: str) -> str:
    return element.get(attr_name)

  def get_attributes_from_elements(self, elements: list[str], attr_name: str) -> list[str]:
    return [element.get(attr_name) for element in elements]

  # 全てのテキストのみを取得
  def get_all_texts(self):
    # script, styleを含む要素を削除する
    for script in self.soup(['script', 'style']):
      script.decompose()

    # テキストのみを取得(タグは全て取る)
    text = self.soup.get_text(separator='\n')

    # テキストを改行毎にリストに入れ、リスト内の要素の前後の空白を削除
    lines = [line.strip() for line in text.splitlines()]

    # リストの空白要素以外を全て文字列に戻す
    text = '\n'.join(line for line in lines if line)

    return text

  # 全てのイメージのみを取得
  def cutout_filename_without_appendix(self, path: str) -> str:
    file = os.path.basename(path)
    file_without_appendix = os.path.splitext(file)[0]
    return file_without_appendix

  def get_all_images(self, appendix: str='png'):
    urls = [self.get_attribute_from_element(element=element, attr_name='src') for element in self.get_elements_by_tag(tag='img')]
    for url in urls:
      response = requests.get(url)
      with open(f'assets/{self.cutout_filename_without_appendix(path=url)}.{appendix}', 'wb') as file:
        file.write(response.content)

  # テキストを綺麗にする
  def text_cosmetics(self, text: str, impurities: list[str]=['\n', '\t', '\r', '\s', '\f'], replacer: str=''):
    # \n: 改行
    # \t: タブ
    # \r: リターン
    # \s: 空白
    # \f: 改ページ
    for impurity in impurities:
      text = text.replace(impurity, replacer)
    return text

  def texts_cosmetics(self, texts: list[str], impurities: list[str]=['\n', '\t'], replacer: str=''):
    texts = [self.text_cosmetics(text=text, impurities=impurities, replacer=replacer) for text in texts]
    return texts

  def text_cosmetics_re(self, text: str, impurities: list[str]=[r'\u[0-9]{4}'], replacer: str=''):
    for impurity in impurities:
      text = re.sub(impurity, replacer, text, flags=re.UNICODE)
    return text

  def texts_cosmetics_re(self, texts: list[str], impurities: list[str]=[r'\u[0-9]{4}'], replacer: str=''):
    texts = [self.text_cosmetics_re(text=text, impurities=impurities, replacer=replacer) for text in texts]
    return texts

  def text_remove_unicode(self, text: str):
    return text.encode('ascii', 'ignore')

  def texts_remove_unicode(self, texts: list[str]):
    texts = [self.text_remove_unicode(text=text) for text in texts]
    return texts

  def remove_boid_texts(self, texts: str):
    return [text for text in texts if text != '']

if __name__ == '__main__':
  parser = BeautifulSoupHTMLParser()
  parser.set_url(url='https://d1d76jlpbzebww.cloudfront.net/')
  text = parser.get_all_texts()
  print(text)
  # parser.get_all_images()

  text = re.sub(r'\\u[0-9]+', 'hoge', 'Copyright\u2002© HOUSE\u2002WELLNESS\u2002FOODS Co.LTD.All\u2002rights\u2002reserved.')
  print(text)
  print('Copyright\u2002© HOUSE\u2002WELLNESS\u2002FOODS Co.LTD.All\u2002rights\u2002reserved.')