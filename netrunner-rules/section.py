from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Optional
from text import (RefDict, RefInfo, FormatText, Example)

import string

@dataclass
class Rule:
  id: str
  formatText: FormatText
  rules: list[Rule]
  examples: list[Example]

  def to_html(self, id_map: RefDict) -> str:
    result = self.formatText.to_html(id_map)
    for example in self.examples:
      result += f'<p>{example.to_html(id_map)}</p>'
    if self.rules:
      result += '<ol>'
      for rule in self.rules:
        result += f'<li class="SubRule" id="{id_map[rule.id].reference}">{rule.to_html(id_map)}</li>'
      result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = self.formatText.to_latex(id_map)
    result += '\n'
    for example in self.examples:
      result += f'\\0 {example.to_latex(id_map)}\n'
    if self.rules:
      for rule in self.rules:
        result += f'\\2 {rule.to_latex(id_map)}'
    return result

  def id_map_sub_rules(self, ctx: str, i: int, dict: dict[int, str]) -> int:
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    letters = string.ascii_lowercase[:14]
    dict[self.id] = RefInfo(f'{ctx}{letters[i]}', 'rule', '')

  def id_map(self, ctx: str, i: int, dict: dict[int, str]) -> int:
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    dict[self.id] = RefInfo(f'{ctx}.{i}', 'rule', '')
    for j, rule in enumerate(self.rules):
      rule.id_map_sub_rules(f'{ctx}.{i}', j, dict)

@dataclass
class Section:
  id: str
  text: str
  lore: Optional[FormatText]
  elements: list[Union[Rule, Example]]

  def to_html(self, id_map: RefDict) -> str:
    result = f'<h2>{self.text}</h2>'
    if self.lore:
      result += f'<p>{self.lore.to_html(id_map)}</p>'
    result += '<ol>'
    for elem in self.elements:
      result += f'<li class="Rule" id="{id_map[elem.id].reference}">{elem.to_html(id_map)}</li>'
    result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = f'\subsection{{{self.text}}}\n'
    if self.lore:
      result += f'{self.lore.to_latex(id_map)}\n'
    prefix = id_map[self.id].reference
    result += f'\setlist[enumerate,1]{{label={prefix}.\\arabic*.,leftmargin=*,labelindent=4pt}}\n'
    result += '\\begin{outline}[enumerate]\n'
    for elem in self.elements:
      match elem:
        case Rule(): result += f'\\1 {elem.to_latex(id_map)}\n'
        case Example(): result += f'\\0 \begin{{adjustwidth}}{{37pt}}{{0pt}} {elem.to_latex(id_map)} \end{{adjustwidth}}\n'
    result += '\end{outline}\n'
    return result

  def id_map(self, ctx: str, i: int, dict: dict[int, str]):
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    dict[self.id] = RefInfo(f'{ctx}.{i}', 'section', self.text)
    for j, elem in enumerate(self.elements):
      elem.id_map(f'{ctx}.{i}', j + 1, dict)

@dataclass
class Header:
  id: str
  text: str
  elements: list[Section]

  def to_html(self, id_map: RefDict) -> str:
    result = f'<h1>{self.text}</h1><ol>'
    for section in self.elements:
      result += f'<li class="Section" id="{id_map[section.id].reference}">{section.to_html(id_map)}</li>'
    result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = f'\section{{{self.text}}}\n'
    for section in self.elements:
      result += section.to_latex(id_map)
    result += '\end{document}'
    return result

  def id_map(self, i: int, dict: RefDict):
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}', self.text)
    dict[self.id] = RefInfo(f'{i}', 'header', self.text)
    for j, elem in enumerate(self.elements):
      elem.id_map(f'{i}', j + 1, dict)

@dataclass
class Document:
  elements: list[Section]

  def to_html(self, id_map: RefDict) -> str:
    result = '<ol>'
    for header in self.elements:
      result += f'<li class="Header" id="{id_map[header.id].reference}">{header.to_html(id_map)}</li>'
    result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = '\documentclass{article}\n'
    result += '\\usepackage[a4paper,bindingoffset=0.1in,left=0.8in,right=0.8in,top=0.8in,bottom=0.8in,footskip=.25in]{geometry}\n'
    result += '\\usepackage{outlines}\n'
    result += '\\usepackage{enumitem}\n'
    result += '\\usepackage{changepage}\n'
    result += '\\setlist[enumerate,2]{label=\\alph*.}\n'
    result += '\\begin{document}\n'
    for subsection in self.elements:
      result += subsection.to_latex(id_map)
    result += '\end{document}\n'
    return result

  def id_map(self):
    id_map = {}
    for j, elem in enumerate(self.elements):
      elem.id_map(j + 1, id_map)
    return id_map