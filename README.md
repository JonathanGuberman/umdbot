# UmDbot: an Unmatched Discord bot

UmDbot is a Discord bot that queries [UmDb](https://unmatched.cards/umdb)
and displays nicely-formatted Unmatched data.

## Commands

### `/umdb card [title search]`
Search UmDb for a card. If multiple cards match the search term, a select box
will be shown to the user. If a card is present in multiple decks, the user will
be shown a select box where they can show data for the card in general, or for
a deck-specific version of the card. Deck-specific information includes the boost,
quantity, who can user the card, and art if available.

Note that card value is not considered deck-specific. If a card has multiple values
(as with Second Shot), UmDb considers those different cards.

### `/umdb deck [name search]`
Search UmDb for a deck. If multiple decks match the search term, a select box
will be shown to the user.

### `/umdb board [name search]`
Search UmDb for a board. If multiple boards match the search term, a select box
will be shown to the user.

## About

UmDbot is made using the [Interactions.py](https://interactions.fl0w.dev/) Discord
library.

Feel free to add an issue, make a PR, or talk about the bot in the [Unmatched Maker
Discord](https://discord.com/invite/DZDHn8U).
