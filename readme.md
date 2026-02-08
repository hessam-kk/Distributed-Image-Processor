# 📸 Kubernetes Microservices Image Processor

A distributed image processing application built with **Python (Flask)** and **Redis**, designed to run on **Kubernetes**.

This project demonstrates core cloud-native concepts including:

* **Microservices Architecture** (Orchestrator + Workers)
* **Inter-service Communication** (HTTP/REST)
* **State Management** (Redis)
* **Horizontal Scaling** (Demonstrated via load testing)
* **Observability** (Tracking which Pod processed a request)

---

## 🏗 Architecture

The application is decomposed into 4 separate components:

1. **Web API (Orchestrator):**
* Entry point for users.
* Handles routing and pipelines (e.g., "Apply Blur -> Then Apply B&W").
* Exposed via NodePort/LoadBalancer.


2. **Blur Service (Worker):**
* Performs CPU-intensive image blurring.
* Contains an artificial delay (2s) to simulate heavy load for scaling demos.
* Returns the processed image + the **Pod Name** in headers for tracking.


3. **B&W Service (Worker):**
* Converts images to grayscale.


4. **Redis (Database):**
* Stores the final processed images with a UUID key.



---

## 📋 Prerequisites

* **Docker** (Desktop or Engine)
* **Kubernetes Cluster** (Minikube, or Docker Desktop)
* **kubectl** CLI tool
* **Python 3.9** (for running the pods and load test script)
* **WSL 2** (If on Windows)

---

## 🚀 Setup & Installation

### 1. Configure Docker Environment (WSL/Minikube Only)

If you are using Minikube, you must point your terminal to Minikube's internal Docker daemon so it can see the images you build.

```bash
eval $(minikube docker-env)

```

*(Skip this if using Docker Desktop or Kind).*

### 2. Build the Docker Images

Build the images for each service. Note the tags used in the Kubernetes manifests.

```bash
docker build -t web-api:latest ./web-api
docker build -t blur-processor:latest ./blur-processor
docker build -t bw-processor:latest ./bw-processor

```

### 3. Deploy to Kubernetes

Apply the configuration files to start the Deployments and Services.

```bash
kubectl apply -f k8s/

```

### 4. Verify Deployment

Check that all pods are running:

```bash
kubectl get pods

```

*Status should be `Running` for all pods.*

---

## 📡 Usage

### Accessing the API

Since the service is running inside the cluster, you need to expose it. The most reliable method (especially in WSL) is **Port Forwarding**.

Open a **separate terminal** and run:

```bash
# Forward local port 5000 to the Web API service
kubectl port-forward svc/web-api-service 5000:5000

```

If that does not work for any reason, the other alternative is to run the command and use the output ip:

```bash
minikube service web-api-service --url

```


### 1. Upload an Image

You can apply `blur`, `bw`, or both (comma-separated).

```bash
curl -X POST -F "file=@test.jpg" -F "effects=bw,blur" http://localhost:5000/upload

```

**Response:**

```json
{
  "id": "a1b2c3d4-...",
  "applied_effects": ["bw", "blur"],
  "processed_by_pod": "blur-deployment-xyz",
  "view_url": "/image/a1b2c3d4-..."
}

```

### 2. View the Result

Open your browser and navigate to:
`http://localhost:5000/image/<YOUR_IMAGE_ID>`

---

## ⚖️ Horizontal Scaling Demonstration

This project includes a stress test to demonstrate the power of Kubernetes Horizontal Pod Autoscaling.

### The Experiment

We will compare processing **20 concurrent requests** with **1 replica** vs **4 replicas**.

**Prerequisite:** Ensure `load_test.sh` is executable (`chmod +x load_test.sh`) and your port-forward is running.

### Scenario A: The Bottleneck (1 Pod)

1. Scale down the blur service (the default):
```bash
kubectl scale deployment blur --replicas=1

```


2. Run the load test:
```bash
./load_test.sh

```


3. **Result:** ~40-50 seconds. Requests queue up and are processed sequentially.

### Scenario B: Unleashing the Cluster (4 Pods)

1. Scale up the blur service:
```bash
kubectl scale deployment blur --replicas=4

```


2. **Wait** 15 seconds for pods to initialize (`kubectl get pods`).
3. Run the load test again:
```bash
./load_test.sh

```


4. **Result:** ~20-25 seconds. Requests are distributed in parallel across 4 pods.

**Visual Proof:**
The load test script prints the **Pod Name** that handled each request. In Scenario B, you will see a variety of pod names, proving the load balancer is working.

---

## 📂 Project Structure

```text
/
├── k8s/                    # Kubernetes Manifests
│   ├── redis.yaml          # Redis Deployment + Service
│   ├── web-api.yaml        # Web API Deployment + Service
│   ├── blur.yaml           # Blur Worker Deployment + Service
│   └── bw.yaml             # B&W Worker Deployment + Service
│
├── web-api/                # API Gateway Code
│   ├── app.py              # Flask app with Gunicorn (Orchestrator)
│   └── Dockerfile
│
├── blur-processor/         # Blur Worker Code
│   ├── app.py              # Flask app with simulated delay
│   └── Dockerfile
│
├── bw-processor/           # B&W Worker Code
│   ├── app.py              # Standard Flask app
│   └── Dockerfile
│
├── load_test.sh            # Bash script for concurrent load testing
└── README.md

```

---

