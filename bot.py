import discord
from discord.ext import commands


client = commands.Bot(command_prefix= '#')
bot_token = 'NzI4MjI2OTQwMTM3MjQyNjk3.Xv5iTg.AZ-p4jRNb9D_8p544USGS_dUJ9E'

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
    await guild.text_channels[0].send(f"oh shit {member} has joined. like we need another degenerate in here :unamused:")

@client.event
async def on_message(message):
    """
    called when a user writes a msg
    :param message: message writen
    :return: (name, msg)
    """
    name = message.author
    msg = message.content
    return (name,msg)

@client.event
async def on_member_remove(member):
    """
    called when a member leaves the server
    :param member: the member that left
    :return: None
    """
    guild = member.guild
    await guild.text_channels[0].send(f"fewwwww. {member} is gone. finally!!")

@client.command(pass_context=True)
async def ping(ctx):
    """
    shows that the server is alive and running, called when a user type #ping
    :param ctx: Context
    :return: None
    """
    await ctx.send("Pong!")

client.run(bot_token)