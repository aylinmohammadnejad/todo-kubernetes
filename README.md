#  To-Do List App with Docker & Kubernetes

A simple yet powerful To-Do List web application built using **Python Flask**, containerized with **Docker**, and deployed to a local **Kubernetes cluster (Minikube)**. This project demonstrates application packaging, orchestration, auto-scaling, and health checks in a microservices environment.

---

##  Tech Stack

- Python 3 + Flask
- HTML (Jinja templates)
- Docker
- Kubernetes (Minikube)
- Horizontal Pod Autoscaler (HPA)
- Liveness & Readiness Probes

---

##  Features

- Add/Delete to-do tasks
- Runs locally or in Kubernetes
- Horizontal pod auto-scaling
- Liveness & readiness health endpoints
- CPU resource limits for autoscaler
- Dockerized application

---

##  Project Structure

```
.
├── app.py
├── requirements.txt
├── Dockerfile
├── templates/
│   └── index.html
├── todo-deployment.yaml
├── todo-service.yaml
└── README.md
```

---

##  Run with Docker

```bash
docker build -t todo-app .
docker run -p 5000:5000 todo-app
```

Visit: [http://localhost:5000](http://localhost:5000)

---

##  Deploy with Kubernetes + Minikube

1. Start Minikube:
```bash
minikube start
```

2. (Optional) Use Minikube's Docker environment:
```bash
& minikube -p minikube docker-env | Invoke-Expression
docker build -t todo-app .
```

3. Apply deployment and service:
```bash
kubectl apply -f todo-deployment.yaml
kubectl apply -f todo-service.yaml
```

4. Access the app:
```bash
minikube service todo-service
```

---

##  Enable Auto-scaling (HPA)

1. Enable metrics-server:
```bash
minikube addons enable metrics-server
```

2. Add autoscaler:
```bash
kubectl autoscale deployment todo-app --cpu-percent=50 --min=2 --max=5
```

3. Check status:
```bash
kubectl get hpa
```

---

##  Health Probes

Health check endpoint implemented at `/health`:
- Used in Kubernetes `livenessProbe` and `readinessProbe`

---

##  Author

**Aylin Mohammadnejad**  
[GitHub Profile](https://github.com/aylinmohammadnejad)

---

##  License

This project is for educational purposes only.
