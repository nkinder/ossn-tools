#!/bin/python

import argparse
import ossn
import sys

if __name__ == '__main__':
    # Parse our arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('ossn', help='Path to OSSN')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--yaml", help="output to YAML",
                        action="store_true")
    output_group.add_argument("--text", help="output to text",
                        action="store_true")
    output_group.add_argument("--raw", help="output to raw",
                        action="store_true")
    args = parser.parse_args()

    # Read in our OSSN
    ossn_text=''
    try:
        with open(args.ossn) as f:
            for line in f:
                ossn_text += line
    except Exception as e:
        print ('Error accessing OSSN file %s (%s)' % (args.ossn, e))
        sys.exit(1)

    note = ossn.SecurityNote()
    note.load_from_text(ossn_text)

    if (args.yaml):
        # Print out yaml
        print note.to_yaml()
    elif (args.text):
        # Print out note string
        print note.to_text()
    elif (args.raw):
        # Print out note repr
        print('%r' % note)

    sys.exit(0)
