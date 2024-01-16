# coding: utf-8

import os
import shutil
import datetime
import sys
import git
import questionary
from questionary import Choice
import configparser
import colorama
from colorama import Fore, Back, Style


def main():
    try:
        # Gitの設定変更
        configure_git_details()

        # 日付取得
        dt = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        date = dt.strftime("%Y%m%d")

        # 色設定初期化
        colorama.init()
        # 共通変数
        DEFAULT_CHOICE = [
            Choice('はい', value=1),
            Choice('いいえ', value=2),
        ]

        # 実行ファイルのディレクトリを取得
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname('./dist/')

        # 設定ファイルのパスを設定
        config_file_path = os.path.join(application_path, 'setting.ini')

        # 設定ファイル取得
        config = configparser.ConfigParser()
        config.read(config_file_path, encoding='utf-8')
        # セクション名のlistを取り出す
        settings = config.sections()

        if len(settings) == 0:
            print("設定を記述してください。")
            sys.exit()

        # プロジェクト選択
        setting_project = questionary.select(
            '対象のプロジェクトを選択してください。',
            choices=settings,
        ).ask()

        # 各種設定取得
        project_name = config[setting_project]['project_name']
        project_path = config[setting_project]['project_path']
        export_path = config[setting_project]['export_path']
        diff_file_name = config[setting_project]['diff_file_name']

        if diff_file_name == "":
            diff_file_name = "diffs.txt"

        # パスが間違っている場合は終了。
        if not os.path.exists(project_path):
            print('プロジェクトフォルダが存在しません。PATH：' + project_path)
            sys.exit()
        if not os.path.exists(export_path):
            print('出力先フォルダが存在しません。PATH：' + export_path)
            sys.exit()

        # 出力先パスを設定
        diff_file_directory = export_path + "/" + date + "/"
        output_directory = diff_file_directory + project_name + "/"
        repo = git.Repo(project_path)

        # コミット番号入力
        print('比較元のコミット番号を入力してください。')
        from_commit_num = get_from_commit_num()

        # print('比較先のコミット番号を入力してください。（最新と比較する場合は空で入力してください。')
        # after_commit_num = input('>> ')

        # git diff処理
        # if after_commit_num == "":
        # 差分情報非表示
        diff_result = repo.git.diff(from_commit_num, name_only=True, diff_filter='d')
        # 削除以外の差分
        diff_result_status = repo.git.diff(from_commit_num, name_status=True, diff_filter='d')
        # 削除の差分
        diff_result_status_delete = repo.git.diff(from_commit_num, name_status=True, diff_filter='D')
        # else:
        #     diff_result = repo.git.diff(from_commit_num, after_commit_num, name_only=True, diff_filter='d')
        #     diff_result_status = repo.git.diff(from_commit_num, after_commit_num, name_status=True, diff_filter='d')
        #     diff_result_status_delete = repo.git.diff(from_commit_num, after_commit_num, name_status=True, diff_filter='D')

        print_file_list('●コピー対象ファイル一覧', diff_result_status, Fore.GREEN)
        print_file_list('●削除ファイル一覧', diff_result_status_delete, Fore.LIGHTRED_EX)

        # 配列を分割して取得
        diff_result_array = diff_result.splitlines()
        print("コピー対象", len(diff_result_array), "件\n")

        copy_confirm = questionary.select(
            '以上のファイルをコピーしてよいですか？（1度出力している場合は、削除され再コピーされます。）',
            choices=DEFAULT_CHOICE,
        ).ask()
        if copy_confirm == 2:
            sys.exit()

        # 一度実行済みだったら実行前に一旦フォルダごと削除
        if os.path.exists(output_directory):
            shutil.rmtree(output_directory)

        os.makedirs(output_directory, exist_ok=True)

        print("\nコピー開始\n")
        # コピー処理
        count = 0
        print(Fore.CYAN)
        print('●作成ファイル一覧')
        print('----------------------------------------------------------')
        for i in diff_result_array:
            count += 1
            # ルート直下のファイル以外
            if "/" in i:
                directory_path = os.path.dirname(i)
                os.makedirs(directory_path, exist_ok=True)
                destination_path = shutil.copy2(project_path + "/" + i, directory_path)
            else:
                destination_path = shutil.copy2(project_path + "/" + i, output_directory)

            print(destination_path)
        print('----------------------------------------------------------')
        print(Fore.RESET)

        print("コピー終了\n")
        print(count, "/", len(diff_result_array), "件ファイルをコピーしました。\n")

        # 変更履歴をテキストファイルに吐き出し。
        export_txt_file(diff_file_directory, diff_file_name, [diff_result_status, diff_result_status_delete])

    except Exception as e:
        print_exception(e)

    finally:
        # キー入力があるまでプロンプトを閉じない。
        os.system('PAUSE')


# 関数定義
# 比較開始コミット番号取得
def get_from_commit_num():
    revision = input('>> ')
    try:
        if num == "e":
            sys.exit()
        elif len(revision) < 40:
            print("40文字のコミット番号を入力してください。(終了する場合は「e」を入力してください。)")
            return get_from_commit_num()
        else:
            return revision
    except Exception as gfcn_e:
        print_exception(gfcn_e)
        sys.exit()


def export_txt_file(directory_name, file_name, diff_results):
    try:
        path = directory_name + file_name
        if os.path.isfile(path):
            os.remove(path)
        with open(path, 'x', encoding='UTF-8') as f:
            for diff in diff_results:
                f.writelines(diff)
                f.writelines("\n")
            f.close()
            print("以下ファイルに差分情報を出力しました。\n")
            print(path)
    except Exception as exf_e:
        print_exception(exf_e)
        sys.exit()


# exceptionの表示
def print_exception(exception):
    print(Fore.RED)
    print("エラーが発生しました。\n")
    print(exception)
    print(Fore.RESET)


# ファイル一覧の表示
def print_file_list(title, list_, color):
    print(color)
    print(title)
    if len(list_) :
        
        print('----------------------------------------------------------')
        print(list_)
        print('----------------------------------------------------------\n')
    else :
        print('差分はありません')
    print(Fore.RESET)


# git設定変更
def configure_git_details():
    config = git.GitConfigParser(
        file_or_files=git.config.get_config_path("global"),
        read_only=False
    )
    with config:
        # core.quotepathがfalseじゃないとgit statusやgit diffが文字化けする。
        config.set_value("core", "quotepath", False)


if __name__ == "__main__":
    main()

