import logging
import os
import requests

import interactions
from dotenv import load_dotenv

from commands.card import card, DECK_SELECT_FOR_CARD_ID, CARD_SELECT_ID, select_card, select_deck_for_card

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
LOGLEVEL = os.getenv('LOG_LEVEL', 'INFO')
DECK_SELECT_ID = 'deck_select_id'

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', 
  level=getattr(logging, LOGLEVEL.upper()),
  datefmt='%Y-%m-%d %H:%M:%S')

bot = interactions.Client(token=TOKEN)

def get_deck(slug):
  r = requests.get(f'https://unmatched.cards/api/db/decks/{slug}')
  return r.json()

def search_decks(filter):
    params={'filter': filter}
    r = requests.get('https://unmatched.cards/api/db/decks', params=params)
    return r.json()['decks']

def make_deck_embed(deck):
  fields = []

  for hero in deck['heroes']:
    if len(deck['heroes']) > 1:
      fields.append(interactions.EmbedField(name="Hero Name", value=hero['name'], inline=False))

    if hero['attack_type']:
      fields.append(interactions.EmbedField(name="Attack Type", value=hero['attack_type'].title(), inline=True))
    
    if hero['hp']:
      fields.append(interactions.EmbedField(name="HP", value=hero['hp'], inline=True))
    
    if hero['quantity'] > 1:
      fields.append(interactions.EmbedField(name="Quantity", value=hero['quantity'], inline=True))
  
  if deck['movement']:
    fields.append(interactions.EmbedField(name="Move", value=deck['movement'], inline=False))

  for sidekick in deck['sidekicks']:
    if sidekick['name']:
      fields.append(interactions.EmbedField(name="Sidekick Name", value=sidekick['name'], inline=False))
    
    if sidekick['attack_type']:
      fields.append(interactions.EmbedField(name="Sidekick Attack Type", value=sidekick['attack_type'].title(), inline=True))
    
    if sidekick['hp']:
      fields.append(interactions.EmbedField(name="Sidekick HP", value=sidekick['hp'], inline=True))
    
    if sidekick['quantity'] and sidekick['quantity'] > 1:
      fields.append(interactions.EmbedField(name="Sidekick Quantity", value=sidekick['quantity'], inline=True))

  if deck['special']:
    fields.append(interactions.EmbedField(name="Special Ability", value=deck['special'], inline=False))

  if deck['notes']:
    fields.append(interactions.EmbedField(name="Notes", value=deck['notes'], inline=False))


  return interactions.Embed(
    title=deck['name'],
    description=deck['set'],
    url=f"https://unmatched.cards/umdb/decks/{deck['slug']}",
    author=get_author_embed(),
    fields=fields,
  )

def make_deck_select(decks):
  select_options = [
    interactions.SelectOption(
      label=deck['name'],
      value=deck['slug'],
    ) for deck in decks
  ]

  return interactions.SelectMenu(
    options=select_options,
    placeholder="Choose a deck",
    custom_id=DECK_SELECT_ID,
  )

@bot.component(DECK_SELECT_ID)
async def select_deck(ctx, value):
  deck = get_deck(value[0])
  embed = make_deck_embed(deck)
  await ctx.send(embeds=embed)

bot.component(CARD_SELECT_ID)(select_card)

bot.component(DECK_SELECT_FOR_CARD_ID)(select_deck_for_card)

async def deck(ctx, name):
  decks = search_decks(name)
  if len(decks) == 1:
    deck = decks[0]
    embed = make_deck_embed(deck)
    await ctx.send(embeds=embed)
  elif len(decks) > 1:
    await ctx.send("Multiple matching decks found", components=make_deck_select(decks), ephemeral=True)
  else:
    await ctx.send(f'No decks found for search term: {name}', ephemeral=True)

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