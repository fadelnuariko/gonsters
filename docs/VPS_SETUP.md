# VPS Server Setup Guide

## Current Status ✅

Your VPS already has the application running! Here's what's deployed:

```
CONTAINER          STATUS              PORTS
gonsters-backend   Up 2 hours (healthy)   0.0.0.0:5000->5000/tcp
gonsters-postgres  Up 2 hours (healthy)   0.0.0.0:5432->5432/tcp
gonsters-redis     Up 2 hours (healthy)   0.0.0.0:6379->6379/tcp
gonsters-influxdb  Up 2 hours (healthy)   0.0.0.0:8086->8086/tcp
gonsters-mosquitto Up 2 hours (healthy)   0.0.0.0:1883->1883/tcp, 0.0.0.0:9001->9001/tcp
```

## What You Need to Do for Auto-Deployment

### 1. Find Your Repository Location

SSH into your VPS and find where the code is:

```bash
ssh fadel@YOUR_VPS_IP

# Find the gonsters directory
find ~ -name "gonsters" -type d 2>/dev/null
# OR
pwd  # if you're already in the directory
```

Common locations:
- `/home/fadel/gonsters`
- `/opt/gonsters`
- `~/gonsters`

### 2. Ensure Git is Set Up

```bash
cd /path/to/gonsters  # use the path you found above

# Check if it's a git repository
git status

# If not initialized, clone it:
git clone https://github.com/fadelnuariko/gonsters.git
cd gonsters
```

### 3. Generate SSH Key for GitHub Actions

```bash
# Generate a dedicated key for deployments
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy -N ""

# Add public key to authorized_keys
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
chmod 600 ~/.ssh/github_deploy
chmod 644 ~/.ssh/github_deploy.pub

# Display the private key (you'll need to copy this)
cat ~/.ssh/github_deploy
```

**Copy the entire output** (including `-----BEGIN` and `-----END` lines)

### 4. Add GitHub Secrets

Go to: `https://github.com/fadelnuariko/gonsters/settings/secrets/actions`

Add these secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `VPS_HOST` | Your VPS IP or domain | `123.45.67.89` |
| `VPS_USERNAME` | Your SSH username | `fadel` |
| `VPS_SSH_KEY` | Private key from step 3 | `-----BEGIN OPENSSH...` |
| `VPS_PORT` | SSH port | `22` |

### 5. Test the Setup

```bash
# From your local machine, test SSH with the new key
ssh -i ~/.ssh/github_deploy fadel@YOUR_VPS_IP

# If it connects without password, you're good! ✅
```

### 6. Trigger Auto-Deployment

Once secrets are configured, any push to `master` will automatically:

1. ✅ Run tests
2. ✅ Run security scans
3. ✅ SSH into your VPS
4. ✅ Pull latest code
5. ✅ Rebuild Docker containers
6. ✅ Restart services
7. ✅ Verify health

```bash
# Make any change and push
git add .
git commit -m "test: trigger auto-deployment"
git push origin master

# Watch the deployment at:
# https://github.com/fadelnuariko/gonsters/actions
```

## Troubleshooting

### If deployment fails:

```bash
# Check container logs
docker logs gonsters-backend

# Check all containers
docker-compose ps

# Restart manually
docker-compose down
docker-compose up -d
```

### If SSH fails:

```bash
# Verify SSH key is in authorized_keys
cat ~/.ssh/authorized_keys | grep github-actions

# Check SSH service
sudo systemctl status sshd
```

## Next Steps

After auto-deployment is working:
- [ ] Set up Nginx reverse proxy (optional)
- [ ] Configure SSL with Let's Encrypt (optional)
- [ ] Set up monitoring and alerts
- [ ] Configure automated backups
