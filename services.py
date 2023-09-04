from telethon.tl.functions.photos import DeletePhotosRequest


async def delete_profile_photo(client, limit=None):
    me = await client.get_profile_photos("me", limit=limit)
    await client(DeletePhotosRequest(me))
