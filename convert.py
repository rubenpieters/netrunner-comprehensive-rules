from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Optional

import os
import re
import string

@dataclass
class RefInfo:
  reference: str
  type: str
  text: str

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

  def to_html(self, id_map: RefDict) -> str:
    if not self.referenced_id in id_map:
      raise Exception(f'id does not exist: {self.referenced_id}')
    ref_info = id_map[self.referenced_id]
    return f'<a href=#{ref_info.reference}>{ref_info.type} {ref_info.reference}</a>'

  def to_latex(self, id_map: RefDict) -> str:
    if not self.referenced_id in id_map:
      raise Exception(f'id does not exist: {self.referenced_id}')
    ref_info = id_map[self.referenced_id]
    return ref_info.reference

@dataclass
class Term:
  text: str

  def to_html(self, id_map: RefDict) -> str:
    return f'<span class="Term">{self.text}</span>'

  def to_latex(self, id_map: RefDict) -> str:
    return self.text


@dataclass
class FormatText:
  textElements: list[Union[Text, Ref, Term, Image]]

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

def create_toc_html(id_map: RefDict):
  result = ''
  for id in id_map:
    ref_info = id_map[id]
    if not (ref_info.type == 'rule' or ref_info.type == 'subrule'):
      result += f'<div>{ref_info.reference} {ref_info.text}</div>'
  return result

def standalone_html(section: Section, id_map: RefDict):
  result = '<!DOCTYPE html><html><head><link rel="stylesheet" href="demo.css"></head><body>'
  result += f'<div>{create_toc_html(id_map)}</div>'
  result += f'<div>{section.to_html(id_map)}</div>'
  result += '</body></html>'
  return result

def write_to_file(folder: str, filename: str, content: str):
  os.makedirs(folder, exist_ok=True)
  file = open(os.path.join(folder, filename), 'w')
  file.write(content)
  file.close()

x = Document(
     [ Header('hdr_game_concepts', 'Game Concepts',
        [ Section('sec_general', 'General', FormatText([Text('These rules are compatible with cards from the game '), Term('android: netrunner'), Text(' by Fantasy Flight Games. '), Term('android: netrunner'), Text(' is a game about the cyber-struggle between massive Corporations and subversive hackers known as Runners.')]),
          [ Rule('rule_1', FormatText([Text('The game is played between two players. One player takes the role of the Corp (Corporation) and the other takes the role of the Runner. This rules document will frequently refer to a player interchangeably with their game role.')]), [], [])
          , Rule('rule_2', FormatText([Text('Each player needs a legal deck, an identity card for their role, and any extra cards used from outside their deck. They also need a supply of tokens as described in '), Ref('sec_counters_tokens'), Text('. The constraints that define the legality of a deck are defined in section 1.4, and the cases where cards outside the deck and identity can be used are defined in section 1.5.')]), [], [])
          ])
        , Section('sec_golden_rules', 'Golden Rules', None,
          [ Rule('rule_3', FormatText([Text('If the text of a card directly contradicts these rules, the text of the card takes precedence.')]), [], [])
          , Rule('rule_4', FormatText([Text('If a rule or ability directs something to happen, but another effect states that it cannot happen, the "cannot" ability takes precedence.')]),
            [ Rule('rule_5', FormatText([Text('If a "cannot" effect prohibits all of the effects of another ability, that ability cannot be triggered.')]), [], [])
            , Rule('rule_6', FormatText([Text('If a "cannot" effect prohibits only part of another ability, that ability can be triggered, but the prohibited steps of resolving that ability are not carried out.')]), [],
              [ Example(FormatText([Text('During a run, Lockdown’s subroutine resolves, preventing the Runner from drawing cards for the remainder of the turn. The Runner has a Diesel and a Process Automation in their grip. For the remainder of this turn, they cannot play Diesel as its entire ability is prohibited, but they can play Process Automation. Even though cards cannot be drawn through Process Automation, the Runner can play it to gain 2'), Image('credit'), Text('.')]))
              ])
            ], [])
          ])
        , Section('sec_symbols', 'Symbols', None,
          [ Rule('symbol_guide', FormatText([Text('Several non-English symbols appear on cards and in this rules document. This section serves as a basic guide to those symbols.')]), [], [])
          , Rule('symbol_images', FormatText([Text('When this document is presented in a format without images, plaintext replacements are used. These replacements are listed along with the symbols themselves for reference.')]), [], [])
          , Rule('symbol_credit', FormatText([Text('The symbol '), Image('credit'), Text(' (plaintext: [c]) stands for “credit”. It always appears with a numeral, such as 1'), Image('credit'), Text(' , which means “one credit,” or 3'), Image('credit'), Text(' , which means “three credits.” See section 1.10 for rules about credits.')]), [], [])
          ])
        , Section('sec_deck_construction', f'Deck Construction', None, [])
        , Section('sec_extra_cards', f'Extra Cards', None, [])
        , Section('sec_starting', f'Starting the Game', None, [])
        , Section('sec_ending', f'Ending the Game', None, [])
        , Section('sec_cards', f'Cards', None, [])
        , Section('sec_counters_tokens', f'Counters and Tokens', None, [])
        ])
      ])

#print(x)
id_map = x.id_map()
write_to_file('html', 'demo.html', standalone_html(x, id_map))
write_to_file('latex', 'demo.tex', x.to_latex(id_map))
