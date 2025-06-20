import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import os
from PIL import Image # Pillowをインポート (フルページスクリーンショット結合用)
from datetime import datetime # タイムスタンプ用
from pathlib import Path

class WebTestAutomation:
    def __init__(self, browser='chrome', screenshot_dir='screenshots', log_filepath='test_log.csv'):
        """
        WebDriverを初期化します。

        Args:
            browser (str): 使用するブラウザ ('chrome' または 'firefox')。
            screenshot_dir (str): スクリーンショットの保存先ディレクトリ。
            log_filepath (str): ログを保存するCSVファイルのパス。
        """
        self.log_filepath = log_filepath
        self._initialize_log_file() # ログファイルを初期化

        if browser.lower() == 'chrome':
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            chrome_options = ChromeOptions()
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.driver = webdriver.Chrome(options=chrome_options)
            
        elif browser.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        else:
            self._log("ERROR", f"サポートされていないブラウザです。'chrome' または 'firefox' を指定してください: {browser}")
            raise ValueError(f"サポートされていないブラウザです。'chrome' または 'firefox' を指定してください。")
        
        self.screenshot_dir = screenshot_dir
        os.makedirs(self.screenshot_dir, exist_ok=True)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.maximize_window()
        time.sleep(0.5)

    def _initialize_log_file(self):
        """ログファイルを初期化し、ヘッダーを書き込みます。"""
        with open(self.log_filepath, 'w', encoding='sjis', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['タイムスタンプ', 'レベル', 'メッセージ'])

    def _log(self, level, message):
        """
        指定されたレベルとメッセージでログを出力します。

        Args:
            level (str): ログレベル (例: "INFO", "ERROR")。
            message (str): ログメッセージ。
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ミリ秒まで
        log_entry = [timestamp, level, message]
        with open(self.log_filepath, 'a', encoding='sjis', newline='') as f:
            writer = csv.writer(f)
            # writer = csv.writer(f, quoting=csv.QUOTE_NONE, escapechar='\\')
            writer.writerow(log_entry)
        # コンソールにも出力 (デバッグ用、不要ならコメントアウト)
        print(f"[{timestamp}] [{level}] {message}")

    def _get_element(self, selector_type, selector_value, timeout=10):
        """
        指定したセレクタで要素を取得します。見つからない場合はエラーを発生させます。
        
        Args:
            selector_type (str): セレクタのタイプ (id, name, class_name, xpath, css_selector, link_text, partial_link_text, tag_name)。
            selector_value (str): セレクタの値。
            timeout (int): 要素が見つかるまでの最大待機時間（秒）。

        Returns:
            WebElement: 見つかった要素。

        Raises:
            NoSuchElementException: 指定された要素が見つからない場合。
        """
        by_strategy = {
            'id': By.ID,
            'name': By.NAME,
            'class_name': By.CLASS_NAME,
            'xpath': By.XPATH,
            'css_selector': By.CSS_SELECTOR,
            'link_text': By.LINK_TEXT,
            'partial_link_text': By.PARTIAL_LINK_TEXT,
            'tag_name': By.TAG_NAME
        }
        
        if selector_type.lower() not in by_strategy:
            self._log("ERROR", f"無効なセレクタタイプです: {selector_type}")
            raise ValueError(f"無効なセレクタタイプです: {selector_type}")

        try:
            element = self.wait.until(
                EC.visibility_of_element_located((by_strategy[selector_type.lower()], selector_value))
            )
            return element
        except TimeoutException:
            msg = f"指定された要素が見つかりません: タイプ='{selector_type}', 値='{selector_value}' (タイムアウト)"
            self._log("ERROR", msg)
            raise NoSuchElementException(msg)

    def navigate_to_url(self, url, wait_time=0):
        """
        指定されたURLに遷移します。

        Args:
            url (str): 遷移先のURL。
            wait_time (int): ページ遷移後に待機する時間（秒）。
        """
        self._log("INFO", f"URLに遷移中: {url}")
        self.driver.get(url)
        if wait_time > 0:
            self._log("INFO", f"ページ遷移後 {wait_time} 秒待機中...")
            time.sleep(wait_time)

    def input_value(self, selector_type, selector_value, value):
        """
        指定した場所（要素）に値を入力します。

        Args:
            selector_type (str): セレクタのタイプ。
            selector_value (str): セレクタの値。
            value (str): 入力する値。

        Raises:
            NoSuchElementException: 指定された要素が見つからない場合。
        """
        element = self._get_element(selector_type, selector_value)
        self._log("INFO", f"'{selector_value}' に値 '{value}' を入力中 (タイプ: {selector_type})")
        element.clear()
        element.send_keys(value)

    def click_element(self, selector_type, selector_value):
        """
        指定した場所（要素）をクリックします。

        Args:
            selector_type (str): セレクタのタイプ。
            selector_value (str): セレクタの値。

        Raises:
            NoSuchElementException: 指定された要素が見つからない場合。
        """
        element = self._get_element(selector_type, selector_value)
        self._log("INFO", f"'{selector_value}' をクリック中 (タイプ: {selector_type})")
        element.click()

    def take_screenshot(self, filename, remark="", full_page=False):
        """
        画面のスクリーンショットを撮影します。

        Args:
            filename (str): 保存するファイル名 (例: "login_page.png")。
            remark (str): スクリーンショットに関する備考。
            full_page (bool): 画面全体を撮影するかどうか (True: 全体, False: 表示領域のみ)。
        """
        filepath = os.path.join(self.screenshot_dir, filename)
        
        log_msg = f"スクリーンショットを保存中: {filepath} (備考: {remark}, 全画面: {full_page})"
        self._log("INFO", log_msg)
        self._log("IMG", f"![{filepath}]({filepath})")  # Markdown形式で画像リンクをログに出力
        self._log("IMG", f'<a src="{filepath}" alt="{filepath}"')  # Markdown形式で画像リンクをログに出力

        if full_page:
            if self.driver.name == 'firefox':
                self.driver.save_full_page_screenshot(filepath)
            elif self.driver.name == 'chrome':
                try:
                    original_window_size = self.driver.get_window_size()
                    original_scroll_position = self.driver.execute_script("return window.pageYOffset;")

                    total_width = max(self.driver.execute_script("return document.body.scrollWidth"),
                                      self.driver.execute_script("return document.documentElement.scrollWidth"))
                    total_height = max(self.driver.execute_script("return document.body.scrollHeight"),
                                       self.driver.execute_script("return document.documentElement.scrollHeight"))

                    viewport_width = self.driver.execute_script("return document.body.clientWidth")
                    viewport_height = self.driver.execute_script("return window.innerHeight")

                    # self.driver.set_window_size(total_width, viewport_height)
                    time.sleep(1) 

                    screenshots = []
                    current_scroll_y = 0

                    while current_scroll_y < total_height:
                        temp_screenshot_path = os.path.join(self.screenshot_dir, f"temp_screenshot_{current_scroll_y}.png")
                        self.driver.save_screenshot(temp_screenshot_path)
                        screenshots.append((temp_screenshot_path, current_scroll_y))

                        scroll_amount = viewport_height - 10 # 10ピクセル重複させる例

                        current_scroll_y += scroll_amount
                        
                        if current_scroll_y < total_height:
                            self.driver.execute_script(f"window.scrollTo(0, {current_scroll_y});")
                            time.sleep(1.0) 

                    stitched_image = Image.new('RGB', (total_width, total_height))
                    for img_path, scroll_y in screenshots:
                        try:
                            img = Image.open(img_path)
                            stitched_image.paste(img, (0, scroll_y)) 
                        except Exception as e:
                            self._log("ERROR", f"画像ファイルの読み込みまたは結合中にエラーが発生しました: {e}")
                        finally:
                            if os.path.exists(img_path):
                                os.remove(img_path)

                    stitched_image.save(filepath)
                    self._log("INFO", f"フルページスクリーンショットを結合して保存しました: {filepath}")

                except Exception as e:
                    self._log("ERROR", f"フルページスクリーンショット（JavaScriptスクロール）の撮影中にエラーが発生しました: {e}")
                    self._log("INFO", "表示領域のみのスクリーンショットを保存します。")
                    self.driver.save_screenshot(filepath)
                finally:
                    self.driver.set_window_size(original_window_size['width'], original_window_size['height'])
                    self.driver.execute_script(f"window.scrollTo(0, {original_scroll_position});")
                    time.sleep(0.5)

            else:
                self._log("INFO", f"フルページスクリーンショットは現在のブラウザではサポートされていません。表示領域のみを保存します。")
                self.driver.save_screenshot(filepath)
        else:
            self.driver.save_screenshot(filepath)

    def log_content(self, selector_type, selector_value, content_type, remark=""):
        """
        指定されたセレクタの要素のテキスト内容または属性値をログに出力します。

        Args:
            selector_type (str): セレクタのタイプ。
            selector_value (str): セレクタの値。
            content_type (str): 取得したい内容の種類 (text, value, または属性名)。
            remark (str): ログに対する備考。
        """
        try:
            element = self._get_element(selector_type, selector_value)
            content = None
            if content_type.lower() == 'text':
                content = element.text
            elif content_type.lower() == 'value':
                content = element.get_attribute('value')
            else:
                content = element.get_attribute('text')
            
            log_msgs = [f"要素内容ログ: タイプ='{selector_type}'", f"値='{selector_value}'", f"取得内容='{content_type}'", f"結果='{content}'"]
            if remark:
                log_msgs.append(f"備考: {remark}")
            for log_msg in log_msgs:
                self._log("INFO", log_msg)

        except NoSuchElementException:
            self._log("ERROR", f"要素内容ログ失敗: 指定された要素が見つかりません - タイプ='{selector_type}', 値='{selector_value}'")
        except Exception as e:
            self._log("ERROR", f"要素内容ログ中に予期せぬエラーが発生しました: {e} (タイプ='{selector_type}', 値='{selector_value}')")
    def log_remark(self, remark=""):
        """
        指定されたテキスト内容をログに出力します。
            remark (str): ログに対する備考。
        """
        self._log("TXT", remark)


    def execute_commands_from_csv(self, csv_filepath):
        """
        CSVファイルからコマンドを読み込み、実行します。

        Args:
            csv_filepath (str): コマンドが記述されたCSVファイルのパス。
        """
        self._log("INFO", f"CSVファイル '{csv_filepath}' からコマンドの実行を開始します。")
        with open(csv_filepath, 'r', encoding='sjis') as f:
            reader = csv.reader(f)
            header = next(reader) # ヘッダーを読み飛ばす

            for i, row in enumerate(reader):
                command = row[0].strip().lower()
                selector_type = row[1].strip() if len(row) > 1 else ''
                selector_value = row[2].strip() if len(row) > 2 else ''
                value_or_path = row[3].strip() if len(row) > 3 else '' # log_contentではcontent_typeとして使用
                option1 = row[4].strip() if len(row) > 4 else ''
                option2 = row[5].strip() if len(row) > 5 else ''

                options = {}
                for opt_str in [option1, option2]:
                    if '=' in opt_str:
                        key, val = opt_str.split('=', 1)
                        options[key.strip()] = val.strip()
                
                command_detail = f"コマンド: {command}"
                if selector_type: command_detail += f", セレクタタイプ: {selector_type}"
                if selector_value: command_detail += f", セレクタ値: {selector_value}"
                if value_or_path: command_detail += f", 内容/ファイルパス/属性: {value_or_path}" # 表示を更新
                if options: command_detail += f", オプション: {options}"
                
                self._log("INFO", f"--- コマンド実行中 (行 {i+2}) --- {command_detail}")

                try:
                    if command == 'navigate':
                        wait_time = int(options.get('wait_time', 0))
                        self.navigate_to_url(value_or_path, wait_time=wait_time)
                    elif command == 'input':
                        self.input_value(selector_type, selector_value, value_or_path)
                    elif command == 'click':
                        self.click_element(selector_type, selector_value)
                    elif command == 'screenshot':
                        remark = options.get('remark', '')
                        full_page = options.get('full_page', '').lower() == 'true'
                        self.take_screenshot(value_or_path, remark=remark, full_page=full_page)
                    elif command == 'log_content':
                        content_type = value_or_path # 値/ファイルパスの列をcontent_typeとして使用
                        remark = options.get('remark', '')
                        self.log_content(selector_type, selector_value, content_type, remark=remark)
                    elif command == 'log_remark':
                        remark = options.get('remark', '')
                        self.log_remark(remark)
                    else:
                        self._log("WARNING", f"不明なコマンドをスキップしました: {command}")
                except NoSuchElementException as e:
                    self._log("ERROR", f"エラー: 要素が見つかりません - {e}")
                except Exception as e:
                    self._log("ERROR", f"コマンド実行中に予期せぬエラーが発生しました: {e}")
                
    def close(self):
        """WebDriverを閉じます。"""
        self._log("INFO", "ブラウザを閉じます。")
        self.driver.quit()
        self._log("INFO", "テスト実行が完了しました。") # 終了ログ

# --- 使用例 ---
if __name__ == "__main__":
    # CSVファイルのパス
    csv_filename = input("テストに使用するCSVファイルのパスを入力してください (例: 'test_scenario.csv'): ")
    # csv_filename = 'test_scenario.csv'
    # CSVファイルが存在するか確認
    if not os.path.exists(csv_filename):
        print(f"エラー: 指定されたCSVファイルが存在しません: {csv_filename}")
        exit(1)
    # スクリーンショットの保存先ディレクトリとログファイルのパス
    output_dir_name = f"{Path(csv_filename).stem}_{datetime.now().strftime("%Y%m%d_%H%M%S")}"
    screenshot_dir= f'.\\{output_dir_name}_screenshots'
    log_filepath=f'{output_dir_name}.csv'
    # テスト実行
    try:
        automation = WebTestAutomation(browser='chrome', screenshot_dir=screenshot_dir, log_filepath=log_filepath)
        
        automation.execute_commands_from_csv(csv_filename)
    except Exception as e:
        if 'automation' in locals():
            automation._log("CRITICAL", f"テスト実行中に重大なエラーが発生しました: {e}")
        else:
            print(f"テスト実行開始前に重大なエラーが発生しました: {e}")
    finally:
        if 'automation' in locals() and automation.driver:
            automation.close()