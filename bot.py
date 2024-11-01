from datetime import timezone
import discord
import httpx


from settings import DISCORD_TOKEN, RENDER_URL, BACKEND_URL, SYSTEM_TOKEN

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

client = discord.Client(intents=intents)

timeout = httpx.Timeout(timeout=30.0, read=30.0)

@client.event
async def on_message(message: discord.Message):
    global client
    if message.author == client.user:
        return

    data = create_dto(message)

    async with httpx.AsyncClient() as httpx_client:
        await httpx_client.post(f'{RENDER_URL}/discord/image', json=data, timeout=timeout)


@client.event
async def on_message_edit(before, after: discord.Message):
    global client
    if after.author == client.user:
        return

    data = create_dto(after)

    async with httpx.AsyncClient() as httpx_client:
        await httpx_client.post(f'{RENDER_URL}/discord/image', params={'update': True}, json=data, timeout=timeout)


def create_dto(message: discord.Message):

    if len(message.embeds) == 1 and message.embeds[0].type == 'gifv':
        # gif
        return {
            'message_id': message.id,
            'text': '' if message.clean_content == message.embeds[0].url else message.clean_content,
            'attachments': [message.embeds[0].thumbnail.url],
            'embeds': [],
            'guild': message.guild.id,
            'channel': message.channel.name,
            'author': message.author.display_name,
            'jump_url': message.jump_url,
            'avatar_url': message.author.display_avatar.url,
            'date': message.created_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }
    else:
        # regular message
        attachments = [attachment.url for attachment in message.attachments]
        return {
            'message_id': message.id,
            'text': message.clean_content,
            'attachments': attachments,
            'embeds': [{
                'title': e.title,
                'author': None if not e.author else {
                    'name': e.author.name,
                    'url': e.url,
                    'icon_url': e.author.icon_url
                },
                'type': e.type,
                'description': e.description,
                'thumbnail_url': e.thumbnail.url,
                'color': None if e.color == None else '#%02x%02x%02x' % (e.color.r, e.color.g, e.color.b),
                'url': e.url
            } for e in message.embeds],
            'guild': message.guild.id,
            'channel': message.channel.name,
            'author': message.author.display_name,
            'jump_url': message.jump_url,
            'avatar_url': message.author.display_avatar.url,
            'date': message.created_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        }


@client.event
async def on_message_delete(message):
    global client
    if message.author == client.user:
        return

    async with httpx.AsyncClient() as httpx_client:
        await httpx_client.delete(
            f'{BACKEND_URL}/discord/bot/images',
            params={
                'message_link': message.jump_url
            },
            headers={
                'Authorize': SYSTEM_TOKEN
            }
        )


def run():
    client.run(DISCORD_TOKEN)
