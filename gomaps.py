import re

import requests
import http.cookiejar as cookielib
import xlwt
from bs4 import BeautifulSoup
from googletrans import Translator
import urllib.request

domain_name = 'http://www.gomaps.com.au'  # https://japanshopping.com.au nippon
translator = Translator()


def get_data_by_category(session, category_url):
    # headers 里面大小写均可
    headers = {'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"}
    data = session.get(category_url, headers=headers)
    # print(data.text)
    return data


def get_data_homepage(homepage_url):
    # headers 里面大小写均可
    headers = {
        'Host': "www.gomaps.com.au",
        'Origin': "http://www.gomaps.com.au",
        'Referer': "http://www.gomaps.com.au/bbs/login.php?url=%2Fshop%2F",
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
    }
    session = requests.Session()
    session.cookies = cookielib.LWPCookieJar(filename='cookies')
    # try:
    # session.cookies.load(ignore_discard=True)
    # except:
    # print('failed to load cookies')

    post_url = domain_name + '/bbs/login_check.php'
    post_data = {
        'url': '%2Fshop%2F',
        'mb_id': 'allanwang0201',
        'mb_password': '1380610Dh',
        'auto_login': 'on'
    }
    login_page = session.post(post_url, data=post_data, headers=headers)
    print(login_page.status_code)
    session.cookies.save()
    data = session.get(homepage_url, headers=headers)
    # print(data.text)
    return data, session


def translate_english_to_chinese(text):
    if text == '':
        return ''
    else:
        return translator.translate(text, src='en', dest='zh-cn').text


def translate_korean_to_chinese(text):
    if text == '':
        return ''
    else:
        return translator.translate(text, src='ko', dest='zh-cn').text


def translate_english_to_korean(text):
    if text == '':
        return ''
    else:
        return translator.translate(text, src='en', dest='ko').text


def translate_korean_to_english(text):
    if text == '':
        return ''
    else:
        return translator.translate(text, src='ko', dest='en').text

def hasNumbers(input_string):
  return any(char.isdigit() for char in input_string)

# 解析数据
def parse_sub_category_data(session, data, key, img_urls, codes, names, chinese_names, korean_names, details,
                            chinese_details,
                            korean_details, prices, category_names):
    soup = BeautifulSoup(data.text, 'lxml')
    # print(soup)
    products = soup.find('ul', {'class': 'product'})
    if not products:
        return
    products = products.find_all('li', {'class': 'product_li'})
    items = list(products)

    for item in items:
        item_url = item.find('div', {'class': 'product_img'}).find('a').get('href')

        item_soup = BeautifulSoup(session.get(item_url).text, 'lxml')
        img_url = item_soup.find('div', {'id': 'sit_pvi_big'}).find('img').get('src')

        code = item_url.split('=')[-1]
        codes.append(code)

        filename = img_url.split("/")[-1]
        new_filename = code + '.' + filename.split(".")[-1]
        # urllib.request.urlretrieve(img_url, new_filename)

        price = item_soup.find('input', {'id': 'it_price'}).get('value')
        if price.isdecimal():
            prices.append(price)
        else:
            prices.append('0')

        img_urls.append('catalog/product/gomaps/' + new_filename)

        title = item_soup.find('h2', {'id': 'sit_title'}).find(text=True, recursive=False)

        if len(re.findall(r'(.*?)\(.*?\)', title)) == 0:
            korean_name = title
            korean_names.append(korean_name)
            name = translate_korean_to_english(korean_name)
            names.append(name)
            chinese_name = translate_korean_to_chinese(korean_name)
            chinese_names.append(chinese_name)
        else:
            korean_name = re.sub("[\(\[].*?[\)\]]", "", title)
            korean_names.append(korean_name)
            name = title[title.rfind("(") + 1:title.rfind(")")]
            if hasNumbers(name) or len(name) < 3 or len(get_korean(name)) > 0 or name == 'WHOLE' or name == 'PET' or name == 'BQF':
                if len(get_korean(name)) > 0:
                    korean_name = korean_name + '(' + name + ')'
                name = translate_korean_to_english(korean_name)
                names.append(name)
                chinese_name = translate_korean_to_chinese(korean_name)
                chinese_names.append(chinese_name)
            else:
                names.append(name)
                chinese_name = translate_english_to_chinese(name)
                chinese_names.append(chinese_name)

        if item_soup.find('div', {'id': 'sit_inf_explan'}):
            description = item_soup.find('div', {'id': 'sit_inf_explan'}).get_text()
            if len(get_korean(description)) != 0:
                last_korean_letter = get_korean(description)[-1]
                last_korean_letter_index = description.rfind(last_korean_letter)
                korean_detail = description[0: last_korean_letter_index + 2]
                korean_details.append(korean_detail)

                chinese_detail = translate_korean_to_chinese(korean_detail)
                chinese_details.append(chinese_detail)

                detail = "".join(get_english(description)).strip()
                if len(detail.replace(' ', '').replace('kg', '').replace('g', '').replace('mg', '').replace('kcal', '')
                       .replace('m', '')) > 5:
                    detail = description[last_korean_letter_index + 2:]
                    details.append(detail)
                else:
                    detail = translate_korean_to_english(korean_detail)
                    details.append(detail)
            else:
                detail = ''
                details.append(detail)
                chinese_detail = ''
                chinese_details.append(chinese_detail)
                korean_detail = ''
                korean_details.append(korean_detail)
        else:
            detail = ''
            details.append(detail)
            chinese_detail = ''
            chinese_details.append(chinese_detail)
            korean_detail = ''
            korean_details.append(korean_detail)

        category_names.append(get_category(key))

        print(
            'catalog/product/gomaps/' + new_filename + '| ' + code + '| ' + name + '| ' + chinese_name + '| ' +
            korean_name + '{ ' + detail + '| ' +
            chinese_detail + '| ' + korean_detail + '}' + '$' + price + '| ' + key)


def get_korean(texts):
    # korean
    return re.findall("[\uac00-\ud7a3]", texts)


def get_chinese(texts):
    # chinese
    return re.findall("[\u4e00-\u9FFF ]", texts)


def get_english(texts):
    # chinese
    return re.findall("[a-zA-Z ]", texts)


def get_sub_category_pages(data):
    soup = BeautifulSoup(data.text, 'lxml')
    if soup.find('a', {'class': 'pg_end'}):
        pages = soup.find('a', {'class': 'pg_end'}).get('href').split('=')[-1]
    else:
        pages = 1
    return int(pages)


def parse_homepage_data(data):
    category_map = {}
    soup = BeautifulSoup(data.text, 'lxml')
    categories = soup.find_all('li', {'class': 'gnb_2dli'})

    for category in categories:
        category_name = category.find('a').get_text()
        category_url = category.find('a').get('href')
        category_map[category_name] = category_url
    return category_map


def append_to_list(write_list, pk, english, korean, chinese, image, category, code, brand, unit):
    app = [pk, english.replace(',', ''), "".join(korean).replace(',', ''), "".join(chinese).replace(',', ''),
           get_category(category), '', str(code), '', '', '', '', '', 10, str(code), "".join(brand).replace(',', ''),
           'catalog/product/korean/' + image, 'yes', str(unit * 1.35), 0, '2020-06-24 00:00:00',
           '2020-06-24 00:00:00', '2020-06-24', 0, 'g', 0, 0, 0, 'cm', 'true', 0, '', '', '', english.replace(',', ''),
           "".join(korean).replace(',', ''), "".join(chinese).replace(',', ''), '', '', '', '', '', '', 7, 0, '0:', '',
           '', '', '', 1, 'true', 1]
    write_list.append(app)


def save_data(img_urls, codes, names, chinese_names, korean_names, details, chinese_details, korean_details, prices,
              category_names):
    start = 6000
    write_list = []
    for i in range(len(img_urls)):
        code = codes[i]
        if code.isdecimal():
            code = int(code)
        index = start + i
        line = [index, names[i], korean_names[i], chinese_names[i], category_names[i], '', code, '',
                '', '', '', '', 10, code, 'gomaps', img_urls[i], 'yes', round(float(prices[i]) * 1.35, 1), 0,
                '2020-06-24 00:00:00',
                '2020-06-24 00:00:00', '2020-06-24', 0, 'g', 0, 0, 0, 'cm', 'true', 0, details[i], korean_details[i],
                chinese_details[i], names[i], korean_names[i], chinese_names[i],
                '', '', '', '', '', '', 7, 0, '0:', '', '', '', '', 1, 'true', 1]
        write_list.append(line)
    write_to_excel('result.xls', write_list)


def write_to_excel(file='result.xls', list=[]):
    book = xlwt.Workbook()  # 创建一个Excel
    sheet1 = book.add_sheet('hello')  #
    i = 0  # 行序号
    for app in list:  # 遍历list每一行
        j = 0  # 列序号
        for x in app:  # 遍历该行中的每个内容（也就是每一列的）
            sheet1.write(i, j, x)  # 在新sheet中的第i行第j列写入读取到的x值
            j = j + 1  # 列号递增
        i = i + 1  # 行号递增
    book.save(file)  # 创建保存文件


'''
'RICE', 'NOODLE', 'SOY SAUCE｜PASTE', 'SALT', 'OIL', 'SAUCE', 'SUGAR', 'SOURNESS', 'SEASONING', 'INSTANT FOOD', 
'FROZEN DUMPLING', 'FROZEN FOOD', 'SEAWEED', 'FROZEN SEAFOOD', 'RED PEPPER POWDER', 'PROCESSED FLOUR', 'GRAINS FLOUR',
'PREMIX', 'OTHER POWDER', 'POWDER', 'DRIED SEAFOOD', 'DRIED VEGETABLES', 'DRIED SEED', 'FROZEN SIDE DISH', 'PICKLED',
'KITCHEN', 'CONTAINER', 'OTHER SUNDRIE', 'CAN', 'BOTTLE', 'COFFEE / TEA', 'OTHER DRINK', 'VEGETABLE', 'FRUIT'])
'''


def get_category(category):
    noodle = ['NOODLE']
    for s in noodle:
        if s in category:
            return '43,34'

    seaweed = ['SEAWEED']
    for s in seaweed:
        if s in category:
            return '53,34'

    dry = ['DRIED SEAFOOD', 'DRIED VEGETABLES', 'DRIED SEED']
    for s in dry:
        if s in category:
            return '39,34'

    houseware = ['KITCHEN', 'CONTAINER', 'OTHER SUNDRIE']
    for s in houseware:
        if s in category:
            return '78,33'

    drink = ['CAN', 'BOTTLE', 'OTHER DRINK']
    for s in drink:
        if s in category:
            return '46,18'

    coffee_tea = ['COFFEE / TEA']
    for s in coffee_tea:
        if s in category:
            return '45,18'

    kimchi = ['PICKLED']
    for s in kimchi:
        if s in category:
            return '30,25'

    sauce = ['SOY SAUCE｜PASTE', 'SAUCE', 'SOURNESS', 'SEASONING']
    for s in sauce:
        if s in category:
            return '38,34'

    seasoning = ['SALT', 'OIL', 'SUGAR', 'RED PEPPER POWDER', 'PREMIX', 'OTHER POWDER', 'POWDER']
    for s in seasoning:
        if s in category:
            return '37,34'

    vege = ['VEGETABLE', 'FRUIT']
    for s in vege:
        if s in category:
            return '28,25'

    flour = ['PROCESSED FLOUR', 'GRAINS FLOUR']
    for s in flour:
        if s in category:
            return '56,34'

    instant_food = ['INSTANT FOOD']
    for s in instant_food:
        if s in category:
            return '48,34'

    rice = ['RICE']
    for s in rice:
        if s in category:
            return '55,34'

    frozen_dumpling = ['FROZEN DUMPLING']
    for s in frozen_dumpling:
        if s in category:
            return '71,20'

    frozen_fish = ['FROZEN SEAFOOD']
    for s in frozen_fish:
        if s in category:
            return '27,20'

    frozen_others = ['FROZEN FOOD', 'FROZEN SIDE DISH']
    for s in frozen_others:
        if s in category:
            return '72,20'

    return '34'


def run():
    img_urls = []
    codes = []
    names = []
    chinese_names = []
    korean_names = []
    details = []
    chinese_details = []
    korean_details = []
    prices = []
    category_names = []

    homepage_url = domain_name + '/shop/?locale=en_US'
    homepage_data, session = get_data_homepage(homepage_url)

    category_map = parse_homepage_data(homepage_data)

    for key, value in category_map.items():
        # category_data is fist page of that category
        category_data = get_data_by_category(session, domain_name + value)
        pages = get_sub_category_pages(category_data)
        for i in range(pages):
            category_data = get_data_by_category(session, domain_name + value + "&page=" + str(i + 1))
            parse_sub_category_data(session,
                                    category_data, key, img_urls, codes, names, chinese_names, korean_names, details,
                                    chinese_details,
                                    korean_details, prices, category_names)

    save_data(img_urls, codes, names, chinese_names, korean_names, details, chinese_details, korean_details,
              prices, category_names)


if __name__ == '__main__':
    run()
