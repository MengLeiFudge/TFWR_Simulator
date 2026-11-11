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
    /// <summary>实际读取的场景和存档字节哈希，用于复核初始条件。</summary>
    public Dictionary<string, string> InputHashes { get; } = new();
    /// <summary>是否显式覆盖场景的库存、科技或目标；地图覆盖由CLI另行记录。</summary>
    public bool HasOverrides { get; private set; }

    /// <summary>读取初始条件；CLI覆盖场景值，排行榜与preset/save互斥。</summary>
    /// <param name="scenarioPath">可选场景JSON路径。</param>
    /// <param name="preset">命令行科技预设。</param>
    /// <param name="leaderboard">命令行排行榜名称。</param>
    /// <param name="savePath">只导入科技和库存的存档路径。</param>
    /// <param name="items">命令行库存覆盖。</param>
    /// <param name="unlocks">命令行科技覆盖。</param>
    /// <returns>通过结构、名称和数值检查的场景。</returns>
    public static SimulationScenario Load(string? scenarioPath, string? preset, string? leaderboard, string? savePath,
        Dictionary<string, double> items, Dictionary<string, int> unlocks)
    {
        var result = new SimulationScenario();
        var data = scenarioPath == null ? new JsonObject() : result.ReadInput(scenarioPath);
        foreach (string field in new[] { "items", "unlocks" })
            if (data.ContainsKey(field) && data[field] is not JsonObject)
                throw new ArgumentException($"Scenario {field} must be an object: {scenarioPath}");
        foreach (var key in data.Select(p => p.Key))
            if (key is not ("preset" or "items" or "unlocks" or "goal" or "leaderboard"))
                throw new ArgumentException($"Unknown scenario field: {key}");

        string? boardName = leaderboard ?? data["leaderboard"]?.GetValue<string>();
        if (boardName != null)
        {
            boardName = Normalize(boardName);
            if (boardName.StartsWith("lb_", StringComparison.Ordinal)) boardName = boardName[3..];
            result.Leaderboard = ResourceManager.GetAllLeaderboards().SingleOrDefault(b => b.leaderboardName == boardName)
                ?? throw new ArgumentException($"Unknown leaderboard: {boardName}");
            if (preset != null || data["preset"] != null || savePath != null)
                throw new ArgumentException("Leaderboard cannot be combined with preset/save; use item/unlock overrides instead");
        }
        result.Preset = result.Leaderboard?.everythingUnlocked == true ? "all" : result.Leaderboard != null ? "reset" : preset ?? data["preset"]?.GetValue<string>() ?? "max";
        if (savePath != null)
        {
            if (preset != null || data["preset"] != null) throw new ArgumentException("Save cannot be combined with preset; use item/unlock overrides instead");
            result.Preset = "reset";
        }
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
            var saved = result.ReadInput(savePath);
            if (saved["unlocks"] is not JsonArray savedUnlocks || saved["items"] is not JsonObject savedItems || savedItems["serializeList"] is not JsonArray savedRows)
                throw new ArgumentException($"Save requires unlocks and items.serializeList arrays: {savePath}");
            foreach (string key in result.Unlocks.Keys) result.Unlocks[key] = 0;
            foreach (var entry in savedUnlocks)
            {
                string key = entry!.GetValue<string>(); int level = 1;
                if (!result.Unlocks.ContainsKey(key))
                {
                    int index = key.LastIndexOf('_');
                    if (index < 0 || !int.TryParse(key[(index + 1)..], out level)) continue;
                    key = key[..index];
                }
                if (result.Unlocks.TryGetValue(key, out int previous))
                {
                    if (level < 0) throw new ArgumentException($"Invalid save unlock: {entry}");
                    // 原始名称和等级名称可能同时存在；导入结果不依赖序列化顺序。
                    result.SetUnlock(key, Math.Max(previous, level));
                }
            }
            var names = new HashSet<string>();
            foreach (var entry in savedRows)
            {
                if (entry is not JsonObject row || row["name"] == null || row["nr"] == null)
                    throw new ArgumentException($"Save item requires name/nr: {savePath}");
                string name = row["name"]!.GetValue<string>();
                if (!names.Add(Normalize(name))) throw new ArgumentException($"Duplicate save item: {name}");
                result.SetItem(name, row["nr"]!.GetValue<double>());
            }
        }
        if (data["items"] is JsonObject itemData)
        {
            var names = new HashSet<string>();
            foreach (var pair in itemData)
            {
                if (!names.Add(Normalize(pair.Key))) throw new ArgumentException($"Duplicate scenario item: {pair.Key}");
                result.SetItem(pair.Key, pair.Value!.GetValue<double>());
            }
        }
        if (data["unlocks"] is JsonObject unlockData)
        {
            var names = new HashSet<string>();
            foreach (var pair in unlockData)
            {
                if (!names.Add(Normalize(pair.Key))) throw new ArgumentException($"Duplicate scenario unlock: {pair.Key}");
                result.SetUnlock(pair.Key, pair.Value!.GetValue<int>());
            }
        }
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
        result.HasOverrides = (data["items"]?.AsObject().Count ?? 0) > 0 || (data["unlocks"]?.AsObject().Count ?? 0) > 0
            || items.Count > 0 || unlocks.Count > 0 || result.Goal != null;
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
    /// <summary>将游戏常量名称或裸名称转换为资源表键。</summary>
    /// <param name="name">例如Items.Coal、Unlocks.Mining或coal。</param>
    /// <returns>去除常量组前缀后的小写名称。</returns>
    internal static string Normalize(string name) => name[(name.LastIndexOf('.') + 1)..].ToLowerInvariant();

    /// <summary>只读加载JSON对象，并冻结此次解析使用的字节哈希。</summary>
    /// <param name="path">场景或存档JSON路径。</param>
    /// <returns>输入对象；非对象根节点直接拒绝。</returns>
    private JsonObject ReadInput(string path)
    {
        byte[] bytes = File.ReadAllBytes(path);
        var data = JsonNode.Parse(System.Text.Encoding.UTF8.GetString(bytes).TrimStart('\uFEFF')) as JsonObject
            ?? throw new ArgumentException($"JSON input must be an object: {path}");
        InputHashes[path] = Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(bytes));
        return data;
    }
}
