# Chatbot Helm Chart

This Helm chart deploys a complete AI Chatbot application with frontend and backend services to Kubernetes.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (optional, for persistent storage)

## Installation

### Install the chart

```bash
helm install my-chatbot ./helm-chatbot
```

The command deploys the chatbot on the Kubernetes cluster with the default configuration.

### Install with custom values

```bash
helm install my-chatbot ./helm-chatbot --set frontend.replicas=3
```

Or provide a custom values file:

```bash
helm install my-chatbot ./helm-chatbot -f custom-values.yaml
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicas` | Number of frontend replicas | `1` |
| `frontend.image.repository` | Frontend image repository | `chatbot-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.image.pullPolicy` | Frontend image pull policy | `Never` |
| `frontend.service.type` | Frontend service type | `LoadBalancer` |
| `frontend.service.port` | Frontend service port | `80` |
| `backend.replicas` | Number of backend replicas | `1` |
| `backend.image.repository` | Backend image repository | `chatbot-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.image.pullPolicy` | Backend image pull policy | `Never` |
| `backend.service.type` | Backend service type | `ClusterIP` |
| `backend.service.port` | Backend service port | `80` |
| `secrets.databaseUrl` | Database connection string | `postgresql://...` |
| `secrets.openaiApiKey` | OpenAI API key | `AIza...` |
| `secrets.openaiBaseUrl` | OpenAI base URL | `https://...` |
| `secrets.jwtSecretKey` | JWT secret key | `your-secret-key` |
| `secrets.betterAuthSecret` | Better Auth secret | `super-duper-auth-secret` |
| `config.openaiModel` | OpenAI model to use | `gemini-2.5-flash` |
| `config.accessTokenExpireMinutes` | Access token expiry (minutes) | `60` |
| `config.environment` | Environment | `development` |
| `config.skipAuth` | Skip authentication | `false` |
| `config.corsOrigins` | CORS allowed origins | `http://localhost...` |
| `config.logLevel` | Log level | `INFO` |

Specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example:

```bash
helm install my-chatbot ./helm-chatbot --set frontend.replicas=3,backend.replicas=2
```

Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart:

```bash
helm install my-chatbot ./helm-chatbot -f custom-values.yaml
```

## Upgrading

To upgrade the release:

```bash
helm upgrade my-chatbot ./helm-chatbot
```

## Uninstalling

To uninstall/delete the deployment:

```bash
helm uninstall my-chatbot
```

## Security Considerations

**IMPORTANT:** The default values in `values.yaml` contain placeholder secrets. Before deploying to production:

1. Update all secret values in `values.yaml`
2. Consider using external secret management (e.g., HashiCorp Vault, AWS Secrets Manager)
3. Use Helm's `--set` or `--set-file` to provide secrets at deployment time:

```bash
helm install my-chatbot ./helm-chatbot \
  --set secrets.openaiApiKey="your-actual-key" \
  --set secrets.jwtSecretKey="your-actual-secret"
```

## Resource Management

The chart allows you to set resource requests and limits. Edit the `values.yaml` file or use `--set` to configure:

```yaml
frontend:
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 250m
      memory: 256Mi

backend:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

## Troubleshooting

Get the status of your release:

```bash
helm status my-chatbot
```

View all resources:

```bash
helm get all my-chatbot
```

Check pod logs:

```bash
kubectl logs -n default -l "app.kubernetes.io/instance=my-chatbot,component=backend"
kubectl logs -n default -l "app.kubernetes.io/instance=my-chatbot,component=frontend"
```
