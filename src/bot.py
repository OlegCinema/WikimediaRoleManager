from discord.ext import commands
import discord

from datetime import datetime
import json
import asyncio

from src.botlike import LikerBot, UserHasZeroContributions, UserNotRegistered, UserHasBlocked
from src.file import File

class Bot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix=self.get_prefix)
        self.confing = File("config", format="json")
        self.list_of_users_logging = {}
        self.bot.remove_command("help")
        self._main_events()

    def read_config(self):
        return json.loads(self.confing.read_data())

    def run(self, token):
        self.bot.run(token)

    def get_prefix(self, client, message):
        data = self.read_config()
        return data[str(message.guild.id)]["prefix"]

    def _main_events(self):
        @self.bot.event
        async def on_ready():
            await self.bot.change_presence(activity=discord.Game("Wikipedia"))
            print("[Bot is started]: OK")

        @self.bot.command(pass_context=True)
        async def help(ctx):
            embed = discord.Embed(
            colour = discord.Colour.orange()
            )

            embed.set_author(
                name="WikipediaDiscordBot", url="https://wikipedia.org", 
                icon_url="https://upload.wikimedia.org/wikipedia/commons/6/63/Wikipedia-logo.png"
            )
            embed.add_field(name="Краткая информация", value=
            "Этот бот используется на сервере русской Википедии. " +
            "Узнать список команд можно на странице разработчика в Github: " +
            "https://github.com/OlegCinema/WikipediaDiscordBot"
            )
            embed.add_field(name="Функции", value=
            "1) Подтверждение новых пользователей на сервере и " +
            "автоматизация некоторых рутинных задач во время верификации. \n" +
            "2) Добавление в тематические каналы при помощи реакций."
            )

            await ctx.channel.send(embed=embed)

        @self.bot.event
        async def on_guild_join(guild):
            data = self.read_config()
            if (str(guild.id) not in data):
                data[str(guild.id)] = {
                    "moderator_channel": None,
                    "main_role": None,
                    "moderators_role": None,
                    "join_channel_id": None,
                    "reactions": {
                        "wikipedia": None
                    },
                    "message_id": None,
                    "message_channel": None,
                    "time_adding": str(datetime.now()),
                    "owner": str(guild.owner),
                    "created_at": str(guild.created_at),
                    "prefix": "$",
                    "bot_name": "OlegCinema" # Name of your bot.
                }
            self.confing.re_write(json.dumps(data, indent=4))


        async def is_moderator(ctx):
            data = self.read_config()
            if ctx.author.top_role.id == int(data[str(ctx.guild.id)]["moderators_role"]):
                return True

            return False

        @commands.check(is_moderator)
        @self.bot.command()
        async def change_prefix(ctx, prefix):
            data = self.read_config()
            data[str(ctx.guild.id)]["prefix"] = prefix

            self.confing.re_write(json.dumps(data, indent=4))

        @commands.check(is_moderator)
        @self.bot.command()
        async def get_login_users(ctx):
            try:
                if self.list_of_users_logging[str(ctx.guild.id)]["list_verific"]:
                    await ctx.send(
                        "Верифицирующихся пользователей: {0}\n\n".format(len(self.list_of_users_logging[str(ctx.guild.id)]["list_verific"])) +
                        "```{0}```".format(json.dumps(self.list_of_users_logging[str(ctx.guild.id)]["list_verific"], indent=4, ensure_ascii=False))
                    )
                    return
                await ctx.send("Пользователей в процессе верификации нет.")
            except KeyError:
                await ctx.send("Пользователей в процессе верификации нет.")

        @commands.check(is_moderator)
        @self.bot.command()
        async def set_login_channel(ctx, channel_id):
            data = self.read_config()
            if channel_id.isdigit():
                data[str(ctx.guild.id)]["join_channel_id"] = int(channel_id)
                self.confing.re_write(json.dumps(data, indent=4))
                return

            await ctx.send("Возникла ошибка при выполнении команды. Пожалуйста, введите её ещё раз, следуя инструкции.")

        @commands.check(is_moderator)
        @self.bot.command()
        async def set_moderator_role(ctx, role_id):
            data = self.read_config()
            if role_id.isdigit():
                data[str(ctx.guild.id)]["moderators_role"] = int(role_id)
                self.confing.re_write(json.dumps(data, indent=4))
                return

            await ctx.send("Возникла ошибка при выполнении команды. Пожалуйста, введите её ещё раз, следуя инструкции.")

        @commands.check(is_moderator)
        @self.bot.command()
        async def set_checking_role(ctx, role_id):
            data = self.read_config()
            if role_id.isdigit():
                data[str(ctx.guild.id)]["main_role"] = int(role_id)
                self.confing.re_write(json.dumps(data, indent=4))
                return

            await ctx.send("Возникла ошибка при выполнении команды. Пожалуйста, введите её ещё раз, следуя инструкции.")

        @commands.check(is_moderator)
        @self.bot.command()
        async def add_user_blacklist(ctx, user_id):
           if ctx.guild.id == 633673794468446270:
                blacklist = File("blacklist")
                if user_id in blacklist.read_data():
                   await ctx.send("Пользователь уже есть в чёрном списке!")
                   return 
                blacklist.write_data(f"{user_id} ({ctx.guild.get_member(int(user_id)).name})\n")
                await ctx.send("Пользователь был добавлен в чёрный список.")

        @commands.check(is_moderator)
        @self.bot.command()
        async def remove_user_blacklist(ctx, user_id):
           if ctx.guild.id == 633673794468446270:
                blacklist = File("blacklist")
                if user_id not in blacklist.read_data():
                   await ctx.send("Пользователя нет в чёрном списке!")
                   return 
                data = blacklist.read_data().replace(f"{user_id} ({ctx.guild.get_member(int(user_id)).name})\n", "")
                await ctx.send("Пользователь был убран из чёрного списка.")
                blacklist.re_write(data)

        @commands.check(is_moderator)
        @self.bot.command()
        async def get_blacklist(ctx):
            if ctx.guild.id == 633673794468446270:
                blacklist = File("blacklist")
                if len(blacklist.read_data()) > 5:
                    await ctx.send(f"``{blacklist.read_data()}``")
                else:
                    await ctx.send("В чёрном списке никого нет.")


class MainBot(Bot):
    def __init__(self):
        super().__init__()

        self._events()

    def _get_like(self, lang, user):
        self.like = LikerBot(lang, user)
        return self.like.like_random_revision()

    def _get_message(self):
        self.read_config()[str(633673794468446270)]["message_id"]

    async def _send_hello_msg(self, member):
        await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(
            f"{member.mention}: приветствуем вас в чате сообщества Викимедиа, {member.name}!\n" +
            "На этом канале можно пройти автоматическую верификацию аккаунта, чтобы получить доступ к чату. \n" +
            "Для автоматической верификации необходимо иметь аккаунт в русской Википедии. \n\n" +
            "Пожалуйста, отправьте ответное сообщение с названием своего аккаунта (никнейма) в Википедии без слова ``Участник:``." +
            "Если вы не зарегистрированы в Википедии, отправьте сообщение с текстом ``нет``."
        )

    async def _send_stop_check(self, member):
        await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(
            f"{member.mention}: к сожалению, автоматическая верификация невозможна (либо вы ввели ``нет``, " +
            "либо возникла проблема с вашим аккаунтом), поэтому ваше " +
            "подтверждение пройдёт в ручном режиме. Пожалуйста, дождитесь сообщения модератора."
        )

    async def _check_ok(self, member):
        role = member.guild.get_role(int(self.read_config()[str(member.guild.id)]["main_role"]))
        await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(f"{member.mention} успешно верифицирован.")
        await member.add_roles(role)
        del self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]

    async def _check_user(self, member):
        bot_name = self.read_config()[str(member.guild.id)]["bot_name"]
        await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(
            f"{member.mention}: большое спасибо! Теперь можем приступать к верификации.\n" +
            f"Участник Википедии **{bot_name}** только что поблагодарил одну из ваших правок. " +
            "Вам необходимо в ответном сообщение отправить либо номер диффа, либо ссылку на этот дифф, " +
            "либо название статьи, в которой находится отблагодарённая правка."
        )
            
        msg = (await self.bot.wait_for('message', check=lambda msg: member == msg.author and member.guild.id == msg.guild.id)).content

        if ((self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]["diff"]["id"] in msg) or 
            (self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]["diff"]["name"].find(msg) != -1) and len(msg) > 4):
            await self._check_ok(member)
            return

        else:
            del self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]
            await self._send_stop_check(member)

    async def _get_nickname(self, member):
        msg = (await self.bot.wait_for('message', check=lambda msg: member == msg.author and member.guild.id == msg.guild.id)).content
        print(msg)
        if msg == "нет":
            await self._send_stop_check(member)
            return

        try:
            like = self._get_like(user=msg, lang="ru")
            self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]["diff"] = {
                "id": like[0],
                "name": like[1]
            }
            print(like)
            await self._check_user(member)
            
        except UserHasZeroContributions:
            await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(
            f"{member.mention}: к сожалению, " +
            "автоматическая верификация невозможна: у вас менее 1 правки."
            )
            del self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]

        except UserNotRegistered:
            await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(
            f"{member.mention}: к сожалению, " +
            "автоматическая верификация невозможна: " +
            "вы не зарегистрированы в Википедии."
            )
            del self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]

        except UserHasBlocked:
            await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(
                f"Пользователь {member.mention} был кикнут, так как его аккаунт заблокирован."
            )
            await member.kick()
            del self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]

    def _events(self):
        @self.bot.event
        async def on_raw_reaction_add(preyload):
            react_channel = await self.bot.fetch_channel(preyload.channel_id)
            if self.read_config()[str(react_channel.guild.id)]["message_id"] is None:
                return

            blacklist = File("blacklist")

            if str(preyload.user_id) in blacklist.read_data():
                return

            reaction_list = (await react_channel.fetch_message(preyload.message_id)).reactions
            user = react_channel.guild.get_member(preyload.user_id)

            if preyload.message_id == self.read_config()[str(react_channel.guild.id)]["message_id"]:
                for key, value in (self.read_config()[str(react_channel.guild.id)]["reactions"]).items():
                    if key == preyload.emoji.name:
                        await user.add_roles(react_channel.guild.get_role(int(value)))
                        return

        @self.bot.event
        async def on_raw_reaction_remove(preyload):
            react_channel = await self.bot.fetch_channel(preyload.channel_id)
            if self.read_config()[str(react_channel.guild.id)]["message_id"] is None:
                return

            blacklist = File("blacklist")

            if str(preyload.user_id) in blacklist.read_data():
                return

            reaction_list = (await react_channel.fetch_message(preyload.message_id)).reactions
            user = react_channel.guild.get_member(preyload.user_id)
            if preyload.message_id == self.read_config()[str(react_channel.guild.id)]["message_id"]:
                for key, value in (self.read_config()[str(react_channel.guild.id)]["reactions"]).items():
                    if key == preyload.emoji.name:
                        await user.remove_roles(react_channel.guild.get_role(int(value)))
                        return 

        @self.bot.event
        async def on_member_join(member):
            if member.bot: return
            self.list_of_users_logging[str(member.guild.id)] = {
                "list_verific": {
                    member.name: {
                    "member": str(member),
                    "diff": None
                    }
                },
                "login_channel": self.bot.get_channel(json.loads(self.confing.read_data())[str(member.guild.id)]["join_channel_id"])
            }

            await asyncio.sleep(0.5)
            await self._send_hello_msg(member)
            await self._get_nickname(member)

        @self.bot.event
        async def on_member_remove(member):
            if member.bot: return
            if str(member.guild.id) in self.list_of_users_logging:
                if member.name in self.list_of_users_logging[str(member.guild.id)]["list_verific"]:
                    await self.list_of_users_logging[str(member.guild.id)]["login_channel"].send(f"Пользователь {member.mention} покинул сервер. Верификация остановлена.")
                    del self.list_of_users_logging[str(member.guild.id)]["list_verific"][member.name]
    
