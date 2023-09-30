from argparse import ArgumentParser
import os
import shutil

from rules_doc_generator.config import Config
from rules_doc_generator.model.main import standalone_html, standalone_latex, standalone_json, write_to_file
from rules_doc_generator.input.yaml.parser import yaml_to_document
from rules_doc_generator.model.analysis.references import construct_reference_map

# Parse command line arguments.
parser = ArgumentParser()
parser.add_argument("-a", "--annotated", default=False, help="Also generate annotated version with highlights of new parts", action="store_true")
parser.add_argument("-y", "--year", default="2023", help="Effective year", action="store")
parser.add_argument("-m", "--month", default="XX", help="Effective month", action="store")
parser.add_argument("-d", "--day", default="XX", help="Effective day", action="store")
parser.add_argument("-p", "--generate-php", default=False, help="Generate php output", action="store_true")
parser.add_argument("-b", "--php-base-path", default="https://example.org/", help="Basepath of php server", action="store")
args = parser.parse_args()
config = Config(args.annotated, args.year, args.month, args.day, args.generate_php, args.php_base_path)

print("- Config -")
print("- Annotated: " + str(config.annotated))

print("Parsing...")
document = yaml_to_document()
print("Constructing Model...")
ref_dict = construct_reference_map(document)
print("Writing Output...")
write_to_file('html', 'rules.html', standalone_html(document, config.not_php(), ref_dict))
if config.annotated:
  write_to_file('latex_annotated', 'rules_annotated.tex', standalone_latex(document, config, ref_dict))
write_to_file('latex', 'rules.tex', standalone_latex(document, config.not_annotated(), ref_dict))
write_to_file('json', 'rules.json', standalone_json(document, config.not_annotated(), ref_dict))
print("Ready!")

shutil.copyfile(os.path.join('data', 'images', 'credit.svg'), os.path.join('html', 'credit.svg'))
shutil.copyfile(os.path.join('data', 'templates', 'html', 'rules.css'), os.path.join('html', 'rules.css'))

# Files for php server
if config.generate_php:
  write_to_file('php', 'rules.html', standalone_html(document, config, ref_dict))
  write_to_file('php', 'rules.json', standalone_json(document, config, ref_dict))
  shutil.copyfile(os.path.join('data', 'images', 'credit.svg'), os.path.join('php', 'credit.svg'))
  shutil.copyfile(os.path.join('data', 'templates', 'html', 'rules.css'), os.path.join('php', 'rules.css'))
  shutil.copyfile(os.path.join('data', 'templates', 'php', 'extended.css'), os.path.join('php', 'extended.css'))
  shutil.copyfile(os.path.join('data', 'templates', 'php', 'rules.js'), os.path.join('php', 'rules.js'))
  shutil.copyfile(os.path.join('data', 'templates', 'php', 'index.php'), os.path.join('php', 'index.php'))
  shutil.copyfile(os.path.join('data', 'templates', 'php', 'logo.png'), os.path.join('php', 'logo.png'))
  phpConfigFile = "<?php\n$CONFIG = array (\n"
  phpConfigFile += f"  'base_path' => '{config.php_base_path}',\n"
  phpConfigFile += ");\n?>\n"
  write_to_file('php', 'config.php', phpConfigFile)