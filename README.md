# Document Generator for Netrunner Comprehensive Rules

This project is a document generator to convert a YAML description of rules into formatted outputs (such as pdf / html). You can view the example output of the github workflow action [here](https://github.com/rubenpieters/netrunner-comprehensive-rules/actions/workflows/convert.yaml).

## Document Elements

The YAML contains several levels of structures to organize the rules.

### Changelog

Contains the changelog entries. Entries can contain [formatted text](#formatted-text-syntax).

```
changelog:
- text: entry1
- text: entry2
```

### Chapter

Defines a chapter (numbered with 1.).

```
chapter: chapter_id
text: Chapter Title
sections:
- section:
  ...
- section:
  ...
```

### Section

Defines a section (numbered with 1.1.).

```
section: section_id
text: Formatted Section Title
toc_entry: (optional) alternate title for the table of contents (useful if the formatted title would break the toc)
snippet: (optional) snippet for the section
rules:
- rule:
  ...
- subsection:
  ...
```

### Subsection

Defines a subsection (numbered with 1.1.1.).

```
subsection: subsection_id
text: Formatted Subsection Text
toc: (optional indicator whether this subsection should be added to the table of contents)
steps: (optional indicator whether this subsection and any subelements should be referred to as 'step')
examples:
- text: Formatted Example Text
rules:
- rule:
  ...
- rule:
  ...
```

### Rule

Defines a rule. A rule can be under a section (numbered with 1.1.1.) or nested below a rule (numbered with a.).

```
rule: rule_id
text: Formatted Rule Text
examples:
- text: Formatted Example Text
- text: Formatted Example Text
```

### Timing Structure

Timing structures can be added in the `rules` block of a section.

```
timing_structure:
elements:
- text: Step 1
  elements:
  - text: Step A
    elements:
    - text: Step Z
- text: Step 2
```

## Formatted Text Syntax

### References

Reference any identifier of a chapter, section, rule, or subrule.

```
{ref:ref_id}
```

A reference can contain a capital letter at the start, to indicate the reference text should be capitalized.

```
{ref:Ref_id}
```

Referencing multiple identifiers at once is possible with a `,`.

```
{ref:ref_1,ref_2,ref_3}
```

If you want a different word than `and` to combine the reference, you can specify it after `/`.

```
{ref/through:ref_1,ref_2,ref_3}
```

### Images

Embed an image in the document.

```
{img:img_name}
```

### Terms

Indicates a game term.

```
{term:credits}
```

### Subtype

Indicates a subtype.

```
{subtype:connection}
```

### Card Reference

Indicates a card name.

```
{card:Fermenter}
```

### Product Names

Indicates a product name.

```
{product:System Gateway}
```

### Links

Indicates a link to a website.

```
{link:website|https://nullsignal.games}
```

### Note on literal scalar style

The use of the [literal scalar style](https://yaml.org/spec/1.2.2/#literal-style) of the YAML spec is useful to define literal text.

```
text: |-
  My text goes here.
```

## Highlighting new parts of releases

Highlight a rule as new.

```
- rule:
  new:
```

Highlight a piece of text as new.

```
text: This is old text. {n}This is new text.{/n}
```
