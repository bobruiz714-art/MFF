import discord
from discord.ext import commands
import requests
import json
import os

TOKEN = 'YOUR_DISCORD_BOT_TOKEN'
GUILD_ID = 1411094363819343882  # Replace with your server ID
ROLE_ID = 1411104335059882045  # Replace with the role ID to give
GAMEPASS_ID = 1433209076        # Replace with your Game Pass ID

LINKS_FILE = 'linked_accounts.json'

# Load or initialize the account link data
if os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, 'r') as f:
        linked_accounts = json.load(f)
else:
    linked_accounts = {}

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

def save_links():
    with open(LINKS_FILE, 'w') as f:
        json.dump(linked_accounts, f)

def owns_gamepass(roblox_user_id):
    url = f"https://inventory.roblox.com/v1/users/{roblox_user_id}/items/GamePass/{GAMEPASS_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return len(data.get("data", [])) > 0
    return False

def get_roblox_user_id(username):
    url = f"https://api.roblox.com/users/get-by-username?username={username}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("Id")
    return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def link(ctx, roblox_username):
    discord_id = str(ctx.author.id)

    if discord_id in linked_accounts:
        await ctx.send("You already linked an account. Use `!unlink` first.")
        return

    # Prevent multiple Discord accounts linking the same Roblox account
    if roblox_username in linked_accounts.values():
        await ctx.send("That Roblox account is already linked to another Discord user.")
        return

    roblox_user_id = get_roblox_user_id(roblox_username)
    if not roblox_user_id:
        await ctx.send("Roblox user not found.")
        return

    if not owns_gamepass(roblox_user_id):
        await ctx.send("You don't own the required Game Pass.")
        return

    # Save the link
    linked_accounts[discord_id] = roblox_username
    save_links()

    # Add the role
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(ctx.author.id)
    role = guild.get_role(ROLE_ID)

    if member and role:
        await member.add_roles(role)
        await ctx.send(f"✅ Linked with {roblox_username}. Role assigned.")
    else:
        await ctx.send("Something went wrong assigning the role.")

@bot.command()
async def unlink(ctx):
    discord_id = str(ctx.author.id)

    if discord_id not in linked_accounts:
        await ctx.send("You don't have a linked account.")
        return

    # Remove role
    guild = bot.get_guild(GUILD_ID)
    member = guild.get_member(ctx.author.id)
    role = guild.get_role(ROLE_ID)

    if member and role:
        await member.remove_roles(role)

    del linked_accounts[discord_id]
    save_links()
    await ctx.send("🔓 Your account has been unlinked and role removed.")

bot.run(MTQxNTQyODgwMTY4MDM3NTg2OQ.Ghq2qx.7mFQTXVfj99BX705lXL5zWSj2CdMqQRJiRwuWw)
