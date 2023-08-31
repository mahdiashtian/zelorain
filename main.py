# -*- coding:utf-8 -*-
import asyncio
import logging

import aiocron
import redis.asyncio as redis
from decouple import config
from telethon import TelegramClient, events
from telethon import functions

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


@aiocron.crontab('*/1 * * * *')
async def worker():
    online_mode = await r.get("online")

    if online_mode == "1":
        await client(functions.account.UpdateStatusRequest(offline=False))


@client.on(events.NewMessage(pattern="-Hello"))
async def main(event):
    await event.reply('Hey!')


@client.on(events.NewMessage(from_users=admin_list, pattern="-online"))
async def set_online(event):
    await r.set("online", "1")
    await client.send_message(event.chat_id, "-Keep online mode turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-offline"))
async def set_offline(event):
    await r.set("online", "0")
    await client.send_message(event.chat_id, "-Keep online mode turned off")


worker.start()
asyncio.get_event_loop().run_forever()
client.run_until_disconnected()
