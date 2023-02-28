import re
import yaml

from rules_doc_generator.model.text import (FormatText, TextElement, Ref, Image, Text, Term)

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
  splitCurly = re.split('[\{\}]', rule['text'])
  parsed = map(parseTextElement, splitCurly)
  return FormatText(list(parsed))

if __name__ == "__main__":
  with open("data/input/rules.yaml", "r") as stream:
    try:
      obj = yaml.safe_load(stream)

      for section in obj:
        print('section ' + section['id'] + ' - ' + section['name'])
        for subsection in section['sections']:
          print('subsection ' + subsection['id'] + ' - ' + subsection['name'])
          for rule in subsection['rules']:
            text = rule['text'].rstrip()
            print('rule ' + rule['id'] + ' - ' + text)
            print(parseFormatText(text))
    except yaml.YAMLError as exc:
      print(exc)
