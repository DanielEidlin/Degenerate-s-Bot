from discord.ext import commands

client = commands.Bot(command_prefix='#')
bot_token = 'NzI4MjI2OTQwMTM3MjQyNjk3.Xv5oRw.3iWs7qFxPU2VNasbUqErc8rz_gM'
user_score = {}


def get_member_by_letter(letter):
    """
    Return the matching user by the first letter.
    :param letter: The first letter of the user's nickname.
    :return: The string of the user's nickname.
    """
    for user in user_score:
        if user[0].lower() == letter.lower():
            return user


@client.event
async def on_ready():
    """
    called after the bot has connected online
    :return: None
    """
    for guild in client.guilds:
        await guild.text_channels[0].send("BRACE YOURSELVES DEGENERATES! IT'S SHOW TIME!!!!")

    global user_score
    user_score = {member.nick: 0 for member in client.get_all_members() if
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
    random = "random"
    url = f"https://mywaifulist.moe/{random}"
    await ctx.send(f"{user} has a new waifu!!\n{url}")


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


@client.command(pass_context=True)
async def vote(ctx, user_vote):
    """
    Registers a vote from a user.
    :param ctx: Context
    :param user_vote: The user's vote.
    :return: None
    """
    user = ctx.author
    voted_user = get_member_by_letter(user_vote[0])
    user_score[voted_user] += 1
    print(f"{user} your vote has been registered!")
    await ctx.send(f"{user} your vote has been registered!")


@client.command(pass_context=True)
async def show_score(ctx):
    """
    Displays the current score.
    :param ctx: Context
    :return: None
    """
    print("Showing score")
    await ctx.send(user_score)


client.run(bot_token)
