#bot 
import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from datetime import datetime
import threading


lockedChannels = {}
events = {}
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)
bot = commands.Bot(command_prefix = '|')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.event
async def on_reaction_add(reaction, user):
    print(reaction, user)
    for event in events:
        if events[event].message == reaction.message and user != bot.user:
            print(type(events), type(event), type(user), type(events[event].RSVPList))
            events[event].RSVPList.add(user)
            print(f'Flag! {events[event].RSVPList}')


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.content == 'die':
        await bot.close()
    #print(message.channel.id)
    

@bot.command(name = 'setEventChannel')
async def lockEventChannel(ctx):
    lockedChannels['eventChannel'] = ctx.message.channel.id
    print(f'Done! The new locked channel is {lockedChannels["eventChannel"]}')

@bot.command(name = 'createEvent')
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
    embedVar.set_footer(text = 'To RSVP and get reminded of the event, click the check below!')
    eventMessage = await channel.send(embed = embedVar)
    tempEvent.message = eventMessage
    events[eventTitle] = tempEvent
    await eventMessage.add_reaction('\N{WHITE HEAVY CHECK MARK}')

@bot.command(name = 'testPing')
async def testPing(ctx):
    channel = bot.get_channel(lockedChannels['eventChannel'])
    for event in events:
        embed, message = pingAll(events[event])
        await channel.send(embed = embed)
        await channel.send(message)

class event(object):
    def __init__(self, year, month, day, hour, minute, RSVP, title, message = None):
        self.month = month
        self.year = year
        self.day = day
        self.hour = hour
        self.minute = minute
        self.RSVP = RSVP
        self.message = message
        self.title = title
        self.RSVPList = set()
    
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
    pingString = ''
    for user in event.RSVPList:
        pingString += f'<@{user.id}>'
    embed = discord.Embed(title = f'{event.title}', description = f'This is a reminder for {event.message.jump_url}')
    embed.set_footer(text = '''I am a bot, and this action was performed automatically. If you think there may
                                be a problem, please contact TheAwesomeWizard13597#9482 with questions.''')
    return embed, pingString
bot.run(TOKEN)
