# stable-diffusion-web-ui-discord-bot
Stable Diffusion Web UIをdiscordから使えるようにするBOT

### 使い方

pythonは3.10をインストールしてください。WindowsならMicroSoftStoreアプリを開いてPythonで検索したらあります。

gitも入れてください。以下のリンクを開いて右側のDownload for Windowsのボタンを押すとダウンロードできます。

[https://git-scm.com/](https://git-scm.com/)

コマンドプロンプト、PowerShell、ターミナル（Windows11）のどれかで以下のコマンドを順番に打ちます。

```
git clone https://github.com/suzunayui/stable-diffusion-web-ui-discord-bot.git
```

```
cd stable-diffusion-web-ui-discord-bot
```

```
pip install -r requirements.txt
```

設定ファイルの編集をします。

sample.config.pyをconfig.pyにリネームしてください。

DISCORD_BOT_TOKENはDiscord Developer PortalでApplicationを作ってから取得したものを設定してください。

API_URLはStable Diffusion Web UIの設定を変えていないならそのままでいいです。

model_directory_pathはStable Diffusion Web UIのmodels\Stable-diffusionフォルダを指定。

output_directory_pathは出力したいフォルダを設定。

channel_ids_by_serverは左がguild_id、右がchannel_idです。discordの開発者モードを有効にしたらIDをコピーできるのでそれで取得します。

Stable Diffusion Web UIのwebui-user.batを編集します。

```
set COMMANDLINE_ARGS=
```

の行を

```
set COMMANDLINE_ARGS=--no-half --api
```

に変えます。（環境によっては--no-halfは必要ない場合があります、--apiオプションはつけないとAPIが使用できないはずです）

webui-user.batをダブルクリックして起動しておきます。

ここまで設定したらコマンドで

```
python main.py
```

で起動したら動くはずです。動かなかったら作成者にXかDiscordで質問するか、わかる人に聞いてください。