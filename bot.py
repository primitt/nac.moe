# TODO: Make discord bot with functions to add events ect
from typing import Optional
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from db.db import database, events, news, settings
import datetime
import os

load_dotenv(override=True)

bot = commands.Bot(command_prefix=["Mi!", "mi!"],
                   intents=nextcord.Intents.all())


@bot.event
async def on_ready():
    # add a status to the bot
    await bot.change_presence(activity=nextcord.Game(name="Northwood High School Anime Club"))
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.slash_command(guild_ids=[1342913889544962090])
async def create_event(
    interaction: nextcord.Interaction,
    event_type: str = nextcord.SlashOption(name="type", choices=[
                                           "Meeting", "Convention", "Local Event", "Movie"], required=True),
    name: str = nextcord.SlashOption(
        name="name", description="Name of the event", required=True),
    date: Optional[str] = nextcord.SlashOption(
        name="date", description="Date of the event (DD/MM/YYYY) ex. 03/03/2025", required=False),
    date_end: Optional[str] = nextcord.SlashOption(
        name="date_end", description="End date of the event (DD/MM/YYYY) ex. 03/03/2025", required=False),
    time: Optional[str] = nextcord.SlashOption(
        name="time", description="Range of time of the event (No format) Ex. Lunch, All Day, 7 PM - 12 AM", required=False),
    location: Optional[str] = nextcord.SlashOption(
        name="location", description="Location of the event", required=False),
    url: Optional[str] = nextcord.SlashOption(
        name="url", description="URL of the event", required=False)
):
    if date:
        parsed_date = datetime.datetime.strptime(date, "%m/%d/%Y")
    else:
        parsed_date = None
    if date_end:
        parsed_date_end = datetime.datetime.strptime(date_end, "%m/%d/%Y")
    else:
        parsed_date_end = None

    # Check if event already exists
    existing_event = events.select().where(
        (events.name == name) & (events.date == parsed_date)
    ).first()

    if existing_event:
        await interaction.response.send_message(f"Event `{name}` on `{date}` already exists!", ephemeral=True)
        return

    # Create the event
    event = events.create(
        type=event_type, name=name, date=parsed_date, date_end=parsed_date_end, time=time, location=location, url=url)
    await interaction.response.send_message(f"Event `{event.name}` with id `{event.id}` created!")


@bot.slash_command(guild_ids=[1342913889544962090])
async def all_events(interaction: nextcord.Interaction):
    all_events = events.select()
    event_list = []
    event_list.append("```Events (Name, Type, Date, Ending Date, Time, Location, URL):")
    for event in all_events:
        event_list.append(f"(ID) {event.id}. {event.name} - {event.type} - {event.date} - {event.date_end} - {event.time} - {event.location} - {event.url}")
        event_list.append("\n")
    event_list.append("```")
    await interaction.response.send_message("\n".join(event_list))  

@bot.slash_command(guild_ids=[1342913889544962090])
async def delete_event(
    interaction: nextcord.Interaction,
    event_id: int = nextcord.SlashOption(name="id", description="ID of the event", required=True)
):
    try:
        event = events.get(events.id == event_id)
        event.delete_instance()
        await interaction.response.send_message(f"Event `{event.name}` with id `{event.id}` deleted!")
    except events.DoesNotExist:
        await interaction.response.send_message(f"Error: No event found with ID `{event_id}`.", ephemeral=True)

@bot.slash_command(guild_ids=[1342913889544962090])
async def create_news(
    interaction: nextcord.Interaction,
    title: str = nextcord.SlashOption(name="title", description="Title of the news", required=True),
    content: str = nextcord.SlashOption(name="content", description="Content of the news", required=True),
):
    author = interaction.user.nick if interaction.user.nick else interaction.user.name
    # Create the news
    news_cmd = news.create(
        title=title, date=datetime.datetime.now(), content=content, author=author)
    await interaction.response.send_message(f"News `{news_cmd.title}` with id `{news_cmd.id}` created!")
@bot.slash_command(guild_ids=[1342913889544962090])
async def all_news(interaction: nextcord.Interaction):
    all_news = news.select()
    news_list = []
    news_list.append("```News (Title, Content, Date, Author):")
    for news_cmd in all_news:
        news_list.append(f"(ID) {news_cmd.id}. {news_cmd.title} - {news_cmd.content} - {news_cmd.date} - {news_cmd.author}")
        news_list.append("\n")
    news_list.append("```")
    await interaction.response.send_message("\n".join(news_list))

@bot.slash_command(guild_ids=[1342913889544962090])
async def delete_news(
    interaction: nextcord.Interaction,
    news_id: int = nextcord.SlashOption(name="id", description="ID of the news", required=True)
):
    try:
        news_cmd = news.get(news.id == news_id)
        news_cmd.delete_instance()
        await interaction.response.send_message(f"News `{news_cmd.title}` with id `{news_cmd.id}` deleted!")
    except news.DoesNotExist:
        await interaction.response.send_message(f"Error: No news found with ID `{news_id}`.", ephemeral=True)

@bot.slash_command(guild_ids=[1342913889544962090])
async def get_setting(
    interaction: nextcord.Interaction,
    setting_name: str = nextcord.SlashOption(name="name", description="Name of the setting, blank to get all", required=False)
):
    if setting_name:
        setting = settings.get(settings.name == setting_name)
        await interaction.response.send_message(f"Setting `{setting.name}` has value: `{setting.value}`")
    else:
        all_settings = settings.select()
        settings_list = [f"Setting `{s.name}` has value: `{s.value}`" for s in all_settings]
        await interaction.response.send_message("\n".join(settings_list))
        
@bot.slash_command(guild_ids=[1342913889544962090])
async def set_setting(
    interaction: nextcord.Interaction,
    setting_name: str = nextcord.SlashOption(name="name", description="Name of the setting", required=True),
    setting_value: str = nextcord.SlashOption(name="value", description="Value of the setting", required=True)
):
    setting = settings.select().where(settings.name == setting_name).first()
    if not setting:
        await interaction.response.send_message(f"Error: Setting with name `{setting_name}` does not exist.", ephemeral=True)
        return 
    setting.value = setting_value
    setting.save()
    await interaction.response.send_message(f"Setting `{setting.name}` updated to value: `{setting.value}`")

@bot.slash_command(guild_ids=[1342913889544962090])
async def create_setting(
    interaction: nextcord.Interaction,
    setting_name: str = nextcord.SlashOption(name="name", description="Name of the setting", required=True),
    setting_value: str = nextcord.SlashOption(name="value", description="Value of the setting", required=True)
):
    setting, created = settings.get_or_create(name=setting_name, defaults={'value': setting_value})
    if not created:
        await interaction.response.send_message(f"Error: Setting with name `{setting_name}` already exists.", ephemeral=True)
        return
    await interaction.response.send_message(f"Setting `{setting.name}` created with value: `{setting.value}`")
        
        
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
