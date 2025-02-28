import discord
import os
import json
import pytz
from datetime import datetime
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from LinkChecker import LinkChecker
from broodcode_modules.broodcode import generate_paninis_menu_markdown, generate_sandwich_menu_markdown, generate_special_menu_markdown

load_dotenv()

CONFIG_FILE = 'config.json'
BREADMASTER_ROLE_ID = int(os.getenv('BREADMASTER_ROLE_ID'))
DEV_ROLE_ID = int(os.getenv('DEV_ROLE_ID'))
REMINDER_CHANNEL_ID = int(os.getenv('REMINDER_CHANNEL_ID'))
MESSAGE_CHANNEL_ID = int(os.getenv('MESSAGE_CHANNEL_ID'))


intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)

def read_config():
    """Reads the configuration from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return json.load(file)
    return {}

def write_config(data):
    """Writes the configuration data to the config file."""
    with open(CONFIG_FILE, 'w') as file:
        json.dump(data, file, indent=4)

def is_breadmaster_or_dev(interaction: discord.Interaction):
    """Check if the user has the breadmaster or dev role."""
    return any(role.id in [BREADMASTER_ROLE_ID, DEV_ROLE_ID] for role in interaction.user.roles)

async def check_link_status():
    """Check the current status of the payment link."""
    config = read_config()
    link_to_check = config.get("payment_link", "")
    if not link_to_check:
        return "No payment link set."
    
    link_checker = LinkChecker()
    return link_checker.check_link(link_to_check)

async def send_order_message():
    """Send the order message with the payment link."""
    status = await check_link_status()
    if status in ["expired", "error"]:
        reminder_channel = bot.get_channel(REMINDER_CHANNEL_ID)
        await reminder_channel.send(f"<@&{DEV_ROLE_ID}> the payment link is invalid, please enter a new one using: `/set_link [payment_link]`")
        return None

    channel = bot.get_channel(MESSAGE_CHANNEL_ID)
    full_menu = generate_full_menu()
    config = read_config()

    message_content = f"""
{config["order_message"]}
<{config["payment_link"]}>
"""
    await channel.send(content=full_menu)
    payment_message = await channel.send(content=message_content)
    return payment_message

def generate_full_menu():
    """Generates the full menu combining sandwich, special, and paninis menus."""
    special_menu = generate_special_menu_markdown()
    sandwich_menu = generate_sandwich_menu_markdown()
    paninis_menu = generate_paninis_menu_markdown()

    return special_menu + sandwich_menu +  paninis_menu

@tasks.loop(seconds=read_config()["loop_timeout"])
async def daily_check():
    """Performs the daily check every 60 seconds."""
    tz = pytz.timezone('Europe/Amsterdam')
    now = datetime.now(tz)
    payment_message = None
    if now.hour == 8 and now.minute == 0 and now.strftime("%A") == "Friday":
        print('Friday YIPPEE')
        payment_message = await send_order_message()
    elif now.hour == 10 and now.minute == 0 and now.strftime("%A") == "Friday":
        print('Not Friday')
        if payment_message:
            payment_message.edit(content="Orders are now closed. Thank you!")
        else:
            channel = bot.get_channel(MESSAGE_CHANNEL_ID)
            channel.send(content="Orders are now closed. Thank you!")

@bot.event
async def on_ready():
    """Triggered when the bot has logged in and is ready."""
    print(f'Logged in as {bot.user}')
    if not daily_check.is_running(): # type: ignore
        daily_check.start() # type: ignore
    await bot.tree.sync()

@bot.tree.command(name="check_link", description="Check the current status of the Rabobank link.")
@app_commands.check(is_breadmaster_or_dev)
async def check_link(interaction: discord.Interaction):
    """Check the current status of the payment link."""
    await interaction.response.send_message(f"Fetching status...")
    status = await check_link_status()
    await interaction.edit_original_response(content=f"<@&{BREADMASTER_ROLE_ID}>, the payment link is: {status}")

@bot.tree.command(name="set_link", description="Set a new Rabobank payment link.")
@app_commands.check(is_breadmaster_or_dev)
async def set_link(interaction: discord.Interaction, new_link: str):
    """Set a new Rabobank payment link."""
    config = read_config()
    config["payment_link"] = new_link
    write_config(config)
    await interaction.response.send_message(f"Payment link has been updated to: {new_link}")

@bot.tree.command(name="send_message", description="Sends the order message after the right payment link has been set.")
@app_commands.check(is_breadmaster_or_dev)
async def send_message(interaction: discord.Interaction):
    """Send the order message with the current payment link."""
    await interaction.response.send_message('Sending order message...')
    await send_order_message()

@bot.tree.command(name="menu", description="Show the full menu in Markdown format.")
async def menu(interaction: discord.Interaction):
    """Show the full menu in markdown format."""
    await interaction.response.send_message("Fetching menu...")
    full_menu = generate_full_menu()
    await interaction.edit_original_response(content=full_menu)

bot.run(os.getenv('DISCORD_TOKEN'))
