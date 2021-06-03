import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse
import logging

# Chromeを起動する関数
def set_driver(headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定　
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付　与

    # ChromeのWebDriverオブジェクトを作成する。
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

# main処理

def main():
    # ログ出力
    logging.basicConfig(filename='./logger.log')
    formatter = '%(asctime)s:%(funcName)s:%(name)s:%(message)s'
    logging.basicConfig(format=formatter)

    search_keyword = input("検索キーワードを入力してください")

    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver(False)
    elif os.name == 'posix': #Mac
        driver = set_driver(False)

    # キーワード調整
    adjust_search_keyword = " "
    for key in search_keyword.split():
        adjust_search_keyword += "kw{}_".format(key)
    adjust_search_keyword = adjust_search_keyword.rstrip("_").lstrip(" ")
    # エンコード
    search_keyword_quote = urllib.parse.quote(adjust_search_keyword)
    # 検索URL作成
    url = "https://tenshoku.mynavi.jp/list/{0}".format(search_keyword_quote)
    # Webサイトを開く
    driver.get(url)
    time.sleep(5)
 
    try:
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
        time.sleep(5)
        # ポップアップを閉じる
        driver.execute_script('document.querySelector(".karte-close").click()')
    except:
        pass
    time.sleep(8)

    exp_name_list = []
    exp_annual_income_list = []
    result_list = []
    # ページ終了まで繰り返し取得
    while True:
        try:
            # ポップアップを閉じる
            driver.execute_script('document.querySelector(".karte-close").click()')
        except:
            pass
        time.sleep(5)
        try:
            # 検索結果ページの会社名を取得
            name_list = driver.find_elements_by_class_name("cassetteRecruit__name")
            # 検索結果ページの給与を取得
            annual_income_list = driver.find_elements_by_css_selector("table.tableCondition > tbody > tr:nth-child(4) > td")
            # 1ページ分繰り返し
            for index in range(len(name_list)):
                exp_name_list.append(name_list[index].text)
                exp_annual_income_list.append(annual_income_list[index].text)
                print("会社名：{0}, 給与：{1}".format(name_list[index].text, annual_income_list[index].text))

            #次のページのリンクを探す
            next = driver.find_element_by_css_selector("body > div.wrapper > div:nth-child(5) > form > div > nav:nth-child(51) > ul > li.pager__next > a.iconFont--arrowLeft")
            next.click()
        except:
            driver.close()

            # csv出力
            for index in range(len(exp_name_list)):
                result_list.append([exp_name_list[index], exp_annual_income_list[index]])
            df = pd.DataFrame(result_list, columns = ['会社名', '給与'])
            df.to_csv("./source.csv", encoding = "utf-8")
            break
        time.sleep(10)

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()