import os
import csv
import io
import discord
from datetime import datetime
from dotenv import load_dotenv

from discord.ext import commands
from constants import ROLE, BIG_DAYS_VALUE

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents = intents)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')


async def get_roles_dict(roles):
    roles_set = {ROLE.get_broad_role(role.name) for role in roles}

    roles_dict = {}
    for role in [ROLE.PLAYER, ROLE.PATRON]:
        roles_dict[role] = 1 if role in roles_set else 0

    return roles_dict


async def classify_members(members):
    return {member: await get_roles_dict(member.roles) for member in members}


async def get_latest_time(a, b):
    if a is None and b is None:
        return a
    elif a is None:
        return b
    elif b is None:
        return a
    else:
        return max(a, b)


async def fetch_members_last_messages(channels, members):
    member_last_message = {member:None for member in members}

    for channel in channels:
        #todo: replace by channel type checking
        for member in members:
            msg = None
            try:
                #todo: test for replies as well
                msg = await channel.history().get(author__name=member.display_name)
            except Exception as e:
                pass

            if msg is not None:
                msg_timestamp = msg.edited_at if msg.edited_at is not None else msg.created_at
                member_last_message[member] = await get_latest_time(member_last_message[member], msg_timestamp)

    return member_last_message


async def get_days_between(d1, d2):
    if d1 is None or d2 is None:
        return BIG_DAYS_VALUE
    delta = d1 - d2
    return delta.days


async def compute_days_since_last_message(members_last_messages):
    current_time = datetime.utcnow()
    members_days_since = {}
    for member in members_last_messages.keys():
        days_between = await get_days_between(current_time, members_last_messages[member])
        members_days_since[member] = days_between
    return members_days_since


async def merge(members_roles, members_last_messages, members_days_since_last_message):
    merged_list = []
    for member in members_roles.keys():
        merged_value = {
            "name": member.display_name,
            "is_player": members_roles[member][ROLE.PLAYER],
            "is_patron": members_roles[member][ROLE.PATRON],
            "last_message_timestamp": members_last_messages[member],
            "days_since_last_message": members_days_since_last_message[member]
        }
        merged_list.append(merged_value)

    return merged_list


@bot.command(name='mr')
async def member_report(ctx):
    guild = ctx.guild

    channels = guild.channels
    members = guild.members

    members_roles = await classify_members(members)
    members_last_messages = await fetch_members_last_messages(channels, members)
    members_days_since_last_message = await compute_days_since_last_message(members_last_messages)

    members_info = await merge(members_roles, members_last_messages, members_days_since_last_message)

    csv_headers = ["name","is_player","is_patron","last_message_timestamp","days_since_last_message"]
    writer_file = io.StringIO()
    writer = csv.DictWriter(writer_file, fieldnames=list(csv_headers))
    writer.writeheader()
    for member_info in members_info:
        writer.writerow(member_info)
    writer_file.seek(0)

    await ctx.send(file=discord.File(io.BytesIO(writer_file.read().encode()), filename="data.csv"))
    await ctx.send("done")

bot.run(TOKEN)