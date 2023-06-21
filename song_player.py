import random

import discord
import youtube_dl as youtube_dl
from discord.ext import commands
import asyncio

from database_functions import *

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ffmpeg_options = {
    'options': '-vn -fflags +discardcorrupt -ignore_unknown -dn -sn -ab 32000',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

OWNER_CLIENT_ID = "921646960946073600"


# Referenced from the Author of discord.py Rapptz
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(executable="E:/ffmpeg-2021-06-02-git-071930de72-full_build/bin/ffmpeg.exe",
                                          source=filename, **ffmpeg_options), data=data)


class song_commands(commands.Cog, name="song_commands"):

    def __init__(self, bot):
        self.bot = bot
        with open('songs.json') as f:
            data = json.load(f)
            self.song_data = data
        print(f"Loaded {len(self.song_data)} songs...")
        random.shuffle(self.song_data)
        self.song_index = 0

    @commands.command(name="playgame", aliases=['pg'], pass_context=True)
    async def play_game(self, ctx):

        play_amount = 0
        args = ctx.message.content.split(" ")
        if len(args) > 2:
            play_amount += int(args[1])
        voice_channel = ctx.author.voice.channel
        try:
            await voice_channel.connect()
            await ctx.send("Playing a song in a few seconds, hold tight!")
        except Exception as e:
            print(e)
            await ctx.send("Starting up another game!")
        await asyncio.sleep(1)

        if self.song_index == len(self.song_data) - 1:
            self.song_index = 0
            random.shuffle(self.song_data)
            await ctx.send("All unique songs have been played, shuffling the list now")

        def check_anime_song(m):
            anime_name = m.content.lower()
            return anime_name == music_to_guess.lower() and m.channel == ctx.channel

        while True:
            try:
                music_to_guess = self.song_data[self.song_index][0]
                music_url = self.song_data[self.song_index][1]

                player = await YTDLSource.from_url(music_url, loop=self.bot.loop,
                                                   stream=True)
                try:
                    if ctx.voice_client is not None:
                        ctx.voice_client.play(player, after=lambda x: print('Player error: %s' % x) if x else None)
                except Exception as e:
                    print("error playing song:", e)
                    self.song_index += 1
                    continue
                await ctx.send(
                    "Try guessing this anime by typing in this channel (anyone can try)! You got 25 seconds.")

                user_msg = await self.bot.wait_for('message', check=check_anime_song, timeout=25.0)
                add_points(str(user_msg.author.id), 1)
                await ctx.send("Nice, you guessed the correct anime ({})!".format(
                    music_to_guess.title()))

                self.song_index += 1

                if self.song_index == len(self.song_data) - 1:
                    self.song_index = 0
                    random.shuffle(self.song_data)
                    await ctx.send("All unique songs have been played, shuffling the list now")

                music_to_guess = self.song_data[self.song_index][0]
                music_url = self.song_data[self.song_index][1]

                ctx.voice_client.stop()
                await asyncio.sleep(1)
            except Exception as e:
                print(e)
                if "Video unavailable" in str(e) or "Private video" in str(e):
                    await ctx.send(
                        f"{music_to_guess} has a broken link ({self.song_data[self.song_index][1]}), pls fix!")
                else:
                    await ctx.send(
                        "Sorry, you took to long to guess do !playgame to start again, the song was from {}.".format(
                            music_to_guess.title()))
                self.song_index += 1
                ctx.voice_client.stop()

    @commands.command(name="playsong", pass_context=True)
    async def play_song(self, ctx):
        voice_channel = ctx.author.voice.channel
        try:
            await voice_channel.connect()
            await ctx.send("Playing a random anime song in my database, hold tight!")
        except Exception as e:
            print(e)
            ctx.voice_client.stop()
            await ctx.send("Starting up another random anime song!")
        await asyncio.sleep(1)

        rand_idx = random.randint(0, len(self.song_data) - 1)
        music_url = self.song_data[rand_idx][1]

        player = await YTDLSource.from_url(music_url, loop=self.bot.loop,
                                           stream=True)
        ctx.voice_client.play(player, after=lambda x: print('Player error: %s' % x) if x else None)

    @commands.command(name="leavegame", pass_context=True)
    async def leave_vc(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.send("Goodbye!")




    @commands.command(name="query_song", aliases=['qs'], pass_context=True)
    async def query_song(self, ctx):
        args = ctx.message.content.split(" ")
        if len(args) < 2:
            await ctx.send("Format: !query_song <anime name>")
            return
        links = ""
        queried_name = " ".join(args[1:]).lower()
        total_songs = 0
        for data in self.song_data:
            anime_name = data[0].lower()
            if queried_name in anime_name:
                # youtube_vid = await YTDLSource.from_url(data[1], stream=True)
                links += anime_name.title() + f": " + data[1] + "\n\n"  # Links
                total_songs += 1

        await ctx.send(
            f"All Song Links from the queried {queried_name.title()}:\n```Total Songs Found: {total_songs}\n\n{links}```")







async def setup(bot):
    await bot.add_cog(song_commands(bot))
