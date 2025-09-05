from dataclasses import dataclass
from typing import Callable, Union

import re

from rules_doc_generator.config import (Config)
from rules_doc_generator.model.model_data import (ModelData)

def lookup_ref(model_data: ModelData, referenced_id: str):
  if not referenced_id in model_data.id_map:
    raise Exception(f'id does not exist: {referenced_id}')
  return model_data.id_map[referenced_id]

@dataclass
class Image:
  text: str

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return f'<img class="Symbol" src="{self.text}.svg" alt="{self.text}"/>'

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    # White-colored text overlapping with the image, to act as pseudo alt text.
    text = f'\\rlap{{\\color{{white}} {self.text}}}'
    text += '\hspace*{1pt}\\raisebox{-1pt}{\includesvg[height = 10pt]{'
    text += self.text
    return text + '}}'
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    match self.text:
      case "credit": return "[c]"
      case "click": return "[click]"
      case "recurring": return "[recurring]"
      case "link": return "[link]"
      case "mu": return "[MU]"
      case "sub": return "[sub]"
      case "trash": return "[trash]"
      case "interrupt": return "[interrupt]"
      case "trashcost": return "[trashcost]"
      case default: raise Exception(f'Unknown image: {self.text}')

@dataclass
class Text:
  text: str

  def to_plaintext(self) -> str:
    return self.text

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return self.text

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    return self.text.replace('{', '\{').replace('}', '\}')
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return self.text

@dataclass
class Ref:
  referenced_ids: list[str]
  capitalize: bool
  combiner: str

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return self.to_text(" ", model_data, lambda ref_id, ref_text: fr'<a href=#{ref_id}>{ref_text}</a>')

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    return self.to_text("~", model_data, lambda ref_id, ref_text: fr'\reful{{{ref_id}}}{{{ref_text}}}')
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return self.to_text(" ", model_data, lambda ref_id, ref_text: ref_text)

  def to_text(self, spacer: str, model_data: ModelData, mk_link: Callable[[str, str], str]) -> str:
    try:
      if len(self.referenced_ids) == 1:
        ref_info = lookup_ref(model_data, self.referenced_ids[0])
        ref_text = ref_info.type
        if self.capitalize:
          ref_text = ref_text.capitalize()
        return mk_link(ref_info.id, f'{ref_text}{spacer}{ref_info.reference}')
      elif len(self.referenced_ids) > 1:
        latex_refs = list(map(lambda ref_id: mk_link(ref_id, lookup_ref(model_data, ref_id).reference), self.referenced_ids))
        joined = f' {self.combiner} '.join([', '.join(latex_refs[:-1]), latex_refs[-1]])
        ref_info = model_data.id_map[self.referenced_ids[0]]
        ref_text = ref_info.type
        if self.capitalize:
          ref_text = ref_text.capitalize()
        return f'{ref_text}s {joined}'
      else:
        raise Exception('No referenced ids')
    except Exception as e:
      if "does not exist" in str(e):
        # TODO: make this a configurable option with a strict/non-strict setting.
        #unknown_ref_string = ','.join(self.referenced_ids).replace('_', '\_')
        #return f"UNKNOWNREF({unknown_ref_string})"
        # Default behavior is to re-raise the reference error.
        raise e
      else:
        raise e

@dataclass
class Term:
  text: str

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return f'<span class="Term">{self.text}</span>'

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    return f'{{\\gameterm{{{self.text}}}}}'
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return self.text.upper()

@dataclass
class SubType:
  text: str

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return f'<span class="SubType">{self.text}</span>'

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    return f'\\textbf{{{self.text}}}'
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return self.text

@dataclass
class Card:
  text: str

  def to_html(self, config: Config, model_data: ModelData) -> str:
    if self.text in model_data.nrdb_info:
      id = model_data.nrdb_info[self.text]
      return f'<a class="Thumbnail Card" href="https://netrunnerdb.com/en/card/{id}">{self.text}<span class="ThumbnailImageContainer"><img src="preview_placeholder.jpg" data-src="https://card-images.netrunnerdb.com/v2/large/{id}.jpg" /></span></a>'
    else:
      raise Exception('Unknown card title: {self.text}')

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    return f'\\textit{{{self.text}}}'
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return self.text

@dataclass
class Product:
  text: str

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return f'<span class="Product">{self.text}</span>'

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    return f'\\textit{{{self.text}}}'
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return self.text

@dataclass
class Link:
  text: str
  link: str

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return f'<a href={self.link}>{self.text}</a>'

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    return f'\\hreful{{{self.link}}}{{{self.text}}}'
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return f'{self.text} ({self.link})'

@dataclass
class NewStart:
  def to_html(self, config: Config, model_data: ModelData) -> str:
    return ''

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    if config.annotated:
      return '\\textbf{\\color{orange}'
    else:
      return ''
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return ''

@dataclass
class NewEnd:
  def to_html(self, config: Config, model_data: ModelData) -> str:
    return ''

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    if config.annotated:
      return '}'
    else:
      return ''
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return ''

TextElement = Union[Text, Ref, Term, Image, SubType, Product, Card, Link, NewStart, NewEnd]

@dataclass
class FormatText:
  textElements: list[TextElement]

  def to_plaintext(self) -> str:
    result = ''
    for element in self.textElements:
      match element:
        case Text(): result += element.to_plaintext()
        case _: raise Exception(f'Unexpected element type for plaintext: {element}')
    return result

  def to_html(self, config: Config, model_data: ModelData) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_html(config, model_data)
    return result

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_latex(config, model_data)
    result = re.sub(r'\"(.*?)\"', r"``\1''", result)
    result = re.sub('&', '\&', result)
    return result
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    result = ''
    for element in self.textElements:
      result += element.to_json(config, model_data).replace('"', '\\"')
    return result

@dataclass
class Example:
  text: FormatText
  new: bool

  def to_html(self, config: Config, model_data: ModelData) -> str:
    return f'<li class="Example">Example: {self.text.to_html(config, model_data)}</li>'

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    result = r'\emph{'
    if self.new and config.annotated:
      result += r'\textbf{\color{orange}'
    result += f'Example: {self.text.to_latex(config, model_data)}'
    result += r'}'
    if self.new and config.annotated:
      result += r'}'
    return result
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return self.text.to_json(config, model_data).replace('"', '\\"')
