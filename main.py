# -*- coding:utf-8 -*-
import asyncio
import logging
import os
from datetime import datetime

import aiocron
import pytz
import redis.asyncio as redis
from decouple import config
from telethon import TelegramClient, events
from telethon import functions
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from services import delete_profile_photo
from utils import image_set_clock

telegram_id = 777000

try:
    r = redis.StrictRedis(host="localhost", port=6379, db=1, password="", decode_responses=True)
except Exception as e:
    print("[-] i can`t connect to redis!\n[-] error: " + str(e))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s ',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

master = config('master', cast=int)

admin_list = config('admin_list', cast=lambda v: [int(s.strip()) for s in v.split(',') if v],) + [master]

api_id = config('api_id')

api_hash = config('api_hash')

client = TelegramClient(
    'mahdi',
    api_id,
    api_hash
)

client.start()

save_path = "assets/images/avatar.jpg"


@aiocron.crontab('*/1 * * * *')
async def worker():
    online_mode = await r.get("online")
    clock_in_profile = await r.get("clock_in_profile")

    ir = pytz.timezone("Asia/Tehran")
    time = datetime.now(ir).strftime("%H:%M")

    if online_mode == "1":
        await client(functions.account.UpdateStatusRequest(offline=False))

    if clock_in_profile == "1":
        result = image_set_clock(time)
        await delete_profile_photo(client)
        image = await client.upload_file(result)
        await client(UploadProfilePhotoRequest(file=image))


@client.on(events.NewMessage(pattern="-Hello"))
async def main(event):
    await event.reply('Hey!')


@client.on(events.NewMessage(from_users=admin_list, pattern="-set online"))
async def set_online(event):
    await r.set("online", "1")
    await client.send_message(event.chat_id, "-Keep online mode turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset online"))
async def set_offline(event):
    await r.set("online", "0")
    await client.send_message(event.chat_id, "-Keep online mode turned off")


@client.on(events.NewMessage(from_users=admin_list, pattern="-set clock in profile"))
async def clock_in_profile_on(event):
    clock_in_profile = await r.get("clock_in_profile")
    if clock_in_profile == "1":
        await client.send_message(event.chat_id, "-Clock in profile is already on")
    else:
        result = await client.download_profile_photo("me", file=save_path)
        if result is None:
            await client.send_message(event.chat_id, "-You don`t have profile photo!")
        else:
            await r.set("clock_in_profile", "1")
            await client.send_message(event.chat_id, "-Clock in profile turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset clock in profile"))
async def clock_in_profile_off(event):
    await delete_profile_photo(client) if await r.get("clock_in_profile") == "1" else ...
    if os.path.exists(save_path):
        image = await client.upload_file(save_path)
        await client(UploadProfilePhotoRequest(file=image))
    await r.set("clock_in_profile", "0")
    await client.send_message(event.chat_id, "-Clock in profile turned off")


@client.on(events.NewMessage(from_users=admin_list, pattern="-remove profile"))
async def remove_profile(event):
    await delete_profile_photo(client)
    await client.send_message(event.chat_id, "-Profile photo removed")


worker.start()
asyncio.get_event_loop().run_forever()
client.run_until_disconnected()
