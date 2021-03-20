import discord
from discord.ext import commands, tasks
import random
import time
from discord import FFmpegPCMAudio
import youtube_dl
import asyncio


client=commands.Bot(command_prefix='.',description="prefix > .",)

musics = {}
ytdl = youtube_dl.YoutubeDL()

@client.event
async def on_ready():
    print("BIP BOUP BIP {0.user}".format(client))
    ChangeStatus.start()

# .ping
@client.command()
async def ping(ctx):
    await ctx.send(f'tu as {round(client.latency*1000)}ms')

# .clear (ex : .clear 5)
@client.command()
async def clear(ctx, nombre : int):
	messages = await ctx.channel.history(limit = nombre).flatten()
	for message in messages:
		await message.delete()

# .mp 
@client.command()
async def mp(ctx):
    await ctx.author.send(".help")
  
# .kick (ex : .kick @jereeem1111)
@client.command()
@commands.has_permissions(kick_members = True)
async def kick(ctx, user : discord.User):
	await ctx.guild.kick(user)
	await ctx.send(f"{user} à été kick.")
	await ctx.send(embed = embed)
embed = discord.Embed(title = 'Banissement', description = "Une personne vient de disparaître !")
embed.set_thumbnail(url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Python.svg/1200px-Python.svg.png")

# activité du bot
status = [".help","Spotify","Discord","Atom","Visual Studio Code","Netflix","Google chrome","YouTube"]

@tasks.loop(seconds= 3600)
async def ChangeStatus():
    game = discord.Game(random.choice(status))
    await client.change_presence(status = discord.Status.idle, activity= game)

# MUSIQUE en local
# .local
@client.command(pass_context = True)
async def local(ctx):
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio ('votre musique.mp3') # telecharger une musique (mp3,mp4,wav)
        player = voice.play(source)
    else:
        await ctx.send("Tu n'est pas dans le channel")

# MUSIQUE avec youtube
class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]

# .play https://www.youtube.com/ 
@client.command()
async def play(ctx, url):
    client = ctx.guild.voice_client

    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        await ctx.send(f"Je lance : {video.url}")
        play_song(client, musics[ctx.guild], video)
        
# .leave
@client.command()
async def leave(ctx):
    client = ctx.guild.voice_client
    await client.disconnect()
    musics[ctx.guild] = []
    
# .resume
@client.command()
async def resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()

# .pause
@client.command()
async def pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()

# .skip
@client.command()
async def skip(ctx):
    client = ctx.guild.voice_client
    client.stop()

#.userinfo (ex : .userinfo @jereeem1111)
class userinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

@client.command()
async def userinfo(ctx, *, user: discord.User = None): 
    if user is None:
        user = ctx.author 
        roles = [role for role in ctx.author.roles]

    else:
        roles = [role for role in user.roles]

        embed = discord.Embed(title=f"{user}", colour=user.colour, timestamp=ctx.message.created_at)
        embed.set_author(name="Informations utilisateur : ")
        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Python.svg/1200px-Python.svg.png")
        embed.add_field(name="ID:", value=user.id, inline=False)
        embed.add_field(name="Nom d'utilisateur:",value=user.display_name, inline=False)
        embed.add_field(name="#:",value=user.discriminator, inline=False)
        embed.add_field(name="Status:", value=str(user.status).title(), inline=False)
        embed.add_field(name="meilleur role:", value=user.top_role, inline=False)
        embed.set_footer(text=f"Demandé par: {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        return

#@client.event
#async def on_message(message):
    #if message.channel.id == id de votre channel:
       #await message.add_reaction("❤️")

def setup(bot):
    bot.add_cog(userinfo(bot))

def play_song(client, queue, song):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url
        , before_options = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            play_song(client, queue, new_song)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), client.loop)

    client.play(source, after=next)


client.run('Le token de votre bot')


