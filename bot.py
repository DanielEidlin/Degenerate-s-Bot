import discord
import requests
from discord.ext import commands

client = commands.Bot(command_prefix='#')
bot_token = 'NzI4MjI2OTQwMTM3MjQyNjk3.Xv5oRw.3iWs7qFxPU2VNasbUqErc8rz_gM'


@client.event
async def on_ready():
    """
    called after the bot has connected online
    :return: None
    """
    for guild in client.guilds:
        await guild.text_channels[0].send("BRACE YOURSELVES DEGENERATES! IT'S SHOW TIME!!!!")


@client.event
async def on_member_join(member):
    """
    called when a member joins the server
    :param member: the member that joined
    :return: None
    """
    guild = member.guild
    await guild.text_channels[0].send(
        f"oh shit {member} has joined. like we need another degenerate in here :unamused:")


@client.command(pass_context=True)
async def generate(ctx):
    """
    :return: A URL that contains a random waifu
    """
    user = ctx.author
    response = requests.get("https://mywaifulist.moe/random")
    print(response.url)
    # url = "https://mywaifulist.moe/waifu/jiao-sun"
    await ctx.send("{} has a new waifu!! \n".format(user) + response.url)


@client.event
async def on_member_remove(member):
    """
    called when a member leaves the server
    :param member: the member that left
    :return: None
    """
    guild = member.guild
    await guild.text_channels[0].send("fewwwww. {} is gone. finally!!".format(member))


@client.event
async def on_message(message):
    if not message.content.startswith('#'):
        print("{},{}".format(message.author, message.content))
    else:
        await client.process_commands(message)


@client.command(pass_context=True)
async def ping(ctx):
    """
    shows that the server is alive and running, called when a user type #ping
    :param ctx: Context
    :return: None
    """
    await ctx.send("Pong!")


client.run(bot_token)
