import discord
import requests
import pytz
from datetime import datetime
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
import json
from LinkChecker import LinkChecker  # Import the LinkChecker class
from broodcode_modules.broodcode import generate_paninis_menu_markdown, generate_sandwich_menu_markdown, generate_special_menu_markdown

load_dotenv()

CONFIG_FILE = 'config.json'
BREADMASTER_ROLE_ID = int(os.getenv('BREADMASTER_ROLE_ID'))
DEV_ROLE_ID = int(os.getenv('DEV_ROLE_ID'))

def read_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    else:
        return {}

def write_config(data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file, indent=4)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

def check_link_status():
    config = read_config()
    link_to_check = config.get("payment_link", "")
    if not link_to_check:
        return "No payment link set."
    
    link_checker = LinkChecker()
    return link_checker.check_link(link_to_check)

@tasks.loop(hours=24)
async def daily_check():
    tz = pytz.timezone('Europe/Amsterdam')
    now = datetime.now(tz)
    
    if now.hour == 8 and now.minute == 0:
        status = check_link_status()
        if status == "verlopen":
            channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))
            await channel.send(f"<@&{DEV_ROLE_ID}> The Rabobank betaalverzoek link is: {status}")

def is_breadmaster(interaction: discord.Interaction):
    return any(role.id == BREADMASTER_ROLE_ID for role in interaction.user.roles)

def is_dev(interaction: discord.Interaction):
    return any(role.id == DEV_ROLE_ID for role in interaction.user.roles)


@bot.tree.command(name="check_link", description="Check the current status of the Rabobank link.")
@app_commands.check(lambda interaction: is_breadmaster(interaction) or is_dev(interaction))
async def check_link(interaction: discord.Interaction):
    await interaction.response.send_message(f"Fetching status...")
    status = check_link_status()
    await interaction.edit_original_response(content=f"<@&{DEV_ROLE_ID}> The Rabobank betaalverzoek link is: {status}")


@bot.tree.command(name="set_link", description="Set a new Rabobank payment link.")
@app_commands.check(lambda interaction: is_breadmaster(interaction) or is_dev(interaction))
async def set_link(interaction: discord.Interaction, new_link: str):
    config = read_config()
    config["payment_link"] = new_link
    write_config(config)
    await interaction.response.send_message(f"Payment link has been updated to: {new_link}")

@bot.tree.command(name="menu", description="Show the full menu in Markdown format.")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message("Fetching menu...")

    sandwich_menu = generate_sandwich_menu_markdown()
    special_menu = generate_special_menu_markdown()
    paninis_menu = generate_paninis_menu_markdown()

    full_menu = sandwich_menu + special_menu + paninis_menu
    await interaction.edit_original_response(content=full_menu)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.tree.sync()
    daily_check.start()

bot.run(os.getenv('DISCORD_TOKEN'))
