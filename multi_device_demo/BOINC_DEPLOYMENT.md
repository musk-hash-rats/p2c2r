# 🌍 BOINC-Style Deployment Guide

## Overview

Deploy P2C2R like BOINC - one central server, contributors and gamers connect from anywhere.

## Architecture

```
Contributor (Device 1)          Cloud Server (Device 2)         Gamer (Device 3)
    USA                              AWS                             Europe
     |                                |                                |
     |------ Internet (WS) ----------|------- Internet (WS) ----------|
     |                                |                                |
  Provides compute              Routes & stores                   Uses compute
  Earns $0.15/hr               Takes 10% fee                    Pays $0.01/hr
```

## Deployment Options

### Option 1: Cloud Server (Recommended for Production)

**Providers:**
- AWS EC2 (t3.small = $15/month)
- DigitalOcean Droplet ($12/month)
- Linode ($10/month)
- Your own server with public IP

**Setup:**

```bash
# 1. Launch server (Ubuntu 22.04 recommended)

# 2. Install Python and dependencies
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install websockets

# 3. Upload P2C2R code
scp -r multi_device_demo user@YOUR_SERVER_IP:~/

# 4. Open firewall
sudo ufw allow 8765
sudo ufw enable

# 5. Start cloud coordinator
cd multi_device_demo
python3 run_cloud.py

# 6. Optional: Run as service (systemd)
sudo cp p2c2r-cloud.service /etc/systemd/system/
sudo systemctl enable p2c2r-cloud
sudo systemctl start p2c2r-cloud
```

**DNS Setup (Optional but Recommended):**
```bash
# Point domain to server IP
# Example: p2c2r.yourcompany.com -> 203.0.113.42

# Then users can connect with:
# python3 run_peer.py --cloud-ip p2c2r.yourcompany.com
```

### Option 2: ngrok (Testing Only)

**Perfect for testing before getting a server:**

```bash
# 1. Sign up at ngrok.com (free)

# 2. Download ngrok
# macOS:
brew install ngrok
# Linux:
snap install ngrok

# 3. Authenticate
ngrok config add-authtoken YOUR_TOKEN

# 4. Start P2C2R cloud
cd multi_device_demo
python3 run_cloud.py

# 5. In another terminal, expose it:
ngrok tcp 8765

# You'll see:
# Forwarding: tcp://0.tcp.ngrok.io:12345 -> localhost:8765

# 6. Share this address with contributors and gamers:
# python3 run_peer.py --cloud-ip 0.tcp.ngrok.io --cloud-port 12345
```

**ngrok Limitations:**
- URL changes every restart (free tier)
- Limited bandwidth
- Not for production use
- Great for testing!

### Option 3: Home Server with Port Forwarding

**If you have a home server with static IP:**

```bash
# 1. Configure router port forwarding:
#    External Port: 8765
#    Internal IP: Your server's local IP
#    Internal Port: 8765

# 2. Find your public IP:
curl ifconfig.me

# 3. Start cloud coordinator
cd multi_device_demo
python3 run_cloud.py

# 4. Share your public IP with users
# python3 run_peer.py --cloud-ip YOUR_PUBLIC_IP
```

**Considerations:**
- Residential IP might be dynamic (changes)
- ISP might block ports
- Use dynamic DNS (DynDNS, No-IP) for stability

## Security (Important!)

### Current Demo Security:
⚠️ **NO AUTHENTICATION** - Anyone can connect!

### Before Production, Add:

1. **API Keys**
```python
# Require peers/gamers to authenticate
# Add to registration messages:
{
    "type": "register_peer",
    "peer_id": "peer_001",
    "api_key": "your-secret-key-here"
}
```

2. **SSL/TLS**
```python
# Use wss:// instead of ws://
# Get free SSL cert from Let's Encrypt
# Use nginx as reverse proxy
```

3. **Rate Limiting**
```python
# Limit connections per IP
# Prevent abuse
```

4. **Payment Integration**
```python
# Stripe/PayPal for gamer payments
# Crypto for peer payouts
```

## Cost Analysis (BOINC Style)

### Your Server Costs:
- **AWS t3.small**: $15/month (handles 100+ concurrent peers)
- **Bandwidth**: ~$0.09/GB (minimal for task data)
- **Database**: Free (SQLite) or $10/mo (managed PostgreSQL)
- **Total**: ~$25-50/month to start

### Revenue Model:
- Gamers pay: $0.01/hour
- Peers earn: $0.15/hour (of compute they provide)
- Your cut: 10% = $0.001/hour per gamer

**Break-even:** ~2,500 gamer-hours/month = 84 gamers playing 30 hours/month

### Scale Example:
- **1,000 active gamers** (10 hrs/mo each)
- **10,000 gamer-hours/month**
- **Revenue**: $100/month
- **Your profit**: $10/month (after peer payments + server costs)

**At scale (10K gamers):**
- **100,000 gamer-hours/month**
- **$1,000/month revenue**
- **~$100/month profit** (need bigger server ~$200/mo)

## Monitoring & Management

### Essential Tools:

**1. Monitor Cloud Server:**
```bash
# Watch connections
tail -f cloud_logs.txt

# Check database
sqlite3 p2c2r_cloud.db "SELECT COUNT(*) FROM tasks"

# Monitor resources
htop
```

**2. Set Up Alerts:**
```bash
# Email when cloud goes down
# Alert when peer count drops
# Notify on high latency
```

**3. Track Economics:**
```bash
# Total revenue
sqlite3 p2c2r_cloud.db "SELECT SUM(cost_usd) FROM tasks"

# Top peers by earnings
sqlite3 p2c2r_cloud.db "SELECT peer_id, total_earned_usd FROM peers ORDER BY total_earned_usd DESC LIMIT 10"
```

## Contributor Onboarding (BOINC Style)

### Make It Easy:

**1. One-Line Install (Future):**
```bash
curl https://p2c2r.com/install.sh | bash
# Automatically installs, connects, starts earning
```

**2. Desktop App (Future):**
- Windows/Mac/Linux app
- Shows earnings dashboard
- One-click start/stop
- Auto-updates

**3. Web Dashboard (Future):**
- Contributors see: earnings, tasks completed, uptime
- Gamers see: spending, savings vs GPU, task history

## Testing Your BOINC-Style Setup

### Test 1: Local Testing
```bash
# All on one machine with ngrok
python3 run_cloud.py
# In another terminal: ngrok tcp 8765
# In another terminal: python3 run_peer.py --cloud-ip 0.tcp.ngrok.io --cloud-port XXXX
# In another terminal: python3 run_gamer.py --cloud-ip 0.tcp.ngrok.io --cloud-port XXXX
```

### Test 2: Friend Testing
```bash
# You run cloud on AWS
# Friend 1 runs peer from their house
# Friend 2 runs gamer from their house
# All connect over internet!
```

### Test 3: Geographic Testing
```bash
# Cloud in US East
# Peer in Europe
# Gamer in Asia
# Measure latency and performance across continents
```

## Next Steps

1. **Test with ngrok** (5 minutes)
   ```bash
   python3 run_cloud.py
   ngrok tcp 8765
   # Share ngrok URL with friends!
   ```

2. **Deploy to AWS/DigitalOcean** (30 minutes)
   - Launch cheapest server
   - Install code
   - Open port 8765
   - Done!

3. **Add your first contributor** (5 minutes)
   - Give them: `python3 run_peer.py --cloud-ip YOUR_IP`
   - Watch them earn money!

4. **Add your first gamer** (5 minutes)
   - Give them: `python3 run_gamer.py --cloud-ip YOUR_IP`
   - Watch them save money!

## The BOINC Comparison

| Feature | BOINC | P2C2R |
|---------|-------|-------|
| Contributors earn? | No (volunteer) | Yes ($0.15/hr) |
| Central server? | Yes | Yes |
| Open to anyone? | Yes | Yes (with auth) |
| Internet-based? | Yes | Yes |
| Purpose | Science | Gaming compute |
| Scale | Millions | Starting small |

**P2C2R = BOINC + Payments + Gaming Focus** 🚀

---

**Ready to deploy?** Start with ngrok testing, then move to AWS when ready!
