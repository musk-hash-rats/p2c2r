using System;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;

namespace P2C2R
{
    /// <summary>
    /// Main client for connecting to P2C2R network and offloading compute tasks.
    /// This is the primary API developers interact with.
    /// </summary>
    public class P2C2RClient : MonoBehaviour
    {
        #region Singleton
        private static P2C2RClient _instance;
        public static P2C2RClient Instance
        {
            get
            {
                if (_instance == null)
                {
                    GameObject go = new GameObject("P2C2RClient");
                    _instance = go.AddComponent<P2C2RClient>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
        #endregion

        #region Configuration
        [Header("Connection Settings")]
        [Tooltip("P2C2R coordinator URL (default: ws://localhost:8765)")]
        public string coordinatorUrl = "ws://localhost:8765";

        [Tooltip("Auto-connect on start")]
        public bool autoConnect = true;

        [Tooltip("Auto-reconnect on disconnect")]
        public bool autoReconnect = true;

        [Header("Debug")]
        [Tooltip("Enable debug logging")]
        public bool enableDebugLogs = true;

        [Tooltip("Show performance stats")]
        public bool showStats = true;
        #endregion

        #region State
        private ClientWebSocket _webSocket;
        private CancellationTokenSource _cancellationTokenSource;
        private bool _isConnected = false;
        private string _userId;
        private Queue<Action> _mainThreadActions = new Queue<Action>();

        // Pending tasks
        private Dictionary<string, TaskRequest> _pendingTasks = new Dictionary<string, TaskRequest>();

        // Stats
        private int _tasksSent = 0;
        private int _tasksCompleted = 0;
        private int _tasksFailed = 0;
        private float _averageLatency = 0f;
        #endregion

        #region Properties
        public bool IsConnected => _isConnected;
        public int PendingTaskCount => _pendingTasks.Count;
        public int TasksSent => _tasksSent;
        public int TasksCompleted => _tasksCompleted;
        public int TasksFailed => _tasksFailed;
        public float AverageLatency => _averageLatency;
        #endregion

        #region Unity Lifecycle
        private void Awake()
        {
            if (_instance != null && _instance != this)
            {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);

            _userId = $"unity_user_{Guid.NewGuid().ToString().Substring(0, 8)}";
        }

        private void Start()
        {
            if (autoConnect)
            {
                Connect();
            }
        }

        private void Update()
        {
            // Execute queued main thread actions
            lock (_mainThreadActions)
            {
                while (_mainThreadActions.Count > 0)
                {
                    _mainThreadActions.Dequeue()?.Invoke();
                }
            }
        }

        private void OnDestroy()
        {
            Disconnect();
        }

        private void OnApplicationQuit()
        {
            Disconnect();
        }
        #endregion

        #region Connection Management
        /// <summary>
        /// Connect to P2C2R coordinator
        /// </summary>
        public async void Connect()
        {
            if (_isConnected)
            {
                LogWarning("Already connected to P2C2R");
                return;
            }

            try
            {
                Log($"Connecting to P2C2R coordinator: {coordinatorUrl}");

                _webSocket = new ClientWebSocket();
                _cancellationTokenSource = new CancellationTokenSource();

                await _webSocket.ConnectAsync(new Uri(coordinatorUrl), _cancellationTokenSource.Token);

                _isConnected = true;
                Log("✓ Connected to P2C2R coordinator");

                // Send registration
                await RegisterUser();

                // Start listening for messages
                _ = ListenForMessages();
            }
            catch (Exception e)
            {
                LogError($"Failed to connect: {e.Message}");
                _isConnected = false;

                if (autoReconnect)
                {
                    Log("Will retry connection in 5 seconds...");
                    await Task.Delay(5000);
                    Connect();
                }
            }
        }

        /// <summary>
        /// Disconnect from P2C2R coordinator
        /// </summary>
        public async void Disconnect()
        {
            if (!_isConnected) return;

            try
            {
                Log("Disconnecting from P2C2R...");

                _cancellationTokenSource?.Cancel();

                if (_webSocket?.State == WebSocketState.Open)
                {
                    await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Client disconnect", CancellationToken.None);
                }

                _webSocket?.Dispose();
                _isConnected = false;

                Log("✓ Disconnected from P2C2R");
            }
            catch (Exception e)
            {
                LogError($"Error during disconnect: {e.Message}");
            }
        }

        private async Task RegisterUser()
        {
            var msg = new
            {
                msg_type = "register_user",
                msg_id = Guid.NewGuid().ToString(),
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
                data = new
                {
                    user_id = _userId,
                    client_info = new
                    {
                        platform = "Unity",
                        version = Application.unityVersion,
                        device = SystemInfo.deviceModel
                    }
                }
            };

            await SendMessage(msg);
        }
        #endregion

        #region Task Submission
        /// <summary>
        /// Submit an AI inference task
        /// </summary>
        public async Task<TaskResult> SubmitAITask(string model, Dictionary<string, object> input, Action<TaskResult> callback = null)
        {
            var taskData = new Dictionary<string, object>
            {
                { "type", "ai_inference" },
                { "model", model },
                { "input", input }
            };

            return await SubmitTask(taskData, callback);
        }

        /// <summary>
        /// Submit a ray tracing task
        /// </summary>
        public async Task<TaskResult> SubmitRayTracingTask(int complexity, int numLights, int numReflective, Action<TaskResult> callback = null)
        {
            var taskData = new Dictionary<string, object>
            {
                { "type", "ray_tracing" },
                { "complexity", complexity },
                { "num_lights", numLights },
                { "num_reflective", numReflective },
                { "resolution", new int[] { Screen.width, Screen.height } }
            };

            return await SubmitTask(taskData, callback);
        }

        /// <summary>
        /// Submit a physics simulation task
        /// </summary>
        public async Task<TaskResult> SubmitPhysicsTask(int numObjects, float timestep, Action<TaskResult> callback = null)
        {
            var taskData = new Dictionary<string, object>
            {
                { "type", "physics" },
                { "num_objects", numObjects },
                { "timestep", timestep }
            };

            return await SubmitTask(taskData, callback);
        }

        /// <summary>
        /// Submit a generic task
        /// </summary>
        public async Task<TaskResult> SubmitTask(Dictionary<string, object> taskData, Action<TaskResult> callback = null)
        {
            if (!_isConnected)
            {
                LogError("Not connected to P2C2R. Call Connect() first.");
                return new TaskResult { success = false, error = "Not connected" };
            }

            string taskId = Guid.NewGuid().ToString();

            var msg = new
            {
                msg_type = "task_request",
                msg_id = Guid.NewGuid().ToString(),
                timestamp = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
                data = new
                {
                    task_id = taskId,
                    user_id = _userId,
                    task_data = taskData
                }
            };

            var taskRequest = new TaskRequest
            {
                taskId = taskId,
                taskData = taskData,
                callback = callback,
                submittedAt = Time.realtimeSinceStartup,
                taskCompletionSource = new TaskCompletionSource<TaskResult>()
            };

            _pendingTasks[taskId] = taskRequest;
            _tasksSent++;

            await SendMessage(msg);

            Log($"Task submitted: {taskData["type"]} ({taskId.Substring(0, 8)}...)");

            return await taskRequest.taskCompletionSource.Task;
        }
        #endregion

        #region Message Handling
        private async Task SendMessage(object msg)
        {
            if (_webSocket?.State != WebSocketState.Open) return;

            string json = JsonUtility.ToJson(msg);
            byte[] bytes = Encoding.UTF8.GetBytes(json);
            var segment = new ArraySegment<byte>(bytes);

            await _webSocket.SendAsync(segment, WebSocketMessageType.Text, true, _cancellationTokenSource.Token);
        }

        private async Task ListenForMessages()
        {
            var buffer = new byte[8192];

            try
            {
                while (_webSocket.State == WebSocketState.Open && !_cancellationTokenSource.Token.IsCancellationRequested)
                {
                    var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cancellationTokenSource.Token);

                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        Log("Server closed connection");
                        _isConnected = false;

                        if (autoReconnect)
                        {
                            await Task.Delay(3000);
                            Connect();
                        }
                        break;
                    }

                    string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    HandleMessage(message);
                }
            }
            catch (Exception e)
            {
                LogError($"Error receiving messages: {e.Message}");
                _isConnected = false;

                if (autoReconnect)
                {
                    await Task.Delay(3000);
                    Connect();
                }
            }
        }

        private void HandleMessage(string json)
        {
            try
            {
                var msg = JsonUtility.FromJson<NetworkMessage>(json);

                switch (msg.msg_type)
                {
                    case "registration_ack":
                        Log("✓ Registration confirmed by coordinator");
                        break;

                    case "task_result":
                        HandleTaskResult(msg);
                        break;

                    case "task_failure":
                        HandleTaskFailure(msg);
                        break;

                    case "peer_count_update":
                        // Could show this in UI
                        break;

                    case "error":
                        LogError($"Error from coordinator: {msg.data}");
                        break;
                }
            }
            catch (Exception e)
            {
                LogError($"Error parsing message: {e.Message}");
            }
        }

        private void HandleTaskResult(NetworkMessage msg)
        {
            // Parse task result (Unity's JsonUtility is limited, this is simplified)
            string taskId = GetTaskIdFromMessage(msg.data);

            if (_pendingTasks.TryGetValue(taskId, out var taskRequest))
            {
                float latency = Time.realtimeSinceStartup - taskRequest.submittedAt;

                // Update stats
                _tasksCompleted++;
                _averageLatency = (_averageLatency * (_tasksCompleted - 1) + latency) / _tasksCompleted;

                var result = new TaskResult
                {
                    success = true,
                    taskId = taskId,
                    data = msg.data,
                    latency = latency
                };

                // Complete the task
                taskRequest.taskCompletionSource?.SetResult(result);

                // Call callback on main thread
                if (taskRequest.callback != null)
                {
                    lock (_mainThreadActions)
                    {
                        _mainThreadActions.Enqueue(() => taskRequest.callback(result));
                    }
                }

                _pendingTasks.Remove(taskId);

                Log($"✓ Task completed: {taskId.Substring(0, 8)}... ({latency:F2}s)");
            }
        }

        private void HandleTaskFailure(NetworkMessage msg)
        {
            string taskId = GetTaskIdFromMessage(msg.data);

            if (_pendingTasks.TryGetValue(taskId, out var taskRequest))
            {
                _tasksFailed++;

                var result = new TaskResult
                {
                    success = false,
                    taskId = taskId,
                    error = "Task failed on peer"
                };

                taskRequest.taskCompletionSource?.SetResult(result);

                if (taskRequest.callback != null)
                {
                    lock (_mainThreadActions)
                    {
                        _mainThreadActions.Enqueue(() => taskRequest.callback(result));
                    }
                }

                _pendingTasks.Remove(taskId);

                LogError($"✗ Task failed: {taskId.Substring(0, 8)}...");
            }
        }

        private string GetTaskIdFromMessage(string data)
        {
            // Simple parsing (in real implementation, use proper JSON parser)
            int start = data.IndexOf("\"task_id\":\"") + 11;
            int end = data.IndexOf("\"", start);
            return data.Substring(start, end - start);
        }
        #endregion

        #region Logging
        private void Log(string message)
        {
            if (enableDebugLogs)
            {
                Debug.Log($"[P2C2R] {message}");
            }
        }

        private void LogWarning(string message)
        {
            if (enableDebugLogs)
            {
                Debug.LogWarning($"[P2C2R] {message}");
            }
        }

        private void LogError(string message)
        {
            Debug.LogError($"[P2C2R] {message}");
        }
        #endregion

        #region GUI Debug
        private void OnGUI()
        {
            if (!showStats) return;

            GUILayout.BeginArea(new Rect(10, 10, 300, 200));
            GUILayout.Box("P2C2R Stats");
            GUILayout.Label($"Connected: {(_isConnected ? "✓" : "✗")}");
            GUILayout.Label($"Tasks Sent: {_tasksSent}");
            GUILayout.Label($"Tasks Completed: {_tasksCompleted}");
            GUILayout.Label($"Tasks Failed: {_tasksFailed}");
            GUILayout.Label($"Pending: {_pendingTasks.Count}");
            GUILayout.Label($"Avg Latency: {_averageLatency:F2}s");

            if (!_isConnected && GUILayout.Button("Connect"))
            {
                Connect();
            }

            GUILayout.EndArea();
        }
        #endregion
    }

    #region Data Classes
    [Serializable]
    public class NetworkMessage
    {
        public string msg_type;
        public string msg_id;
        public long timestamp;
        public string data;
    }

    public class TaskRequest
    {
        public string taskId;
        public Dictionary<string, object> taskData;
        public Action<TaskResult> callback;
        public float submittedAt;
        public TaskCompletionSource<TaskResult> taskCompletionSource;
    }

    public class TaskResult
    {
        public bool success;
        public string taskId;
        public string data;
        public string error;
        public float latency;
    }
    #endregion
}
