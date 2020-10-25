#!/usr/bin/env python3
""" This is a basic script to redact any ifo I don't want to appear in this
repo for anyone to see. I'm sure you can all understand :P
"""
import os
import json

CONFIG_PATH = os.environ.get('REDACTED_CONFIG_PATH')
ROOT = "writeups"
REDACTED_STRINGS = []
SKIP_LOCATIONS = ['/src/', '/archives/']
REPLACEMENT_STR = "{REDACTED}"

if CONFIG_PATH and os.path.exists(CONFIG_PATH):
    # JSON: ["string", "string2"]
    with open(CONFIG_PATH, 'r') as handle:
        REDACTED_STRINGS = json.load(handle)


for folder, subfolders, filenames in os.walk(ROOT):
    for filename in filenames:
            filepath = os.path.join(folder, filename)

            # Skip if not a file
            if not os.path.isfile(filepath):
                continue
            # HACK: 'convert' Windows paths to Unix
            testpath = filepath.replace('\\', '/')
            skip_loc = False

            for loc in SKIP_LOCATIONS:
                if loc in testpath:
                    skip_loc = True

            if skip_loc:
                continue

            print("[+] Processing file :: " + filepath)

            with open(filepath, 'r') as handle:
                content = handle.read()

            for redacted_str in REDACTED_STRINGS:
                content = content.replace(redacted_str, REPLACEMENT_STR)

            with open(filepath, 'w') as handle:
                handle.write(content)
