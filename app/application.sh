#! /bin/bash

export ACCESS_TOKEN=$(gcloud auth print-access-token)
export BASE64_IMAGE=$(base64 -i $1)
export INPUT_DATA_FILE="request.json"
export PREDICT_URL=$2

envsubst < request-template.json > ${INPUT_DATA_FILE}

curl -X POST -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" "${PREDICT_URL}" -d "@${INPUT_DATA_FILE}"

rm ${INPUT_DATA_FILE}
