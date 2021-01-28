import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import os

from cogs.poll import Poll

TOKEN = os.environ['POLL_TOKEN'].strip()
# print(TOKEN.strip())

bot = commands.Bot(command_prefix='poll ', case_insensitive=True, help_command=None)


@bot.event
async def on_ready():
    # Log events to console.
    print('Bot online.')
    print("Name: {}".format(bot.user.name))
    print("ID: {}".format(bot.user.id))


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    # print('ping')
    await bot.process_commands(message)


@bot.command(name='set')
@has_permissions(administrator=True)
async def set_target_channel(ctx: discord.ext.commands.Context, args):
    if len(args) < 1:
        await ctx.send('Error: Need input channel id!')
        return
    # print('set target channel: ' + str(args))
    bot.add_cog(Poll(bot, int(args)))
    await ctx.send(f'Bound to <#{str(args)}>.')


bot.run(TOKEN)
