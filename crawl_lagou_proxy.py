#!/user/bin/python3
# _*_ encoding:utf-8 _*_

"""
针对拉勾网的爬虫程序
"""
import time
import pymysql

from bs4 import BeautifulSoup
from lagou_spider import lagou_util

BASE_URL = "https://www.lagou.com/shanghai/"
URL_PAGE_FILE = "../lagou/url_page_num.txt"
JOB_INFO = "jobs.txt"
ALREADY_URL_FILE = "../lagou/already_crawl_urls.txt"



def crawl_per_page(url, page_id, con, cursor, proxy_ips={}):
    """
    拉勾网 爬取一页
    :param page_id:
    :param url: 岗位页面的url，如
        https://www.lagou.com/zhaopin/Python/2/
    :param proxy_ips: 代理列表
    :param con: 数据库连接对象
    :param cursor: 数据库指针
    :param sql: 插入岗位信息的sql
    :return:
    """
    status = 0
    sql1 = "insert into lagou ( t_page_id, t_job, t_addr, t_com, t_tag, t_money, t_edu, t_exp, t_type, t_level, t_csize, " \
           "t_benefit, t_pubdate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
    sql2 = "update lagou_page_fetched set is_fetched=1 where id={}".format(page_id)
    try:
        # 发送请求
        response = lagou_util.send_request(url, proxy_ips)
        url_bs = BeautifulSoup(response, "html.parser")
    except Exception as e:
        print("异常", e)
        status = 0    # TO_DO: 2
        return status
    else:
        # 正常处理逻辑
        job_list = url_bs.select("ul.item_con_list li.con_list_item a.position_link h3")
        # 工作岗位 jobs
        jobs = [job_h3.text for job_h3 in job_list]
        # print(jobs)
        if len(jobs) == 0:
            status = 3
            # print(response)
            return status

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
        pub_dates = [pub_date.text for pub_date in pub_dates]

        write_content = ""
        records = []
        # 取出的值：jobs  addrs  companys  true_tags  moneys  edus  exps types  levels  csizes benefitss pub_dates
        for i in range(len(jobs)):
            record = [str(page_id), jobs[i], addrs[i], companys[i], true_tags[i], moneys[i], edus[i], exps[i], types[i],
                      levels[i], csizes[i], benefitss[i], pub_dates[i]]
            records.append(record)
        try:
            cursor.executemany(sql1, records)
            cursor.execute(sql2)
            con.commit()
        except Exception as e:
            print("Error:写入数据库异常!", e)
            con.rollback()
            status = 4
            return status
    # 返回状态代码
    print("抓取完毕：", url)
    return status



def start_crawl_all_lagou_data(con, cursor, id_pages):
    """
    开始抓取拉勾所有的岗位详细数据
    :param con: 数据库连接对象
    :param cursor: 数据库指针
    :param all_page_urls: 所有岗位页面的url
    :return:
    """
    print("开始抓取拉勾数据...")
    cnt, all_num = 0, len(id_pages)
    for id_page in id_pages:
        page_id = id_page[0]
        page_url = id_page[1]
        print("剩余待抓取网页数目:{0}，当前抓取url:{1}".format(all_num - cnt, page_url))
        status = crawl_per_page(page_url, page_id, con, cursor)
        while status > 0:
            print("本次未抓取到网页内容，返回代码：", status)
            time.sleep(12)
            status = crawl_per_page(page_url, page_id, con, cursor)
        cnt += 1
        time.sleep(1)


def start():
    """
    启动方法
    :return: 无返回（方法执行，代表开始执行抓取）
    """
    # 数据库连接相关
    con = pymysql.connect(host="localhost", user="root", password="root", database="spider", charset='utf8', port=3306)
    cursor = con.cursor()
    sql = "insert into lagou_page_fetched(job_id, page_url, is_fetched) values (%s, %s, %s) "
    id_job_url_pages = lagou_util.read_job_and_page_from_table(cursor)

    # 判断，表中没有职位大类信息时抓取
    while id_job_url_pages.__len__() == 0:
        lagou_util.crawl_lagou_jobs_to_table(con, cursor)
        id_job_url_pages = lagou_util.read_job_and_page_from_table(cursor)

    # 判断，表中没有职位的详细url时抓取
    page_num = lagou_util.read_record_number_from_table(cursor)
    while page_num == 0:
        # 所有的URL（包含所有岗位对应每一页的URL）
        job_all_urls = []
        for one in id_job_url_pages:
            for i in range(int(one[3])):
                job_all_urls.append((one[0], one[2] + str(i + 1) + "/", 0))
        cursor.executemany(sql, job_all_urls)
        con.commit()
        page_num = lagou_util.read_record_number_from_table(cursor)

    # 从表中获取剩余要抓取的job url
    id_pages = lagou_util.read_page_to_fetch_from_table(cursor)

    # 开始抓取
    start_crawl_all_lagou_data(con, cursor, id_pages)
    con.close()
    print("抓取拉勾数据完毕！")



if __name__ == "__main__":
    """
    程序执行入口：启动抓取
    """
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    start()
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))