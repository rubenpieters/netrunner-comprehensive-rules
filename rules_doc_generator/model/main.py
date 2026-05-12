import os

from rules_doc_generator.config import (Config)
from rules_doc_generator.model.section import (Document)
from rules_doc_generator.model.model_data import (ModelData)

def standalone_html(document: Document, config: Config, model_data: ModelData):
  result = document.to_html(config, model_data)
  return result

def standalone_latex(document: Document, config: Config, model_data: ModelData):
  result = document.to_latex(config, model_data)
  return result

def standalone_json(document: Document, config: Config, model_data: ModelData):
  preamble_text = f'This rules document is to be used as reference material. It is not intended to be read straight through. This version of the Comprehensive Rules document is effective {config.effective_date_str()}.'
  preamble = f'{{"id": "preamble", "nr": "0", "type": "preamble", "text": "{preamble_text}"}}'
  result = '[\n'
  result += preamble + ',\n'
  result += document.to_json(config, model_data)
  result += '\n]'
  return result

def write_to_file(folder: str, filename: str, content: str):
  os.makedirs(folder, exist_ok=True)
  file = open(os.path.join(folder, filename), 'w')
  file.write(content)
  file.close()
