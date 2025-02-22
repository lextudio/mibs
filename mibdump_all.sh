#!/bin/bash

set -e

mkdir -p json

for mib in asn1/*.txt; do
    echo "Processing $mib..."
    mibdump --mib-source asn1 --destination-format json --destination-directory json "$mib"
done