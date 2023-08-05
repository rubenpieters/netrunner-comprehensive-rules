from dataclasses import dataclass

@dataclass
class Config:
  annotated: bool

  def not_annotated(self):
    return Config(False)
