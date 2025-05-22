#!/usr/bin/env bash
set -e

if ! kubectl get namespace istio-system &>/dev/null; then
  istioctl install --set profile=default -y
fi

kubectl label namespace default istio-injection=enabled --overwrite

docker build -t custom-app:latest .

kubectl apply -f config-map.yaml
kubectl apply -f test-pod.yaml
kubectl wait --for=condition=Ready pod/app-test-pod --timeout=60s

kubectl port-forward pod/app-test-pod 5000:5000 &
PF_PID=$!
sleep 5
curl http://localhost:5000/
curl http://localhost:5000/status
curl -X POST -H "Content-Type: application/json" -d '{"message":"Test message"}' http://localhost:5000/log
curl http://localhost:5000/logs
kill $PF_PID

kubectl apply -f app-deployment.yaml
kubectl apply -f app-service.yaml
kubectl wait --for=condition=Available deployment/custom-app --timeout=60s
kubectl apply -f log-agent-daemonset.yaml
kubectl apply -f log-archive-cronjob.yaml

kubectl port-forward svc/custom-app-service 8080:80 &
PF_PID=$!
sleep 5
curl http://localhost:8080/
curl http://localhost:8080/status
curl -X POST -H "Content-Type: application/json" -d '{"message":"Service test"}' http://localhost:8080/log
curl http://localhost:8080/logs
kill $PF_PID

kubectl apply -f istio/gateway.yaml
kubectl apply -f istio/virtualservice.yaml
kubectl apply -f istio/destinationrule-app-service.yaml
kubectl apply -f istio/destinationrule-log-service.yaml
