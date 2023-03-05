from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union
import string

from rules_doc_generator.model.text import (RefDict, RefInfo, FormatText, Example)

@dataclass
class TimingStructureElement:
  text: FormatText | None
  elements: list[TimingStructureElement]

  def to_html(self, id_map: RefDict) -> str:
    return ''

  def to_latex_l1(self, id_map: RefDict) -> str:
    result = f'\\1 \\textbf{{{self.text.to_latex(id_map)}}}\n'
    for elem in self.elements:
      result += elem.to_latex_l2(id_map)
    return result

  def to_latex_l2(self, id_map: RefDict) -> str:
    result = f'  \\2 {self.text.to_latex(id_map)}\n'
    for elem in self.elements:
      result += elem.to_latex_l3(id_map)
    return result

  def to_latex_l3(self, id_map: RefDict) -> str:
    return f'    \\3 {self.text.to_latex(id_map)}\n'

  def to_latex(self, id_map: RefDict) -> str:
    result = '\setlist[enumerate,1]{label=\\textbf{\\arabic*)}}\n'
    result += '\setlist[enumerate,2]{label=\\alph*)}\n'
    result += '\setlist[enumerate,3]{label=\\roman*)}\n'
    for elem in self.elements:
      result += elem.to_latex_l1(id_map)
    return result

@dataclass
class SubRule:
  id: str
  format_text: FormatText
  examples: list[Example]

  def to_html(self, id_map: RefDict) -> str:
    result = self.format_text.to_html(id_map)
    for example in self.examples:
      result += f'<p>{example.to_html(id_map)}</p>'
    return result
  
  def to_latex(self, id_map: RefDict) -> str:
    result = f'% SubRule {self.id}\n'
    result += f'  \\2 \\refstepcounter{{manual_refs}}\label{{{self.id}}} {self.format_text.to_latex(id_map)}\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-14pt}}{{0pt}} {example.to_latex(id_map)} \end{{adjustwidth}}\n'
    return result

  def id_map(self, ctx: str, i: int, dict: dict[int, str], ref_type: str) -> int:
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    letters = string.ascii_lowercase[:14]
    dict[self.id] = RefInfo(f'{ctx}{letters[i]}', ref_type, '', self.id)

@dataclass
class Rule:
  id: str
  format_text: FormatText
  toc: bool
  steps: bool
  rules: list[SubRule]
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
    result = f'% Rule {self.id}\n'
    result += '\\1 '
    if self.toc:
      result += '\\phantomsection '
      result += '\\addtocounter{subsubsection}{1} '
      result += '\\addcontentsline{toc}{subsubsection}{\\arabic{section}.\\arabic{subsection}.\\arabic{subsubsection}~~ ' + self.format_text.to_latex(id_map) + '} '
    result += f'\\refstepcounter{{manual_refs}} \label{{{self.id}}} {self.format_text.to_latex(id_map)}\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-27pt}}{{0pt}} {example.to_latex(id_map)} \end{{adjustwidth}}\n'
    if self.rules:
      for rule in self.rules:
        result += rule.to_latex(id_map)
    return result

  def id_map(self, ctx: str, i: int, dict: dict[int, str]) -> int:
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    ref_type = 'step' if self.steps == 'steps' else 'rule'
    dict[self.id] = RefInfo(f'{ctx}.{i}', ref_type, '', self.id)
    for j, rule in enumerate(self.rules):
      rule.id_map(f'{ctx}.{i}', j, dict, ref_type)

SectionElement = Union[Rule, TimingStructureElement]

@dataclass
class Section:
  id: str
  text: FormatText
  toc_entry: str | None
  snippet: Optional[FormatText]
  section_elements: list[SectionElement]

  def to_html(self, id_map: RefDict) -> str:
    result = f'<h2>{self.text.to_html(id_map)}</h2>'
    if self.snippet:
      result += f'<p>{self.snippet.to_html(id_map)}</p>'
    result += '<ol>'
    for elem in self.section_elements:
      match elem:
        case Rule(): result += f'<li class="Rule" id="{id_map[elem.id].reference}">{elem.to_html(id_map)}</li>'
    result += '</ol>'
    return result

  def to_latex(self, id_map: RefDict) -> str:
    result = f'% Section {self.id}.\n'
    if self.toc_entry:
      result += '\\addtocounter{subsection}{1}\n'
      result += '\\addcontentsline{toc}{subsection}{\\arabic{section}.\\arabic{subsection}~~ ' + self.toc_entry + '}\n'
      result += f'\subsection*{{\\arabic{{section}}.\\arabic{{subsection}}~~ {self.text.to_latex(id_map)}}}\n'
    else:
      result += f'\subsection{{{self.text.to_latex(id_map)}}}\n'
    result += f'\label{{{self.id}}}\n'
    if self.snippet:
      snippet_lines = self.snippet.to_latex(id_map).split('\n')
      for snippet_text in snippet_lines:
        result += f'\\noindent\emph{{{snippet_text}}}\n\n'

    result += '\\begin{outline}[enumerate]\n'
    for elem in self.section_elements:
      result += elem.to_latex(id_map)
    result += '\end{outline}\n'
    return result

  def id_map(self, ctx: str, i: int, dict: dict[int, str]):
    if self.id in dict:
      raise Exception(f'id defined twice: {self.id}')
    dict[self.id] = RefInfo(f'{ctx}.{i}', 'section', self.text, self.id)
    for j, elem in enumerate(self.section_elements):
      match elem:
        case Rule(): elem.id_map(f'{ctx}.{i}', j + 1, dict)

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
    result = f'% Header {self.id}.\n'
    result += f'\section{{{self.text}}}\n'
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
    latex_template = open("data/templates/latex/template.tex", "r")
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
