import base64
import requests
from typing import Optional
from discord.ext import commands

PREFIX = '!'
client = commands.Bot(command_prefix=PREFIX)
base64_bot_token = 'TnpJNE1qSTJPVFF3TVRNM01qUXlOamszLlh2NW9Sdy4zaVdzN3FGeFBVMlZOYXNiVXFFcmM4cnpfZ00='
bot_token = (base64.b64decode(base64_bot_token)).decode()
players = []  # type: List[Player]
""" A list containing all the Player objects, representing the players in the game. """


class Player(object):
    def __init__(self, mention_string):
        self.mention_string = mention_string
        self.round_score = 0
        self.total_score = 0
        self.has_voted = False


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


def update_players(guild):
    """
    updates the player pool
    :param guild: the guild being updated
    :return: None
    """
    players.clear()
    for member in guild.voice_channels[0].members:
        players.append(Player(mention_string=member.mention))


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
    response = requests.get("https://mywaifulist.moe/random")
    # url = "https://mywaifulist.moe/waifu/jiao-sun"
    await ctx.send("{} has a new waifu!! \n".format(user) + response.url)


@client.command(pass_context=True)
async def reset(ctx):
    """
    reset the score and the players
    :return: None
    """
    guild = ctx.guild
    update_players(guild)


@client.command(pass_context=True)
async def remove(mention_string):
    """
    removes a player from game
    :return: None
    """
    player = get_player_by_mention_string(mention_string)
    if player in players:
        players.remove(player)


@client.command(pass_context=True)
async def add(player):
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
    if not voter.has_voted and voted_player:
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

    else:
        await ctx.send("This user is more imaginary then your girlfriend!")


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
            winner_names += " " + winner.name
        results = f"the winners are {winner_names}!!!"
    else:
        results = f"the winner is {winners[0]}!!!"
    gif = "https://giphy.com/gifs/thebachelor-the-bachelor-thebachelorabc-bachelorabc-EBolRO7z50KTOn85Pi"
    await ctx.send(results + "\n" + gif)


client.run(bot_token)
