using UnityEngine;

namespace P2C2R
{
    /// <summary>
    /// Component for offloading ray tracing to P2C2R
    /// Enhances scene with ray-traced reflections, shadows, and global illumination
    /// </summary>
    [RequireComponent(typeof(Camera))]
    public class P2C2RRayTracing : MonoBehaviour
    {
        [Header("Ray Tracing Settings")]
        [Tooltip("Enable ray tracing assist")]
        public bool enableRayTracing = true;

        [Tooltip("Scene complexity (affects compute time)")]
        [Range(10, 500)]
        public int sceneComplexity = 100;

        [Tooltip("Number of light sources")]
        [Range(1, 10)]
        public int numLights = 3;

        [Tooltip("Number of reflective objects")]
        [Range(0, 20)]
        public int numReflective = 2;

        [Header("Performance")]
        [Tooltip("Target framerate for ray tracing updates")]
        [Range(15, 60)]
        public int targetRayTracingFPS = 30;

        [Tooltip("Enable progressive rendering")]
        public bool progressiveRendering = true;

        [Header("Visual Settings")]
        [Tooltip("Blend factor for ray traced layer (0-1)")]
        [Range(0f, 1f)]
        public float blendFactor = 0.8f;

        [Tooltip("Fade in time for new ray traced frames")]
        public float fadeInTime = 0.2f;

        // Internal state
        private Camera _camera;
        private RenderTexture _rayTracedLayer;
        private Material _blendMaterial;
        private float _lastRayTraceTime = 0f;
        private float _rayTraceInterval = 0f;
        private bool _isRayTracing = false;
        private int _framesSinceLastUpdate = 0;

        private void Start()
        {
            _camera = GetComponent<Camera>();
            _rayTraceInterval = 1f / targetRayTracingFPS;

            // Create render texture for ray traced layer
            _rayTracedLayer = new RenderTexture(Screen.width, Screen.height, 0, RenderTextureFormat.ARGB32);
            _rayTracedLayer.Create();

            // Create blend material
            CreateBlendMaterial();

            Debug.Log($"[P2C2RRayTracing] Initialized. Target FPS: {targetRayTracingFPS}");
        }

        private void Update()
        {
            if (!enableRayTracing || !P2C2RClient.Instance.IsConnected)
                return;

            // Check if it's time to request new ray traced frame
            if (Time.time - _lastRayTraceTime >= _rayTraceInterval && !_isRayTracing)
            {
                RequestRayTracedFrame();
            }

            _framesSinceLastUpdate++;
        }

        private async void RequestRayTracedFrame()
        {
            _isRayTracing = true;
            _lastRayTraceTime = Time.time;

            Debug.Log($"[P2C2RRayTracing] Requesting ray traced frame...");

            // Submit ray tracing task
            var result = await P2C2RClient.Instance.SubmitRayTracingTask(
                sceneComplexity,
                numLights,
                numReflective,
                OnRayTracedFrameReceived
            );

            _isRayTracing = false;
        }

        private void OnRayTracedFrameReceived(TaskResult result)
        {
            if (result.success)
            {
                Debug.Log($"[P2C2RRayTracing] Ray traced frame received! Latency: {result.latency:F2}s");

                // In real implementation, decode the ray traced image data
                // and apply it to _rayTracedLayer
                
                // For now, we'll just log it
                _framesSinceLastUpdate = 0;
            }
            else
            {
                Debug.LogWarning($"[P2C2RRayTracing] Ray tracing failed: {result.error}");
            }
        }

        private void OnRenderImage(RenderTexture source, RenderTexture destination)
        {
            if (!enableRayTracing || _blendMaterial == null)
            {
                Graphics.Blit(source, destination);
                return;
            }

            // Blend ray traced layer with source
            _blendMaterial.SetTexture("_RayTracedTex", _rayTracedLayer);
            _blendMaterial.SetFloat("_BlendFactor", blendFactor);
            
            Graphics.Blit(source, destination, _blendMaterial);
        }

        private void CreateBlendMaterial()
        {
            // Simple blend shader
            Shader shader = Shader.Find("Hidden/P2C2R/RayTracingBlend");
            
            if (shader == null)
            {
                // Create a simple blend shader inline
                shader = CreateBlendShader();
            }

            _blendMaterial = new Material(shader);
        }

        private Shader CreateBlendShader()
        {
            // In real implementation, this would be a proper shader asset
            // For now, just use a simple blit
            return Shader.Find("Unlit/Texture");
        }

        private void OnDestroy()
        {
            if (_rayTracedLayer != null)
            {
                _rayTracedLayer.Release();
                Destroy(_rayTracedLayer);
            }

            if (_blendMaterial != null)
            {
                Destroy(_blendMaterial);
            }
        }

        private void OnGUI()
        {
            // Show ray tracing stats overlay
            if (enableRayTracing)
            {
                GUILayout.BeginArea(new Rect(10, 220, 300, 100));
                GUILayout.Box("Ray Tracing Stats");
                GUILayout.Label($"Enabled: {(P2C2RClient.Instance.IsConnected ? "✓" : "✗ (Disconnected)")}");
                GUILayout.Label($"Target FPS: {targetRayTracingFPS}");
                GUILayout.Label($"Frames since update: {_framesSinceLastUpdate}");
                GUILayout.Label($"Is ray tracing: {(_isRayTracing ? "Yes" : "No")}");
                GUILayout.EndArea();
            }
        }
    }
}
