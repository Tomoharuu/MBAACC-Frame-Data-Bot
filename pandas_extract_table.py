import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_numpad(string):
	p = re.compile('^(j.)?([1-9]+)')
	m = p.match(string)
	if m:
		return m.group(0)
	return None

#characters = ["Akiha Tohno", "Aoko Aozaki", "Arcueid Brunestud", "Ciel", "Archetype: Earth", "Hisui", "Koha & Mech", "Kohaku", "Kouma Kishima", "Len", "Mech-Hisui", "Miyako Arima", "Neco-Arc Chaos", "Shiki Nanaya", "Hisui & Kohaku", "Neco-Arc", "Neco & Mech", "Nero Chaos", "Powered Ciel", "Red Arcueid", "Riesbyfe Stridberg", "Roa", "Shiki Ryougi", "Satsuki Yumizuka", "Akiha Tohno (Seifuku)", "Sion Eltnam Atlasia", "Shiki Tohno", "Akiha Vermilion", "Sion TATARI", "Warachia", "White Len"]
#moons = ["Full_Moon", "Half_Moon", "Crescent_Moon"]
characters = ["Akiha Tohno"]
moons = ["Full_Moon"]

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

			#p = re.compile('^(.+?)(\\(EX: (.+?)\\))?$')
			#m = p.match(base_move_name)
			#if m:
			#	print("A/B =", m.group(1))
			#	print("C   =", m.group(3))

			#print()

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

				# Moves with variants
				if variant_cell:
					variant_name = variant_cell.get_text(" ", strip=True)
					if variant_name == "EX":
						variant_name = "C"
					
					# ignoring system mechanics, they will just be referred to
					# by their names instead of input notation.
					if (
						("Shield Counter" != base_move_name)
						and ("Shield Bunker" != base_move_name)
						and ("Heat" != base_move_name)
						and ("Blood Heat" != base_move_name)
						and ("Circuit Spark" != base_move_name)
						and ("Ground Throw" != base_move_name)
						and ("Air Throw" != base_move_name)
					):
						small = table.find("small")
						smalltext = small.get_text(strip=True)
						#print("small = ", small)
						#print("variant_name = ", variant_name)
						notation = extract_numpad(smalltext) + variant_name
						#print("notation = ", notation)

						#move_name = f"{notation} - {base_move_name}"
						move_name = f"{notation}"

						# quick fix for AD, AAD and Last Arc
						if "41236" in smalltext:
							move_name = "Arc Drive"

							if "Blood Heat" in smalltext:
								move_name = "Another Arc Drive"
						
						if "EX Shield during Blood Heat" in smalltext:
							move_name = "Last Arc"

						if "A+B+C during" in smalltext:
							move_name = "Heat Activation"
						#print("move_name =", move_name)
						#print()

					else:
						move_name = f"{base_move_name} ({variant_name})"

					current_move = {
						"Character": character,
						"Moon": moon,
						"Move": move_name,
						"Image": image_url,			  # NOVO
						"TotalFrames": total_frames	  # NOVO
					}

					all_moves.append(current_move)

				# Moves without variants
				elif current_move is None:
					#print(base_move_name)

					# Checking for specials that have no variants
					small = table.find("small")
					move_name = base_move_name
					if small:
						smalltext = small.get_text(strip=True)
						#print(smalltext)

						notation = extract_numpad(smalltext)

						if (
							("Ground Throw" != base_move_name)
							and ("Air Throw" != base_move_name)
						):
							move_name = f"{smalltext} - {base_move_name}"
							if notation:
								move_name = f"{notation}X"

						# quick fix for AD, AAD and Last Arc
						if "41236" in smalltext:
							if "Blood Heat" in smalltext:
								#print("IS AAD")
								move_name = "Another Arc Drive"
							else:
								#print("IS AD")
								move_name = "Arc Drive"

						if "EX Shield during Blood Heat" in smalltext:
							#print("IS LAST ARC")
							move_name = "Last Arc"

						if "A+B+C during" in smalltext:
							move_name = "Heat Activation"

					#print("move_name =", move_name)
					#print()

					current_move = {
						"Character": character,
						"Moon": moon,
						"Move": move_name,
						#"Move": base_move_name,
						"Image": image_url,			  # NOVO
						"TotalFrames": total_frames	  # NOVO
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
final_df.to_csv("all_characters_new.csv", index=False)

#print(final_df)
