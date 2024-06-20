import sys
from pathlib import Path

from jsonargparse import CLI

from bot.bot import Bot


class Main:
  def __init__(self, discord_token: str, cache_dir: str) -> None:
    self.discord_token: str = discord_token
    self.cache_dir: Path = Path(cache_dir)

  def run(self):
    bot = Bot(discord_token=self.discord_token, cache_dir=self.cache_dir)
    bot.start()


def main():
  try:
    CLI(Main)
    return 0
  except KeyboardInterrupt:
    return 0
  except ValueError:
    return 0


if __name__ == '__main__':
  main()
  sys.exit(main())
