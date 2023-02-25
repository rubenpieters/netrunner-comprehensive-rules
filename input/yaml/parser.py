import yaml

with open("data/input/rules.yaml", "r") as stream:
  try:
    obj = yaml.safe_load(stream)

    for section in obj:
      print('section ' + section['id'] + ' - ' + section['name'])
      for subsection in section['sections']:
        print('subsection ' + subsection['id'] + ' - ' + subsection['name'])
        for rule in subsection['rules']:
          print('rule ' + rule['id'] + ' - ' + rule['text'].rstrip())
  except yaml.YAMLError as exc:
    print(exc)
