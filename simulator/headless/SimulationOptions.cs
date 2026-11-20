using System.Globalization;
using System.Security.Cryptography;
using System.Text.Json.Nodes;

public sealed class SimulationOptions
{
    public string Script { get; private set; } = "";
    public int Seed { get; private set; } = 1;
    public int[] Seeds { get; private set; } = [];
    public int Jobs { get; private set; } = Math.Max(1, Environment.ProcessorCount);
    public int Size { get; private set; }
    public double GameSeconds { get; private set; } = 30;
    public double WallSeconds { get; private set; } = 10;
    public long MaxCalls { get; private set; } = 2_000_000;
    public long MaxNodes { get; private set; } = 50_000_000;
    public bool Worker { get; private set; }
    public bool SyntaxOnly { get; private set; }
    public string? Preset { get; private set; }
    public string? Scenario { get; private set; }
    public string? Leaderboard { get; private set; }
    public string LeaderboardRandom { get; private set; } = "";
    public string? Save { get; private set; }
    public string? Output { get; private set; }
    public string? Trace { get; private set; }
    public string? HotSpots { get; private set; }
    public Dictionary<string, double> Items { get; } = new(StringComparer.OrdinalIgnoreCase);
    public Dictionary<string, int> Unlocks { get; } = new(StringComparer.OrdinalIgnoreCase);
    public static string Help => """
        TFWRSimulator <script.py> [options]
          --preset max|all|reset   基础满科技 / 含DLC满科技 / 重置初始条件
          --scenario file.json    初始科技、库存和目标；preset/save与排行榜互斥
          --leaderboard name      排行榜盘面；不给种子时按游戏加密随机跑一轮
          --save save.json        只读导入科技和库存，不恢复地形
          --item NAME=AMOUNT      覆盖初始库存，可重复
          --unlock NAME=LEVEL     覆盖科技等级，可重复
          --size 0                固定地图边长1..32；0按Expand科技决定
          --seed 1                用种子1跑一轮，排行榜据此重放随机
          --seeds 1,2,3           用种子1到3各跑一轮，默认按核数并行
          --jobs 8                并行轮数；只给jobs时按游戏方式随机取8个种子
          --seconds 30            游戏时间上限（别名 --game-seconds）
          --wall-seconds 10       墙钟上限，最大600秒（别名 --timeout）
          --max-api-calls 2000000 内置函数调用上限
          --max-nodes 50000000     原版AST节点执行上限
          --syntax-only           仅检查入口及全部导入模块的游戏语法
          --trace trace.jsonl     记录API应用时刻、参数、返回值与tick
          --hot-spots costs.json  源码行级实际费用与分机账单，不改变游戏计时
          --json report.json      写报告（别名 --output）
        """;

    /// <summary>解析CLI输入并拒绝重复资源名、错误入口和相互覆盖的文件路径。</summary>
    /// <param name="args">入口路径与后续参数；至少包含入口路径。</param>
    /// <returns>传入工作进程的已验证选项。</returns>
    public static SimulationOptions Parse(string[] args)
    {
        var result = new SimulationOptions { Script = Path.GetFullPath(args[0]) };
        if (!Path.GetExtension(result.Script).Equals(".py", StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException($"Script must be a .py file: {result.Script}");
        var seen = new HashSet<string>();
        for (int i = 1; i < args.Length; i++)
        {
            string option = args[i] switch { "--game-seconds" => "--seconds", "--timeout" => "--wall-seconds", "--output" => "--json", _ => args[i] };
            if (option is not ("--item" or "--unlock") && !seen.Add(option)) throw new ArgumentException($"Repeated option: {option}");
            if (option == "--worker") { result.Worker = true; continue; }
            if (option == "--syntax-only") { result.SyntaxOnly = true; continue; }
            if (++i >= args.Length) throw new ArgumentException($"Missing value: {option}");
            string value = args[i];
            switch (option)
            {
                case "--seed": result.Seed = Int(value); break;
                case "--leaderboard-random": result.LeaderboardRandom = value; break;
                case "--seeds": result.Seeds = value.Split(',').Select(Int).ToArray(); break;
                case "--jobs": result.Jobs = Int(value); break;
                case "--size": result.Size = Int(value); break;
                case "--seconds": result.GameSeconds = Double(value); break;
                case "--wall-seconds": result.WallSeconds = Double(value); break;
                case "--max-api-calls": result.MaxCalls = long.Parse(value, CultureInfo.InvariantCulture); break;
                case "--max-nodes": result.MaxNodes = long.Parse(value, CultureInfo.InvariantCulture); break;
                case "--preset": result.Preset = value; break;
                case "--scenario": result.Scenario = Path.GetFullPath(value); break;
                case "--leaderboard": result.Leaderboard = value; break;
                case "--save": result.Save = Path.GetFullPath(value); break;
                case "--json": result.Output = Path.GetFullPath(value); break;
                case "--trace": result.Trace = Path.GetFullPath(value); break;
                case "--hot-spots": result.HotSpots = Path.GetFullPath(value); break;
                case "--item":
                    var item = Pair(value);
                    if (!result.Items.TryAdd(SimulationScenario.Normalize(item.name), Double(item.value)))
                        throw new ArgumentException($"Duplicate item: {item.name}");
                    break;
                case "--unlock":
                    var unlock = Pair(value);
                    if (!result.Unlocks.TryAdd(SimulationScenario.Normalize(unlock.name), Int(unlock.value)))
                        throw new ArgumentException($"Duplicate unlock: {unlock.name}");
                    break;
                default: throw new ArgumentException($"Unknown option: {option}");
            }
        }
        if (seen.Contains("--seed") && seen.Contains("--seeds")) throw new ArgumentException("Use seed or seeds, not both");
        bool seedGiven = seen.Contains("--seed") || seen.Contains("--seeds");
        if (result.Jobs is < 1 or > 64 && seen.Contains("--jobs"))
            throw new ArgumentException("Jobs must be between 1 and 64");
        if (result.LeaderboardRandom.Length == 0)
        {
            bool hasBoard = result.Leaderboard != null;
            if (!hasBoard && !seedGiven && !result.SyntaxOnly && result.Scenario != null)
                hasBoard = JsonNode.Parse(File.ReadAllText(result.Scenario))?["leaderboard"] != null;
            result.LeaderboardRandom = hasBoard && !seedGiven ? "game" : "seeded";
        }
        if (result.LeaderboardRandom is not ("game" or "seeded"))
            throw new ArgumentException("Leaderboard random mode must be game or seeded");
        if (result.Seeds.Length == 0)
            result.Seeds = result.LeaderboardRandom == "game"
                ? Enumerable.Range(0, seen.Contains("--jobs") ? result.Jobs : 1).Select(_ => RandomNumberGenerator.GetInt32(int.MaxValue)).ToArray()
                : [result.Seed];
        if (!seen.Contains("--jobs")) result.Jobs = Math.Max(1, Math.Min(Math.Min(Environment.ProcessorCount, result.Seeds.Length), 64));
        if (result.Seeds.Length > 100 || result.Seeds.Distinct().Count() != result.Seeds.Length || result.Seeds.Any(s => s < 0)
            || result.Jobs < 1 || result.Jobs > 64 || result.MaxCalls < 1 || result.MaxNodes < 1 || result.Size is < 0 or > 32
            || !double.IsFinite(result.GameSeconds) || result.GameSeconds <= 0 || result.GameSeconds > 86400
            || !double.IsFinite(result.WallSeconds) || result.WallSeconds <= 0 || result.WallSeconds > 600)
            throw new ArgumentException("Invalid seed or simulation budget");
        if (result.Save != null && result.Preset != null) throw new ArgumentException("Use save or preset, not both");
        var inputs = new[] { result.Script, result.Scenario, result.Save }.Where(p => p != null).ToArray();
        var outputs = new[] { result.Output, result.Trace, result.HotSpots }.Where(p => p != null).ToArray();
        if (outputs.Any(p => string.Equals(Path.GetExtension(p), ".py", StringComparison.OrdinalIgnoreCase)))
            throw new ArgumentException("Report, trace and hot-spot paths cannot name Python source files");
        if (outputs.Distinct(StringComparer.OrdinalIgnoreCase).Count() != outputs.Length || outputs.Any(p => inputs.Contains(p, StringComparer.OrdinalIgnoreCase)))
            throw new ArgumentException("Input and diagnostic output paths must be different");
        if (result.SyntaxOnly && result.HotSpots != null) throw new ArgumentException("Hot spots require script execution, not syntax-only mode");
        return result;
    }

    public IEnumerable<string> WorkerArguments(int seed, double seconds)
    {
        yield return Script; yield return "--worker";
        foreach (var pair in new (string name, string? value)[] {
            ("--seed",seed.ToString()), ("--wall-seconds",seconds.ToString("R",CultureInfo.InvariantCulture)),
            ("--seconds",GameSeconds.ToString("R",CultureInfo.InvariantCulture)), ("--max-api-calls",MaxCalls.ToString()),
            ("--max-nodes",MaxNodes.ToString()), ("--size",Size.ToString()), ("--preset",Preset),
            ("--scenario",Scenario), ("--leaderboard",Leaderboard), ("--leaderboard-random",LeaderboardRandom), ("--save",Save),
            ("--trace",SeedOutput(Trace, seed)), ("--hot-spots",SeedOutput(HotSpots, seed)) })
            if (pair.value != null) { yield return pair.name; yield return pair.value; }
        foreach (var item in Items) { yield return "--item"; yield return $"{item.Key}={item.Value.ToString("R",CultureInfo.InvariantCulture)}"; }
        foreach (var unlock in Unlocks) { yield return "--unlock"; yield return $"{unlock.Key}={unlock.Value}"; }
        if (SyntaxOnly) yield return "--syntax-only";
    }
    private string? SeedOutput(string? path, int seed) => path == null || Seeds.Length == 1 ? path
        : Path.Combine(Path.GetDirectoryName(path)!, $"{Path.GetFileNameWithoutExtension(path)}.seed-{seed}{Path.GetExtension(path)}");
    private static int Int(string value) => int.Parse(value, CultureInfo.InvariantCulture);
    private static double Double(string value) => double.Parse(value, CultureInfo.InvariantCulture);
    private static (string name, string value) Pair(string text)
    {
        int index = text.IndexOf('=');
        if (index < 1 || index == text.Length - 1) throw new ArgumentException($"Expected NAME=VALUE: {text}");
        return (text[..index], text[(index + 1)..]);
    }
}
