import requests
from bs4 import BeautifulSoup
import re


class UrlGetter:
    def __init__(self):
        pass
    
    def get_afp_url(self, page):
        return "http://www.afpbb.com/category/news?page={}".format(page)
    
    def get_reuters_url(self, page):
        return "https://jp.reuters.com/news/archive/topNews?view=page&page={}&pageSize=10".format(page)
    
    def get_cnn_url(self, category, page):
        return "https://www.cnn.co.jp/{}/{}/".format(category, page)
        
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
    
    def get_cnn_articles(self):
        results = []
        url_list = self.soup.find("ul", attrs={"class":"list-news-line"})
        return ["https://www.cnn.co.jp"+result['href'] for result in set(url_list.find_all("a"))]
    
    def get_reuters_articles(self):
        results = []
        for tmp_result in self.soup.find_all("div", attrs={"class":"story-content"}):
            results += tmp_result.find_all("a")
        return ["https://jp.reuters.com"+result['href'] for result in set(results)]
    
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
        title = self.soup.find("h1", {"class": "title"}).get_text()
        body = self.soup.find("div", {"class": "article-body"}).get_text()
        body = re.sub(r"【.+?】", "", body)
        body = re.sub(r"\(c\)AFP.*", "", body)
        body = body.replace("AFP","")
        day  = self.soup.find("span", {"class": "day"})
        day.find("span").extract()
        return title, body, day.get_text()
    
    def extract_reuters_article(self):
        article = self.soup.find("div", attrs={"id": self.target_url.split("-id")[1]})
        title = article.find("h1").get_text()
        tmp = article.find("h1")
        tmp.extract()
        tmp = article.find_all(re.compile(r"(div|p|span)"), {"class": re.compile(r"(channel_*|reading-time_*|attribution_*|trustBadge*)")})
        [t.extract() for t in tmp]
        tmp = article.find("div", {"class": re.compile(r"date_*")})
        day = tmp.get_text()
        tmp.extract()
        body = article.get_text()
        body = re.sub(r"［.+?ロイター］","", body)[2:]
        return title, body, day
    
    def extract_cnn_article(self):
        article = self.soup.find("article")
        title = article.find("h1").get_text()
        body = article.find("div", attrs={"id": "leaf-body"}).get_text().replace("（ＣＮＮ）","")
        day = article.find("div", {"class": "metadata-updatetime"}).get_text()
        return title, body, day
    
    def extract_article(self, site_type):
        title, body, day = getattr(self, "extract_{}_article".format(site_type))()
        title = title.replace("\n", " ").replace("\u3000", " ").replace("\r","").strip()
        body = body.replace("\n", " ").replace("\u3000", " ").replace("\r", "").strip()
        day = day.replace("\n", " ").replace("\u3000", " ").replace("\r", "").strip()
        return title, body, day


if __name__ == "__main__":
    from tqdm import tqdm
    import pandas as pd
    
    site_types = ["afp", "reuters", "cnn"]
    params = [
        [],
        [],
        ["world"]
    ]
    pages = [700, 2200, 300]
    
    urlgetter = UrlGetter()
    results = []

    for site_type, param, page_len in zip(site_types, params, pages):
        for i in tqdm(range(page_len)):
            base_url = urlgetter.get_url(site_type, *param, i+1)
            for target_url in ArticleGetter(base_url).get_articles(site_type):
                try:
                    title, body, day = ArticleExtractor(target_url).extract_article(site_type)
                    results.append({
                        "title": title,
                        "body": body,
                        "url": target_url,
                        "day": day
                    })
                except:
                    print(target_url)

    df = pd.DataFrame(results)
    df.to_csv("gathered_data.csv", index=False)
