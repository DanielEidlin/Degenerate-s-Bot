import base64
import discord
import requests
from discord.ext import commands

client = commands.Bot(command_prefix='!')
base64_bot_token = 'TnpJNE1qSTJPVFF3TVRNM01qUXlOamszLlh2NW9Sdy4zaVdzN3FGeFBVMlZOYXNiVXFFcmM4cnpfZ00='
bot_token = (base64.b64decode(base64_bot_token)).decode()
user_score = {}
"""
A dictionary that contains the user nickname as the key and his score and a state of vote as the value.
{nickname: [score, voted]}
"""


def get_member_by_letter(letter):
    """
    Return the matching user by the first letter.
    :param letter: The first letter of the user's nickname.
    :return: The string of the user's nickname.
    """
    for user in user_score:
        if user[0].lower() == letter.lower():
            return user


def prettifie_score():
    """
    Prettifie the score dict.
    :return: Prettified score dict.
    """
    # Prettifie score
    prettified_score = ""
    for user, val in user_score.items():
        prettified_score += '{} {}\n'.format(user, val[0])
    return prettified_score

@client.event
async def on_ready():
    """
    called after the bot has connected online
    :return: None
    """
    for guild in client.guilds:
        await guild.text_channels[0].send("BRACE YOURSELVES DEGENERATES! IT'S SHOW TIME!!!!")

    global user_score
    user_score = {member.nick: [0, False] for member in client.get_all_members() if
                  "Waifu Protector" in [role.name for role in member.roles]}


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
    if message.content.startswith('#'):
        await client.process_commands(message)
    else:
        pass

@client.command(pass_context=True)
async def ping(ctx):
    """
    shows that the server is alive and running, called when a user type #ping
    :param ctx: Context
    :return: None
    """
    await ctx.send("Pong!")


@client.command(pass_context=True)
async def vote(ctx, user_vote):
    """
    Registers a vote from a user.
    :param ctx: Context
    :param user_vote: The user's vote.
    :return: None
    """
    user = ctx.author
    user_score[user.nick][1] = True  # Update user's vote state to True.
    voted_user = get_member_by_letter(user_vote[0])  # Get the chosen user.
    if voted_user in client.get_all_members():
        user_score[voted_user][0] += 1  # Increment score of the chosen user.
    else:
        await ctx.send("This user is more imaginary then your girlfriend!")
    print(f"{user} your vote has been registered!")

    # Check if all users have voted.
    for member in user_score:
        if user_score[member][1] is False:
            return

    # Update all users' vote state to False.
    for member in user_score:
        user_score[member][1] = False

    # Send score.
    prettified_score = prettifie_score()
    await ctx.send(f"Here is the score:\n{prettified_score}")


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
    for user in user_score:
        if user_score[user][0] > max_points:
            winners.clear()
            winners.append(user)
            max_points = user_score[user][0]
        elif user_score[user][0] == max_points:
            winners.append(user)

    if len(winners) > 1:
        winner_names = ""
        for winner in winners:
            winner_names = winner_names + " "+ winner
        results = f"the winners are {winner_names}!!!"
    else:
        results = f"the winner is {winners[0]}!!!"
    gif = "https://giphy.com/gifs/thebachelor-the-bachelor-thebachelorabc-bachelorabc-EBolRO7z50KTOn85Pi"
    await ctx.send(results + "\n" + gif)


client.run(bot_token)
