import os
import discord
import discord.app_commands
import datetime
import requests
import io
import base64
from PIL import Image
from database_access import UserSettingsDatabase

from config import DISCORD_BOT_TOKEN, API_URL, model_directory_path, output_directory_path, channel_ids_by_server

# すべてのintentsを有効にする
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

# セッションを作成
session = requests.Session()

# モデルファイルのリストを作成
allowed_extensions = (".safetensors", ".ckpt")
model_files = [file for file in os.listdir(
    model_directory_path) if file.endswith(allowed_extensions)]

# choicesリストを作成
choices = [discord.app_commands.Choice(name=file, value=file) for file in model_files]

# 起動時処理
@client.event
async def on_ready():
    print(f'ログインしました： {client.user.name}')

    # データベースを初期化
    with UserSettingsDatabase("user_settings.db") as user_settings_db:
        pass  # ここで何か他の初期化処理を行うこともできます

    await tree.sync()

# sd_list_models コマンド
@tree.command(description="使用可能なモデル一覧を表示します。")
async def sd_list_models(ctx):
    if model_files:
        models_list = "\n".join(model_files)
        await ctx.response.send_message(f"使用可能なモデル:\n```\n{models_list}```")
    else:
        await ctx.response.send_message("使用可能なモデルはありません.")

# sd_set_model コマンド
@tree.command(description="使用するモデルを設定します。")
@discord.app_commands.choices(
    value=choices
)
async def sd_set_model(ctx, value: str):
    # モデルが存在しない場合のエラーハンドリング
    model_path = os.path.join(model_directory_path, value)
    if not os.path.exists(model_path):
        await ctx.response.send_message(f"モデル {value} が存在しません。確認してください.")
        return

    key = "sd_model_checkpoint"
    user_id = ctx.user.id  # ユーザーID
    guild_id = ctx.guild.id  # サーバー（ギルド）ID

    # データベース接続を with ステートメントで確立
    with UserSettingsDatabase("user_settings.db") as user_settings_db:
        user_settings_db.add_setting(user_id, guild_id, key, value)

    await ctx.response.send_message(f"設定を変更しました、キー: {key}, 値: {value}")

# sd_model コマンド
@tree.command(description="現在設定しているモデルを確認します。")
async def sd_model(ctx):
    key = "sd_model_checkpoint"
    user_id = ctx.user.id
    guild_id = ctx.guild.id

    # データベース接続を with ステートメントで確立
    with UserSettingsDatabase("user_settings.db") as user_settings_db:
        # データベースからユーザーのモデル設定を取得
        model_setting = user_settings_db.get_setting(user_id, guild_id, key)

    if model_setting is not None:
        await ctx.response.send_message(f"現在のモデル設定: {model_setting}")
    else:
        await ctx.response.send_message("モデルが設定されていません。")

# sd_set_negative_prompt コマンド
@tree.command(description="ネガティブプロンプトを設定します。")
async def sd_set_negative_prompt(ctx, value: str):
    key = "negative_prompt"
    user_id = ctx.user.id  # ユーザーID
    guild_id = ctx.guild.id  # サーバー（ギルド）ID

    # データベース接続を with ステートメントで確立
    with UserSettingsDatabase("user_settings.db") as user_settings_db:
        user_settings_db.add_setting(user_id, guild_id, key, value)

    await ctx.response.send_message(f"設定を変更しました、キー: {key}, 値: {value}")

# sd_negative_prompt コマンド
@tree.command(description="現在設定しているネガティブプロンプトを確認します。")
async def sd_negative_prompt(ctx):
    key = "negative_prompt"  # キーを "negative_prompt" に変更
    user_id = ctx.user.id
    guild_id = ctx.guild.id

    # データベース接続を with ステートメントで確立
    with UserSettingsDatabase("user_settings.db") as user_settings_db:
        # データベースからユーザーの negative_prompt 設定を取得
        negative_prompt_setting = user_settings_db.get_setting(user_id, guild_id, key)

    if negative_prompt_setting is not None:
        await ctx.response.send_message(f"現在の negative_prompt 設定: {negative_prompt_setting}")
    else:
        await ctx.response.send_message("negative_prompt が設定されていません。")

# メッセージが送られた時の処理
@client.event
async def on_message(message):

    # メッセージがボット自身のものであるかをチェック
    if message.author == client.user:
        return  # ボット自身のメッセージは無視

    # メッセージが空であるかをチェック（任意の追加の条件をここに追加できます）
    if not message.content:
        return  # 空のメッセージを無視

    # メッセージが特定のチャンネルから送信されたかを確認
    if message.guild.id in channel_ids_by_server:
        target_channel_ids = channel_ids_by_server[message.guild.id]
        if message.channel.id in target_channel_ids:
            # メッセージが指定したサーバーの対応するチャンネルから送信された場合
            # ここで処理を続行

            prompt = message.content

            if prompt.startswith("/"):
                return

            # 使う設定の読み込み
            user_id = message.author.id
            guild_id = message.guild.id

            model = None

            with UserSettingsDatabase("user_settings.db") as user_settings_db:
                # データベースからユーザーのモデル設定を取得
                model = user_settings_db.get_setting(user_id, guild_id, "sd_model_checkpoint")

            if not model:
                default_model = model_files[0]  # デフォルトのモデル
                with UserSettingsDatabase("user_settings.db") as user_settings_db:
                    user_settings_db.add_setting(user_id, guild_id, "sd_model_checkpoint", default_model)
                model = default_model

            negative_prompt = None
            
            with UserSettingsDatabase("user_settings.db") as user_settings_db:
                # データベースからユーザーの negative_prompt 設定を取得
                negative_prompt = user_settings_db.get_setting(user_id, guild_id, "negative_prompt")

            if not negative_prompt:
                default_negative_prompt = "(worst quality, low quality:1.4)"  # デフォルトのネガティブプロンプト
                with UserSettingsDatabase("user_settings.db") as user_settings_db:
                    user_settings_db.add_setting(user_id, guild_id, "negative_prompt", default_negative_prompt)
                negative_prompt = default_negative_prompt

            user_settings_db.close()

            payload = {
                "sd_model_checkpoint": model,
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "steps": 20,
                "sampler_index": "DPM++ 2M Karras",
                "width": 512,
                "height": 512,
                "cfg_scale": 7,
                "seed": -1
            }

            # リクエストを送信して応答を待つ
            with session.post(url=API_URL, json=payload) as response:
                r = response.json()
                print("status:" + str(response.status_code))

            if 'images' in r:
                timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")  # タイムスタンプを生成
                # ファイル名を生成
                output_file_directory = f'{output_directory_path}{timestamp}.png'
                output_file_name = f'{timestamp}.png'

                # ディレクトリが存在しない場合、途中のディレクトリを作成
                os.makedirs(os.path.dirname(output_file_directory), exist_ok=True)

                image = Image.open(io.BytesIO(
                    base64.b64decode(r['images'][0])))
                image.save(output_file_directory)  # 生成したディレクトリ・ファイル名で保存

                with open(output_file_directory, 'rb') as image_file:
                    image_data = discord.File(image_file, filename=output_file_name)

                await message.channel.send(file=image_data)
            else:
                await message.channel.send("画像を生成できませんでした.")

client.run(DISCORD_BOT_TOKEN)