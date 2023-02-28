import re
from typing import Any
import yaml

from rules_doc_generator.model.text import (FormatText, TextElement, Ref, Image, Text, Term)
from rules_doc_generator.model.section import (Rule)

def parseTextElement(str: str) -> TextElement:
  if str.startswith('ref:'):
    return Ref(str[4:])
  elif str.startswith('img:'):
    return Image(str[4:])
  elif str.startswith('term:'):
    return Term(str[5:])
  else:
    return Text(str)

def parseFormatText(str: str) -> FormatText:
  splitCurly = re.split('[\{\}]', str)
  parsed = map(parseTextElement, splitCurly)
  return FormatText(list(parsed))

def parseRule(yaml_rule: Any) -> Rule:
  id = yaml_rule['id']
  text = yaml_rule['text'].rstrip()
  return Rule(id, parseFormatText(text), [], [])

if __name__ == "__main__":
  with open("data/input/rules.yaml", "r") as stream:
    try:
      obj = yaml.safe_load(stream)

      for section in obj:
        print('section ' + section['id'] + ' - ' + section['name'])
        for subsection in section['sections']:
          print('subsection ' + subsection['id'] + ' - ' + subsection['name'])
          for rule in subsection['rules']:
            print(parseRule(rule))
    except yaml.YAMLError as exc:
      print(exc)
