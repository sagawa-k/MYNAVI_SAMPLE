import os
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import urllib.parse

LOG_FILE_PATH = "./log/log_{datetime}.log"
EXP_CSV_PATH="./exp_list_{search_keyword}_{datetime}.csv"
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))

### Chromeを起動する関数
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
    return Chrome(ChromeDriverManager().install(), options=options)

### ログファイル及びコンソール出力
def log(txt):
    now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

def find_table_target_word(th_elms, td_elms, target:str):
    # tableのthからtargetの文字列を探し一致する行のtdを返す
    for th_elm,td_elm in zip(th_elms,td_elms):
        if th_elm.text == target:
            return td_elm.text

def make_search_url(search_keyword:str):
     # キーワード調整
    adjust_search_keyword = " "
    for key in search_keyword.split():
        adjust_search_keyword += "kw{}_".format(key)
    adjust_search_keyword = adjust_search_keyword.rstrip("_").lstrip(" ")
    # エンコードurlを返す
    return  urllib.parse.quote(adjust_search_keyword)

### main処理
def main():
    log("処理開始")
    search_keyword = input("検索キーワードを入力してください")
    log("検索キーワード:{}".format(search_keyword))
    # driverを起動
    if os.name == 'nt': #Windows
        driver = set_driver(False)
    elif os.name == 'posix': #Mac
        driver = set_driver(False)

    # 検索URL作成
    url = "https://tenshoku.mynavi.jp/list/{0}".format(make_search_url(search_keyword))
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
    count = 0
    success = 0
    fail = 0
    # ページ終了まで繰り返し取得
    while True:
        try:
            # urlで直接検索した場合、2ページ目以降にポップアップが出る事があるため閉じる
            driver.execute_script('document.querySelector(".karte-close").click()')
        except:
            pass
        time.sleep(5)
        try:
            # 会社名を取得
            name_list = driver.find_elements_by_css_selector(".cassetteRecruit__heading .cassetteRecruit__name")
            # 給与を取得
            table_list = driver.find_elements_by_css_selector(".cassetteRecruit .tableCondition")
            annual_income_list = driver.find_elements_by_css_selector("table.tableCondition > tbody > tr:nth-child(4) > td")

            # 1ページ分繰り返し
            for name, income, table in zip(name_list, annual_income_list, table_list):
                # 給与をテーブルから探す
                annual_income = find_table_target_word(table.find_elements_by_tag_name("th"), table.find_elements_by_tag_name("td"), "給与")
                exp_name_list.append(name.text)
                exp_annual_income_list.append(annual_income)
                log(f"{count}件目成功 : {name.text}")
                success+=1
        except Exception as e:
            log(f"{count}件目失敗 : {name.text}")
            log(e)
            fail+=1
        
            driver.close()
        finally:
            # finallyは成功でもエラーでも必ず実行
            count+=1

        # 次のページボタンがあればクリックなければ終了
        next_page = driver.find_elements_by_class_name("iconFont--arrowLeft")
        if len(next_page) >=1:
            next_page_link = next_page[0].get_attribute("href")
            driver.get(next_page_link)
        else:
            log("最終ページです。終了します。")
            break

        # csv出力
        now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        df = pd.DataFrame({"企業名":exp_name_list, "給与":exp_annual_income_list})
        df.to_csv(EXP_CSV_PATH.format(search_keyword=search_keyword,datetime=
                                  now), encoding="utf-8-sig")
        log(f"処理完了 成功件数: {success} 件 / 失敗件数: {fail} 件")

# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()