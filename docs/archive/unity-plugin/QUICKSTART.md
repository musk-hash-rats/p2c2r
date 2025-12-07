# Unity Plugin Quick Start Guide

Get P2C2R working in your Unity game in 5 minutes!

---

## Prerequisites

- Unity 2020.3 or later
- P2C2R network running locally (or remote coordinator URL)

---

## Step 1: Start P2C2R Network (30 seconds)

Open terminal and run:

```bash
cd /path/to/P2c2gPOC
./run_network.sh
```

You should see:
```
✓ P2C2R NETWORK RUNNING
  • Cloud Coordinator: localhost:8765
  • Peer Nodes: 3
  • User Client: demo_user (demo mode)
```

Leave this running in the background.

---

## Step 2: Add Plugin to Unity (1 minute)

### Option A: Git URL (Recommended)
1. Open Unity Package Manager (Window > Package Manager)
2. Click "+" → "Add package from git URL"
3. Enter: `https://github.com/musk-hash-rats/p2c2r.git?path=/unity-plugin`
4. Click "Add"

### Option B: Local Install
1. Copy `P2c2gPOC/unity-plugin` folder
2. Paste into your Unity project's `Packages` directory
3. Unity auto-detects and imports

---

## Step 3: Add P2C2R to Scene (30 seconds)

### Quick Method:
1. Right-click in Hierarchy
2. Select: `GameObject > P2C2R > Add P2C2R Client`
3. Done! (uses default settings)

### Manual Method:
1. Create empty GameObject
2. Add `P2C2RClient` component
3. Set Coordinator URL: `ws://localhost:8765`
4. Enable "Auto Connect"

---

## Step 4: Test Connection (1 minute)

1. **Enter Play Mode** (press Play button)
2. **Check Console** - You should see:
   ```
   [P2C2R] Connecting to P2C2R coordinator: ws://localhost:8765
   [P2C2R] ✓ Connected to P2C2R coordinator
   [P2C2R] ✓ Registration confirmed by coordinator
   ```
3. **Check Stats Overlay** (top-left corner):
   ```
   P2C2R Stats
   Connected: ✓
   Tasks Sent: 0
   Tasks Completed: 0
   ...
   ```

✅ **Success!** P2C2R is connected and ready.

---

## Step 5: Try Your First Task (2 minutes)

### Example: AI NPC Dialogue

Create a simple test script:

```csharp
using UnityEngine;
using P2C2R;
using System.Collections.Generic;

public class P2C2RTest : MonoBehaviour
{
    async void Start()
    {
        // Wait for connection
        await System.Threading.Tasks.Task.Delay(2000);

        // Submit AI task
        var input = new Dictionary<string, object>
        {
            { "player_input", "Hello, who are you?" },
            { "npc_name", "Guard" }
        };

        Debug.Log("Submitting AI task...");
        
        var result = await P2C2RClient.Instance.SubmitAITask(
            "npc_dialogue", 
            input
        );

        if (result.success)
        {
            Debug.Log($"✓ AI task completed in {result.latency:F2}s");
            Debug.Log($"Result: {result.data}");
        }
        else
        {
            Debug.LogError($"✗ Task failed: {result.error}");
        }
    }
}
```

**Steps:**
1. Create empty GameObject, add this script
2. Enter Play Mode
3. Check Console for results

**Expected Output:**
```
Submitting AI task...
[P2C2R] Task submitted: ai_inference (abc12345...)
[P2C2R] ✓ Task completed: abc12345... (0.15s)
✓ AI task completed in 0.15s
Result: { ... }
```

---

## Next Steps

### 🎮 Try the Examples

**AI NPC Example:**
```
Window > Package Manager > P2C2R Compute Assist > Samples > AI NPC Dialogue > Import
```

**Ray Tracing Example:**
```
Window > Package Manager > P2C2R Compute Assist > Samples > Ray Tracing Enhancement > Import
```

### 📚 Read the Docs

- [Full README](README.md) - Complete API reference
- [Architecture Guide](../docs/HYBRID_COMPUTE_ARCHITECTURE.md) - How it works
- [Network Layer](../network/README.md) - Protocol details

### 🔧 Build Something Cool

**Ideas:**
- AI-powered NPC conversations
- Ray-traced reflections in your scenes
- Procedural content generation
- Complex physics simulations

---

## Common Issues

### "WebSocket connection failed"

**Problem:** Can't connect to coordinator.

**Fix:**
1. Check P2C2R network is running: `ps aux | grep cloud_coordinator`
2. If not, restart: `./run_network.sh`
3. Verify URL in Inspector: `ws://localhost:8765`

### "Task never completes"

**Problem:** Task submitted but no response.

**Fix:**
1. Check peers are running: `ps aux | grep peer_node`
2. Check coordinator logs for errors
3. Restart network: `./run_network.sh`

### "Stats overlay not showing"

**Problem:** Can't see P2C2R stats in Game view.

**Fix:**
1. Select P2C2RClient in Hierarchy
2. Enable "Show Stats" in Inspector
3. Make sure you're in Play Mode

---

## 🚀 You're Ready!

P2C2R is now integrated in your Unity game. 

**What to try next:**
1. Add an AI NPC to your scene
2. Enable ray tracing on your camera
3. Offload heavy compute tasks
4. Build something amazing!

**Need help?**
- Open an issue on [GitHub](https://github.com/musk-hash-rats/p2c2r/issues)

Happy developing! 🎮✨
