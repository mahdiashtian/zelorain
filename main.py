# -*- coding:utf-8 -*-
import asyncio
import logging
import os
import random
from datetime import datetime

import aiocron
import pytz
import redis.asyncio as redis
from decouple import config
from telethon import TelegramClient, events
from telethon import functions
from telethon.errors.rpcerrorlist import ContactIdInvalidError
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest

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

admin_list = config('admin_list', cast=lambda v: [int(s.strip()) for s in v.split(',') if v]) + [master]

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
    change_name = await r.get("change_name")

    ir = pytz.timezone("Asia/Tehran")
    time = datetime.now(ir).strftime("%H:%M")

    if online_mode == "1":
        await client(functions.account.UpdateStatusRequest(offline=False))

    if clock_in_profile == "1":
        result = image_set_clock(time)
        await delete_profile_photo(client)
        image = await client.upload_file(result)
        await client(UploadProfilePhotoRequest(file=image))

    if change_name == "1":
        list_name = await r.lrange("list_name", 0, -1) or await client.get_me()
        name = random.choice(list_name) if isinstance(list_name, list) else list_name.first_name
        await client(functions.account.UpdateProfileRequest(first_name=name))


@client.on(events.NewMessage(pattern="-Hello"))
async def main(event):
    await event.reply('Hey!')


@client.on(events.NewMessage(from_users=admin_list, pattern="-set online"))
async def set_online(event):
    await r.set("online", "1")
    await client.send_message(event.chat_id, "-Keep online mode turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset online"))
async def unset_online(event):
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
    await delete_profile_photo(client, 1)
    await client.send_message(event.chat_id, "-Profile photo removed")


@client.on(events.NewMessage(from_users=admin_list, pattern="-fuck"))
async def fuck(event):
    fuck_text_sended = "			.\n \n                          /¯ )\n                        /¯  / \n                      /    / \n              /´¯/'   '/´¯ )\n           /'/   /     /    / / \ \n          ('(   (   (   (     |/    )\n          \                       ./ \n           \                _.•´\n             \              (\n               \             \ "
    fuck_text_edited = "			.\n \n                          \n                         \n                       \n              /´¯/'   '/´¯ )\n           /'/   /     /    / / \ \n          ('(   (   (   (     |/    )\n          \                       ./ \n           \                _.•´\n             \              (\n               \             \ "
    message = await client.send_message(event.chat_id, fuck_text_sended, reply_to=event.reply_to_msg_id)
    for i in range(1, 5):
        await asyncio.sleep(0.5)
        await client.edit_message(event.chat_id, message, fuck_text_edited)
        await asyncio.sleep(0.5)
        await client.edit_message(event.chat_id, message, fuck_text_sended)


@client.on(events.NewMessage(from_users=admin_list, pattern="-ping"))
async def ping(event):
    x = 7
    black_ball = "⚫️"
    white_ball = "⚪️"
    message = await client.send_message(event.chat_id, black_ball * x)
    for i in range(x + 2):
        await client.edit_message(event.chat_id, message, f"{black_ball * (x - i + 1) + (white_ball * (i + 1))}")
    await client.edit_message(event.chat_id, message, "-Im online")


@client.on(events.NewMessage(func=lambda e: e.is_private and e.chat_id not in admin_list))
async def lock_pv(event):
    status = await r.get("lock_pv")
    if status == "1":
        sender = await event.get_sender()
        if not sender.contact:
            await client.delete_messages(event.chat_id, event.message.id)


@client.on(events.NewMessage(from_users=admin_list, pattern="-set lock pv"))
async def set_lock_pv(event):
    await r.set("lock_pv", "1")
    await client.send_message(event.chat_id, "-Lock pv turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset lock pv"))
async def unset_lock_pv(event):
    await r.set("lock_pv", "0")
    await client.send_message(event.chat_id, "-Lock pv turned off")


@client.on(events.NewMessage(from_users=admin_list, pattern="-set auto seen"))
async def set_auto_seen(event):
    await r.set("auto_seen", "1")
    await client.send_message(event.chat_id, "-Auto seen turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset auto seen"))
async def unset_auto_seen(event):
    await r.set("auto_seen", "0")
    await client.send_message(event.chat_id, "-Auto seen turned off")


@client.on(events.NewMessage(func=lambda e: e.is_private))
async def auto_seen(event):
    status = await r.get("auto_seen")
    if status == "1":
        try:
            await client.send_read_acknowledge(event.chat_id, max_id=event.id)
        except ValueError as va:
            sender = await event.get_input_sender()
            await client.send_read_acknowledge(sender, max_id=event.id)


@client.on(events.NewMessage(from_users=admin_list, pattern="-set block"))
async def set_block(event):
    if event.reply_to_msg_id is None:
        await client.send_message(event.chat_id, "-Reply to a message!")
    else:
        try:
            replied = await event.get_reply_message()
            sender = replied.sender_id
            await client(functions.contacts.BlockRequest(id=sender))
            full = await client(GetFullUserRequest(sender))
            await client.send_message(event.chat_id, f"-User {full.user.first_name} {full.user.last_name} blocked")
        except ContactIdInvalidError:
            await client.send_message(event.chat_id, "-The provided contact ID is invalid")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset block"))
async def unset_block(event):
    if event.reply_to_msg_id is None:
        await client.send_message(event.chat_id, "-Reply to a message!")
    else:
        try:
            replied = await event.get_reply_message()
            sender = replied.sender_id
            await client(functions.contacts.UnblockRequest(id=sender))
            full = await client(GetFullUserRequest(sender))
            await client.send_message(event.chat_id, f"-User {full.user.first_name} {full.user.last_name} unblocked")
        except ContactIdInvalidError:
            await client.send_message(event.chat_id, "-The provided contact ID is invalid")


@client.on(events.NewMessage(from_users=admin_list, pattern="-set name (.*)"))
async def set_name(event):
    name = event.pattern_match.group(1)
    await client(functions.account.UpdateProfileRequest(first_name=name))
    await client.send_message(event.chat_id, f"-Name changed to {name}")


@client.on(events.NewMessage(from_users=admin_list, pattern="-set bio (.*)"))
async def set_bio(event):
    bio = event.pattern_match.group(1)
    await client(functions.account.UpdateProfileRequest(about=bio))
    await client.send_message(event.chat_id, f"-Bio changed to {bio}")


@client.on(events.NewMessage(from_users=admin_list, pattern="-set list name (.*)"))
async def set_list_name(event):
    name = event.pattern_match.group(1)
    await r.rpush("list_name", name)
    await client.send_message(event.chat_id, f"-{name} added to list name")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset list name (.*)"))
async def unset_list_name(event):
    name = event.pattern_match.group(1)
    await r.lrem("list_name", 0, name)
    await client.send_message(event.chat_id, f"-{name} removed from list name")


@client.on(events.NewMessage(from_users=admin_list, pattern="-clear list name"))
async def clear_list_name(event):
    await r.delete("list_name")
    await client.send_message(event.chat_id, "-List name cleared")


@client.on(events.NewMessage(from_users=admin_list, pattern="-show list name"))
async def show_list_name(event):
    name_list = '\n'.join(await r.lrange("list_name", 0, -1))
    await client.send_message(event.chat_id, f"-List name:\n{name_list}")


@client.on(events.NewMessage(from_users=admin_list, pattern="-set change name"))
async def set_change_name(event):
    status = await r.set("change_name", "1")
    await client.send_message(event.chat_id, "-Change name turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset change name"))
async def unset_change_name(event):
    status = await r.set("change_name", "0")
    await client.send_message(event.chat_id, "-Change name turned off")


@client.on(events.NewMessage(from_users=admin_list, pattern="-set self destructing downloader"))
async def self_destructing_downloader(event):
    status = await r.set("self_destructing_downloader", "1")
    await client.send_message(event.chat_id, "-Self destructing downloader turned on")


@client.on(events.NewMessage(from_users=admin_list, pattern="-unset self destructing downloader"))
async def unset_self_destructing_downloader(event):
    status = await r.set("self_destructing_downloader", "0")
    await client.send_message(event.chat_id, "-Self destructing downloader turned off")


@client.on(events.NewMessage(func=lambda e: e.is_private and (e.photo or e.video) and e.media_unread))
async def self_destructing_downloader(event):
    status = await r.get("self_destructing_downloader")
    if status == "1":
        result = await event.download_media()
        await client.send_file("me", result, caption=f"-{event.sender.first_name} {event.sender.last_name} sent a file")


worker.start()
asyncio.get_event_loop().run_forever()
client.run_until_disconnected()
