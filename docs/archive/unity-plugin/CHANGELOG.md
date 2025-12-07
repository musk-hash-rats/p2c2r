# P2C2R Unity Plugin Changelog

All notable changes to the Unity plugin will be documented in this file.

---

## [0.1.0] - 2025-12-06

### 🎉 Initial Release

#### Added
- **P2C2RClient** - Main WebSocket client for Unity
  - Singleton pattern for easy access
  - Auto-connect and auto-reconnect
  - Task submission API (AI, ray tracing, physics)
  - Async/await support
  - Callback support
  - Debug stats overlay
  - Connection management

- **P2C2RNPC** - AI-powered NPC component
  - Dialogue generation via P2C2R
  - Configurable personality and context
  - Response caching
  - Local fallback support
  - Unity Events integration

- **P2C2RRayTracing** - Ray tracing enhancement component
  - Offload ray tracing to peers
  - Progressive rendering
  - Configurable quality/performance
  - Blend with local rendering
  - Target FPS control

- **Editor Tools**
  - Quick setup menu items
  - Settings window
  - Custom inspectors
  - Test connection tools
  - Documentation links

- **Documentation**
  - Complete README with API reference
  - Quick Start Guide
  - Usage examples
  - Best practices
  - Troubleshooting guide

#### Features
- ✅ WebSocket-based communication
- ✅ Async task submission
- ✅ Automatic reconnection
- ✅ Graceful degradation
- ✅ Performance monitoring
- ✅ Unity 2020.3+ support
- ✅ Easy integration (3-5 minutes)

#### Known Limitations
- JSON parsing uses Unity's JsonUtility (limited)
- Ray tracing blend shader is simplified
- No binary protocol yet (JSON only)
- No result caching beyond NPC dialogue
- No multi-coordinator support

---

## [Planned for 0.2.0]

### Upcoming Features
- [ ] Better JSON parsing (Newtonsoft.Json or System.Text.Json)
- [ ] Result caching system
- [ ] Task priority queues
- [ ] Binary protocol support (MessagePack)
- [ ] Multi-coordinator support (fallback)
- [ ] Peer reputation/preference
- [ ] Texture streaming for ray tracing
- [ ] Physics state interpolation
- [ ] Profiler integration
- [ ] Sample scenes
- [ ] Video tutorials
- [ ] Performance dashboard
- [ ] Mobile support (iOS/Android)

### Bug Fixes
- Fix WebSocket thread safety issues
- Improve error handling
- Better connection retry logic

---

## [Planned for 0.3.0]

### Advanced Features
- [ ] Task splitting (use multiple peers)
- [ ] Predictive task submission
- [ ] ML-based task scheduling
- [ ] Shader integration (render pipeline)
- [ ] VR/XR support
- [ ] Multiplayer support
- [ ] Cloud save/load
- [ ] Analytics integration

---

## Development Notes

### Version Strategy
- **0.1.x** - Initial release, bug fixes, stability
- **0.2.x** - Core features, performance improvements
- **0.3.x** - Advanced features, integrations
- **1.0.0** - Production-ready, stable API

### Compatibility
- Unity 2020.3 LTS and newer
- Tested on: Windows, macOS, Linux
- Supported render pipelines: Built-in, URP, HDRP

---

## Feedback

Have suggestions? Found a bug? Want a feature?

- **GitHub Issues:** https://github.com/musk-hash-rats/p2c2r/issues
- **GitHub Discussions:** https://github.com/musk-hash-rats/p2c2r/discussions

We'd love to hear from you! 🎮
