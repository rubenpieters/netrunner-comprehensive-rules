from rules_doc_generator.model.text import (FormatText, TextElement, Ref, Image, Text, Term, Example, SubType, Card, Product, Link)
from rules_doc_generator.model.section import (Rule, SubRule, Section, Chapter, Document, SectionElement, TimingStructureElement)

def text_element_to_latex(text_element: TextElement) -> str:
  match text_element:
    case Image(text): return fr'\includegraphics[height=8pt]{{{text}.png}}'
    case Text(text): return text
    case Term(text): return fr'\textsc{{{text}}}'
    case SubType(text): return fr'\textbf{{{text}}}'
    case Card(text): return fr'\textit{{{text}}}'
    case Product(text): return fr'\textit{{{text}}}'
    case Link(text, link): return fr'\hreful{{{link}}}{{{text}}}'
    case _: raise Exception(f'Unsupported converting {text_element} to latex.')
