import discord
from discord.ext import commands
import pandas as pd
from datetime import datetime
import pytz

emoji = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']
tz = pytz.timezone('America/Chicago')


class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot, target: int):
        self.bot = bot
        self._target_channel_id = target
        self._target_channel = self.bot.get_channel(target)  # Channel object
        self._target_message = None
        self._responses = []

        print(f'Target channel: {self._target_channel}')

    @commands.command(name='create')
    async def create_poll(self, ctx, args):
        self._responses = []
        num_options = int(args[0])

        # assume args is an int
        if num_options > 9:
            await ctx.send('Too many options')
            return

        question_txt = f'Question: {self.get_time()}'
        msg = await self._target_channel.send(question_txt)
        self._target_message = msg
        for i in range(num_options):
            await msg.add_reaction(emoji[i])

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        curr_time, netid, reaction = self.parse_raw_react_payload(payload)
        self._responses.append({'time': curr_time, 'netid': netid, 'reaction': reaction})
        await self.remove_reaction(payload)

    @commands.command(name='results')
    async def send_results(self, ctx):
        file_name = 'data/' + datetime.now(tz).strftime('%H-%M-%S') + '.csv'
        df = pd.DataFrame(self._responses)
        df.to_csv(file_name)

        with open(file_name, 'rb') as fp:
            await ctx.channel.send(file=discord.File(fp, 'poll_results.csv'))

    async def remove_reaction(self, payload: discord.RawReactionActionEvent):
        await self._target_message.remove_reaction(emoji=payload.emoji, member=payload.member)

    def parse_raw_react_payload(self, payload: discord.RawReactionActionEvent):
        curr_time = self.get_time()
        netid = self.parse_netid(payload.member.nick)
        react = payload.emoji

        print(curr_time)
        print(netid)
        print(react)
        return curr_time, netid, react

    def parse_netid(self, user_nickname):
        return user_nickname[user_nickname.find('(') + 1:user_nickname.find(')')]

    def get_time(self):
        return datetime.now(tz).strftime('%H:%M:%S CST')
