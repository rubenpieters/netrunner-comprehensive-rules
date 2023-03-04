from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import string

from rules_doc_generator.model.text import (RefDict, RefInfo, FormatText, Example)

@dataclass
class Rule:
  id: str
  format_text: FormatText
  section: str | None
  sub_rule: bool
  rules: list[Rule]
  examples: list[Example]

  def to_html(self, id_map: RefDict) -> str:
    result = self.format_text.to_html(id_map)
    for example in self.examples:
      result += f'<p>{example.to_html(id_map)}</p>'
    if self.rules:
      result += '<ol>'
      for rule in self.rules:
        result += f'<li class="SubRule" id="{id_map[rule.id].reference}">{rule.to_html(id_map)}</li>'
      result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = self.format_text.to_latex(id_map)
    result += '\n'
    if len(self.examples) > 0:
      result += '\n'
    for example in self.examples:
      if self.sub_rule:
        result += f'\\begin{{adjustwidth}}{{-14pt}}{{0pt}} {example.to_latex(id_map)} \end{{adjustwidth}}\n'
      else:  
        result += f'\\begin{{adjustwidth}}{{-27pt}}{{0pt}} {example.to_latex(id_map)} \end{{adjustwidth}}\n'
    if self.rules:
      for rule in self.rules:
        result += f'\\refstepcounter{{manual_refs}}\label{{{rule.id}}}\n'
        result += f'\\2 {rule.to_latex(id_map)}'
    return result

  def id_map_sub_rules(self, ctx: str, i: int, dict: dict[int, str], ref_type: str) -> int:
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    letters = string.ascii_lowercase[:14]
    dict[self.id] = RefInfo(f'{ctx}{letters[i]}', ref_type, '', self.id)

  def id_map(self, ctx: str, i: int, dict: dict[int, str]) -> int:
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    ref_type = 'step' if self.section == 'steps' else 'rule'
    dict[self.id] = RefInfo(f'{ctx}.{i}', ref_type, '', self.id)
    for j, rule in enumerate(self.rules):
      rule.id_map_sub_rules(f'{ctx}.{i}', j, dict, ref_type)

@dataclass
class Section:
  id: str
  text: str
  snippet: Optional[FormatText]
  rules: list[Rule]

  def to_html(self, id_map: RefDict) -> str:
    result = f'<h2>{self.text}</h2>'
    if self.snippet:
      result += f'<p>{self.snippet.to_html(id_map)}</p>'
    result += '<ol>'
    for elem in self.rules:
      result += f'<li class="Rule" id="{id_map[elem.id].reference}">{elem.to_html(id_map)}</li>'
    result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = f'\subsection{{{self.text}}}\n'
    result += f'\label{{{self.id}}}\n'
    if self.snippet:
      snippet_lines = self.snippet.to_latex(id_map).split('\n')
      for snippet_text in snippet_lines:
        result += f'\\noindent\emph{{{snippet_text}}}\n\n'

    result += '\\begin{outline}[enumerate]\n'
    for elem in self.rules:
      match elem:
        case Rule(): 
          if elem.section:
            result += '\\phantomsection\n'
            result += '\\addtocounter{subsubsection}{1}\n'
            result += '\\addcontentsline{toc}{subsubsection}{\\arabic{section}.\\arabic{subsection}.\\arabic{subsubsection}~~ ' + elem.format_text.to_latex(id_map) + '}\n'
          result += f'\\refstepcounter{{manual_refs}}\label{{{elem.id}}}\n'
          result += f'\\1 {elem.to_latex(id_map)}\n'
        case Example(): result += f'\\0 {elem.to_latex(id_map)}\n'
    result += '\end{outline}\n'
    return result

  def id_map(self, ctx: str, i: int, dict: dict[int, str]):
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    dict[self.id] = RefInfo(f'{ctx}.{i}', 'section', self.text, self.id)
    for j, elem in enumerate(self.rules):
      elem.id_map(f'{ctx}.{i}', j + 1, dict)

@dataclass
class Header:
  id: str
  text: str
  sections: list[Section]

  def to_html(self, id_map: RefDict) -> str:
    result = f'<h1>{self.text}</h1><ol>'
    for section in self.sections:
      result += f'<li class="Section" id="{id_map[section.id].reference}">{section.to_html(id_map)}</li>'
    result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = f'\section{{{self.text}}}\n'
    result += f'\label{{{self.id}}}\n'
    for section in self.sections:
      result += section.to_latex(id_map)
    return result

  def id_map(self, i: int, dict: RefDict):
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}', self.text)
    dict[self.id] = RefInfo(f'{i}', 'section', self.text, self.id)
    for j, elem in enumerate(self.sections):
      elem.id_map(f'{i}', j + 1, dict)

@dataclass
class Document:
  headers: list[Section]

  def to_html(self, id_map: RefDict) -> str:
    result = '<ol>'
    for header in self.headers:
      result += f'<li class="Header" id="{id_map[header.id].reference}">{header.to_html(id_map)}</li>'
    result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    latex_template = open("templates/latex/template.tex", "r")
    latex_content = latex_template.read()
    latex_template.close()
    
    latex_content = latex_content.replace("__CHANGELOG_PLACEHOLDER__", "")

    document_content = ''
    for element in self.headers:
      document_content += element.to_latex(id_map)
    latex_content = latex_content.replace("__DOCUMENT_PLACEHOLDER__", document_content)

    return latex_content

  def id_map(self):
    id_map = {}
    for j, elem in enumerate(self.headers):
      elem.id_map(j + 1, id_map)
    return id_map
