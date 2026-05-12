from dataclasses import dataclass

@dataclass
class RefInfo:
  reference: str
  type: str
  text: str
  id: str
  toc: bool

RefDict = dict[str, RefInfo]

def ref_info_depth(ref_info: RefInfo) -> int:
  return ref_info.reference.count('.') + 1

@dataclass
class ModelData:
  id_map: RefDict
  nrdb_info: dict[str, int]