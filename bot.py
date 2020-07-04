import base64
import requests
from typing import Optional
from discord.ext import commands

PREFIX = '!'
client = commands.Bot(command_prefix=PREFIX)
base64_bot_token = 'TnpJNE1qSTJPVFF3TVRNM01qUXlOamszLlh2NW9Sdy4zaVdzN3FGeFBVMlZOYXNiVXFFcmM4cnpfZ00='
bot_token = (base64.b64decode(base64_bot_token)).decode()
PLAYER_ROLE = "Waifu Protector"
players = []  # type: List[Player]
""" A list containing all the Player objects, representing the players in the game. """


class Player(object):
    def __init__(self, nickname):
        self.nickname = nickname
        self.score = 0
        self.has_voted = False


def get_member_by_letter(letter: str) -> Optional[Player]:
    """
    Return the matching player by the first letter of it's nickname.
    :param letter: The first letter of the user's nickname.
    :return: Player object.
    """
    for player in players:
        if player.nickname[0].lower() == letter.lower():
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
        prettified_score += f'{player.nickname} {player.score}\n'
    return prettified_score


@client.event
async def on_ready():
    """
    called after the bot has connected online
    :return: None
    """
    for guild in client.guilds:
        await guild.text_channels[0].send("BRACE YOURSELVES DEGENERATES! IT'S SHOW TIME!!!!")

    # Initialize players
    for member in client.get_all_members():
        if PLAYER_ROLE in [role.name for role in member.roles]:
            players.append(Player(nickname=member.nick))


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
async def vote(ctx, user_vote: str):
    """
    Registers a vote from a user.
    :param ctx: Context
    :param user_vote: The user's vote.
    :return: None
    """
    user = ctx.author
    voted_user = get_member_by_letter(user_vote[0])
    if voted_user:
        voter = get_member_by_letter(user.nick[0])
        voter.has_voted = True  # Update user's vote state to True.
        voted_user.score += 1  # Increment score of the chosen user.
        print(f"{user} your vote has been registered!")

        # Check if all users have voted.
        for player in players:
            if not player.has_voted:
                return

        # Update all users' vote state to False.
        for player in players:
            player.has_voted = False

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
    print("Showing score")
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
        if player.score > max_points:
            winners.clear()
            winners.append(player)
            max_points = player.score
        elif player.score == max_points:
            winners.append(player)

    if len(winners) > 1:
        winner_names = ""
        for winner in winners:
            winner_names += " " + winner.nickname
        results = f"the winners are {winner_names}!!!"
    else:
        results = f"the winner is {winners[0]}!!!"
    gif = "https://giphy.com/gifs/thebachelor-the-bachelor-thebachelorabc-bachelorabc-EBolRO7z50KTOn85Pi"
    await ctx.send(results + "\n" + gif)


@client.command(pass_context=True)
async def reset(ctx):
    """
    Resets the players' scores.
    :param ctx:
    # :return: None
    """
    for player in players:
        player.score = 0


client.run(bot_token)
