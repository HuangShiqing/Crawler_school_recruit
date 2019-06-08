import requests
from lxml import etree
from tqdm import tqdm
import csv


def get_one_page(url):
    """
    用requests库get爬取一个网页html源码
    """
    headers = {
        "User-Agent": "Mozilla/s.o(Macintosh Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"}
    respond = requests.get(url, headers=headers)
    if respond.status_code == 200:
        respond.encoding = respond.apparent_encoding
        return respond.text
    return None


def parse_first_page(url):
    """
    解析页面获得省份名和网址
    """
    respond = get_one_page(url)
    html = etree.HTML(respond, etree.HTMLParser())
    province_elements = html.xpath("//td/a")[36:67]

    provinces = list()
    urls = list()
    for i in range(len(province_elements)):
        province = province_elements[i].text[:-6]
        provinces.append(province)
        url = province_elements[i].xpath("@href")[0]
        urls.append(url)

    return provinces, urls


def parse_second_page(provinces, urls):
    """
    解析页面获得每个省各个学校的信息
    """
    school_inf = list()

    for i in tqdm(range(len(provinces)), desc="获取学校信息中: "):
        respond = get_one_page(urls[i])
        html = etree.HTML(respond, etree.HTMLParser())
        elements = html.xpath("//a[contains(@href,'cuabout.asp')]")
        for element in elements:
            school = element.text
            tail = element.tail
            tail = [inf for inf in tail.split('\u3000') if inf != '']
            department = tail[0]
            city = tail[1]
            education = tail[2]

            school_inf.append({'学校名': school, '城市': city,
                               '省份': provinces[i], '主管部门': department, '教育制': education})

    return school_inf


def save_csv(school_inf):
    """
    保存为csv文件
    """
    with open('school_list.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['省份', '学校名', '城市', '教育制', '主管部门'])
        for inf in tqdm(school_inf, desc="保存中: "):
            writer.writerow(
                [inf['省份'], inf['学校名'], inf['城市'], inf['教育制'], inf['主管部门']])


if __name__ == "__main__":
    url = "http://www.huaue.com/gxmd.htm"

    provinces, urls = parse_first_page(url)
    school_inf = parse_second_page(provinces, urls)
    save_csv(school_inf)
