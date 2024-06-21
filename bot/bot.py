from dataclasses import dataclass
from pathlib import Path
import subprocess
import time
import io
import os

import psutil
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from utils.filesystem import CacheDir
from utils.logger_to_file import LoggerToFile


def get_system_info():
  cpu = psutil.cpu_percent(interval=1)
  mem = psutil.virtual_memory()
  disk = psutil.disk_usage('/')
  net = psutil.net_io_counters()
  for proc in psutil.process_iter([
    'pid',
    'name',
    'cpu_percent',
    'memory_percent',
  ]):
    proc.cpu_percent(interval=None)
  time.sleep(1)
  processes = []
  for proc in sorted(
    psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
    key=lambda x: x.info['cpu_percent'],
    reverse=True,
  )[:8]:
    processes.append({
      'pid': proc.info['pid'],
      'name': proc.info['name'],
      'cpu_percent': proc.info['cpu_percent'],
      'memory_percent': proc.info['memory_percent'],
    })
  return {
    'cpu': {'total': cpu},
    'mem': {
      'total': mem.total,
      'available': mem.available,
      'percent': mem.percent,
    },
    'disk': {
      'total': disk.total,
      'used': disk.used,
      'free': disk.free,
      'percent': disk.percent,
    },
    'network': {'bytes_sent': net.bytes_sent, 'bytes_recv': net.bytes_recv},
    'top_processes': processes,
  }


def draw_bar(draw, x, y, width, height, percent, color):
  draw.rectangle([x, y, x + width, y + height], outline='black', fill='grey')
  draw.rectangle(
    [x, y, x + int(width * (percent / 100)), y + height],
    outline='black',
    fill=color,
  )


def create_image(system_info):
  width, height = 800, 400
  image = Image.new('RGB', (width, height), color=(30, 30, 30))
  draw = ImageDraw.Draw(image)
  font = ImageFont.load_default()
  text_color = (255, 255, 255)
  draw.text(
    (10, 10),
    f"CPU Usage: {system_info['cpu']['total']}%",
    font=font,
    fill=text_color,
  )
  draw_bar(draw, 10, 30, 780, 20, system_info['cpu']['total'], 'red')
  draw.text(
    (10, 60),
    f"Memory Usage: {system_info['mem']['percent']}%",
    font=font,
    fill=text_color,
  )
  draw_bar(draw, 10, 80, 780, 20, system_info['mem']['percent'], 'blue')
  draw.text(
    (10, 110),
    f"Disk Usage: {system_info['disk']['percent']}%",
    font=font,
    fill=text_color,
  )
  draw_bar(draw, 10, 130, 780, 20, system_info['disk']['percent'], 'green')
  draw.text(
    (10, 160),
    f"Network Sent: {system_info['network']['bytes_sent'] / (1024 * 1024):.2f} MB",
    font=font,
    fill=text_color,
  )
  draw.text(
    (10, 180),
    f"Network Received: {system_info['network']['bytes_recv'] / (1024 * 1024):.2f} MB",
    font=font,
    fill=text_color,
  )
  draw.text((10, 210), 'Top Processes:', font=font, fill=text_color)
  for i, proc in enumerate(system_info['top_processes']):
    draw.text(
      (10, 230 + i * 20),
      f"{proc['name']} (PID {proc['pid']}) - CPU: {proc['cpu_percent']}%, MEM: {proc['memory_percent']:.2f}%",
      font=font,
      fill=text_color,
    )
  return image


intents = discord.Intents.default()
intents.message_content = True
DISCORD_BOT = commands.Bot(command_prefix='/', intents=intents)


@DISCORD_BOT.command()
async def mon(ctx):
  try:
    await ctx.send('monitoring server ...')
    system_info = get_system_info()
    image = create_image(system_info)
    with io.BytesIO() as image_binary:
      image.save(image_binary, 'PNG')
      image_binary.seek(0)
      await ctx.send(file=discord.File(fp=image_binary, filename='system_info.png'))
  except Exception as e:
    await ctx.send(f'An error occurred: {str(e)}')
    raise Exception(f'Detailed error: {str(e)}')


@DISCORD_BOT.command()
async def logs(ctx):
  path = Path(os.getenv('XDG_CACHE_HOME', '')) / 'halfass-it' / 'logs'
  if not path.exists():
    await ctx.send('```\nlogs not found\n```')
    return
  try:
    logs = subprocess.run(
      f'cat {path}/*.log',
      shell=True,
      capture_output=True,
      text=True,
    )
    output = logs.stdout or 'no errors found in logs'
    if len(output) > 2000:
      output = '...' + output[-1984:]
    await ctx.send(f'```\n{output}\n```')
  except Exception as e:
    await ctx.send(f'error occurred: {str(e)}')


@DISCORD_BOT.command()
async def logerr(ctx):
  path = Path(os.getenv('XDG_CACHE_HOME', '')) / 'halfass-it' / 'logs'
  if not path.exists():
    await ctx.send('```\nlogs not found\n```')
    return
  try:
    logs = subprocess.run(
      f"cat {path}/*.log | grep 'ERROR'",
      shell=True,
      capture_output=True,
      text=True,
    )
    output = logs.stdout or 'no errors found in logs'
    if len(output) > 2000:
      output = '...' + output[-1984:]
    await ctx.send(f'```\n{output}\n```')
  except Exception as e:
    await ctx.send(f'error occurred fetching logs: {str(e)}')


@DISCORD_BOT.command()
async def ping(ctx):
  await ctx.send('pong')


@DISCORD_BOT.command()
async def kys(ctx):
  await ctx.send('.|.')


@dataclass
class Bot:
  discord_token: str
  cache_dir: Path = None

  def __post_init__(self):
    self.cache_dir = self.cache_dir or CacheDir().path
    self.logger = LoggerToFile(self.cache_dir)

  def start(self):
    try:
      DISCORD_BOT.run(self.discord_token)
    except discord.errors.LoginFailure as e:
      self.logger.error(f'Failed to log in: {str(e)}')
      self.logger.error("Please check your Discord token and ensure it's correctly formatted.")
    except Exception as e:
      self.logger.error(f'An error occurred while starting the bot: {str(e)}')
