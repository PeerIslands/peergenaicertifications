## AWS Deployment Guide (Frontend and Backend split)

This guide explains how to deploy the split apps to AWS:
- Backend: FastAPI on ECS Fargate behind an Application Load Balancer (ALB)
- Frontend: Static site on S3 + CloudFront (recommended), or Nginx on ECS


### Prerequisites
- AWS account with admin access (for setup) and the AWS CLI configured
- Docker installed locally (for image builds)
- Node 18+ and npm (for local frontend builds)
- Domain in Route 53 (optional but recommended)


### Backend (FastAPI on ECS Fargate)

1) Build and push container image
- Docker Hub example:
```bash
# from repo root
docker build -t your-dockerhub-username/rag-backend:latest backend

docker push your-dockerhub-username/rag-backend:latest
```
- Using ECR (recommended):
```bash
aws ecr create-repository --repository-name rag-backend || true
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)
ECR_URI=${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/rag-backend

aws ecr get-login-password | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

docker build -t rag-backend:latest backend

docker tag rag-backend:latest ${ECR_URI}:latest

docker push ${ECR_URI}:latest
```

2) Networking
- Create or reuse a VPC with public subnets (for ALB) and private subnets (optional for tasks)
- Create a security group for the ALB (inbound 80/443 from Internet)
- Create a security group for ECS tasks (inbound 8000 from the ALB SG)

3) Persistence for PDFs and reports
- EFS:
  - Create EFS filesystem and an access point
  - In the ECS Task Definition, add an EFS volume and mount it to `/app/data` and `/app/reports`
- S3 (recommended for PDFs):
  - Upload PDFs to an S3 bucket
  - Update the backend to load PDFs from S3 at startup or on reload (optional enhancement)

4) ECS Task Definition (Fargate)
- Launch type: Fargate
- Task size: e.g., 0.5 vCPU / 1GB RAM (adjust as needed)
- Container image: the ECR/DockerHub image from step 1
- Port mapping: container port 8000 TCP
- Env vars:
  - `OLLAMA_BASE_URL` (point to your LLM server; if not running Ollama in AWS, use a managed LLM and adjust code accordingly)
  - `OLLAMA_LLM_MODEL` (e.g., `llama3.1`)
  - `OLLAMA_EMBED_MODEL` (e.g., `nomic-embed-text`)
- Volumes: attach EFS volumes if used

5) ECS Service
- Cluster: create an ECS Cluster (Fargate)
- Service: desired count: 1+ (scale later)
- Load Balancer: attach an ALB target group (port 8000)
- Health check path: `/health`
- Deployment: rolling update

6) Application Load Balancer
- Create an ALB with listeners:
  - 80 -> redirect to 443
  - 443 -> forward to backend target group
- ACM: request/validate a certificate for `api.yourdomain.com`
- Route 53: create an `A` alias record `api.yourdomain.com` -> ALB


### Frontend (S3 + CloudFront)

1) Build
- Build via Dockerfile or node locally:
```bash
# local build
cd frontend
npm ci
# set API base so the UI calls your backend ALB/Domain
# Windows PowerShell: $env:VITE_API_BASE = "https://api.yourdomain.com"
# macOS/Linux: export VITE_API_BASE=https://api.yourdomain.com
npm run build
```
- Artifacts are in `frontend/dist/`.

2) S3 bucket
- Create an S3 bucket (e.g., `rag-frontend-prod`)
- Keep bucket private if using CloudFront (recommended)
- Upload `frontend/dist/` to the bucket:
```bash
aws s3 sync frontend/dist/ s3://rag-frontend-prod/ --delete
```

3) CloudFront distribution
- Origin: the S3 bucket (use OAC)
- Default behavior: GET/HEAD allowed, caching enabled
- Optional: set `index.html` short TTLs; long TTLs for hashed assets
- Custom domain: `app.yourdomain.com` with ACM cert
- Route 53: `CNAME` to the CloudFront domain


### Alternative Frontend: Nginx on ECS
- Build and push: `docker build -t your-account/rag-frontend:latest frontend && docker push ...`
- ECS Task Definition: container port 80
- ECS Service behind ALB listener on 80/443 (separate target group from backend)


### CORS and environment
- Backend CORS currently allows all origins. In production, restrict `allow_origins` to your frontend domain
- Frontend: set `VITE_API_BASE` to the backend public URL at build time


### CI/CD (optional)
- Backend:
  - GitHub Actions or CodePipeline to build/push to ECR and run `aws ecs update-service --force-new-deployment`
- Frontend:
  - Build with `VITE_API_BASE` from environment
  - `aws s3 sync dist/ s3://<bucket>/ --delete`
  - `aws cloudfront create-invalidation --distribution-id <ID> --paths "/*"`


### Local Development
```bash
# from repo root
# Backend (Docker)
docker build -t rag-backend:dev backend

docker run --rm -p 8000:8000 rag-backend:dev

# Frontend (local dev)
cd frontend
npm ci
# Windows PowerShell: $env:VITE_API_BASE = "http://127.0.0.1:8000"
# macOS/Linux: export VITE_API_BASE=http://127.0.0.1:8000
npm run dev -- --host --port 8080
```


### Troubleshooting
- ALB health checks failing: confirm target group port (8000) and `/health` path
- 403/AccessDenied on S3: use CloudFront, keep bucket private, add OAC (Origin Access Control)
- CORS errors: restrict/allow `allow_origins` appropriately in the backend
- PDFs not found: ensure EFS mounted to `/app/data` or migrate PDFs to S3 and adjust loader


—
This document covers a standard, secure baseline. Adjust sizing, scaling, and security per your org’s requirements.
