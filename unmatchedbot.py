import os
import requests

import discord
from discord.ext import commands
from discord_components import DiscordComponents, Select, SelectOption
from discord_slash import SlashCommand, SlashContext
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')
DiscordComponents(bot)

def get_cards(filter):
  params={'filter': filter}
  r = requests.get('https://unmatched.cards/api/db/cards', params=params)
  return r.json()['cards']

def make_card_embed(card):
      embed=discord.Embed(
        title=card["title"], 
        description=f"{card['type']} {card['value']}",
        url=f"https://unmatched.cards/umdb/cards/{card['slug']}",
      )
      embed.set_author(name="UmDb", url="https://unmatched.cards/umdb")

      if card['basicText']:
        embed.add_field(name="Text", value=card['basicText'], inline=False)
      
      if card['immediateText']:
        embed.add_field(name="Immediately", value=card['immediateText'], inline=True)

      if card['duringText']:
        embed.add_field(name="During combat", value=card['duringText'], inline=True)
      
      if card['afterText']:
        embed.add_field(name="After combat", value=card['afterText'], inline=True)

      if card['notes']:
        embed.add_field(name="Notes", value=card['notes'], inline=False)

      image = card['decks'][0]['image']
      if image:
        embed.set_thumbnail(url=card['decks'][0]['image'])
      return embed

@bot.command()
async def card(ctx, card_name):
    cards = get_cards(card_name)
    if len(cards) > 1:
      card = next((card for card in cards if card['title'].casefold() == card_name.casefold()), None)
      if card:
        embed = make_card_embed(card)
        await ctx.send(embed=embed)
      else:
        # response = f'I found {len(cards)} cards matching those terms:\n'
        # response += '\n'.join([card['title'] for card in cards])
        # await ctx.send(response)
        await ctx.send(
        "I found multiple matches:",
          components = [
            Select(
              placeholder = "Choose a card",
              options = [
                  SelectOption(label = card['title'], value = idx)
                  for idx, card in enumerate(cards)
              ]
            )
          ]
        )
        interaction = await bot.wait_for("select_option")
      
        idx = int(interaction.values[0])
        await interaction.send(embed = make_card_embed(cards[idx]), ephemeral=False)
    elif len(cards) == 1:
      card = cards[0]
      embed = make_card_embed(card)
      await ctx.send(embed=embed)
      # response = f'**{card["title"]}**\n{card["type"]} {card["value"]}'
    else:
      await ctx.send(f'No cards found for search term: {card_name}')

bot.run(TOKEN)