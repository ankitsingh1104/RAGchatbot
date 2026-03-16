# Kubernetes Pods

A Pod is the smallest deployable unit in Kubernetes. It represents a single instance of a running process in your cluster. Pods contain one or more containers that share storage and network resources.

## Creating a Pod

Use kubectl to create a pod:
kubectl run nginx --image=nginx

## Pod Lifecycle

Pods go through several phases: Pending, Running, Succeeded, Failed, and Unknown. The kubelet manages the pod lifecycle on each node.

## Deployments

A Deployment provides declarative updates for Pods. You describe the desired state in a Deployment and the Deployment Controller changes the actual state to match at a controlled rate.

kubectl create deployment nginx --image=nginx
kubectl get deployments
kubectl scale deployment nginx --replicas=3
