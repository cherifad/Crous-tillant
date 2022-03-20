import random
import sys
import os
import time
import discord
from discord.ext import commands
from methods import importData, search, customToString, update, availableDays, days
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

intents = discord.Intents(messages=True, guilds=True, message_content=True)

########################################################################################################################
################################################# LOG ##################################################################
########################################################################################################################

Log_Format = "%(levelname)s %(asctime)s - %(message)s"

formatter = logging.Formatter("%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s")

handler_critic = logging.FileHandler("critic.log", mode="a", encoding="utf-8")
handler_info = logging.FileHandler("info.log", mode="a", encoding="utf-8")

handler_critic.setFormatter(formatter)
handler_info.setFormatter(formatter)

handler_info.setLevel(logging.INFO)
handler_critic.setLevel(logging.CRITICAL)

logger = logging.getLogger("bs4")
logger.setLevel(logging.INFO)
logger.addHandler(handler_critic)
logger.addHandler(handler_info)

########################################################################################################################
################################################# LOG ##################################################################
########################################################################################################################

sched = AsyncIOScheduler(timezone='Europe/Paris')

load_dotenv(dotenv_path="config")

sys.path.append(".")

days = days()

RU_words = ['RU', 'RESTAURANT', 'MANGER', 'RESTO', 'FAIM', 'NOURRITURE']

channelid = int(os.getenv('CHANNEL'))

emmissions = ['1000 secondes', 'À la di Stasio', 'À pleines dents !', 'Anthony Bourdain: Parts Unknown',
              'Art et magie de la cuisine', "L'Assiette brésilienne",
              'Avec Eric', 'Bien dans votre assiette', 'Bon appétit bien sûr', 'Bon et à savoir', 'Bonne Cuisine',
              'Les Carnets de Julie', 'Carnotzet',
              'Carte postale gourmande', "Cauchemar à l'hôtel", 'Cauchemar en cuisine (France)',
              'Cauchemar en cuisine (Grande-Bretagne)', 'Le Chef en France',
              'The Chef Show Working', 'Chef, la recette !', 'Les chefs contre-attaquent', "Chef's Table",
              'Côté cuisine', 'Côté labo, côté cuisine', "La Cuisine d'à côté",
              'La Cuisine des Mousquetaires', 'Cuisine sauvage', 'Le Cuisinier rebelle', 'Cupcake Wars',
              'Curieux Bégin', "De l'art et du cochon",
              'Diners, Drive-Ins and Dives', "L'École des chefs", "L'Effet Vézina", "L'Épicerie",
              'Les Escapades de Petitrenaud', 'File-moi ta recette',
              'Fourchette et sac à dos', 'The French Chef', "Gourmet's Diary of a Foodie", 'De keuken van Sofie',
              'Liste des épisodes de Cupcake Wars', 'Mange mon geek',
              'Miam : Mon invitation à manger', 'Mon gâteau est le meilleur de France', 'Oh My Ghostess', 'Oui chef !',
              'Petits Plats en équilibre',
              "Quand c'est bon ?… Il n'y a pas meilleur !", 'Repas de familles', 'Selena + Chef', 'Toque Show',
              'Le Tour de France culinaire de Sarah Wiener',
              'La Tournée des popotes', 'La vérité est au fond de la marmite', 'Voyages et délices by Chef Kelly']

avaiable_commands = ['Git', 'Faim', 'Json']


def start(url: str):
    dir_list = os.listdir('./files')

    dir_list.reverse()

    if len(dir_list) > 5:
        for file in range(len(dir_list)):
            if os.path.exists('./files/{}'.format(dir_list[file])):
                os.remove('./files/{}'.format(dir_list[file]))

    name = update(url)

    find = False

    while find:
        for files in os.walk("./files"):
            if name in files:
                find = True
            else:
                time.sleep(1)

    return_list = importData(name)

    return return_list


list_food = start(os.getenv('URL'))

available_day = availableDays(list_food)


########################################################################################################################
################################################# CLASS ################################################################
########################################################################################################################

class Bot(commands.Bot):
    def __init__(self):
        print("bot initialized")
        super().__init__(command_prefix=commands.when_mentioned_or("$"), intents=intents)

    async def on_ready(self):
        view = discord.ui.View(timeout=None)

        await bot.get_channel(int(channelid)).purge(limit=100)

        for day in days:
            if day in available_day:
                view.add_item(DayButton(day))
            else:
                view.add_item(DayButton(day, True))

        view.add_item(Button('Aide', style=discord.enums.ButtonStyle.red))

        await today_food()

        try:
            await self.get_channel(channelid).send("Choisir un jour", view=view)
        except:
            pass

        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Logged in as {self.user} (ID: {self.user.id})")


class DayButton(discord.ui.Button):
    def __init__(self, label, disable=False):
        """
        A button for one role. `custom_id` is needed for persistent views.
        """
        super().__init__(
            label=label,
            style=discord.enums.ButtonStyle.primary,
            custom_id=label,
            disabled=disable,
        )

    async def callback(self, interaction: discord.Interaction):
        def response_printer(day):
            query = search('day', list_food, day)
            embed = discord.Embed(title=str(query[0].day).upper(),
                                  description=str(query[0].moment),
                                  color=discord.Color.random())
            for food in query:
                embed.add_field(name=str(food.type_food).upper(), value=customToString(food))

            return embed

        embed = response_printer(str(self.label))
        embed.set_footer(text="Prefixe des commandes : $\nhelp pour avoir l'aide")

        await interaction.response.send_message(embed=embed, ephemeral=True)


class Button(discord.ui.Button):
    def __init__(self, label, disable=False, style=discord.enums.ButtonStyle.primary):
        """
        A button for one role. `custom_id` is needed for persistent views.
        """
        super().__init__(
            label=label,
            style=style,
            custom_id=label,
            disabled=disable,
        )

    async def callback(self, interaction: discord.Interaction):
        message = None
        embed = None
        view = None
        file_send = None

        if self.custom_id.upper() == 'GIT':
            message = 'https://github.com/NeldaZeram/Menu_RU.git'

        if self.custom_id.upper() == 'FAIM':
            try:
                embed = discord.Embed(title="Aujourd'hui".upper(),
                                      description=str(search('today', list_food)[0].moment),
                                      color=discord.Color.random())
                for food in search('today', list_food):
                    embed.add_field(name=str(food.type_food), value=customToString(food))
                embed.set_footer(text="Préfixe des commandes : $\nhelp pour avoir l'aide")
            except:
                embed = discord.Embed(url=os.getenv('URL'),
                                      title="Aujourd'hui".upper(),
                                      description="Rien !",
                                      color=discord.Color.random())
                embed.set_footer(text="Préfixe des commandes : $\nhelp pour avoir l'aide")

        if self.custom_id.upper() == 'AIDE':
            view = discord.ui.View(timeout=None)

            for command in avaiable_commands:
                view.add_item(Button(command.title()))
            embed = await helpBot()

        if self.custom_id.upper() == 'JSON':
            dir_list = os.listdir('./files')
            for file in dir_list:
                if 'json' in str(file):
                    file_send = file
            if file_send is None:
                message = 'Pas de fichier dispo (réessaye plus tard)'

        if file_send is None:
            await interaction.response.send_message(content=str(message), embed=embed, ephemeral=True, view=view)
        else:
            await interaction.response.send_message(content=message, embed=embed, ephemeral=True, view=view,
                                                    file=discord.File(f'./files/{file_send}'))


########################################################################################################################
################################################ COMMANDS ##############################################################
########################################################################################################################

bot = Bot()

bot.remove_command("help")


@bot.command()
async def clear(ctx, amount=10):
    await ctx.message.delete()
    await ctx.channel.purge(limit=amount)


@discord.ext.commands.cooldown(20, 20, type=discord.ext.commands.BucketType.default)
@bot.command()
async def faim(ctx: commands.Context):
    await ctx.message.delete()

    """Asks the user a question to confirm something."""
    # We create the view and assign it to a variable so we can wait for it later.
    view = discord.ui.View(timeout=None)

    if channelid == 0:
        embed = discord.Embed(title="attention !".upper(),
                              description='$channel channelid password pour configurer un channel ou envoyer les menus',
                              color=discord.Color.red())

    for day in days:
        if day in available_day:
            view.add_item(DayButton(day))
        else:
            view.add_item(DayButton(day, True))

    await ctx.send("Choisir un jour", view=view)
    # Wait for the View to stop listening for input...


@bot.command()
async def channel(ctx, channelidP, password):
    await ctx.message.delete()

    channels = []

    for channel in ctx.guild.channels:
        channels.append(str(channel.id))

    if password != os.getenv('PASSWORD'):
        await ctx.send(f"❌ '{password}' n'est pas le bon mot de passe")
    elif str(channelidP) not in channels:
        await ctx.send(f"❌ {channelidP} ne fais pas partis des salons disponibles")
    else:
        try:
            with open('config', 'r') as fr:
                lines = fr.readlines()

                with open('config', 'w') as fw:
                    for line in lines:

                        # find() returns -1
                        # if no match found
                        if line.find('CHANNEL') == -1:
                            fw.write(line)
            print("Deleted")
            await ctx.send(f"✅ '{channelidP}' sera le nouveau salon par défaut"
                           f"\n Le bot va redémarrer")
        except:
            await ctx.send(f"❌ Une erreur est survenue lors de l'écriture du fichier de configuration")
            print("Oops! something error")

        with open("config", "a") as text_file:
            text_file.write(f'CHANNEL={channelidP}')

        os.environ['CHANNEL'] = channelidP

        restart_bot()


@bot.command()
async def update(ctx, password):
    await ctx.message.delete()
    if password == os.getenv("PASSWORD"):
        list_food = start(os.getenv('URL'))
        await ctx.channel.send('Mise à jour lancée')
    else:
        await ctx.send(f"❌ '{password}' n'est pas le bon mot de passe")


@discord.ext.commands.cooldown(20, 20, type=discord.ext.commands.BucketType.default)
@bot.command()
async def help(ctx):
    await ctx.message.delete()
    view = discord.ui.View(timeout=None)

    for command in avaiable_commands:
        view.add_item(Button(command))

    embed = await helpBot()

    await ctx.send(embed=embed)
    await ctx.send('Liste des raccourcis', view=view)

    @bot.event
    async def on_command_error(ctx, error):
        send_help = (
            commands.MissingRequiredArgument, commands.BadArgument, commands.TooManyArguments, commands.UserInputError)

        if isinstance(error, commands.CommandNotFound):  # fails silently
            pass

        elif isinstance(error, send_help):
            await ctx.send("Il manque des arguments")

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'This command is on cooldown. Please wait {error.retry_after:.2f}s')

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('You do not have the permissions to use this command.')
        # If any other error occurs, prints to console.
        else:
            print(''.join(traceback.format_exception(type(error), error, error.__traceback__)))


########################################################################################################################
################################################ FUNCTIONS #############################################################
########################################################################################################################

def restart_bot():
    logger.info('Restart')
    os.execv(sys.executable, ['main'] + sys.argv)


async def today_food():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(emmissions)))
    try:
        embed = discord.Embed(title="Aujourd'hui".upper(),
                              description=str(search('today', list_food)[0].moment),
                              color=discord.Color.random())
        for food in search('today', list_food):
            embed.add_field(name=str(food.type_food), value=customToString(food))
        embed.set_footer(text="Préfixe des commandes : $\nhelp pour avoir l'aide")
    except:
        embed = discord.Embed(url=os.getenv('URL'),
                              title="Aujourd'hui".upper(),
                              description="Rien !",
                              color=discord.Color.random())
        embed.set_footer(text="Préfixe des commandes : $\nhelp pour avoir l'aide")

    embed.set_author(name='🕖 MAJ à 7h30 du lundi au vendredi')

    try:
        await bot.get_channel(int(channelid)).send(content=None, embed=embed)
    except:
        pass

    return embed


async def helpBot():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(emmissions)))

    embed = discord.Embed(title="AIDE ($help)",
                          description='__Préfixe des commandes__ : **$**',
                          color=discord.Color.random())
    embed.add_field(name='__**Sans mot de passe**__', value='**faim** : menu du jour'
                                                            '\n**git** : lien du repo'
                                                            '\n**json** : fichier json (pour ceux et celle qui veulent'
                                                            'me faire de la concurrence (pas de commande $json)')
    embed.add_field(name='__*Avec mot de passe*__', value='**update** : forcer la mise à jour des menu'
                                                          '\n**channel** : mettre à jour le salon par défaut'
                                                          '\n**clear** x : suppression des messages '
                                                          '\n(sans paramètre, supprime 5 message)')
    embed.set_footer(text="Préfixe des commandes : $\nhelp pour avoir l'aide"
                          "\nSi une commande ne fonctionne pas : tkt")
    embed.set_author(name='🕖 MAJ à 7h30 du lundi au vendredi')

    return embed


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=7, minute=30)
async def display_today():
    logger.info('Display updated')
    await bot.on_ready()


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=5, minute=30)
async def update_data():
    list_food = start(os.getenv('URL'))


@sched.scheduled_job('interval', minutes=30)
async def status_change():
    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(emmissions)))


sched.start()

bot.run(os.getenv("TOKEN"))
