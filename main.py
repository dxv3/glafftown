import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CloseButton(Button):
    def __init__(self, channel):
        super().__init__(label="Close", style=discord.ButtonStyle.danger, custom_id=f"close_{channel.id}")
        self.channel = channel

    async def callback(self, interaction: discord.Interaction):
        if interaction.user in self.channel.members:
            transcript_channel_id = 1267786315798417471  # Replace with your desired channel ID
            transcript_channel = interaction.guild.get_channel(transcript_channel_id)
            messages = []
            
            async for message in self.channel.history(limit=None, oldest_first=True):
                messages.append(message)
            
            transcript = f"Transcript of {self.channel.name}:\n"
            for message in messages:
                transcript += f"{message.author.display_name}: {message.content}\n"
            
            # Sending the transcript to the designated channel
            await transcript_channel.send(f"Transcript of {self.channel.mention}:\n```{transcript}```")
            
            await self.channel.delete()
        else:
            await interaction.response.send_message("You do not have permission to close this ticket.", ephemeral=True)


class TicketView(View):
    def __init__(self, channel):
        super().__init__(timeout=None)
        self.add_item(CloseButton(channel))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)

    # Set streaming presence
    streaming = discord.Streaming(name="GlaffTown", url="https://www.twitch.tv/kamidrills")
    await bot.change_presence(activity=streaming)

    # Send a message to a specific channel when the bot is up
    channel_id = 1267194755155099648  # Replace with your desired channel ID
    channel = bot.get_channel(channel_id)
    if channel:
        await channel.send("bot online")

    # Set streaming presence
    streaming = discord.Streaming(name="GlaffTown", url="https://www.twitch.tv/kamidrills")
    await bot.change_presence(activity=streaming)

@bot.event
async def on_command(ctx):
    # Log command usage
    print(f"Command {ctx.command} invoked by {ctx.author} in {ctx.guild}/{ctx.channel}")

@bot.event
async def on_message(message):
    if message.channel.name.startswith('｜apply'):
        if not message.content.startswith('/apply'):
            await message.delete()
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    # Log command errors and notify the user to DM @dxv3
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.")
    else:
        error_message = (f"Command {ctx.command} invoked by {ctx.author} failed: {error}\n"
                         f"Please DM @dxv3 for assistance.")
        await ctx.send(f"An error occurred. Please DM @dxv3 for assistance.")
        print(error_message)

@bot.tree.command(name="refresh_commands")
@commands.is_owner()
async def refresh_commands(interaction: discord.Interaction):
    await bot.tree.sync()
    await interaction.response.send_message("Commands refreshed.")

@bot.event
async def on_member_join(member):
    role_id = 1267649808911437874  # Replace with your role ID
    role = member.guild.get_role(role_id)
    if role:
        await member.add_roles(role)
        print(f"Assigned {role.name} to {member.name}")

    welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if welcome_channel:
        await welcome_channel.send(f"Welcome {member.mention}!")

@bot.tree.command(name="dmall", description="Send a DM to all server members")
async def slash_dmall(interaction: discord.Interaction, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    guild = interaction.guild
    for member in guild.members:
        if not member.bot:
            try:
                await member.send(message)
            except:
                pass
    await interaction.response.send_message("Message sent to all members.")


@bot.command(name="dmall")
@commands.has_permissions(administrator=True)
async def prefix_dmall(ctx, *, message: str):
    guild = ctx.guild
    for member in guild.members:
        if not member.bot:
            try:
                await member.send(message)
            except:
                pass
    await ctx.send("Message sent to all members.")

@bot.command(name="embed", description="Create a custom embed")
async def slash_embed(interaction: discord.Interaction, title: str, description: str, color: str = "000000"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    
    color = int(color.lstrip('#'), 16)
    embed = discord.Embed(title=title, description=description, color=color)
    await interaction.channel.send(embed=embed)
    await interaction.response.send_message("Embed created successfully.", ephemeral=True)


@bot.tree.command(name="lockdown", description="Lock down all channels in the server")
async def slash_lockdown(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    
    guild = interaction.guild
    role = guild.default_role
    for channel in guild.channels:
        try:
            await channel.set_permissions(role, send_messages=False)
        except Exception as e:
            await interaction.response.send_message(f"Failed to lock down {channel.name}: {str(e)}", ephemeral=True)
    
    await interaction.response.send_message("All channels have been locked down.", ephemeral=True)

@bot.tree.command(name="unlockdown", description="Unlock all channels in the server")
async def slash_unlockdown(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    
    guild = interaction.guild
    role = guild.default_role
    for channel in guild.channels:
        try:
            await channel.set_permissions(role, send_messages=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to unlock {channel.name}: {str(e)}", ephemeral=True)
    
    await interaction.response.send_message("All channels have been unlocked.", ephemeral=True)

@bot.tree.command(name="purge", description="Delete a specified number of messages from the channel")
@commands.has_permissions(manage_messages=True)
async def slash_purge(interaction: discord.Interaction, number: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    deleted = await interaction.channel.purge(limit=number)
    await interaction.response.send_message(f"Deleted {len(deleted)} messages.", ephemeral=True)

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def prefix_purge(ctx, number: int):
    if not ctx.author.guild_permissions.manage_messages:
        await ctx.send("You do not have permission to use this command.")
        return

    deleted = await ctx.channel.purge(limit=number)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)

@bot.tree.command(name="apply", description="Create a private channel with an application form")
@commands.cooldown(1, 3, commands.BucketType.user)
async def slash_apply(interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user

    # Check if the user already has a ticket open
    if discord.utils.get(guild.channels, name=f"ticket-{user.name}"):
        await interaction.response.send_message("You already have an open ticket.", ephemeral=True)
        return

    # Define the channel permissions
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True)
    }

    # Get the category by ID
    category = discord.utils.get(guild.categories, id=1267645661902409740)
    if not category:
        await interaction.response.send_message("Category not found.", ephemeral=True)
        return

    # Create the channel in the specified category with the user's username and ID
    channel = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites, category=category)

    # Create the embed message and close button
    embed = discord.Embed(title="Application Form", 
                          description="""Please fill out the form below:
1. What is your IGN?
2. How old are you?
3. What timezone are you in?
4. What roles can you play?
5. PFs?
6. POVs?
7. How many hours can you play per day?
8. Are you able to record in 1080p 60fps?
9. Do you have a good microphone?
""")
    embed.set_footer(text="more to be added soon")
    view = TicketView(channel)

    # Send the embed message and button in the channel
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Ticket created: {channel.mention}", ephemeral=True)


@bot.command(name="apply")
@commands.cooldown(1, 3, commands.BucketType.user)
async def prefix_apply(ctx):
    guild = ctx.guild
    user = ctx.author

    # Check if the user already has a ticket open
    if discord.utils.get(guild.channels, name=f"ticket-{user.name}"):
        await ctx.send("You already have an open ticket.")
        return

    # Define the channel permissions
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True)
    }

    # Get the category by ID
    category = discord.utils.get(guild.categories, id=1267645661902409740)
    if not category:
        await ctx.send("Category not found.")
        return

    # Create the channel in the specified category with the user's username and ID
    channel = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites, category=category)

    # Create the embed message and close button
    embed = discord.Embed(title="Application Form", 
                          description="""Please fill out the form below:
1. What is your IGN?
2. How old are you?
3. What timezone are you in?
4. What roles can you play?
5. PFs?
6. POVs?
7. How many hours can you play per day?
8. Are you able to record in 1080p 60fps?
9. Do you have a good microphone?
""")
    embed.set_footer(text="You will be need to 1v1 someone, if you quickdrop or get 7+ potted, you will be **REJECTED**")
    view = TicketView(channel)

    # Send the embed message and button in the channel
    await channel.send(embed=embed, view=view)
    await ctx.send(f"Ticket created: {channel.mention}")

bot.run("token")

