import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm


class UrlGetter:
    def __init__(self):
        pass
    
    def get_afp_url(self, page):
        return "http://www.afpbb.com/category/news?page={}".format(page)
        
    def get_url(self, site_type, *params):
        return getattr(self, "get_{}_url".format(site_type))(*params)


class ArticleGetter:
    def __init__(self, base_url):
        self.base_url = base_url
        r = requests.get(base_url)
        self.soup = BeautifulSoup(r.content, "html.parser")
    
    def get_afp_articles(self):
        ul = self.soup.find("ul", {"id": "tab-latest"})
        return list(set([result['href'] for result in ul.find_all("a")]))
    
    def get_articles(self, site_type):
        return getattr(self, "get_{}_articles".format(site_type))()


class ArticleExtractor:
    def __init__(self, target_url):
        self.target_url = target_url
        r = requests.get(target_url)
        self.soup = BeautifulSoup(r.content, "html.parser")
        [s.extract() for s in self.soup('script')]
        [s.extract() for s in self.soup('link')]
        
    def extract_afp_article(self):
        try:
            title = self.soup.find("h1", {"class": "title"}).get_text()
        except:
            title = ""

        try:
            body = self.soup.find("div", {"class": "article-body"}).get_text()
            body = re.sub(r"【.+?】", "", body)
            body = re.sub(r"\(c\)AFP.*", "", body)
            body = body.replace("AFP","")
        except:
            body = ""

        try:
            day  = self.soup.find("span", {"class": "day"})
            if day is None:
                day = ""
            else:
                day.find("span").extract()
                day = day.get_text()
        except:
            day = ""
        
        return title, body, day
    
    def extract_article(self, site_type):
        title, body, day = getattr(self, "extract_{}_article".format(site_type))()
        title = title.replace("\n", " ").replace("\u3000", " ").replace("\r","").strip()
        body = body.replace("\n", " ").replace("\u3000", " ").replace("\r", "").strip()
        day = day.replace("\n", " ").replace("\u3000", " ").replace("\r", "").strip()
        return title, body, day
    

def run():
    site_type = "afp"
    urlgetter = UrlGetter()
    results = []
    for i in tqdm(range(3850)):
        base_url = urlgetter.get_url(site_type, i+1)
        for target_url in ArticleGetter(base_url).get_articles(site_type):
            title, body, day = ArticleExtractor(target_url).extract_article(site_type)
            results.append({
                "title": title,
                "body": body,
                "url": target_url,
                "day": day
            })
    return pd.DataFrame(results)


if __name__ == "__main__":
    run().to_csv("afp.csv", index=False)
    
    
