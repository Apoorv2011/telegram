import os
import asyncio
from quart import Quart 
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from hypercorn.config import Config
from hypercorn.asyncio import serve

# --- 1. ASYNC WEB SERVER SETUP ---
app = Quart(__name__)

@app.route('/')
async def home():
    return "Status: Userbot is Active and Monitoring 24/7", 200

# --- 2. TELEGRAM CONFIGURATION ---
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")
TARGET_ID = int(os.environ.get("TARGET_ID"))

client = TelegramClient(
    StringSession(STRING_SESSION),
    API_ID,
    API_HASH,
    connection_retries=None
)

async def process_and_save(event):
    """Clones messages instantly. 
    Handles text, audio, voice notes, and videos independently of the sender.
    """
    try:
        # Passing event.message tells Telethon to send an identical copy of the text/media
        await client.send_message('me', event.message)
        print(f"Captured & Secured: Message/Audio from {TARGET_ID} cloned to Saved Messages.", flush=True)
    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"Failed to clone message: {e}", flush=True)

@client.on(events.NewMessage(from_users=TARGET_ID, incoming=True))
async def instant_forwarder(event):
    # create_task pushes the download/upload process to the background instantly
    # This ensures a 0-second reaction time for consecutive messages
    asyncio.create_task(process_and_save(event))

# --- 3. UNIFIED STARTUP ENGINE ---
async def main():
    print("Userbot is connecting to Telegram...", flush=True)
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("--- ERROR: The STRING_SESSION is invalid or expired! ---", flush=True)
            return
        print("--- SUCCESS: Bot is now online and listening! ---", flush=True)
    except Exception as e:
        print(f"Failed to start client: {e}", flush=True)
        return

    config = Config()
    config.bind = ["0.0.0.0:7860"]

    await asyncio.gather(
        serve(app, config),
        client.run_until_disconnected()
    )

if __name__ == "__main__":
    asyncio.run(main())
