#bot 
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
from datetime import datetime
from threading import Thread
from music import Player
import threading
import time
import requests
from PIL import Image, ImageDraw

lockedChannels = {}
events = {}
RPS = {} 
rankedRPS = list()
unrankedRPS = list()
kill = False
load_dotenv()
command_prefix = '|'
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix = command_prefix)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_reaction_add(reaction, user):
    print(reaction.emoji, user)
    for event in events:
        if events[event].message == reaction.message and user != bot.user:
            if reaction.emoji == '✅':
                events[event].RSVPList.add(user)
            elif reaction.emoji == '❌':
                if user in events[event].RSVPList:
                    events[event].RSVPList.remove(user)
            message = reaction.message
            await message.remove_reaction(reaction.emoji, user)
        print(events[event].RSVPList)

@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content == 'die':
        await bot.close()



##Rock paper scissors stuff
@bot.command(name = 'lockRPSChannel')
async def lockRPSChannel(ctx):
    locked = False
    for role in ctx.author.roles:
        if role.id == 657010078364205086:
            lockedChannels['RPSChannel'] = ctx.message.channel.id
            print(f'Done! The new locked channel is {lockedChannels["RPSChannel"]}')
            locked = True
    if not locked: 
        channel = ctx.message.channel
        await channel.send("Oops! It doesn't look like you have the roles to execute that command (Fuckin loser)")

@bot.command(name = 'joinRPS')
async def joinRPS(ctx):
    ID = ctx.author.id
    name = ctx.author.display_name
    RPS[ID] = RPSPLAYER(name, ID)
    embed = joinRPSEmbed(name)
    channel = bot.get_channel(lockedChannels['RPSChannel'])
    await channel.send(embed = embed)

@bot.command(name = 'joinLobbyRPS')
async def joinLobbyRPS(ctx):
    if ctx.author.id not in RPS:
        channel = ctx.message.channel
        await channel.send(f"Oops! You aren't registered for RPS! Please register using the command {command_prefix}joinRPS!")
    elif ctx.author.id in unrankedRPS:
        channel = ctx.message.channel
        await channel.send(f"You're already in the queue! To leave the queue, type '{command_prefix}leaveRPS!")
    else: 
        unrankedRPS.append(ctx.author.id)

@bot.command(name = 'joinRankedRPS')
async def joinRankedRPS(ctx):
    if ctx.author.id not in RPS:
        channel = ctx.message.channel
        await channel.send(f"Oops! You aren't registered for RPS! Please register using the command {command_prefix}joinRPS!")
    elif ctx.author.id in rankedRPS:
        channel = ctx.message.channel
        await channel.send(f"You're already in the queue! To leave the queue, type '{command_prefix}leaveRPS!")
    else:
        rankedRPS.append(ctx.author.id)

async def checkLobbies():
    await bot.wait_until_ready()
    while True: 
        if 'RPSChannel' not in lockedChannels:
            pass
        else:
            channel = bot.get_channel(lockedChannels['RPSChannel'])
            if len(unrankedRPS) > 2:
                embed = getUnrankedMatchEmbed(unrankedRPS[0], unrankedRPS[1])
                await channel.send(embed = embed)
            
            check, ID1, ID2 = rankedRPSChecker()
            if check:
                embed = getRankedMatchEmbed(ID1, ID2)
                await channel.send(embed = embed)
        await asyncio.sleep(10)

def rankedRPSChecker():
    for i in range(len(rankedRPS)):
        for j in range(len(rankedRPS)):
            if i != j and abs(RPS[rankedRPS[i]].MMR - RPS[rankedRPS[j]].MMR) <= 10:
                return True, rankedRPS[i], rankedRPS[j]
    return False, None, None

def getUnrankedMatchEmbed(ID1, ID2):
    embed = discord.Embed(title = "Unranked Rock Paper Scissors Match!", description = f'This rock paper scissors match is between {RPS[ID1].name} and {RPS[ID2].name}!')
    embed.add_field(name = 'Instructions', value = 'Please DM this bot with your answer (either Rock, Paper, or Scissors) in the next five seconds! When both responses are received, the results will be displayed!')
    embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                                be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')

def getRankedMatchEmbed(ID1, ID2):
    embed = discord.Embed(title = "Ranked Rock Paper Scissors Match!", description = f'This rock paper scissors match is between {RPS[ID1].name} and {RPS[ID2].name}!')
    embed.add_field(name = RPS[ID1].name, value = f'{RPS[ID1].name} has won {RPS[ID1].won} and lost {RPS[ID1].lost} with a total MMR rating of {RPS[ID1].MMR}!', inline = True)
    embed.add_field(name = RPS[ID2].name, value = f'{RPS[ID2].name} has won {RPS[ID2].won} and lost {RPS[ID2].lost} with a total MMR rating of {RPS[ID2].MMR}!', inline = True)
    embed.add_field(name = 'Instructions', value = 'Please DM this bot with your answer (either Rock, Paper, or Scissors) in the next five seconds! When both responses are received, the results will be displayed!', inline = False)
    embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                                be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')

def joinRPSEmbed(name):
    embed = discord.Embed(title = f'{name} has joined the brawl!', description = f'Type {command_prefix}joinLobbyRPS or {command_prefix}joinRankedRPS to play!')
    embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                            be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')
    return embed

class RPSPLAYER(object):
    def __init__(self, name, ID):
        self.MMR = 0 
        self.wins = 0
        self.losses = 0
        self.name = name
        self.ID = ID


##Image Manip
def spinHelper(image):
    angle = 10 
    gifImages = []
    
    bg = Image.new('RGB', (100, 100), (255, 255, 255))
    temp = image.resize((100, 100))
    bg.paste(temp, (0, 0))
    for i in range(360//angle):
        bg = Image.new('RGB', (100, 100), (255, 255, 255))
        temp = temp.rotate(angle)
        bg.paste(temp, (0, 0))
        gifImages.append(bg.convert("P",palette=Image.ADAPTIVE))
    if not os.path.exists('imageManip'):
        os.mkdir('imageManip')
    print(len(gifImages))
    gifImages[0].save('imageManip/spin.gif', save_all = True, append_images = gifImages[1:], optimize = False, duration = 40, loop = 0)

@bot.command(name = 'spin', brief = 'wheeeeeeeeeee!')
async def spin(ctx, user : discord.Member):
    pfp = Image.open((requests.get(user.avatar_url, stream=True).raw))
    spinHelper(pfp)
    await ctx.channel.send(file = discord.File('imageManip/spin.gif'))













##Event stuff cause python won't let me use more than one file nosimmon
@bot.command(name = 'setEventChannel', brief = 'Sets the Event Channel ')
async def lockEventChannel(ctx):
    locked = False
    for role in ctx.author.roles:
        if role.id == 657010078364205086:
            lockedChannels['eventChannel'] = ctx.message.channel.id
            print(f'Done! The new locked channel is {lockedChannels["eventChannel"]}')
            locked = True
    if not locked: 
        channel = ctx.message.channel
        await channel.send("Oops! It doesn't look like you have the roles to execute that command (Fuckin loser)")


@bot.command(name = 'createEvent', brief = 'Creates an event', help = "Events must be structured into YY-MM-DD-Hour-Minute, and must contain an event title, the time, if a RSVP is required, and a description in that order.")
async def createEvent(ctx, eventTitle, time, requiredRSVP = 'false', eventDesc = 'No Description Given!'):
    tempEvent = eventCreate(time, requiredRSVP, eventTitle)
    channel = bot.get_channel(lockedChannels['eventChannel'])
    #Checks formatting
    if tempEvent == False:
        desc = '''It seems like you've formatted your event incorrectly. Your RSVP value should 
                be either True or False, and your date should be formatted in the form 
                YY-MM-DD-Hr-Min. Your event should be formatted Event Title, Time, RSVP, and event
                description.'''
        embed = discord.Embed(title = 'Oh no!', description = desc, color = 0x00ff00)
        embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                                be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')
        await channel.send(embed = embed)
    #Creates the text for the event
    embedVar = discord.Embed(title = eventTitle, description = eventDesc, color = 0x00ff00)
    embedVar.add_field(name = 'Time', value = createTimeString(tempEvent), inline = True)
    embedVar.add_field(name = 'RSVP?', value = requiredRSVP, inline = True)
    embedVar.set_footer(text = 'To RSVP and get reminded of the event, click the check below! \n To remove your RSVP, click the x!')
    eventMessage = await channel.send(embed = embedVar)
    tempEvent.message = eventMessage
    events[eventTitle] = tempEvent
    await eventMessage.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    await eventMessage.add_reaction('❌')

@bot.command(name = 'testPing', brief = "don't worry about it")
async def testPing(event):
    channel = bot.get_channel(lockedChannels['eventChannel'])
    
    embed, message = pingAll(event)
    await channel.send(embed = embed)
    await channel.send(message)

async def checkTime():
    await bot.wait_until_ready()
    while 1 == 1:
        if 'eventChannel' not in lockedChannels:
            pass
        else:
            channel = bot.get_channel(lockedChannels['eventChannel']) # replace with channel ID that you want to send to
            now = datetime.now()
            for event in events:
                e = events[event]
                if (e.year, e.month, e.day, e.hour, e.minute) == (now.year, now.month, now.day, now.hour, now.minute) and not e.alreadyPassed:
                    embed, message = pingAll(e)
                    e.alreadyPassed = True
                    await channel.send(embed = embed)
                    await channel.send(message)
        await asyncio.sleep(1)

class event(object):
    def __init__(self, year, month, day, hour, minute, RSVP, title, message = None):
        self.month = int(month)
        self.year = int(year)
        self.day = int(day)
        self.hour = int(hour)
        self.minute = int(minute)
        self.RSVP = RSVP
        self.message = message
        self.title = title
        self.RSVPList = set()
        self.alreadyPassed = False
    
    def addRSVP(self, RSVP):
        self.RSVPList += RSVP
        print(f'Here! {self.RSVPList}')

#Time format: YY-MM-DD-HH-MM
def eventCreate(time, RSVP, title):
    timeFormat = time.split('-')
    if RSVP.lower() == 'true':
        RSVPFormat = True
    elif RSVP.lower() == 'false':
        RSVPFormat = False
    else:
        return False
    
    if len(timeFormat) < 5:
        return False
    else:
        tempEvent = event(timeFormat[0], timeFormat[1], timeFormat[2], timeFormat[3], timeFormat[4], RSVPFormat, title)
    
    return tempEvent
     
def createTimeString(event):
    Year = event.year
    Months = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    Month = Months[int(event.month) - 1]
    Day = event.day
    Hour = event.hour
    Minute = event.minute
    return(f'{Month} {Day}, {Year}, {Hour}:{Minute}')

def pingAll(event):
    channel = bot.get_channel(lockedChannels['eventChannel'])
    pingString = ''
    if len(event.RSVPList) == 0:
        pingString = 'Nobody RSVPed!'
    for user in event.RSVPList:
        pingString += f'<@{user.id}>'
    embed = discord.Embed(title = f'{event.title}', description = f'This is a reminder for {event.message.jump_url}')
    embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                                be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')
    return embed, pingString

bot.loop.create_task(checkLobbies())
bot.loop.create_task(checkTime())
bot.run(TOKEN)
