from typing import Optional
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv
from db.db import events, news, officers, reviews, settings
import datetime
import os
from AnilistPython import Anilist
import requests


anilist = Anilist()
load_dotenv(override=True)

bot = commands.Bot(command_prefix=["Mi!", "mi!"],
                   intents=nextcord.Intents.all())


@bot.event
async def on_ready():
    # add a status to the bot
    await bot.change_presence(activity=nextcord.Game(name="Northwood High School Anime Club"))
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

# EVENTS
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



# NEWS
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



# SETTINGS
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



# OFFICERS
@bot.slash_command(guild_ids=[1342913889544962090])
async def add_officer(
    interaction: nextcord.Interaction,
    name: str = nextcord.SlashOption(name="name", description="Name of the officer", required=True),
    position: str = nextcord.SlashOption(name="position", description="Position of the officer", required=True),
    bio: str = nextcord.SlashOption(name="bio", description="Bio of the officer", required=True),
    order: int = nextcord.SlashOption(name="order", description="Order of the officer", required=False),
    pfp: Optional[str] = nextcord.SlashOption(name="pfp", description="Profile picture URL of the officer", required=False),
    favorite_anime: Optional[str] = nextcord.SlashOption(name="favorite_anime", description="Favorite anime of the officer (enter AniList URL)", required=False)
):
    if pfp is None:
        pfp = "https://upload.wikimedia.org/wikipedia/commons/a/ac/Default_pfp.jpg"
    if favorite_anime is not None:
        # extract the id from the url
        try:
            if "anilist.co/anime/" in favorite_anime:
                ani_id = int(favorite_anime.split("anilist.co/anime/")[1].split("/")[0])
            else:
                await interaction.response.send_message("Error: Invalid AniList URL. Please provide a valid URL.", ephemeral=True)
                return
            print(ani_id)
            ani_data = anilist.get_anime_with_id(ani_id)
            fav_name = ani_data['name_english']
            fav_img = ani_data['cover_image']
            fav_url = f"https://anilist.co/anime/{ani_id}"
            fav_genre = ", ".join(ani_data['genres']) if 'genres' in ani_data else "N/A"
            fav_season = f"{ani_data['season'][0]}{ani_data['season'][1:].lower()} {ani_data['starting_time'].split('/')[-1]}" if 'season' in ani_data and 'starting_time' in ani_data else "N/A"
            fav_bio = ani_data['desc'] if 'desc' in ani_data else "N/A"
            fav_score_al = str(ani_data['average_score']) if 'average_score' in ani_data else "N/A"
            fav_score_mal = "N/A"
            # call mal api to get the score https://api.jikan.moe/v4/anime?q={query name here}&limit=1
            try:
                mal_response = requests.get(
                    f"https://api.jikan.moe/v4/anime?q={ani_data['name_romaji']}&limit=1",
                    timeout=10
                )
                if mal_response.status_code == 200:
                    mal_data = mal_response.json()
                    if 'data' in mal_data and len(mal_data['data']) > 0 and 'score' in mal_data['data'][0]:
                        fav_score_mal = str(mal_data['data'][0]['score'])
            except requests.exceptions.RequestException:
                # If MAL API fails, continue with N/A
                pass
        except Exception as e:
            await interaction.response.send_message(f"Error: Could not fetch anime/manga data. {str(e)}", ephemeral=True)
            return
        officers.create(
            name=name, position=position, bio=bio, pfp=pfp, favorite_anime_enabled=True,
            favorite_anime_name=fav_name, favorite_anime_img=fav_img, favorite_anime_genre=fav_genre,
            favorite_anime_season=fav_season, favorite_anime_bio=fav_bio,
            favorite_anime_score_al=fav_score_al, favorite_anime_score_mal=fav_score_mal, favorite_anime_url_al=fav_url, order=order
        )
        await interaction.response.send_message(f"Officer `{name}` created with favorite anime `{fav_name}`!")
    else:
        officers.create(
            name=name, position=position, bio=bio, pfp=pfp, order=order
        )
        await interaction.response.send_message(f"Officer `{name}` created without a favorite anime!")
@bot.slash_command(guild_ids=[1342913889544962090])
async def edit_officer(
    interaction: nextcord.Interaction,
    officer_id: int = nextcord.SlashOption(name="id", description="ID of the officer", required=True),
    name: Optional[str] = nextcord.SlashOption(name="name", description="Name of the officer", required=False),
    position: Optional[str] = nextcord.SlashOption(name="position", description="Position of the officer", required=False),
    bio: Optional[str] = nextcord.SlashOption(name="bio", description="Bio of the officer", required=False),
    pfp: Optional[str] = nextcord.SlashOption(name="pfp", description="Profile picture URL of the officer", required=False),
    favorite_anime: Optional[str] = nextcord.SlashOption(name="favorite_anime", description="Favorite anime of the officer (enter AniList URL)", required=False),
    disable_favorite_anime: Optional[bool] = nextcord.SlashOption(name="disable_favorite_anime", description="Disable favorite anime section", required=False, default=False),
    order: Optional[int] = nextcord.SlashOption(name="order", description="Order of the officer", required=False),
    current: Optional[bool] = nextcord.SlashOption(name="current", description="Is this officer a current staff member?", required=False),
    year: Optional[int] = nextcord.SlashOption(name="year", description="Year for past staff (e.g. 2024)", required=False)
):
    try:
        officer = officers.get(officers.id == officer_id)
    except officers.DoesNotExist:
        await interaction.response.send_message(f"Error: No officer found with ID `{officer_id}`.", ephemeral=True)
        return
    if name:
        officer.name = name
    if position:
        officer.position = position
    if bio:
        officer.bio = bio
    if pfp:
        officer.pfp = pfp
    if order is not None:
        officer.order = order
    if favorite_anime:
        try:
            if "anilist.co/anime/" in favorite_anime:
                ani_id = int(favorite_anime.split("anilist.co/anime/")[1].split("/")[0])
            else:
                await interaction.response.send_message("Error: Invalid AniList URL. Please provide a valid URL.", ephemeral=True)
                return
            print(ani_id)
            ani_data = anilist.get_anime_with_id(ani_id)
            fav_name = ani_data['name_english']
            fav_img = ani_data['cover_image']
            fav_url = f"https://anilist.co/anime/{ani_id}"
            fav_genre = ", ".join(ani_data['genres']) if 'genres' in ani_data else "N/A"
            fav_season = f"{ani_data['season'][0]}{ani_data['season'][1:].lower()} {ani_data['starting_time'].split('/')[-1]}" if 'season' in ani_data and 'starting_time' in ani_data else "N/A"
            fav_bio = ani_data['desc'] if 'desc' in ani_data else "N/A"
            fav_score_al = str(ani_data['average_score']) if 'average_score' in ani_data else "N/A"
            fav_score_mal = "N/A"
            try:
                mal_response = requests.get(
                    f"https://api.jikan.moe/v4/anime?q={ani_data['name_romaji']}&limit=1",
                    timeout=10
                )
                if mal_response.status_code == 200:
                    mal_data = mal_response.json()
                    if 'data' in mal_data and len(mal_data['data']) > 0 and 'score' in mal_data['data'][0]:
                        fav_score_mal = str(mal_data['data'][0]['score'])
            except requests.exceptions.RequestException:
                pass
        except Exception as e:
            await interaction.response.send_message(f"Error: Could not fetch anime/manga data. {str(e)}", ephemeral=True)
            return
        officer.favorite_anime_enabled = True
        officer.favorite_anime_name = fav_name
        officer.favorite_anime_img = fav_img
        officer.favorite_anime_url_al = fav_url
        officer.favorite_anime_genre = fav_genre
        officer.favorite_anime_season = fav_season
        officer.favorite_anime_bio = fav_bio
        officer.favorite_anime_score_al = fav_score_al
        officer.favorite_anime_score_mal = fav_score_mal
    if disable_favorite_anime:
        officer.favorite_anime_enabled = False
        officer.favorite_anime_name = None
        officer.favorite_anime_img = None
        officer.favorite_anime_url_al = None
        officer.favorite_anime_genre = None
        officer.favorite_anime_season = None
        officer.favorite_anime_bio = None
        officer.favorite_anime_score_al = None
        officer.favorite_anime_score_mal = None
    if current is not None:
        officer.current = current
    if year is not None:
        officer.year = year
    await interaction.response.send_message(f"Officer `{officer.name}` with id `{officer.id}` updated!")
    officer.save()

@bot.slash_command(guild_ids=[1342913889544962090])
async def all_officers(interaction: nextcord.Interaction):
    all_officers_q = officers.select().where(officers.current == True)
    officer_list = []
    officer_list.append("```Officers (Name, Position, Bio, Favorite Anime Enabled, Favorite Anime Name, Favorite Anime Genre, Favorite Anime Season, Favorite Anime Score AniList, Favorite Anime Score MyAnimeList), Order:")
    for officer in all_officers_q:
        officer_list.append(f"(ID) {officer.id}. {officer.name} - {officer.position} - {officer.bio} - {officer.favorite_anime_enabled} - {officer.favorite_anime_name} - {officer.favorite_anime_genre} - {officer.favorite_anime_season} - {officer.favorite_anime_score_al} - {officer.favorite_anime_score_mal} - {officer.order}")
        officer_list.append("\n")
    officer_list.append("```")
    full_message = "\n".join(officer_list)
    if len(full_message) > 2000:
        chunks = []
        current_chunk = ["```Officers (Name, Position, Bio, Favorite Anime Enabled, Favorite Anime Name, Favorite Anime Genre, Favorite Anime Season, Favorite Anime Score AniList, Favorite Anime Score MyAnimeList), Order:"]
        current_length = len(current_chunk[0]) + 1
        for line in officer_list[1:-1]:
            line_length = len(line) + 1
            if current_length + line_length + 4 > 2000 and len(current_chunk) > 1:
                current_chunk.append("```")
                chunks.append("\n".join(current_chunk))
                current_chunk = ["```Officers (continued):", line]
                current_length = len("```Officers (continued):") + 1 + line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        if current_chunk:
            current_chunk.append("```")
            chunks.append("\n".join(current_chunk))
        await interaction.response.send_message(chunks[0])
        for chunk in chunks[1:]:
            await interaction.followup.send(chunk)
    else:
        await interaction.response.send_message(full_message)

@bot.slash_command(guild_ids=[1342913889544962090])
async def move_officers_to_archive(
    interaction: nextcord.Interaction,
    year: int = nextcord.SlashOption(name="year", description="Year to archive current officers into", required=True)
):
    try:
        updated = officers.update({officers.current: False, officers.year: year}).where(officers.current == True).execute()
        await interaction.response.send_message(f"Archived {updated} officers into year {year}.")
    except Exception as e:
        await interaction.response.send_message(f"Error archiving officers: {e}", ephemeral=True)

@bot.slash_command(guild_ids=[1342913889544962090])
async def get_past_officer(
    interaction: nextcord.Interaction,
    officer_id: Optional[int] = nextcord.SlashOption(name="id", description="ID of the past officer", required=False),
    name: Optional[str] = nextcord.SlashOption(name="name", description="Name of the past officer (exact match)", required=False)
):
    if not officer_id and not name:
        await interaction.response.send_message("Provide either `id` or `name` to lookup a past officer.", ephemeral=True)
        return
    try:
        if officer_id:
            o = officers.get((officers.id == officer_id) & (officers.current == False))
            await interaction.response.send_message(f"(ID) {o.id}. {o.name} - {o.position} - Year: {o.year} - Bio: {o.bio}")
            return
        if name:
            q = officers.select().where((officers.name == name) & (officers.current == False))
            results = list(q)
            if not results:
                await interaction.response.send_message(f"No past officer found with name `{name}`.", ephemeral=True)
                return
            lines = []
            for o in results:
                lines.append(f"(ID) {o.id}. {o.name} - {o.position} - Year: {o.year} - Bio: {o.bio}")
            await interaction.response.send_message("\n".join(lines))
    except officers.DoesNotExist:
        await interaction.response.send_message(f"No past officer found with ID `{officer_id}`.", ephemeral=True)

@bot.slash_command(guild_ids=[1342913889544962090])
async def delete_officer(
    interaction: nextcord.Interaction,
    officer_id: int = nextcord.SlashOption(name="id", description="ID of the officer", required=True)
):
    try:
        officer = officers.get(officers.id == officer_id)
        officer.delete_instance()
        await interaction.response.send_message(f"Officer `{officer.name}` with id `{officer.id}` deleted!")
    except officers.DoesNotExist:
        await interaction.response.send_message(f"Error: No officer found with ID `{officer_id}`.", ephemeral=True)


@bot.slash_command(guild_ids=[1342913889544962090])
async def reorder_officers(
    interaction: nextcord.Interaction,
    officer_ids: str = nextcord.SlashOption(
        name="officer_ids",
        description="All current officer IDs in display order, separated by commas",
        required=True
    )
):
    try:
        ordered_ids = [int(value.strip()) for value in officer_ids.split(",")]
    except ValueError:
        await interaction.response.send_message("Officer IDs must be comma-separated numbers.", ephemeral=True)
        return

    current_ids = {officer.id for officer in officers.select().where(officers.current == True)}
    if len(ordered_ids) != len(set(ordered_ids)) or set(ordered_ids) != current_ids:
        await interaction.response.send_message(
            f"Provide every current officer ID exactly once. Current IDs: {', '.join(map(str, sorted(current_ids)))}",
            ephemeral=True
        )
        return

    with officers._meta.database.atomic():
        for position, officer_id in enumerate(ordered_ids, start=1):
            officers.update(order=position).where(officers.id == officer_id).execute()
    await interaction.response.send_message("Officer display order updated.")


# MONTHLY PICKS AND REVIEWS
@bot.slash_command(guild_ids=[1342913889544962090])
async def create_review(
    interaction: nextcord.Interaction,
    title: str = nextcord.SlashOption(name="title", required=True),
    anime: str = nextcord.SlashOption(name="anime", required=True),
    score: int = nextcord.SlashOption(name="score", description="Score from 1 to 10", required=True),
    content: str = nextcord.SlashOption(name="content", required=True),
    url: Optional[str] = nextcord.SlashOption(name="url", required=False)
):
    if not 1 <= score <= 10:
        await interaction.response.send_message("Score must be between 1 and 10.", ephemeral=True)
        return
    author = interaction.user.nick or interaction.user.name
    entry = reviews.create(title=title, anime=anime, score=score, content=content,
                           author=author, date=datetime.date.today(), url=url)
    await interaction.response.send_message(f"Monthly pick `{entry.anime}` created with ID `{entry.id}`.")


@bot.slash_command(guild_ids=[1342913889544962090])
async def all_reviews(interaction: nextcord.Interaction):
    entries = reviews.select().order_by(reviews.date.desc())
    lines = [f"(ID) {entry.id}. {entry.anime}: {entry.title} ({entry.score}/10) by {entry.author}"
             for entry in entries]
    await interaction.response.send_message("\n".join(lines) or "No reviews found.")


@bot.slash_command(guild_ids=[1342913889544962090])
async def delete_review(
    interaction: nextcord.Interaction,
    review_id: int = nextcord.SlashOption(name="id", required=True)
):
    deleted = reviews.delete().where(reviews.id == review_id).execute()
    message = f"Review `{review_id}` deleted." if deleted else "Review not found."
    await interaction.response.send_message(message, ephemeral=not bool(deleted))


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
