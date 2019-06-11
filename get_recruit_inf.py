import csv
import requests
from lxml import etree
import re
from tqdm import tqdm
import numpy as np

from get_school_list import get_one_page


def get_school_inf(file_name, target_province=None):
    school_list = list()
    with open(file_name, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if target_province == None or row[0] in target_province:
                # school_list.append({'省份': row[0], '学校名': row[1], '城市': row[2],
                #                     '教育制': row[3], '主管部门': row[4]})
                school_list.append([row[0], row[1], row[2], row[3], row[4]])
    return school_list[1:] if target_province == None else school_list


def parse_first_page(url):
    """
    解析页面获得发布信息的学校
    """
    respond = get_one_page(url)
    html = etree.HTML(respond, etree.HTMLParser())
    next_page_url = html.xpath(
        "//a[contains(@href,'/list.php')]")[-1].xpath("@href")[0]

    recruit_list_date = html.xpath("//div[contains(@class,'newslist_date')]")
    recruit_list_text = html.xpath("//div[contains(@class,'newslist_text')]")

    titles = list()
    publish_times = list()
    urls = list()

    for i in range(len(recruit_list_date)):
        temp = recruit_list_text[i].xpath("div/a/b")
        if temp == []:
            temp = recruit_list_text[i].xpath("div/a")
        titles.append(temp[0].text)
        publish_times.append(recruit_list_date[i].xpath(
            "span")[0].text+'.'+recruit_list_date[i].xpath("em")[0].text[:-1])
        urls.append(recruit_list_text[i].xpath("div/a/@href")[0])
    return next_page_url, titles, urls, publish_times


def parse_second_page(url):
    respond = get_one_page(url)
    html = etree.HTML(respond, etree.HTMLParser())
    temp_elements = html.xpath("//span")

    pattern1 = re.compile('视觉传达')
    pattern2 = re.compile('广告设计')
    for temp_element in temp_elements:
        temp = temp_element.text
        if temp:  # 可能会是None
            require = ''.join(re.findall('[\u4e00-\u9fa5]', temp))
            if re.findall(pattern1, require) or re.findall(pattern2, require):
                return True
    return False


def filter_school(title):
    patterns = ['[\u4e00-\u9fa5]*?大学[\u4e00-\u9fa5]*?学院',
                '[\u4e00-\u9fa5]*?学院[\u4e00-\u9fa5]*?学院',
                '[\u4e00-\u9fa5]*?学院',
                '[\u4e00-\u9fa5]*?大学',
                '[\u4e00-\u9fa5]*?专科学校']

    school = None
    college = None

    for i, pattern in enumerate(patterns):
        if re.findall(pattern, title):
            result = re.findall(pattern, title)

            if i == 0:
                school = result[0].split('大学')[0]+'大学'
                college = result[0].split('大学')[1]
            elif i == 1:
                school = result[0].split('学院')[0]+'学院'
                college = result[0].split('学院')[1]+'学院'
            else:
                school = result[0]

            break
    return school, college


if __name__ == "__main__":
    school_inf = get_school_inf('school_list_new.csv',
                                target_province=['四川','浙江','江苏','重庆'])
    school_arry = np.array(school_inf)[:,1]

    target_urls = list()
    target_titles = list()

    root_url = 'http://m.gaoxiaojob.com/'
    next_page_url = 'list.php?tid=50&TotalResult=14377&PageNo=121'
    while next_page_url:
        next_page_url, titles, urls, publish_times = parse_first_page(
            root_url+next_page_url)
        print('parsing page: ',next_page_url.split('=')[-1])
        for i in tqdm(range(len(urls))):
            if parse_second_page(root_url+urls[i]):
                target_urls.append(urls[i])
                target_titles.append(titles[i])

                school_name,college_name = filter_school(titles[i])
                print(school_name,college_name, '\r\n')
                with open('no_filter.csv', 'a') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([school_name, college_name, root_url+urls[i]])
                
                if school_name in school_arry:
                    print('interesting', '\r\n')
                    with open('filter.csv', 'a') as csvfile:
                        writer = csv.writer(csvfile)
                        writer.writerow([school_name, college_name, root_url+urls[i]])
                

    exit()
