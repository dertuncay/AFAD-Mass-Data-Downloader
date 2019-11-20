#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from sac_creator import txt2sac


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text files into SAC")
    parser.add_argument("filename", nargs="+", help="filename")
    parser.add_argument("-o", "--output_dir", default=".",
                        help="output directory")

    args = parser.parse_args()

    for filename in args.filename:
        txt2sac(filename, args.output_dir)
