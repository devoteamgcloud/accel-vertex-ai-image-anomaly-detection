from base64 import b64decode
import contextlib
from flask import Flask, request
import gc
from google.cloud import storage
import os
from io import BytesIO
import numpy as np
from pathlib import Path
import PIL.Image
import torch
from torchvision import transforms

import patchcore.common
import patchcore.metrics
import patchcore.patchcore
import patchcore.sampler
import patchcore.utils


PORT = os.getenv("AIP_HTTP_PORT")
PREDICT_ROUTE = os.getenv("AIP_PREDICT_ROUTE")
HEALTH_ROUTE = os.getenv("AIP_HEALTH_ROUTE")
STORAGE_URI = os.getenv("AIP_STORAGE_URI")

TRAINED_MODEL_PATH = os.path.join(
    STORAGE_URI,
    "model",
    "MVTecAD_Results",
    "IM224_WR50_L2-3_P01_D1024-1024_PS-3_AN-1_S0",
    "models",
)
STORAGE_URI_SPLIT = TRAINED_MODEL_PATH[len("gs://"):].split("/")
STORAGE_URI_BUCKET_NAME = STORAGE_URI_SPLIT[0]
STORAGE_URI_PREFIX = "/".join(STORAGE_URI_SPLIT[1:])

LOCAL_PATH = "/accel-image-anomaly-detection/models"

DEBUG = bool(
    os.environ.get(
        "DEBUG",
        False,
    )
)

STORAGE_CLIENT = storage.Client()


IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def initialize_system():
    print("Bucket:", STORAGE_URI_BUCKET_NAME)
    print("Prefix:", STORAGE_URI_PREFIX)

    blobs = STORAGE_CLIENT.list_blobs(
        bucket_or_name=STORAGE_URI_BUCKET_NAME,
        prefix=STORAGE_URI_PREFIX,
    )
    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        file_split = blob.name.split("/")
        directory = "/".join(file_split[0:-1])
        directory = LOCAL_PATH + directory[len(STORAGE_URI_PREFIX):]
        print("Directory:", directory)
        Path(directory).mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(LOCAL_PATH + blob.name[len(STORAGE_URI_PREFIX):])

    print("All blobs created!")


initialize_system()


app = Flask(__name__)


@app.route(HEALTH_ROUTE)
def health():
    return "OK"


def predict_images(
    images,
    gpu=[0],
    seed=0,
    patch_core_paths=[],
    faiss_on_gpu=True,
    faiss_num_workers=8,
):
    def get_patchcore_iter(device):
        for patch_core_path in patch_core_paths:
            loaded_patchcores = []
            gc.collect()
            n_patchcores = len(
                [x for x in os.listdir(patch_core_path) if ".faiss" in x]
            )
            if n_patchcores == 1:
                nn_method = patchcore.common.FaissNN(faiss_on_gpu, faiss_num_workers)
                patchcore_instance = patchcore.patchcore.PatchCore(device)
                patchcore_instance.load_from_path(
                    load_path=patch_core_path, device=device, nn_method=nn_method
                )
                loaded_patchcores.append(patchcore_instance)
            else:
                for i in range(n_patchcores):
                    nn_method = patchcore.common.FaissNN(
                        faiss_on_gpu, faiss_num_workers
                    )
                    patchcore_instance = patchcore.patchcore.PatchCore(device)
                    patchcore_instance.load_from_path(
                        load_path=patch_core_path,
                        device=device,
                        nn_method=nn_method,
                        prepend="Ensemble-{}-{}_".format(i + 1, n_patchcores),
                    )
                    loaded_patchcores.append(patchcore_instance)

            yield patch_core_path, loaded_patchcores

    device = patchcore.utils.set_torch_device(gpu)
    # Device context here is specifically set and used later
    # because there was GPU memory-bleeding which I could only fix with
    # context managers.
    device_context = (
        torch.cuda.device("cuda:{}".format(device.index))
        if "cuda" in device.type.lower()
        else contextlib.suppress()
    )

    patchcore_iter = get_patchcore_iter(device)

    full_scores = {}
    patchcore.utils.fix_seeds(seed, device)
    with device_context:
        for patch_core_path, PatchCore_list in patchcore_iter:
            torch.cuda.empty_cache()
            aggregator = {"scores": []}
            for PatchCore in PatchCore_list:
                torch.cuda.empty_cache()

                scores, _ = PatchCore.predict(
                    images
                )
                aggregator["scores"].append(scores)

            scores = np.array(aggregator["scores"])
            scores = np.mean(scores, axis=0)

            full_scores[patch_core_path] = scores.tolist()

            del PatchCore_list
            gc.collect()

    return full_scores


@app.route(PREDICT_ROUTE, methods=["POST"])
def predict():
    patch_core_paths = [
        f"{LOCAL_PATH}/{d}"
        for d in os.listdir(LOCAL_PATH)
        if os.path.isdir(f"{LOCAL_PATH}/{d}")
    ]

    resize = 256
    imagesize = 224
    transform_img = [
        transforms.Resize(resize),
        transforms.CenterCrop(imagesize),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ]
    transform_img = transforms.Compose(transform_img)

    images = [
        transform_img(
            PIL.Image.open(
                BytesIO(
                    b64decode(instance)
                )
            ).convert("RGB")
        )
        for instance in request.json.get("instances")
    ]
    images = torch.stack(images)

    full_scores = predict_images(
        images,
        gpu=[0, 1],
        seed=0,
        patch_core_paths=patch_core_paths,
        faiss_on_gpu=True,
        faiss_num_workers=8,
    )

    api_output = {
        "estimations": full_scores,
    }

    return {"predictions": api_output}


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=DEBUG,
    )
