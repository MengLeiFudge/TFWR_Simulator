using System.Globalization;

namespace TFWRMechanismModel;

internal static class Program
{
    public static int Main(string[] args)
    {
        try
        {
            if (args.Length == 0 || args[0] is "-h" or "--help" or "help")
            {
                PrintHelp();
                return 0;
            }

            string command = args[0].ToLowerInvariant();
            var reader = new ArgumentReader(args.Skip(1));

            switch (command)
            {
                case "all":
                    RunDinosaur(reader);
                    Console.WriteLine();
                    RunCactus(reader);
                    Console.WriteLine();
                    RunCompanion(reader);
                    return 0;
                case "dinosaur":
                    RunDinosaur(reader);
                    return 0;
                case "cactus":
                    RunCactus(reader);
                    return 0;
                case "companion":
                    RunCompanion(reader);
                    return 0;
                default:
                    Console.Error.WriteLine($"Unknown command: {command}");
                    PrintHelp();
                    return 2;
            }
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex.Message);
            return 1;
        }
    }

    private static void RunDinosaur(ArgumentReader reader)
    {
        int size = reader.GetInt("size", 32);
        bool oneStepRecoverDetour = reader.GetBool("recover-detour", false);
        var options = new DinosaurOptions
        {
            Size = size,
            Runs = reader.GetInt("runs", 50),
            Seed = reader.GetInt("seed", 20260625),
            MaxMoves = reader.GetInt("max-moves", 2_000_000),
            InitialMoveTicks = reader.GetInt("move-ticks", 400),
            IncludeHeavy = reader.GetBool("include-heavy", false),
            PolicyFilter = reader.TryGetString("policy"),
            ChaseLimitNumerator = reader.GetInt("chase-limit-num", 9),
            ChaseLimitDenominator = reader.GetInt("chase-limit-den", 25),
            ChaseLateAbortNumerator = reader.GetInt("chase-late-abort-num", 0),
            ChaseLateAbortDenominator = reader.GetInt("chase-late-abort-den", 1),
            ChaseLateAbortMinAppleX = reader.GetInt("chase-late-abort-min-apple-x", 0),
            ExtraChaseLimitNumerator = reader.GetInt("extra-chase-limit-num", 0),
            ExtraChaseLimitDenominator = reader.GetInt("extra-chase-limit-den", 1),
            ExtraChaseMinAppleX = reader.GetInt("extra-chase-min-apple-x", 0),
            ExtraChaseFillStepNumerator = reader.GetInt("extra-chase-fill-step-num", -1),
            ExtraChaseFillStepDenominator = reader.GetInt("extra-chase-fill-step-den", 1),
            FillStepNumerator = reader.GetInt("fill-step-num", 15),
            FillStepDenominator = reader.GetInt("fill-step-den", 16),
            PhaseStats = reader.GetBool("phase-stats", false),
            CycleAdjacentMaxSkip = reader.GetInt("cycle-adjacent-max-skip", 0),
            CycleGreedyShortcutMaxSkip = reader.GetInt("cycle-greedy-shortcut-max-skip", 0),
            RecoverDetourMaxSteps = reader.GetInt("recover-detour-max-steps", oneStepRecoverDetour ? 1 : size * size),
            CycleBfsShortcut = reader.GetBool("cycle-bfs-shortcut", false),
            CheckTickCost = reader.GetInt("check-tick-cost", 0),
            CycleUseMoveResult = reader.GetBool("cycle-use-move-result", false),
            UseMoveResult = reader.GetBool("use-move-result", true),
            CycleWaitStats = reader.GetBool("cycle-wait-stats", false),
            CycleEntryStats = reader.GetBool("cycle-entry-stats", false),
            RecoverSouthEdgeProbe = reader.GetBool("recover-south-edge-probe", false),
            RecoverSouthEdgeCycle = reader.GetBool("recover-south-edge-cycle", false),
            RecoverSouthSweep = reader.GetBool("recover-south-sweep", false),
            RecoverUseMoveResult = reader.GetBool("recover-use-move-result", false),
            ChaseSkipLeftX = reader.GetInt("chase-skip-left-x", 0),
            RecoverWestStopX = reader.GetInt("recover-west-stop-x", 0),
            RecoverBfsToOrigin = reader.GetBool("recover-bfs-to-origin", false),
            RecoverBfsMaxDepth = reader.GetInt("recover-bfs-max-depth", 64),
            RecoverBfsMaxNodes = reader.GetInt("recover-bfs-max-nodes", size * size),
            ChaseVerticalUseMoveResult = reader.GetBool("chase-vertical-use-move-result", false),
        };

        IReadOnlyList<DinosaurAggregate> summaries = DinosaurModel.Run(options);

        Console.WriteLine("Dinosaur action model");
        Console.WriteLine($"  size={options.Size} runs={options.Runs} seed={options.Seed} target_length={options.Size * options.Size - 1} chase_limit={options.ChaseLimitNumerator}/{options.ChaseLimitDenominator} chase_late_abort={options.ChaseLateAbortNumerator}/{options.ChaseLateAbortDenominator} chase_late_abort_min_apple_x={options.ChaseLateAbortMinAppleX} extra_chase_limit={options.ExtraChaseLimitNumerator}/{options.ExtraChaseLimitDenominator} extra_chase_min_apple_x={options.ExtraChaseMinAppleX} extra_chase_fill_step={options.ExtraChaseFillStepNumerator}/{options.ExtraChaseFillStepDenominator} fill_step={options.FillStepNumerator}/{options.FillStepDenominator} chase_skip_left_x={options.ChaseSkipLeftX} recover_west_stop_x={options.RecoverWestStopX} recover_bfs_to_origin={options.RecoverBfsToOrigin} recover_bfs_max_depth={options.RecoverBfsMaxDepth} recover_bfs_max_nodes={options.RecoverBfsMaxNodes} chase_vertical_use_move_result={options.ChaseVerticalUseMoveResult} cycle_adjacent_max_skip={options.CycleAdjacentMaxSkip} cycle_greedy_shortcut_max_skip={options.CycleGreedyShortcutMaxSkip} recover_detour_max_steps={options.RecoverDetourMaxSteps} recover_south_edge_probe={options.RecoverSouthEdgeProbe} recover_south_edge_cycle={options.RecoverSouthEdgeCycle} recover_south_sweep={options.RecoverSouthSweep} recover_use_move_result={options.RecoverUseMoveResult} cycle_bfs_shortcut={options.CycleBfsShortcut} cycle_use_move_result={options.CycleUseMoveResult} use_move_result={options.UseMoveResult} check_tick_cost={options.CheckTickCost} cycle_wait_stats={options.CycleWaitStats} cycle_entry_stats={options.CycleEntryStats}");
        Console.WriteLine("  action_ticks count move(); can_move()/measure() are reported separately and can be folded in with --check-tick-cost.");

        foreach (DinosaurAggregate summary in summaries)
        {
            Console.WriteLine($"  policy={summary.Policy}");
            Console.WriteLine($"    completed={summary.Completed}/{summary.Runs} rate={ModelMath.FormatPercent(summary.CompletionRate)} collisions={summary.Collisions} walls={summary.Walls} move_limits={summary.MoveLimits}");
            Console.WriteLine($"    avg_moves={ModelMath.FormatDouble(summary.AverageMoves)} avg_action_ticks={ModelMath.FormatDouble(summary.AverageActionTicks)} avg_apples={ModelMath.FormatDouble(summary.AverageApples)} avg_final_length={ModelMath.FormatDouble(summary.AverageFinalLength)} avg_shortcuts={ModelMath.FormatDouble(summary.AverageShortcuts)}");
            Console.WriteLine($"    avg_can_move_checks={ModelMath.FormatDouble(summary.AverageCanMoveChecks)} avg_measure_checks={ModelMath.FormatDouble(summary.AverageMeasureChecks)} avg_script_checks={ModelMath.FormatDouble(summary.AverageScriptChecks)}");
            if (options.CheckTickCost > 0)
            {
                double checkTicks = summary.AverageScriptChecks * options.CheckTickCost;
                Console.WriteLine($"    avg_check_ticks={ModelMath.FormatDouble(checkTicks)} avg_total_ticks_with_checks={ModelMath.FormatDouble(summary.AverageActionTicks + checkTicks)}");
            }

            Console.WriteLine($"    avg_moves_per_apple={ModelMath.FormatDouble(summary.AverageMovesPerApple)} avg_action_ticks_per_apple={ModelMath.FormatDouble(summary.AverageActionTicksPerApple)}");
            if (options.PhaseStats && summary.PhaseStats.Count > 0)
            {
                Console.WriteLine("    phase_stats:");
                foreach ((string phase, DinosaurPhaseStats stats) in summary.PhaseStats.OrderByDescending(pair => pair.Value.ActionTicks).ThenBy(pair => pair.Key, StringComparer.Ordinal))
                {
                    double actionShare = summary.TotalActionTicks == 0 ? 0.0 : (double)stats.ActionTicks / summary.TotalActionTicks;
                    double movesPerApple = stats.Apples == 0 ? double.PositiveInfinity : (double)stats.Moves / stats.Apples;
                    Console.WriteLine($"      {phase}: avg_moves={ModelMath.FormatDouble((double)stats.Moves / summary.Runs)} avg_action_ticks={ModelMath.FormatDouble((double)stats.ActionTicks / summary.Runs)} avg_apples={ModelMath.FormatDouble((double)stats.Apples / summary.Runs)} moves_per_apple={ModelMath.FormatDouble(movesPerApple)} action_share={ModelMath.FormatPercent(actionShare)}");
                }
            }

            if (options.CycleWaitStats && !summary.CycleWaitStats.IsEmpty)
            {
                DinosaurCycleWaitStats stats = summary.CycleWaitStats;
                Console.WriteLine("    cycle_wait_stats:");
                Console.WriteLine($"      avg_wait_moves_per_apple={ModelMath.FormatDouble(stats.AverageWaitMoves)} waited_apples={stats.WaitedApples} opportunity_samples={stats.OpportunitySamples}");
                Console.WriteLine($"      avg_forward_distance={ModelMath.FormatDouble(stats.AverageForwardDistance)} forward_le1={ModelMath.FormatPercent(stats.ForwardLe1Rate)} forward_le2={ModelMath.FormatPercent(stats.ForwardLe2Rate)} forward_le4={ModelMath.FormatPercent(stats.ForwardLe4Rate)} forward_le8={ModelMath.FormatPercent(stats.ForwardLe8Rate)}");
                Console.WriteLine($"      avg_manhattan_distance={ModelMath.FormatDouble(stats.AverageManhattanDistance)} manhattan_le1={ModelMath.FormatPercent(stats.ManhattanLe1Rate)} manhattan_le2={ModelMath.FormatPercent(stats.ManhattanLe2Rate)} manhattan_le4={ModelMath.FormatPercent(stats.ManhattanLe4Rate)}");
            }

            if (options.CycleEntryStats && !summary.CycleEntryStats.IsEmpty)
            {
                DinosaurCycleEntryStats stats = summary.CycleEntryStats;
                Console.WriteLine("    cycle_entry_stats:");
                Console.WriteLine($"      avg_script_length={ModelMath.FormatDouble(stats.AverageScriptLength)} avg_grid_dinosaur={ModelMath.FormatDouble(stats.AverageGridDinosaurCount)} avg_remaining_apples={ModelMath.FormatDouble(stats.AverageRemainingApples)} samples={stats.Samples}");
                Console.WriteLine($"      avg_entry_moves={ModelMath.FormatDouble(stats.AverageMoves)} avg_entry_action_ticks={ModelMath.FormatDouble(stats.AverageActionTicks)} avg_entry_can_move_checks={ModelMath.FormatDouble(stats.AverageCanMoveChecks)} avg_entry_measure_checks={ModelMath.FormatDouble(stats.AverageMeasureChecks)}");
            }

            if (!string.IsNullOrWhiteSpace(summary.FirstFailureDetail))
            {
                Console.WriteLine($"    first_failure={summary.FirstFailureDetail}");
            }
        }
    }

    private static void RunCactus(ArgumentReader reader)
    {
        var options = new CactusOptions
        {
            Size = reader.GetInt("size", 32),
            Samples = reader.GetInt("samples", reader.GetInt("runs", 1_000)),
            Seed = reader.GetInt("seed", 20260625),
            ActionTick = reader.GetInt("action-tick", 200),
        };

        CactusSummary summary = CactusModel.Run(options);

        Console.WriteLine("Cactus row-then-column sort model");
        Console.WriteLine($"  size={options.Size} samples={options.Samples} seed={options.Seed}");
        Console.WriteLine("  values use randomCactus.Next(10); action_ticks count move()+swap(); measure count is reported separately.");
        Console.WriteLine($"  avg_row_moves={ModelMath.FormatDouble(summary.AverageRowMoves)} avg_row_swaps={ModelMath.FormatDouble(summary.AverageRowSwaps)} avg_row_measures={ModelMath.FormatDouble(summary.AverageRowMeasures)}");
        Console.WriteLine($"  avg_column_moves={ModelMath.FormatDouble(summary.AverageColumnMoves)} avg_column_swaps={ModelMath.FormatDouble(summary.AverageColumnSwaps)} avg_column_measures={ModelMath.FormatDouble(summary.AverageColumnMeasures)}");
        Console.WriteLine($"  avg_sort_actions={ModelMath.FormatDouble(summary.AverageSortActions)} avg_sort_action_ticks={ModelMath.FormatDouble(summary.AverageSortActions * options.ActionTick)} avg_measure_count={ModelMath.FormatDouble(summary.AverageMeasureCount)}");
        Console.WriteLine($"  avg_parallel_wall_actions_lower_bound={ModelMath.FormatDouble(summary.AverageWallActions)} avg_parallel_wall_ticks_lower_bound={ModelMath.FormatDouble(summary.AverageWallActions * options.ActionTick)} failures={summary.Failures}");
    }

    private static void RunCompanion(ArgumentReader reader)
    {
        int size = reader.GetInt("size", 5);
        GridPoint target = reader.GetPoint("target", new GridPoint(4, 3));
        HashSet<GridPoint> blocked = reader.GetPointSet("blocked", new HashSet<GridPoint> { new(4, 4) });
        HashSet<GridPoint>? support = reader.TryGetPointSet("support");

        var options = new CompanionOptions
        {
            Size = size,
            Samples = reader.GetInt("samples", reader.GetInt("runs", 100_000)),
            Seed = reader.GetInt("seed", 20260625),
            Crop = reader.GetString("crop", "grass").ToLowerInvariant(),
            AcceptEntity = reader.GetString("accept", "bush").ToLowerInvariant(),
            Target = target,
            Blocked = blocked,
            Support = support,
        };

        CompanionSummary summary = CompanionModel.Run(options);

        Console.WriteLine("Companion hit-rate model");
        Console.WriteLine($"  size={options.Size} samples={options.Samples} seed={options.Seed} crop={options.Crop} accept={options.AcceptEntity} target={options.Target}");
        Console.WriteLine($"  blocked={FormatPointSet(options.Blocked)} support_count={summary.SupportCount}");
        Console.WriteLine("  position distribution follows Growable.ChooseCompanion(): wrapped radius 3, excluding current tile; type excludes the current crop.");
        Console.WriteLine($"  success={summary.Success}/{summary.Samples} rate={ModelMath.FormatPercent(summary.SuccessRate)} avg_requests_per_success={ModelMath.FormatDouble(summary.AverageRequestsPerSuccess)} avg_failed_rerolls_before_success={ModelMath.FormatDouble(summary.AverageFailedRerollsBeforeSuccess)}");
        Console.WriteLine($"  type_match_rate={ModelMath.FormatPercent(summary.TypeMatchRate)} blocked_rate={ModelMath.FormatPercent(summary.BlockedRate)} unsupported_rate={ModelMath.FormatPercent(summary.UnsupportedRate)}");
        Console.WriteLine($"  type_counts={FormatTypeCounts(summary.TypeCounts)}");
    }

    private static string FormatTypeCounts(IReadOnlyDictionary<string, int> typeCounts)
    {
        return string.Join(", ", typeCounts.OrderBy(pair => pair.Key, StringComparer.Ordinal).Select(pair => $"{pair.Key}:{pair.Value}"));
    }

    private static string FormatPointSet(IReadOnlySet<GridPoint> points)
    {
        if (points.Count == 0)
        {
            return "-";
        }

        return string.Join(";", points.OrderBy(point => point.X).ThenBy(point => point.Y).Select(point => point.ToString()));
    }

    private static void PrintHelp()
    {
        Console.WriteLine("TFWR mechanism model");
        Console.WriteLine();
        Console.WriteLine("Usage:");
        Console.WriteLine("  dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- all");
        Console.WriteLine("  dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- dinosaur --size 32 --runs 50");
        Console.WriteLine("  dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- cactus --size 32 --samples 2000");
        Console.WriteLine("  dotnet run --project mechanism_model/TFWRMechanismModel.csproj -- companion --size 5 --crop grass --accept bush --target 4,3 --blocked 4,4");
        Console.WriteLine();
        Console.WriteLine("Common options:");
        Console.WriteLine("  --size <n>       world size");
        Console.WriteLine("  --runs <n>       alias used by dinosaur and companion; cactus also accepts it as samples");
        Console.WriteLine("  --samples <n>    cactus / companion sample count");
        Console.WriteLine("  --seed <n>       deterministic local random seed");
        Console.WriteLine("  --max-moves <n>  dinosaur safety cap");
        Console.WriteLine("  --policy <name>  run one dinosaur policy, e.g. lb-current-game");
        Console.WriteLine("  --chase-limit-num <n> --chase-limit-den <n>  current-script chase threshold fraction");
        Console.WriteLine("  --chase-late-abort-num <n> --chase-late-abort-den <n>  local probe: after this length, leave chase when the measured apple is gated out");
        Console.WriteLine("  --chase-late-abort-min-apple-x <n>  local probe: late-abort low-X apple threshold");
        Console.WriteLine("  --extra-chase-limit-num <n> --extra-chase-limit-den <n>  local probe: extend chase only for gated apples after base threshold");
        Console.WriteLine("  --extra-chase-min-apple-x <n>  local probe: minimum apple X for extended chase");
        Console.WriteLine("  --extra-chase-fill-step-num <n> --extra-chase-fill-step-den <n>  local probe: fill fraction used only during extended chase; -1 uses the base fill fraction");
        Console.WriteLine("  --fill-step-num <n> --fill-step-den <n>  current-script chase fill step fraction");
        Console.WriteLine("  --chase-skip-left-x <n>  local probe: skip chase_align when target apple X is below n");
        Console.WriteLine("  --chase-vertical-use-move-result  use move() return value for chase_align North/South probes before falling back West");
        Console.WriteLine("  --phase-stats   print current-script phase-level move / action summaries");
        Console.WriteLine("  --cycle-adjacent-max-skip <n>  allow adjacent apple Hamilton-forward shortcuts in cycle_finish");
        Console.WriteLine("  --cycle-greedy-shortcut-max-skip <n>  local probe: O(4) Hamilton-forward greedy shortcuts in cycle_finish");
        Console.WriteLine("  --recover-detour  try one Hamilton path move when recover_west/recover_south is blocked");
        Console.WriteLine("  --recover-detour-max-steps <n>  max Hamilton path detour moves while recover_west/recover_south is blocked");
        Console.WriteLine("  --recover-west-stop-x <n>  local probe: stop west recovery at column n before recovering south");
        Console.WriteLine("  --recover-bfs-to-origin  local upper-bound probe: try bounded BFS back to 0,0 before normal recovery");
        Console.WriteLine("  --recover-bfs-max-depth <n>  max BFS path depth for --recover-bfs-to-origin");
        Console.WriteLine("  --recover-bfs-max-nodes <n>  max BFS nodes for --recover-bfs-to-origin");
        Console.WriteLine("  --recover-south-edge-probe  local probe: when recover_south is blocked at x=0, try simple escape directions");
        Console.WriteLine("  --recover-south-edge-cycle  local probe: when recover_south is blocked at x=0, follow the Hamilton path back to x=0 before continuing south");
        Console.WriteLine("  --recover-south-sweep  local probe: when recover_south is blocked, sweep horizontally until south is available");
        Console.WriteLine("  --recover-use-move-result  use move() return value instead of can_move() precheck in recover_west/recover_south");
        Console.WriteLine("  --cycle-bfs-shortcut  local upper-bound probe for Hamilton-monotonic cycle_finish shortcuts");
        Console.WriteLine("  --cycle-use-move-result  use move() return value instead of can_move() precheck in fixed cycle_finish");
        Console.WriteLine("  --use-move-result  use move() return value instead of update_and_move/simple_update prechecks");
        Console.WriteLine("  --check-tick-cost <n> fold can_move()/measure() counts into a diagnostic tick budget");
        Console.WriteLine("  --cycle-wait-stats  print cycle_finish apple wait and local opportunity distribution");
        Console.WriteLine("  --cycle-entry-stats  print state and cost when lb-current-game enters cycle_finish");
        Console.WriteLine("  --include-heavy  include expensive local-only Dinosaur probes");
        Console.WriteLine();
        Console.WriteLine("Companion point-list syntax:");
        Console.WriteLine("  --target x,y");
        Console.WriteLine("  --blocked 'x,y;x,y'");
        Console.WriteLine("  --support 'x,y;x,y'");
    }
}

internal sealed class ArgumentReader
{
    private readonly Dictionary<string, string> values = new(StringComparer.OrdinalIgnoreCase);

    public ArgumentReader(IEnumerable<string> args)
    {
        string? pendingKey = null;
        foreach (string arg in args)
        {
            if (arg.StartsWith("--", StringComparison.Ordinal))
            {
                if (pendingKey is not null)
                {
                    values[pendingKey] = "true";
                    pendingKey = null;
                }

                string body = arg[2..];
                int equalIndex = body.IndexOf('=');
                if (equalIndex >= 0)
                {
                    values[body[..equalIndex]] = body[(equalIndex + 1)..];
                }
                else
                {
                    pendingKey = body;
                }
            }
            else if (pendingKey is not null)
            {
                values[pendingKey] = arg;
                pendingKey = null;
            }
            else
            {
                throw new ArgumentException($"Unexpected argument: {arg}");
            }
        }

        if (pendingKey is not null)
        {
            values[pendingKey] = "true";
        }
    }

    public int GetInt(string name, int defaultValue)
    {
        if (!values.TryGetValue(name, out string? value))
        {
            return defaultValue;
        }

        if (!int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out int parsed))
        {
            throw new ArgumentException($"Invalid integer for --{name}: {value}");
        }

        return parsed;
    }

    public string GetString(string name, string defaultValue)
    {
        return values.TryGetValue(name, out string? value) ? value : defaultValue;
    }

    public string? TryGetString(string name)
    {
        return values.TryGetValue(name, out string? value) ? value : null;
    }

    public bool GetBool(string name, bool defaultValue)
    {
        if (!values.TryGetValue(name, out string? value))
        {
            return defaultValue;
        }

        return value.Equals("true", StringComparison.OrdinalIgnoreCase) ||
               value.Equals("1", StringComparison.OrdinalIgnoreCase) ||
               value.Equals("yes", StringComparison.OrdinalIgnoreCase);
    }

    public GridPoint GetPoint(string name, GridPoint defaultValue)
    {
        return values.TryGetValue(name, out string? value) ? ParsePoint(value, name) : defaultValue;
    }

    public HashSet<GridPoint> GetPointSet(string name, HashSet<GridPoint> defaultValue)
    {
        return values.TryGetValue(name, out string? value) ? ParsePointSet(value, name) : defaultValue;
    }

    public HashSet<GridPoint>? TryGetPointSet(string name)
    {
        return values.TryGetValue(name, out string? value) ? ParsePointSet(value, name) : null;
    }

    private static HashSet<GridPoint> ParsePointSet(string value, string name)
    {
        var points = new HashSet<GridPoint>();
        if (string.IsNullOrWhiteSpace(value) || value == "-")
        {
            return points;
        }

        foreach (string part in value.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries))
        {
            points.Add(ParsePoint(part, name));
        }

        return points;
    }

    private static GridPoint ParsePoint(string value, string name)
    {
        string[] parts = value.Split(',', StringSplitOptions.TrimEntries);
        if (parts.Length != 2 ||
            !int.TryParse(parts[0], NumberStyles.Integer, CultureInfo.InvariantCulture, out int x) ||
            !int.TryParse(parts[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out int y))
        {
            throw new ArgumentException($"Invalid point for --{name}: {value}; expected x,y");
        }

        return new GridPoint(x, y);
    }
}
