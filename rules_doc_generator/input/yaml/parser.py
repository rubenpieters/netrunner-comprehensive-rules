import re
from typing import Any, Callable, TypeVar
import yaml

from rules_doc_generator.model.text import (FormatText, TextElement, Ref, Image, Text, Term, Example, SubType, Card, Product, Link)
from rules_doc_generator.model.section import (Rule, SubRule, SubSection, Section, Chapter, Document, SectionElement, TimingStructureElement)

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
  else:
    return Text(str)

def parse_format_text(str: str) -> FormatText:
  split_curly = re.split('[\{\}]', str)
  parsed = list(map(parseTextElement, split_curly))
  return FormatText(parsed)

def parse_example(yaml_example: Any) -> Example:
  text = parse_format_text_field(yaml_example, 'text')
  return Example(text)

def parse_timing_structure(yaml_timing_structure: Any) -> TimingStructureElement:
  text = parse_with_default(yaml_timing_structure, 'text', None, parse_format_text_field)
  elements = parse_subelements(yaml_timing_structure, 'elements', parse_timing_structure)
  return TimingStructureElement(text, elements)

def parse_subrule(yaml_sub_rule: Any = False) -> SubRule:
  id = parse_id(yaml_sub_rule, 'rule')
  text = parse_format_text_field(yaml_sub_rule, 'text')
  examples = parse_subelements(yaml_sub_rule, 'examples', parse_example)
  return SubRule(id, text, examples)

def parse_rule(yaml_rule: Any) -> Rule:
  id = parse_id(yaml_rule, 'rule')
  toc = parse_boolean(yaml_rule, 'toc')
  text = parse_format_text_field(yaml_rule, 'text')
  examples = parse_subelements(yaml_rule, 'examples', parse_example)
  return Rule(id, text, toc, examples)

def parse_subsection(yaml_rule: Any) -> SubSection:
  id = parse_id(yaml_rule, 'subsection')
  toc = parse_boolean(yaml_rule, 'toc')
  steps = parse_boolean(yaml_rule, 'steps')
  text = parse_format_text_field(yaml_rule, 'text')
  rules = parse_subelements(yaml_rule, 'rules', parse_subrule)
  return SubSection(id, text, toc, steps, rules)

def parse_section_element(yaml_section_element: Any) -> SectionElement:
  funcs: list[Callable[[Any], SectionElement]] = [parse_rule, parse_timing_structure, parse_subsection]
  return parse_union(
    yaml_section_element,
    ['rule', 'timing_structure', 'subsection'],
    funcs
  )

def parse_section(yaml_section: Any) -> Section:
  id = parse_id(yaml_section, 'section')
  text = parse_format_text_field(yaml_section, 'text')
  toc_entry = parse_with_default(yaml_section, 'toc_entry', None, parse_str_field)
  snippet = parse_with_default(yaml_section, 'snippet', None, parse_format_text_field)
  section_elements = parse_subelements(yaml_section, 'rules', parse_section_element)
  return Section(id, text, toc_entry, snippet, section_elements)

def parse_chapter(yaml_chapter: Any) -> Chapter:
  id = parse_id(yaml_chapter, 'chapter')
  text = parse_str_field(yaml_chapter, 'text')
  sections = parse_subelements(yaml_chapter, 'sections', parse_section)
  return Chapter(id, text, sections)

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
  return obj[id_type]

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

def parse_with_default(obj: Any, field_type: str, default: A, parse_func: Callable[[Any, str], A]) -> A:
  if not field_type in obj:
    return default
  return parse_func(obj, field_type)

# General utility.

def read_changelog_from_file() -> list[FormatText]:
  with open(f'data/input/00_changelog.yaml', "r") as stream:
    yaml_input = yaml.safe_load(stream)
    return parse_changelog(yaml_input)

def read_chapter_from_file(section_file: str) -> Chapter:
  with open(f'data/input/{section_file}.yaml', "r") as stream:
    yaml_input = yaml.safe_load(stream)
    return parse_chapter(yaml_input)

def yaml_to_document() -> Document:
  changelog = read_changelog_from_file()
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

if __name__ == "__main__":
  doc = yaml_to_document()
  print(doc)
