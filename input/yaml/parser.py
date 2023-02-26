import re
import yaml

def parseFormatText(str):
  result = re.split('[\{\}]', rule['text'])
  print(result)

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
          parseFormatText(text)
  except yaml.YAMLError as exc:
    print(exc)
