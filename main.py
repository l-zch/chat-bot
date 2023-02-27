import os
import openai
from discord.ext import commands
import discord
from keep_alive import keep_alive
from random import uniform
from collections import deque

openai.organization = "org-QUZ0hlz3nUHf0f7oQaPhGV9V"
openai.api_key = os.environ['API_KEY']
openai.Model.list()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DEFAULT_CONTEXT = "你是一隻全知全能的黃主席機器狗，使用discord和人類交流，偶爾會用狗叫聲回答問題\n"


@client.event
async def on_ready():
    print("ready!")


cached_messages = {}

@client.event
async def on_message(message):
    if client.user in message.mentions or uniform(0,1)<=0.05:
        if message.author.id == client.user.id: return

        context = ""
        original_message = message
        
        for i in range(10):
            if message.author.id == client.user.id:
                author_name = "你"
            else:
                author_name = message.author.display_name
            embeds_content = ""
            for embed in message.embeds:
                embeds_content += f'\n{embed.title}「{embed.description}」。'
            tmp = f'{author_name}:{message.clean_content}{embeds_content}\n'
            if len(tmp) + len(context) < 700:
                context = tmp + context 
            else:
                break
            try:
                message_id = message.reference.message_id
                message = client.get_message(message_id) or cached_messages.get(message_id)
                if not message:
                    message = await original_message.channel.fetch_message(message_id)
                    cached_messages[message.id] = message
    
            except Exception as e:
                print(e)
                break

        print(context)
        async with original_message.channel.typing():
            completion = await openai.Completion.acreate(
                engine="text-davinci-003",
                temperature=0.9,
                max_tokens=2000,
                prompt= DEFAULT_CONTEXT + context + "你:")

        if completion.choices[0].finish_reason != "stop":
            answer = "汪汪汪汪!"
        else:
            answer = completion.choices[0].text
        await original_message.reply(answer)


keep_alive()
token = os.environ['TOKEN']
client.run(token)
