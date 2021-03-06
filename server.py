import subprocess

from aiohttp import web
import asyncio
import socketio

import re

chat_reg = re.compile("<[^ ]+>")

async def minecraft_handler(process, sock):
    """p = await asyncio.create_subprocess_shell(' '.join(["java", "-jar", "-Xmx12G", "-Xms12G", "../server-files/minecraft_fridays/forge-1.16.1-32.0.107.jar", "nogui"]),
                         stdout = asyncio.subprocess.PIPE,
                         stdin  = asyncio.subprocess.PIPE,
                         stderr = asyncio.subprocess.STDOUT)
    """
    print('bruh')

    while True:
        line = await process.stdout.readline()
        print('test ' + line.decode()[:-1])

        if line == 'quit':
            print("quit the minecraft thread")
            break;

        line = line.decode()

        if "joined the game" in line:
            end_idx = line.index(" joined the game")
            start_idx = line.rindex(' ', 0, end_idx)

            name = line[start_idx + 1: end_idx]

            await sock.emit('joinleave', {
                "task" : "message-discord-joinleave",
                "user" : name,
                "message" : "%s joined the game 💎" % name,
                "joining" : True
            })

        elif "left the game" in line:
            end_idx = line.index(" left the game")
            start_idx = line.rindex(' ', 0, end_idx)

            name = line[start_idx + 1: end_idx]

            await sock.emit('joinleave', {
                "task" : "message-discord-joinleave",
                "user" : name,
                "message" : "%s left the game 🏃" % name,
                "joining" : False
            })

        match = chat_reg.search(line)
        if match:
            print("found match!")

            span = match.span()

            user = line[span[0] + 1 : span[1] - 1]
            message = line[span[1] + 1 : -2]

            await sock.emit('minecraft-chat', {
                "task" : "message-discord",
                "user" : user,
                "message" : message
            })

        if line == b'':
            print("process has stopped")
            break;

async def run_server(runner):
    print("running server")
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8001)
    print("run")
    await site.start()
    print("ran")

async def main():
    
    p = await asyncio.create_subprocess_shell('python nonce.py', 
                                              stdout = asyncio.subprocess.PIPE,
                                              stdin  = asyncio.subprocess.PIPE,
                                              stderr = asyncio.subprocess.STDOUT)

    sock = socketio.AsyncServer()
    app = web.Application()
    sock.attach(app)

    @sock.event
    async def connect(sid, environ):
        print("connection:", sid, environ)
        await sock.emit('ack')

    @sock.on('discord-chat')
    async def recv_message(sid, data):
        print("message", data)
        
        # do stuff here
        command = 'tellraw @a {"text": "[%s] %s", "color" : "green"}' % (item['user'], item['message'].replace('\n', ' | '))
        p.communicate((command + '\n').encode())

        await sock.emit('ack')

    @sock.event
    async def disconnect(sid):
        print("disconnect", sid)
    
    @sock.on('quit')
    async def quit_minecraft(sid):
        p.communicate(b'quit')  
        p.kill()

    runner = web.AppRunner(app)

    await asyncio.gather(
        run_server(runner),
        minecraft_handler(p, sock),
    )

if __name__ == "__main__":
    asyncio.run(main())
