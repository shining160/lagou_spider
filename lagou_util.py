#!/user/bin/python3
# -*- encoding:utf-8 -*-

import random

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.lagou.com/shanghai/"
URL_PAGE_FILE = "../lagou/url_page_num.txt"
JOB_INFO = "jobs.txt"
ALREADY_URL_FILE = "../lagou/already_crawl_urls.txt"


def get_job_type_all_url():
    """
    获取拉勾上所有工作大类及分页数
    :param lagou_url:
    :param job_page_file:
    :return:
    """
    lagou_url = "https://www.lagou.com/"
    print("==> 抓取lagou网页job信息：", lagou_url)


    content = ""
    while content == "":
        content = send_request(lagou_url)
    soup = BeautifulSoup(content, "html.parser")
    tags = soup.find_all("div", class_="mainNavs")
    job_types = []
    for tag in tags:
        div_as = tag.find_all("a", class_="", attrs={"data-lg-tj-cid": "idnull"})
        for div_a in div_as:
            job = div_a.text
            url = div_a['href']
            pageNum = get_each_job_page_number(div_a['href'])
            print("job=", job, "url=", url, "pageNum=", pageNum)
            job_types.append((job, url, pageNum))
    return job_types

def get_each_job_page_number(job_url):
    """
    获取一个工作大类的分页数
    :param job_url: 岗位的url，例如：https://www.lagou.com/python/2/
    :return:
    """
    content = send_request(job_url)
    bs = BeautifulSoup(content, "html.parser")
    bs_spans = bs.select('.totalNum')
    num = ""
    if bs_spans is not None:
        num = bs_spans[0].text
    return num


def crawl_lagou_jobs_to_table(con, cursor, sql=""):
    """
    写入拉勾网上所有工作大类的url及网页数目
    :param sql:
    :param cursor:
    :param con:
    :return:
    """
    sql = "insert into dim_lagou(job_type, job_base_url, max_page_num) values (%s, %s, %s)"
    job_url_pages = get_job_type_all_url()
    print("==>", "提交数据库...")
    cursor.executemany(sql, job_url_pages)
    con.commit()
    print("==>", "提交成功！")



def read_job_and_page_from_table(cursor):
    """
    读取本地文件，查找目标url是否已记录
    :param cursor:
    """
    id_job_url_pages = []
    sql = "select id, job_type, job_base_url, max_page_num from dim_lagou"
    cursor.execute(sql)
    results = cursor.fetchall()
    for result in results:
        id_job_url_pages.append((result[0], result[1], result[2], result[3]))
    return id_job_url_pages

def read_page_to_fetch_from_table(cursor):
    """
    读取本地文件，查找目标url是否已记录
    :param cursor:
    """
    all_pages = []
    sql = "select id, page_url from lagou_page_fetched where is_fetched=0"
    cursor.execute(sql)
    results = cursor.fetchall()
    for result in results:
        all_pages.append([result[0], result[1]])
    return all_pages

def read_record_number_from_table(cursor):
    """
    读取本地文件，查找目标url是否已记录
    :param cursor:
    """
    sql = "select count(1) from lagou_page_fetched where is_fetched=0"
    cursor.execute(sql)
    record_num = cursor.fetchone()[0]
    return record_num

def send_request(url, proxy_list=[]):
    """
    使用代理，向目标url发起访问，
    :param url: 目标url
    :param proxy_list: 代理列表
    :return: 返回响应内容
    """
    if not proxy_list:
        proxy_list = [
            {"http": "http://124.88.67.81:80"},
            {"http": "http://124.88.67.82:80"},
            {"http": "http://124.88.67.83:80"},
            {"http": "http://124.88.67.84:80"},
            {"http": "http://124.88.67.85:80"}
        ]
    proxy = random.choice(proxy_list)

    headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT)'}
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    req = requests.get(url, headers=headers, proxies=proxy)
    req.encoding = "UTF-8"
    html = req.text
    return html



def crawl_proxy_ips_from_kuaidaili(number):
    """
    从快代理网站爬取一页代理地址，组成list返回
    :param number: 指定爬取的页数
    :return:
    """
    proxy_net_url = "https://www.kuaidaili.com/free/inha/"
    check_url = "https://www.ip.cn/"
    header = {
        "User-Agent": "'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36 "
    }
    proxy_ips = []
    proxy_page_url = proxy_net_url + str(number)
    print("爬取代理页：", proxy_page_url)
    # 爬取快代理网站
    try:
        response = requests.get(proxy_page_url)
        response.encoding = "UTF-8"
        html = response.text
    except Exception as e:
        print("访问快代理失败！")
    else:
        # print(html)
        content = BeautifulSoup(html, "html.parser")
        tr_divs = content.select("table.table tbody tr")
        tr_divs = [tr_div.text.split("\n") for tr_div in tr_divs]
        for i in range(len(tr_divs)):
            ip = tr_divs[i][1]
            port = tr_divs[i][2]
            ip_url_next = '://' + ip + ':' + port
            proxy = {'http': 'http' + ip_url_next, 'https': 'https' + ip_url_next}
            # 检查ip是否可用
            try:
                rq = requests.get(check_url, headers=header, proxies=proxy, timeout=15)
            except Exception as e:
                print("代理失败：", proxy)
                print(e)
            else:
                if rq.status_code == 200:
                    proxy_ips.append(proxy)
    return proxy_ips

def crawl_proxy_ips_from_jiangxianli(number):
    """
    从快代理网站爬取一页代理地址，组成list返回
    :param number: 指定爬取的页数
    :return:
    """
    proxy_net_url = "https://ip.jiangxianli.com/?page={}&country=中国".format(number)
    check_url = "https://www.ip.cn/"
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
    }
    proxy_ips = []
    print("爬取代理页：", proxy_net_url)
    # 爬取快代理网站
    try:
        response = requests.get(proxy_net_url)
        response.encoding = "UTF-8"
        html = response.text
    except Exception as e:
        print("访问快代理失败！")
    else:
        content = BeautifulSoup(html, "html.parser")
        tr_divs = content.select("table.layui-table tbody tr")
        tr_divs = [str(tr_div).strip("<tr><td>").split("</td><td>") for tr_div in tr_divs]
        for i in range(len(tr_divs)):
            ip = tr_divs[i][0]
            port = tr_divs[i][1]
            ip_url_next = '://' + ip + ':' + port
            proxy = {'http': 'http' + ip_url_next, 'https': 'https' + ip_url_next}
            # 检查ip是否可用
            try:
                rq = requests.get(check_url, headers=header, proxies=proxy, timeout=15)
            except Exception as e:
                # print("代理不可用：", proxy)
                ...
            else:
                if rq.status_code == 200:
                    proxy_ips.append(proxy)
                print("代理成功：", proxy)
    return proxy_ips






