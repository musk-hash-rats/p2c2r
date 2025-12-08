# P2C2R Unity Plugin

**Offload heavy compute tasks (AI, ray tracing, physics) to a distributed peer network.**

Get RTX 4090-level graphics and AI on any GPU for $5-10/month.

---

## 🚀 Quick Start

### Installation

1. **Add Package to Unity**
   - Open Unity Package Manager (Window > Package Manager)
   - Click "+" → "Add package from git URL"
   - Enter: `https://github.com/musk-hash-rats/p2c2r.git?path=/unity-plugin`

   OR manually:
   - Copy `unity-plugin` folder to your Unity project's `Packages` directory
   - Unity will auto-detect the package

2. **Add P2C2R Client to Scene**
   - Right-click in Hierarchy
   - Select `GameObject > P2C2R > Add P2C2R Client`
   - Configure coordinator URL in Inspector (default: `ws://localhost:8765`)

3. **Start Local Network** (for testing)
   ```bash
   cd /path/to/P2c2gPOC
   ./run_network.sh
   ```

4. **Enter Play Mode**
   - P2C2R will auto-connect
   - Check console for "✓ Connected to P2C2R coordinator"

---

## 📚 Features

### ✅ AI-Powered NPCs
Offload NPC dialogue generation, behavior trees, and decision-making to the cloud.

### ✅ Ray-Traced Graphics
Add ray tracing, reflections, and global illumination without requiring RTX hardware.

### ✅ Advanced Physics
Simulate complex physics (destruction, fluids, cloth) on powerful peer GPUs.

### ✅ Automatic Fallback
Gracefully degrades to local compute if P2C2R unavailable.

### ✅ Progressive Enhancement
Core game runs locally (60fps guaranteed), enhancements arrive asynchronously.

---

## 🎮 Usage Examples

### Example 1: AI NPC Dialogue

```csharp
using P2C2R;
using UnityEngine;

public class MyNPC : MonoBehaviour
{
    private P2C2RNPC p2c2rNPC;

    void Start()
    {
        p2c2rNPC = GetComponent<P2C2RNPC>();
        
        // Configure NPC
        p2c2rNPC.npcName = "Merchant";
        p2c2rNPC.personality = "A greedy but helpful merchant";
        
        // Listen for dialogue
        p2c2rNPC.onDialogueReceived.AddListener(OnDialogueReceived);
    }

    void OnPlayerTalk(string playerInput)
    {
        // Request AI-generated dialogue
        p2c2rNPC.GenerateDialogue(playerInput);
    }

    void OnDialogueReceived(string dialogue)
    {
        Debug.Log($"NPC says: {dialogue}");
        // Display in UI, trigger voice synthesis, etc.
    }
}
```

**OR use the quick setup:**
```
1. Right-click in Hierarchy
2. Select "GameObject > P2C2R > Create AI NPC"
3. Configure personality in Inspector
4. Call GenerateDialogue() when player interacts
```

---

### Example 2: Ray-Traced Reflections

```csharp
using P2C2R;
using UnityEngine;

public class EnableRayTracing : MonoBehaviour
{
    void Start()
    {
        // Add ray tracing to main camera
        Camera.main.gameObject.AddComponent<P2C2RRayTracing>();
    }
}
```

**OR use the quick setup:**
```
1. Select your Main Camera
2. Menu: "GameObject > P2C2R > Add Ray Tracing to Camera"
3. Configure settings in Inspector
4. Ray tracing automatically enabled when P2C2R connects
```

---

### Example 3: Manual Task Submission

```csharp
using P2C2R;
using System.Collections.Generic;
using UnityEngine;

public class ManualTaskExample : MonoBehaviour
{
    async void SubmitCustomTask()
    {
        // Create task data
        var taskData = new Dictionary<string, object>
        {
            { "type", "ai_inference" },
            { "model", "pathfinding" },
            { "input", new Dictionary<string, object>
                {
                    { "start", new int[] {0, 0} },
                    { "goal", new int[] {100, 100} }
                }
            }
        };

        // Submit to P2C2R
        var result = await P2C2RClient.Instance.SubmitTask(taskData);

        if (result.success)
        {
            Debug.Log($"Task completed in {result.latency}s");
            Debug.Log($"Result: {result.data}");
        }
        else
        {
            Debug.LogError($"Task failed: {result.error}");
        }
    }
}
```

---

### Example 4: Physics Simulation

```csharp
using P2C2R;
using UnityEngine;

public class ComplexPhysics : MonoBehaviour
{
    async void SimulateDestruction()
    {
        // Offload heavy physics to P2C2R
        var result = await P2C2RClient.Instance.SubmitPhysicsTask(
            numObjects: 500,     // 500 debris pieces
            timestep: 0.016f     // 60 FPS
        );

        if (result.success)
        {
            // Apply physics result to local objects
            ApplyPhysicsState(result.data);
        }
    }

    void ApplyPhysicsState(string data)
    {
        // Parse and apply physics state to GameObjects
        // This would interpolate between keyframes
    }
}
```

---

## ⚙️ Configuration

### P2C2RClient Settings

| Property | Description | Default |
|----------|-------------|---------|
| `coordinatorUrl` | P2C2R coordinator WebSocket URL | `ws://localhost:8765` |
| `autoConnect` | Connect automatically on Start | `true` |
| `autoReconnect` | Reconnect on disconnect | `true` |
| `enableDebugLogs` | Show debug messages in console | `true` |
| `showStats` | Show stats overlay in game view | `true` |

### P2C2RNPC Settings

| Property | Description | Default |
|----------|-------------|---------|
| `npcName` | NPC name for context | `"Guard"` |
| `personality` | NPC personality/role description | `"A friendly guard..."` |
| `aiModel` | AI model to use | `"npc_dialogue"` |
| `enableFallback` | Use local fallback if offline | `true` |
| `cacheResponses` | Cache dialogue responses | `true` |

### P2C2RRayTracing Settings

| Property | Description | Default |
|----------|-------------|---------|
| `enableRayTracing` | Enable ray tracing assist | `true` |
| `sceneComplexity` | Scene complexity (10-500) | `100` |
| `numLights` | Number of lights (1-10) | `3` |
| `numReflective` | Reflective objects (0-20) | `2` |
| `targetRayTracingFPS` | Target update rate (15-60) | `30` |
| `blendFactor` | Blend amount (0-1) | `0.8` |

---

## 🔧 API Reference

### P2C2RClient

**Main client for P2C2R network.**

#### Properties
- `bool IsConnected` - Connection status
- `int PendingTaskCount` - Number of pending tasks
- `int TasksSent` - Total tasks sent
- `int TasksCompleted` - Total tasks completed
- `int TasksFailed` - Total tasks failed
- `float AverageLatency` - Average task latency

#### Methods

**Connect()**
```csharp
void Connect()
```
Connect to P2C2R coordinator.

**Disconnect()**
```csharp
void Disconnect()
```
Disconnect from P2C2R coordinator.

**SubmitAITask()**
```csharp
async Task<TaskResult> SubmitAITask(
    string model, 
    Dictionary<string, object> input, 
    Action<TaskResult> callback = null
)
```
Submit an AI inference task.

**SubmitRayTracingTask()**
```csharp
async Task<TaskResult> SubmitRayTracingTask(
    int complexity, 
    int numLights, 
    int numReflective,
    Action<TaskResult> callback = null
)
```
Submit a ray tracing task.

**SubmitPhysicsTask()**
```csharp
async Task<TaskResult> SubmitPhysicsTask(
    int numObjects, 
    float timestep,
    Action<TaskResult> callback = null
)
```
Submit a physics simulation task.

**SubmitTask()**
```csharp
async Task<TaskResult> SubmitTask(
    Dictionary<string, object> taskData,
    Action<TaskResult> callback = null
)
```
Submit a generic task.

---

### TaskResult

**Result of a P2C2R task.**

#### Properties
- `bool success` - Whether task succeeded
- `string taskId` - Unique task identifier
- `string data` - Result data (JSON)
- `string error` - Error message (if failed)
- `float latency` - Task latency in seconds

---

## 🎯 Best Practices

### 1. **Graceful Degradation**
Always provide local fallback for critical features:

```csharp
if (P2C2RClient.Instance.IsConnected)
{
    // Use P2C2R for enhanced features
    await SubmitAITask(...);
}
else
{
    // Use local simple implementation
    UseSimpleLocalAI();
}
```

### 2. **Latency Tolerance**
Only offload tasks that can tolerate 50-300ms latency:

✅ **Good for P2C2R:**
- NPC dialogue (100-300ms OK)
- Ray tracing / reflections (50-100ms OK)
- Procedural generation (300-1000ms OK)
- Future frame prediction (1-5s OK)

❌ **Keep Local:**
- Player input (< 16ms required)
- Camera movement (< 16ms required)
- Core game logic (< 16ms required)
- Audio playback (< 10ms required)

### 3. **Progressive Enhancement**
Layer enhancements over time:

```csharp
// Frame 0: Show basic version immediately
RenderBasicVersion();

// Frame 0: Request enhancement
var task = SubmitRayTracingTask(...);

// Frame 3-6: Enhancement arrives, blend it in
await task;
BlendEnhancement();
```

### 4. **Caching**
Cache results for repeated queries:

```csharp
Dictionary<string, string> dialogueCache = new Dictionary<string, string>();

string GetDialogue(string input)
{
    if (dialogueCache.ContainsKey(input))
        return dialogueCache[input];
    
    var result = await SubmitAITask(...);
    dialogueCache[input] = result.data;
    return result.data;
}
```

---

## 🐛 Troubleshooting

### "Not connected to P2C2R"

**Problem:** Client can't connect to coordinator.

**Solutions:**
1. Ensure P2C2R network is running: `./run_network.sh`
2. Check coordinator URL in Inspector
3. Verify firewall allows WebSocket connections
4. Check console for connection errors

### "Tasks timing out"

**Problem:** Tasks never complete.

**Solutions:**
1. Check if peers are connected (see coordinator logs)
2. Verify peers are running and healthy
3. Reduce task complexity
4. Check network latency

### "Poor performance"

**Problem:** Game runs slowly with P2C2R.

**Solutions:**
1. Reduce `targetRayTracingFPS` (try 15-20)
2. Lower `sceneComplexity`
3. Disable `showStats` overlay
4. Only offload truly heavy tasks

---

## 📦 Package Contents

```
unity-plugin/
├── package.json              # Package manifest
├── Runtime/
│   ├── P2C2RClient.cs       # Main client (singleton)
│   ├── P2C2RNPC.cs          # AI NPC helper
│   └── P2C2RRayTracing.cs   # Ray tracing helper
├── Editor/
│   └── P2C2REditor.cs       # Editor tools & inspectors
├── Samples~/
│   ├── AINPCDialogue/       # AI NPC example scene
│   └── RayTracingEnhancement/ # Ray tracing example scene
└── README.md                # This file
```

---

## 🔗 Links

- **Main Repository:** https://github.com/musk-hash-rats/p2c2r
- **GitHub Issues:** [Report bugs/request features](https://github.com/musk-hash-rats/p2c2r/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/musk-hash-rats/p2c2r/discussions)
- **Network Documentation:** [../network/README.md](../network/README.md)
- **Architecture Guide:** [../docs/HYBRID_COMPUTE_ARCHITECTURE.md](../docs/HYBRID_COMPUTE_ARCHITECTURE.md)

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🙏 Credits

Built with ❤️ by the P2C2R team.

**Special thanks to:**
- Game Engine Companies for the game engine
- WebSocket contributors for networking
- The open-source community

---

**Questions? Issues? Feature requests?**

Open an issue on [GitHub](https://github.com/musk-hash-rats/p2c2r/issues)!
