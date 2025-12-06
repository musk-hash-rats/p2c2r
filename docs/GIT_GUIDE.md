# Git Commands Reference for P2C2G

## First Time Setup - Pushing to GitHub

### Step 1: Configure Git Identity
```bash
git config user.name "musk-hash-rats"
git config user.email "your-email@example.com"
```

### Step 2: Stage All Files
```bash
git add .
```

### Step 3: Create Initial Commit
```bash
git commit -m "feat: initial P2C2G proof of concept implementation

Complete distributed computing simulation with:
- Peer agent with latency and reliability modeling
- Coordinator with intelligent task scheduling
- Automatic failover and retry mechanism
- Comprehensive test suite
- CI/CD pipeline
- Full documentation
- Proprietary license"
```

### Step 4: Create GitHub Repository

1. Go to https://github.com
2. Log in to "musk-hash-rats" account
3. Click "+" → "New repository"
4. Repository name: **p2c2r**
5. Description: **Peer-to-Cloud-to-Gamer: Distributed Computing Proof of Concept**
6. Visibility: **Private** (recommended)
7. **Do NOT** check any initialization boxes
8. Click "Create repository"

### Step 5: Add Remote and Push
```bash
# Add remote
git remote add origin https://github.com/musk-hash-rats/p2c2r.git

# Verify remote
git remote -v

# Set main branch
git branch -M main

# Push to GitHub
git push -u origin main
```

When prompted for credentials:
- Username: `musk-hash-rats` or your GitHub username
- Password: Use a **Personal Access Token** (not your password)

### Creating a Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "P2C2G Development"
4. Expiration: Choose duration
5. Scopes: Check `repo` (full control)
6. Click "Generate token"
7. **COPY THE TOKEN** (you won't see it again!)
8. Use this token as your password when pushing

## Daily Workflow

### Making Changes
```bash
# Check what changed
git status

# Stage specific files
git add src/p2c2g/coordinator.py

# Or stage all changes
git add .

# Commit with message
git commit -m "feat: add new feature"

# Push to GitHub
git push
```

### Creating a Feature Branch
```bash
# Create and switch to new branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: implement feature"

# Push branch to GitHub
git push -u origin feature/your-feature-name

# Switch back to main
git checkout main
```

### Pulling Latest Changes
```bash
# Update main branch
git checkout main
git pull origin main
```

### Viewing History
```bash
# Show commit history
git log

# Show recent commits (prettier)
git log --oneline --graph --decorate --all

# Show changes in last commit
git show
```

### Undoing Changes
```bash
# Discard unstaged changes to a file
git checkout -- filename

# Unstage a file (keep changes)
git reset HEAD filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - CAREFUL!
git reset --hard HEAD~1
```

## Common Scenarios

### Forgot to Add Files to Commit
```bash
git add forgotten-file.py
git commit --amend --no-edit
git push --force  # Only if not shared with others!
```

### Wrong Commit Message
```bash
git commit --amend -m "Better commit message"
git push --force  # Only if not shared with others!
```

### Check Differences
```bash
# Show unstaged changes
git diff

# Show staged changes
git diff --staged

# Compare with another branch
git diff main..feature-branch
```

### Stash Changes Temporarily
```bash
# Save changes for later
git stash

# List stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{0}
```

### Tagging Releases
```bash
# Create annotated tag
git tag -a v0.1.0 -m "Initial release"

# Push tags to GitHub
git push origin --tags

# List tags
git tag -l
```

## Troubleshooting

### Authentication Failed
```bash
# Make sure you're using Personal Access Token, not password
# Or switch to SSH authentication (see docs/GITHUB_SETUP.md)
```

### Push Rejected (Non-Fast-Forward)
```bash
# Pull first, then push
git pull origin main --rebase
git push origin main
```

### Merge Conflicts
```bash
# Pull latest changes
git pull origin main

# Git will mark conflicts in files
# Edit files to resolve conflicts
# Look for markers: <<<<<<< HEAD, =======, >>>>>>>

# After resolving conflicts:
git add .
git commit -m "fix: resolve merge conflicts"
git push
```

### Accidentally Committed to Wrong Branch
```bash
# On wrong branch:
git log  # Note the commit hash

# Switch to correct branch
git checkout correct-branch

# Cherry-pick the commit
git cherry-pick <commit-hash>

# Go back and reset wrong branch
git checkout wrong-branch
git reset --hard HEAD~1
```

## Git Aliases (Optional Time-Savers)

Add to your `~/.gitconfig`:

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --oneline --graph --decorate --all
    amend = commit --amend --no-edit
```

Then use:
```bash
git st        # instead of git status
git co main   # instead of git checkout main
git visual    # pretty log view
```

## Quick Reference Card

| Command | Description |
|---------|-------------|
| `git status` | Show working tree status |
| `git add <file>` | Stage file for commit |
| `git add .` | Stage all changes |
| `git commit -m "msg"` | Commit staged changes |
| `git push` | Push commits to remote |
| `git pull` | Fetch and merge from remote |
| `git checkout <branch>` | Switch branches |
| `git checkout -b <branch>` | Create and switch to branch |
| `git branch` | List branches |
| `git log` | Show commit history |
| `git diff` | Show unstaged changes |
| `git stash` | Temporarily save changes |
| `git stash pop` | Restore stashed changes |

## Need Help?

- Git basics: https://git-scm.com/book/en/v2
- GitHub guides: https://guides.github.com/
- Git cheatsheet: https://education.github.com/git-cheat-sheet-education.pdf
