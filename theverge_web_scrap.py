import datetime
import sqlite3
import sys

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


class TheVergeScrap:
    def __init__(self):
        """Initialize the connection to the website and database, create CSV file and table in db"""

        option = webdriver.ChromeOptions()
        option.add_argument("--headless")
        option.add_argument("--no-sandbox")
        option.add_argument("--disable-dev-sh-usage")

        s = Service(
            "C:\\Users\\bhavi\\Downloads\\chromedriver_win32\\chromedriver.exe")
        self.base_url = "https://www.theverge.com"

        result = requests.get(self.base_url)
        if result.status_code != 200:
            sys.exit("Website not accessible!")
        else:
            self.driver = webdriver.Chrome(service=s, options=option)
            self.driver.get(self.base_url)

        self.soup = BeautifulSoup(self.driver.page_source, "html.parser")

        # To convert the extracted data(theverge.html) into readable format
        # html = soup.prettify()

        # with open("theverge.html", "w") as theverge:
        #     for i in range(0, len(html)):
        #         try:
        #             theverge.write(html[i])
        #         except Exception:
        #             1 + 1

        self.conn = sqlite3.connect("theverge.db")
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS articles (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT, headline TEXT, author TEXT, date TEXT);"""
        )

        today = datetime.date.today().strftime("%d%m%Y")
        self.filename_csv = today + "_verge.csv"
        row = "id,url,headline,author,date"
        with open(self.filename_csv, "w", newline="") as theverge:
            try:
                theverge.write(row)
                theverge.write("\n")
            except Exception as e:
                print(e)

        self.pid = 0

    def save_article(self, url, headline, author, date):
        """Save an article in the database"""

        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE url=?", (url,))
        result = cursor.fetchone()
        if result:
            return
        q = f"INSERT INTO articles (url, headline, author, date) VALUES (?, ?, ?, ?)"
        self.conn.execute(q, (url, headline, author, date))
        self.conn.commit()

    def save_main_article(self):
        """Extract header article and save in db and CSV file"""

        div_tags = self.soup.find(
            "div",
            class_="relative border-b border-gray-31 pb-20 md:pl-80 lg:border-none lg:pl-[165px] -mt-20 sm:-mt-40",
        )

        headline = div_tags.find(
            "a",
            class_="group-hover:shadow-highlight-blurple",
        ).get_text(strip=True)

        link = div_tags.find(
            "a",
            class_="group-hover:shadow-highlight-blurple",
        ).get("href")

        author = div_tags.find(
            "a",
            class_="text-gray-31 hover:shadow-underline-inherit dark:text-franklin mr-8",
        ).get_text(strip=True)

        date = div_tags.find(
            "span", class_="text-gray-63 dark:text-gray-94").get_text()

        if "GMT" in date or "ago" in date:
            date = datetime.date.today().strftime("%Y/%m/%d")
        else:
            date = datetime.datetime.strptime(
                date, "%b %d").strftime("%Y/%m/%d")
            date = date.replace("1900", str(datetime.date.today().year))

        url = self.base_url + link

        row = f"{self.pid},{url},{headline},{author},{date}"
        with open(self.filename_csv, "a", newline="") as theverge:
            try:
                theverge.write(row)
                theverge.write("\n")
            except Exception as e:
                print(e)

        self.save_article(url, headline, author, date)

    def save_top_stories(self):
        """Extract top stories and save in db and CSV file"""

        div_tags = self.soup.find_all(
            "div",
            class_="max-w-content-block-standard md:w-content-block-compact md:max-w-content-block-compact lg:w-[240px] lg:max-w-[240px] lg:pr-10",
        )

        for div_tag in div_tags:
            headline = div_tag.find(
                "a",
                class_="group-hover:shadow-underline-franklin",
            ).get_text(strip=True)

            link = div_tag.find(
                "a",
                class_="group-hover:shadow-underline-franklin",
            ).get("href")

            author = div_tag.find(
                "a",
                class_="text-gray-31 hover:shadow-underline-inherit dark:text-franklin mr-8",
            ).get_text(strip=True)

            date = div_tag.find(
                "span", class_="text-gray-63 dark:text-gray-94"
            ).get_text()

            if "GMT" in date or "ago" in date:
                date = datetime.date.today().strftime("%Y/%m/%d")
            else:
                date = datetime.datetime.strptime(
                    date, "%b %d").strftime("%Y/%m/%d")
                date = date.replace("1900", str(datetime.date.today().year))

            url = self.base_url + link

            self.pid += 1
            row = f"{self.pid},{url},{headline},{author},{date}"
            with open(self.filename_csv, "a", newline="") as theverge:
                try:
                    theverge.write(row)
                    theverge.write("\n")
                except Exception as e:
                    print(e)

            self.save_article(url, headline, author, date)

    def save_other_content(self):
        """Extract other articles and save in db and CSV file"""

        div_tags = self.soup.find_all(
            "div",
            class_="max-w-content-block-mobile",
        )

        for div_tag in div_tags:
            headline = div_tag.find(
                "a",
                class_="after:absolute after:inset-0 group-hover:shadow-underline-blurple dark:group-hover:shadow-underline-franklin",
            ).get_text()

            if headline == "Advertiser Content":
                continue

            link = div_tag.find(
                "a",
                class_="after:absolute after:inset-0 group-hover:shadow-underline-blurple dark:group-hover:shadow-underline-franklin",
            ).get("href")

            a_author = div_tag.find(
                "div",
                class_="inline-block",
            )

            author = a_author.find('a').text

            date = div_tag.find(
                "span", class_="text-gray-63 dark:text-gray-94"
            ).get_text()

            if "GMT" in date or "ago" in date:
                date = datetime.date.today().strftime("%Y/%m/%d")
            else:
                date = datetime.datetime.strptime(
                    date, "%b %d").strftime("%Y/%m/%d")
                date = date.replace("1900", str(datetime.date.today().year))

            url = self.base_url + link

            self.pid += 1
            row = f"{self.pid},{url},{headline},{author},{date}"
            with open(self.filename_csv, "a", newline="") as theverge:
                try:
                    theverge.write(row)
                    theverge.write("\n")
                except Exception as e:
                    print(e)

            self.save_article(url, headline, author, date)
        self.conn.close()


if __name__ == '__main__':
    scrap_obj = TheVergeScrap()
    scrap_obj.save_main_article()
    scrap_obj.save_top_stories()
    scrap_obj.save_other_content()
