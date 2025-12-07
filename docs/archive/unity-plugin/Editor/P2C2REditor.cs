using UnityEngine;
using UnityEditor;

namespace P2C2R.Editor
{
    /// <summary>
    /// Quick setup menu items for P2C2R
    /// </summary>
    public static class P2C2RMenu
    {
        [MenuItem("GameObject/P2C2R/Add P2C2R Client", false, 10)]
        public static void AddP2C2RClient()
        {
            GameObject go = new GameObject("P2C2RClient");
            go.AddComponent<P2C2RClient>();
            Selection.activeGameObject = go;
            
            Debug.Log("✓ P2C2R Client added to scene. Configure the coordinator URL in the Inspector.");
        }

        [MenuItem("GameObject/P2C2R/Add Ray Tracing to Camera", false, 11)]
        public static void AddRayTracingToCamera()
        {
            Camera camera = Camera.main;
            
            if (camera == null)
            {
                Debug.LogError("No main camera found in scene!");
                return;
            }

            if (camera.GetComponent<P2C2RRayTracing>() != null)
            {
                Debug.LogWarning("Camera already has P2C2RRayTracing component!");
                return;
            }

            camera.gameObject.AddComponent<P2C2RRayTracing>();
            Selection.activeGameObject = camera.gameObject;
            
            Debug.Log("✓ Ray Tracing component added to Main Camera.");
        }

        [MenuItem("GameObject/P2C2R/Create AI NPC", false, 12)]
        public static void CreateAINPC()
        {
            GameObject npc = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            npc.name = "AI_NPC";
            npc.AddComponent<P2C2RNPC>();
            Selection.activeGameObject = npc;
            
            Debug.Log("✓ AI NPC created. Configure personality and dialogue settings in the Inspector.");
        }

        [MenuItem("Window/P2C2R/Settings", false, 100)]
        public static void OpenSettings()
        {
            P2C2RSettingsWindow.ShowWindow();
        }

        [MenuItem("Window/P2C2R/Documentation", false, 101)]
        public static void OpenDocumentation()
        {
            Application.OpenURL("https://github.com/musk-hash-rats/p2c2r");
        }
    }

    /// <summary>
    /// Settings window for P2C2R configuration
    /// </summary>
    public class P2C2RSettingsWindow : EditorWindow
    {
        private string coordinatorUrl = "ws://localhost:8765";
        private bool autoConnect = true;
        private bool enableDebugLogs = true;
        private bool showStats = true;

        public static void ShowWindow()
        {
            var window = GetWindow<P2C2RSettingsWindow>("P2C2R Settings");
            window.Show();
        }

        private void OnGUI()
        {
            GUILayout.Label("P2C2R Configuration", EditorStyles.boldLabel);
            GUILayout.Space(10);

            coordinatorUrl = EditorGUILayout.TextField("Coordinator URL", coordinatorUrl);
            autoConnect = EditorGUILayout.Toggle("Auto-Connect", autoConnect);
            enableDebugLogs = EditorGUILayout.Toggle("Enable Debug Logs", enableDebugLogs);
            showStats = EditorGUILayout.Toggle("Show Stats Overlay", showStats);

            GUILayout.Space(20);

            if (GUILayout.Button("Apply Settings"))
            {
                ApplySettings();
            }

            GUILayout.Space(20);
            GUILayout.Label("Quick Actions", EditorStyles.boldLabel);

            if (GUILayout.Button("Add P2C2R Client to Scene"))
            {
                P2C2RMenu.AddP2C2RClient();
            }

            if (GUILayout.Button("Test Connection"))
            {
                TestConnection();
            }

            GUILayout.Space(20);
            GUILayout.Label("Documentation", EditorStyles.boldLabel);
            
            if (GUILayout.Button("Open Documentation"))
            {
                Application.OpenURL("https://github.com/musk-hash-rats/p2c2r/blob/main/network/README.md");
            }

            if (GUILayout.Button("View Examples"))
            {
                Application.OpenURL("https://github.com/musk-hash-rats/p2c2r/tree/main/examples");
            }
        }

        private void ApplySettings()
        {
            var client = FindObjectOfType<P2C2RClient>();
            
            if (client == null)
            {
                EditorUtility.DisplayDialog("P2C2R", 
                    "No P2C2RClient found in scene. Add one first!", 
                    "OK");
                return;
            }

            client.coordinatorUrl = coordinatorUrl;
            client.autoConnect = autoConnect;
            client.enableDebugLogs = enableDebugLogs;
            client.showStats = showStats;

            EditorUtility.SetDirty(client);
            
            Debug.Log("✓ P2C2R settings applied");
        }

        private void TestConnection()
        {
            var client = FindObjectOfType<P2C2RClient>();
            
            if (client == null)
            {
                EditorUtility.DisplayDialog("P2C2R", 
                    "No P2C2RClient found in scene. Add one first!", 
                    "OK");
                return;
            }

            if (Application.isPlaying)
            {
                client.Connect();
                Debug.Log("Testing connection to P2C2R coordinator...");
            }
            else
            {
                EditorUtility.DisplayDialog("P2C2R", 
                    "Enter Play Mode to test the connection.", 
                    "OK");
            }
        }
    }

    /// <summary>
    /// Custom inspector for P2C2RClient
    /// </summary>
    [CustomEditor(typeof(P2C2RClient))]
    public class P2C2RClientEditor : UnityEditor.Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();

            GUILayout.Space(10);
            GUILayout.Label("Runtime Controls", EditorStyles.boldLabel);

            var client = (P2C2RClient)target;

            if (Application.isPlaying)
            {
                EditorGUILayout.HelpBox(
                    client.IsConnected ? "✓ Connected to P2C2R" : "✗ Not connected", 
                    client.IsConnected ? MessageType.Info : MessageType.Warning
                );

                if (client.IsConnected)
                {
                    EditorGUILayout.LabelField("Tasks Sent", client.TasksSent.ToString());
                    EditorGUILayout.LabelField("Tasks Completed", client.TasksCompleted.ToString());
                    EditorGUILayout.LabelField("Tasks Failed", client.TasksFailed.ToString());
                    EditorGUILayout.LabelField("Pending", client.PendingTaskCount.ToString());
                    EditorGUILayout.LabelField("Avg Latency", $"{client.AverageLatency:F2}s");

                    if (GUILayout.Button("Disconnect"))
                    {
                        client.Disconnect();
                    }
                }
                else
                {
                    if (GUILayout.Button("Connect"))
                    {
                        client.Connect();
                    }
                }

                GUILayout.Space(10);

                if (GUILayout.Button("Test AI Task"))
                {
                    TestAITask(client);
                }

                if (GUILayout.Button("Test Ray Tracing Task"))
                {
                    TestRayTracingTask(client);
                }
            }
            else
            {
                EditorGUILayout.HelpBox("Enter Play Mode to connect and test P2C2R", MessageType.Info);
            }
        }

        private async void TestAITask(P2C2RClient client)
        {
            var input = new System.Collections.Generic.Dictionary<string, object>
            {
                { "test", "dialogue" },
                { "player_input", "Hello!" }
            };

            Debug.Log("Submitting test AI task...");
            var result = await client.SubmitAITask("npc_dialogue", input);
            
            if (result.success)
            {
                Debug.Log($"✓ Test AI task completed in {result.latency:F2}s");
            }
            else
            {
                Debug.LogError($"✗ Test AI task failed: {result.error}");
            }
        }

        private async void TestRayTracingTask(P2C2RClient client)
        {
            Debug.Log("Submitting test ray tracing task...");
            var result = await client.SubmitRayTracingTask(100, 3, 2);
            
            if (result.success)
            {
                Debug.Log($"✓ Test ray tracing task completed in {result.latency:F2}s");
            }
            else
            {
                Debug.LogError($"✗ Test ray tracing task failed: {result.error}");
            }
        }
    }
}
