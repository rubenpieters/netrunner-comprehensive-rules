from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union

from rules_doc_generator.config import (Config)
from rules_doc_generator.model.text import (RefDict, FormatText, Example)

@dataclass
class TimingStructureElement:
  text: FormatText | None
  bold: bool
  elements: list[TimingStructureElement]

  def to_html_l1(self, config: Config, id_map: RefDict, bold: bool) -> str:
    if bold:
      result = f'<li class="TimingStructureL1 TimingStructureBold">{self.text.to_html(config, id_map)}'
    else:
      result = f'<li class="TimingStructureL1 TimingStructureNormal">{self.text.to_html(config, id_map)}'
    result += f'<ol>'
    for elem in self.elements:
      result += elem.to_html_l2(config, id_map)
    result += '</ol></li>'
    return result

  def to_html_l2(self, config: Config, id_map: RefDict) -> str:
    result = f'<li class="TimingStructureL2 TimingStructureNormal">{self.text.to_html(config, id_map)}'
    result += f'<ol>'
    for elem in self.elements:
      result += elem.to_html_l3(config, id_map)
    result += '</ol></li>'
    return result

  def to_html_l3(self, config: Config, id_map: RefDict) -> str:
    return f'<li class="TimingStructureL3 TimingStructureNormal">{self.text.to_html(config, id_map)}</li>'

  def to_html(self, config: Config, id_map: RefDict) -> str:
    result = '<ol class="TimingStructureList">'
    for elem in self.elements:
      result += elem.to_html_l1(config, id_map, self.bold)
    result += '</ol>'
    return result

  def to_latex_l1(self, config: Config, id_map: RefDict, bold: bool) -> str:
    result = '\\1 '
    if bold:
      result += '\\textbf{'
    result += self.text.to_latex(config, id_map)
    if bold:
      result += '}'
    result += '\n'
    for elem in self.elements:
      result += elem.to_latex_l2(config, id_map)
    return result

  def to_latex_l2(self, config: Config, id_map: RefDict) -> str:
    result = f'  \\2 {self.text.to_latex(config, id_map)}\n'
    for elem in self.elements:
      result += elem.to_latex_l3(config, id_map)
    return result

  def to_latex_l3(self, config: Config, id_map: RefDict) -> str:
    return f'    \\3 {self.text.to_latex(config, id_map)}\n'

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    if self.bold:
      result = '\setlist[enumerate,1]{label=\\textbf{\\arabic*)}}\n'
    else:
      result = '\setlist[enumerate,1]{label=\\arabic*)}\n'
    result += '\setlist[enumerate,2]{label=\\alph*)}\n'
    result += '\setlist[enumerate,3]{label=\\roman*)}\n'
    for elem in self.elements:
      result += elem.to_latex_l1(config, id_map, self.bold)
    return result
  
  def to_json(self, config: Config, id_map: RefDict) -> str:
    return 'TODO'

@dataclass
class SubRule:
  id: Union[str, None]
  new: bool
  format_text: FormatText
  examples: list[Example]

  def to_html(self, config: Config, id_map: RefDict) -> str:
    result = self.format_text.to_html(config, id_map)
    result += '<ol class="Examples ExamplesSubRule">'
    for example in self.examples:
      result += example.to_html(config, id_map)
    result += '</ol>'
    return result
  
  def to_latex(self, config: Config, id_map: RefDict) -> str:
    result = f'% SubRule {self.id}\n'
    result += f'\\refstepcounter{{manual_refs}} \label{{{self.id}}} '
    if self.new and config.annotated:
      result += '\\global \\colorlabeltrue '
    result += '\\2 '
    if self.new and config.annotated:
      result += '\\color{orange} \\bfseries '
    result += self.format_text.to_latex(config, id_map)
    if self.new and config.annotated:
      result += '\\color{black} \\normalfont'
    # Additional newline after this paragraph to ensure correct spacing.
    result += '\n\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-14pt}}{{0pt}} {example.to_latex(config, id_map)} \end{{adjustwidth}}\n'
    return result

@dataclass
class Rule:
  id: Union[str, None]
  new: bool
  format_text: FormatText
  examples: list[Example]

  def to_html(self, config: Config, id_map: RefDict) -> str:
    result = self.format_text.to_html(config, id_map)
    result += '<ol class="Examples ExamplesRule">'
    for example in self.examples:
      result += example.to_html(config, id_map)
    result += '</ol>'
    return result

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    result = f'% Rule {self.id}\n'
    result += '\\addtocounter{subsubsection}{1} '
    result += f'\\refstepcounter{{manual_refs}} \label{{{self.id}}} '
    if self.new and config.annotated:
      result += '\\global \\colorlabeltrue '
    result += '\\1 '
    if self.new and config.annotated:
      result += '\\color{orange} \\bfseries '
    result += self.format_text.to_latex(config, id_map)
    if self.new and config.annotated:
      result += '\\color{black} \\normalfont'
    # Additional newline after this paragraph to ensure correct spacing.
    result += '\n\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-27pt}}{{0pt}} {example.to_latex(config, id_map)} \end{{adjustwidth}}\n'
    return result
  
  def to_json(self, config: Config, id_map: RefDict) -> str:
    return f'"{self.id}": "{self.format_text.to_json(config, id_map)}"'

@dataclass
class SubSection:
  id: Union[str, None]
  new: bool
  format_text: FormatText
  toc: bool
  steps: bool
  snippet: Optional[FormatText]
  examples: list[Example]
  rules: list[SubRule]

  def to_html(self, config: Config, id_map: RefDict) -> str:
    if self.toc:
      result = f'<span class="SubSection">{self.format_text.to_html(config, id_map)}</span>'
    else:
      result = self.format_text.to_html(config, id_map)
    if self.rules:
      result += '<ol class="SubRules">'
      if self.snippet:
        result += f'<p class="Snippet">{self.snippet.to_html(config, id_map)}</p>'
      result += '<ol class="Examples ExamplesSubSection">'
      for example in self.examples:
        result += example.to_html(config, id_map)
      result += '</ol>'
      for rule in self.rules:
        result += f'<li class="SubRule" id="{rule.id}">{rule.to_html(config, id_map)}</li>'
      result += '</ol>'
    return result

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    result = f'% SubSection {self.id}\n'
    result += '\\addtocounter{subsubsection}{1} '
    if self.toc:
      # Needed for hyperref to jump to the correct place.
      # https://tex.stackexchange.com/questions/44088/when-do-i-need-to-invoke-phantomsection
      result += '\\phantomsection '
      result += '\\addcontentsline{toc}{subsubsection}{\\arabic{section}.\\arabic{subsection}.\\arabic{subsubsection}~~ ' + self.format_text.to_latex(config, id_map) + '} '
    result += f'\\refstepcounter{{manual_refs}} \label{{{self.id}}} '
    if self.new and config.annotated:
      result += '\\global \\colorlabeltrue '
    result += '\\1 '
    if self.new and config.annotated:
      result += '\\color{orange} \\bfseries '
    if self.toc:
      result += '\\large '
    if self.toc and not (self.new and config.annotated):
      result += '\\bfseries \\color{darkgray}'
    result += self.format_text.to_latex(config, id_map)
    if self.toc or (self.new and config.annotated):
      result += '\\color{black} \\normalfont'
    if self.toc:
      result += ' \\normalsize'
    result += '\n'
    if self.snippet:
      snippet_lines = self.snippet.to_latex(config, id_map).split('\n')
      for snippet_text in snippet_lines:
        result += f'\n\\noindent\emph{{{snippet_text}}}\n\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-27pt}}{{0pt}} {example.to_latex(config, id_map)} \end{{adjustwidth}}\n'
    if self.rules:
      for rule in self.rules:
        result += rule.to_latex(config, id_map)
    return result
  
  def to_json(self, config: Config, id_map: RefDict) -> str:
    return f'"{self.id}": "{self.format_text.to_json(config, id_map)}"'
  
  def toc_text(self):
    return self.format_text.to_plaintext() if self.toc else ''

SectionElement = Union[Rule, SubSection, TimingStructureElement]

@dataclass
class Section:
  id: str
  new: bool
  text: FormatText
  toc_entry: str | None
  snippet: Optional[FormatText]
  section_elements: list[SectionElement]

  def to_html(self, config: Config, id_map: RefDict) -> str:
    result = f'<h2 class="Section" id="{self.id}">{self.text.to_html(config, id_map)}</h2>'
    if self.snippet:
      result += f'<p class="Snippet">{self.snippet.to_html(config, id_map)}</p>'
    result += '<ol class="Rules">'
    for elem in self.section_elements:
      match elem:
        case Rule(): result += f'<li class="Rule" id="{elem.id}">{elem.to_html(config, id_map)}</li>'
        case SubSection(): result += f'<li class="Rule" id="{elem.id}">{elem.to_html(config, id_map)}'
        case TimingStructureElement(): result += elem.to_html(config, id_map)
    result += '</ol>'
    return result

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    result = f'% Section {self.id}.\n'
    if self.toc_entry:
      result += f'\subsection[{self.toc_entry}]{{{self.text.to_latex(config, id_map)}}}\n'
    elif self.new and config.annotated:
      result += f'{{\color{{orange}}\subsection{{{self.text.to_latex(config, id_map)}}}}}\n'
    else:
      result += f'\subsection{{{self.text.to_latex(config, id_map)}}}\n'
    result += f'\label{{{self.id}}}\n'
    if self.snippet:
      snippet_lines = self.snippet.to_latex(config, id_map).split('\n')
      for snippet_text in snippet_lines:
        result += f'\\noindent\emph{{{snippet_text}}}\n\n'

    result += '\\begin{outline}[enumerate]\n'
    for elem in self.section_elements:
      result += elem.to_latex(config, id_map)
    result += '\end{outline}\n'
    return result
  
  def to_json(self, config: Config, id_map: RefDict) -> str:
    return f'"{self.id}": "{self.text.to_json(config, id_map)}",\n' + \
      ',\n'.join(map(lambda element: element.to_json(config, id_map), self.section_elements))
  
  def toc_text(self):
    return self.toc_entry if self.toc_entry else self.text.to_plaintext()

@dataclass
class Chapter:
  id: str
  text: str
  sections: list[Section]

  def to_html(self, config: Config, id_map: RefDict) -> str:
    result = f'<h1 class="Chapter" id="{self.id}">{self.text}</h1>'
    for section in self.sections:
      result += section.to_html(config, id_map)
    return result

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    result = f'% Chapter {self.id}.\n'
    result += f'\section{{{self.text}}}\n'
    result += f'\label{{{self.id}}}\n'
    for section in self.sections:
      result += section.to_latex(config, id_map)
    return result

  def to_json(self, config: Config, id_map: RefDict) -> str:
    return f'"{self.id}": "{self.text}",\n' + \
      ',\n'.join(map(lambda section: section.to_json(config, id_map), self.sections))

@dataclass
class Document:
  changelog: list[FormatText]
  chapters: list[Chapter]

  def to_html(self, config: Config, id_map: RefDict) -> str:
    result = ''
    for chapter in self.chapters:
      result += chapter.to_html(config, id_map)
    return result

  def to_latex(self, config: Config, id_map: RefDict) -> str:
    latex_template = open("data/templates/latex/template.tex", "r")
    latex_content = latex_template.read()
    latex_template.close()
    
    changelog_content = "\n\\1 ".join(map(lambda x: x.to_latex(config, id_map), self.changelog))
    latex_content = latex_content.replace("%__CHANGELOG_PLACEHOLDER__%", f'\\1 {changelog_content}')

    document_content = ''.join(map(lambda x: x.to_latex(config, id_map), self.chapters))
    latex_content = latex_content.replace("%__DOCUMENT_PLACEHOLDER__%", document_content)

    return latex_content
  
  def to_json(self, config: Config, id_map: RefDict) -> str:
    return ',\n'.join(map(lambda chapter: chapter.to_json(config, id_map), self.chapters[:-1]))

ModelElement = Union[Document, Chapter, Section, SectionElement, SubRule]
