# Contribution Guide

This guide will help you get set up on contributing to the netrunner comprehensive rules project.

## Overview

Overview of the folder structure in the project:

```
- .github             | files for github actions
- data                | input data for the document generation 
- rules_doc_generator | python project for the format conversion
```

## Setup

To get set up with the Python project you'll need at least Python 3.11 and install the required dependencies.

```
pip install -r requirements.txt
```

After that you can generate the output documents via the python module.

```
python -X utf8 -m rules_doc_generator
```

This will generate an output folder corresponding to each of the output formats (currently: `html` and `latex`). When making changes and pushing them to the repository, you should verify that the output can be generated and looks like you expect.
