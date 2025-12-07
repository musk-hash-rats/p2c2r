# P2C2R Unity Plugin - Complete Integration Guide

**Turn your Unity game into a P2C2R-powered experience in under 30 minutes.**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Basic Setup](#basic-setup)
4. [Integration Patterns](#integration-patterns)
5. [Testing & Debugging](#testing--debugging)
6. [Production Deployment](#production-deployment)
7. [FAQ](#faq)

---

## Prerequisites

### Required
- **Unity 2020.3 LTS** or newer
- **P2C2R Network** running (local or remote)
  - Cloud coordinator
  - At least 1 peer node
- **WebSocket support** (built into Unity)

### Recommended
- Basic C# knowledge
- Familiarity with Unity components
- Understanding of async/await

---

## Installation Methods

### Method 1: Unity Package Manager (Recommended)

**Best for:** Production use, auto-updates

```
1. Open Unity Package Manager (Window > Package Manager)
2. Click "+" in top-left
3. Select "Add package from git URL..."
4. Enter: https://github.com/musk-hash-rats/p2c2r.git?path=/unity-plugin
5. Click "Add"
6. Wait for import (30-60 seconds)
```

**Verify installation:**
- Check Package Manager shows "P2C2R Compute Assist"
- Menu bar should have new option: "GameObject > P2C2R"

---

### Method 2: Local Package (Development)

**Best for:** Plugin development, offline work

```bash
# Clone repository
git clone https://github.com/musk-hash-rats/p2c2r.git
cd p2c2r

# Copy plugin to your Unity project
cp -r unity-plugin /path/to/YourUnityProject/Packages/com.p2c2r.compute-assist
```

**Verify installation:**
- Unity will auto-detect the package
- Check Packages folder in Project window
- Look for "P2C2R Compute Assist" package

---

### Method 3: Asset Package (.unitypackage)

**Best for:** Sharing with team, asset store

```
Coming soon! Will be available at:
- Unity Asset Store
- GitHub Releases
```

---

## Basic Setup

### Step 1: Start P2C2R Network

**Option A: Local Testing (Development)**

```bash
cd /path/to/p2c2r
./run_network.sh
```

**Option B: Remote Server (Production)**

```bash
# On your cloud server
python network/cloud_coordinator.py

# Get your server IP
curl ifconfig.me
# Example: 203.0.113.5
```

---

### Step 2: Add P2C2R Client to Scene

**Quick Method:**
```
Right-click in Hierarchy
→ GameObject
→ P2C2R
→ Add P2C2R Client
```

**Manual Method:**
```
1. Create Empty GameObject
2. Rename to "P2C2RClient"
3. Add Component → P2C2RClient
```

---

### Step 3: Configure Connection

Select `P2C2RClient` in Hierarchy, then in Inspector:

**For Local Testing:**
```
Coordinator URL: ws://localhost:8765
Auto Connect: ✓
Auto Reconnect: ✓
Enable Debug Logs: ✓
Show Stats: ✓
```

**For Remote Server:**
```
Coordinator URL: ws://203.0.113.5:8765
(Replace with your server IP)
```

---

### Step 4: Test Connection

```
1. Enter Play Mode
2. Check Console for:
   "[P2C2R] ✓ Connected to P2C2R coordinator"
3. Check Game view top-left for stats overlay
4. Verify "Connected: ✓"
```

✅ **Success!** You're connected to P2C2R.

---

## Integration Patterns

### Pattern 1: AI NPC Dialogue

**Use Case:** Offload dialogue generation to cloud AI

**Implementation:**

```csharp
using UnityEngine;
using P2C2R;

public class MyNPC : MonoBehaviour
{
    private P2C2RNPC npc;

    void Start()
    {
        // Add P2C2RNPC component
        npc = gameObject.AddComponent<P2C2RNPC>();
        
        // Configure
        npc.npcName = "Village Elder";
        npc.personality = "Wise old man who speaks in riddles";
        npc.aiModel = "npc_dialogue";
        
        // Listen for responses
        npc.onDialogueReceived.AddListener(OnDialogue);
    }

    public void OnPlayerInteract(string playerSays)
    {
        // Request AI-generated response
        npc.GenerateDialogue(playerSays);
    }

    void OnDialogue(string npcResponse)
    {
        // Display in UI
        DialogueUI.Show(npcResponse);
        
        // Trigger voice synthesis
        VoiceSystem.Speak(npcResponse);
    }
}
```

**Quick Setup Alternative:**
```
1. Right-click in Hierarchy → GameObject → P2C2R → Create AI NPC
2. Configure personality in Inspector
3. Call GenerateDialogue() from your interaction system
```

---

### Pattern 2: Enhanced Graphics (Ray Tracing)

**Use Case:** Add ray tracing to existing scenes

**Implementation:**

```csharp
using UnityEngine;
using P2C2R;

public class GraphicsEnhancer : MonoBehaviour
{
    void Start()
    {
        // Add ray tracing to main camera
        Camera mainCam = Camera.main;
        P2C2RRayTracing rt = mainCam.gameObject.AddComponent<P2C2RRayTracing>();
        
        // Configure
        rt.enableRayTracing = true;
        rt.sceneComplexity = 150;
        rt.numLights = 3;
        rt.targetRayTracingFPS = 30;
        rt.blendFactor = 0.8f;
    }
}
```

**Quick Setup Alternative:**
```
Menu: GameObject → P2C2R → Add Ray Tracing to Camera
```

**Result:**
- Game runs at full 60fps locally
- Ray tracing applied 3-4 frames later (imperceptible)
- Quality improves progressively

---

### Pattern 3: Custom Task Submission

**Use Case:** Offload custom compute tasks

**Example: Pathfinding**

```csharp
using UnityEngine;
using P2C2R;
using System.Collections.Generic;

public class PathfindingSystem : MonoBehaviour
{
    public async void FindPath(Vector3 start, Vector3 goal)
    {
        // Create task data
        var taskData = new Dictionary<string, object>
        {
            { "type", "pathfinding" },
            { "start", new float[] { start.x, start.y, start.z } },
            { "goal", new float[] { goal.x, goal.y, goal.z } },
            { "map_size", new int[] { 100, 100 } }
        };

        // Submit to P2C2R
        var result = await P2C2RClient.Instance.SubmitTask(taskData);

        if (result.success)
        {
            // Parse path from result
            Vector3[] path = ParsePath(result.data);
            
            // Move character along path
            MoveAlongPath(path);
        }
    }

    Vector3[] ParsePath(string data)
    {
        // Parse JSON path data
        // Return array of waypoints
        return new Vector3[0]; // Implement parsing
    }
}
```

---

### Pattern 4: Procedural Generation

**Use Case:** Generate content using cloud compute

**Example: Dungeon Generation**

```csharp
using UnityEngine;
using P2C2R;
using System.Collections.Generic;

public class DungeonGenerator : MonoBehaviour
{
    public async void GenerateDungeon(int size, string theme)
    {
        var input = new Dictionary<string, object>
        {
            { "size", size },
            { "theme", theme },
            { "seed", Random.Range(0, 10000) }
        };

        // Offload generation to P2C2R
        var result = await P2C2RClient.Instance.SubmitAITask(
            "dungeon_generation",
            input
        );

        if (result.success)
        {
            // Build dungeon from result
            BuildDungeon(result.data);
        }
    }

    void BuildDungeon(string data)
    {
        // Parse dungeon layout
        // Instantiate rooms, corridors, enemies
    }
}
```

---

## Testing & Debugging

### Debug Mode

Enable detailed logging:

```csharp
P2C2RClient.Instance.enableDebugLogs = true;
P2C2RClient.Instance.showStats = true;
```

**Console Output:**
```
[P2C2R] Connecting to coordinator...
[P2C2R] ✓ Connected
[P2C2R] ✓ Registration confirmed
[P2C2R] Task submitted: ai_inference (abc123...)
[P2C2R] ✓ Task completed: abc123 (0.15s)
```

---

### Stats Overlay

Enable in Inspector or code:

```csharp
P2C2RClient.Instance.showStats = true;
```

**Displays:**
- Connection status
- Tasks sent/completed/failed
- Pending tasks
- Average latency

---

### Test Connection

**In Editor:**
```
1. Select P2C2RClient in Hierarchy
2. Inspector → Runtime Controls
3. Click "Connect" button
4. Click "Test AI Task" or "Test Ray Tracing Task"
```

**In Code:**
```csharp
if (P2C2RClient.Instance.IsConnected)
{
    Debug.Log("✓ P2C2R is connected and ready!");
}
else
{
    Debug.LogWarning("✗ P2C2R not connected. Check coordinator.");
}
```

---

### Common Issues

**"WebSocket connection failed"**
```
Fix:
1. Verify network is running: ./run_network.sh
2. Check coordinator URL in Inspector
3. Test with: telnet localhost 8765
4. Check firewall settings
```

**"Task never completes"**
```
Fix:
1. Check peers are running
2. View coordinator logs
3. Verify task type is supported by peers
4. Check network latency
```

**"Poor performance"**
```
Fix:
1. Reduce targetRayTracingFPS (try 15-20)
2. Lower sceneComplexity
3. Disable stats overlay in production
4. Only offload truly heavy tasks
```

---

## Production Deployment

### Checklist

**Before shipping:**

- [ ] Disable debug logs: `enableDebugLogs = false`
- [ ] Hide stats overlay: `showStats = false`
- [ ] Set production coordinator URL
- [ ] Test with various network conditions
- [ ] Implement graceful degradation
- [ ] Add analytics/telemetry
- [ ] Test on target hardware
- [ ] Verify fallback behavior works
- [ ] Load test with multiple users
- [ ] Security audit (if using custom tasks)

---

### Best Practices

**1. Always Provide Fallback**
```csharp
if (P2C2RClient.Instance.IsConnected)
{
    await UseP2C2R();
}
else
{
    UseLocalFallback();
}
```

**2. Cache Expensive Results**
```csharp
Dictionary<string, string> cache = new Dictionary<string, string>();

async Task<string> GetDialogue(string input)
{
    if (cache.ContainsKey(input))
        return cache[input];
    
    var result = await SubmitAITask(input);
    cache[input] = result.data;
    return result.data;
}
```

**3. Handle Timeouts**
```csharp
using System.Threading.Tasks;

async Task<TaskResult> SubmitWithTimeout(float timeoutSeconds)
{
    var task = P2C2RClient.Instance.SubmitAITask(...);
    var timeout = Task.Delay((int)(timeoutSeconds * 1000));
    
    if (await Task.WhenAny(task, timeout) == timeout)
    {
        // Timeout - use fallback
        return null;
    }
    
    return await task;
}
```

---

### Performance Optimization

**Batch Requests:**
```csharp
// Instead of 10 small requests:
foreach (var npc in npcs)
{
    await SubmitAITask(npc); // DON'T DO THIS
}

// Do 1 batched request:
var batch = npcs.Select(n => n.input).ToList();
await SubmitBatchAITask(batch);
```

**Predictive Loading:**
```csharp
// Submit task BEFORE you need it
void OnPlayerApproachingArea()
{
    // Player is 5 seconds away
    StartPreloadingArea();
}

async void StartPreloadingArea()
{
    // Result arrives just as player enters
    var result = await SubmitTask(...);
    CacheResult(result);
}
```

---

## FAQ

**Q: Can I use P2C2R in production?**  
A: The plugin is currently v0.1.0 (alpha). Suitable for prototypes and MVPs. Production-ready features coming in v1.0.0.

**Q: Does it work on mobile?**  
A: WebSocket support on iOS/Android is planned for v0.2.0. Currently desktop only.

**Q: What about multiplayer games?**  
A: Works great! Each player connects to P2C2R independently. Multiplayer support planned for v0.3.0.

**Q: Can I run my own coordinator?**  
A: Yes! See [network/README.md](../../network/README.md) for deployment guide.

**Q: How much does it cost?**  
A: For users: $5-10/month. For peers: earn $8-16/month. Platform takes 25% fee.

**Q: Is my game data secure?**  
A: Tasks are sandboxed. No game assets are transmitted. Only task parameters and results.

**Q: Can I contribute?**  
A: Yes! Open issues and PRs on GitHub. See CONTRIBUTING.md.

---

## Next Steps

1. ✅ **Install plugin** (you've done this!)
2. 📖 **Read the [README](README.md)** for full API reference
3. 🎮 **Try the examples** (AI NPC, Ray Tracing)
4. 🚀 **Build something cool!**
5. 💬 **Share your creation** on GitHub Discussions or Twitter

---

## Support

**Need help?**

- 📖 Documentation: [README.md](README.md)
- 💬 Discussions: https://github.com/musk-hash-rats/p2c2r/discussions
- 🐛 Issues: https://github.com/musk-hash-rats/p2c2r/issues

**Want to contribute?**

- Check open issues
- Fork and submit PRs
- Share feedback
- Report bugs

---

**Happy developing! 🎮✨**
