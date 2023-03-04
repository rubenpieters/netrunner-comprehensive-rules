import re
from typing import Any
import yaml

from rules_doc_generator.model.text import (FormatText, TextElement, Ref, Image, Text, Term, Example)
from rules_doc_generator.model.section import (Rule, Section, Header, Document)

def parseTextElement(str: str) -> TextElement:
  if str.startswith('ref:'):
    text = str[4:]
    capitalize = str[4].isupper()
    return Ref(text.lower(), capitalize)
  elif str.startswith('img:'):
    return Image(str[4:])
  elif str.startswith('term:'):
    return Term(str[5:])
  else:
    return Text(str)

def parse_format_text(str: str) -> FormatText:
  split_curly = re.split('[\{\}]', str)
  parsed = list(map(parseTextElement, split_curly))
  return FormatText(parsed)

def parse_example(yaml_example: Any) -> Example:
  text = parse_format_text(yaml_example['text'].rstrip())
  return Example(text)

def parse_rule(yaml_rule: Any, sub_rule: bool = False) -> Rule:
  id = yaml_rule['id']
  text = yaml_rule['text'].rstrip()
  section = False
  if 'section' in yaml_rule:
    section = True
  rules = []
  if 'rules' in yaml_rule:
    rules = list(map(lambda x: parse_rule(x, True), yaml_rule['rules']))
  examples = []
  if 'examples' in yaml_rule:
    examples = list(map(parse_example, yaml_rule['examples']))
  return Rule(id, parse_format_text(text), section, sub_rule, rules, examples)

def parse_section(yaml_section: Any) -> Section:
  id = yaml_section['id']
  text = yaml_section['text']
  snippet = None
  if 'snippet' in yaml_section:
    snippet = parse_format_text(yaml_section['snippet'].rstrip())
  rules = list(map(parse_rule, yaml_section['rules']))
  return Section(id, text, snippet, rules)

def parse_header(yaml_header: Any) -> Header:
  id = yaml_header['id']
  text = yaml_header['text']
  sections = list(map(parse_section, yaml_header['sections']))
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

if __name__ == "__main__":
  doc = yaml_to_document()
  print(doc)