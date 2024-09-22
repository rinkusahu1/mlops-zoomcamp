#!/usr/bin/env bash

## github vm has diff root path and don't want to change it
if [ -z "${GITHUB_ACTIONS}" ]; then
  echo "setting current"
  cd "$(dirname "$0")"
fi

echo "local image path ${LOCAL_IMAGE_NAME}"

if [ -z "${LOCAL_IMAGE_NAME}" ]; then 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="stream-model-duration:${LOCAL_TAG}"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi


export PREDICTIONS_STREAM_NAME="ride_predictions"
export AWS_REGION="eu-north-1"

docker compose up -d

sleep 10 

aws --endpoint-url=http://localhost:4566 \
    kinesis create-stream \
    --stream-name ${PREDICTIONS_STREAM_NAME} \
    --shard-count 1 \
    --region $AWS_REGION

echo "aws stream created"

aws --endpoint-url=http://localhost:4566 \
    kinesis list-streams

pipenv run python test_docker.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi


pipenv run python test_kinesis.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi


docker compose down
