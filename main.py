import discord
from discord import ui
from discord.ext import commands
from discord import app_commands
import pandas as pd

with open('bot_token.txt', 'r', encoding='utf-8') as f:
    token = f.read()

df = pd.read_csv("https://raw.githubusercontent.com/Tomoharuu/MBAACC-Frame-Data-Bot/refs/heads/main/all_characters.csv")
intents = discord.Intents.all()

bot = commands.Bot(".", intents=intents)

@bot.event 
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user}!")

personagens = df['CharMoon'].unique().tolist()

banners = {"Akiha": "https://mizuumi.wiki/images/e/ec/Akihabanner.png",
"Aoko": "https://mizuumi.wiki/images/d/d3/Aokobanner.png",
"Arcueid": "https://mizuumi.wiki/images/1/1a/Arcueidbanner.png",
"Ciel": "https://mizuumi.wiki/images/6/6d/Cielbanner.png",
"Hime": "https://mizuumi.wiki/images/0/0b/Archetypebanner.png",
"Hisui": "https://mizuumi.wiki/images/d/dc/Hisuibanner.png",
"Koha-Mech": "https://mizuumi.wiki/images/e/e2/Kohamechbanner.png",
"Kohaku": "https://mizuumi.wiki/images/1/14/Kohakubanner.png",
"Kouma": "https://mizuumi.wiki/images/5/55/Koumabanner.png",
"Len": "https://mizuumi.wiki/images/1/1b/Lenbanner.png",
"Mech-Hisui": "https://mizuumi.wiki/images/8/80/Mechbanner.png",
"Miyako": "https://mizuumi.wiki/images/1/1f/Miyakobanner.png",
"NAC": "https://mizuumi.wiki/images/1/1d/NerChaosbanner.png",
"Nanaya": "https://mizuumi.wiki/images/6/6c/Nanayabanner.png",
"Maids": "https://mizuumi.wiki/images/2/25/HisuKohabanner.png",
"Neco-Arc": "https://mizuumi.wiki/images/3/37/Necobanner.png",
"Neco-Mech": "https://mizuumi.wiki/images/5/56/Necomechbanner.png",
"Nero": "https://mizuumi.wiki/images/1/1a/Nerobanner.png",
"P.Ciel": "https://mizuumi.wiki/images/f/ff/PCielbanner4.png",
"Ries": "https://mizuumi.wiki/images/2/2a/Riesbanner.png",
"Roa": "https://mizuumi.wiki/images/a/a0/Roabanner.png",
"Ryougi": "https://mizuumi.wiki/images/a/ad/Ryougibanner.png",
"Satsuki": "https://mizuumi.wiki/images/b/b4/Satsukibanner.png",
"Seifuku": "https://mizuumi.wiki/images/b/b8/Seifukubanner.png",
"Sion": "https://mizuumi.wiki/images/9/9a/Sionbanner.png",
"Tohno": "https://mizuumi.wiki/images/2/22/Tohnobanner.png",
"V.Akiha": "https://mizuumi.wiki/images/7/76/Vakihabanner.png",
"V.Sion": "https://mizuumi.wiki/images/c/c6/Vsionbanner.png",
"Wara": "https://mizuumi.wiki/images/2/2c/Warakiabanner.png",
"Warc": "https://mizuumi.wiki/images/2/27/Warcbanner.png",
"WLen": "https://mizuumi.wiki/images/7/74/Wlenbanner.png"}


@bot.tree.command()
async def framedata(interact:discord.Interaction, char:str, move:str):
    view = MoveDisplay(char, move)
    await interact.response.send_message(view=view)

@framedata.autocomplete('char')
async def char_autocomplete(interact:discord.Interaction, pesquisa:str):
    opcoes =[]
    for char in personagens:
        if pesquisa.upper() in char.upper():
            char_option = app_commands.Choice(name=char, value=char)
            opcoes.append(char_option)
    return opcoes[:25]

@framedata.autocomplete('move')
async def move_autocomplete(interact:discord.Interaction, pesquisa:str):
    personagem_escolhido = interact.namespace.char
    filtro = df["CharMoon"] == personagem_escolhido
    df_filtrado = df[filtro]
    moves = df_filtrado["Move"].tolist()
    opcoes =[]
    for move in moves:
        if pesquisa.upper() in move.upper():
            move_option = app_commands.Choice(name=move, value=move)
            opcoes.append(move_option)
    return opcoes[:25]


# Testando comando com AutoComplete
@bot.hybrid_command()
async def echo(ctx: commands.Context, color: str):
    await ctx.send(color)

@echo.autocomplete("color")
async def color_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    options = ["Red", "Green", "Blue"]
    return [app_commands.Choice(name=option, value=option) for option in options if option.lower().startswith(current.lower())][:25]



# Testando comando sem slash
def normalizar(texto):
    texto = texto.replace(".", "")

    if texto[1:-1].isdigit():
        return f"{texto[0].lower()}.{texto[1:-1]}{texto[-1].upper()}"

    if texto[:-1].isdigit():
        return f"{texto[:-1]}{texto[-1].upper()}"

    return f"{texto[0].lower()}.{texto[1].upper()}"

@bot.command()
async def framedata(ctx:commands.Context, char:str, move:str):
    view = MoveDisplay(char.title(), normalizar(move))
    await ctx.send(view=view)


class MoveDisplay(ui.LayoutView):

    def __init__(self, char: str, move: str):
        super().__init__()

        self.char = char
        self.move = move


        df_filtro = df[(df["CharMoon"] == self.char) & (df["Move"] == self.move)]
        char_name = df_filtro["Character"].values[0]
        damage = df_filtro["Damage"].values[0]
        red_damage = df_filtro["Red Damage"].values[0]
        proration = df_filtro["Proration"].values[0]
        cancel = df_filtro["Cancel"].values[0]
        guard = df_filtro["Guard"].values[0]
        first_active = df_filtro["First Active"].values[0]
        active = df_filtro["Active"].values[0]
        recovery = df_filtro["Recovery"].values[0]
        overall = int(df_filtro["TotalFrames"].values[0])
        frameadv = df_filtro["Frame Adv"].values[0]
        imagem = df_filtro["Image"].values[0]
        imagem2 = df_filtro["Image2"].values[0]

        header = discord.ui.MediaGallery["BasicMediaGalleryView"](
            discord.MediaGalleryItem(
                media=f"{banners[char_name]}"
            )
        )

        texto_intro = ui.TextDisplay(
            f"## {self.char} | {self.move}\n"
        )

        texto_general = ui.TextDisplay(
            f'''> **General Info**\n**Damage:** {damage}\n**Guard:** {guard}    **Cancel:** {cancel}\n\n> **Frame Data Info**\n**First Active:** {first_active}\n**Active:** {active}\n**Recovery:** {recovery}\n**Overall:** {overall}\n**Frame Advantage:** {frameadv}'''
        )

        texto_vazio = ui.TextDisplay(f"⠀")

        texto_frames = ui.TextDisplay(
            f'> **Frame Data Info**\n**First Active:** {first_active}\n**Active:** {active}\n**Recovery:** {recovery}\n**Overall:** {overall}'
        )

        texto_hitbox = ui.TextDisplay(f"> **Hitbox**")

        items = [
            discord.MediaGalleryItem(media=imagem)
        ]

        if pd.notna(imagem2) and str(imagem2).strip().lower() != "nan":
            items.append(
                discord.MediaGalleryItem(media=imagem2)
            )

        hitbox = discord.ui.MediaGallery["BasicMediaGalleryView"](*items)

        container = ui.Container(
            header,
            texto_intro,
            ui.Separator(),
            texto_general,
            ui.Separator(),
            texto_hitbox,
            hitbox,
            accent_color=discord.Colour.red()
        )

        self.add_item(container)


bot.run(token)