
from telethon import TelegramClient, events
import requests, os, time

# HARD-CODED API values for PythonAnywhere
api_id = 3533119  # Replace with your API ID
api_hash = '52f122fdff0aed9adb76267cd9d2e5c1'  # Replace with your API hash

client = TelegramClient('user_session', api_id, api_hash)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T']:
        if abs(num) < 1024.0:
            return f"{num:.2f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.2f}P{suffix}"

@client.on(events.NewMessage)
async def handle_url(event):
    url = event.raw_text.strip()
    if not url.startswith('http'):
        await event.reply("Please send a direct download URL.")
        return

    msg = await event.respond("Downloading...")

    try:
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            total = int(r.headers.get('content-length', 0))
            fname = url.split('/')[-1].split('?')[0] or "file"
            done = 0
            chunk = 1024 * 1024 * 4
            start = time.time()

            with open(fname, 'wb') as f:
                for i, data in enumerate(r.iter_content(chunk_size=chunk)):
                    f.write(data)
                    done += len(data)
                    if i % 3 == 0:
                        speed = done / (time.time() - start)
                        percent = done * 100 / total if total else 0
                        await msg.edit(f"**Downloading:** {sizeof_fmt(done)} / {sizeof_fmt(total)} ({percent:.2f}%)\nSpeed: {sizeof_fmt(speed)}/s")

        await msg.edit("Uploading to Telegram...")

        async def upload_progress(cur, total):
            percent = cur * 100 / total
            speed = cur / (time.time() - start)
            await msg.edit(f"**Uploading:** {sizeof_fmt(cur)} / {sizeof_fmt(total)} ({percent:.2f}%)\nSpeed: {sizeof_fmt(speed)}/s")

        start = time.time()
        await client.send_file(event.chat_id, fname, caption="Here's your file!", progress_callback=upload_progress)
        os.remove(fname)

    except Exception as e:
        await msg.edit(f"Error: {e}")

client.start()
client.run_until_disconnected()
