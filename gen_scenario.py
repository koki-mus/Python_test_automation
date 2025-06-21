import csv
import re
import os

def generate_commands_with_vars(var_filepath, template_filepath, output_filepath):
    """
    変数定義CSVとテンプレートCSVを基に、変数を代入した新しいCSVファイルを生成します。

    Args:
        var_filepath (str): 変数定義CSVファイルのパス。
        template_filepath (str): コマンドテンプレートCSVファイルのパス。
        output_filepath (str): 出力する新しいCSVファイルのパス。
    """
    # 1. 変数定義CSVの読み込み
    var_data = []
    try:
        with open(var_filepath, 'r', newline='', encoding='sjis') as infile:
            reader = csv.reader(infile)
            var_header = next(reader)  # ヘッダー行を読み込む
            # var_headerから変数名のインデックスをマップ
            var_name_to_index = {name.strip(): i for i, name in enumerate(var_header)}

            for row in reader:
                var_data.append(row)
    except FileNotFoundError:
        print(f"エラー: 変数定義ファイル '{var_filepath}' が見つかりません。")
        return
    except Exception as e:
        print(f"変数定義ファイルの読み込み中にエラーが発生しました: {e}")
        return

    # 2. テンプレートCSVの読み込み
    template_commands = []
    try:
        with open(template_filepath, 'r', newline='', encoding='sjis') as infile:
            reader = csv.reader(infile)
            command_header = next(reader) # コマンドテンプレートのヘッダーを読み込む
            for row in reader:
                template_commands.append(row)
    except FileNotFoundError:
        print(f"エラー: テンプレートファイル '{template_filepath}' が見つかりません。")
        return
    except Exception as e:
        print(f"テンプレートファイルの読み込み中にエラーが発生しました: {e}")
        return

    # 処理後のコマンドを格納するリスト
    generated_commands = [command_header] # ヘッダーを出力に追加

    # 3. `for`/`forend` ブロックの検出と処理
    in_for_block = False
    for_block_commands = []

    for i, row in enumerate(template_commands):
        command = row[0].strip().lower() # コマンド名を小文字で取得

        if command == 'for':
            if in_for_block:
                print(f"警告: ネストされた 'for' コマンドが検出されました (行 {i+2})。現在の実装ではネストはサポートされていません。")
                continue
            in_for_block = True
            for_block_commands = [] # 新しいforブロックのコマンドを初期化
            continue # 'for' コマンド自体は出力しない

        if command == 'forend':
            if not in_for_block:
                print(f"警告: 'forend' が 'for' の開始なしで検出されました (行 {i+2})。スキップします。")
                continue
            in_for_block = False

            # forブロック内のコマンドを変数データに基づいて展開
            if not var_data:
                print("警告: 変数データがありません。'for' ブロックはスキップされます。")
            else:
                for var_row_data in var_data:
                    for for_cmd_row in for_block_commands:
                        new_row = []
                        for cell in for_cmd_row:
                            # 変数プレースホルダーを置換
                            # 例: "$var1" を対応する値に置換
                            replaced_cell = cell
                            matches = re.findall(r'\$(\w+)', cell) # $var1, $var2 などのパターンを検索
                            for var_name in matches:
                                if var_name in var_name_to_index:
                                    var_index = var_name_to_index[var_name]
                                    if var_index < len(var_row_data):
                                        replaced_cell = replaced_cell.replace(f"${var_name}", var_row_data[var_index])
                                    else:
                                        print(f"警告: 変数 '{var_name}' の値が変数定義CSVの行に存在しません。")
                                else:
                                    print(f"警告: 未定義の変数 '{var_name}' が検出されました。")
                            new_row.append(replaced_cell.replace('-', '')) # '-' もここで空文字列に置換

                        generated_commands.append(new_row)
            for_block_commands = [] # 処理後クリア
            continue # 'forend' コマンド自体は出力しない

        if in_for_block:
            for_block_commands.append(row)
        else:
            # forブロック外の通常のコマンドをそのまま追加（'-'は置換）
            processed_row = [cell.replace('-', '') if cell == '-' else cell for cell in row]
            generated_commands.append(processed_row)

    if in_for_block:
        print("警告: 'for' コマンドが 'forend' で閉じられていません。未処理の 'for' ブロックがあります。")

    # 5. 新しいCSVファイルの作成
    try:
        with open(output_filepath, 'w', newline='', encoding='sjis') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(generated_commands)
        print(f"処理が完了しました。生成されたコマンドは '{output_filepath}' に保存されました。")
    except Exception as e:
        print(f"生成されたコマンドの書き込み中にエラーが発生しました: {e}")

# --- 実行例 ---
if __name__ == "__main__":
    # 実行用のダミーファイルを作成

    var_filename = input("変数設定ファイルのパスを入力してください：")#vars.csv
    template_filename = input("テンプレートファイルのパスを入力してください：")#"commands_template.csv"
    output_filename = input("出力ファイル名を入力してください：")#"generated_commands.csv"



    # 関数を実行
    generate_commands_with_vars(var_filename, template_filename, output_filename)

    # 生成されたCSVの内容を確認 (オプション)
    print("\n--- 生成されたCSVファイルの内容 ---")
    try:
        with open(output_filename, 'r', newline='', encoding='sjis') as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)
    except FileNotFoundError:
        print("出力ファイルが見つかりませんでした。")

