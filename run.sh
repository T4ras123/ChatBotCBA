minikube start
docker build -t chatbot-cba:latest .
kubectl apply -f k8s/videos-configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/role.yaml
kubectl apply -f k8s/rolebinding.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/pvc.yaml
