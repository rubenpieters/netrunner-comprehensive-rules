from rules_doc_generator.model.model_data import (RefInfo)
from rules_doc_generator.model.section import (ModelElement, Document, Chapter, Section, SubSection, Rule, SubRule, TimingStructureElement)

import string
from typing import Optional

RefMap = dict[str, RefInfo]

def check_id_defined(ref_map: RefMap, id: str):
  if id in ref_map:
    raise Exception(f'id defined twice: {id}')

def construct_reference_map(element: ModelElement) -> RefMap:
  ref_map: RefMap = {}
  _construct_reference_map(element, ref_map, 0, 0, 0, 0)
  return ref_map

letters = string.ascii_lowercase[:14]

def _construct_reference_map(
    element: ModelElement,
    ref_map: RefMap,
    chapter_index: int,
    section_index: int,
    subsection_index: int,
    subrule_index: int,
    ref_type: Optional[str] = None
  ):
  match element:
    case Document(chapters=chapters):
      for i, chapter in enumerate(chapters):
        _construct_reference_map(chapter, ref_map, i+1, 0, 0, 0)
    case Chapter(id=id, sections=sections, text=text):
      check_id_defined(ref_map, id)
      ref_map[id] = RefInfo(f'{chapter_index}', 'section', text, id, toc=True)
      for i, section in enumerate(sections):
        _construct_reference_map(section, ref_map, chapter_index, i+1, 0, 0)
    case Section(id=id, section_elements=section_elements, text=text, steps=steps):
      check_id_defined(ref_map, id)
      ref_map[id] = RefInfo(f'{chapter_index}.{section_index}', 'section', element.toc_text(), id, toc=True)
      sub_ref_type = 'step' if steps else 'rule'
      for i, section_element in enumerate(section_elements):
        _construct_reference_map(section_element, ref_map, chapter_index, section_index, i+1, 0, sub_ref_type)
    case SubSection(id=id, rules=rules, steps=steps, toc=toc):
      if id is not None:
        check_id_defined(ref_map, id)
        ref_type = 'step' if steps else 'section'
        ref_map[id] = RefInfo(f'{chapter_index}.{section_index}.{subsection_index}', ref_type, element.toc_text(), id, toc)
      sub_ref_type = 'step' if steps else 'rule'
      for i, rule in enumerate(rules):
        _construct_reference_map(rule, ref_map, chapter_index, section_index, subsection_index, i, sub_ref_type)
    case Rule(id=id):
      if id is not None:
        check_id_defined(ref_map, id)
        ref_type = ref_type if ref_type else 'rule'
        ref_map[id] = RefInfo(f'{chapter_index}.{section_index}.{subsection_index}', ref_type, '', id, toc=False)
    case SubRule(id=id):
      if id is not None:
        check_id_defined(ref_map, id)
        ref_type = ref_type if ref_type else 'rule'
        ref_map[id] = RefInfo(f'{chapter_index}.{section_index}.{subsection_index}{letters[subrule_index]}', ref_type, '', id, toc=False)
    case TimingStructureElement():
      return

