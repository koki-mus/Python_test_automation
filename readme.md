Seleniumを使ったテスト自動化のためのPythonコードです。CSVから命令を読み込み、基本的なWeb操作を実行できるフレームワークです。

-----

## テスト自動化フレームワーク（Selenium & Python）

このフレームワークは、CSVファイルに記述されたテストシナリオを読み込み、Selenium WebDriverを使ってWebブラウザ上で操作を実行します。

### 前提条件

  * Python 3.xがインストールされていること。
  * `selenium` ライブラリがインストールされていること。
    ```bash
    pip install selenium
    ```
  * `pillow` ライブラリがインストールされていること。(Chromeでのフルページスクリーンショット用)
    ```bash
    pip install pillow
    ```
  * 古いseleniumの場合、使用するブラウザ（Chrome, Firefoxなど）に対応するWebDriverがインストールされており、PATHが通っているか、スクリプトから指定できる場所に配置されていること。
      * Chromeの場合：[ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/)
      * Firefoxの場合：[geckodriver](https://github.com/mozilla/geckodriver/releases)

### CSVフォーマット例

テストシナリオを記述するCSVファイルは、以下のようなフォーマットを想定しています。

| コマンド | セレクタタイプ | セレクタ値 | 値／ファイルパス | オプション1 | オプション2 |
| :------- | :------------- | :--------- | :--------------- | :---------- | :---------- |
| `navigate` | -              | -          | `https://example.com` | `wait_time=5` | -           |
| `input`  | `id`           | `username` | `testuser`       | -           | -           |
| `input`  | `class_name`           | `username` | `testuser`       | -           | -           |
| `click`  | `name`         | `login_button` | -                | -           | -           |
| `click`  | `tag_name`         | `login_button` | -                | -           | -           |
|`log_content` |`class_name`|`profile-textblock`|`text`|`remark="自己紹介"`|
| `screenshot` | -              | -          | `evidence_01.png` | `remark=LoginSuccess` | `full_page=True` |




# --- 使用例 ---


-----

### コードの説明

1.  **`WebTestAutomation` クラス**:
      * **`__init__(self, browser='chrome', screenshot_dir='screenshots')`**:
          * `browser` 引数で `'chrome'` または `'firefox'` を指定して、対応するWebDriverを初期化します。
          * `screenshot_dir` でスクリーンショットの保存先ディレクトリを指定し、存在しない場合は作成します。
          * `WebDriverWait` を初期化し、要素が見つかるまでのデフォルトの最大待機時間を設定します。

      * **`_log(self, level, message)`**
        * 指定されたレベルとメッセージでログを出力します。
        * level (str): ログレベル (例: "INFO", "ERROR")。
        * message (str): ログメッセージ。
      * **`_get_element(self, selector_type, selector_value, timeout=10)`**:
          * 内部ヘルパー関数。指定されたセレクタタイプと値でWebDriverの要素を検索します。
          * 要素が可視状態になるまで待機し、見つからない場合は `NoSuchElementException` を発生させます。
          * サポートされるセレクタタイプ (`id`, `name`, `class_name`, `xpath` など) をマッピングしています。
      * **`navigate(self, url, wait_time=0)`**:
          * 指定されたURLにブラウザを遷移させます。
          * `wait_time` オプションで、ページ遷移後に指定した秒数だけ待機できます。
      * **`input_value(self, selector_type, selector_value, value)`**:
          * 指定された要素を見つけ、`value` を入力します。
          * 入力前に既存の値をクリアします。
      * **`click_element(self, selector_type, selector_value)`**:
          * 指定された要素を見つけ、クリックします。
      * **`log_content(self, selector_type, selector_value, content_type, remark)`**:
          * 指定された要素を見つけ、内容をログに出力します
      * **`log_remark(self, remark)`**:
          * 指定された文字列をログに出力します
      * **`take_screenshot(self, filename, remark="", full_page=False)`**:
          * スクリーンショットを撮影し、指定された `filename` で `screenshot_dir` に保存します。
          * `remark` (備考) を追加できます。
          * `full_page=True` とすることで、**画面全体（スクロールが必要な部分も含む）** のスクリーンショットを試みます。ChromeとFirefoxで実装が異なります。Chromeの場合はDevTools Protocol (CDP) を使用しますが、これは環境によっては設定が必要な場合があります。より確実なのは表示領域のみの撮影か、画像結合のライブラリ利用です。
      * **`execute_commands_from_csv(self, csv_filepath)`**:
          * メインの実行関数。CSVファイルを一行ずつ読み込み、各行のコマンドを実行します。
          * 各コマンドには、セレクタタイプ、セレクタ値、値／ファイルパス、そして追加のオプションを渡すことができます。
          * エラーハンドリングを行い、要素が見つからない場合やその他のエラーが発生した場合にメッセージを出力します。
      * **`close(self)`**:
          * WebDriverセッションを終了し、ブラウザを閉じます。

### CSVファイルのフォーマットとオプション

  * **`コマンド`**: 実行する操作 (例: `navigate`, `input`, `click`, `screenshot`,`log_content`,`log_remark`)
  * **`セレクタタイプ`**: 要素を特定する方法 (例: `id`, `name`, `class_name`, `xpath`, `css_selector`, `link_text`, `partial_link_text`, `tag_name`)
  * **`セレクタ値`**: セレクタに対応する値 (例: `username`, `login_button`, `//div[@id='header']`)
  * **`値／ファイルパス`**: `input` コマンドの場合は入力する値、`navigate` コマンドの場合はURL、`screenshot` コマンドの場合は保存するファイル名,`log_content`コマンドの場合は出力したい属性（例：`text`,`value`。指定なしの場合は`text`）
  * **`オプション1`, `オプション2`**: 追加のオプションを `key=value` 形式で記述します。
      * `navigate`:
          * `wait_time=<秒数>`: ページ遷移後に指定した秒数だけ待機します。
      * `screenshot`:
          * `remark=<備考>`: スクリーンショットに対する備考。
          * `full_page=True`: 画面全体（スクロールが必要な部分も含む）のスクリーンショットを撮影します。`full_page=False` または未指定の場合は表示領域のみ。
      * `log_content`:
          * `remark=<備考>`: 出力に対する備考、期待値の記載を想定。
      * `log_remark`:
          * `remark=<備考>`: 任意内容でログを出力する。ログの中で目印となるようなの記載を想定。
### 使用方法

1.  上記のPythonコードを `.py` ファイルとして保存します (例: `test_automation.py`)。

2.  テストシナリオを記述したCSVファイルを作成します (例: `test_scenario.csv`)。

3.  Pythonスクリプトを実行します。

    ```bash
    python test_automation.py
    ```

スクリプトが実行されると、ブラウザが起動し、CSVファイルに記述された順序で操作が実行され、スクリーンショットが指定されたディレクトリに保存されます。

-----

ご不明な点や追加したい機能がありましたら、お気軽にお知らせください。


#### 利用できるセレクタタイプの詳しい説明

id,name,class_nameの3つでほとんど事足りるとは思うが、それらがユニークでない場合などに参考にしてください。

* ID:

HTML要素のid属性を使用します。IDはページ内で一意であるべきとされているため、最も信頼性が高いセレクタです。
例: \<input id="username" type="text"> を選択する場合
ID, "username"

* NAME:

HTML要素のname属性を使用します。フォームの入力要素などでよく使われます。
例: \<input name="password" type="password"> を選択する場合
NAME, "password"

* CLASS_NAME:

HTML要素のclass属性を使用します。同じクラス名を持つ要素が複数ある場合、最初に見つかった要素が返されます。
例: \<button class="submit-button primary"> を選択する場合
CLASS_NAME, "submit-button"

注意点: 複数のクラスが指定されている場合 (class="class1 class2")、find_element(By.CLASS_NAME, "class1 class2") のように複数クラスを指定することはできません。単一のクラス名のみを渡す必要があります。
* TAG_NAME:

HTML要素のタグ名（例: div, a, input, button）を使用します。同じタグ名を持つ要素が複数ある場合、最初に見つかった要素が返されます。
例: <div>Hello</div> を選択する場合
TAG_NAME, "div"

* LINK_TEXT:

ハイパーリンク（\<a>タグ）の完全な表示テキストを使用します。
例: \<a href="/about">About Us</a> を選択する場合
LINK_TEXT, "About Us"

* PARTIAL_LINK_TEXT:

ハイパーリンク（\<a>タグ）の表示テキストの一部を使用します。
例: \<a href="/contact">Contact Support</a> を選択する場合
PARTIAL_LINK_TEXT, "Contact"

* XPATH:

XML Path Language (XPath) を使用して要素を特定します。非常に強力で柔軟性があり、IDやクラス名がない場合でも要素を見つけることができます。親要素からの相対パスや属性値、テキスト内容など、様々な条件で指定可能です。
例:
IDがmainのdiv内の最初のpタグ: //div[@id='main']/p[1]
テキストが"Submit"のボタン: //button[text()='Submit']
任意のタグでname属性がqのもの: //*[@name='q']
XPATH, "//input[@name='q']"

注意点: XPathは強力ですが、ページの構造変更に弱く、パフォーマンスも他のセレクタより劣る場合があります。
* CSS_SELECTOR:

Cascading Style Sheets (CSS) のセレクタ構文を使用します。XPathと同様に柔軟性がありますが、より簡潔で高速な場合が多いです。
例:
IDがusernameの要素: #username
クラスがbtnの要素: .btn
name属性がpasswordのinput要素: input[name='password']
class属性にprimaryを含むbutton要素: button.primary
CSS_SELECTOR, "input[name='q']"

注意点: CSSセレクタはHTMLの構造に密接に関連しているため、HTML構造が変更されるとセレクタも更新する必要がある場合があります。

