#disbot.py
'''This code is for running discord bot for save photo on construction line check 
  1.create folder YYMMDD for each day the photo was sent
  2.rename photo to YYmmddhhmm_caption and save for the folder in that day'''

######################################################################################################################
import discord
import os
import requests
from flask import Flask
from threading import Thread
from datetime import datetime
import pytz
from utils import is_image


### for get token and webhook from pipedream ###
TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

### Listen for message in discord ###
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
allowed_channels = [1369712932006527179]

### Set up flask for web server ###
app = Flask('')
@app.route('/')
def home():
    return "🤖 Discord bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

# Run Flask server in background
Thread(target=run).start()

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    print(f"[LOG] New message from {message.author}: {message.content}")

    if message.content.strip() == "!status":
        await message.channel.send(f"✅ I’m alive as {client.user}\n Please send me a photo or file to save it.")
        return

    if message.author.bot:
        print("[LOG] Ignored bot message")
        return

    # ⏰ Restrict to 08:00–22:00 Thai time
    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)
    if now.hour < 8 or now.hour >= 23.5:
        print("[LOG] Outside active hours. Ignoring message.")
        return

    ### Protect no attachement	###
    if not message.attachments:
        print("[LOG] Message received without attachment. Skipping.")
        return
    ### Protect not allowed_channels ###
    if message.channel.id not in allowed_channels:
        print("[LOG] Message not in allowed channel. Ignoring.")
        return  # Ignore messages from other channels

    print(f"[LOG] {len(message.attachments)} attachment(s) found")
    caption = message.content.strip().replace("/", "_") or "No_Caption"
    timestamp = now.strftime("%y%m%d_%H%M")
    folder_name = now.strftime("%Y%m%d")
    attachments = message.attachments

    ### If 1 filename	###
    if len(attachments) == 1:
        attachment = attachments[0]
        ### Check file type  ###
        if is_image(attachment):
            file_type = "photo"
            filename = f"{timestamp}_{caption}.jpg"
        else:
            file_type = "file"
            filename = f"{timestamp}_{attachment.filename}" 

       
        print(f"[LOG] Sending file: {filename}")

        data = {
            "filename": attachment.filename,
            "url": attachment.url,
            "author": str(message.author),
            "channel": str(message.channel),
            "folder": folder_name,
            "renamed": filename,
            "caption": caption,
            "ftype": file_type
        }
        try:
            res = requests.post(WEBHOOK_URL, json=data)
            print(f"[LOG] Sent to Pipedream. Response: {res.status_code}")
            if res.status_code in [200, 202]:
                try:
                    result = res.json()
                    if result.get("status") == "success":
                        await message.channel.send(f"✅ File `{filename}` was uploaded and processed by Power Automate!")
                    else:
                        await message.channel.send(
                            f"❌ Flow error: {result.get('error', 'Unknown error')}"
                        )
                except Exception as e:
                    await message.channel.send(f"⚠️ Uploaded, but could not read status from Power Automate: {e}")
            else:
                await message.channel.send(f"❌ Failed to upload `{filename}`")
        except Exception as e:
            print(f"[ERROR] Failed to send to Pipedream: {e}")
            await message.channel.send(f"❌ Upload error: {e}")
        '''try:
            res = requests.post(WEBHOOK_URL, json=data)
            print(f"[LOG] Sent to Pipedream. Response: {res.status_code}")
            if res.status_code == 200 or 202:
                await message.channel.send(f"✅ File `{filename}` was already uploaded")
            else:
                await message.channel.send(f"❌ Failed to upload `{filename}`")
        except Exception as e:
            print(f"[ERROR] Failed to send to Pipedream: {e}")
            await message.channel.send(f"❌ Upload error: {e}")'''

    ### Else More than 1 files	###
    else:
        for i, attachment in enumerate(attachments, start=1):
            ### Check file type  ###
            if is_image(attachment):
                file_type = "photo"
                indexed_caption = f"{caption}_{i}"
                filename = f"{timestamp}_{caption}_{i}.jpg"
                caption_to_use = indexed_caption
            else:
                file_type = "file"
                filename = f"{timestamp}_{attachment.filename}"
                caption_to_use = caption 
            

            print(f"[LOG] Sending file: {filename}")

            data = {
                "filename": attachment.filename,
                "url": attachment.url,
                "author": str(message.author),
                "channel": str(message.channel),
                "folder": folder_name,
                "renamed": filename,
                "caption": caption_to_use,
                "ftype": file_type
            }
            try:
                res = requests.post(WEBHOOK_URL, json=data)
                print(f"[LOG] Sent to Pipedream. Response: {res.status_code}")
                if res.status_code in [200, 202]:
                    try:
                        result = res.json()
                        if result.get("status") == "success":
                            await message.channel.send(f"✅ File `{filename}` was uploaded and processed by Power Automate!")
                        else:
                            await message.channel.send(
                                f"❌ Flow error: {result.get('error', 'Unknown error')}"
                            )
                    except Exception as e:
                        await message.channel.send(f"⚠️ Uploaded, but could not read status from Power Automate: {e}")
                else:
                    await message.channel.send(f"❌ Failed to upload `{filename}`")
            except Exception as e:
                print(f"[ERROR] Failed to send to Pipedream: {e}")
                await message.channel.send(f"❌ Upload error: {e}")
            '''try:
                res = requests.post(WEBHOOK_URL, json=data)
                print(f"[LOG] Sent to Pipedream. Response: {res.status_code}")
                if res.status_code == 200 or 202 :
                    await message.channel.send(f"✅ File `{filename}` was already uploaded")
                else:
                    await message.channel.send(f"❌ Failed to upload `{filename}`")
            except Exception as e:
                print(f"[ERROR] Failed to send to Pipedream: {e}")
                await message.channel.send(f"❌ Upload error: {e}")'''

client.run(TOKEN)

