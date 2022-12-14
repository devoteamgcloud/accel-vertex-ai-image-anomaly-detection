"""Deploy model."""
from kfp.dsl import (
    component,
)
import os


ARTIFACT_REGISTRY_URL = os.environ.get("_ARTIFACT_REGISTRY_URL")
CONTAINER_HASH = os.environ.get("_CONTAINER_VERSION")


@component(
    base_image=(
        f"{ARTIFACT_REGISTRY_URL}/python:{CONTAINER_HASH}"
    ),
)
def deploy_model_to_custom_endpoint(
    pipeline_root: str,
    project_id: str,
    region: str,
    endpoint_name: str,
    model_name: str,
    vertex_ai_service_account: str,
    serving_image: str,
    model_bucket: str,
):
    from google.api_core import page_iterator
    from google.cloud import aiplatform
    from google.cloud.aiplatform import gapic as aip
    from google.cloud import storage

    gcs = storage.Client(project=project_id)

    def endpoint_retrieve_or_create(endpoint_display_name: str):
        endpoints = aiplatform.Endpoint.list()
        for endpoint in endpoints:
            if endpoint.display_name == endpoint_display_name:
                return endpoint

        return aiplatform.Endpoint.create(display_name=endpoint_display_name)

    def model_retrieve(model_display_name: str):
        models = aiplatform.Model.list()
        for model in models:
            if model.display_name == model_display_name:
                return model

        return None

    def _item_to_value(iterator, item):
        return item

    def list_directories(bucket_name, prefix):
        if prefix and not prefix.endswith('/'):
            prefix += '/'

        extra_params = {
            "projection": "noAcl",
            "prefix": prefix,
            "delimiter": '/'
        }

        path = "/b/" + bucket_name + "/o"

        iterator = page_iterator.HTTPIterator(
            client=gcs,
            api_request=gcs._connection.api_request,
            path=path,
            items_key='prefixes',
            item_to_value=_item_to_value,
            extra_params=extra_params,
        )

        return [x for x in iterator]

    aiplatform.init(
        project=project_id,
        location=region,
        staging_bucket=model_bucket,
    )

    vertex_endpoint = endpoint_retrieve_or_create(endpoint_name)
    vertex_model = model_retrieve(model_name)

    artifact_uri = pipeline_root + "/custom_container_training_job"
    artifact_uri = artifact_uri.split("/")
    artifact_uri_bucket_name = artifact_uri[2]
    artifact_uri_prefix = "/".join(artifact_uri[3:])
    artifact_uri_augmented = list_directories(
        artifact_uri_bucket_name,
        artifact_uri_prefix,
    )[0]
    artifact_uri = f"gs://{artifact_uri_bucket_name}/{artifact_uri_augmented}"
    print(f"Selected artifact_uri: {artifact_uri}")

    vertex_model = aiplatform.Model.upload(
        model_id=model_name,
        parent_model=model_name if vertex_model is not None else None,
        display_name=model_name,
        artifact_uri=artifact_uri,
        serving_container_image_uri=serving_image,
    )

    DEPLOY_GPU, DEPLOY_NGPU = (aip.AcceleratorType.NVIDIA_TESLA_K80, 2)
    DEPLOY_COMPUTE = "n1-standard-16"
    vertex_model.deploy(
        endpoint=vertex_endpoint,
        machine_type=DEPLOY_COMPUTE,
        min_replica_count=1,
        max_replica_count=1,
        accelerator_type=DEPLOY_GPU.name,
        accelerator_count=DEPLOY_NGPU,
        traffic_split={"0": 100},
        deployed_model_display_name=model_name,
        service_account=vertex_ai_service_account,
        deploy_request_timeout=3600,
    )
