# LLM DevOps Project

An end-to-end DevOps project for deploying a self-hosted LLM application on **AWS EKS** with **Docker, Amazon ECR, Kubernetes, GitHub Actions, Prometheus, and Grafana**.

The application provides a simple Streamlit chat interface backed by a FastAPI API and a CPU-based vLLM model server running **Qwen/Qwen2.5-0.5B-Instruct**.

## Live Demo

> **Demo URL:** http://a4eb7e4910fe04ce4a08de8f564f3457-449331885.ap-south-1.elb.amazonaws.com:8501
>
> The demo is HTTP-only and the AWS Load Balancer hostname may change when the infrastructure is recreated.

## Architecture

```text
                         Internet
                            |
                            v
                  AWS Load Balancer
                            |
                            v
                    Streamlit :8501
                            |
                            v
                     FastAPI :8001
                            |
                            v
                       vLLM :8000
                            |
                            v
               Qwen2.5-0.5B-Instruct

CI/CD
-----
Developer -> GitHub -> GitHub Actions -> Docker Build/Test
                                      |
                                      v
                                     ECR
                                      |
                                      v
                                     EKS
                                      |
                                      v
                         FastAPI + Streamlit rollout

Monitoring
----------
Kubernetes/cAdvisor -> Prometheus -> Grafana
```

## What This Project Demonstrates

- Containerizing an application with Docker
- Storing images in Amazon ECR
- Deploying workloads with Kubernetes on Amazon EKS
- Kubernetes Deployments and Services
- Public application exposure with an AWS Load Balancer
- GitHub Actions CI/CD
- GitHub OIDC authentication with AWS IAM roles
- Automated ECR image publishing
- Automated EKS application rollouts
- Prometheus metrics collection
- Grafana dashboards
- CPU-only LLM inference with vLLM
- Basic cloud and Kubernetes troubleshooting

## Tech Stack

| Category | Technology |
|---|---|
| Frontend | Streamlit |
| API | FastAPI |
| LLM serving | vLLM |
| Model | Qwen/Qwen2.5-0.5B-Instruct |
| Language | Python |
| Containerization | Docker |
| Container Registry | Amazon ECR |
| Orchestration | Kubernetes |
| Cloud Kubernetes | Amazon EKS |
| CI/CD | GitHub Actions |
| AWS authentication | IAM + GitHub OIDC |
| Monitoring | Prometheus + Grafana |
| Cluster metrics | Kubernetes/cAdvisor |

## Project Structure

```text
llm-devops-project/
├── app/
│   ├── api.py
│   └── streamlit_app.py
├── k8s/
│   ├── eks-cluster.yaml
│   ├── fastapi-deployment.yaml
│   ├── fastapi-service.yaml
│   ├── streamlit-deployment.yaml
│   ├── streamlit-service.yaml
│   ├── vllm-deployment.yaml
│   └── vllm-service.yaml
├── .github/
│   └── workflows/
│       └── ci.yml
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── monitoring-values.yaml
├── grafana-values.yaml
├── github-actions-trust-policy.json
└── github-actions-permissions.json
```

## Application Flow

1. A user opens the Streamlit web interface.
2. Streamlit sends the prompt to the FastAPI `/chat` endpoint.
3. FastAPI calls the OpenAI-compatible vLLM API inside the Kubernetes cluster.
4. vLLM runs the Qwen model and returns the generated response.
5. FastAPI returns the response to Streamlit.
6. Streamlit displays the result in the browser.

FastAPI and vLLM are exposed through internal Kubernetes `ClusterIP` Services. Streamlit is exposed through a `LoadBalancer` Service.

## CI/CD Flow

Every push to the `main` branch triggers GitHub Actions.

```text
Git push
   |
   v
GitHub Actions
   |
   +--> Checkout source
   |
   +--> Configure AWS credentials using GitHub OIDC
   |
   +--> Build Docker image
   |
   +--> Run API smoke test
   |
   +--> Push image to Amazon ECR
   |
   +--> Configure kubectl for EKS
   |
   +--> Update FastAPI and Streamlit images
   |
   +--> Wait for Kubernetes rollouts
   |
   v
New application version running on EKS
```

Images are tagged with the Git commit SHA so deployments can reference an immutable image version rather than relying only on `latest`.

## Monitoring

Prometheus collects Kubernetes/container metrics and Grafana visualizes them.

The project dashboard includes metrics such as:

- vLLM memory usage
- vLLM CPU usage
- Monitoring target health
- Kubernetes node memory usage

Example monitoring path:

```text
vLLM container
      |
      v
cAdvisor metrics
      |
      v
Prometheus
      |
      v
Grafana dashboard
```

## Run Locally with Docker Compose

### Prerequisites

- Docker Desktop
- Docker Compose
- Git

### Start the application

```bash
git clone https://github.com/Aslamvs1/llm-devops-project.git
cd llm-devops-project

docker compose up -d --build
```

Check the containers:

```bash
docker compose ps
```

The local application exposes the Streamlit UI on port `8501`.

## Deploy to AWS EKS

### Prerequisites

- AWS CLI
- kubectl
- eksctl
- Helm
- An AWS account with the required permissions

Configure AWS credentials locally:

```bash
aws configure
```

Verify the identity:

```bash
aws sts get-caller-identity
```

Create or use an EKS cluster and configure kubectl:

```bash
aws eks update-kubeconfig --name <cluster-name> --region <aws-region>
```

Apply the Kubernetes manifests:

```bash
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl apply -f k8s/fastapi-service.yaml
kubectl apply -f k8s/vllm-deployment.yaml
kubectl apply -f k8s/vllm-service.yaml
kubectl apply -f k8s/streamlit-deployment.yaml
kubectl apply -f k8s/streamlit-service.yaml
```

Check workloads:

```bash
kubectl get deployments
kubectl get pods
kubectl get svc
```

## Install Monitoring

Prometheus and Grafana are installed with Helm using the lightweight values files in the repository.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana-community https://grafana-community.github.io/helm-charts
helm repo update
```

Prometheus:

```bash
helm upgrade --install prometheus prometheus-community/prometheus \
  -f monitoring-values.yaml
```

Grafana:

```bash
kubectl create namespace monitoring
helm install grafana grafana-community/grafana \
  -n monitoring \
  -f grafana-values.yaml
```

For local access during administration, port-forward the services:

```bash
kubectl port-forward svc/prometheus-server 9090:80
kubectl port-forward -n monitoring svc/grafana 3000:80
```

Then open:

- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`

## Troubleshooting Notes

### vLLM `/dev/shm` error

The vLLM deployment uses an in-memory `emptyDir` mounted at `/dev/shm` to provide more shared memory than the container default.

### vLLM `VLLM_PORT` URI error

Kubernetes service-link environment variables conflicted with vLLM's environment handling. The vLLM Deployment disables automatic Service environment variable injection with:

```yaml
enableServiceLinks: false
```

Kubernetes DNS service discovery still works, so FastAPI can continue using:

```text
http://vllm:8000/v1
```

### Single-node scheduling pressure

The vLLM workload is memory-heavy. The Deployment uses:

```yaml
strategy:
  type: Recreate
```

This allows the old vLLM Pod to stop before a replacement is scheduled, avoiding the temporary resource requirement of running two vLLM Pods at once on a single worker node.

### Prometheus PVC pending

For this project/demo, Prometheus persistence is disabled to avoid requiring a PersistentVolume. Prometheus data is therefore temporary and is lost when the Pod is recreated.

### Grafana startup / OOM

Grafana is given a higher memory limit than the initial configuration so that startup does not fail under the node's memory constraints.

## Security Notes

- GitHub Actions authenticates to AWS using GitHub OIDC and an IAM role.
- The workflow does not require long-lived AWS access keys stored in GitHub Secrets.
- FastAPI and vLLM are internal Kubernetes Services.
- The demo endpoint is intentionally a simple project deployment and is not configured with HTTPS or application authentication.
- Do not commit AWS access keys, passwords, tokens, or private SSH keys to the repository.

## Future Improvements

- HTTPS with a custom domain and TLS certificate
- Application authentication/authorization
- Centralized logging
- Alerting with Prometheus/Grafana
- Infrastructure as Code with Terraform
- Persistent monitoring storage
- Kubernetes resource autoscaling
- Production-grade security hardening

## Author

**Muhammed Aslam V S**

GitHub: [@Aslamvs1](https://github.com/Aslamvs1)
