import discord
import os
import requests
import json
from keep_alive import keep_alive
import yagmail
import asyncio
from discord.ext import commands
from discord.ext.commands import Bot, when_mentioned_or
from discord.ext.commands import CommandNotFound, CommandOnCooldown, MissingPermissions, MissingRequiredArgument, BadArgument, MissingAnyRole
import smtplib
from email.message import EmailMessage

os.system('pip install Pillow')
from PIL import Image, ImageFont, ImageDraw


FONT_FILE = ImageFont.truetype(r'font.ttf', 180)
FONT_COLOR = "#FFFFFF"

template = Image.open(r'cert.png')
WIDTH, HEIGHT = template.size

client = commands.Bot(command_prefix=when_mentioned_or('&gen '),description='A bot used to generate certificates')

game="ggk"

mlid=os.environ['id']
mp=os.environ['pas']

async def send_message(ctx, message):
    await ctx.send(embed=discord.Embed(description=message))

def make_certificates(name):
    '''Function to save certificates as a .png file'''

    image_source = Image.open(r'cert.png')
    draw = ImageDraw.Draw(image_source)

    name_width, name_height = draw.textsize(name, font=FONT_FILE)

    draw.text(((WIDTH - name_width) / 2, (HEIGHT - name_height) / 2 - 30), name, fill=FONT_COLOR, font=FONT_FILE)

    image_source.save("./certificates/"+name +".png")

@client.event
async def on_ready():
  print("We have logged in as {0.user}".format(client))
  # await client.change_presence(status=discord.Status.online, activity=game)

#ping

@client.command(brief='inputting')
async def create(ctx):
  
  def check1(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel
  # try:
  await send_message(ctx, f"{ctx.author.mention}, Please enter the winners name")

  try:
        msg = await client.wait_for("message", check=check1, timeout=30) 
        name=msg.content
  except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")
        return

  name=name.lower()
  finalname=name[0].upper()
  for i in range(1, len(name)):
    if(name[i-1]==" "):
      finalname=finalname+name[i].upper()
    else:
      finalname=finalname+name[i]
  make_certificates(finalname)
  await msg.channel.send(file=discord.File("./certificates/"+finalname +".png"))

  def check2(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in ["y", "n"]

  await send_message(ctx, f"{ctx.author.mention}, Do you want to mail it, enter y for yes and n for no")

  try:
        msg = await client.wait_for("message", check=check2, timeout=30) 
        flag=msg.content.lower()
  except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")
        return

  if flag=='n':
    await send_message(ctx,"Mail not send")
    return

  # To

  mymail=EmailMessage()
  mymail['Subject']="Certificate of Appreciation"
  mymail['from']=mlid
  mymail.set_content("Congrats!, your certificate is attached herewith")

  server=smtplib.SMTP_SSL('smtp.gmail.com',465)
  server.login(mlid, mp)
  
  await send_message(ctx, f"{ctx.author.mention}, Enter the reciever's mail adress")
  
  try:
      message = await client.wait_for('message', timeout=30, check=check1)
      recipient = str(message.content).split(' ')

  except asyncio.TimeoutError:
      await ctx.send("Sorry, you didn't reply in time!")
      return

  #CC

  await send_message(ctx, f"{ctx.author.mention}, Enter the CC of recievers address and type 'na' if none")
  
  try:
      message = await client.wait_for('message', timeout=30, check=check1)
      ccrec=[]
      if(message.content.lower() != "na"):
        ccrec = str(message.content).split(' ')

  except asyncio.TimeoutError:
      await ctx.send("Sorry, you didn't reply in time!")
      return

  #BCC

  await send_message(ctx, f"{ctx.author.mention}, Enter the BCC of recievers address and type 'na' if none")
  
  try:
      message = await client.wait_for('message', timeout=30, check=check1)
      bccrec=[]
      if(message.content.lower() != "na"):
        bccrec = str(message.content).split(' ')

  except asyncio.TimeoutError:
      await ctx.send("Sorry, you didn't reply in time!")
      return

  mymail['To']=", ".join(recipient)
  mymail['Cc']=", ".join(ccrec)
  mymail['Bcc']=", ".join(bccrec)

  with open("./certificates/"+finalname +".png","rb") as fl:
    data=fl.read()
  mymail.add_attachment(data,maintype="application",subtype="png",filename=name+".png")

  try:
    server.send_message(mymail)
    await send_message(ctx, "mail sent successfully")
  except:
    await send_message(ctx, "Some error occured :( Please try again")
    
  del mymail
  server.quit()

    # make_certificates(message)
  # except:
  #   await ctx.send(f"You took too long to type{ctx.author.mention}")
  #   return

@client.command(brief='Measure delays')
async def ping(ctx):
    await ctx.send(':ping_pong: Pong! ~' + str(round(client.latency * 1000, 2)) + " ms")

# @client.event
# async def on_message(message):
#   if message.author == client.user:
#     return

#   if message.content.startswith('&gen'):
#     name=message.content.split("&gen ",1)[1]
#     name=name.lower()
#     finalname=name[0].upper()
#     for i in range(1, len(name)):
#       if(name[i-1]==" "):
#         finalname=finalname+name[i].upper()
#       else:
#         finalname=finalname+name[i]
#   make_certificates(finalname)
  
#   await message.channel.send(file=discord.File("./certificates/"+finalname +".png"))
#   s="Do you want to send it via email"
  
#   await message.channel.send(s)

@ client.event
async def on_command_error(ctx: commands.Context, error: Exception):
    if isinstance(error, CommandNotFound):
        pass

    elif isinstance(error, CommandOnCooldown):
        pass

    elif isinstance(error, BadArgument) or isinstance(error, MissingRequiredArgument):
        command = ctx.command
        usage = f".{str(command)} "
        params = []
        for key, value in command.params.items():
            if key not in ['self', 'ctx']:
                params.append(f"[{key}]" if "NoneType" in str(
                    value) else f"<{key}>")
        usage += ' '.join(params)
        await ctx.send(f"Usage: **{usage}**")

    elif isinstance(error, MissingPermissions) or isinstance(error, MissingAnyRole):
        await ctx.send(f"{str(error)}")

    else:
        print(f"{ctx.author.id} {ctx.guild.id} {ctx.message.content}")
        print(error)
        await ctx.send(error)
  
tok = os.environ['TOKEN']

keep_alive()
client.run(tok)