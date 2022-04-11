import logging
import os
import requests

import interactions
from dotenv import load_dotenv

from commands.card import card, DECK_SELECT_FOR_CARD_ID, CARD_SELECT_ID, select_card, select_deck_for_card
from commands.deck import deck, DECK_SELECT_ID, select_deck

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
LOGLEVEL = os.getenv('LOG_LEVEL', 'INFO')

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', 
  level=getattr(logging, LOGLEVEL.upper()),
  datefmt='%Y-%m-%d %H:%M:%S')

bot = interactions.Client(token=TOKEN)

bot.component(DECK_SELECT_ID)(select_deck)

bot.component(CARD_SELECT_ID)(select_card)

bot.component(DECK_SELECT_FOR_CARD_ID)(select_deck_for_card)

@bot.command(
  name="umdb",
  description="Search UmDb",
  options=[
    interactions.Option(
      name="card",
      description="Search UmDb for a card",
      type=interactions.OptionType.SUB_COMMAND,
      options=[
        interactions.Option(
          name="card_title",
          description="Title to search",
          type=interactions.OptionType.STRING,
          required=True,
        ),
      ],
    ),
    interactions.Option(
        name="deck",
        description="Search UmDb for a deck",
        type=interactions.OptionType.SUB_COMMAND,
        options=[
          interactions.Option(
            name="deck_name",
            description="Deck name to search",
            type=interactions.OptionType.STRING,
            required=True,
          ),
        ],
    ),
  ],
)
async def cmd(ctx: interactions.CommandContext, sub_command: str, deck_name=None, card_title=None):
    if sub_command == "card":
      await card(ctx, card_title)
    elif sub_command == "deck":
      await deck(ctx, deck_name)

bot.start()