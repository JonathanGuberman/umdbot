from interactions import EmbedAuthor

def get_author_embed():
  """Get Author field for adding to embeds."""
  # TODO: Make UmDb logo to show here as author thumbnail.
  return EmbedAuthor(name="UmDb", url="https://unmatched.cards/umdb")
