from src.bot import MainBot
from src.token import TOKEN


if __name__ == "__main__":
    bot = MainBot()
    bot.run(TOKEN)