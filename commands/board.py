import interactions
import requests

from .lib import get_author_embed

BOARD_SELECT_ID = 'board_select_id'

# TODO: UmDb doesn't have an endpoint for single boards!
# def get_board(slug):
#   r = requests.get(f'https://unmatched.cards/api/db/boards/{slug}')
#   return r.json()

def search_boards(filter):
    params={'filter': filter}
    r = requests.get('https://unmatched.cards/api/db/boards', params=params)
    return r.json()['boards']

def make_board_embed(board):
  fields = []

  if board['max_players']:
    fields.append(interactions.EmbedField(name="Max Players", value=board['max_players'], inline=True))

  if board['spaces_count']:
    fields.append(interactions.EmbedField(name="Space Count", value=board['spaces_count'], inline=True))

  if board['zone_count']:
    fields.append(interactions.EmbedField(name="Zone Count", value=board['zone_count'], inline=True))

  if board['notes']:
    fields.append(interactions.EmbedField(name="Notes", value=board['notes'], inline=False))

  image_url = board['image']

  return interactions.Embed(
    title=board['name'],
    author=get_author_embed(),
    fields=fields,
    image={'url': image_url} if image_url else None,
  )

def make_board_select(boards):
  select_options = [
    interactions.SelectOption(
      label=board['name'],
      value=board['name'],
    ) for board in boards
  ]

  return interactions.SelectMenu(
    options=select_options,
    placeholder="Choose a board",
    custom_id=BOARD_SELECT_ID,
  )

async def select_board(ctx, value):
  board = search_boards(value[0])
  embed = make_board_embed(board[0])
  await ctx.send(embeds=embed)

async def board(ctx, name):
  boards = search_boards(name)
  if len(boards) == 1:
    board = boards[0]
    embed = make_board_embed(board)
    await ctx.send(embeds=embed)
  elif len(boards) > 1:
    await ctx.send("Multiple matching boards found", components=make_board_select(boards), ephemeral=True)
  else:
    await ctx.send(f'No boards found for search term: {name}', ephemeral=True)