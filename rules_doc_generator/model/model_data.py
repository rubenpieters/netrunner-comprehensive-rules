from dataclasses import dataclass

@dataclass
class RefInfo:
  reference: str
  type: str
  text: str
  id: str
  toc: bool

RefDict = dict[str, RefInfo]

@dataclass
class ModelData:
  id_map: RefDict
  nrdb_info: dict[str, int]