import os
import discord
from discord.ext import commands
import requests
import io
import base64
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
from discord import app_commands
from enum import Enum
import datetime  # datetime モジュールをインポート

# サーバーごとの対応するチャンネルIDを指定
channel_ids_by_server = {
    1111111111111111111: [2222222222222222222] #1111111111111111111をguild idに、2222222222222222222をchannel idに変えてください。
}

# すべてのintentsを有効にする
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

sd_model_checkpoint = "default.safetensors"  # デフォルトのモデル名を設定

# セッションを作成
session = requests.Session()


# APIエンドポイント
API_URL = 'http://127.0.0.1:7860/sdapi/v1/txt2img'

directory_path = 'D:\\stable-diffusion-webui\\models\\Stable-diffusion' #ローカルのフォルダに変えてください。
safetensors_files = [file for file in os.listdir(directory_path) if file.endswith('.safetensors')]

@client.event
async def on_ready():
    print(f'ログインしました： {client.user.name}')
    await tree.sync()#スラッシュコマンドを同期

@tree.command(name="list",description="モデル名一覧表示。")
async def list_command(interaction: discord.Interaction):
    
    if safetensors_files:
        models_list = "\n".join(safetensors_files)
        await interaction.response.send_message(f"使用可能なモデル:\n```\n{models_list}```")
    else:
        await interaction.response.send_message("使用可能なモデルはありません。")

@tree.command(name="set",description="モデル名の設定。")
@discord.app_commands.describe(
    text="モデル名の設定。"
)
@discord.app_commands.rename(
    text="set"
)
@discord.app_commands.choices(
    text=[discord.app_commands.Choice(name=file, value=file) for file in safetensors_files]
)
async def set_command(interaction: discord.Interaction,text:str):
    global sd_model_checkpoint
    # モデルが存在しない場合のエラーハンドリング
    model_path = f'D:\\stable-diffusion-webui\\models\\Stable-diffusion\\{text}'
    if not os.path.exists(model_path):
        await interaction.response.send_message(f"モデル {text} が存在しません。確認してください。")
        return

    # モデル名を受け取り、sd_model_checkpointを更新
    sd_model_checkpoint = text
    await interaction.response.send_message(f"使用するモデルを変更しました、モデル名: {text}")

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

            if prompt == "/list":
                return
            
            if prompt.startswith("/set "):
                return

            payload = {
                "sd_model_checkpoint": sd_model_checkpoint,
                "prompt": prompt,
                "negative_prompt" : "(worst quality, low quality:1.4)",
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
                output_file_name = f'{message.channel.id}-{timestamp}.png'  # ファイル名を生成
                image = Image.open(io.BytesIO(base64.b64decode(r['images'][0])))
                image.save(output_file_name)  # 生成したファイル名で保存

                with open(output_file_name, 'rb') as image_file:
                    image_data = discord.File(image_file)

                await message.channel.send(file=image_data)
            else:
                await message.channel.send("画像を生成できませんでした.")

TOKEN = os.environ.get("DISCORD_BOT_TOKEN2")  # 環境変数からトークンを取得
client.run(TOKEN)
