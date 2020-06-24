#!/usr/bin/env bash
if ls ./deputy-reporting-openapi-v*.yml 1> /dev/null 2>&1
then
  echo "openapi spec exists in folder"
else
#  git clone git@github.com:ministryofjustice/opg-data.git
  git clone -b IN-263 git@github.com:ministryofjustice/opg-data.git
  cp ./opg-data/docs/deputy-reporting-openapi* ./
  rm -rf ./opg-data
fi

for i in deputy-reporting-openapi*.yml
do
    version=$(echo "${i}" | sed 's/deputy-reporting-openapi-//g' | sed 's/.yml//g')
    cp "${i}" lambda_functions/"${version}"/deputy-reporting-openapi.yml
done

for d in lambda_functions/v*/
do
    find "${d}/functions" -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum | cut -c 1-15 > "${d}"/directory_sha
done
