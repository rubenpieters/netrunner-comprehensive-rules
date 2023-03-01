from rules_doc_generator.model.main import standalone_html, standalone_latex, write_to_file
from rules_doc_generator.input.yaml.parser import yaml_to_document

document = yaml_to_document()
id_map = document.id_map()
write_to_file('html', 'demo.html', standalone_html(document, id_map))
write_to_file('latex', 'demo.tex', standalone_latex(document, id_map))
