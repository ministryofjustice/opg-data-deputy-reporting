#!/bin/sh
node /usr/src/prism/packages/cli/dist/index.js mock -h 0.0.0.0 -p 5050 "/app/openapi.yml"
