from argparse import ArgumentParser
from dataclasses import replace
import os
import shutil
import yaml

from rules_doc_generator.config import Config, parse_output_types, validate_nrdb_info_folder, default_config
from rules_doc_generator.model.main import standalone_html, standalone_latex, standalone_json, write_to_file
from rules_doc_generator.input.yaml.parser import yaml_to_document, read_nrdb_info_from_file
from rules_doc_generator.model.analysis.references import construct_reference_map
from rules_doc_generator.model.model_data import ModelData
from rules_doc_generator.input.json.parser import generate_nrdb_info

config = default_config

# Parse config file.
with open('config.yaml') as f:
  yaml_config = yaml.safe_load(f)
 
  if yaml_config["annotated"] is not None:
    config = replace(config, annotated=yaml_config["annotated"])
  if yaml_config["output_types"] is not None:
    config = replace(config, output_types=parse_output_types(yaml_config["output_types"]))
  if yaml_config["date"] is not None:
    config = replace(config, effective_year=str(yaml_config["date"]["year"]), effective_month=str(yaml_config["date"]["month"]), effective_day=str(yaml_config["date"]["day"]))

# Parse command line arguments.
parser = ArgumentParser()
parser.add_argument("-a", "--annotated", const=True, help="Also generate annotated version with highlights of new parts", action="store_const")
parser.add_argument("-y", "--year", help="Effective year", action="store")
parser.add_argument("-m", "--month", help="Effective month", action="store")
parser.add_argument("-d", "--day", help="Effective day", action="store")
parser.add_argument("-b", "--php-base-path", help="Basepath of php server", action="store")
parser.add_argument("-t", "--output-types", help="Output types", nargs="*", action="store")
parser.add_argument("-n", "--nrdb-info-folder", type=validate_nrdb_info_folder, help="Folder to generate the NRDB info file from", action="store")
args = parser.parse_args()
if args.annotated is not None:
  config = replace(config, annotated=args.annotated)
if args.nrdb_info_folder is not None:
  config = replace(config, generate_nrdb_info=True, nrdb_info_folder=args.nrdb_info_folder)
if args.year is not None and args.month is not None and args.day is not None:
  config = replace(config, effective_year=args.year, effective_month=args.month, effective_day=args.day)
if args.php_base_path is not None:
  config = replace(config, php_base_path=args.php_base_path)
if args.output_types is not None:
  config = replace(config, php_base_path=parse_output_types(args.output_types))

not_annotated_config = replace(config, annotated=False)

print("- Config -")
print("- Version String: " + str(config.version_string()))
print("- Effective Date: " + str(config.effective_date_str()))
print("- Annotated: " + str(config.annotated))
print("- Output Types: " + str(config.output_types))
print("- Generate NRDB Info: " + str(config.nrdb_info_folder))

if config.generate_nrdb_info:
  print(f"Generating NRDB Info From {config.nrdb_info_folder}...")
  generate_nrdb_info(config.nrdb_info_folder)

print("Parsing...")
document = yaml_to_document()

print("Parsing NRDB Info File...")
nrdb_info = read_nrdb_info_from_file()

print("Constructing Model...")
ref_dict = construct_reference_map(document)

model_data = ModelData(ref_dict, nrdb_info)

print("Writing Output...")
# PDF Version Output
if "pdf" in config.output_types:
  if os.path.exists('latex'):
    shutil.rmtree('latex')
  write_to_file('latex', f"Null_Signal_Games_Netrunner_Comprehensive_Rules_v{config.version_string()}.tex", standalone_latex(document, not_annotated_config, model_data))
  if config.annotated:
    if os.path.exists('latex_annotated'):
      shutil.rmtree('latex_annotated')
    write_to_file('latex_annotated', f"Null_Signal_Games_Netrunner_Comprehensive_Rules_v{config.version_string()}_Annotated.tex", standalone_latex(document, config, model_data))

# Web Version Output
if "web" in config.output_types:
  if os.path.exists('html'):
    shutil.rmtree('html')
  write_to_file('html', 'rules.html', standalone_html(document, config, model_data))
  shutil.copyfile(os.path.join('data', 'images', 'credit.svg'), os.path.join('html', 'credit.svg'))
  shutil.copyfile(os.path.join('data', 'images', 'preview_placeholder.jpg'), os.path.join('html', 'preview_placeholder.jpg'))
  shutil.copyfile(os.path.join('data', 'templates', 'html', 'rules.js'), os.path.join('html', 'rules.js'))
  shutil.copyfile(os.path.join('data', 'templates', 'html', 'rules.css'), os.path.join('html', 'rules.css'))
  shutil.copyfile(os.path.join('data', 'templates', 'html', 'extended.css'), os.path.join('html', 'extended.css'))

# Opengraph Web Version Output
if "opengraph" in config.output_types:
  if os.path.exists('php'):
    shutil.rmtree('php')
  write_to_file('php', 'rules.html', standalone_html(document, config, model_data))
  write_to_file('php', 'rules.json', standalone_json(document, config, model_data))
  shutil.copyfile(os.path.join('data', 'images', 'credit.svg'), os.path.join('php', 'credit.svg'))
  shutil.copyfile(os.path.join('data', 'images', 'preview_placeholder.jpg'), os.path.join('php', 'preview_placeholder.jpg'))
  shutil.copyfile(os.path.join('data', 'templates', 'html', 'rules.js'), os.path.join('php', 'rules.js'))
  shutil.copyfile(os.path.join('data', 'templates', 'html', 'rules.css'), os.path.join('php', 'rules.css'))
  shutil.copyfile(os.path.join('data', 'templates', 'html', 'extended.css'), os.path.join('php', 'extended.css'))
  shutil.copyfile(os.path.join('data', 'templates', 'php', 'index.php'), os.path.join('php', 'index.php'))
  shutil.copyfile(os.path.join('data', 'templates', 'php', 'logo.png'), os.path.join('php', 'logo.png'))
  phpConfigFile = "<?php\n$CONFIG = array (\n"
  phpConfigFile += f"  'base_path' => '{config.php_base_path}',\n"
  phpConfigFile += ");\n?>\n"
  write_to_file('php', 'config.php', phpConfigFile)

# Json Output
if "json" in config.output_types:
  if os.path.exists('json'):
    shutil.rmtree('json')
  write_to_file('json', 'rules.json', standalone_json(document, not_annotated_config, model_data))

print("Ready!")
