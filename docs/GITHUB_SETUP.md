# GitHub Setup Guide

This guide will help you push your P2C2G project to GitHub under the "musk-hash-rats" account.

## Prerequisites

- Git installed on your system
- GitHub account "musk-hash-rats" created
- Terminal/command line access

## Initial Setup

### 1. Initialize Git Repository (if not already done)

```bash
cd /Users/robertgreenwood/P2c2gPOC
git init
```

### 2. Configure Git User

Set your Git username and email for this repository:

```bash
git config user.name "musk-hash-rats"
git config user.email "your-email@example.com"  # Replace with your GitHub email
```

### 3. Create Repository on GitHub

1. Go to https://github.com
2. Log in to the "musk-hash-rats" account
3. Click the "+" icon in the top right
4. Select "New repository"
5. Repository name: `p2c2r`
6. Description: "Peer-to-Cloud-to-Gamer: Distributed Computing Proof of Concept"
7. Choose "Private" (recommended due to proprietary license)
8. **DO NOT** initialize with README, .gitignore, or license (we already have these)
9. Click "Create repository"

### 4. Add Remote and Push

After creating the repository on GitHub, run these commands:

```bash
# Add the remote repository
git remote add origin https://github.com/musk-hash-rats/p2c2r.git

# Verify the remote was added
git remote -v

# Add all files to staging
git add .

# Create initial commit
git commit -m "feat: initial P2C2G proof of concept implementation

- Add peer agent with latency and reliability simulation
- Add coordinator with task scheduling and failover
- Add renter client interface
- Add comprehensive test suite
- Add CI/CD pipeline with GitHub Actions
- Add documentation and examples
- Add proprietary license"

# Push to GitHub (use 'main' as default branch)
git branch -M main
git push -u origin main
```

### 5. Authentication

When pushing, you'll be prompted for credentials. You have two options:

#### Option A: Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "P2C2G Development"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token (you won't see it again!)
7. When prompted for password, paste the token

#### Option B: SSH Key

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy the public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# 1. Go to GitHub Settings → SSH and GPG keys
# 2. Click "New SSH key"
# 3. Paste the public key
# 4. Save

# Update remote to use SSH
git remote set-url origin git@github.com:musk-hash-rats/p2c2r.git
```

## Repository Structure

Your GitHub repository will contain:

```
P2c2gPOC/
├── .github/
│   ├── workflows/
│   │   └── ci.yml                 # CI/CD pipeline
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   ├── copilot-instructions.md
│   └── pull_request_template.md
├── src/p2c2g/                     # Main package
├── tests/                         # Test suite
├── docs/                          # Documentation
├── examples/                      # Usage examples
├── README.md                      # Main documentation
├── LICENSE                        # Proprietary license
├── CONTRIBUTING.md                # Contribution guidelines
├── setup.py                       # Package setup
├── requirements.txt               # Dependencies
├── requirements-dev.txt           # Dev dependencies
├── pyproject.toml                 # Project metadata
└── .gitignore                     # Git ignore rules
```

## Ongoing Development

### Create a New Branch

```bash
git checkout -b feature/your-feature-name
```

### Make Changes and Commit

```bash
git add .
git commit -m "feat: add new feature"
git push origin feature/your-feature-name
```

### Create Pull Request

1. Go to your repository on GitHub
2. Click "Pull requests" tab
3. Click "New pull request"
4. Select your feature branch
5. Fill in the PR template
6. Click "Create pull request"

### Keep Main Branch Updated

```bash
git checkout main
git pull origin main
```

## GitHub Features to Enable

### 1. Branch Protection

Settings → Branches → Add rule:
- Branch name pattern: `main`
- ✓ Require pull request reviews before merging
- ✓ Require status checks to pass before merging
- ✓ Require branches to be up to date before merging

### 2. Enable GitHub Actions

- Go to Actions tab
- Enable workflows
- CI will run automatically on push and PR

### 3. Add Repository Secrets (Optional)

For advanced CI features:
Settings → Secrets and variables → Actions
- Add `CODECOV_TOKEN` if using Codecov
- Add other secrets as needed

### 4. Setup GitHub Pages (Optional)

For documentation hosting:
Settings → Pages
- Source: Deploy from a branch
- Branch: `main` / docs folder

## Troubleshooting

### Authentication Failed

```bash
# Use personal access token instead of password
# Or switch to SSH authentication (see above)
```

### Permission Denied

```bash
# Ensure you're logged in to correct account
git config user.name
git config user.email
```

### Push Rejected

```bash
# Pull latest changes first
git pull origin main --rebase
git push origin main
```

## Next Steps

After pushing to GitHub:

1. ✓ Verify all files are visible on GitHub
2. ✓ Check CI/CD pipeline runs successfully
3. ✓ Add repository description and topics
4. ✓ Add collaborators if needed
5. ✓ Setup branch protection rules
6. ✓ Review and update README with GitHub badges

## GitHub Repository Settings

Recommended settings for your repository:

- **Visibility**: Private (due to proprietary license)
- **Features**: 
  - ✓ Issues
  - ✓ Projects (optional)
  - ✓ Wiki (optional)
  - ✓ Discussions (optional)
- **Security**: 
  - ✓ Dependabot alerts
  - ✓ Code scanning
