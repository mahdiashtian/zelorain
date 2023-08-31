from telethon.tl.functions.photos import DeletePhotosRequest


async def delete_profile_photo(client):
    me = await client.get_profile_photos("me", limit=1)
    await client(DeletePhotosRequest(me))
