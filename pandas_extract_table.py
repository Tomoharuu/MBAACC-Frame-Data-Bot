import requests
from bs4 import BeautifulSoup
import pandas as pd

characters = ["Kohaku", "Len", "Warachia"]
characters = ["Akiha Tohno", "Aoko Aozaki", "Arcueid Brunestud", "Ciel", "Archetype: Earth", "Hisui", "Koha & Mech", "Kohaku", "Kouma Kishima", "Len", "Mech-Hisui", "Miyako Arima", "Neco-Arc Chaos", "Shiki Nanaya", "Hisui & Kohaku", "Neco-Arc", "Neco & Mech", "Nero Chaos", "Powered Ciel", "Red Arcueid", "Riesbyfe Stridberg", "Roa", "Shiki Ryougi", "Satsuki Yumizuka", "Akiha Tohno (Seifuku)", "Sion Eltnam Atlasia", "Shiki Tohno", "Akiha Vermilion", "Sion TATARI", "Warachia", "White Len"]
moons = ["Full_Moon", "Half_Moon", "Crescent_Moon"]

all_dataframes = []

for character in characters:
    for moon in moons:

        URL = f"https://mizuumi.wiki/w/Melty_Blood/MBAACC/{character.replace(" ", "_")}/{moon}"
        print(URL)
        html = requests.get(URL).text
        soup = BeautifulSoup(html, "lxml")

        tables = soup.select("table.wikitable")
        all_moves = []

        for table in tables:
            big = table.find("big")
            if not big:
                continue

            base_move_name = big.get_text(strip=True)

            # NOVO: pega imagem
            img_tag = table.find("img")
            image_url = None

            if img_tag and img_tag.get("src"):
                image_url = "https://wiki.gbl.gg" + img_tag["src"]

            # NOVO: pega total de frames
            total_span = table.find("span", class_="frame-data-total-value")
            total_frames = None

            if total_span:
                total_frames = total_span.get_text(strip=True)

            rows = table.find_all("tr")
            current_move = None

            for i in range(len(rows) - 1):
                row = rows[i]
                variant_cell = row.find("th", rowspan=True)

                if variant_cell:
                    variant_name = variant_cell.get_text(" ", strip=True)

                    current_move = {
                        "Character": character,
                        "Moon": moon,
                        "Move": f"{base_move_name} ({variant_name})",
                        "Image": image_url,              # NOVO
                        "TotalFrames": total_frames      # NOVO
                    }

                    all_moves.append(current_move)

                elif current_move is None:
                    current_move = {
                        "Character": character,
                        "Moon": moon,
                        "Move": base_move_name,
                        "Image": image_url,              # NOVO
                        "TotalFrames": total_frames      # NOVO
                    }

                    all_moves.append(current_move)

                headers = row.find_all("th")
                values = rows[i + 1].find_all("td")

                if variant_cell and headers:
                    headers = headers[1:]

                if headers and values and len(headers) == len(values):
                    for h, v in zip(headers, values):
                        header = h.get_text(" ", strip=True)
                        value = v.get_text(" ", strip=True)
                        current_move[header] = value

                p = row.find("p")
                if p:
                    current_move["Description"] = p.get_text(" ", strip=True)

        df = pd.DataFrame(all_moves)

        if not df.empty:
            df = df.dropna(subset=["Damage"])

            if "Description" in df.columns:
                df = df.drop(columns=["Description"])

            all_dataframes.append(df)


final_df = pd.concat(all_dataframes, ignore_index=True)



final_df["Character"] = final_df["Character"].str.replace("Archetype: Earth", "Hime").str.replace("Koha & Mech", "Koha-Mech").str.replace("Neco-Arc Chaos", "NAC").str.replace("Shiki ", "").str.replace("Hisui & Kohaku", "Maids").str.replace("Neco & Mech", "Neco-Mech").str.replace("Powered Ciel", "P.Ciel").str.replace("Red Arcueid", "Warc").str.replace("Riesbyfe Stridberg", "Ries").str.replace("Akiha Tohno (Seifuku)", "Seifuku").str.replace("Akiha Vermilion", "V.Akiha").str.replace("Sion TATARI", "V.Sion").str.replace("Warachia", "Wara").str.replace("White Len", "WLen")

final_df["Character"] = final_df["Character"].str.split(" ").str[0]

final_df["CharMoon"] = (
    final_df["Moon"].str[0] + "-" + final_df["Character"].str.split(" ").str[0]
)

final_df["Image2"] = ""

final_df = final_df[
    [
        'Character',
        'Moon',
        'CharMoon',
        'Move',
        'Damage',
        'Red Damage',
        'Proration',
        'Cancel',
        'Guard',
        'First Active',
        'Active',
        'Recovery',
        'Frame Adv',
        'TotalFrames',
        'Circuit',
        'Image',
        'Image2'
    ]
]

final_df["Image"] = final_df["Image"].str.replace("https://wiki.gbl.gg/images/thumb", "https://mizuumi.wiki/images")
final_df["Image"] = final_df["Image"].str.split(".png").str[0] + ".png"
final_df.to_csv("all_characters.csv", index=False)

print(final_df.head(20))