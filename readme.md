# 


## 〇開発環境構築手順
1. anaconda最新版をインストール
https://www.anaconda.com/download  
インストール先をメモしておくと良い。（デフォルトはC:\Users\○○\AppData\Local\anaconda3\）
○○はインストール先ユーザ名が入る。
2. windowsメニューからAnaconda promptを起動。
3. プロジェクトフォルダに移動
4. 環境作成
    ```shell
   conda env create -n [環境名] -f env.yml
    ```
5. 仮想環境に入る
    ```shell
    conda activate [環境名]
    ```
6. setting.iniの設定  
setting_sample.iniをコピーしてsetting.iniを作成。
自分の環境に合わせて内容を変更する。

## 〇実行方法
実行ファイルのパスを指定するか、フォルダに移動して以下を実行。
### pythonファイルを実行する場合
```shell
python get_release_files.py
```

### exe化する場合
```shell
pyinstaller get_release_files.py --onefile
```
実行するとdist配下にget_release_files.exeが出来上がる。

## 〇フォルダ構成
- build
    - exe化に必要なファイルが入っている。(gitには含まない)
- dist
    - ここにexeが出来上がる。(gitには含まない)
- get_release_files
    - 本体
- setting_sample.ini
    - これを変更して自分の環境に合わせる。