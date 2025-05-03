from dataclasses import dataclass

@dataclass
class NrdbInfo:
  name: str
  id: int

@dataclass
class Card:
  title: str
  card_id: str

@dataclass
class Printing:
  card_id: str
  img_id: int
  set_id: str

@dataclass
class CardSet:
  set_id: str
  release_date: str
