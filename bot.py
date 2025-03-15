# TODO: Make discord bot with functions to add events ect
from typing import Optional
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from db.db import database, events
import datetime
import os

load_dotenv()

bot = commands.Bot(command_prefix=["Mi!", "mi!"],
                   intents=nextcord.Intents.all())


@bot.event
async def on_ready():
    # add a status to the bot
    await bot.change_presence(activity=nextcord.Game(name="Blue Archive"))
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.slash_command(guild_ids=[1342913889544962090])
async def create_event(
    interaction: nextcord.Interaction,
    event_type: str = nextcord.SlashOption(name="type", choices=[
                                           "Meeting", "Convention", "Local Event", "Movie"], required=True),
    name: str = nextcord.SlashOption(
        name="name", description="Name of the event", required=True),
    date: Optional[str] = nextcord.SlashOption(
        name="date", description="Date of the event (YYYY-MM-DD) ex. 2025-03-02", required=False),
    time: Optional[str] = nextcord.SlashOption(
        name="time", description="Time of the event (HH:MM)", required=False),
    location: Optional[str] = nextcord.SlashOption(
        name="location", description="Location of the event", required=False),
    url: Optional[str] = nextcord.SlashOption(
        name="url", description="URL of the event", required=False)
):
    if date:
        parsed_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    else:
        parsed_date = None
    event = events.create(
        type=event_type, name=name, date=parsed_date, time=time, location=location, url=url)
    await interaction.response.send_message(f"Event `{event.name}` with id `{event.id}` created!")

@bot.slash_command(guild_ids=[1342913889544962090])
async def all_events(interaction: nextcord.Interaction):
    all_events = events.select()
    event_list = []
    event_list.append("Events (Name, Type, Date, Time, Location, URL):")
    for event in all_events:
        event_list.append(f"(ID) {event.id}. {event.name} - {event.type} - {event.date} - {event.time} - {event.location} - {event.url}")
    await interaction.response.send_message("\n".join(event_list))  

@bot.slash_command(guild_ids=[1342913889544962090])
async def delete_event(
    interaction: nextcord.Interaction,
    event_id: int = nextcord.SlashOption(name="id", description="ID of the event", required=True)
):
    event = events.get(events.id == event_id)
    event.delete_instance()
    await interaction.response.send_message(f"Event `{event.name}` with id `{event.id}` deleted!")
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
