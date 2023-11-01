# config.py

# Discord Bot Token
DISCORD_BOT_TOKEN = "Your Discord Bot Token Here"  # ここに実際のトークンを設定

# APIエンドポイント
API_URL = 'http://127.0.0.1:7860/sdapi/v1/txt2img'
SD_MODELS_API_URL = 'http://127.0.0.1:7860/sdapi/v1/sd-models'
OPTIONS_API_URL = 'http://127.0.0.1:7860/sdapi/v1/options'

# 画像を保存するディレクトリを指定
output_directory_path = 'D:\\stable-diffusion-webui\\outputs\\discord-bot\\'

# サーバーごとの対応するチャンネルIDを指定
# guild_id : [channel_id]
channel_ids_by_server = {
    1111111111111111111: [3333333333333333333],
    2222222222222222222: [4444444444444444444]
}