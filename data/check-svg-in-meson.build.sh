#!/bin/bash -e

pushd "$1" > /dev/null
diff -u1 <(grep -o 'svgs/.*\.svg' data/meson.build) <(cd data; ls -v svgs/*.svg)
popd > /dev/null
