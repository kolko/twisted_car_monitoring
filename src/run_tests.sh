#!/bin/bash

for test in ./test/*; do
    python2.7 -m pytest --twisted -v $test
done
