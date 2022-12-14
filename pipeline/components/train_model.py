"""Train model component."""
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
def train_model(
    pipeline_root: str,
    project_id: str,
    region: str,
    training_image: str,
    vertex_ai_service_account: str,
):
    """
    Train a recommender system model.

    :param data: Input dataset
    :return model: Trained model
    """
    from datetime import datetime
    from google.cloud import aiplatform
    from google.cloud.aiplatform import gapic as aip

    aiplatform.init(
        project=project_id,
        location=region,
        staging_bucket=pipeline_root + "/custom_container_training_job",
    )

    TRAIN_GPU, TRAIN_NGPU = (aip.AcceleratorType.NVIDIA_TESLA_V100, 2)
    TRAIN_COMPUTE = "n1-standard-16"

    job_name = "training_job_" + datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    args = [
        *[
            line
            for lines in [
                ["--gpu", f"{i}"]
                for i in range(TRAIN_NGPU)
            ]
            for line in lines
        ],
        "--seed", "0",
        "--save_patchcore_model",
        "--log_group", "IM224_WR50_L2-3_P01_D1024-1024_PS-3_AN-1_S0",
        "--log_project", "MVTecAD_Results",
        "results",

        "sampler",
        "-p", "0.1",
        "approx_greedy_coreset",

        # full datasets
        "dataset",
        "--resize", "256",
        "--imagesize", "224",
        "-d", "bottle",
        "-d", "cable",
        "-d", "capsule",
        "-d", "carpet",
        "-d", "grid",
        "-d", "hazelnut",
        "-d", "leather",
        "-d", "metal_nut",
        "-d", "pill",
        "-d", "screw",
        "-d", "tile",
        "-d", "toothbrush",
        "-d", "transistor",
        "-d", "wood",
        "-d", "zipper",
        "mvtec",
        "/app/data",

        "patch_core",
        "-b", "wideresnet50",
        "-le", "layer2",
        "-le", "layer3",
        "--faiss_on_gpu",
        "--pretrain_embed_dimension", "1024",
        "--target_embed_dimension", "1024",
        "--anomaly_scorer_num_nn", "1",
        "--patchsize", "3",
    ]

    job = aiplatform.CustomContainerTrainingJob(
        display_name=job_name,
        container_uri=training_image,
        command=["python3", "app.py"],
    )

    job.run(
        args=args,
        replica_count=1,
        machine_type=TRAIN_COMPUTE,
        accelerator_type=TRAIN_GPU.name,
        accelerator_count=TRAIN_NGPU,
        service_account=vertex_ai_service_account,
    )
