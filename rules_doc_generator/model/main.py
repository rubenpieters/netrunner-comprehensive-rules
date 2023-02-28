import os

from rules_doc_generator.model.text import (RefDict, Text, Ref, Term, FormatText, Example, Image)
from rules_doc_generator.model.section import (Rule, Section, Header, Document)

def create_toc_html(id_map: RefDict):
  result = ''
  for id in id_map:
    ref_info = id_map[id]
    if not (ref_info.type == 'rule' or ref_info.type == 'subrule'):
      result += f'<div>{ref_info.reference} {ref_info.text}</div>'
  return result

def standalone_html(document: Document, id_map: RefDict):
  result = '<!DOCTYPE html><html><head><link rel="stylesheet" href="demo.css"></head><body>'
  result += f'<div>{create_toc_html(id_map)}</div>'
  result += f'<div>{document.to_html(id_map)}</div>'
  result += '</body></html>'
  return result

def standalone_latex(document: Document, id_map: RefDict):
  result = document.to_latex(id_map)
  return result

def write_to_file(folder: str, filename: str, content: str):
  os.makedirs(folder, exist_ok=True)
  file = open(os.path.join(folder, filename), 'w')
  file.write(content)
  file.close()
