# GitHub Secrets Setup Guide

## Required Secrets for VPS Deployment

You need to add these secrets to your GitHub repository for auto-deployment to work.

### How to Add Secrets

1. Go to your GitHub repository: `https://github.com/fadelnuariko/gonsters`
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below

---

## Secrets to Add

### 1. VPS_HOST
**Value:** Your VPS IP address or domain
```
Example: 123.45.67.89
Or: vmi2239445.contaboserver.net
```

### 2. VPS_USERNAME
**Value:** Your SSH username (from your VPS info: `fadel`)
```
fadel
```

### 3. VPS_SSH_KEY
**Value:** Your SSH private key

**How to get it:**

```bash
# On your VPS (you're already logged in as fadel@vmi2239445)
# Generate a new SSH key for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/github_deploy -N ""

# Add the public key to authorized_keys
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys

# Display the private key (copy ALL of this)
cat ~/.ssh/github_deploy
```

Copy the **entire output** including:
```
-----BEGIN OPENSSH PRIVATE KEY-----
... (all lines)
-----END OPENSSH PRIVATE KEY-----
```

Paste this into the `VPS_SSH_KEY` secret.

### 4. VPS_PORT (Optional)
**Value:** SSH port (default is 22)
```
22
```

---

## Verify Repository Path

The workflow assumes your code is in one of these locations on the VPS:
- `~/gonsters`
- `/opt/gonsters`
- `/home/fadel/gonsters`

**Check where your code is:**
```bash
# On your VPS
pwd
# If you're in the gonsters directory, note the full path
```

If it's in a different location, let me know and I'll update the workflow.

---

## Test SSH Connection

After adding the secrets, test the connection:

```bash
# From your local machine
ssh -i ~/.ssh/github_deploy fadel@YOUR_VPS_IP

# If it works without password, you're good!
```

---

## Summary Checklist

- [ ] Add `VPS_HOST` secret (your VPS IP)
- [ ] Add `VPS_USERNAME` secret (`fadel`)
- [ ] Generate SSH key on VPS
- [ ] Add public key to `authorized_keys`
- [ ] Add `VPS_SSH_KEY` secret (private key)
- [ ] Add `VPS_PORT` secret (`22`)
- [ ] Verify repository path on VPS
- [ ] Push code to trigger deployment

Once all secrets are added, push any change to the `master` branch and GitHub Actions will automatically deploy to your VPS! 🚀
