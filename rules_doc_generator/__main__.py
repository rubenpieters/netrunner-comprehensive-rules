import os
import shutil

from rules_doc_generator.model.main import standalone_html, standalone_latex, write_to_file
from rules_doc_generator.input.yaml.parser import yaml_to_document
from rules_doc_generator.model.analysis.references import construct_reference_map

print("Parsing...")
document = yaml_to_document()
print("Constructing Model...")
ref_dict = construct_reference_map(document)
print("Writing Output...")
write_to_file('html', 'demo.html', standalone_html(document, ref_dict))
write_to_file('latex', 'demo.tex', standalone_latex(document, ref_dict))
print("Ready!")

shutil.copyfile(os.path.join('data', 'images', 'credit.svg'), os.path.join('html', 'credit.svg'))
shutil.copyfile(os.path.join('data', 'templates', 'html', 'demo.css'), os.path.join('html', 'demo.css'))