import re
from typing import Any, Callable, TypeVar
import yaml

from rules_doc_generator.model.text import (FormatText, TextElement, Ref, Image, Text, Term, Example, SubType, Card)
from rules_doc_generator.model.section import (Rule, SubRule, Section, Header, Document, SectionElement, TimingStructureElement)

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
  text = None
  if 'text' in yaml_timing_structure:
    text = parse_format_text(yaml_timing_structure['text'])
  elements = parse_subelements(yaml_timing_structure, 'elements', parse_timing_structure)
  return TimingStructureElement(text, elements)

def parse_sub_rule(yaml_sub_rule: Any = False) -> SubRule:
  id = parse_id(yaml_sub_rule, 'sub_rule')
  text = parse_format_text_field(yaml_sub_rule, 'text')
  examples = parse_subelements(yaml_sub_rule, 'examples', parse_example)
  return SubRule(id, text, examples)

def parse_rule(yaml_rule: Any) -> Rule:
  id = parse_id(yaml_rule, 'rule')
  toc = parse_boolean(yaml_rule, 'toc')
  steps = parse_boolean(yaml_rule, 'steps')
  text = parse_format_text_field(yaml_rule, 'text')
  rules = parse_subelements(yaml_rule, 'rules', parse_sub_rule)
  examples = parse_subelements(yaml_rule, 'examples', parse_example)
  return Rule(id, text, toc, steps, rules, examples)

def parse_section_element(yaml_section_element: Any) -> SectionElement:
  return parse_union(
    yaml_section_element,
    ['rule', 'timing_structure'],
    [parse_rule, parse_timing_structure]
  )

def parse_section(yaml_section: Any) -> Section:
  id = parse_id(yaml_section, 'section')
  text = parse_format_text_field(yaml_section, 'text')
  toc_entry = parse_with_default(yaml_section, 'toc_entry', None, parse_str_field)
  snippet = parse_with_default(yaml_section, 'snippet', None, parse_format_text_field)
  section_elements = parse_subelements(yaml_section, 'rules', parse_section_element)
  return Section(id, text, toc_entry, snippet, section_elements)

def parse_header(yaml_header: Any) -> Header:
  id = parse_id(yaml_header, 'header')
  text = parse_str_field(yaml_header, 'text')
  sections = parse_subelements(yaml_header, 'sections', parse_section)
  return Header(id, text, sections)

def parse_document(yaml_document: Any) -> Document:
  headers = list(map(parse_header, yaml_document))
  return Document(headers)

def yaml_to_document():
  with open("data/input/rules.yaml", "r") as stream:
    try:
      yaml_input = yaml.safe_load(stream)
      return parse_document(yaml_input)
    except yaml.YAMLError as exc:
      print(exc)

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

if __name__ == "__main__":
  doc = yaml_to_document()
  print(doc)
