import requests
import re
import pandas as pd
import pymp
from tqdm import tqdm
from urllib.parse import quote 
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from sklearn.preprocessing import MinMaxScaler


def execute(queries, categories, keywords, target_names, executable_path, retry_size=20):
    driver = build_driver(executable_path)
    df = download_data(driver, queries, categories, keywords, target_names, retry_size)
    model, X, _queries = minmax_data(df, target_names)
    return model, X, _queries, df


def build_driver(executable_path):
    options = Options()
    options.binary_location = '/usr/bin/chromium-browser'
    options.add_argument('--headless')
    options.add_argument('--window-size=1280,1024')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(executable_path=executable_path, chrome_options=options)


def get_result(driver, query, keyword=None):
    url = "http://www.gibiru.com/?q={}"
    if keyword is None:
        q = quote(query)
    else:
        q = '+'.join([quote(query), 'AND', quote(keyword)])
    driver.get(url.format(q))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return int(re.sub(r'.+? (.+?) .+', r'\1', soup.find("td", {'class': "gsc-result-info-container"}).get_text()).replace(",",""))


def solve_value(tmp_value, keyword, driver, query, retry_size=5):
    for i in range(retry_size):
        try:
            result = get_result(driver, query, keyword)
            tmp_value += result
            break
        except Exception as e:
            continue
        print(query, keyword)
        return False
    return tmp_value


def download_data(driver, queries, categories, keywords, target_names, retry_size=20):
    results = []
    base = []
    for query in queries:
        row = [query]
        b = None
        for i in range(retry_size):
            try:
                b = get_result(driver, query)
                base.append((query, b))
                break
            except:
                continue
            print(query)
        if b is None:
            continue
        for category in tqdm(categories):
            tmp_value = 0
            for keyword in keywords[category]:
                tmp_value = solve_value(tmp_value, keyword, driver, query)
            row.append(float(tmp_value)/float(len(keywords[category])))
        assert len(row) == len(categories)+1
        results.append(row)
    return pd.merge(
        pd.DataFrame(results, columns=target_names).drop_duplicates(),
        pd.DataFrame(base, columns=[target_names[0], "base_count"])
    )


def minmax_data(df, target_names, base_column="base_count"):
    queries = df[target_names[0]]
    X = df[target_names[1:]]
    for col in target_names[1:]:
        X[col] = X[col]/df[base_column]
    model = MinMaxScaler().fit(X)
    X_fixed = model.transform(X)
    return model, X_fixed, queries


def plot(X, queries, keywords, num):
    try:
        plt.title(queries[num])
        plt.pie(X[num], labels=keywords)
        return True
    except:
        return False