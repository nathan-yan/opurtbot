import discord
from discord.ext import tasks, commands

import asyncio
import threading

import subprocess
import time 
from queue import Queue, Empty

from threading import Thread
from requests import get

import os

import re

chat_reg = re.compile("<[^ ]+>")

q = Queue()
inq = Queue()       # queue for discord -> minecraft communication
outq = Queue()      # queue for minecraft -> discord communication 

active_players = set()

def enqueue(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    
    out.close()

def run_minecraft(command):    
    p = subprocess.Popen(["java", "-jar","-Xmx11000M", "-Xms11000M", "forge-1.16.1-32.0.107.jar", "nogui"],
                     stdout=subprocess.PIPE,
                     stdin = subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     )

    t = Thread(target = enqueue, args = (p.stdout, q))

    t.daemon = True
    t.start()

    cc = 0
    while True:
        cc += 1

        while not inq.empty():
            # push commands into the subprocess
            item = inq.get()

            print(item)

            if item['task'] == 'message-minecraft':
                print(item)

                command = 'tellraw @a {"text": "[%s] %s", "color" : "green"}' % (item['user'], item['message'].replace('\n', ' | '))
                p.stdin.write((command + "\n").encode())
                p.stdin.flush()

        try:
            line = q.get(timeout = 0.5)
            if line == 'quit':
                print("quit the minecraft thread")
                p.kill  ()
                break;

            line = line.decode()
            print(line)

            if "joined the game" in line:
                end_idx = line.index(" joined the game")
                start_idx = line.rindex(' ', 0, end_idx)

                name = line[start_idx + 1: end_idx]

                active_players.add(name)

                outq.put({
                    "task" : "message-discord-joinleave",
                    "user" : name,
                    "message" : "%s joined the game 💎" % name
                })

            elif "left the game" in line:
                end_idx = line.index(" left the game")
                start_idx = line.rindex(' ', 0, end_idx)

                name = line[start_idx + 1: end_idx]

                active_players.remove(name)

                outq.put({
                    "task" : "message-discord-joinleave",
                    "user" : name,
                    "message" : "%s left the game 🏃" % name
                })

            match = chat_reg.search(line)
            if match:
                print("found match!")

                span = match.span()

                user = line[span[0] + 1 : span[1] - 1]
                message = line[span[1] + 1 : -2]

                outq.put({
                    "task" : "message-discord",
                    "user" : user,
                    "message" : message
                })

        except:
            if cc % 10 == 0:
                print(".")

    return

class SpinupThread (threading.Thread):
   def __init__(self, ):
      threading.Thread.__init__(self)
      
   def run(self):
      client = Spinup()
      client.run(os.environ['DISCORD_TOKEN'])
    
class ServerThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    
    def run(self):
        run_minecraft([])

class Spinup(discord.Client):
    def __init__(self):
        super().__init__() 

        self.voting = False 
        self.voted = set()
        self.running = False
        self.upsince = 0

        self.voteStarted = 0
        self.voteChannel = None

        self.locked = False

        self.dimensional_rift = None
        self.ip = None

        self.vc = None

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.dimensional_rift = discord.utils.get(self.get_all_channels(), name = "dimensional-rift")
        self.server_status = discord.utils.get(self.get_all_channels(), name = "server-status")
    
    async def on_message(self, message):
        print(message.author.id, message.channel.name, message.channel.id)

        if message.channel.name == 'dimensional-rift':
            # this is a message sent from minecraft
            if (message.author == client.user) and message.content.startswith("```"):
                return

            inq.put({
                "task" : 'message-minecraft',
                "message" : message.content,
                "user" : message.author.nick
            })


        if message.content.startswith('#purge'):
            summary = {}

            num = int(message.content.split(" ")[1])

            if num > 10:
                num = 10
            
            num += 1

            if 'admin' in [r.name for r in message.author.roles]:
                history = await message.channel.history(limit = 100).flatten()
                
                for m in history[:num]:
                    if m.author.display_name not in summary:
                        summary[m.author.display_name] = 1
                    else:
                        summary[m.author.display_name] += 1

                summary_msg = ">>> "
                for n in summary:
                    summary_msg += n + ": " + str(summary[n]) + "\n"

                await message.channel.delete_messages(history[:num])
                await message.channel.send(summary_msg)

        # TODO: Put these in a dictionary or smth
        if message.content == "!clipthat":
            print(message.author.voice.channel)
            try:
                self.vc = await message.author.voice.channel.connect()

                self.vc.play(
                    discord.FFmpegPCMAudio(executable = "C:/ffmpeg/bin/ffmpeg.exe", source = "./wardell_clipthat.mp3")
                )

                while self.vc.is_playing():
                    await asyncio.sleep(.1)
                
                await self.vc.disconnect()
            except discord.errors.ClientException:
                await message.channel.send(
                    "opurtbot is already playing a clip"
                )
        
        if message.content == "!yessir":
            print(message.author.voice.channel)
            try:
                self.vc = await message.author.voice.channel.connect()

                self.vc.play(
                    discord.FFmpegPCMAudio(executable = "C:/ffmpeg/bin/ffmpeg.exe", source = "./wardell_yessir.mp3")
                )

                while self.vc.is_playing():
                    await asyncio.sleep(.1)
                
                await self.vc.disconnect()
            except discord.errors.ClientException:
                await message.channel.send(
                    "opurtbot is already playing a clip"
                )

        if message.content == "!yooo":
            print(message.author.voice.channel)
            try:
                self.vc = await message.author.voice.channel.connect()

                self.vc.play(
                    discord.FFmpegPCMAudio(executable = "C:/ffmpeg/bin/ffmpeg.exe", source = "./csgo_niceknife.mp3")
                )

                while self.vc.is_playing():
                    await asyncio.sleep(.1)
                
                await self.vc.disconnect()
            except discord.errors.ClientException:
                await message.channel.send(
                    "opurtbot is already playing a clip"
                )
        
        if message.content == '!bwaaa':
            try:
                self.vc = await message.author.voice.channel.connect()

                self.vc.play(
                    discord.FFmpegPCMAudio(executable = "C:/ffmpeg/bin/ffmpeg.exe", source = "./victory.mp3")
                )

                while self.vc and self.vc.is_playing():
                    await asyncio.sleep(.1)
                
                await self.vc.disconnect()
            except discord.errors.ClientException:
                await message.channel.send(
                    "opurtbot is already playing a clip"
                )
        
        if message.content == '!bwaa':
            try:
                self.vc = await message.author.voice.channel.connect()

                self.vc.play(
                    discord.FFmpegPCMAudio(executable = "C:/ffmpeg/bin/ffmpeg.exe", source = "./imposter_victory.mp3")
                )

                while self.vc and self.vc.is_playing():
                    await asyncio.sleep(.1)
                
                await self.vc.disconnect()
            except discord.errors.ClientException:
                await message.channel.send(
                    "opurtbot is already playing a clip"
                )
        
            
        if message.content == '!delib':
            try:
                self.vc = await message.author.voice.channel.connect()

                self.vc.play(
                    discord.FFmpegPCMAudio(executable = "C:/ffmpeg/bin/ffmpeg.exe", source = "./naruto_deliberation.mp3")
                )

                while self.vc and self.vc.is_playing():
                    await asyncio.sleep(.1)
                
                await self.vc.disconnect()
            except discord.errors.ClientException:
                await message.channel.send(
                    "opurtbot is already playing a clip"
                )
        
        elif message.content == '!!delib':
            if self.vc:
                await self.vc.disconnect()
                self.vc = None
        
        if message.content.startswith("!spinup"):
            if self.voting:
                await message.channel.send("you mf clown there's already an active vote")
            elif self.running:
                await message.channel.send("the server is already up u fool")
            elif self.locked:
                await message.channel.send("the server is locked! nathan's probably playing valorant...")
            else:
                if (message.author.id == 279456734773510145) and not message.content.endswith("nosudo"):
                    await self.spinup(message)
                else:
                    await message.channel.send("starting vote, need 5 people to confirm. you have 3 MINUTES to vote [type `!yes` to vote, `!no` to cancel your existing vote]")

                    self.voteChannel = message.channel
                    self.voteStarted = time.time()
                    self.voting = True
                    self.voted = set()
        


        elif message.content.startswith("!whois"):
            if len(active_players):
                res = "players currently on: \n```" 
                for p in active_players:
                    res += "  - " + p + "\n"
                await message.channel.send(res + "```")
            else:
                await message.channel.send("no one is on, hop in!")

        elif message.content.startswith("!lock"):
            if (message.author.id == 279456734773510145):
                await message.channel.send("the server is locked and cannot be spun up")

                self.locked = True

                if self.voting:
                    await message.channel.send("the active vote has been cancelled")
                    self.voting = False
                    self.voted = set()
        
        elif message.content.startswith("!unlock"):
            if (message.author.id == 279456734773510145):
                await message.channel.send("the server is unlocked can can be spun up")

                self.locked = False

        elif message.content.startswith("!help"):
            await message.channel.send("""
`!spinup`   - starts a vote to spin up the minecraft server, type `!yes` to vote, `!no` to cancel
`!spindown` - spins down the minecraft server, there is NO voting process
`!ip`       - returns the IP address of the server
`!isup`     - checks if the server is currently up/starting up
`!uptime`   - returns the uptime of the server in seconds
            """)


        elif message.content.startswith("!yes"):
            if message.author not in self.voted and self.voting:
                self.voted.add(message.author)
                await message.channel.send("%s out of 5 votes recorded" % len(self.voted))
            
                if len(self.voted) == 5:
                    # spin up the mineraft server
                    await self.spinup(message)        

        elif message.content.startswith("!no"):
            if message.author in self.voted and self.voting:
                self.voted.remove(message.author)
                await message.channel.send("%s out of 5 votes recorded" % len(self.voted))

        elif message.content.startswith("!spindown"):
            await message.channel.send("spinning down the minecraft server")

            q.put("quit")
            self.running = False

        elif message.content.startswith("!isup"):
            if self.running:
                await message.channel.send("the server IS up") 
            else:
                await message.channel.send("the server is NOT up")
        elif message.content.startswith("!uptime"):
            if self.running:
                await message.channel.send("the server has been up for %s seconds" % ((time.time() - self.upsince)))
            else:
                await message.channel.send("the server is not currently up")
            
        elif message.content.startswith("!ip"):
            self.ip = get('https://api.ipify.org').text
            await message.channel.send("`%s:25565`" % (get('https://api.ipify.org').text))
    
    async def spinup(self, message):
        await message.channel.send("vote succeeded, spinning up minecraft @ %s:25565" % (get('https://api.ipify.org').text))
        self.ip = get('https://api.ipify.org').text

        self.voting = False
        self.voted = set()

        if (not self.running):
            m = ServerThread()
            m.start()

            self.running = True
            self.upsince = time.time()
            
client = Spinup()

async def check_messages(ctx):
    last_message = None

    prev_topic = ""
    while True:
        if ctx.dimensional_rift and ctx.server_status:
            if not last_message:
                last_message = ctx.server_status.last_message_id 

            # set the topic of the chat
            statuses = []

            statuses.append("ON @ %s" % ctx.ip if ctx.running else "OFF")
            statuses.append("LOCKED" if ctx.locked else "UNLOCKED")
            
            if ctx.voting:
                statuses.append("VOTING")

            topic = "SERVER: "
            for status in statuses:
                topic += status + ", "
            topic = topic[:-2]

            if len(active_players) and ctx.running:
                topic += " | "
                for player in active_players:
                    topic += player + ", "
                topic = topic[:-2]

            elif len(active_players) == 0 and ctx.running:
                topic += " | no one is on, hop on!"

            if topic != prev_topic:
                print("EDITING TOPIC: %s, %s" % (prev_topic, topic))

                # delete the last message 
                if last_message: 
                    try:
                        if type(last_message) == int:
                            msg = await ctx.server_status.fetch_message(last_message)
                            await msg.delete()
                        else:
                            await last_message.delete()
                    except Exception as e:
                        print(e)

                last_message = await ctx.server_status.send(topic)

                prev_topic = topic


            if (time.time() - ctx.voteStarted) > 180 and ctx.voting:
                ctx.voting = False
                ctx.voted = set() 

                await ctx.voteChannel.send("sorry! the vote has ended, type `!spinup` to start another vote")
            elif int(time.time() - ctx.voteStarted) == 120 and ctx.voting:
                ctx.voteStarted -= 1    # this is so fucking janky. we only want this message sent once, so we rely on the 0.1 second resolution of the check_messages function. we subtract one from voteStarted to simulate a second of time passing, ensuring this message is only sent once.

                await ctx.voteChannel.send("the vote will end in 1 MINUTE")
            elif int(time.time() - ctx.voteStarted) == 60 and ctx.voting:
                ctx.voteStarted -= 1

                await ctx.voteChannel.send("the vote will end in 2 MINUTES")

            while not outq.empty():
                item = outq.get()

                if item['task'] == 'message-discord':
                    #channel = discord.utils.get(ctx.get_all_channels(), name = "dimensional-rift")
                    #print(channel)
                    if not item['message'].endswith("Disconnected"):
                        await ctx.dimensional_rift.send("```diff\n+ <%s> %s```" % (item['user'], item['message']))

                elif item['task'] == 'message-discord-joinleave':
                    
                    user = item['user']
                    message = item['message']

                    await ctx.dimensional_rift.send(message)

        await asyncio.sleep(0.1)

client.loop.create_task(check_messages(client))

client.run(os.environ['DISCORD_TOKEN'])