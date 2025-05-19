import discord
import os
import requests
from flask import Flask
from threading import Thread


TOKEN = os.environ.get("TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
app = Flask('')

@app.route('/')
def home():
    return "🤖 Discord bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

# Run the Flask web server in a separate thread
Thread(target=run).start()

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    print(f"[LOG] New message from {message.author}: {message.content}")
    
    if message.content.strip() == "!status":
        await message.channel.send(f"✅ I’m alive as {client.user}")
        return


    if message.author.bot:
        print("[LOG] Ignored bot message")
        return

    if message.attachments:
        print(f"[LOG] {len(message.attachments)} attachment(s) found")

        for attachment in message.attachments:
            print(f"[LOG] Sending file: {attachment.filename}")
            data = {
                "filename": attachment.filename,
                "url": attachment.url,
                "author": str(message.author),
                "channel": str(message.channel)
            }
            try:
                res = requests.post(WEBHOOK_URL, json=data)
                print(f"[LOG] Sent to Pipedream. Response: {res.status_code}")
            except Exception as e:
                print(f"[ERROR] Failed to send to Pipedream: {e}")


client.run(TOKEN)
