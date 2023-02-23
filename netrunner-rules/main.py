from text import (RefDict, Text, Ref, Term, FormatText, Example, Image)
from section import (Rule, Section, Header, Document)

import os

def create_toc_html(id_map: RefDict):
  result = ''
  for id in id_map:
    ref_info = id_map[id]
    if not (ref_info.type == 'rule' or ref_info.type == 'subrule'):
      result += f'<div>{ref_info.reference} {ref_info.text}</div>'
  return result

def standalone_html(document: Document, id_map: RefDict):
  result = '<!DOCTYPE html><html><head><link rel="stylesheet" href="demo.css"></head><body>'
  result += f'<div>{create_toc_html(id_map)}</div>'
  result += f'<div>{document.to_html(id_map)}</div>'
  result += '</body></html>'
  return result

def standalone_latex(document: Document, id_map: RefDict):
  result = document.to_latex(id_map)
  return result

def write_to_file(folder: str, filename: str, content: str):
  os.makedirs(folder, exist_ok=True)
  file = open(os.path.join(folder, filename), 'w')
  file.write(content)
  file.close()

x = Document(
     [ Header('hdr_game_concepts', 'Game Concepts',
        [ Section('sec_general', 'General', FormatText([Text('These rules are compatible with cards from the game '), Term('android: netrunner'), Text(' by Fantasy Flight Games. '), Term('android: netrunner'), Text(' is a game about the cyber-struggle between massive Corporations and subversive hackers known as Runners.')]),
          [ Rule('rule_1', FormatText([Text('The game is played between two players. One player takes the role of the Corp (Corporation) and the other takes the role of the Runner. This rules document will frequently refer to a player interchangeably with their game role.')]), [], [])
          , Rule('rule_2', FormatText([Text('Each player needs a legal deck, an identity card for their role, and any extra cards used from outside their deck. They also need a supply of tokens as described in '), Ref('sec_counters_tokens'), Text('. The constraints that define the legality of a deck are defined in section 1.4, and the cases where cards outside the deck and identity can be used are defined in section 1.5.')]), [], [])
          ])
        , Section('sec_golden_rules', 'Golden Rules', None,
          [ Rule('rule_3', FormatText([Text('If the text of a card directly contradicts these rules, the text of the card takes precedence.')]), [], [])
          , Rule('rule_4', FormatText([Text('If a rule or ability directs something to happen, but another effect states that it cannot happen, the "cannot" ability takes precedence.')]),
            [ Rule('rule_5', FormatText([Text('If a "cannot" effect prohibits all of the effects of another ability, that ability cannot be triggered.')]), [], [])
            , Rule('rule_6', FormatText([Text('If a "cannot" effect prohibits only part of another ability, that ability can be triggered, but the prohibited steps of resolving that ability are not carried out.')]), [],
              [ Example(FormatText([Text('During a run, Lockdown’s subroutine resolves, preventing the Runner from drawing cards for the remainder of the turn. The Runner has a Diesel and a Process Automation in their grip. For the remainder of this turn, they cannot play Diesel as its entire ability is prohibited, but they can play Process Automation. Even though cards cannot be drawn through Process Automation, the Runner can play it to gain 2'), Image('credit'), Text('.')]))
              ])
            ], [])
          ])
        , Section('sec_symbols', 'Symbols', None,
          [ Rule('symbol_guide', FormatText([Text('Several non-English symbols appear on cards and in this rules document. This section serves as a basic guide to those symbols.')]), [], [])
          , Rule('symbol_images', FormatText([Text('When this document is presented in a format without images, plaintext replacements are used. These replacements are listed along with the symbols themselves for reference.')]), [], [])
          , Rule('symbol_credit', FormatText([Text('The symbol '), Image('credit'), Text(' (plaintext: [c]) stands for “credit”. It always appears with a numeral, such as 1'), Image('credit'), Text(' , which means “one credit,” or 3'), Image('credit'), Text(' , which means “three credits.” See section 1.10 for rules about credits.')]), [], [])
          ])
        , Section('sec_deck_construction', f'Deck Construction', None, [])
        , Section('sec_extra_cards', f'Extra Cards', None, [])
        , Section('sec_starting', f'Starting the Game', None, [])
        , Section('sec_ending', f'Ending the Game', None, [])
        , Section('sec_cards', f'Cards', None, [])
        , Section('sec_counters_tokens', f'Counters and Tokens', None, [])
        ])
      ])

if __name__ == "__main__":
  #print(x)
  id_map = x.id_map()
  write_to_file('html', 'demo.html', standalone_html(x, id_map))
  write_to_file('latex', 'demo.tex', standalone_latex(x, id_map))
