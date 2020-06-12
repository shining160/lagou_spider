#!/user/bin/python3
# -*-coding:utf-8-*-

"""
针对拉勾网的爬虫程序
"""

import random
import threading
import time
import datetime
import pymysql
import requests
from queue import Queue
from threading import Thread
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from DBUtils.PooledDB import PooledDB

# 关闭安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


# 计算运行所需的时间
def run_time(func):
    def wrapper(*args, **kw):
        start = time.time()
        func(*args, **kw)
        end = time.time()
        print('running', end - start, 's')
    return wrapper


class LagouSpider:
    def __init__(self):
        self.target_url = "https://www.lagou.com/shanghai/"
        self.proxy_url = "https://www.kuaidaili.com/free/inha/"
        self.target_file = "../lagou/job_info.txt"
        self.thread_num = 6
        self.db_pool = self.mysql_connection()
        self.user_agent = [
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
            "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
            "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
            "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
            "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
            "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
            "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
            "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
            "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
            "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
            "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        ]
        self.pool = Queue()
        self.head_urls = Queue()
        self.jobs = []

    def set_proxy(self):
        """
        爬取西刺代理获取代理ip：port
        :return:
        """
        proxy_net = self.proxy_url + str(random.randint(1, 100))
        try:
            r = requests.get(proxy_net, headers={"user_agent": random.choice(self.user_agent)}, verify=False, timeout=1)
        except Exception as e:
            print("代理网站访问失败！")
        else:
            r.encoding = "UTF-8"
            if r.status_code == 200:
                content = BeautifulSoup(r.text, "html.parser")
                tr_divs = content.select("table.table tbody tr")
                tr_divs = [tr_div.text.split("\n") for tr_div in tr_divs]
                for tr_div in tr_divs:
                    ip = tr_div[1]
                    port = tr_div[2]
                    http = tr_div[4].lower()
                    ip_url_next = '://' + ip + ':' + port
                    proxy = {http: http + ip_url_next}
                    self.pool.put(proxy)

    def get_proxy(self):
        while self.pool.empty():
            self.set_proxy()
        proxy = self.pool.get()
        return proxy

    def send_request(self, url):
        """
        使用代理发送请求
        :param url:
        :return:
        """
        requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
        code = 0
        while code != 200:
            try:
                req = requests.get(url, headers={"User-Agent": random.choice(self.user_agent)}, proxies=self.get_proxy()
                                   , verify=False, timeout=15)
            except Exception:
                print("抓取网页{}异常".format(url))
            else:
                code = req.status_code
        req.encoding = "UTF-8"
        html = req.text

        return html

    def parse_head_page(self):
        """
        解析拉勾网站首页，获取职位关键词url
        :return:
        """
        t = threading.currentThread()
        print("当前线程：Thread id=%s，Thread name=%s，抓取url:%s" % (t.ident, t.getName(), self.target_url))
        content = self.send_request(self.target_url)
        soup = BeautifulSoup(content, "html.parser")
        tags = soup.find_all("div", class_="mainNavs")
        for tag in tags:
            div_as = tag.find_all("a", class_="", attrs={"data-lg-tj-cid": "idnull"})
            for div_a in div_as:
                job = div_a.text
                url = div_a['href']
                # print("job=", job, "url=", url)
                self.head_urls.put(url)
        print("拉勾网主要工作岗位类别抓取完毕！")

    def parse_details_page(self):
        while not self.head_urls.empty():
            self.parse_details(self.head_urls.get())

    def parse_details(self, url):
        """
        解析每个关键词下的所有职位信息
        :param url: 职位相关的url，如：https://www.lagou.com/shanghai-zhaopin/Python/
        :return:
        """
        t = threading.currentThread()
        print("当前线程：Thread id=%s，Thread name=%s，抓取url:%s" % (t.ident, t.getName(), url))

        job_details = []
        res = self.send_request(url)
        url_bs = BeautifulSoup(res, "html.parser")
        empty_judge = url_bs.select("ul.item_con_list div.empty_position div.txt")
        job_list = url_bs.select("ul.item_con_list li.con_list_item a.position_link h3")

        if empty_judge:
            print("暂时没有符合该搜索条件的职位,跳过")
        elif job_list:
            # 职位 jobs
            jobs = [job_h3.text for job_h3 in job_list]

            # 岗位关键词 keyword
            keyword = url_bs.select("div.keyword-wrapper input")
            keyword = keyword[0]["value"]

            # 岗位地点 addrs
            addrs = url_bs.select("span.add em")
            addrs = [addr.text for addr in addrs]

            # 公司 companys
            companys = url_bs.select("div.company_name a")
            companys = [c.text for c in companys]

            # 职位标签 true_tags
            tagss = url_bs.select("div.list_item_bot div.li_b_l")
            true_tags = []
            for tags in tagss:
                spans = tags.select("span")
                tag_content = ",".join([span.text for span in spans])  # str.join([]) 方法 将一个list中的元素以str来连接
                true_tags.append(tag_content)

            # 职位薪资 moneys
            moneys = url_bs.select("span.money")
            moneys = [money.text for money in moneys]

            # 经验要求 exps 和学历要求 edus
            exps_and_edus = url_bs.select("div.p_bot div.li_b_l")
            exps_and_edus = [ee.text.strip() for ee in exps_and_edus]  # strip()去掉开头和结尾的指定字符串
            edus = [edu.split("/")[1].strip() for edu in exps_and_edus]
            expss = [edu.split("/")[0].strip() for edu in exps_and_edus]
            exps = [exp.split("\n")[1].strip() for exp in expss]

            # 公司描述 types 和 公司融资级别 levels 和 公司规模 csizes
            types_and_levels = url_bs.select("div.industry")
            tl = [tal.text.strip() for tal in types_and_levels]
            types = []  # 公司描述，标签
            levels = []  # 公司融资级别
            csizes = []  # 公司规模
            for tals in tl:
                t_a_l = tals.split(" / ")
                if len(t_a_l) != 3:
                    types.append("无")
                    levels.append("无")
                    csizes.append("无")
                else:
                    types.append(t_a_l[0])
                    levels.append(t_a_l[1])
                    csizes.append(t_a_l[2])

            # 福利待遇 benefitss
            url_bs.select("div.list_item_bot div.li_b_r")
            benefitss = url_bs.select("div.list_item_bot div.li_b_r")
            benefitss = ["/".join(benefits.text.strip('“').strip('”').splitlines()) for benefits in benefitss]

            # 发布时间 pub_dates
            pub_dates = url_bs.select("span.format-time")
            pub_dates_format = []
            for pub_date in pub_dates:
                if pub_date.text.find("天前") > 0:
                    time_delta = int(pub_date.text.split("天前")[0])
                    format_time = (datetime.datetime.now() - datetime.timedelta(days=time_delta)).strftime("%Y-%m-%d")
                elif pub_date.text.find(":") > 0:
                    format_time = (datetime.datetime.now()).strftime("%Y-%m-%d")
                else:
                    format_time = pub_date.text
                pub_dates_format.append(format_time)

            # 取出的值：jobs  addrs  companys  true_tags  moneys  edus  exps types  levels  csizes benefitss pub_dates
            for i in range(len(jobs)):
                record = (keyword, jobs[i], addrs[i], companys[i], true_tags[i], moneys[i], edus[i], exps[i], types[i],
                          levels[i], csizes[i], benefitss[i], pub_dates_format[i])
                # self.jobs.append("^".join(record) + "\n")
                job_details.append(record)
            self.insert_table(job_details)

            div_as = url_bs.select("div.pager_container a")
            for a in div_as:
                if a.text == "下一页" and a["href"].startswith("http"):
                    next_page = a['href']
                    self.parse_details(next_page)
        else:
            print("本次没有获得job信息, 重试！")
            time.sleep(15)
            self.parse_details(url)

    def create_table(self):
        con = self.db_pool.connection()
        cur = con.cursor()
        # sql1 = "DROP TABLE IF EXISTS lagou_shanghai"
        sql2 = """
            CREATE TABLE IF NOT EXISTS lagou_shanghai (
                id int(11) NOT NULL AUTO_INCREMENT,
                t_keyword varchar(255) DEFAULT NULL COMMENT '职位关键字',
                    t_job varchar(255) DEFAULT NULL COMMENT '职位名称',
                t_addr varchar(255) DEFAULT NULL COMMENT '企业地址',
                t_com varchar(255) DEFAULT NULL COMMENT '企业名称',
                t_tag varchar(255) DEFAULT NULL COMMENT '企业标签',
                t_money varchar(255) DEFAULT NULL COMMENT '薪资待遇',
                t_edu varchar(255) DEFAULT NULL COMMENT '学历要求',
                t_exp varchar(255) DEFAULT NULL COMMENT '工作经验要求',
                t_type varchar(255) DEFAULT NULL COMMENT '企业类型',
                t_level varchar(255) DEFAULT NULL COMMENT '企业融资情况',
                t_csize varchar(255) DEFAULT NULL COMMENT '企业规模',
                t_benefit varchar(255) DEFAULT NULL COMMENT '福利待遇',
                t_pubdate varchar(255) DEFAULT NULL COMMENT '发布时间',
                PRIMARY KEY (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
        """
        try:
            # cur.execute(sql1)
            cur.execute(sql2)
            con.commit()
        except Exception as e:
            con.rollback()
            print("Error:写入数据库异常!", e)
        finally:
            cur.close()
            con.close()

    def insert_table(self, records):
        sql = "insert into lagou_shanghai(t_keyword,t_job,t_addr,t_com,t_tag,t_money,t_edu,t_exp,t_type,t_level,t_csize,t_benefit,t_pubdate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        con = self.db_pool.connection()
        cur = con.cursor()
        try:
            cur.executemany(sql, records)
            con.commit()
        except Exception as e:
            con.rollback()
            print("Error:写入数据库异常!", e)
        finally:
            cur.close()
            con.close()

    def mysql_connection(self):
        """
        数据库连接池
        :return:
        """
        pool = PooledDB(
            pymysql,
            self.thread_num,  # 最大连接数，设置为线程数一致
            host='localhost',
            user='root',
            port=3306,
            passwd='root',
            db='spider',
            use_unicode=True)
        return pool

    @run_time
    def main(self):
        self.create_table()

        ths = []
        th1 = Thread(target=self.parse_head_page)
        # th1.setDaemon(True)
        th1.start()
        ths.append(th1)
        time.sleep(5)

        for _ in range(self.thread_num):
            th = Thread(target=self.parse_details_page)
            th.setDaemon(True)
            th.start()
            ths.append(th)

        for th in ths:
            # 等待线程终止
            th.join()

        # with open(self.target_file, "a+", encoding="utf-8") as fo:
        #     fo.write("".join(self.jobs))


if __name__ == "__main__":
    spider = LagouSpider()
    spider.main()



