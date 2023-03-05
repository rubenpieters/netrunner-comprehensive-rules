import os
import shutil

from rules_doc_generator.model.main import standalone_html, standalone_latex, write_to_file
from rules_doc_generator.input.yaml.parser import yaml_to_document

document = yaml_to_document()
id_map = document.id_map()
write_to_file('html', 'demo.html', standalone_html(document, id_map))
write_to_file('latex', 'demo.tex', standalone_latex(document, id_map))

shutil.copyfile(os.path.join('data', 'images', 'credit.svg'), os.path.join('html', 'credit.svg'))
shutil.copyfile(os.path.join('data', 'templates', 'html', 'demo.css'), os.path.join('html', 'demo.css'))