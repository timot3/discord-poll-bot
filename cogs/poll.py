import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import pandas as pd
from datetime import datetime
import pytz
import emoji as em
from slugify import slugify
from collections import deque


emoji = [':one:', ':two:', ':three:', ':four:', ':five:', ':six:', ':seven:', ':eight:', ':nine:']
tz = pytz.timezone('America/Chicago')


class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot, target: int):
        self.bot = bot
        self._target_channel_id = target
        self._target_channel = self.bot.get_channel(target)  # Channel object
        self._target_message = None
        self._responses = []
        self._users_responded = set()
        self._question_text = ''
        self._queue = deque([])

        print(f'Target channel: {self._target_channel}')

    @commands.command(name='create')
    @has_permissions(administrator=True)
    async def create_poll(self, ctx, *arg):
        # Clear last poll's responses
        self._responses = []
        self._users_responded = set()
        self._question_text = ''

        num_options = int(arg[0])  # Number of responses is based on the first number
        # Question text always comes after the number of options
        self._question_text = ' '.join(word for word in arg[1:])

        if num_options > 9:
            await ctx.send('Too many options')
            return

        message_text = f'Question: {self.get_time()}\n{self._question_text}'
        msg = await self._target_channel.send(message_text)
        self._target_message = msg
        for i in range(num_options):
            await msg.add_reaction(em.emojize(emoji[i], use_aliases=True))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Don't care about bot reactions
        if payload.member.bot or payload.message_id != self._target_message.id:
            return
        curr_time, netid, uuid, reaction = self.parse_raw_react_payload(payload)
        if netid not in self._users_responded:
            self._users_responded.add(netid)
            self._responses.append({'time': curr_time, 'netid': netid, 'uuid': uuid, 'reaction': reaction})
        else:
            entry = next(i for i in self._responses if i['uuid'] == uuid)
            entry['reaction'] = reaction
        await self.remove_reaction(payload)

    @commands.command(name='results')
    @has_permissions(administrator=True)
    async def send_results(self, ctx):
        file_name = f'data/{slugify(self._question_text)}.csv'
        df = pd.DataFrame(self._responses)
        df.to_csv(file_name)
        df.sort_values('time')

        # Calculate percentages of responses
        response_percents = df['reaction'].value_counts(normalize=True) * 100

        with open(file_name, 'rb') as fp:
            file_name = self._question_text
            if len(file_name) == 0:  # If the question has no text
                file_name = 'question'

            await ctx.channel.send('Results:\n' + str(response_percents), file=discord.File(fp, f'{file_name}.csv'))

    @commands.command(name='close')
    @has_permissions(administrator=True)
    async def poll_close(self, ctx):
        await self._target_message.delete()
        self._target_message = None

    async def remove_reaction(self, payload: discord.RawReactionActionEvent):
        await self._target_message.remove_reaction(emoji=payload.emoji, member=payload.member)

    def parse_raw_react_payload(self, payload: discord.RawReactionActionEvent):
        curr_time = self.get_time()
        netid = self.parse_netid(payload.member)
        print(netid)
        uuid = payload.user_id
        # print(payload.emoji.name)
        react = em.demojize(payload.emoji.name)[-2]  # Get the last character of emoji, ignore ":" char (1,2,3 etc)
        print(react)
        return curr_time, netid, uuid, react

    def parse_netid(self, user: discord.Member):
        user_name = user.display_name
        return user_name[user_name.find('(') + 1:user_name.find(')')]

    def get_time(self):
        return datetime.now(tz).strftime('%H:%M:%S CST')
