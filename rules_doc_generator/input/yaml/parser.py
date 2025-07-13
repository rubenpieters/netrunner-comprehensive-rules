import re
from typing import Any, Callable, TypeVar
import yaml

from rules_doc_generator.config import (Config, default_config)
from rules_doc_generator.model.text import (FormatText, TextElement, Ref, Image, Text, Term, Example, SubType, Card, Product, Link, NewStart, NewEnd)
from rules_doc_generator.model.section import (Rule, SubRule, SubSection, Section, Chapter, Document, SectionElement, TimingStructure, TimingStructureElement)
from rules_doc_generator.model.nrdb_info import (NrdbInfo)

# Parsing model elements.

def parseTextElement(str: str) -> TextElement:
  if str.startswith('ref:'):
    text = str[4:].lower()
    capitalize = str[4].isupper()
    ids = text.split(',')
    return Ref(ids, capitalize, 'and')
  if str.startswith('ref/'):
    text = str[4:].lower()
    combiner_and_ids = re.split(':|,', text)
    combiner = combiner_and_ids[0]
    ids = combiner_and_ids[1:]
    capitalize = ids[0].isupper()
    return Ref(ids, capitalize, combiner)
  elif str.startswith('img:'):
    return Image(str[4:])
  elif str.startswith('term:'):
    return Term(str[5:])
  elif str.startswith('subtype:'):
    return SubType(str[8:])
  elif str.startswith('card:'):
    return Card(str[5:])
  elif str.startswith('product:'):
    return Product(str[8:])
  elif str.startswith('link:'):
    full_text = str[5:].lower()
    text_and_link = full_text.split('|')
    text = text_and_link[0]
    link = text_and_link[1]
    return Link(text, link)
  elif str.startswith('curly:'):
    return Text(f'{{{str[6:]}}}')
  elif str == '/n':
    return NewEnd()
  elif str == 'n':
    return NewStart()
  else:
    return Text(str)

def parse_format_text(str: str) -> FormatText:
  str = str.replace('[c]', '{img:credit}')
  str = str.replace('[click]', '{img:click}')
  str = str.replace('[recurring]', '{img:recurring}')
  str = str.replace('[link]', '{img:link}')
  str = str.replace('[MU]', '{img:mu}')
  str = str.replace('[sub]', '{img:sub}')
  str = str.replace('[trash]', '{img:trash}')
  str = str.replace('[interrupt]', '{img:interrupt}')
  str = str.replace('[trashcost]', '{img:trashcost}')
  split_curly = re.split('[\{\}]', str)
  parsed = list(map(parseTextElement, split_curly))
  return FormatText(parsed)

def parse_example(yaml_example: Any) -> Example:
  text = parse_format_text_field(yaml_example, 'text')
  new = parse_boolean(yaml_example, 'new')
  return Example(text, new)

def parse_timing_structure_element(yaml_timing_structure_element: Any) -> TimingStructureElement:
  text = parse_format_text_field(yaml_timing_structure_element, 'text')
  elements = parse_subelements(yaml_timing_structure_element, 'elements', parse_timing_structure_element)
  new = parse_boolean(yaml_timing_structure_element, 'new')
  return TimingStructureElement(text, elements, new)

def parse_timing_structure(yaml_timing_structure: Any) -> TimingStructure:
  bold = parse_boolean(yaml_timing_structure, 'bold')
  elements = parse_subelements(yaml_timing_structure, 'elements', parse_timing_structure_element)
  return TimingStructure(bold, elements)

def parse_subrule(yaml_sub_rule: Any = False) -> SubRule:
  id = parse_id(yaml_sub_rule, 'rule')
  new = parse_boolean(yaml_sub_rule, 'new')
  text = parse_format_text_field(yaml_sub_rule, 'text')
  examples = parse_subelements(yaml_sub_rule, 'examples', parse_example)
  return SubRule(id, new, text, examples)

def parse_rule(yaml_rule: Any) -> Rule:
  id = parse_id(yaml_rule, 'rule')
  new = parse_boolean(yaml_rule, 'new')
  text = parse_format_text_field(yaml_rule, 'text')
  examples = parse_subelements(yaml_rule, 'examples', parse_example)
  return Rule(id, new, text, examples)

def parse_subsection(yaml_rule: Any) -> SubSection:
  id = parse_id(yaml_rule, 'subsection')
  new = parse_boolean(yaml_rule, 'new')
  toc = parse_boolean(yaml_rule, 'toc')
  steps = parse_boolean(yaml_rule, 'steps')
  text = parse_format_text_field(yaml_rule, 'text')
  snippet = parse_with_default(yaml_rule, 'snippet', None, parse_format_text_field)
  examples = parse_subelements(yaml_rule, 'examples', parse_example)
  rules = parse_subelements(yaml_rule, 'rules', parse_subrule)
  return SubSection(id, new, text, toc, steps, snippet, examples, rules)

def parse_section_element(yaml_section_element: Any) -> SectionElement:
  funcs: list[Callable[[Any], SectionElement]] = [parse_rule, parse_timing_structure, parse_subsection]
  return parse_union(
    yaml_section_element,
    ['rule', 'timing_structure', 'subsection'],
    funcs
  )

def parse_section(yaml_section: Any) -> Section:
  id = parse_id(yaml_section, 'section')
  new = parse_boolean(yaml_section, 'new')
  text = parse_format_text_field(yaml_section, 'text')
  toc_entry = parse_with_default(yaml_section, 'toc_entry', None, parse_str_field)
  steps = parse_boolean(yaml_section, 'steps')
  snippet = parse_with_default(yaml_section, 'snippet', None, parse_format_text_field)
  section_elements = parse_subelements(yaml_section, 'rules', parse_section_element)
  return Section(id, new, text, toc_entry, steps, snippet, section_elements)

def parse_chapter(yaml_chapter: Any) -> Chapter:
  id = parse_id(yaml_chapter, 'chapter')
  new = parse_boolean(yaml_chapter, 'new')
  text = parse_str_field(yaml_chapter, 'text')
  sections = parse_subelements(yaml_chapter, 'sections', parse_section)
  return Chapter(id, new, text, sections)

def parse_changelog_entry(yaml_changelog_entry: Any) -> FormatText:
  text = parse_format_text_field(yaml_changelog_entry, 'text')
  return text

def parse_changelog(yaml_changelog: Any) -> list[FormatText]:
  changelog = parse_subelements(yaml_changelog, 'changelog', parse_changelog_entry)
  return changelog

# Utility methods for parsing fields from the YAML dicts.

A = TypeVar('A')
B = TypeVar('B')

def parse_id(obj: Any, id_type: str) -> str:
  if not id_type in obj:
    raise Exception(f'Expected id type: {id_type}, instead got fields: {str(obj.keys())}')
  id = obj[id_type]
  if id is None or id.strip() == '':
    raise Exception(f'Empty id of type {id_type}')
  return id

def parse_str_field(obj: Any, field_type: str) -> str:
  return parse_str_field_generic(obj, field_type, lambda x: x)

def parse_format_text_field(obj: Any, field_type: str) -> FormatText:
  return parse_str_field_generic(obj, field_type, parse_format_text)

def parse_str_field_generic(obj: Any, field_type: str, func: Callable[[str], A]) -> A:
  if not field_type in obj:
    raise Exception(f'Expected field: {field_type}, instead got fields: {str(obj.keys())}')
  field_content = obj[field_type]
  if not isinstance(field_content, str):
    raise Exception(f'Expected str field for {field_type}, instead got: {type(field_content)}')
  return func(field_content.rstrip())

def parse_subelements(obj: Any, element_type: str, func: Callable[[Any], A]) -> list[A]:
  if not element_type in obj:
    return []
  return list(map(func, obj[element_type]))

def parse_union(obj: Any, element_types: list[str], funcs: list[Callable[[Any], A]]) -> A:
  for i, element_type in enumerate(element_types):
    if element_type in obj:
      return funcs[i](obj)
  raise Exception(f'None of the expected fields found: {str(element_types)}, instead got fields: {str(obj.keys())}')

def parse_boolean(obj: Any, field_type: str) -> bool:
  if field_type in obj:
    return True
  return False

def parse_int(obj: Any, field_type: str) -> int:
  return parse_with_default(obj, field_type, -1, lambda x: int(x))

def parse_with_default(obj: Any, field_type: str, default: A, parse_func: Callable[[Any, str], A]) -> A:
  if not field_type in obj:
    return default
  return parse_func(obj, field_type)

# General utility.

def read_changelog_from_file(config: Config) -> list[FormatText]:
  print(f"Parsing changelog")
  with open(f'data/changelogs/{config.version_string()}.yaml', "r", encoding="utf8") as stream:
    yaml_input = load_yaml(stream)
    return parse_changelog(yaml_input)

def read_chapter_from_file(section_file: str) -> Chapter:
  print(f"Parsing {section_file}")
  with open(f'data/input/{section_file}.yaml', "r", encoding="utf8") as stream:
    yaml_input = load_yaml(stream)
    return parse_chapter(yaml_input)

def load_yaml(stream):
  try:
    return yaml.load(stream, yaml.SafeLoader)

  except yaml.YAMLError as exc:
      print ("Error while parsing YAML file:")
      if hasattr(exc, 'problem_mark'):
          if exc.context != None:
              print ('  parser says\n' + str(exc.problem_mark) + '\n  ' +
                  str(exc.problem) + ' ' + str(exc.context) +
                  '\nPlease correct data and retry.')
          else:
              print ('  parser says\n' + str(exc.problem_mark) + '\n  ' +
                  str(exc.problem) + '\nPlease correct data and retry.')
      else:
          print ("Something went wrong while parsing yaml file")
      exit()

def yaml_to_document(config: Config) -> Document:
  changelog = read_changelog_from_file(config)
  chapter_files = \
    [ "01_game_concepts"
    , "02_parts_of_a_card"
    , "03_card_types"
    , "04_game_zones"
    , "05_turns"
    , "06_runs"
    , "07_access_breach"
    , "08_card_manipulation"
    , "09_abilities"
    , "10_additional_rules"
    , "11_appendix_timing_structures"
    ]
  chapters = list(map(read_chapter_from_file, chapter_files))
  return Document(changelog, chapters)

def read_nrdb_info_from_file() -> dict[str, str]:
  with open(f'generated/nrdb/nrdb.yaml', "r", encoding="utf8") as stream:
    nrdb_info = load_yaml(stream)
    return nrdb_info

if __name__ == "__main__":
  doc = yaml_to_document(default_config)
  print(doc)
