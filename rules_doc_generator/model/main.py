import os

from rules_doc_generator.config import (Config)
from rules_doc_generator.model.section import (Document)
from rules_doc_generator.model.model_data import (ModelData, RefDict)

def create_toc_html(model_data: ModelData):
  result = ''
  for id in model_data.id_map:
    ref_info = model_data.id_map[id]
    if ref_info.toc:
      result += f'<li><a href="#{ref_info.id}">{ref_info.reference} {ref_info.text}</a></li>'
  return result

def standalone_html(document: Document, config: Config, model_data: ModelData):
  result = document.to_html(config, model_data)
  return result

def standalone_latex(document: Document, config: Config, model_data: ModelData):
  result = document.to_latex(config, model_data)
  return result

def standalone_json(document: Document, config: Config, model_data: ModelData):
  result = '[\n'
  result += document.to_json(config, model_data)
  result += '\n]'
  return result

def write_to_file(folder: str, filename: str, content: str):
  os.makedirs(folder, exist_ok=True)
  file = open(os.path.join(folder, filename), 'w')
  file.write(content)
  file.close()
