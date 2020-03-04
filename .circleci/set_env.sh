#!/usr/bin/env bash

WORKSPACE=${WORKSPACE:-$CIRCLE_BRANCH}
WORKSPACE=${WORKSPACE//[^[:alnum:]]/}
WORKSPACE=${WORKSPACE,,}
WORKSPACE=${WORKSPACE:0:14}
echo "export TF_WORKSPACE=${WORKSPACE}"
TF_VAR_stage=`grep -A1 'info:' deputy-reporting-openapi.yml | grep 'version:' | head -1 | awk '{print $2}' | sed 's/\./_/g'`
echo "export TF_VAR_stage=${TF_VAR_stage}"
