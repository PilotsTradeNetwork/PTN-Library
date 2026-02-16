# Define whether the bot is in testing or live mode. Default is testing mode.
import discord
import os


# define bot token
TOKEN = os.getenv("DISCORD_TOKEN_PROD")

############################
### Production variables ###
############################
"""
For consistency, please prepend all emoji with "EMOJI_"
"""

DISCORD_GUILD = 800080948716503040  # PTN server ID
guild_obj = discord.Object(DISCORD_GUILD)

# Emoji
EMOJI_ASSASSIN = 806498760586035200  # PTN :assassin: emoji
EMOJI_CARRIER_DONE = 878216234653605968  # PTN :fc_complete: emoji
EMOJI_CARRIER_EMPTY = 878216288525242388  # PTN :fc_empty: emoji
EMOJI_DISCORD_EMOJI = 1122605426844905503  # PTN :discord: emoji
EMOJI_LOADING_ICON = 1160871046786846780  # PTN :loading_icon: emoji
EMOJI_O7 = 806138784294371368  # PTN :o7: emoji
EMOJI_PTN_ROLE_ICON = 1109925017443115088  # PTN :PTN_roleicon: emoji
EMOJI_THOON = 1058010828458176563  # PTN :thoon: emoji
EMOJI_UNLOADING_ICON = 1160881163641049178  # PTN :unloading_icon: emoji
EMOJI_UPVOTE = 828287733227192403  # PTN :upvote: emoji
