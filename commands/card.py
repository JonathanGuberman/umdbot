import interactions
import requests

from .lib import get_author_embed

CARD_SELECT_ID = 'card_select'
DECK_SELECT_FOR_CARD_ID = 'deck_select_for_card'

def search_cards(filter):
  params={'filter': filter}
  r = requests.get('https://unmatched.cards/api/db/cards', params=params)
  return r.json()['cards']

def get_card(slug):
  r = requests.get(f'https://unmatched.cards/api/db/cards/{slug}')
  return r.json()

def get_colour(card):
  first_letter = card['type'][0].lower()
  color_map = {
    'd': 0x2c76ac,
    'a': 0xdc3034,
    'v': 0x6c4e8d,
    's': 0xfcbd71,
  }
  return color_map.get(first_letter, 0xf7eadb)

def get_card_description(card):
  first_letter = card['type'][0].lower()
  if first_letter == 's':
    return 'Scheme'
  return f"{card['type'].title()} {card['value']}"

def make_card_select(cards):
  select_options = [
    interactions.SelectOption(
      label=card['title'],
      value=card['slug'],
      description=get_card_description(card),
    ) for card in cards
  ]

  return interactions.SelectMenu(
    options=select_options,
    placeholder="Choose a card",
    custom_id=CARD_SELECT_ID,
  )

def get_deck_link(deck):
  return f"[{deck['name']}](https://unmatched.cards/umdb/decks/{deck['slug']})"

def make_deckcard_embed(card, idx):
  fields = []
  decks = card['decks']
  deck = decks[idx]
  

  fields.append(interactions.EmbedField(name="Usable by", value=deck['characterName'], inline=True))
  fields.append(interactions.EmbedField(name="Boost", value=deck['boost'], inline=True))
  fields.append(interactions.EmbedField(name="Quantity", value=deck['quantity'], inline=True))

  if card['basicText']:
    fields.append(interactions.EmbedField(name="Text", value=card['basicText'], inline=False))
  
  if card['immediateText']:
    fields.append(interactions.EmbedField(name="Immediately", value=card['immediateText'], inline=False))

  if card['duringText']:
    fields.append(interactions.EmbedField(name="During combat", value=card['duringText'], inline=False))
  
  if card['afterText']:
    fields.append(interactions.EmbedField(name="After combat", value=card['afterText'], inline=False))

  if card['notes']:
    fields.append(interactions.EmbedField(name="Notes", value=card['notes'], inline=False))

  fields.append(interactions.EmbedField(
    name="Decks", 
    value=get_other_decks(decks), 
    inline=False))

  image_url = deck['image']

  return interactions.Embed(
    title=card["title"], 
    description=f"**{get_deck_link(deck)}**\n{get_card_description(card)}",
    url=f"https://unmatched.cards/umdb/cards/{card['slug']}",
    author=get_author_embed(),
    fields=fields,
    image={'url': image_url} if image_url else None,
    color=get_colour(card),
  )

def get_deck_specifics(deck):
  return f"{deck['characterName']} Boost {deck['boost']} ×{deck['quantity']}"

def get_other_decks(decks):
  if len(decks) > 1:
    other_decks = f"This card appears in {len(decks)} decks: {', '.join([deck['name'] for deck in sorted(decks, key=lambda x: x['name'])])}"
  else:
    other_decks = "This card is currently unique to this deck."
  return other_decks

async def _send_card_or_deck_select(ctx, card):
  if len(card['decks']) == 1:
    embed = make_deckcard_embed(card, 0)
    await ctx.send(embeds=embed)
  else:
    await ctx.send("Which deck version?", components=make_deck_select_for_card(card), ephemeral=True)

def make_deck_select_for_card(card):
  select_options = [
    interactions.SelectOption(
      label=deck['name'],
      value=f"{card['slug']},{idx}",
      description=get_deck_specifics(deck),
    ) for idx, deck in enumerate(card['decks'])
  ]

  select_options.insert(0, 
    interactions.SelectOption(
      label='All decks',
      value=f"{card['slug']},-1",
      description="Show general card information",
    )
  )

  return interactions.SelectMenu(
    options=select_options,
    placeholder="Choose a deck",
    custom_id=DECK_SELECT_FOR_CARD_ID,
  )

def make_card_embed(card):
      fields = []
      if card['basicText']:
        fields.append(interactions.EmbedField(name="Text", value=card['basicText'], inline=False))
      
      if card['immediateText']:
        fields.append(interactions.EmbedField(name="Immediately", value=card['immediateText'], inline=False))

      if card['duringText']:
        fields.append(interactions.EmbedField(name="During combat", value=card['duringText'], inline=False))
      
      if card['afterText']:
        fields.append(interactions.EmbedField(name="After combat", value=card['afterText'], inline=False))

      if card['notes']:
        fields.append(interactions.EmbedField(name="Notes", value=card['notes'], inline=False))

      decks = card['decks']

      fields.append(interactions.EmbedField(
        name="Decks", 
        value=get_other_decks(decks), 
        inline=False))


      return interactions.Embed(
        title=card["title"], 
        description=get_card_description(card),
        url=f"https://unmatched.cards/umdb/cards/{card['slug']}",
        author=get_author_embed(),
        fields=fields,
        color=get_colour(card),
      )


async def card(ctx, title):
  card_name=title
  cards = search_cards(card_name)
  if len(cards) > 1:
    await ctx.send("Multiple matching cards found", components=make_card_select(cards), ephemeral=True)
  elif len(cards) == 1:
    card = cards[0]
    await _send_card_or_deck_select(ctx, card)
  else:
    await ctx.send(f'No cards found for search term: {card_name}', ephemeral=True)

async def select_card(ctx, value):
  card = get_card(value[0])
  await _send_card_or_deck_select(ctx, card)

async def select_deck_for_card(ctx, value):
    slug, idx = value[0].split(',')
    card = get_card(slug)
    idx = int(idx)
    embed = make_card_embed(card) if idx < 0 else make_deckcard_embed(card, idx)
    await ctx.send(embeds=embed)