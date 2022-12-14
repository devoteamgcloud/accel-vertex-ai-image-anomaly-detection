# accel-image-anomaly-detection

## Description
This accelerator covers the image anomaly detection use case on the industrial MVTecAD dataset. It uses the PathCore model which you can read in detail about in the [published paper](https://arxiv.org/pdf/2106.08265.pdf).

## Setup instructions
- Create a new Google Cloud project
- Enable IAM Service Account Credentials API
- Create a new `terraform-init` service account with Owner role
- Give yourself the Service Account Token Creator role
- Create the bucket for your Terraform state
- Connect your GitHub project to Source Repositories
- Fill in and rename `TEMPLATE.tfvars` + `TEMPLATE.backend`
- `gcloud config set project <PROJECT_ID>`
- `gcloud auth application-default login`
- `terraform init --backend-config=<BACKEND_FILENAME>.backend`
- `terraform workspace new <WORKSPACE_NAME>`
- `terraform plan --out tf.plan --var-file=<TFVARS_FILENAME>.tfvars`
- `terraform apply "tf.plan"`
- Create an Artifact Registry "Kubeflow Pipelines" repository named `pipeline-templates`

## Developer instructions
- Push changes to the Git, it will automatically trigger a Cloud Build run and update the necessary components
- To launch a training pipeline, go to Cloud Functions and visit the HTTP link of the "pipeline-training" Cloud Function
- Once the model is deployed, use `app/application.sh` for predictions by passing an image and the URI of your Vertex AI Endpoint, e.g. `app/application.sh cable-bent.png https://<REGION>-aiplatform.googleapis.com/v1/projects/<PROJECT_ID>/locations/<REGION>/endpoints/<ENDPOINT_ID>:predict`

## Known issues
- Predicted suspicion scores are not normalised. A high score means an image that is very suspicious, a low score means that an image does not contain an anomaly.
- Vertex AI Endpoints only accept requests up to 1.5MB. You may need to compress your images before sending them out to the endpoint. Another alternative would be to refactor the prediction code to accept Cloud Storage URIs instead of the full images directly.
