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


def translate_to_chinese(text):
    if text == '':
        return ''
    else:
        return translator.translate(text, src='en', dest='zh-cn').text


def translate_to_korean(text):
    if text == '':
        return ''
    else:
        return translator.translate(text, src='en', dest='ko').text


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
        urllib.request.urlretrieve(img_url, new_filename)

        price = item_soup.find('input', {'id': 'it_price'}).get('value')
        prices.append(price)

        '''
        filename = img_url.split("/")[-1]
        new_filename = code + '.' + filename.split(".")[-1]
        urllib.request.urlretrieve(img_url, new_filename)

        img_urls.append('catalog/product/nippon/' + new_filename)

        name = product_meta_content.find('h3', {'class': 'product-title'}).get_text()
        names.append(name)
        chinese_name = translate_to_chinese(name)
        chinese_names.append(chinese_name)
        korean_name = translate_to_korean(name)
        korean_names.append(korean_name)

        detail = item.find('div', {'class': 'product_short_content'}).get_text()
        details.append(detail)
        chinese_detail = translate_to_chinese(detail)
        chinese_details.append(chinese_detail)
        korean_detail = translate_to_korean(detail)
        korean_details.append(korean_detail)



        category_names.append(get_category(key))

        print(
            new_filename + ', ' + code + ', ' + name + ', ' + chinese_name + ', ' + korean_name + ', ' + detail + ', ' + chinese_detail + ', ' + korean_detail + ', ' + price + ', ' + key)
'''


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
    start = 4000
    write_list = []
    for i in range(len(img_urls)):
        index = start + i
        line = [index, names[i], korean_names[i], chinese_names[i], category_names[i], '', codes[i], '',
                '', '', '', '', 10, codes[i], 'nippon', img_urls[i], 'yes', round(float(prices[i]) * 1.35, 1), 0,
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


def get_category(category):
    noodle = ['Noodle']
    for s in noodle:
        if s in category:
            return '43,34'

    candy = ['Confectionery']
    for s in candy:
        if s in category:
            return '50,34'

    seaweed = ['Seaweed']
    for s in seaweed:
        if s in category:
            return '53,34'

    frozen = ['Frozen']
    for s in frozen:
        if s in category:
            return '72,20'

    houseware = ['Houseware']
    for s in houseware:
        if s in category:
            return '78,33'

    drink = ['Beverage']
    for s in drink:
        if s in category:
            return '46,18'

    sauce = ['Sauce & Seasoning']
    for s in sauce:
        if s in category:
            return '38,34'

    liquor = ['Japanese Liquor']
    for s in liquor:
        if s in category:
            return '79,18'

    flour = ['Flour']
    for s in flour:
        if s in category:
            return '56,34'

    instant_food = ['Instant']
    for s in instant_food:
        if s in category:
            return '48,34'

    rice = ['Rice']
    for s in rice:
        if s in category:
            return '55,34'

    seasoning = ['Soup Stock']
    for s in seasoning:
        if s in category:
            return '38,34'

    other = ['Other']
    for s in other:
        if s in category:
            return '34'

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
        category_data = get_data_by_category(session, domain_name + value)
        parse_sub_category_data(session,
                                category_data, key, img_urls, codes, names, chinese_names, korean_names, details,
                                chinese_details,
                                korean_details, prices, category_names)
    save_data(img_urls, codes, names, chinese_names, korean_names, details, chinese_details, korean_details,
              prices, category_names)


if __name__ == '__main__':
    run()