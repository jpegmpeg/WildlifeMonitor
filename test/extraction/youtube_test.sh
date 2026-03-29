#!/bin/bash
# Test the youtube downloader 

set -e

cd "../../src/sources" || exit 1
python3.12 download.py -s youtube "https://www.youtube.com/watch?v=bd7FaTtCt04"