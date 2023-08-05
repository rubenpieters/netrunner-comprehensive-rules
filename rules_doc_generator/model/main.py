import os

from rules_doc_generator.config import (Config)
from rules_doc_generator.model.text import (RefDict)
from rules_doc_generator.model.section import (Document)

def create_toc_html(id_map: RefDict):
  result = ''
  for id in id_map:
    ref_info = id_map[id]
    if ref_info.toc:
      result += f'<li>{ref_info.reference} {ref_info.text}</li>'
  return result

def standalone_html(document: Document, config: Config, id_map: RefDict):
  result = '<!DOCTYPE html><html><head><link rel="stylesheet" href="demo.css"></head><body>'
  result += '<div class="RulesGrid">'
  result += f'<ul class="RulesToc">{create_toc_html(id_map)}</ul>'
  result += f'<div class="RulesContent">{document.to_html(config, id_map)}</div>'
  result += '</div>'
  result += '</body></html>'
  return result

def standalone_latex(document: Document, config: Config, id_map: RefDict):
  result = document.to_latex(config, id_map)
  return result

def write_to_file(folder: str, filename: str, content: str):
  os.makedirs(folder, exist_ok=True)
  file = open(os.path.join(folder, filename), 'w')
  file.write(content)
  file.close()
