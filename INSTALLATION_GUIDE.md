# Installation Method Comparison

Choose the best installation method for your needs.

## Quick Comparison

| Feature | Native Installation | Docker Installation |
|---------|-------------------|-------------------|
| **Setup Time** | 5-10 minutes | 2-3 minutes |
| **Dependencies** | Manual (auto-installed) | None (containerized) |
| **System Impact** | Direct installation | Isolated containers |
| **Resource Usage** | Lower overhead | Slightly higher |
| **Portability** | System-specific | Works everywhere |
| **Development** | ✅ Excellent | ⚠️ Good |
| **Production** | ⚠️ Good | ✅ Excellent |
| **Cleanup** | Manual uninstall | One command |
| **Updates** | Package updates | Image rebuild |
| **Debugging** | Direct access | Container access |

---

## Native Installation

### ✅ Choose Native If:

- You're developing/testing locally
- You want direct file access
- You prefer traditional server setup
- You're comfortable with Linux administration
- You want lower resource overhead
- You have specific system requirements

### Installation

```bash
cd /app/scripts
./install.sh
```

The installer will:
- ✅ Auto-detect if Python 3 or Node.js are missing
- ✅ Offer to install missing dependencies automatically
- ✅ Install Python 3.11+ and Node.js 18.x
- ✅ Set up Python virtual environment
- ✅ Install all required packages
- ✅ Configure MongoDB
- ✅ Create necessary directories

### Pros

- **Direct Access**: Full control over all files and processes
- **Performance**: No containerization overhead (~5-10% faster)
- **Debugging**: Easier to debug with direct access
- **Flexibility**: Can customize any aspect of the system
- **Hot Reload**: Faster development cycle
- **System Integration**: Direct systemd integration

### Cons

- **Dependencies**: Requires Python, Node.js, MongoDB installation
- **Conflicts**: Potential version conflicts with other software
- **Cleanup**: More effort to completely remove
- **Portability**: May behave differently on different systems
- **Security**: Runs with system-level access

### Best For

- Development environments
- Testing and debugging
- Single-server deployments
- Resource-constrained systems
- Long-term production with stable configuration

---

## Docker Installation

### ✅ Choose Docker If:

- You want quick deployment
- You're deploying to production
- You need environment isolation
- You want easy cleanup/removal
- You're deploying to multiple servers
- You want consistent environments

### Installation

```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com | sh

# Deploy
cd /app
docker-compose up -d
```

### Pros

- **Isolated Environment**: No dependency conflicts
- **Consistency**: Same environment everywhere
- **Quick Setup**: Running in 2-3 minutes
- **Easy Cleanup**: `docker-compose down -v` removes everything
- **Portability**: Works on any Docker-enabled system
- **Security**: Containerized isolation
- **Rollback**: Easy to revert versions
- **Scaling**: Simple horizontal scaling

### Cons

- **Resource Overhead**: Extra ~5-10% CPU/memory usage
- **Complexity**: Need to understand Docker basics
- **File Access**: Requires volume mounts for direct access
- **Debugging**: Slightly more complex (container access)
- **Network**: Additional network layer

### Best For

- Production deployments
- Multi-server environments
- CI/CD pipelines
- Testing different versions
- Temporary/disposable environments
- Cloud deployments (AWS, Azure, GCP)

---

## Hybrid Approach

You can use both methods for different purposes:

### Development → Production Pipeline

```bash
# Development (Native)
./install.sh --auto
# Code, test, debug locally

# Production (Docker)
docker-compose up -d
# Deploy to servers
```

### Benefits

- **Dev Speed**: Native installation for faster iteration
- **Prod Safety**: Docker for isolated, reproducible deployments
- **Best of Both**: Optimal for each use case

---

## Migration Between Methods

### Native → Docker

```bash
# Backup your data
cd /app/scripts
./backup.sh migration-backup

# Stop native services
sudo systemctl stop tactical-backend tactical-frontend

# Start Docker
cd /app
docker-compose up -d

# Restore data (optional)
./restore.sh migration-backup
```

### Docker → Native

```bash
# Backup from Docker
docker exec tactical-mongodb mongodump --out=/backup
docker cp tactical-mongodb:/backup ./mongodb-backup

# Stop Docker
docker-compose down

# Install natively
cd /app/scripts
./install.sh --auto

# Restore data
mongorestore --dir=./mongodb-backup
```

---

## System Requirements

### Native Installation

**Required:**
- Linux (Ubuntu 20.04+)
- Python 3.11+
- Node.js 16+
- MongoDB 4.4+
- 2GB RAM minimum

**Installation Size:**
- ~500MB for dependencies
- ~200MB for application
- ~100MB for MongoDB data

### Docker Installation

**Required:**
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum (for containers)

**Installation Size:**
- ~1GB for Docker images
- ~100MB for MongoDB data
- Additional ~200MB for volumes

---

## Performance Comparison

### Native Installation

```
Startup Time: ~5 seconds
API Response: ~50ms
Memory Usage: ~500MB
CPU Usage: 10-15%
```

### Docker Installation

```
Startup Time: ~10 seconds
API Response: ~55ms (5ms overhead)
Memory Usage: ~700MB (container overhead)
CPU Usage: 12-18% (slight overhead)
```

**Note:** Performance differences are minimal and often negligible in real-world usage.

---

## Security Considerations

### Native Installation

- Runs with system user privileges (www-data)
- Direct access to system resources
- Systemd security features (PrivateTmp, etc.)
- Firewall rules recommended

### Docker Installation

- Container isolation by default
- Network segmentation
- Limited system access
- Security through isolation
- User namespaces available

**Winner:** Docker provides better security through isolation.

---

## Recommendation Matrix

| Use Case | Recommended Method |
|----------|-------------------|
| Local Development | **Native** |
| Production Server | **Docker** |
| Multi-Server Deploy | **Docker** |
| Testing/Staging | **Docker** |
| Resource Limited | **Native** |
| Learning/Education | **Native** |
| Enterprise Deploy | **Docker** |
| Cloud Platforms | **Docker** |
| Single VPS | Either |
| Bare Metal | Either |

---

## Still Can't Decide?

### Start with Docker if:
- You're new to server administration
- You want the quickest path to production
- You value convenience over customization

### Start with Native if:
- You're developing/testing frequently
- You want to learn the full stack
- You have specific system requirements

### Remember:
- You can always switch methods later
- Both methods are fully supported
- Both provide the same features
- The panel works identically in both

---

## Getting Help

- **Installation Issues**: Check logs in `/app/install.log`
- **Docker Problems**: Run `docker-compose logs`
- **Native Issues**: Check `journalctl -u tactical-backend`
- **General Help**: See README.md or DEPLOYMENT.md

---

**Quick Start:**

```bash
# Docker (Production)
docker-compose up -d

# Native (Development)
./scripts/install.sh --auto
```

Choose what works best for you. Both methods are production-ready! 🚀
