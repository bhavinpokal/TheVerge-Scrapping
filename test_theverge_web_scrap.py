import csv
import datetime
import os
import unittest

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from theverge_web_scrap import TheVergeScrap

today = datetime.date.today().strftime("%d%m%Y")
filename_csv = today + "_verge.csv"
row0 = '0,https://www.theverge.com/23670169/logout-button-ui-websites-design-ui-interface,The impossibility of logging off,Terry Nguyen,2023/04/06\n'
row1 = '1,https://www.theverge.com/23669728/apple-lisa-macintosh-ui-design-history,The Apple Lisa was a design revolution — and it still feels like one today,Adi Robertson,2023/04/06\n'
row2 = '1,https://www.theverge.com/2023/4/6/23673462/google-webgpu-chrome-113-api-machine-learning,Google is rolling out WebGPU tech for next-gen gaming in your browser,Mitchell Clark,2023/04/07\n'


class TestTheVergeScrap(unittest.TestCase):
    def setUp(self):
        self.scrap_obj = TheVergeScrap()
        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-dev-sh-usage")

        s = Service(
            "C:\\Users\\bhavi\\Downloads\\chromedriver_win32\\chromedriver.exe")
        self.base_url = "https://www.theverge.com"
        self.driver = webdriver.Chrome(service=s, options=option)
        self.driver.get(self.base_url)

        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.file = open(filename_csv, "r")

    # def tearDown(self):
    #     self.s.close()

    def test_save_main_article(self):
        self.scrap_obj.save_main_article()
        main_article = self.file.readlines()
        self.assertEqual(main_article[1], row0)

    def test_save_top_stories(self):
        self.scrap_obj.save_top_stories()
        top_stories = self.file.readlines()
        self.assertEqual(top_stories[1], row1)

    def test_save_other_content(self):
        self.scrap_obj.save_other_content()
        other_content = self.file.readlines()
        self.assertEqual(other_content[1], row2)


if __name__ == '__main__':
    unittest.main()
