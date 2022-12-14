FROM us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.1-11:latest

ARG ARTIFACT_REGISTRY_URL_PACKAGE
ARG PACKAGE_VERSION

USER root

RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

RUN export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s` && \
    echo "deb https://packages.cloud.google.com/apt $GCSFUSE_REPO main" | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - && \
    apt-get update && \
    apt-get install gcsfuse

RUN apt-get update && \
    apt-get install -y gettext-base && \
    apt-get clean && rm -rf /var/cache/apt/* && rm -rf /var/lib/apt/lists/* && rm -rf /tmp/*

WORKDIR /app
COPY . .

RUN pip3 install keyring==23.8.2 keyrings.google-artifactregistry-auth==1.0.0
RUN export ARTIFACT_REGISTRY_URL_PACKAGE=$ARTIFACT_REGISTRY_URL_PACKAGE && \
    export PACKAGE_VERSION=$PACKAGE_VERSION && \
    envsubst < requirements.txt > requirements-all.txt && \
    pip3 install -r requirements-all.txt

RUN cd data && ./download_mvtec.sh

CMD ["python3", "app.py"]
