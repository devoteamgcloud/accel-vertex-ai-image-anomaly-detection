FROM python:3.8-slim

ARG ARTIFACT_REGISTRY_URL_PACKAGE
ARG PACKAGE_VERSION

RUN apt-get update && \
    apt-get install -y gettext-base && \
    apt-get clean && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/*

COPY requirements.txt .

RUN pip3 install keyring==23.8.2 keyrings.google-artifactregistry-auth==1.0.0
RUN export ARTIFACT_REGISTRY_URL_PACKAGE=$ARTIFACT_REGISTRY_URL_PACKAGE && \
    export PACKAGE_VERSION=$PACKAGE_VERSION && \
    envsubst < requirements.txt > requirements-all.txt && \
    pip3 install -r requirements-all.txt

CMD ["python3"]
