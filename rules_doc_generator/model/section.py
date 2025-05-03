from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Union

from rules_doc_generator.config import (Config)
from rules_doc_generator.model.text import (FormatText, Example)
from rules_doc_generator.model.model_data import (ModelData)

@dataclass
class TimingStructureElement:
  text: FormatText
  elements: list[TimingStructureElement]

  def to_html_l1(self, config: Config, model_data: ModelData, bold: bool) -> str:
    if bold:
      result = f'<li class="TimingStructureL1 TimingStructureBold">{self.text.to_html(config, model_data)}'
    else:
      result = f'<li class="TimingStructureL1 TimingStructureNormal">{self.text.to_html(config, model_data)}'
    result += f'<ol>'
    for elem in self.elements:
      result += elem.to_html_l2(config, model_data)
    result += '</ol></li>'
    return result

  def to_html_l2(self, config: Config, model_data: ModelData) -> str:
    result = f'<li class="TimingStructureL2 TimingStructureNormal">{self.text.to_html(config, model_data)}'
    result += f'<ol>'
    for elem in self.elements:
      result += elem.to_html_l3(config, model_data)
    result += '</ol></li>'
    return result

  def to_html_l3(self, config: Config, model_data: ModelData) -> str:
    return f'<li class="TimingStructureL3 TimingStructureNormal">{self.text.to_html(config, model_data)}</li>'

  def to_latex_l1(self, config: Config, model_data: ModelData, bold: bool) -> str:
    result = '\\1 '
    if bold:
      result += '\\textbf{'
    result += self.text.to_latex(config, model_data)
    if bold:
      result += '}'
    result += '\n'
    for elem in self.elements:
      result += elem.to_latex_l2(config, model_data)
    return result

  def to_latex_l2(self, config: Config, model_data: ModelData) -> str:
    result = f'  \\2 {self.text.to_latex(config, model_data)}\n'
    for elem in self.elements:
      result += elem.to_latex_l3(config, model_data)
    return result

  def to_latex_l3(self, config: Config, model_data: ModelData) -> str:
    return f'    \\3 {self.text.to_latex(config, model_data)}\n'


@dataclass
class TimingStructure:
  bold: bool
  elements: list[TimingStructureElement]

  def to_html(self, config: Config, model_data: ModelData) -> str:
    result = '<ol class="TimingStructureList">'
    for elem in self.elements:
      result += elem.to_html_l1(config, model_data, self.bold)
    result += '</ol>'
    return result

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    if self.bold:
      result = '\setlist[enumerate,1]{label=\\textbf{\\arabic*)}}\n'
    else:
      result = '\setlist[enumerate,1]{label=\\arabic*)}\n'
    result += '\setlist[enumerate,2]{label=\\alph*)}\n'
    result += '\setlist[enumerate,3]{label=\\roman*)}\n'
    for elem in self.elements:
      result += elem.to_latex_l1(config, model_data, self.bold)
    return result
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return 'TODO'

@dataclass
class SubRule:
  id: str
  new: bool
  format_text: FormatText
  examples: list[Example]

  def to_html(self, config: Config, model_data: ModelData) -> str:
    result = self.format_text.to_html(config, model_data)
    result += '<ol class="Examples ExamplesSubRule">'
    for example in self.examples:
      result += example.to_html(config, model_data)
    result += '</ol>'
    return result
  
  def to_latex(self, config: Config, model_data: ModelData) -> str:
    result = f'% SubRule {self.id}\n'
    result += f'\\refstepcounter{{manual_refs}} \label{{{self.id}}} '
    if self.new and config.annotated:
      result += '\\global \\colorlabeltrue '
    result += '\\2 '
    if self.new and config.annotated:
      result += '\\color{orange} \\bfseries '
    result += self.format_text.to_latex(config, model_data)
    if self.new and config.annotated:
      result += '\\color{black} \\normalfont'
    # Additional newline after this paragraph to ensure correct spacing.
    result += '\n\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-14pt}}{{0pt}} {example.to_latex(config, model_data)} \end{{adjustwidth}}\n'
    return result
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    obj = "{"
    obj += f'"id": "{self.id}",'
    obj += f'"nr": "{model_data.id_map[self.id].reference}",'
    obj += f'"type": "{model_data.id_map[self.id].type}",'
    obj += f'"text": "{self.format_text.to_json(config, model_data)}", "children": [],'
    examples = ','.join(map(lambda example: f'"{example.text.to_json(config, model_data)}"', self.examples))
    obj += f'"examples": [{examples}]'
    obj += "}"
    return obj

@dataclass
class Rule:
  id: str
  new: bool
  format_text: FormatText
  examples: list[Example]

  def to_html(self, config: Config, model_data: ModelData) -> str:
    result = self.format_text.to_html(config, model_data)
    result += '<ol class="Examples ExamplesRule">'
    for example in self.examples:
      result += example.to_html(config, model_data)
    result += '</ol>'
    return result

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    result = f'% Rule {self.id}\n'
    result += '\\addtocounter{subsubsection}{1} '
    result += f'\\refstepcounter{{manual_refs}} \label{{{self.id}}} '
    if self.new and config.annotated:
      result += '\\global \\colorlabeltrue '
    result += '\\1 '
    if self.new and config.annotated:
      result += '\\color{orange} \\bfseries '
    result += self.format_text.to_latex(config, model_data)
    if self.new and config.annotated:
      result += '\\color{black} \\normalfont'
    # Additional newline after this paragraph to ensure correct spacing.
    result += '\n\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-27pt}}{{0pt}} {example.to_latex(config, model_data)} \end{{adjustwidth}}\n'
    return result
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    obj = "{"
    obj += f'"id": "{self.id}",'
    obj += f'"nr": "{model_data.id_map[self.id].reference}",'
    obj += f'"type": "{model_data.id_map[self.id].type}",'
    obj += f'"text": "{self.format_text.to_json(config, model_data)}", "children": [],'
    examples = ','.join(map(lambda example: f'"{example.text.to_json(config, model_data)}"', self.examples))
    obj += f'"examples": [{examples}]'
    obj += "}"
    return obj

@dataclass
class SubSection:
  id: str
  new: bool
  format_text: FormatText
  toc: bool
  steps: bool
  snippet: Optional[FormatText]
  examples: list[Example]
  rules: list[SubRule]

  def to_html(self, config: Config, model_data: ModelData) -> str:
    if self.toc:
      result = f'<span class="SubSection">{self.format_text.to_html(config, model_data)}</span>'
    else:
      result = self.format_text.to_html(config, model_data)
    if self.rules:
      result += '<ol class="SubRules">'
      if self.snippet:
        result += f'<p class="Snippet">{self.snippet.to_html(config, model_data)}</p>'
      result += '<ol class="Examples ExamplesSubSection">'
      for example in self.examples:
        result += example.to_html(config, model_data)
      result += '</ol>'
      for rule in self.rules:
        ruleletter:str = f'{model_data.id_map[rule.id].reference[-1]}.'
        result += f'<li class="SubRule" id="{rule.id}"><span class="RuleLinkOuterWrapper"><span class="RuleLinkInnerWrapper"><a class="RuleAnchor" href="#{rule.id}"></a><a class="RuleLink" href="#{rule.id}">{ruleletter}</a><span class="RuleLinkSymbol material-symbols-outlined">link</span></span></span>{rule.to_html(config, model_data)}</li>'
      result += '</ol>'
    return result

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    result = f'% SubSection {self.id}\n'
    result += '\\addtocounter{subsubsection}{1} '
    if self.toc:
      # Needed for hyperref to jump to the correct place.
      # https://tex.stackexchange.com/questions/44088/when-do-i-need-to-invoke-phantomsection
      result += '\\phantomsection '
      result += '\\addcontentsline{toc}{subsubsection}{\\arabic{section}.\\arabic{subsection}.\\arabic{subsubsection}~~ ' + self.format_text.to_latex(config, model_data) + '} '
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
    result += self.format_text.to_latex(config, model_data)
    if self.toc or (self.new and config.annotated):
      result += '\\color{black} \\normalfont'
    if self.toc:
      result += ' \\normalsize'
    result += '\n'
    if self.snippet:
      snippet_lines = self.snippet.to_latex(config, model_data).split('\n')
      for snippet_text in snippet_lines:
        result += f'\n\\noindent\emph{{{snippet_text}}}\n\n'
    for i, example in enumerate(self.examples):
      result += f'% Example {i}\n'
      result += f'\\begin{{adjustwidth}}{{-27pt}}{{0pt}} {example.to_latex(config, model_data)} \end{{adjustwidth}}\n'
    if self.rules:
      for rule in self.rules:
        result += rule.to_latex(config, model_data)
    return result
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    obj = "{"
    obj += f'"id": "{self.id}",'
    obj += f'"nr": "{model_data.id_map[self.id].reference}",'
    obj += f'"type": "{model_data.id_map[self.id].type}",'
    obj += f'"text": "{self.format_text.to_json(config, model_data)}",'
    childrenIds = ','.join(map(lambda rule: f'"{rule.id}"', self.rules))
    obj += f'"children": [{childrenIds}],'
    examples = ','.join(map(lambda example: f'"{example.text.to_json(config, model_data)}"', self.examples))
    obj += f'"examples": [{examples}]'
    obj += "}"
    return f'{obj},\n' + \
      ',\n'.join(map(lambda element: element.to_json(config, model_data), self.rules))
  
  def toc_text(self):
    return self.format_text.to_plaintext() if self.toc else ''

SectionElement = Union[Rule, SubSection, TimingStructure]

@dataclass
class Section:
  id: str
  new: bool
  text: FormatText
  toc_entry: str | None
  steps: bool
  snippet: Optional[FormatText]
  section_elements: list[SectionElement]

  def to_html(self, config: Config, model_data: ModelData) -> str:
    secnr:str = f'{model_data.id_map[self.id].reference}.'
    result = f'<h2 class="Section" id="{self.id}"><a class="RuleLink" href="#{self.id}">{secnr} {self.text.to_html(config, model_data)}</a><span class="RuleLinkSymbol material-symbols-outlined">link</span></h2>'
    if self.snippet:
      result += f'<p class="Snippet">{self.snippet.to_html(config, model_data)}</p>'
    result += '<ol class="Rules">'
    for n, elem in enumerate(self.section_elements):
      rulenr:str = f'{model_data.id_map[self.id].reference}.{n+1}.'

      match elem:
        case Rule():       result += f'<li class="Rule" id="{elem.id}"><span class="RuleLinkOuterWrapper"><span class="RuleLinkInnerWrapper"><a class="RuleAnchor" href="#{elem.id}"></a><a class="RuleLink" href="#{elem.id}">{rulenr}</a><span class="RuleLinkSymbol material-symbols-outlined">link</span></span></span>{elem.to_html(config, model_data)}</li>'
        case SubSection(): result += f'<li class="Rule" id="{elem.id}"><span class="RuleLinkOuterWrapper"><span class="RuleLinkInnerWrapper"><a class="RuleAnchor" href="#{elem.id}"></a><a class="RuleLink" href="#{elem.id}">{rulenr}</a><span class="RuleLinkSymbol material-symbols-outlined">link</span></span></span>{elem.to_html(config, model_data)}</li>'
        case TimingStructure(): result += elem.to_html(config, model_data)
    result += '</ol>'
    return result

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    result = f'% Section {self.id}.\n'
    text = self.text.to_latex(config, model_data)
    toc_text = self.toc_entry if self.toc_entry else text

    result += '\\addtocounter{subsection}{1} \setcounter{subsubsection}{0} '
    # Needed for hyperref to jump to the correct place.
    # https://tex.stackexchange.com/questions/44088/when-do-i-need-to-invoke-phantomsection
    result += '\\phantomsection '
    result += f'\\addcontentsline{{toc}}{{subsection}}{{\\arabic{{section}}.\\arabic{{subsection}}~~ {toc_text}}} '
    if self.new and config.annotated:
      result += f'\subsection*{{\\color{{orange}} \\arabic{{section}}.\\arabic{{subsection}}~~ {text}}}'
    else:
      result += f'\subsection*{{\\arabic{{section}}.\\arabic{{subsection}}~~ {text}}}'

    result += f'\label{{{self.id}}}\n'
    if self.snippet:
      snippet_lines = self.snippet.to_latex(config, model_data).split('\n')
      for snippet_text in snippet_lines:
        result += f'\\noindent\emph{{{snippet_text}}}\n\n'

    result += '\\begin{outline}[enumerate]\n'
    for elem in self.section_elements:
      result += elem.to_latex(config, model_data)
    result += '\end{outline}\n'
    return result
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    obj = "{"
    obj += f'"id": "{self.id}",'
    obj += f'"nr": "{model_data.id_map[self.id].reference}",'
    obj += f'"type": "{model_data.id_map[self.id].type}",'
    obj += f'"text": "{self.text.to_json(config, model_data)}",'
    childrenIds = ','.join(map(lambda element: f'"{element.id}"' if hasattr(element, "id") else "TODO", self.section_elements))
    obj += f'"children": [{childrenIds}]'
    obj += "}"
    return f'{obj},\n' + \
      ',\n'.join(map(lambda element: element.to_json(config, model_data), self.section_elements))
  
  def toc_text(self):
    return self.toc_entry if self.toc_entry else self.text.to_plaintext()

@dataclass
class Chapter:
  id: str
  new: bool
  text: str
  sections: list[Section]

  def to_html(self, config: Config, model_data: ModelData) -> str:
    chapnr:str = f'{model_data.id_map[self.id].reference}.'
    result = f'<h1 class="Chapter" id="{self.id}"><a class="RuleLink" href="#{self.id}">{chapnr} {self.text}</a><span class="RuleLinkSymbol material-symbols-outlined">link</span></h1>'
    for section in self.sections:
      result += section.to_html(config, model_data)
    return result

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    result = f'% Chapter {self.id}.\n'

    result += '\\addtocounter{section}{1} \setcounter{subsection}{0}  \setcounter{subsubsection}{0} '
    # Needed for hyperref to jump to the correct place.
    # https://tex.stackexchange.com/questions/44088/when-do-i-need-to-invoke-phantomsection
    result += '\\phantomsection '
    result += f'\\addcontentsline{{toc}}{{section}}{{\\arabic{{section}}~~ {self.text}}} '
    if self.new and config.annotated:
      result += f'\section*{{\\color{{orange}} \\arabic{{section}}~~ {self.text}}}'
    else:
      result += f'\section*{{\\arabic{{section}}~~ {self.text}}}'

    result += f'\label{{{self.id}}}\n'
    for section in self.sections:
      result += section.to_latex(config, model_data)
    return result

  def to_json(self, config: Config, model_data: ModelData) -> str:
    obj = "{"
    obj += f'"id": "{self.id}",'
    obj += f'"nr": "{model_data.id_map[self.id].reference}",'
    obj += f'"type": "{model_data.id_map[self.id].type}",'
    obj += f'"text": "{self.text}",'
    childrenIds = ','.join(map(lambda section: f'"{section.id}"', self.sections))
    obj += f'"children": [{childrenIds}]'
    obj += "}"
    return f'{obj},\n' + \
      ',\n'.join(map(lambda section: section.to_json(config, model_data), self.sections))

@dataclass
class Document:
  changelog: list[FormatText]
  chapters: list[Chapter]

  def to_html(self, config: Config, model_data: ModelData) -> str:
    result = ''
    for chapter in self.chapters:
      result += chapter.to_html(config, model_data)
    return result

  def to_latex(self, config: Config, model_data: ModelData) -> str:
    latex_template = open("data/templates/latex/template.tex", "r")
    latex_content = latex_template.read()
    latex_template.close()
    
    changelog_content = "\n\\1 ".join(map(lambda x: x.to_latex(config, model_data), self.changelog))
    latex_content = latex_content.replace("%__CHANGELOG_PLACEHOLDER__%", f'\\1 {changelog_content}')

    document_content = ''.join(map(lambda x: x.to_latex(config, model_data), self.chapters))
    date_content = f'This version of the Comprehensive Rules document is effective \\textbf{{{config.effective_date_str()}}}.'
    latex_content = latex_content.replace("%__DATE_PLACEHOLDER__%", date_content)
    latex_content = latex_content.replace("%__DOCUMENT_PLACEHOLDER__%", document_content)

    return latex_content
  
  def to_json(self, config: Config, model_data: ModelData) -> str:
    return ',\n'.join(map(lambda chapter: chapter.to_json(config, model_data), self.chapters[:-1]))

ModelElement = Union[Document, Chapter, Section, SectionElement, SubRule]
