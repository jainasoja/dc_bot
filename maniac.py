import discord
import os
import asyncio
import yt_dlp
from dotenv import load_dotenv

def run_bot():
    load_dotenv()
    TOKEN = os.getenv('discord_token')
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    voice_clients = {}
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    song_queue = {}

    ffmpeg_options = {'options': '-vn'}

    @client.event
    async def on_ready():
        print(f'{client.user} on kuulolla!')

    @client.event
    async def on_message(message):
        if message.content.startswith("!!play"):
            try:
                if(message.author.voice == None):
                    await message.channel.send("Et oo viä kanaval!")
                    return
                voice_client = await message.author.voice.channel.connect()
                voice_clients[voice_client.guild.id] = voice_client
            except Exception as e:
                print(e)

            try:
                url = message.content.split()[1]

                guild_id = message.guild.id

                if guild_id not in song_queue:
                    song_queue[guild_id] = []

                song_queue[guild_id].append(url)

                if not voice_client.is_playing():
                    await play_next_song(voice_client, guild_id)
            except Exception as e:
                print(e)


        if message.content.startswith("!!pause"):
            try:
                voice_clients[message.guild.id].pause()
            except Exception as e:
                print(e)
        
        if message.content.startswith("!!resume"):
            try:
                voice_clients[message.guild.id].resume()
            except Exception as e:
                print(e)
        
        if message.content.startswith("!!stop"):
            try:
                voice_clients[message.guild.id].stop()
                await voice_clients[message.guild.id].disconnect()
            except Exception as e:
                print(e)

        if message.content.startswith("!!help"):
            try:
                await message.channel.send("Commands: \n!!play <url> \n!!pause \n!!resume \n!!stop \n!!skip")
            except Exception as e:
                print(e)
        
        if message.content.startswith("!!skip"):
            try:
                voice_clients[message.guild.id].stop()
            except Exception as e:
                print(e)
         
    async def play_next_song(voice_client, guild_id):
        if song_queue[guild_id]:
            url = song_queue[guild_id].pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            song = data['url']
            source = discord.FFmpegPCMAudio(song, **ffmpeg_options)
            voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(voice_client, guild_id), loop))
        else:
            await voice_client.disconnect()
            print("soimassa")


    client.run(TOKEN)

