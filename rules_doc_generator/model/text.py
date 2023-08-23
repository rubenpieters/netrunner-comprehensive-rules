from dataclasses import dataclass
from typing import Callable, Union

import re

from rules_doc_generator.config import (Config)

@dataclass
class RefInfo:
  reference: str
  type: str
  text: str
  id: str
  toc: bool

RefDict = dict[str, RefInfo]

def lookup_ref(id_map: RefDict, referenced_id: str):
  if not referenced_id in id_map:
    raise Exception(f'id does not exist: {referenced_id}')
  return id_map[referenced_id]

@dataclass
class Image:
  text: str

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return f'<img class="Symbol" src="{self.text}.svg" alt="{self.text}"/>'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return f'\includegraphics[height=8pt]{{{self.text}.png}}'

@dataclass
class Text:
  text: str

  def to_plaintext(self) -> str:
    return self.text

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return self.text

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return self.text

@dataclass
class Ref:
  referenced_ids: list[str]
  capitalize: bool
  combiner: str

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return self.to_text(" ", id_map, lambda ref_id, ref_text: fr'<a href=#{ref_id}>{ref_text}</a>')

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return self.to_text("~", id_map, lambda ref_id, ref_text: fr'\reful{{{ref_id}}}{{{ref_text}}}')

  def to_text(self, spacer: str, id_map: RefDict, mk_link: Callable[[str, str], str]) -> str:
    try:
      if len(self.referenced_ids) == 1:
        ref_info = lookup_ref(id_map, self.referenced_ids[0])
        ref_text = ref_info.type
        if self.capitalize:
          ref_text = ref_text.capitalize()
        return mk_link(ref_info.id, f'{ref_text}{spacer}{ref_info.reference}')
      elif len(self.referenced_ids) > 1:
        latex_refs = list(map(lambda ref_id: mk_link(ref_id, lookup_ref(id_map, ref_id).reference), self.referenced_ids))
        joined = f' {self.combiner} '.join([', '.join(latex_refs[:-1]), latex_refs[-1]])
        ref_info = id_map[self.referenced_ids[0]]
        ref_text = ref_info.type
        if self.capitalize:
          ref_text = ref_text.capitalize()
        return f'{ref_text}s {joined}'
      else:
        raise Exception('No referenced ids')
    except Exception as e:
      if "does not exist" in str(e):
        # TODO: make this configurable with a strict option.
        # For now, emit an unknown ref string.
        unknown_ref_string = ','.join(self.referenced_ids).replace('_', '\_')
        return f"UNKNOWNREF({unknown_ref_string})"
      else:
        raise e

@dataclass
class Term:
  text: str

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return f'<span class="Term">{self.text}</span>'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return f'{{\\gameterm{{{self.text}}}}}'

@dataclass
class SubType:
  text: str

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return f'<span class="SubType">{self.text}</span>'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return f'\\textbf{{{self.text}}}'

@dataclass
class Card:
  text: str

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return f'<span class="Card">{self.text}</span>'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return f'\\textit{{{self.text}}}'

@dataclass
class Product:
  text: str

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return f'<span class="Product">{self.text}</span>'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return f'\\textit{{{self.text}}}'

@dataclass
class Link:
  text: str
  link: str

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return f'<a href={self.link}>{self.text}</a>'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    return f'\\hreful{{{self.link}}}{{{self.text}}}'

@dataclass
class NewStart:
  def to_html(self, config: Config, id_map: RefDict) -> str:
    return ''

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    if config.annotated:
      return '\\textbf{\\color{orange}'
    else:
      return ''

@dataclass
class NewEnd:
  def to_html(self, config: Config, id_map: RefDict) -> str:
    return ''

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    if config.annotated:
      return '}'
    else:
      return ''

TextElement = Union[Text, Ref, Term, Image, SubType, Product, Card, Link, NewStart, NewEnd]

@dataclass
class FormatText:
  textElements: list[TextElement]

  def to_plaintext(self) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_plaintext()
    return result

  def to_html(self, config: Config, id_map: RefDict) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_html(config, id_map)
    return result

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_latex(config, id_map)
    result = re.sub(r'\"(.*?)\"', r"``\1''", result)
    result = re.sub('&', '\&', result)
    return result

@dataclass
class Example:
  text: FormatText
  new: bool

  def to_html(self, config: Config, id_map: RefDict) -> str:
    return f'<li class="Example">Example: {self.text.to_html(config, id_map)}</li>'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    result = r'\emph{'
    if self.new and config.annotated:
      result += r'\textbf{\color{orange}'
    result += f'Example: {self.text.to_latex(config, id_map)}'
    result += r'}'
    if self.new and config.annotated:
      result += r'}'
    return result
