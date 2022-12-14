"""Build pipeline."""
import argparse
from kfp import compiler, dsl
from kfp.registry import RegistryClient

from components.deploy_model import deploy_model_to_custom_endpoint
from components.train_model import train_model


parser = argparse.ArgumentParser()
parser.add_argument(
    "--pipeline-root",
    help="the location to use as staging area for the pipeline",
    type=str,
)
parser.add_argument(
    "--pipeline-name",
    help="the name of the pipeline",
    type=str,
    default="pipeline-v1",
)
parser.add_argument(
    "--pipeline-file",
    help="the location to write the pipeline JSON to",
    type=str,
    default="pipeline.yaml",
)
parser.add_argument(
    "--project-id",
    help="the project ID",
    type=str,
    required=True,
)
parser.add_argument(
    "--region",
    help="the region",
    type=str,
    default="us-central1",
)
parser.add_argument(
    "-t", "--tags",
    nargs="*",
    help="Extra tags to set on the image.",
    required=True,
)

args = parser.parse_args()


@dsl.pipeline(
    pipeline_root=args.pipeline_root,
    name=args.pipeline_name,
)
def build_pipeline(
    pipeline_root: str,
    project_id: str,
    region: str,
    training_image: str,
    serving_image: str,
    endpoint_name: str,
    model_name: str,
    vertex_ai_service_account: str,
    model_bucket: str,
):
    """Build pipeline."""
    train_model_op = train_model(
        pipeline_root=pipeline_root,
        project_id=project_id,
        region=region,
        training_image=training_image,
        vertex_ai_service_account=vertex_ai_service_account,
    )
    deploy_model_to_custom_endpoint(
        pipeline_root=pipeline_root,
        project_id=project_id,
        region=region,
        endpoint_name=endpoint_name,
        model_name=model_name,
        vertex_ai_service_account=vertex_ai_service_account,
        serving_image=serving_image,
        model_bucket=model_bucket,
    ).after(train_model_op)


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=build_pipeline,
        package_path=args.pipeline_file,
        pipeline_parameters={
            "project_id": args.project_id,
            "region": args.region,
        },
    )

    client = RegistryClient(
        host=f"https://{args.region}-kfp.pkg.dev/{args.project_id}/pipeline-templates",
    )
    print(["v1", "latest"] + args.tags)
    templateName, versionName = client.upload_pipeline(
        file_name=args.pipeline_file,
        tags=["v1", "latest"] + args.tags,
        extra_headers={"description": "Image anomaly detection template."},
    )
