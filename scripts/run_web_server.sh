#!/usr/bin/env bash

set -Eeuo pipefail

# Generate web server files.
python3 -m rules_doc_generator -a -t opengraph

# Run the server.
cd php
php -S 0.0.0.0:80
