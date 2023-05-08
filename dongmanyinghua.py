import requests
from pyquery import PyQuery as pq
from urllib.parse import urljoin
import pymongo

start_url = 'http://www.imomoe.live/'
PAGE = 3
DIQU = "%C8%D5%B1%BE"


# request头部
def scrape_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (HTML, like Gecko) '
                      'Chrome/97.0.4692.99 Safari/537.36 '
    }
    return headers


# 页面提取
def scrape_api(url):
    scrape_header = scrape_headers()
    response = requests.get(url, headers=scrape_header)

    response.encoding = 'gb2312'
    print(response.status_code)
    if response.status_code == 200:
        return response.text


# url页数
def scrape_page(page):
    scrape_url = f'{start_url}so.asp?page={page}&dq={DIQU}&pl=time'
    print(scrape_url)
    return scrape_api(scrape_url)


# url链接提取
def parse_index(html):
    doc = pq(html)
    scrape_hrefs = doc('#contrainer .pics ul li a')
    for scrape_href in scrape_hrefs.items():
        href = scrape_href.attr('href')
        detail_url = urljoin(start_url, href)
        print(detail_url)
        yield detail_url


# 详情内容提取
def detail_scrape(html):
    doc = pq(html)
    scrape_name = doc('body div h1 .names').text()
    return {
        'scrape_name': scrape_name
    }


# 页面提取拓展
def scrape_parse(url):
    return scrape_api(url)


# 数据保存
Webclient = pymongo.MongoClient('mongodb://localhost:27017')
mydb = Webclient['runoobdb']
collist = mydb['sites']


def save_data(data):
    collist.update_one(
        {
            'name': data.get('name')
        }, {
            '$set': data
        }
        , upsert=True)


# 主函数
def main():
    for page in range(1, PAGE + 1):
        scrape_html = scrape_page(page)
        scrape_urls = parse_index(scrape_html)
        print(scrape_urls)
        for scrape_url in scrape_urls:
            detail_html = scrape_parse(scrape_url)
            scrape_data = detail_scrape(detail_html)
            print(scrape_data)
            save_data(scrape_data)


if __name__ == '__main__':
    # 运行
    main()
