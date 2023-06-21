# Importing libraries and other required dependencies

import random
import discord
import youtube_dl as youtube_dl
from discord.ext import commands
import asyncio
from database_functions import *
from table2ascii import table2ascii as t2a, PresetStyle



# Own discord id
OWNER_CLIENT_ID = "921646960946073600"

class Commands(commands.Cog, name="commands"):

    def __init__(self, bot):
        # Loading instance of songs, characters and trivia questions when initializing self
        self.bot = bot

        # loading characters
        with open('E:\python bot\AnimeQuizBot\\anime_characters.json') as f:
            data = json.load(f)
            self.anime_char_data = data
        print(f"Loaded {len(self.anime_char_data)} anime characters...")
        random.shuffle(self.anime_char_data)
        self.anime_char_index = 0
        self.in_game = {}

        # loading questions
        self.trivia_index = 0
        with open('E:\python bot\AnimeQuizBot\\trivia_questions.json') as f:
            data = json.load(f)
            self.anime_trivia_questions = data
        print(f"Loaded {len(self.anime_trivia_questions)} trivia questions...")
        random.shuffle(self.anime_trivia_questions)

        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None


    @commands.command(name="hello", pass_context=True)
    async def handle_hello(self, ctx):
        add_user_to_db(str(ctx.message.author.id),str(ctx.message.author.name))
        await ctx.send("Player confirmed")


    @commands.command(name="character", aliases=['char', 'c', 'C'], pass_context=True)
    async def rand_char(self, ctx):
        if self.in_game.get(ctx.author.id):
            await ctx.send("You are already in a game, please finish that one first.")
            return
        self.anime_char_index += 1
        if self.in_game.get(ctx.author.id) is None or not self.in_game.get(ctx.author.id):
            self.in_game[ctx.author.id] = True

        character = self.anime_char_data[self.anime_char_index]
        e = discord.Embed(title="Guess the Character")
        e.set_image(url=character['img'])

        def check(m):
            char_name = m.content.lower()
            if m.channel == ctx.channel:
                for n in character['name']:
                    if char_name == n.lower():
                        return True
            reversed_name = reversed(character['name'])
            return char_name == " ".join(character['name']).lower() or char_name == " ".join(reversed_name).lower() or \
                   (char_name == "skip" and m.author.id == ctx.author.id)

        await ctx.send(embed=e)

        try:
            user_msg = await self.bot.wait_for('message', check=check, timeout=25.0)
            if user_msg.content.lower() == "skip":
                await ctx.send(f"Skipped **{' '.join(character['name'])}** from "
                               f"**{character['anime']}**, {user_msg.author.name}")
            else:
                add_points(str(user_msg.author.id), 1,str(ctx.message.author.name))
                # add_character_to_inventory(user_msg.author.id, character)
                await ctx.send(
                    f"Nice, {user_msg.author.name} got the correct answer, you gain a point for guessing"
                    f" **{' '.join(character['name'])}** from the anime **{character['anime']}**!\n")
        except asyncio.TimeoutError:
            await ctx.send(f"You could not answer correctly in the time given {ctx.author.name}.\n"
                           f"The character was **{' '.join(character['name'])}** from the anime **{character['anime']}**")
        finally:
            self.in_game[ctx.author.id] = False
            if self.anime_char_index == len(self.anime_char_data) - 1:
                random.shuffle(self.anime_char_data)
                self.anime_char_index = 0


    @commands.command(name="trivia", aliases=['t', 'T'], pass_context=True)
    async def trivia(self, ctx):
        if self.in_game.get(ctx.author.id):
            await ctx.send("You are already in a game, please finish that one first.")
            return

        self.in_game[ctx.author.id] = True
        e = discord.Embed(title="Anime Trivia [{}]".format(ctx.author.name), color=discord.colour.Colour.teal(),
                          description="Pick one of the numbers or type out the answer.")
        e.set_thumbnail(url="https://cdn.discordapp.com/attachments/746519006961336370/942326792293851157/komi_scared"
                            ".jpg")

        trivia_question = self.anime_trivia_questions[self.trivia_index]
        self.trivia_index += 1
        question = trivia_question["question"]
        e.add_field(name="Question", value=f"```{question}```", inline=False)
        random.shuffle(trivia_question["answers"])
        answers = "```"
        answers_dict = {

        }
        correct_ans = {

        }
        for i, answer in enumerate(trivia_question["answers"]):
            answers_dict[f"{i + 1}"] = answer
            if answer == trivia_question["answer"]:
                correct_ans[f"{i + 1}"] = answer
        for key in answers_dict:
            answer = answers_dict[key]
            answers += f"\n{key}. {answer}"

        answers += "```"
        e.add_field(name="Possible Answers", value=answers, inline=False)

        def check(m):
            return m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        await ctx.send(embed=e)

        try:
            user_msg = await self.bot.wait_for('message', check=check, timeout=25.0)
            user_ans = user_msg.content.lower()
            ans = trivia_question["answer"]
            if user_ans == ans.lower() or correct_ans.get(user_ans) == ans:
                add_points(str(user_msg.author.id), 1,str(ctx.message.author.name))
                await ctx.send(
                    "Nice! {} got the correct answer ({}).".format(user_msg.author.name, trivia_question["answer"]))
            else:
                await ctx.send("Wrong Answer, {}.".format(user_msg.author.name, trivia_question["answer"]))
        except asyncio.TimeoutError:
            await ctx.send(f"You could not answer correctly in the time given {ctx.author.name}.")
        finally:
            self.in_game[ctx.author.id] = False
            if self.trivia_index == len(self.anime_trivia_questions) - 1:
                random.shuffle(self.anime_trivia_questions)
                self.trivia_index = 0


    # @commands.command(name="stats_all", aliases=['s', 'S'], pass_context=True)
    # async def stats_all(self, ctx):
    #         ranks=get_stats()
    #         rankings=""
    #         i=1
    #         for x in ranks.items():
    #             rankings+=f"" + str(i) + "    " + x[1]["Name"].split()[0] + " "*(40-len(str(x[1]["Name"].split()[0]))) + str(x[1]["points"]) +"\n"
    #             i+=1
    #         await ctx.send(rankings)
    #         return
    @commands.command(name="stats", aliases=['st', 'ST'], pass_context=True)
    async def stats(self, ctx):
            ranks=get_stats()
            e = discord.Embed(title="Top Ten in Rankings", color=discord.colour.Colour.teal())
            e.set_thumbnail(url="https://cdn.discordapp.com/attachments/746519006961336370/942326792293851157/komi_scared"
                            ".jpg")
            # answers += f"\n{key}. {answer}

            rankings="```"
            body_generated=[]
            i=1
            for x in ranks.items():
                rankings+=f"\n{i}. {str(x[1]['Name'].split()[0])}   {str(x[1]['points'])}"
                body_generated.append([i,str(x[1]['Name'].split()[0]),str(x[1]['points'])])
                i+=1
                if(i==11):
                    break
            rankings+="```"
            # e.add_field(name="Ranking", value=rankings, inline=False)

            output= t2a(
                header=["Rank","Name","Points"],
                body=body_generated,
                style=PresetStyle.thin_compact
            )

            final_output=f"```\n{output}\n```"

            e.add_field(name="Ranking", value=final_output, inline=False)
            await ctx.send(embed=e)
            return
    


# In your command:
# output = t2a(
#     header=["Rank", "Team", "Kills", "Position Pts", "Total"],
#     body=[[1, 'Team A', 2, 4, 6], [2, 'Team B', 3, 3, 6], [3, 'Team C', 4, 2, 6]],
#     style=PresetStyle.thin_compact
# )

# await ctx.send(f"```\n{output}\n```")
    


async def setup(bot):
    await bot.add_cog(Commands(bot))
