from rules_doc_generator.model.model_data import (RefInfo)
from rules_doc_generator.model.section import (ModelElement, Document, Chapter, Section, SubSection, Rule, SubRule, TimingStructure, TimingStructureElement)

import string
from typing import Optional

_roman = ['i','ii','iii','iv','v','vi','vii','viii','ix','x','xi','xii','xiii','xiv']

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
        if isinstance(section_element, TimingStructure):
          _assign_timing_ids(section_element, ref_map, id, f'{chapter_index}.{section_index}')
        else:
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


def _assign_timing_ids(ts: TimingStructure, ref_map: RefMap, section_id: str, base_nr: str):
  for i, l1 in enumerate(ts.elements):
    l1_id = f'{section_id}_{i+1}'
    l1_nr = f'{base_nr}_{i+1}'
    l1.id = l1_id
    check_id_defined(ref_map, l1_id)
    ref_map[l1_id] = RefInfo(l1_nr, 'appendix', '', l1_id, toc=False)
    for j, l2 in enumerate(l1.elements):
      letter = letters[j]
      l2_id = f'{l1_id}_{letter}'
      l2_nr = f'{l1_nr}_{letter}'
      l2.id = l2_id
      check_id_defined(ref_map, l2_id)
      ref_map[l2_id] = RefInfo(l2_nr, 'appendix', '', l2_id, toc=False)
      for k, l3 in enumerate(l2.elements):
        roman = _roman[k]
        l3_id = f'{l2_id}_{roman}'
        l3_nr = f'{l2_nr}_{roman}'
        l3.id = l3_id
        check_id_defined(ref_map, l3_id)
        ref_map[l3_id] = RefInfo(l3_nr, 'appendix', '', l3_id, toc=False)
