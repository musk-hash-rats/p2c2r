using UnityEngine;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace P2C2R
{
    /// <summary>
    /// Helper component for AI-powered NPCs that use P2C2R for dialogue generation
    /// </summary>
    public class P2C2RNPC : MonoBehaviour
    {
        [Header("NPC Configuration")]
        [Tooltip("NPC name for dialogue context")]
        public string npcName = "Guard";

        [Tooltip("NPC personality/role")]
        [TextArea(3, 5)]
        public string personality = "A friendly guard who protects the village";

        [Tooltip("AI model to use for dialogue")]
        public string aiModel = "npc_dialogue";

        [Header("Dialogue Settings")]
        [Tooltip("Enable local fallback if P2C2R unavailable")]
        public bool enableFallback = true;

        [Tooltip("Cache dialogue responses")]
        public bool cacheResponses = true;

        [Header("Events")]
        public UnityEngine.Events.UnityEvent<string> onDialogueReceived;
        public UnityEngine.Events.UnityEvent<string> onDialogueFailed;

        // Dialogue cache
        private Dictionary<string, string> _dialogueCache = new Dictionary<string, string>();

        // Current dialogue task
        private Task<TaskResult> _currentTask;

        /// <summary>
        /// Generate NPC dialogue based on player input
        /// </summary>
        public async void GenerateDialogue(string playerInput)
        {
            // Check cache first
            if (cacheResponses && _dialogueCache.TryGetValue(playerInput, out string cachedResponse))
            {
                Debug.Log($"[P2C2RNPC] Using cached dialogue for: {playerInput}");
                onDialogueReceived?.Invoke(cachedResponse);
                return;
            }

            // Check if P2C2R is connected
            if (!P2C2RClient.Instance.IsConnected)
            {
                Debug.LogWarning($"[P2C2RNPC] P2C2R not connected. Using fallback dialogue.");
                
                if (enableFallback)
                {
                    string fallback = GetFallbackDialogue(playerInput);
                    onDialogueReceived?.Invoke(fallback);
                }
                else
                {
                    onDialogueFailed?.Invoke("P2C2R not connected");
                }
                return;
            }

            // Prepare AI input
            var input = new Dictionary<string, object>
            {
                { "npc_name", npcName },
                { "personality", personality },
                { "player_input", playerInput },
                { "context", GetContextData() }
            };

            Debug.Log($"[P2C2RNPC] Requesting dialogue from P2C2R...");

            // Submit to P2C2R
            _currentTask = P2C2RClient.Instance.SubmitAITask(aiModel, input, OnDialogueResult);

            // Wait for result (or timeout)
            var result = await _currentTask;

            if (!result.success)
            {
                Debug.LogWarning($"[P2C2RNPC] Dialogue generation failed: {result.error}");
                
                if (enableFallback)
                {
                    string fallback = GetFallbackDialogue(playerInput);
                    onDialogueReceived?.Invoke(fallback);
                }
                else
                {
                    onDialogueFailed?.Invoke(result.error);
                }
            }
        }

        private void OnDialogueResult(TaskResult result)
        {
            if (result.success)
            {
                // Parse dialogue from result
                // In real implementation, parse JSON properly
                string dialogue = ExtractDialogueFromResult(result.data);

                Debug.Log($"[P2C2RNPC] Received dialogue: {dialogue}");

                // Cache it
                if (cacheResponses)
                {
                    // Would need to extract original player input from context
                    // _dialogueCache[playerInput] = dialogue;
                }

                onDialogueReceived?.Invoke(dialogue);
            }
        }

        private string ExtractDialogueFromResult(string data)
        {
            // Simplified parsing (in real implementation, use proper JSON parser)
            // For now, return mock dialogue
            return $"{npcName}: Hello there, traveler!";
        }

        private Dictionary<string, object> GetContextData()
        {
            // Gather context about the game state
            return new Dictionary<string, object>
            {
                { "location", "village_entrance" },
                { "time_of_day", "morning" },
                { "player_reputation", 50 },
                { "quest_state", "none" }
            };
        }

        private string GetFallbackDialogue(string playerInput)
        {
            // Simple local fallback dialogue
            string[] fallbacks = new string[]
            {
                $"{npcName}: Greetings, traveler.",
                $"{npcName}: How can I help you?",
                $"{npcName}: Safe travels!",
                $"{npcName}: I'm on duty right now."
            };

            return fallbacks[Random.Range(0, fallbacks.Length)];
        }
    }
}
