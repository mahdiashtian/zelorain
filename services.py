from telethon.tl.functions.photos import DeletePhotosRequest


async def delete_profile_photo(client, limit=None):
    me = await client.get_profile_photos("me", limit=limit)
    await client(DeletePhotosRequest(me))


async def delete_sender_message(client, event):
    sender = await event.get_sender()
    me = await client.get_me()
    if me.id == sender.id:
        await client.delete_messages(event.chat_id, event.message.id)
