using UnityEngine;
using P2C2R;

/// <summary>
/// Simple demo showing P2C2R connectivity and stats
/// </summary>
public class P2C2RDemo : MonoBehaviour
{
    [Header("P2C2R Connection")]
    public string coordinatorUrl = "ws://localhost:8765";
    public bool autoConnect = true;
    
    [Header("Display")]
    public bool showStats = true;
    public bool showPerformanceComparison = true;
    
    private float localAiTime = 0.02f; // Simulated local AI time
    private float costSavings = 0f;
    
    void Start()
    {
        // P2C2RClient will auto-connect if configured
        Debug.Log("[P2C2RDemo] Starting P2C2R demo...");
        Debug.Log($"[P2C2RDemo] Coordinator: {coordinatorUrl}");
    }
    
    void Update()
    {
        // Calculate cost savings
        if (P2C2RClient.Instance != null && P2C2RClient.Instance.IsConnected)
        {
            CalculateSavings();
        }
    }
    
    void CalculateSavings()
    {
        // Simulated cost calculation
        // Local GPU: $1200 upfront + $50/month electricity
        // P2C2R: $7.50/month subscription
        
        float monthsRunning = Time.time / (60f * 60f * 24f * 30f); // Simplified
        float localCost = 1200f + (50f * monthsRunning);
        float p2c2rCost = 7.50f * monthsRunning;
        costSavings = localCost - p2c2rCost;
    }
    
    void OnGUI()
    {
        if (!showStats) return;
        
        // P2C2R Status Box
        GUI.Box(new Rect(10, 120, 300, 150), "P2C2R Status");
        
        if (P2C2RClient.Instance != null)
        {
            bool connected = P2C2RClient.Instance.IsConnected;
            GUI.Label(new Rect(20, 145, 280, 20), 
                $"Status: {(connected ? "✓ Connected" : "✗ Disconnected")}");
            
            GUI.Label(new Rect(20, 165, 280, 20), 
                $"Tasks Sent: {P2C2RClient.Instance.TasksSent}");
            
            GUI.Label(new Rect(20, 185, 280, 20), 
                $"Tasks Completed: {P2C2RClient.Instance.TasksCompleted}");
            
            GUI.Label(new Rect(20, 205, 280, 20), 
                $"Avg Latency: {P2C2RClient.Instance.AverageLatency:F3}s");
            
            GUI.Label(new Rect(20, 225, 280, 20), 
                $"Pending: {P2C2RClient.Instance.PendingTaskCount}");
        }
        else
        {
            GUI.Label(new Rect(20, 145, 280, 20), "P2C2RClient not initialized");
        }
        
        // Performance Comparison
        if (showPerformanceComparison)
        {
            GUI.Box(new Rect(10, 280, 300, 120), "The \"Uber\" Advantage");
            
            GUI.Label(new Rect(20, 305, 280, 20), "Local GPU: $1200 + $50/mo");
            GUI.Label(new Rect(20, 325, 280, 20), "P2C2R Network: $7.50/mo");
            GUI.Label(new Rect(20, 345, 280, 20), "━━━━━━━━━━━━━━━━");
            GUI.Label(new Rect(20, 365, 280, 20), $"Savings: ${costSavings:F0} (94% cheaper!)");
        }
    }
}
