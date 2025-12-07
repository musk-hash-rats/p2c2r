using UnityEngine;
using P2C2R;
using System.Collections.Generic;

/// <summary>
/// Simple space shooter that uses P2C2R for AI enemy behavior
/// Demonstrates "Uber for Compute" - offloads AI to peer network
/// </summary>
public class SpaceShooter : MonoBehaviour
{
    [Header("Player")]
    public float playerSpeed = 10f;
    public GameObject bulletPrefab;
    public float fireRate = 0.25f;
    private float nextFireTime = 0f;
    
    [Header("Enemies")]
    public GameObject enemyPrefab;
    public int maxEnemies = 10;
    public float spawnRate = 2f;
    private float nextSpawnTime = 0f;
    private List<GameObject> enemies = new List<GameObject>();
    
    [Header("P2C2R AI")]
    public bool useP2C2R = true;
    public float aiUpdateRate = 0.5f; // Update enemy AI every 0.5s
    private float nextAiUpdate = 0f;
    
    [Header("Stats")]
    public int score = 0;
    public int enemiesKilled = 0;
    public float p2c2rLatency = 0f;
    
    void Start()
    {
        // Check if P2C2R is available
        if (useP2C2R && P2C2RClient.Instance != null)
        {
            Debug.Log("[SpaceShooter] P2C2R enabled - AI will use peer network");
        }
        else
        {
            Debug.Log("[SpaceShooter] P2C2R disabled - using local AI");
        }
    }
    
    void Update()
    {
        HandlePlayerInput();
        SpawnEnemies();
        
        if (useP2C2R && Time.time >= nextAiUpdate)
        {
            UpdateEnemyAI_P2C2R();
            nextAiUpdate = Time.time + aiUpdateRate;
        }
        else if (!useP2C2R)
        {
            UpdateEnemyAI_Local();
        }
    }
    
    void HandlePlayerInput()
    {
        // Movement (WASD or Arrow keys)
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");
        
        Vector3 movement = new Vector3(horizontal, vertical, 0f);
        transform.position += movement * playerSpeed * Time.deltaTime;
        
        // Keep player on screen
        Vector3 pos = transform.position;
        pos.x = Mathf.Clamp(pos.x, -8f, 8f);
        pos.y = Mathf.Clamp(pos.y, -4f, 4f);
        transform.position = pos;
        
        // Fire (Spacebar)
        if (Input.GetKey(KeyCode.Space) && Time.time >= nextFireTime)
        {
            FireBullet();
            nextFireTime = Time.time + fireRate;
        }
    }
    
    void FireBullet()
    {
        // Create bullet (or just raycast in simple version)
        Debug.Log($"[SpaceShooter] Fire! Score: {score}");
    }
    
    void SpawnEnemies()
    {
        if (enemies.Count < maxEnemies && Time.time >= nextSpawnTime)
        {
            // Spawn enemy at top of screen
            Vector3 spawnPos = new Vector3(
                Random.Range(-8f, 8f),
                5f,
                0f
            );
            
            // In real Unity, you'd instantiate a prefab
            // For now, just track positions
            GameObject enemy = new GameObject($"Enemy_{enemies.Count}");
            enemy.transform.position = spawnPos;
            enemies.Add(enemy);
            
            nextSpawnTime = Time.time + spawnRate;
            Debug.Log($"[SpaceShooter] Spawned enemy at {spawnPos}");
        }
    }
    
    /// <summary>
    /// Use P2C2R peer network to calculate enemy AI
    /// This offloads compute to the "Uber" network
    /// </summary>
    async void UpdateEnemyAI_P2C2R()
    {
        if (enemies.Count == 0) return;
        
        // Prepare game state for AI computation
        var gameState = new Dictionary<string, object>
        {
            { "player_position", new float[] { 
                transform.position.x, 
                transform.position.y 
            }},
            { "enemy_count", enemies.Count },
            { "enemies", GetEnemyPositions() },
            { "difficulty", Mathf.FloorToInt(score / 100f) }
        };
        
        Debug.Log($"[SpaceShooter] Requesting AI from P2C2R network...");
        
        try
        {
            // Submit AI task to P2C2R network (the "Uber" request)
            var result = await P2C2RClient.Instance.SubmitAITask(
                "enemy_behavior",
                gameState
            );
            
            if (result.success)
            {
                p2c2rLatency = result.latency;
                Debug.Log($"[SpaceShooter] ✓ AI received from peer network ({result.latency:F3}s)");
                
                // Apply AI decisions from peer network
                ApplyAIDecisions(result.data);
            }
            else
            {
                Debug.LogWarning($"[SpaceShooter] P2C2R failed, using local AI: {result.error}");
                UpdateEnemyAI_Local();
            }
        }
        catch (System.Exception e)
        {
            Debug.LogWarning($"[SpaceShooter] P2C2R error, using local AI: {e.Message}");
            UpdateEnemyAI_Local();
        }
    }
    
    /// <summary>
    /// Fallback: Local AI when P2C2R unavailable
    /// </summary>
    void UpdateEnemyAI_Local()
    {
        foreach (var enemy in enemies)
        {
            if (enemy == null) continue;
            
            // Simple AI: Move down and toward player
            Vector3 toPlayer = (transform.position - enemy.transform.position).normalized;
            Vector3 movement = new Vector3(toPlayer.x * 0.5f, -1f, 0f);
            enemy.transform.position += movement * 2f * Time.deltaTime;
            
            // Remove if off screen
            if (enemy.transform.position.y < -5f)
            {
                Destroy(enemy);
                enemies.Remove(enemy);
                break;
            }
        }
    }
    
    List<float[]> GetEnemyPositions()
    {
        var positions = new List<float[]>();
        foreach (var enemy in enemies)
        {
            if (enemy != null)
            {
                positions.Add(new float[] { 
                    enemy.transform.position.x, 
                    enemy.transform.position.y 
                });
            }
        }
        return positions;
    }
    
    void ApplyAIDecisions(string aiData)
    {
        // In production, parse AI response and apply enemy movements
        // For demo, just move enemies based on simple logic
        UpdateEnemyAI_Local();
    }
    
    void OnGUI()
    {
        // Display game stats
        GUI.Label(new Rect(10, 10, 200, 20), $"Score: {score}");
        GUI.Label(new Rect(10, 30, 200, 20), $"Enemies: {enemies.Count}/{maxEnemies}");
        GUI.Label(new Rect(10, 50, 200, 20), $"Killed: {enemiesKilled}");
        
        if (useP2C2R)
        {
            GUI.Label(new Rect(10, 70, 200, 20), $"P2C2R Latency: {p2c2rLatency:F3}s");
            GUI.Label(new Rect(10, 90, 250, 20), "AI: Peer Network (Uber Mode) ✓");
        }
        else
        {
            GUI.Label(new Rect(10, 90, 200, 20), "AI: Local (Fallback)");
        }
    }
}
