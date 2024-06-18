import sys

from jsonargparse import CLI

from bot.bot import Bot


class Main:
  def __init__(self, ip: str, port: str, cache_dir: str) -> None:
    self.ip: str = ip
    self.port: int = int(port)
    self.cache_dir: str = cache_dir

  def run(self):
    bot = Bot(self.ip, self.port, self.cache_dir)
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
