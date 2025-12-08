# Legal Compliance & Open Source Requirements

## ⚖️ Project Policy: Open Source Only

**CRITICAL**: This project uses ONLY open-source, permissively licensed components to avoid legal issues.

## ✅ Current Dependencies (All Safe)

### Core Python Libraries
- **Python 3.x** - PSF License (permissive, open source)
- **asyncio** - Python standard library (PSF License)
- **websockets** - BSD 3-Clause License ✓
- **sqlite3** - Public domain ✓
- **json, time, random, logging** - Python standard library (PSF License)

### Testing & Development
- **pytest** - MIT License ✓
- **Flask** - BSD 3-Clause License ✓
- **tkinter** - Python standard library (PSF License)

### Future Additions (Pre-Approved)
- **NumPy** - BSD License ✓
- **PyTorch** - BSD-style License ✓
- **TensorFlow** - Apache 2.0 License ✓
- **Redis** - BSD 3-Clause License ✓
- **FastAPI** - MIT License ✓
- **Let's Encrypt** - Free SSL certificates (open source) ✓

## 🚫 What to AVOID

### Proprietary Software
- ❌ Commercial game engines without proper licensing
- ❌ Proprietary networking libraries
- ❌ Closed-source ML models with restrictive licenses
- ❌ Premium cloud services that require paid API keys

### Legally Ambiguous
- ❌ Copied code without attribution
- ❌ Reverse-engineered game protocols (DMCA violations)
- ❌ Scraped data from protected sources
- ❌ Libraries with "commercial use prohibited" clauses

### Patent-Encumbered Technologies
- ❌ Avoid any patented codecs or algorithms
- ✅ Use only open-source, royalty-free alternatives
- ✅ Check for patent grants in licenses (Apache 2.0 includes this)

## 📋 License Compatibility Guide

### ✅ Safe Licenses (Compatible)
- **MIT License** - Most permissive, allows commercial use
- **Apache 2.0** - Permissive, includes patent grant
- **BSD 2/3-Clause** - Permissive, minimal restrictions
- **PSF License** - Python software, very permissive
- **MPL 2.0** - Mozilla, file-level copyleft (OK to use)
- **Public Domain** - No restrictions

### ⚠️ Use with Care (Copyleft)
- **GPL v2/v3** - Strong copyleft, requires entire project to be GPL
  - **Our Policy**: Avoid unless absolutely necessary
  - If used, must open-source entire project
- **LGPL** - Lesser GPL, OK for libraries (linking allowed)
  - Can use LGPL libraries without viral effect

### ❌ Never Use
- **Proprietary/Commercial** - Requires paid license
- **"Non-commercial use only"** - Blocks our business model
- **"Academic use only"** - Blocks commercial deployment
- **Unlicensed code** - No license = no permission to use

## 🔍 Before Adding ANY Dependency

**Check these 3 things:**

1. **License Type**
   ```bash
   # Check on PyPI
   pip show <package-name>
   # Look for: License: MIT / BSD / Apache 2.0
   ```

2. **Commercial Use Allowed**
   - Read LICENSE file in repository
   - Ensure "commercial use" is permitted
   - Check for hidden restrictions

3. **Attribution Requirements**
   - Some licenses require crediting authors
   - Keep track in `ATTRIBUTIONS.md`

## 📝 Our Project License

**Recommendation**: MIT or Apache 2.0

### Why MIT?
- ✅ Most permissive
- ✅ Allows commercial use
- ✅ Allows modification
- ✅ No copyleft (users can keep modifications private)
- ✅ Simple and widely understood

### Why Apache 2.0?
- ✅ Includes explicit patent grant (protects against patent trolls)
- ✅ Still very permissive
- ✅ Better for projects with potential patent issues

**Current Status**: Need to add LICENSE file to repository

## 🎮 Game-Specific Considerations

### Safe Approaches
- ✅ Build our own game protocols (no legal issues)
- ✅ Use open game engines (Godot = MIT license)
- ✅ Synthetic benchmarks (our own code)
- ✅ Open datasets (ImageNet, COCO, etc. with proper licenses)

### Avoid
- ❌ Hooking into commercial games (EULA violations)
- ❌ Intercepting game network traffic (ToS violations)
- ❌ Modifying game executables (DMCA violations)
- ❌ Using game assets without permission

## 🌐 Distributed Computing - Legal Considerations

### Our Approach
- ✅ Building from scratch with original code
- ✅ Using open distributed computing concepts (not copyrighted)
- ✅ No code copied from other projects
- ✅ "Distributed" = architectural pattern, not code theft

### What We Can Do
- ✅ Study distributed computing architectures (public knowledge)
- ✅ Implement similar patterns (architectural concepts not copyrighted)
- ✅ Use standard networking protocols (WebSockets, TCP/IP)
- ✅ Reference concepts for comparison (fair use)

### What We Cannot Do
- ❌ Copy source code from other projects
- ❌ Use others' trademarks in confusing way
- ❌ Claim affiliation with other projects

## 💰 Payment Processing (Future)

### Open Source Options
- **Stripe** - API is free to use, just pay transaction fees ✓
- **PayPal** - Same model as Stripe ✓
- **Cryptocurrency** - Open protocols (Bitcoin, Ethereum) ✓
  - Use: web3.py (MIT), bitcoinlib (MIT)

### Avoid
- ❌ Proprietary payment SDKs with restrictive licenses

## 🔐 Security & Cryptography

### Safe Options
- **cryptography** (Python) - Apache 2.0 + BSD ✓
- **OpenSSL** - Apache 2.0 ✓
- **libsodium** - ISC License ✓

## 📊 Monitoring & Analytics

### Safe Options
- **Prometheus** - Apache 2.0 ✓
- **Grafana** - AGPL (OK for hosting, not embedding) ✓
- **ELK Stack** - Elastic License 2.0 (permissive for our use) ✓

## ✅ Compliance Checklist

Before launching:

- [ ] Add LICENSE file (MIT or Apache 2.0)
- [ ] Create ATTRIBUTIONS.md listing all dependencies
- [ ] Audit all dependencies for license compatibility
- [ ] Remove any proprietary code or assets
- [ ] Ensure no game EULA violations
- [ ] Review ToS for any cloud services used
- [ ] Patent search (optional but recommended)
- [ ] Trademark search for project name

## 🚨 Red Flags to Watch For

When reviewing code/libraries:

- "For evaluation purposes only"
- "Academic/research use only"
- "Non-commercial license"
- "Contact us for commercial licensing"
- No LICENSE file in repository
- "All rights reserved" without license
- Code from game mods (often derivative works)

## 📞 When in Doubt

If unsure about a dependency:

1. Check: https://choosealicense.com/
2. Check: https://opensource.org/licenses
3. Ask on: r/opensource, r/legaladvice
4. Consult: Lawyer (if significant risk)

## 🎯 Bottom Line

**Always err on the side of caution.** If a library's license is unclear or restrictive, find an open-source alternative. The open-source ecosystem is vast - there's almost always a permissively-licensed option.

---

**Last Updated**: December 7, 2025
**Status**: All current dependencies verified ✓
**Next Review**: Before adding any new dependencies
