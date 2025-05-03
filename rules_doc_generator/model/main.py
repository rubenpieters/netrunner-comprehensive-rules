import os

from rules_doc_generator.config import (Config)
from rules_doc_generator.model.section import (Document)
from rules_doc_generator.model.model_data import (ModelData, RefDict)

def create_toc_html(model_data: ModelData):
  result = ''
  for id in model_data.id_map:
    ref_info = model_data.id_map[id]
    if ref_info.toc:
      result += f'<li><a href="#{ref_info.id}">{ref_info.reference} {ref_info.text}</a></li>'
  return result

def standalone_html(document: Document, config: Config, model_data: ModelData, opengraph: bool):
  result = '<?xml encoding="utf-8" ?><!DOCTYPE html><html><head>'
  result += '<meta name="viewport" content="width=device-width, initial-scale=1">'
  result += '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible">'
  result += '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />'
  result += '<link rel="stylesheet" href="rules.css">'
  result += '<link rel="stylesheet" href="extended.css">'
  result += f'<title>Netrunner Comprehensive Rules (v{config.version_string()})</title>'
  result += '<script src="rules.js" defer></script>'
  result += '<script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>'
  result += '</head><body>'
  result += '<div id="RulesParent">'
  result += '<div id="RulesToc" class="RulesToc">'
  result += """
  <div id="TocHeader">
    <div id="TocTitle">Table of Contents</div>
    <div id="TocClose" class="TocClose" onClick="closeToc()">×</div>
  </div>
  """
  result += f'<nav><ul class="RulesTocList">{create_toc_html(model_data)}</ul></nav>'
  result += '</div>'
  result += f'<div id="TocOpen" class="TocOpen noprint" onClick="openToc()"><b>☰ Table of Contents</b></div>'
  result += f'<div id="RulesContent" class="RulesContent">'
  result += '<div>'
  result += f'<p class="Title">Netrunner Comprehensive Rules</p>'
  result += f'<p class="SubTitle">Null Signal Games</p>'
  result += f'<p>This rules document is to be used as reference material. It is not intended to be read straight through. If you still have questions after consulting this document, please ask us online via <a href="mailto:rules@nullsignal.games">email</a>. This version of the Comprehensive Rules document is effective <b>{config.effective_date_str()}</b>.</p>'
  result += f'<details><summary class="Clickable"><b>Summary of Changes (v{config.version_string()})</b></summary><ul>'
  for changelog_entry in document.changelog:
    result += f'<li>{changelog_entry.to_html(config, model_data)}</li>'
  result += '</ul></details>'
  result += '<details><summary class="Clickable"><b>Acknowledgements</b></summary>'
  result += '<ul>'
  result += '<li>Netrunner Original Game Design: Richard Garfield</li>'
  result += '<li>Android: Netrunner'
  result += '<ul>'
  result += '<li>Game Development: Lukas Litzsinger</li>'
  result += '<li>Expansion Development: Lukas Litzsinger, Damon Stone, and Michael Boggs</li>'
  result += '<li>Rules by: Adam Baker, Michael Boggs, and Erik Dahlman</li>'
  result += '<li>Android Universe created by: Kevin Wilson with Daniel Lovat Clark</li>'
  result += '</ul>'
  result += '</li>'
  result += '<li>Null Signal Games'
  result += '<ul>'
  result += '<li>Rules Manager: Jamie Perconti</li>'
  result += '<li>Rules Associates: Ruben P. Pieters and Justin Prentice</li>'
  result += '<li>Rules Editors: Jonny Foster</li>'
  result += '<li>Additional Contributions: Kayli Ammen, Noah Bogart, Pat Chapman, Tim Vaduva, and Olive Wesley</li>'
  result += '</ul>'
  result += '</li>'
  result += '<li>Github Repository Contributions: lostgeek, plural, and qwitwa</li>'
  result += '</ul>'
  result += '<p>Netrunner is a ™ of R. Talsorian Games, Inc. Android is ™ & © Fantasy Flight Games. Although these rules are made to be compatible with cards from Android: Netrunner, they are not in any way associated with or endorsed by Fantasy Flight Games, R. Talsorian Games, or Wizards of the Coast.</p>'
  result += '</details>'
  result += '</div>'
  result += document.to_html(config, model_data)
  result += '</div>'
  result += '</div>'
  result += '</body></html>'
  return result

def standalone_latex(document: Document, config: Config, model_data: ModelData):
  result = document.to_latex(config, model_data)
  return result

def standalone_json(document: Document, config: Config, model_data: ModelData):
  result = '[\n'
  result += document.to_json(config, model_data)
  result += '\n]'
  return result

def write_to_file(folder: str, filename: str, content: str):
  os.makedirs(folder, exist_ok=True)
  file = open(os.path.join(folder, filename), 'w')
  file.write(content)
  file.close()
