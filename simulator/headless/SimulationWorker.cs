using System.Diagnostics;
using System.Text.Json;
using System.Text.Json.Nodes;

public static class SimulationWorker
{
    public static JsonObject Run(SimulationOptions options)
    {
        var watch = Stopwatch.StartNew();
        string dataPath = Path.Combine(AppContext.BaseDirectory, "data", "assets.json");
        AssetLoader.Load(dataPath);
        var workspace = MainSim.Inst.workspace;
        Node syntax = workspace.Load(options.Script);
        if (options.Output != null && workspace.SourceHashes.ContainsKey(options.Output) || options.Trace != null && workspace.SourceHashes.ContainsKey(options.Trace))
            throw new ArgumentException("Report/trace cannot overwrite a source module");
        if (options.SyntaxOnly)
            return JsonSerializer.SerializeToNode(new { backend = "csharp-native", stop_reason = "syntax_valid", script = options.Script,
                dependencies = workspace.SourceHashes, wall_seconds = watch.Elapsed.TotalSeconds, error = (string?)null })!.AsObject();
        var scenario = SimulationScenario.Load(options.Scenario, options.Preset, options.Leaderboard, options.Save, options.Items, options.Unlocks);
        double[] initial = (double[])scenario.Items.items.Clone();
        var runner = new HeadlessRunner();
        using var monitor = new SimulationMonitor(watch, options.WallSeconds, options.MaxCalls, options.MaxNodes, options.Trace);
        SimulationMonitor.Current = monitor;
        var sim = scenario.Create(runner, options.Seed, options.Size);
        var execution = new Execution(sim, syntax, 1);
        sim.StartProgramExecution(execution);
        var goal = Duration.FromSeconds(options.GameSeconds);
        object gate = new();
        double nextProgress = 2;
        long steps = 0;
        string? internalError = null;
        try
        {
            while (sim.IsExecuting() && sim.CurrentTime < goal && !sim.Paused && watch.Elapsed.TotalSeconds < options.WallSeconds)
            {
                sim.RunNextStep(goal, gate);
                steps++;
                if (watch.Elapsed.TotalSeconds >= nextProgress)
                {
                    Console.Error.WriteLine($"progress game={sim.CurrentTime.Seconds:F6}s wall={watch.Elapsed.TotalSeconds:F2}s calls={monitor.CallCount}");
                    nextProgress = watch.Elapsed.TotalSeconds + 2;
                }
            }
        }
        catch (Exception ex) { internalError = ex.ToString(); }
        string? error = monitor.LimitReason != null ? null : internalError ?? runner.Logger.Error;
        string reason = monitor.LimitReason ?? (error != null ? "error" : !sim.IsExecuting() ? "finished" : sim.CurrentTime >= goal ? "game_time_limit" : sim.Paused ? "paused" : "wall_time_limit");
        var farm = sim.farm;
        var grid = farm.grid;
        var report = new
        {
            schema_version = 1, backend = "csharp-native", kind = "local_prediction",
            script = options.Script, seed = options.Seed, preset = scenario.Preset,
            leaderboard = scenario.Leaderboard?.leaderboardName,
            random_mode = scenario.Leaderboard == null ? "seeded_simulate" : "seeded_leaderboard_screening",
            dependencies = workspace.SourceHashes,
            assembly_sha256 = Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(typeof(SimulationWorker).Assembly.Location))),
            resources_sha256 = Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(File.ReadAllBytes(dataPath))),
            initial_state = new { unlocks = scenario.Unlocks, items = ResourceManager.GetAllItems().ToDictionary(x => x.itemName, x => initial[x.itemId]) },
            stop_reason = reason, state_complete = error == null && monitor.LimitReason == null,
            goal_reached = scenario.GoalReached(farm),
            game_seconds = sim.CurrentTime.Seconds, nanoseconds = sim.CurrentTime.nanoseconds,
            wall_seconds = watch.Elapsed.TotalSeconds, steps, interpreter_nodes = monitor.NodeCount,
            api_calls = monitor.Calls, api_ticks = monitor.ApiTicks, total_calls = monitor.CallCount,
            inventory = ResourceManager.GetAllItems().ToDictionary(x => x.itemName, x => farm.Items.items[x.itemId]),
            net_inventory = ResourceManager.GetAllItems().ToDictionary(x => x.itemName, x => farm.Items.items[x.itemId] - initial[x.itemId]),
            state = new
            {
                width = grid.WorldSize.x, height = grid.WorldSize.y,
                unlocks = ResourceManager.GetAllUnlocks().ToDictionary(u => u.unlockName, u => farm.NumUnlocked(u.unlockName)),
                used_power = farm.UsedPower,
                drones = farm.drones.Where(d => d != null).Select(d => new { id = d.DroneId, x = d.pos.x, y = d.pos.y, depth = d.depth, hover = d.fleightHeight, hat = d.hat.hatSO.hatName }).ToArray(),
                cells = grid.cells.Select(c => new { depth = c.depth, water = c.waterVolume, entity = c.entity?.objectSO.objectName }).ToArray()
            },
            depths = grid.cells.Select(c => c.depth).ToArray(),
            messages = runner.Logger.Messages, output_dropped = runner.Logger.Dropped, error,
            limits = new { game_seconds = options.GameSeconds, wall_seconds = options.WallSeconds, api_calls = options.MaxCalls, nodes = options.MaxNodes },
            achievement_verification = "not_recorded"
        };
        return JsonSerializer.SerializeToNode(report)!.AsObject();
    }
}
