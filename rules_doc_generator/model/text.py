from dataclasses import dataclass
from typing import Union

import re

@dataclass
class RefInfo:
  reference: str
  type: str
  text: str
  id: str

RefDict = dict[str, RefInfo]

@dataclass
class Image:
  text: str

  def to_html(self, id_map: RefDict) -> str:
    return f'<img class="Symbol" src="{self.text}.svg" alt="{self.text}"/>'

  def to_latex(self, id_map: RefDict) -> str:
    return self.text

@dataclass
class Text:
  text: str

  def to_html(self, id_map: RefDict) -> str:
    return self.text

  def to_latex(self, id_map: RefDict) -> str:
    return re.sub(r'\"(.*?)\"', r"``\1''", self.text)

@dataclass
class Ref:
  referenced_id: str
  capitalize: bool

  def to_html(self, id_map: RefDict) -> str:
    if not self.referenced_id in id_map:
      raise Exception(f'id does not exist: {self.referenced_id}')
    ref_info = id_map[self.referenced_id]
    return f'<a href=#{ref_info.reference}>{ref_info.type} {ref_info.reference}</a>'

  def to_latex(self, id_map: RefDict) -> str:
    if not self.referenced_id in id_map:
      raise Exception(f'id does not exist: {self.referenced_id}')
    ref_info = id_map[self.referenced_id]
    ref_text = ref_info.type
    if self.capitalize:
      ref_text = ref_text.capitalize()
    return f'\\reful{{{ref_info.id}}}{{{ref_text} {ref_info.reference}}}'

@dataclass
class Term:
  text: str

  def to_html(self, id_map: RefDict) -> str:
    return f'<span class="Term">{self.text}</span>'

  def to_latex(self, id_map: RefDict) -> str:
    return f'\\textsc{{{self.text}}}'

TextElement = Union[Text, Ref, Term, Image]

@dataclass
class FormatText:
  textElements: list[TextElement]

  def to_plaintext(self) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_plaintext(id_map)
    return result

  def to_html(self, id_map: RefDict) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_html(id_map)
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_latex(id_map)
    return result

@dataclass
class Example:
  text: FormatText

  def to_html(self, id_map: RefDict) -> str:
    return f'Example: {self.text.to_html(id_map)}'

  def to_latex(self, id_map: RefDict) -> str:
    return f'\emph{{Example: {self.text.to_latex(id_map)}}}'
