import discord
from discord.ext import commands
import sqlite3
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===================== DATABASE =====================
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS recensement (
    user_id TEXT PRIMARY KEY,
    pseudo TEXT,
    principal TEXT,
    mules TEXT,
    actif TEXT
)
""")
conn.commit()

# ===================== FORMULAIRE =====================
class RecensementModal(discord.ui.Modal, title="Recensement Guilde"):

    principal = discord.ui.TextInput(label="Personnage principal")
    mules = discord.ui.TextInput(label="Mules (optionnel)", required=False)
    actif = discord.ui.TextInput(label="Actif ? (oui/non)")

    async def on_submit(self, interaction: discord.Interaction):

        cursor.execute("""
        INSERT OR REPLACE INTO recensement VALUES (?, ?, ?, ?, ?)
        """, (
            str(interaction.user.id),
            str(interaction.user),
            self.principal.value,
            self.mules.value,
            self.actif.value
        ))

        conn.commit()

        await interaction.response.send_message(
            "✅ Recensement enregistré !",
            ephemeral=True
        )

# ===================== BOUTON =====================
class RecensementView(discord.ui.View):

    @discord.ui.button(label="📋 Se recenser", style=discord.ButtonStyle.green)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RecensementModal())

# ===================== COMMANDES =====================
@bot.command()
async def recensement(ctx):
    await ctx.send(
        "📋 **Recensement de la guilde**\nClique sur le bouton :",
        view=RecensementView()
    )

@bot.command()
async def profil(ctx, member: discord.Member = None):
    member = member or ctx.author

    cursor.execute("SELECT * FROM recensement WHERE user_id = ?", (str(member.id),))
    data = cursor.fetchone()

    if not data:
        await ctx.send("❌ Aucun recensement trouvé.")
        return

    await ctx.send(f"""
📊 **Profil de {member.name}**

👤 Principal : {data[2]}
👥 Mules : {data[3]}
⚡ Actif : {data[4]}
""")

@bot.command()
async def stats(ctx):
    cursor.execute("SELECT COUNT(*) FROM recensement")
    total = cursor.fetchone()[0]

    await ctx.send(f"📊 Membres recensés : {total}")

# ===================== START =====================
@bot.event
async def on_ready():
    print(f"{bot.user} est connecté !")

bot.run(TOKEN)
