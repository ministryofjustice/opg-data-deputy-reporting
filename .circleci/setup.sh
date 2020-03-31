#!/usr/bin/env bash
if [ ! -f ./deputy-reporting-openapi-v1.yml ]
    then
    git clone git@github.com:ministryofjustice/opg-data.git
    cp ./opg-data/docs/deputy-reporting-openapi* ./
    rm -rf ./opg-data
fi

for i in deputy-reporting-openapi*.yml
do
    version=$(echo "${i}" | sed 's/deputy-reporting-openapi-//g' | sed 's/.yml//g')
    cp "${i}" lambda_functions/"${version}"/deputy-reporting-openapi.yml
done

for d in lambda_functions/*/
do
    find "${d}/functions" -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum | cut -c 1-15 > "${d}"/directory_sha
done
