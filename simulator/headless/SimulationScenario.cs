using System.Text.Json.Nodes;
using Platforms;
using UnityEngine;

public sealed class SimulationScenario
{
    private static readonly string[] ResetUnlocks = ["loops", "debug", "debug_2", "timing", "lists", "dictionaries", "costs", "auto_unlock", "operators", "variables", "senses", "utilities", "functions", "import", "simulation", "underground_senses", "grass"];
    public string Preset { get; private set; } = "max";
    public Dictionary<string, int> Unlocks { get; private set; } = new();
    public ItemBlock Items { get; private set; } = ItemBlock.CreateEmpty();
    public LeaderboardSO? Leaderboard { get; private set; }
    public JsonObject? Goal { get; private set; }
    public string[] UnlockStrings => BuiltinFunctions.resetUnlocks.Concat(Unlocks.Where(p => p.Value > 0).Select(p => p.Value == 1 ? p.Key : $"{p.Key}_{p.Value}")).ToArray();

    public static SimulationScenario Load(string? scenarioPath, string? preset, string? leaderboard, string? savePath,
        Dictionary<string, double> items, Dictionary<string, int> unlocks)
    {
        var data = scenarioPath == null ? new JsonObject() : JsonNode.Parse(File.ReadAllText(scenarioPath))!.AsObject();
        foreach (var key in data.Select(p => p.Key))
            if (key is not ("preset" or "items" or "unlocks" or "goal" or "leaderboard"))
                throw new ArgumentException($"Unknown scenario field: {key}");
        var result = new SimulationScenario();
        string? boardName = leaderboard ?? data["leaderboard"]?.GetValue<string>();
        if (boardName != null)
        {
            boardName = Normalize(boardName).Replace("lb_", "", StringComparison.Ordinal);
            result.Leaderboard = ResourceManager.GetAllLeaderboards().SingleOrDefault(b => b.leaderboardName == boardName)
                ?? throw new ArgumentException($"Unknown leaderboard: {boardName}");
            if (preset != null || savePath != null) throw new ArgumentException("Leaderboard cannot be combined with preset/save");
        }
        result.Preset = result.Leaderboard?.everythingUnlocked == true ? "all" : result.Leaderboard != null ? "reset" : preset ?? data["preset"]?.GetValue<string>() ?? "max";
        if (savePath != null) result.Preset = "reset";
        if (result.Preset is not ("max" or "all" or "reset")) throw new ArgumentException("Unknown preset");
        result.Unlocks = ResourceManager.GetAllUnlocks().ToDictionary(u => u.unlockName,
            u => u.enabled && (result.Preset == "all" || result.Preset == "max" && u.dlc == EDlcType.None) ? u.maxUnlockLevel : 0);
        if (result.Preset == "reset") foreach (string key in ResetUnlocks) result.Unlocks[key] = 1;
        if (result.Preset != "reset")
        {
            result.SetItem("Pumpkin", 1_000_000_000);
            result.SetItem("Power", 1_000_000_000);
        }
        if (result.Leaderboard != null)
        {
            result.Items = new ItemBlock(result.Leaderboard.startItems);
            if (result.Leaderboard.singleDrone) { result.Unlocks["megafarm"] = 0; result.Unlocks["expand"] = 5; }
        }
        if (savePath != null)
        {
            var saved = JsonNode.Parse(File.ReadAllText(savePath))!.AsObject();
            foreach (string key in result.Unlocks.Keys) result.Unlocks[key] = 0;
            foreach (var entry in saved["unlocks"]!.AsArray())
            {
                string key = entry!.GetValue<string>(); int level = 1;
                if (!result.Unlocks.ContainsKey(key))
                {
                    int index = key.LastIndexOf('_');
                    if (index < 0 || !int.TryParse(key[(index + 1)..], out level)) continue;
                    key = key[..index];
                }
                if (result.Unlocks.ContainsKey(key)) result.SetUnlock(key, level);
            }
            foreach (var entry in saved["items"]!["serializeList"]!.AsArray())
                result.SetItem(entry!["name"]!.GetValue<string>(), entry["nr"]!.GetValue<double>());
        }
        if (data["items"] is JsonObject itemData)
            foreach (var pair in itemData) result.SetItem(pair.Key, pair.Value!.GetValue<double>());
        if (data["unlocks"] is JsonObject unlockData)
            foreach (var pair in unlockData) result.SetUnlock(pair.Key, pair.Value!.GetValue<int>());
        foreach (var pair in items) result.SetItem(pair.Key, pair.Value);
        foreach (var pair in unlocks) result.SetUnlock(pair.Key, pair.Value);
        if (result.Leaderboard != null) result.Unlocks["explosive_drill"] = 0;
        result.Goal = data["goal"]?.AsObject();
        if (result.Goal != null)
        {
            if (result.Goal.Count == 1 && result.Goal["unlock"] != null)
            {
                string key = Normalize(result.Goal["unlock"]!.GetValue<string>());
                if (!result.Unlocks.ContainsKey(key)) throw new ArgumentException($"Unknown goal unlock: {key}");
            }
            else if (result.Goal.Count == 2 && result.Goal["item"] != null && result.Goal["amount"] != null)
            {
                string key = Normalize(result.Goal["item"]!.GetValue<string>());
                double amount = result.Goal["amount"]!.GetValue<double>();
                if (StringIds.GetItemId(key) < 0 || !double.IsFinite(amount) || amount <= 0) throw new ArgumentException("Invalid item goal");
            }
            else throw new ArgumentException("Goal requires item/amount or unlock");
        }
        return result;
    }

    public Simulation Create(HeadlessRunner runner, int seed, int size)
    {
        var board = Leaderboard;
        // 用种子重放；正式排行榜的加密随机源不能据此预测。
        var sim = new Simulation(runner, board != null && board.dlc == EDlcType.None ? EDlcMask.None : EDlcMask.All, UnlockStrings, Items,
            board?.leaderboardName ?? "", board?.steamLeaderboardName ?? "", board?.leaderboardType ?? LeaderboardType.simulation,
            board?.fullyGenerateUnderground ?? true, seed, worldSizeOverride: size == 0 ? default : new Vector2Int(size, size),
            whitelistedGroundFeatureUnlocks: board?.whitelistedGroundFeatureUnlocks,
            pretendedFeatureChunks: board?.pretendedFeatureChunks, pretendedChunkDepths: board?.pretendedChunkDepths, useSeededLeaderboardRandom: true);
        sim.singleDrone = board?.singleDrone ?? false;
        return sim;
    }

    public bool? GoalReached(Farm farm)
    {
        if (Goal?["unlock"] != null) return farm.NumUnlocked(Normalize(Goal["unlock"]!.GetValue<string>())) > 0;
        if (Goal?["item"] != null) return farm.Items.items[StringIds.GetItemId(Normalize(Goal["item"]!.GetValue<string>()))] >= Goal["amount"]!.GetValue<double>();
        if (Leaderboard == null) return null;
        if (Leaderboard.leaderboardType == LeaderboardType.reset) return farm.NumUnlocked(Leaderboard.dlc == EDlcType.Mining ? "underground_leaderboard" : "leaderboard") > 0;
        return farm.Items.items.Zip(Leaderboard.goalItems.items).All(p => p.First >= p.Second);
    }

    private void SetItem(string name, double amount)
    {
        int id = StringIds.GetItemId(Normalize(name));
        if (id < 0 || !double.IsFinite(amount) || amount < 0) throw new ArgumentException($"Invalid item: {name}={amount}");
        Items.items[id] = amount;
    }
    private void SetUnlock(string name, int level)
    {
        string key = Normalize(name);
        var unlock = ResourceManager.GetUnlock(key);
        if (unlock == null || level < 0 || level > unlock.maxUnlockLevel) throw new ArgumentException($"Invalid unlock: {name}={level}");
        Unlocks[key] = level;
    }
    private static string Normalize(string name) => name[(name.LastIndexOf('.') + 1)..].ToLowerInvariant();
}
