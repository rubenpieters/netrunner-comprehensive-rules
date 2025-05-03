import os
import json
from pathlib import Path
from functools import reduce
from datetime import datetime

from rules_doc_generator.model.nrdb_info import (Card, Printing, CardSet)

def read_sets(folder_path: Path) -> dict[str, CardSet]:
  sets = {}

  if not os.path.isdir(folder_path):
    raise ValueError(f"The folder '{folder_path}' does not exist.")

  file_path = Path(folder_path, Path("card_sets.json"))
  with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    for set_json in data:
      set_id = set_json["id"]
      release_date = set_json["date_release"]
      set = CardSet(set_id, release_date)
      sets[set_id] = set
  return sets

def read_cards(folder_path: Path) -> dict[str, Card]:
  cards = {}

  if not os.path.isdir(folder_path):
    raise ValueError(f"The folder '{folder_path}' does not exist.")

  for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
      file_path = os.path.join(folder_path, filename)
      with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        title = data["title"]
        card_id = data["id"]
        card = Card(title, card_id)
        cards[card_id] = card
  return cards

def read_printings(folder_path: Path) -> dict[str, list[Printing]]:
  printings = {}

  if not os.path.isdir(folder_path):
    raise ValueError(f"The folder '{folder_path}' does not exist.")

  for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
      file_path = os.path.join(folder_path, filename)
      with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for printing_json in data:
          img_id = printing_json["id"]
          card_id = printing_json["card_id"]
          set_id = printing_json["card_set_id"]
          printing = Printing(card_id, img_id, set_id)
          # Ignore sets that aren't physical printings
          if set_id != 'salvaged_memories' and set_id != 'system_core_2019':
            if card_id in printings:
              printings[card_id].append(printing)
            else:
              printings[card_id] = [printing]
  return printings

def generate_nrdb_info(base_path_str: str):
  base_path = Path(base_path_str, Path("v2"))
  cards_path = Path(base_path, Path("cards"))
  printings_path = Path(base_path, Path("printings"))
  card_sets = read_sets(base_path)
  cards = read_cards(cards_path)
  printings = read_printings(printings_path)

  content = "# GENERATED, DO NOT EDIT\n"
  for card_id in cards:
    card = cards[card_id]
    card_printings = printings[card.card_id]
    if len(card_printings) == 1:
      # If there's only 1 printing, pick that one.
      printing = card_printings[0]
    else:
      # Look for the last printing if there's multiple.
      id_with_date = list(map(lambda x: {'img_id': x.img_id, 'set_id': card_sets[x.set_id].set_id, 'date': datetime.strptime(card_sets[x.set_id].release_date, "%Y-%m-%d")}, card_printings))
      last_printing = reduce(lambda latest, other: other if other["date"] > latest["date"] else latest, id_with_date[1:], id_with_date[0])
      printing = Printing(card_id, last_printing["img_id"], last_printing["set_id"])
    img_id = printing.img_id
    # Sanitize quotes from the title.
    sanitized_title = card.title.replace("’", "'").replace("“", "\"").replace("”", "\"").replace("\"", "\\\"")
    content += f'\"{sanitized_title}\": \"{img_id}\"\n'
    # Allow to reference IDs without their subtitle
    if ':' in card.title:
      split_title = sanitized_title.split(':')[0]
      content += f'\"{split_title}\": \"{img_id}\"\n'

  # Generate folder if it doesn't exist.
  generated_yaml_folder = os.path.join("generated", "nrdb")
  os.makedirs(generated_yaml_folder, exist_ok=True)
  
  # Write content to file.
  with open(os.path.join(generated_yaml_folder, "nrdb.yaml"), 'w') as file:
    file.write(content)
