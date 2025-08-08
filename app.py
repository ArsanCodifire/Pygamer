import discord
import os
import discord as ds
from discord import app_commands
from discord import utils
import asyncio, random
from economy import update, delete, get_coin, insert
from datetime import datetime

# Load the bot token
token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
embed_color = discord.Color.blue()
afk_id = 1291043234293743646
chnl=1307265337158402059
allow=0

# Define a single class for Tic-Tac-Toe game
class TicTacToeView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'

        # Add buttons dynamically
        for i in range(9):
            self.add_item(
                discord.ui.Button(
                    style=discord.ButtonStyle.secondary, label='-', row=i // 3, custom_id=str(i)
                )
            )

    async def interaction_check(self, interaction: discord.Interaction):
        position = int(interaction.data['custom_id'])
        if self.board[position] != ' ':
            await interaction.response.send_message("This spot is already taken!", ephemeral=True)
            return False

        # Update board and button label
        self.board[position] = self.current_player
        button = [btn for btn in self.children if btn.custom_id == str(position)][0]
        button.label = self.current_player
        button.style = (
            discord.ButtonStyle.success if self.current_player == 'X' else discord.ButtonStyle.danger
        )
        button.disabled = True
        await interaction.response.edit_message(view=self)

        # Check for a winner or draw
        if await self.check_winner(interaction):
            return False

        # Switch turns
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    async def check_winner(self, interaction):
        win_combinations = [
            (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Horizontal
            (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Vertical
            (0, 4, 8), (2, 4, 6),             # Diagonal
        ]
        for combo in win_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                await interaction.followup.send(f"Player {self.current_player} wins!")
                self.stop()
                return True
        if ' ' not in self.board:
            await interaction.followup.send("It's a draw!")
            self.stop()
            return True
        return False


# Define a view for game selection
class GameSelectionView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Tic-Tac-Toe", style=discord.ButtonStyle.grey, custom_id="tic_tac_toe"))
    # Handle game selection based on button press
    async def interaction_check(self, interaction: discord.Interaction):
        custom_id = interaction.data.get("custom_id")
        allow=0
        if custom_id == "tic_tac_toe":
            await interaction.response.send_message("Starting Tic-Tac-Toe!", view=TicTacToeView())
        elif custom_id == "guess_it":
            await interaction.response.send_message("Starting Guess it!", view=GuessItView())
        elif custom_id == "wordle":
            if allow==0:
                user_id=interaction.user.id
                guild = utils.get(client.guilds)
                role, mem = utils.get(guild.roles, id=1311315719044202516), guild.get_member(user_id)
                await mem.add_roles(role)
                allow=1
                await interaction.response.send_message("Play wordle at <#1307265337158402059> !!")
            else:
                await interaction.response.send_message("You can't play now! 😭") 
        return True

# Helper function to calculate the delay
def calculate_delay(time: str, day: str):
    now = datetime.now()
    target_day = datetime.strptime(day, "%Y-%m-%d")
    target_time = datetime.strptime(time, "%H:%M")
    target_datetime = target_day.replace(hour=target_time.hour, minute=target_time.minute)

    if target_datetime < now:
        raise ValueError("The specified time is in the past!")
    return (target_datetime - now).total_seconds()
                
# /announcement command
@tree.command(name="announcement", description="Schedule an announcement")
async def announcement(interaction: discord.Interaction, details: str, time: str, day: str):
    try:
        delay = calculate_delay(time, day)
    except ValueError as e:
        await interaction.response.send_message(f"Error: {e}")

    embed = discord.Embed(title="📢 Announcement Scheduled", description=f"**Details:** {details}\n**Time:** {time}\n**Day:** {day}", color=embed_color)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    await asyncio.sleep(delay)
    
    announcement_embed = discord.Embed(title="📢 Announcement", description=f"**Details:** {details}\n**Time:** {time}\n**Day:** {day}", color=embed_color)
    await interaction.channel.send(embed=announcement_embed)

# /custom_status command
@tree.command(name="custom_status", description="Set a custom status")
async def custom_status(interaction: discord.Interaction, status: str):
    await client.change_presence(activity=discord.Game(name=f"Pygamer.game.{status}"))
    embed = discord.Embed(title="Custom Status Set", description=f"Status set to: {status}", color=embed_color)
    await interaction.response.send_message(embed=embed)

# /secret_dm command
@tree.command(name="secret_dm", description="Send a secret DM to a user")
async def secret_dm(interaction: discord.Interaction, msg: str, user: discord.User):
    embed = discord.Embed(title="Secret Message", description=msg, color=embed_color)
    await user.send(embed=embed)

    confirmation_embed = discord.Embed(title="Secret DM Sent", description=f"Secret DM sent to {user.display_name}", color=embed_color)
    await interaction.response.send_message(embed=confirmation_embed, ephemeral=True)

# /spam command
@tree.command(name="spam", description="Spam a user with messages")
async def spam(interaction: discord.Interaction, user: discord.User, times: int, msg: str):
    if times > 100:
        error_embed = discord.Embed(title="Error", description="Limit exceeded! Max allowed is 100.", color=embed_color)
        await interaction.response.send_message(embed=error_embed)
    else:
        confirmation_embed = discord.Embed(title="Spamming", description=f"Spamming {user.display_name} {times} times!", color=embed_color)
        await interaction.response.send_message(embed=confirmation_embed,ephemeral=True)
        
        for _ in range(times):
            spam_embed = discord.Embed(title="Spam", description=msg, color=embed_color)
            await user.send(embed=spam_embed)
            await asyncio.sleep(1)  # Delay between messages to prevent rate limiting

# /play_game command
@tree.command(name="play_game", description="Select a game to play!")
async def play_game(interaction: discord.Interaction):
    await interaction.response.send_message("Choose a game to play:", view=GameSelectionView())

@tree.command(name="afk", description="Be afk!")
async def afk(interaction: discord.Interaction):
    user_id, guild=interaction.user.id, utils.get(client.guilds)
    role, mem = utils.get(guild.roles, id=afk_id), guild.get_member(user_id)
    await mem.add_roles(role)
    await interaction.response.send_message(f"{interaction.user.mention} is currently AFK!")

@tree.command(name="account", description="Check your account..")
async def account(interaction: discord.Interaction):
    user, id=interaction.user, interaction.user.id
    coin,sts=get_coin(id)
    user_data = {
        "username": user.name,
        "pycoin": coin
        }
    emb=ds.Embed(title=user_data["username"], description=f"No of Pycoins: <:pycoin:1309160887587831949>{user_data["pycoin"]} pycoins", color=embed_color)
    if sts=="acc":
        await interaction.response.send_message(embed=emb)
    else:
        await interaction.response.send_message(sts)

@tree.command(name="beg", description="Beg for Pycoin.")
async def beg(interaction: discord.Interaction):
    user_id, coin=interaction.user.id, 10
    ans=update(user_id,coin,"mid")
    if ans=="acc":
        await interaction.response.send_message(f"{interaction.user.mention} begged for <:pycoin:1309160887587831949> {coin} coins")
    else:
        await interaction. response.send_message(ans)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=discord.Game(name="Pygame.game.run"))
    print(f'Logged in as {client.user}')

client.run(token)
