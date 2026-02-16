# Define whether the bot is in testing or live mode. Default is testing mode.
import discord
import os


# define bot token
TOKEN = os.getenv("DISCORD_TOKEN_TESTING")

#########################
### Testing variables ###
#########################
"""
For consistency, please prepend all emoji with "EMOJI_"
"""

DISCORD_GUILD = 818174236480897055  # PANTS server ID
guild_obj = discord.Object(DISCORD_GUILD)

# Emoji
EMOJI_ASSASSIN = 848957573792137247  # PANTS :assassin: emoji
EMOJI_CARRIER_DONE = 884673510067286076  # PANTS :fc_complete: emoji
EMOJI_CARRIER_EMPTY = 974747678183424050  # PANTS :fc_empty: emoji
EMOJI_DISCORD_EMOJI = 1122605718198026300  # PANTS :discord: emoji
EMOJI_LOADING_ICON = 1160883199833014362  # PANTS :loading_icon: emoji
EMOJI_O7 = 903744117144698950  # PANTS :o7: emoji
EMOJI_PTN_ROLE_ICON = 1409301482934898719  # PANTS :PTN_roleicon: emoji
EMOJI_THOON = 1301319362489356289  # PANTS :thoon: emoji
EMOJI_UNLOADING_ICON = 1160883198419542077  # PANTS :unloading_icon: emoji
EMOJI_UPVOTE = 849388681382068225  # PANTS :upvote: emoji
