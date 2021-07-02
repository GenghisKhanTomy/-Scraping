"""
とあるサイトのデータのスクレイピング
会員サイトなので、HTML要素やまつわる変数名を変更
"""

# coding=utf8

import time, os, csv
import webdriver_manager.chrome

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from webdriver_manager.utils import chrome_version

#chromedriver.exeまでのpathを取得
def get_driver_path():
    webdriver_path = "win32までのパス"
    # chromeとdriverのバージョンが異なるとき
    if chrome_version() not in os.listdir(webdriver_path).pop():
        webdriver_manager.chrome.ChromeDriverManager().install()
    webdriver_path += os.listdir(webdriver_path).pop()
    webdriver_path += "\\chromedriver.exe"
    return webdriver_path

#ユーザ名をパスワードを入力し、文字列で保存
def input_user_password():
    tmp = input("ユーザ名 パスワード：").split()
    name = tmp[0]
    password = tmp[1]
    return name, password

#対象年月を入力
def input_target_year():
    temp = input("一覧表にする検索年を選んでください(未選択の場合は0を入力してください)：")
    if temp == "0":
        temp = "未選択"
    return temp

def input_ts_itemcode():
    print("PC系 => 1 ：漫画系 => 2 ： 料理系 => 3 ： ゲーム系 => 4 ： 選択しない => 0")
    item_data = input("数字を入力してください：")
    if item_data == "1":
        item_data, printed_item_cg = "P", "PC系"
    elif item_data == "2":
        item_data, printed_item_cg = "M", "漫画系"
    elif item_data == "3":
        item_data, printed_item_cg = "C", "料理系"
    elif item_data == "4":
        item_data, printed_item_cg = "G", "ゲーム系"
    else:
        item_data, printed_item_cg = "未選択", "未選択"
    return item_data, printed_item_cg

#テキストボックスにユーザ名をパスワードを入力し、送信
def page_login_need_name_and_password(target_browser, name, password):
    #ユーザ名を入力
    user_elements = target_browser.find_element_by_id("user_name")
    user_elements.clear()
    user_elements.send_keys(name)
    #パスワードを入力
    user_elements = target_browser.find_element_by_name("password")
    user_elements.clear()
    user_elements.send_keys(password)
    userdata_submit = target_browser.find_element_by_name("submit")
    time.sleep(2)
    userdata_submit.click()

def input_file_name_and_place(type, year):
    temp = input("出力するデータの場所を指定しますか？ -Yes => 1 -No => 2：")
    return_file_name_and_path = ""
    if temp == "1":
        return_file_name_and_path += input("主力先のフォルダ\"まで\"の場所を絶対パスで指定してください：")
    return_file_name_and_path += type + "_" + year + "_item_datas.csv"
    return return_file_name_and_path

def close_now_tab(driver, n):
    driver.switch_to.window(driver.window_handles[1])
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(n)

def write_csv(lists):
    with open(output_csv_file_name, 'a', encoding='utf-8') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerows(lists)

    #jsで書かれている商品を展開 (繰り返し処理開始)
def get_item_data(driver, id_name, type):
    lists = []
    for num in range(2, 22): #データ取り出し処理
        try:
            print(num - 1, end=" ")
            driver.find_element_by_id("詳細欄{:0>2}_botton".format(num)).click()
            time.sleep(1)
            list_item_datas = []
            for tg_id in id_name:
                # print(tg_id)
                driver.switch_to.window(driver.window_handles[1]) #商品詳細のページを選択
                textData = driver.find_element_by_id(tg_id).text
                list_item_datas.append(textData)
            if ((type in list_item_datas[2]) or type == "未選択") and (list_item_datas[3] != "" and list_item_datas[4] < 100):
                lists.append(list_item_datas)
            close_now_tab(driver, 1.5)
            time.sleep(1)
        except NoSuchElementException:
            break
    write_csv(lists)
    return lists


"""
Main処理部
"""
print("入力は半角を利用して下さい")
user_name, user_password = input_user_password()

target_yaer = input_target_year()
recommendation = input("推薦商品のみのデータを取得しますか？[y/n]")
ab_item = input("海外製品のみを取得しますか？[y/n]")
item_data, printed_item_cg = input_ts_itemcode()
fee = input("商品条件 ( n円以上)：")

target_login_url = "対象URLへのログインURL"
output_csv_file_name = input_file_name_and_place(item_data, target_yaer)
title_set = input("csvファイルの先頭行にカテゴリデータを書き込みますか？[y/n]")

jp_title = ["商品名", "商品コード", "販売価格", "生産数", "備考"]

targetdata_id_name = [
"id_item", #商品名名...0
"id_code", #商品コード
"id_fee", #販売価格
"id_maked", #生産数
"id_note" #備考
]


# 入力情報の確認
print("==================================================")
print("ユーザ名：", user_name)
print("対象商品カテゴリ：", printed_item_cg)
print("商品回収年度：", target_yaer)
if fee != "":
    try:
        temp = int(fee)
        if isinstance(temp, int):
            print(fee + "万円以上")
    except ValueError:
        pass
if recommendation == "y":
    print("推薦商品のみを獲得する")
if ab_item == "y":
    print("海外製品のみ取り出し")
print("出力先のファイル名；", output_csv_file_name)

"""スクレイピング開始"""
#Chrome起動
option = Options()
option.add_argument('--headless')
browser = webdriver.Chrome(executable_path = get_driver_path(), options=option)
browser.implicitly_wait(5)

#ログインページへ遷移
browser.get(target_login_url)
time.sleep(2)

#ユーザ名とパスワードに入力
page_login_need_name_and_password(browser, user_name, user_password)
time.sleep(2)

#商品のページまで遷移
element = browser.find_element_by_xpath("//*[@id=\"item_datas\"]/div[2]/table/tbody/tr[1]/td[4]/a")
element.click()
time.sleep(2)
element = browser.get("https://xxx.com/yyyy/zzzzz/item.aspx")

close_now_tab(browser, 2)

#商品での条件設定
dropdown_y = browser.find_element_by_id("query_年度")
select = Select(dropdown_y)
select.select_by_value(target_yaer)
if recommendation == "y":
    browser.find_element_by_id("query_推薦商品").click()

dropdown_j = browser.find_element_by_id("query_商品種別")
select = Select(dropdown_j)
select.select_by_value(item_data)

if fee != "":
    input_text_box_s = browser.find_element_by_id("query_代金")
    input_text_box_s.clear()
    input_text_box_s.send_keys(fee)

if ab_item == "y":
    browser.find_element_by_id("query_海外企業製").click()

browser.find_element_by_id("sbm_button").click()
time.sleep(2)

#=====================================================================================================

#商品データのスクレイピング開始
start_time = time.time()

#csvファイルにカテゴリデータを入力
with open(output_csv_file_name, 'w', encoding='utf-8') as file:
    pass

if title_set == "y":
    with open(output_csv_file_name, 'a', encoding='utf-8') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(jp_title)
print("csvファイル準備完了(以降終了まで生成した.csvファイルは開かないでください)")

# スクレイピングのメイン処理部
print("1 ページ目：")
lists = []
for i in range(2, 501):
    time.sleep(3)
    get_item_data(browser, targetdata_id_name, item_data)
    try:
        if i % 10 != 1:
            lists = browser.find_element_by_link_text("{}".format(i)).click()
        elif i == 11:
            lists = browser.find_element_by_link_text("...").click()
        else:
            lists = browser.find_elements_by_link_text("...")[1].click()#i % 10 == 1のページへの遷移はここ
        print(i, "ページ目：")
    except IndexError:
        break
    except NoSuchElementException:
        write_csv(lists)
        break

time.sleep(5)

finish_time = time.time()
detween_time = finish_time - start_time

print("処理時間 :", detween_time)
print("プログラム終了したので、ファイルを閉じます")
browser.quit()