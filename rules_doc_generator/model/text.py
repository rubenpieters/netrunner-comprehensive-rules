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

def lookup_ref(id_map: RefDict, referenced_id: str):
  if not referenced_id in id_map:
    raise Exception(f'id does not exist: {referenced_id}')
  return id_map[referenced_id]

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
    return self.text

@dataclass
class Ref:
  referenced_ids: list[str]
  capitalize: bool

  def to_html(self, id_map: RefDict) -> str:
    if len(self.referenced_ids) == 1:
      referenced_id = self.referenced_ids[0]
      if not referenced_id in id_map:
        raise Exception(f'id does not exist: {referenced_id}')
      ref_info = id_map[referenced_id]
      return f'<a href=#{ref_info.reference}>{ref_info.type} {ref_info.reference}</a>'
    else:
      html_refs = list(map(lambda x: f'<a href=#{lookup_ref(id_map, x).reference}>{lookup_ref(id_map, x).reference}</a>', self.referenced_ids))
      joined = ' and '.join([', '.join(html_refs[:-1]), html_refs[-1]])
      ref_info = id_map[self.referenced_ids[0]]
      ref_text = ref_info.type
      if self.capitalize:
        ref_text = ref_text.capitalize()
      return f'{ref_text}s {joined}'

  def to_latex(self, id_map: RefDict) -> str:
    if len(self.referenced_ids) == 1:
      ref_info = lookup_ref(id_map, self.referenced_ids[0])
      ref_text = ref_info.type
      if self.capitalize:
        ref_text = ref_text.capitalize()
      return f'\\reful{{{ref_info.id}}}{{{ref_text} {ref_info.reference}}}'
    if len(self.referenced_ids) > 1:
      latex_refs = list(map(lambda x: f'\\reful{{{lookup_ref(id_map, x).id}}}{{{lookup_ref(id_map, x).reference}}}', self.referenced_ids))
      joined = ' and '.join([', '.join(latex_refs[:-1]), latex_refs[-1]])
      ref_info = id_map[self.referenced_ids[0]]
      ref_text = ref_info.type
      if self.capitalize:
        ref_text = ref_text.capitalize()
      return f'{ref_text}s {joined}'

@dataclass
class Term:
  text: str

  def to_html(self, id_map: RefDict) -> str:
    return f'<span class="Term">{self.text}</span>'

  def to_latex(self, id_map: RefDict) -> str:
    return f'\\textsc{{{self.text}}}'

@dataclass
class SubType:
  text: str

  def to_html(self, id_map: RefDict) -> str:
    return f'<span class="SubType">{self.text}</span>'

  def to_latex(self, id_map: RefDict) -> str:
    return f'\\textbf{{{self.text}}}'

@dataclass
class Card:
  text: str

  def to_html(self, id_map: RefDict) -> str:
    return f'<span class="Card">{self.text}</span>'

  def to_latex(self, id_map: RefDict) -> str:
    return f'\\textit{{{self.text}}}'

TextElement = Union[Text, Ref, Term, Image, SubType]

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
    return re.sub(r'\"(.*?)\"', r"``\1''", result)

@dataclass
class Example:
  text: FormatText

  def to_html(self, id_map: RefDict) -> str:
    return f'Example: {self.text.to_html(id_map)}'

  def to_latex(self, id_map: RefDict) -> str:
    return f'\emph{{Example: {self.text.to_latex(id_map)}}}'
