import os
import requests

import interactions
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CARD_SELECT_ID = 'card_select'

bot = interactions.Client(token=TOKEN)

def search_cards(filter):
  params={'filter': filter}
  r = requests.get('https://unmatched.cards/api/db/cards', params=params)
  return r.json()['cards']

def get_card(slug):
  r = requests.get(f'https://unmatched.cards/api/db/cards/{slug}')
  return r.json()

def get_card_description(card):
  first_letter = card['type'][0].lower()
  if first_letter == 's':
    return 'Scheme'
  return f"{card['type'].title()} {card['value']}"

def get_colour(card):
  first_letter = card['type'][0].lower()
  color_map = {
    'd': 0x2c76ac,
    'a': 0xdc3034,
    'v': 0x6c4e8d,
    's': 0xfcbd71,
  }
  return color_map.get(first_letter, 0xf7eadb)

def make_card_embed(card):
      fields = []
      if card['basicText']:
        fields.append(interactions.EmbedField(name="Text", value=card['basicText'], inline=False))
      
      if card['immediateText']:
        fields.append(interactions.EmbedField(name="Immediately", value=card['immediateText'], inline=True))

      if card['duringText']:
        fields.append(interactions.EmbedField(name="During combat", value=card['duringText'], inline=True))
      
      if card['afterText']:
        fields.append(interactions.EmbedField(name="After combat", value=card['afterText'], inline=True))

      if card['notes']:
        fields.append(interactions.EmbedField(name="Notes", value=card['notes'], inline=False))

      image_url = card['decks'][0]['image']

      return interactions.Embed(
        title=card["title"], 
        description=get_card_description(card),
        url=f"https://unmatched.cards/umdb/cards/{card['slug']}",
        author=interactions.EmbedAuthor(name="UmDb", url="https://unmatched.cards/umdb"),
        fields=fields,
        image={'url': image_url} if image_url else None,
        color=get_colour(card),
      )

def make_card_select(cards):
  select_options = [
    interactions.SelectOption(
      label=card['title'],
      value=card['slug'],
      description=get_card_description(card),
    ) for idx, card in enumerate(cards)
  ]

  return interactions.SelectMenu(
    options=select_options,
    placeholder="Choose a card",
    custom_id=CARD_SELECT_ID,
  )

@bot.component(CARD_SELECT_ID)
async def select_card(ctx, value):
    card = get_card(value[0])
    embed = make_card_embed(card)
    await ctx.send(embeds=embed)

@bot.command(
  name="umcard", 
  description="Search for an Unmatched card in UmDb",
  options = [
    interactions.Option(
      name="title",
      description="Card title",
      type=interactions.OptionType.STRING,
      required=True,
    ),
  ]
)
async def card(ctx, title):
    card_name=title
    cards = search_cards(card_name)
    if len(cards) > 1:
     await ctx.send("Multiple matching cards found", components=make_card_select(cards), ephemeral=True)
    elif len(cards) == 1:
      card = cards[0]
      embed = make_card_embed(card)
      await ctx.send(embeds=embed)
    else:
      await ctx.send(f'No cards found for search term: {card_name}', ephemeral=True)

bot.start()