import os
import boto
import discord
import requests
from typing import Optional
from bs4 import BeautifulSoup
from discord.ext import commands
from boto.s3.connection import S3Connection

PREFIX = '!'
client = commands.Bot(command_prefix=PREFIX)
# Setting `Watching ` status
await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Boku no Pico"))
try:
    # Try to get the config key from Heroku server when deploying.
    bot_token = S3Connection(os.environ['DISCORD_BOT_TOKEN'])
except boto.exception.NoAuthHandlerFound:
    # When running locally get the token from the local environment variable.
    bot_token = os.environ['DISCORD_BOT_TOKEN']
players = []  # type: List[Player]
""" A list containing all the Player objects, representing the players in the game. """


class Player(object):
    def __init__(self, mention_string):
        self.mention_string = mention_string
        self.round_score = 0
        self.total_score = 0
        self.has_voted = False
        self.has_generated = False
        self.last_generated_waifu = None


def get_player_by_mention_string(mention_string: str) -> Optional[Player]:
    """
    Return the matching player by the player display name.
    :param mention_string: The user's mention string.
    :return: Player object.
    """
    # The strip is needed because Discord has a stupid bug that sometimes the string contains ! and sometimes doesn't.
    stripped_mention_string = mention_string.replace("!", "")
    for player in players:
        stripped_player_mention_string = player.mention_string.replace("!", "")
        if stripped_player_mention_string == stripped_mention_string:
            return player

    return None


def prettifie_score() -> str:
    """
    Prettifie the score.
    :return: Prettified score string.
    """
    # Prettifie score
    prettified_score = ""
    for player in players:
        prettified_score += f'{player.mention_string} {player.total_score}\n'
    if prettified_score == "":
        prettified_score = "wow. no weebs today"
    return prettified_score


def end_round():
    """
    Calculate the round winners and increment their points.
    :return:
    """
    # Find round winner/s
    round_winners = []  # type: List[Player]
    highest_score = 0
    for player in players:
        if player.round_score > highest_score:
            round_winners.clear()
            round_winners.append(player)
            highest_score = player.round_score
        elif player.round_score == highest_score:
            round_winners.append(player)
            highest_score = player.round_score

    # Increment winners' score
    for winner in round_winners:
        winner.total_score += 1

    # Reset round score and vote state
    for player in players:
        player.round_score = 0
        player.has_voted = False
        player.has_generated = False


def update_players(guild):
    """
    updates the player pool
    :param guild: the guild being updated
    :return: None
    """
    players.clear()
    for member in guild.voice_channels[0].members:
        players.append(Player(mention_string=member.mention))


def fetch_waifu_data(user):
    """
    Generates a random waifu, extracts useful information about her/him and constructs an embed.
    :param user: The user who generated the waifu.
    :return: An embed.
    """
    # url = "https://mywaifulist.moe/waifu/jiao-sun"
    response = requests.get("https://mywaifulist.moe/random")
    soup = BeautifulSoup(response.text, 'html.parser')
    name = soup.find("meta", property="og:title")["content"]
    description = soup.find("meta", attrs={"name": "description"})["content"]
    image_url = soup.find("meta", property="og:image")["content"]

    embed = discord.Embed(
        title=name,
        description=description,
        color=user.color,
        url=response.url
    )
    embed.set_image(url=image_url)
    embed.set_author(name=user.display_name, icon_url=user.avatar_url)

    return embed


@client.event
async def on_ready():
    """
    called after the bot has connected online
    :return: None
    """
    for guild in client.guilds:
        await guild.text_channels[0].send("BRACE YOURSELVES DEGENERATES! IT'S SHOW TIME!!!!")

        # Initialize players
        update_players(guild)


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
    player = get_player_by_mention_string(user.mention)
    if player and not player.has_generated:
        player.has_generated = True
        embed = fetch_waifu_data(user)
        player.last_generated_waifu = embed
        await ctx.send("{} has a new waifu!! \n".format(user.display_name), embed=embed)
    else:
        await ctx.send(f"How could you betray your waifu?! :cry:\n", file=discord.File('assets/02.gif'))


@client.command(pass_context=True)
async def reset(ctx):
    """
    reset the score and the players
    :return: None
    """
    guild = ctx.guild
    update_players(guild)


@client.command(pass_context=True)
async def remove(ctx, mention_string):
    """
    removes a player from game
    :return: None
    """
    player = get_player_by_mention_string(mention_string)
    if player in players:
        players.remove(player)

    # Check if all users have voted.
    for player in players:
        if not player.has_voted:
            return

    end_round()
    # Send score.
    prettified_score = prettifie_score()
    await ctx.send(f"Here is the score:\n{prettified_score}")


@client.command(pass_context=True)
async def add(ctx, player):
    """
    adds a player to game
    :return: None
    """
    players.append(Player(mention_string=player))


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
    if message.content.startswith(PREFIX):
        await client.process_commands(message)
    else:
        pass


@client.command(pass_context=True)
async def ping(ctx):
    """
    shows that the server is alive and running, called when a user type !ping
    :param ctx: Context
    :return: None
    """
    await ctx.send("Pong!")


@client.command(pass_context=True)
async def vote(ctx, mention_string: str):
    """
    Registers a vote from a user.
    :param ctx: Context
    :param mention_string: The mention string of the user one has voted for.
    :return: None
    """
    user = ctx.author
    voter = get_player_by_mention_string(user.mention)
    voted_player = get_player_by_mention_string(mention_string)
    if voter and not voter.has_voted and voted_player:
        voter.has_voted = True  # Update user's vote state to True.
        voted_player.round_score += 1  # Increment score of the chosen user.

        # Check if all users have voted.
        for player in players:
            if not player.has_voted:
                return

        end_round()
        # Send score.
        prettified_score = prettifie_score()
        await ctx.send(f"Here is the score:\n{prettified_score}")

    elif voter.has_voted:
        await ctx.send(f"You have already voted! :rage:\n", file=discord.File('assets/illegal.jpg'))

    else:
        await ctx.send("This user is more imaginary than your girlfriend!")


@client.command(pass_context=True)
async def show_score(ctx):
    """
    Displays the current score.
    :param ctx: Context
    :return: None
    """
    prettified_score = prettifie_score()
    await ctx.send(prettified_score)


@client.command(pass_context=True)
async def finish(ctx):
    """
    gives the L
    :param ctx: Context
    :return: None
    """
    winners = []
    max_points = 0
    for player in players:
        if player.total_score > max_points:
            winners.clear()
            winners.append(player)
            max_points = player.total_score
        elif player.total_score == max_points:
            winners.append(player)

    if len(winners) > 1:
        winner_names = ""
        for winner in winners:
            winner_names += " " + winner.mention_string
        results = f"the winners are {winner_names}!!!"
    else:
        results = f"the winner is {winners[0].mention_string}!!!"
    await ctx.send(f"{results}\n", file=discord.File('assets/finish.gif'))


@client.command(pass_context=True)
async def sauce(ctx):
    """
    Sends user's last generated waifu to the sauce channel.
    :param ctx:
    :return:
    """
    user = ctx.author
    player = get_player_by_mention_string(user.mention)
    role_names = [role.name for role in user.roles]
    if "Waifu Protector" in role_names and player.last_generated_waifu:
        sauce_channel = client.get_channel(724375129152421888)
        await sauce_channel.send(embed=player.last_generated_waifu)
    elif "Waifu Protector" not in role_names:
        await ctx.send(
            f"403 Forbidden!\nIt looks like you don't have Waifu Protector permissions :man_shrugging:\n",
            file=discord.File('assets/403.gif'))
    else:
        await ctx.send(f"404 Waifu not found\n", file=discord.File('assets/404.jpg'))


client.run(bot_token)
