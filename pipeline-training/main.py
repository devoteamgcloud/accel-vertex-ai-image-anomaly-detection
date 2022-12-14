"""Code for running a built pipeline."""
from datetime import datetime
from google.cloud.aiplatform import pipeline_jobs
import os


LOCAL = False


env = "dev"
project = os.environ.get("_PROJECT_ID")
region = os.environ.get("_REGION")
service_account = os.environ.get("_PIPELINE_SA")

pipeline_hash = os.environ.get("_PIPELINE_HASH", None)
if pipeline_hash is None:
    import git

    repo = git.Repo(search_parent_directories=True)
    commits = list(repo.iter_commits(max_count=1, paths="*"))
    pipeline_hash = commits[0].hexsha
    pipeline_hash = pipeline_hash[0:7]
    LOCAL = True

pipeline_bucket = os.environ.get("_PIPELINE_BUCKET")
model_bucket = os.environ.get("_MODEL_BUCKET")

endpoint_name = "image-anomaly-detection"
model_name = "patchcore"

container_training_version = os.environ.get(
    "_CONTAINER_TRAINING_VERSION",
    pipeline_hash,
)
container_serving_version = os.environ.get(
    "_CONTAINER_SERVING_VERSION",
    pipeline_hash,
)
artifact_registry_url = os.environ.get("_ARTIFACT_REGISTRY_URL")
custom_training_image = f"{artifact_registry_url}/training:{container_training_version}"
custom_serving_image = f"{artifact_registry_url}/serving:{container_serving_version}"



def create_pipeline_job():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    pipeline_name = f"pipeline-{timestamp}"

    pipeline_root = (
        f"gs://{pipeline_bucket}/pipeline/"
        f"pipeline_root/{pipeline_hash}/{pipeline_name}"
    )
    pipeline_job = pipeline_jobs.PipelineJob(
        display_name=pipeline_name,
        template_path=(
            f"https://{region}-kfp.pkg.dev/{project}/"
            f"pipeline-templates/pipeline/latest"
        ),
        project=project,
        location=region,
        enable_caching=False,
        pipeline_root=pipeline_root,
        parameter_values={
            "pipeline_root": pipeline_root,
            "training_image": custom_training_image,
            "serving_image": custom_serving_image,
            "endpoint_name": endpoint_name,
            "model_name": model_name,
            "vertex_ai_service_account": service_account,
            "model_bucket": f"gs://{model_bucket}/",
        },
    )

    return pipeline_job


if LOCAL:
    pipeline_job = create_pipeline_job()
    pipeline_job.run(
        service_account=service_account,
    )
else:
    import functions_framework

    @functions_framework.http
    def retrain_model(request):
        pipeline_job = create_pipeline_job()
        pipeline_job.run(
            service_account=service_account,
            sync=True,
        )
        return "ok"
