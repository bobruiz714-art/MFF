import discord, requests

from discord import *
from discord.ext.commands import *
from pymongo import *


class Constants:
    GAMEPASS = 1433209076
    ROLE = 1411104335059882045

    mongo_client : MongoClient = MongoClient("mongodb cluster url here")
    db = mongo_client["Linked"]

class Roblox():
    def __init__(self):
        super().__init__()

    @staticmethod
    def findUser(username : str) -> dict:
        r = requests.post(
            url = "https://users.roblox.com/v1/usernames/users",
            json = {
                "usernames": [ username ]
            }
        )
        return r.json()

    @staticmethod
    def ownsGamepass(id : int, gamepass : int) -> bool:
        r = requests.get(
            url = f"https://inventory.roblox.com/v1/users/{id}/items/GamePass/{gamepass}"
        )
        return len(r.json().get("data", [])) > 0

dbot : Bot = Bot(command_prefix = ";", intents = discord.Intents.all())

@dbot.event
async def on_ready():
    print("Ready | " + dbot.user.name)

@dbot.command(name="unlink")
async def unlink(ctx : Context, user : discord.Member = None):
    if not ctx.author.guild_permissions.administrator:
        return

    if user is None:
        await ctx.reply("Provide a user!")
        return
    
    crole = ctx.guild.get_role(Constants.ROLE)
    if crole in user.roles:
        await user.remove_roles(crole)
    
    doc = Constants.db.find_one({ "discord": user.id })
    if doc:
        await Constants.db.delete_one({ "discord": user.id })

    await ctx.reply("Unlinked user!")


@dbot.command(name="link")
async def link(ctx : Context, username : str):
    if str == "" or str == None:
        await ctx.reply("Please enter a username")
        return

    if Constants.db.find_one({"discord": ctx.author.id}) is not None:
        await ctx.reply("You already are linked!")
        return

    if Constants.db.find_one({"username": username}) is not None:
        await ctx.reply("This user is already linked")
        return

    found : dict = Roblox.findUser(username)
    if len(found.get("data", [])) == 0:
        await ctx.reply("User not found")
        return

    id : int = found["data"][0]["id"]
    if not Roblox.ownsGamepass(id, Constants.EG_GAMEPASS):
        await ctx.reply("You don't own the gamepass. Please purchase to redeem your role")
    else:
        Constants.db.insert_one({ "discord": ctx.author.id, "username": username })
        await ctx.author.add_roles(ctx.guild.get_role(Constants.EG_ROLE), reason="Roblox Link")
        await ctx.reply("Successfully linked! You should have your role.")

if __name__ == "__main__":
    dbot.run("")
