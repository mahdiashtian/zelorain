# -*- coding:utf-8 -*-
import asyncio
import logging

import redis
from decouple import config
from telethon import TelegramClient, events

telegram_id = 777000

try:
    r = redis.StrictRedis(host="localhost", port=6379, db=5, password="", decode_responses=True)
except:
    print("[-] i can`t connect to redis!")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s ',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

admin_list = []

admin_master = ...

api_id = config('api_id')

api_hash = config('api_hash')

client = TelegramClient(
    'mahdi',
    api_id,
    api_hash
)

client.start()


@client.on(events.NewMessage(pattern="-Hello"))
async def main(event):
    await event.reply('Hey!')


asyncio.get_event_loop().run_forever()
client.run_until_disconnected()
