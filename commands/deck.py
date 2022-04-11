import interactions
import requests

from .lib import get_author_embed

DECK_SELECT_ID = 'deck_select_id'

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

async def select_deck(ctx, value):
  deck = get_deck(value[0])
  embed = make_deck_embed(deck)
  await ctx.send(embeds=embed)

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