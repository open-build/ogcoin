# ForgeWeb Operations

This directory contains deployment and infrastructure files for ForgeWeb.

## Files Overview

### Docker Deployment
- **`Dockerfile`** - Container definition for ForgeWeb
- **`docker-compose.yml`** - Multi-service orchestration with optional services
- **`nginx.conf`** - Reverse proxy configuration for production
- **`requirements.txt`** - Python dependencies

### Kubernetes Deployment  
- **`kubernetes.yaml`** - Complete Kubernetes deployment with PVC, ConfigMap, Service, and Ingress

## Quick Deployment

### Docker (Single Container)
```bash
# Build and run ForgeWeb container
docker build -f ops/Dockerfile -t forgeweb .
docker run -d -p 8000:8000 -v $(pwd)/content:/app/content forgeweb
```

### Docker Compose (Recommended)
```bash
# Start ForgeWeb with all services
docker-compose -f ops/docker-compose.yml up -d

# With production profile (includes nginx)
docker-compose -f ops/docker-compose.yml --profile production up -d

# With database (for analytics)
docker-compose -f ops/docker-compose.yml --profile database up -d
```

### Kubernetes
```bash
# Deploy to Kubernetes cluster
kubectl apply -f ops/kubernetes.yaml

# Check deployment status
kubectl get pods -n forgeweb
kubectl get services -n forgeweb
```

## Configuration Options

### Environment Variables
- **`PORT`** - Server port (default: 8000)
- **`PYTHONUNBUFFERED`** - Enable unbuffered Python output
- **`FORGEWEB_CONFIG`** - Path to custom configuration file

### Volume Mounts
- **`/app/content`** - Generated site content (articles, pages)
- **`/app/assets`** - Media files and images
- **`/app/admin/site-config.json`** - Site configuration

### Docker Compose Profiles
- **`default`** - ForgeWeb container only
- **`production`** - Includes nginx reverse proxy
- **`database`** - Adds PostgreSQL for analytics

## Production Setup

### SSL/HTTPS Configuration
1. Update `nginx.conf` with your domain and SSL certificates
2. Place SSL certificates in `ops/ssl/` directory
3. Enable the HTTPS server block in nginx configuration

### Scaling and Load Balancing
```bash
# Scale ForgeWeb containers
docker-compose -f ops/docker-compose.yml up -d --scale forgeweb=3

# Kubernetes scaling
kubectl scale deployment forgeweb --replicas=5 -n forgeweb
```

### Monitoring and Logs
```bash
# View logs
docker-compose -f ops/docker-compose.yml logs -f forgeweb

# Kubernetes logs
kubectl logs -f deployment/forgeweb -n forgeweb
```

## Security Considerations

### Container Security
- Runs as non-root user (`appuser`)
- Minimal base image (python:3.11-slim)
- Regular security updates for dependencies
- Health checks for container monitoring

### Network Security
- Rate limiting configured in nginx
- Security headers for XSS/CSRF protection
- HTTPS enforcement in production
- Network isolation with Docker networks

### Data Protection
- Persistent volumes for data storage
- Regular backup strategies recommended
- Environment-based configuration management

## Backup and Recovery

### Data Backup
```bash
# Backup content directory
docker run --rm -v forgeweb_content:/backup -v $(pwd):/host alpine tar czf /host/backup.tar.gz /backup

# Kubernetes backup
kubectl exec -n forgeweb deployment/forgeweb -- tar czf - /app/content > backup.tar.gz
```

### Configuration Backup
```bash
# Backup site configuration
cp admin/site-config.json backups/site-config-$(date +%Y%m%d).json
```

## Troubleshooting

### Common Issues

**Container won't start**
```bash
# Check logs
docker logs <container-id>

# Verify port availability
netstat -tlnp | grep :8000
```

**Permission errors**
```bash
# Fix file permissions
sudo chown -R 1000:1000 ./content
```

**Resource constraints**
```bash
# Monitor resource usage
docker stats

# Kubernetes resource monitoring
kubectl top pods -n forgeweb
```

### Health Checks
- **HTTP**: `curl -f http://localhost:8000/admin/`
- **Docker**: Built-in health check every 30 seconds
- **Kubernetes**: Liveness and readiness probes configured

## Development

### Local Development with Docker
```bash
# Development mode with live reload
docker-compose -f ops/docker-compose.dev.yml up

# Mount source code for development
docker run -it -p 8000:8000 -v $(pwd):/app forgeweb bash
```

### Building Custom Images
```bash
# Build with custom tag
docker build -f ops/Dockerfile -t your-registry/forgeweb:custom .

# Multi-arch build
docker buildx build --platform linux/amd64,linux/arm64 -t forgeweb:multiarch .
```

---

**Need help with deployment?** Check the [deployment documentation](../docs/DEPLOYMENT.md) or get [support](https://buildly.io/support).