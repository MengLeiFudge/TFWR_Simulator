using System.Collections.Generic;

namespace TFWRMechanismModel;

internal sealed record DinosaurOptions
{
    public int Size { get; init; } = 32;
    public int Runs { get; init; } = 50;
    public int Seed { get; init; } = 20260625;
    public int MaxMoves { get; init; } = 2_000_000;
    public int InitialMoveTicks { get; init; } = 400;
    public bool IncludeHeavy { get; init; }
    public string? PolicyFilter { get; init; }
    public int ChaseLimitNumerator { get; init; } = 9;
    public int ChaseLimitDenominator { get; init; } = 25;
    public int ChaseLateAbortNumerator { get; init; }
    public int ChaseLateAbortDenominator { get; init; } = 1;
    public int ChaseLateAbortMinAppleX { get; init; }
    public int ExtraChaseLimitNumerator { get; init; }
    public int ExtraChaseLimitDenominator { get; init; } = 1;
    public int ExtraChaseMinAppleX { get; init; }
    public int ExtraChaseFillStepNumerator { get; init; } = -1;
    public int ExtraChaseFillStepDenominator { get; init; } = 1;
    public int FillStepNumerator { get; init; } = 15;
    public int FillStepDenominator { get; init; } = 16;
    public bool PhaseStats { get; init; }
    public int CycleAdjacentMaxSkip { get; init; }
    public int CycleGreedyShortcutMaxSkip { get; init; }
    public int RecoverDetourMaxSteps { get; init; } = 1024;
    public bool CycleBfsShortcut { get; init; }
    public int CheckTickCost { get; init; }
    public bool CycleUseMoveResult { get; init; }
    public bool UseMoveResult { get; init; } = true;
    public bool CycleWaitStats { get; init; }
    public bool RecoverSouthEdgeProbe { get; init; }
    public bool RecoverSouthEdgeCycle { get; init; }
    public bool RecoverSouthSweep { get; init; }
    public bool RecoverUseMoveResult { get; init; }
    public bool CycleEntryStats { get; init; }
    public int ChaseSkipLeftX { get; init; }
    public int RecoverWestStopX { get; init; }
    public bool RecoverBfsToOrigin { get; init; }
    public int RecoverBfsMaxDepth { get; init; } = 64;
    public int RecoverBfsMaxNodes { get; init; } = 1024;
    public bool ChaseVerticalUseMoveResult { get; init; }
}

internal sealed class DinosaurModel
{
    private static readonly Direction[] ShortcutDirections =
    [
        Direction.North,
        Direction.East,
        Direction.South,
        Direction.West,
    ];

    public static IReadOnlyList<DinosaurAggregate> Run(DinosaurOptions options)
    {
        ValidateOptions(options);

        HamiltonCycle cycle = HamiltonCycle.Build(options.Size);
        var results = new List<DinosaurAggregate>();
        AddPolicy(results, "lb-current-game", options, cycle, DinosaurPolicy.LbCurrentGame);
        AddPolicy(results, "cycle", options, cycle, DinosaurPolicy.Cycle);
        AddPolicy(results, "gif-safe-chase", options, cycle, DinosaurPolicy.GifSafeChase);
        AddPolicy(results, "gif-bfs-safe-chase", options, cycle, DinosaurPolicy.GifBfsSafeChase);

        if (options.IncludeHeavy)
        {
            AddPolicy(results, "gif-virtual-safe-chase", options, cycle, DinosaurPolicy.GifVirtualSafeChase);
        }

        AddPolicy(results, "hamilton-shortcut-probe", options, cycle, DinosaurPolicy.HamiltonShortcutProbe);
        return results;
    }

    private static void AddPolicy(
        List<DinosaurAggregate> results,
        string name,
        DinosaurOptions options,
        HamiltonCycle cycle,
        DinosaurPolicy policy)
    {
        if (options.PolicyFilter is not null &&
            !string.Equals(options.PolicyFilter, name, StringComparison.OrdinalIgnoreCase))
        {
            return;
        }

        results.Add(RunPolicy(name, options, cycle, policy));
    }

    private static DinosaurAggregate RunPolicy(string name, DinosaurOptions options, HamiltonCycle cycle, DinosaurPolicy policy)
    {
        var random = new Random(options.Seed);
        var aggregate = new DinosaurAggregate(name, options.Runs);

        for (int run = 0; run < options.Runs; run++)
        {
            DinosaurTrialResult result = RunOne(options, cycle, random, policy);
            aggregate.Add(result);
        }

        return aggregate;
    }

    private static DinosaurTrialResult RunOne(DinosaurOptions options, HamiltonCycle cycle, Random random, DinosaurPolicy policy)
    {
        if (policy == DinosaurPolicy.LbCurrentGame)
        {
            return RunCurrentScript(options, cycle, random);
        }

        int targetLength = options.Size * options.Size - 2;
        int moveTicks = options.InitialMoveTicks;
        long actionTicks = 0;
        int moves = 0;
        int apples = 0;
        int shortcuts = 0;

        var body = new LinkedList<GridPoint>();
        var occupied = new HashSet<GridPoint>();
        var head = new GridPoint(0, 0);
        body.AddFirst(head);
        occupied.Add(head);

        GridPoint apple = ChooseApple(options.Size, occupied, random);
        Queue<Direction>? pendingShortcut = null;

        while (body.Count < targetLength && moves < options.MaxMoves)
        {
            Direction direction;
            if (policy == DinosaurPolicy.Cycle)
            {
                direction = cycle.NextDirection(head);
            }
            else if (policy == DinosaurPolicy.GifSafeChase)
            {
                direction = ChooseGifSafeChaseDirection(cycle, head, apple, body, occupied);
                if (direction != cycle.NextDirection(head))
                {
                    shortcuts++;
                }
            }
            else if (policy == DinosaurPolicy.GifBfsSafeChase)
            {
                if (pendingShortcut is null || pendingShortcut.Count == 0)
                {
                    pendingShortcut = TryBuildMonotonicShortcut(cycle, head, apple, body, occupied);
                    if (pendingShortcut is { Count: > 0 })
                    {
                        shortcuts++;
                    }
                }

                direction = pendingShortcut is { Count: > 0 }
                    ? pendingShortcut.Dequeue()
                    : cycle.NextDirection(head);
            }
            else if (policy == DinosaurPolicy.GifVirtualSafeChase)
            {
                if (pendingShortcut is null || pendingShortcut.Count == 0)
                {
                    pendingShortcut = TryBuildVirtualSafeApplePath(options.Size, body, occupied, apple);
                    if (pendingShortcut is { Count: > 0 })
                    {
                        shortcuts++;
                    }
                }

                direction = pendingShortcut is { Count: > 0 }
                    ? pendingShortcut.Dequeue()
                    : cycle.NextDirection(head);
            }
            else if (policy == DinosaurPolicy.HamiltonShortcutProbe)
            {
                if (pendingShortcut is null || pendingShortcut.Count == 0)
                {
                    pendingShortcut = TryBuildShortcut(cycle, head, apple, body.Count, occupied);
                    if (pendingShortcut is { Count: > 0 })
                    {
                        shortcuts++;
                    }
                }

                direction = pendingShortcut is { Count: > 0 }
                    ? pendingShortcut.Dequeue()
                    : cycle.NextDirection(head);
            }
            else
            {
                throw new ArgumentOutOfRangeException(nameof(policy), policy, null);
            }

            GridPoint next = head.Move(direction);
            if (!Inside(next, options.Size))
            {
                return DinosaurTrialResult.Wall(moves, actionTicks, apples, body.Count, shortcuts);
            }

            bool grow = next == apple;
            if (!grow)
            {
                GridPoint tail = body.Last!.Value;
                body.RemoveLast();
                occupied.Remove(tail);
            }

            if (occupied.Contains(next))
            {
                return DinosaurTrialResult.Collision(moves, actionTicks, apples, body.Count, shortcuts);
            }

            moves++;
            actionTicks += moveTicks;
            body.AddFirst(next);
            occupied.Add(next);
            head = next;

            if (grow)
            {
                apples++;
                moveTicks -= (int)Math.Floor(moveTicks * 0.03);
                pendingShortcut = null;

                if (body.Count >= targetLength || occupied.Count >= options.Size * options.Size)
                {
                    break;
                }

                apple = ChooseApple(options.Size, occupied, random);
            }
        }

        if (body.Count >= targetLength)
        {
            return DinosaurTrialResult.Completed(moves, actionTicks, apples, body.Count, shortcuts);
        }

        return DinosaurTrialResult.MoveLimit(moves, actionTicks, apples, body.Count, shortcuts);
    }

    private static DinosaurTrialResult RunCurrentScript(DinosaurOptions options, HamiltonCycle cycle, Random random)
    {
        int size = options.Size;
        int targetDinosaurCount = size * size - 1;
        int maxTailLength = size * size - 2;
        int moveTicks = options.InitialMoveTicks;
        long actionTicks = 0;
        int moves = 0;
        int apples = 0;
        int shortcuts = 0;
        long canMoveChecks = 0;
        long measureChecks = 1;
        int scriptLength = 1;
        int step = 0;
        string phase = "init";
        string? cycleFinishBlockedDetail = null;
        Queue<Direction>? pendingCycleShortcut = null;
        DinosaurCycleWaitStats cycleWaitStats = new();
        DinosaurCycleEntryStats? cycleEntryStats = null;
        var phaseStats = options.PhaseStats
            ? new Dictionary<string, DinosaurPhaseStats>(StringComparer.Ordinal)
            : null;

        var head = new GridPoint(0, 0);
        var tail = new LinkedList<DinosaurTailSegment>();
        var dinosaurs = new Dictionary<GridPoint, DinosaurTailSegment>();
        GridPoint? targetApple = head;
        GridPoint? targetNext = ChooseGameApple(size, dinosaurs, currentApple: targetApple, random);
        GridPoint? measuredApple = targetNext;

        string StateDetail(Direction direction)
        {
            return $"{phase} dir={direction.ShortName()} head={head} apple={measuredApple?.ToString() ?? "-"} " +
                   $"target={targetApple?.ToString() ?? "-"} next={targetNext?.ToString() ?? "-"} " +
                   $"tail={tail.Count} grid_dino={dinosaurs.Count} script_length={scriptLength} step={step} moves={moves} " +
                   $"can=N:{CanMove(Direction.North)} E:{CanMove(Direction.East)} S:{CanMove(Direction.South)} W:{CanMove(Direction.West)} " +
                   $"path={cycle.NextDirection(head).ShortName()}";
        }

        DinosaurTrialResult WithScriptStats(DinosaurTrialResult result)
        {
            return result with
            {
                CanMoveChecks = canMoveChecks,
                MeasureChecks = measureChecks,
                CycleWaitStats = cycleWaitStats.IsEmpty ? null : cycleWaitStats,
                CycleEntryStats = cycleEntryStats,
            };
        }

        DinosaurTrialResult? MoveBlocked(Direction direction)
        {
            GridPoint next = head.Move(direction);
            return Inside(next, size)
                ? WithScriptStats(DinosaurTrialResult.Collision(moves, actionTicks, apples, dinosaurs.Count, shortcuts, StateDetail(direction)))
                : WithScriptStats(DinosaurTrialResult.Wall(moves, actionTicks, apples, dinosaurs.Count, shortcuts, StateDetail(direction)));
        }

        bool CanMove(Direction direction)
        {
            GridPoint next = head.Move(direction);
            if (!Inside(next, size))
            {
                return false;
            }

            return !dinosaurs.TryGetValue(next, out DinosaurTailSegment? dinosaur) || dinosaur.CanMoveTo;
        }

        bool ScriptCanMove(Direction direction)
        {
            canMoveChecks++;
            return CanMove(direction);
        }

        bool SpawnNextAppleFrom(GridPoint oldApple)
        {
            if (targetNext is null)
            {
                targetApple = null;
                return false;
            }

            if (tail.Count >= maxTailLength ||
                dinosaurs.ContainsKey(targetNext.Value))
            {
                targetApple = null;
                targetNext = null;
                return false;
            }

            targetApple = targetNext.Value;
            targetNext = ChooseGameApple(size, dinosaurs, currentApple: targetApple, random);
            return true;
        }

        DinosaurTrialResult? UpdateAndMove(Direction direction)
        {
            if (moves >= options.MaxMoves)
            {
                return WithScriptStats(DinosaurTrialResult.MoveLimit(moves, actionTicks, apples, dinosaurs.Count, shortcuts, StateDetail(direction), PhaseStatsSnapshot()));
            }

            bool canMove = options.UseMoveResult ? CanMove(direction) : ScriptCanMove(direction);
            if (!canMove)
            {
                if (options.UseMoveResult)
                {
                    actionTicks++;
                }

                return MoveBlocked(direction);
            }

            return MoveAfterCanMove(direction, updateScriptMeasure: true, incrementScriptStep: true);
        }

        DinosaurTrialResult? TryUpdateAndMove(Direction direction, out bool moved)
        {
            moved = false;
            if (moves >= options.MaxMoves)
            {
                return WithScriptStats(DinosaurTrialResult.MoveLimit(moves, actionTicks, apples, dinosaurs.Count, shortcuts, StateDetail(direction), PhaseStatsSnapshot()));
            }

            if (!CanMove(direction))
            {
                actionTicks++;
                return null;
            }

            moved = true;
            return MoveAfterCanMove(direction, updateScriptMeasure: true, incrementScriptStep: true);
        }

        DinosaurTrialResult? TryChaseVerticalOrWest(Direction verticalDirection)
        {
            if (!options.ChaseVerticalUseMoveResult)
            {
                bool canMove = ScriptCanMove(verticalDirection);
                phase = verticalDirection == Direction.North
                    ? (canMove ? "chase_north_to_apple_y" : "chase_west_after_north_block")
                    : (canMove ? "chase_south_to_apple_y" : "chase_west_after_south_block");
                return UpdateAndMove(canMove ? verticalDirection : Direction.West);
            }

            phase = verticalDirection == Direction.North
                ? "chase_north_to_apple_y"
                : "chase_south_to_apple_y";
            DinosaurTrialResult? attempted = TryUpdateAndMove(verticalDirection, out bool moved);
            if (attempted is not null)
            {
                return attempted.Value;
            }

            if (moved)
            {
                return null;
            }

            phase = verticalDirection == Direction.North
                ? "chase_west_after_north_block"
                : "chase_west_after_south_block";
            return UpdateAndMove(Direction.West);
        }

        DinosaurTrialResult? SimpleUpdateAndMove(Direction direction, bool updateScriptMeasure, out bool moved)
        {
            moved = false;
            if (moves >= options.MaxMoves)
            {
                return WithScriptStats(DinosaurTrialResult.MoveLimit(moves, actionTicks, apples, dinosaurs.Count, shortcuts, StateDetail(direction), PhaseStatsSnapshot()));
            }

            bool canMove = (options.UseMoveResult || options.CycleUseMoveResult) ? CanMove(direction) : ScriptCanMove(direction);
            if (!canMove)
            {
                if (options.UseMoveResult || options.CycleUseMoveResult)
                {
                    actionTicks++;
                }

                cycleFinishBlockedDetail = StateDetail(direction);
                return null;
            }

            moved = true;
            return MoveAfterCanMove(direction, updateScriptMeasure, incrementScriptStep: false);
        }

        DinosaurTrialResult? MoveAfterCanMove(Direction direction, bool updateScriptMeasure, bool incrementScriptStep)
        {
            string movePhase = phase;
            GridPoint old = head;
            GridPoint next = head.Move(direction);
            bool ateApple = targetApple is not null && targetApple.Value == old;
            if (ateApple)
            {
                apples++;
                if (SpawnNextAppleFrom(old))
                {
                    moveTicks -= (int)Math.Floor(moveTicks * 0.03);
                }
            }

            if (ateApple || tail.Count > 0)
            {
                var newSegment = new DinosaurTailSegment(old);
                tail.AddFirst(newSegment);
                dinosaurs[old] = newSegment;

                if (!ateApple)
                {
                    LinkedListNode<DinosaurTailSegment>? last = tail.Last;
                    if (last is not null)
                    {
                        dinosaurs.Remove(last.Value.Position);
                        tail.RemoveLast();
                    }
                }

                if (tail.Count < maxTailLength &&
                    tail.Count > 1 &&
                    targetApple is not null &&
                    next != targetApple.Value &&
                    tail.Last is not null)
                {
                    tail.Last.Value.CanMoveTo = true;
                }
            }

            while (targetApple is not null &&
                   targetNext is not null &&
                   targetNext.Value == old &&
                   tail.Count < maxTailLength)
            {
                targetNext = ChooseGameApple(size, dinosaurs, currentApple: targetApple, random);
            }

            moves++;
            actionTicks += moveTicks;
            RecordPhase(movePhase, moveTicks, ateApple ? 1 : 0);
            head = next;
            if (incrementScriptStep)
            {
                step++;
            }

            if (updateScriptMeasure &&
                measuredApple is not null &&
                head == measuredApple.Value)
            {
                measureChecks++;
                if (targetApple is not null &&
                    targetApple.Value == head &&
                    targetNext is not null)
                {
                    measuredApple = targetNext.Value;
                    scriptLength++;
                }
            }

            return null;
        }

        Direction? TryChooseCycleAdjacentShortcut()
        {
            if (options.CycleAdjacentMaxSkip <= 0 || measuredApple is null)
            {
                return null;
            }

            Direction pathDirection = cycle.NextDirection(head);
            foreach (Direction direction in ShortcutDirections)
            {
                if (direction == pathDirection)
                {
                    continue;
                }

                GridPoint next = head.Move(direction);
                if (next != measuredApple.Value)
                {
                    continue;
                }

                int forwardDistance = cycle.ForwardDistance(head, next);
                if (forwardDistance <= 1 || forwardDistance > options.CycleAdjacentMaxSkip)
                {
                    continue;
                }

                if (!ScriptCanMove(direction))
                {
                    continue;
                }

                return direction;
            }

            return null;
        }

        Direction? TryChooseCycleGreedyShortcut()
        {
            if (options.CycleGreedyShortcutMaxSkip <= 0 || measuredApple is null)
            {
                return null;
            }

            Direction pathDirection = cycle.NextDirection(head);
            int targetDistance = cycle.ForwardDistance(head, measuredApple.Value);
            int safeDistance = size * size - scriptLength;
            if (targetDistance <= 1 || targetDistance >= safeDistance)
            {
                return null;
            }

            Direction? bestDirection = null;
            int bestManhattan = head.ManhattanTo(measuredApple.Value);
            int bestForward = 1;
            foreach (Direction direction in ShortcutDirections)
            {
                if (direction == pathDirection)
                {
                    continue;
                }

                GridPoint next = head.Move(direction);
                if (!Inside(next, size))
                {
                    continue;
                }

                int forwardDistance = cycle.ForwardDistance(head, next);
                if (forwardDistance <= 1 ||
                    forwardDistance > options.CycleGreedyShortcutMaxSkip ||
                    forwardDistance > targetDistance ||
                    forwardDistance >= safeDistance)
                {
                    continue;
                }

                int manhattan = next.ManhattanTo(measuredApple.Value);
                if (manhattan > bestManhattan)
                {
                    continue;
                }

                if (!ScriptCanMove(direction))
                {
                    continue;
                }

                if (manhattan < bestManhattan || forwardDistance > bestForward)
                {
                    bestDirection = direction;
                    bestManhattan = manhattan;
                    bestForward = forwardDistance;
                }
            }

            return bestDirection;
        }

        Direction? TryChooseCycleBfsShortcut()
        {
            if (!options.CycleBfsShortcut || measuredApple is null)
            {
                return null;
            }

            if (pendingCycleShortcut is null || pendingCycleShortcut.Count == 0)
            {
                pendingCycleShortcut = TryBuildShortcut(cycle, head, measuredApple.Value, scriptLength, new HashSet<GridPoint>(dinosaurs.Keys));
                if (pendingCycleShortcut is { Count: > 0 })
                {
                    shortcuts++;
                }
            }

            return pendingCycleShortcut is { Count: > 0 }
                ? pendingCycleShortcut.Dequeue()
                : null;
        }

        void RecordPhase(string movePhase, int ticks, int appleDelta)
        {
            if (phaseStats is null)
            {
                return;
            }

            phaseStats.TryGetValue(movePhase, out DinosaurPhaseStats current);
            phaseStats[movePhase] = current.Add(new DinosaurPhaseStats(1, ticks, appleDelta));
        }

        IReadOnlyDictionary<string, DinosaurPhaseStats>? PhaseStatsSnapshot()
        {
            return phaseStats is null
                ? null
                : new Dictionary<string, DinosaurPhaseStats>(phaseStats, StringComparer.Ordinal);
        }

        bool IsBelowScriptLengthLimit(int numerator, int denominator)
        {
            return scriptLength * denominator < size * size * numerator;
        }

        bool IsBaseChase()
        {
            return IsBelowScriptLengthLimit(options.ChaseLimitNumerator, options.ChaseLimitDenominator);
        }

        bool ShouldContinueChase()
        {
            if (IsBaseChase())
            {
                if (options.ChaseLateAbortNumerator > 0 &&
                    !IsBelowScriptLengthLimit(options.ChaseLateAbortNumerator, options.ChaseLateAbortDenominator) &&
                    measuredApple is not null &&
                    (measuredApple.Value.Y == 0 || measuredApple.Value.X < options.ChaseLateAbortMinAppleX))
                {
                    return false;
                }

                return true;
            }

            if (options.ExtraChaseLimitNumerator <= 0 ||
                !IsBelowScriptLengthLimit(options.ExtraChaseLimitNumerator, options.ExtraChaseLimitDenominator) ||
                measuredApple is null)
            {
                return false;
            }

            // 延长追踪只吃更容易恢复形状的候选，避免重复踩历史低 X / 底边负例。
            return measuredApple.Value.Y > 0 &&
                   measuredApple.Value.X >= options.ExtraChaseMinAppleX;
        }

        while (ShouldContinueChase())
        {
            if (measuredApple is null)
            {
                return WithScriptStats(DinosaurTrialResult.MoveLimit(moves, actionTicks, apples, dinosaurs.Count, shortcuts, "measured apple unavailable", PhaseStatsSnapshot()));
            }

            phase = "chase_fill";
            step = 0;
            bool baseChase = IsBaseChase();
            int fillStepNumerator = baseChase || options.ExtraChaseFillStepNumerator < 0
                ? options.FillStepNumerator
                : options.ExtraChaseFillStepNumerator;
            int fillStepDenominator = baseChase || options.ExtraChaseFillStepNumerator < 0
                ? options.FillStepDenominator
                : options.ExtraChaseFillStepDenominator;
            while (step < scriptLength * fillStepNumerator / fillStepDenominator)
            {
                DinosaurTrialResult? result = UpdateAndMove(cycle.NextDirection(head));
                if (result is not null)
                {
                    return result.Value;
                }
            }

            phase = "chase_east_to_apple_x";
            while (head.X < measuredApple.Value.X)
            {
                DinosaurTrialResult? result = UpdateAndMove(Direction.East);
                if (result is not null)
                {
                    return result.Value;
                }
            }

            phase = "chase_leave_bottom";
            while (head.Y == 0)
            {
                Direction direction = head.X % 2 == 0 ? Direction.East : Direction.North;
                DinosaurTrialResult? result = UpdateAndMove(direction);
                if (result is not null)
                {
                    return result.Value;
                }
            }

            phase = "chase_align_to_apple";
            while (measuredApple is not null && head.X >= measuredApple.Value.X)
            {
                int targetX = measuredApple.Value.X;
                int targetY = measuredApple.Value.Y;
                if (targetY == 0 ||
                    (options.ChaseSkipLeftX > 0 && targetX < options.ChaseSkipLeftX))
                {
                    break;
                }

                while (head.Y < targetY)
                {
                    DinosaurTrialResult? result = TryChaseVerticalOrWest(Direction.North);
                    if (result is not null)
                    {
                        return result.Value;
                    }

                    if (head.X == 0)
                    {
                        break;
                    }
                }

                if (head.X == 0)
                {
                    break;
                }

                while (head.Y > targetY)
                {
                    DinosaurTrialResult? result = TryChaseVerticalOrWest(Direction.South);
                    if (result is not null)
                    {
                        return result.Value;
                    }

                    if (head.X == 0)
                    {
                        break;
                    }
                }

                if (head.X == 0)
                {
                    break;
                }

                phase = "chase_west_to_apple_x";
                while (head.X > targetX)
                {
                    DinosaurTrialResult? result = UpdateAndMove(Direction.West);
                    if (result is not null)
                    {
                        return result.Value;
                    }

                    if (head.X == 0)
                    {
                        break;
                    }
                }

                if (head.X == 0)
                {
                    break;
                }
            }

            phase = "recover_west";
            if (options.RecoverBfsToOrigin)
            {
                Queue<Direction>? recoverPath = TryBuildRecoverPathToOrigin();
                if (recoverPath is { Count: > 0 })
                {
                    phase = "recover_bfs_to_origin";
                    shortcuts++;
                    while (recoverPath.Count > 0)
                    {
                        DinosaurTrialResult? result = UpdateAndMove(recoverPath.Dequeue());
                        if (result is not null)
                        {
                            return result.Value;
                        }
                    }
                }
            }

            int recoverWestDetours = 0;
            while (head.X > options.RecoverWestStopX)
            {
                Direction direction = Direction.West;
                if (options.RecoverDetourMaxSteps > 0)
                {
                    if (options.RecoverUseMoveResult)
                    {
                        DinosaurTrialResult? attempted = TryUpdateAndMove(direction, out bool moved);
                        if (attempted is not null)
                        {
                            return attempted.Value;
                        }

                        if (moved)
                        {
                            recoverWestDetours = 0;
                            continue;
                        }
                    }
                    else if (ScriptCanMove(direction))
                    {
                        recoverWestDetours = 0;
                    }
                    else if (recoverWestDetours < options.RecoverDetourMaxSteps)
                    {
                        Direction detour = cycle.NextDirection(head);
                        if (detour != direction)
                        {
                            direction = detour;
                            shortcuts++;
                            recoverWestDetours++;
                        }
                    }
                }

                DinosaurTrialResult? result = UpdateAndMove(direction);
                if (result is not null)
                {
                    return result.Value;
                }
            }

            phase = "recover_south";
            int recoverSouthDetours = 0;
            bool recoverSouthEdgeCycle = false;
            Direction recoverSouthSweepDirection = Direction.East;
            while (head.Y > 0)
            {
                Direction direction = Direction.South;
                if (options.RecoverDetourMaxSteps > 0)
                {
                    if (recoverSouthEdgeCycle)
                    {
                        direction = cycle.NextDirection(head);
                        shortcuts++;
                        if (head.X == 0 && direction == Direction.South)
                        {
                            recoverSouthEdgeCycle = false;
                            recoverSouthDetours = 0;
                        }
                    }
                    else if (options.RecoverUseMoveResult)
                    {
                        DinosaurTrialResult? attempted = TryUpdateAndMove(direction, out bool moved);
                        if (attempted is not null)
                        {
                            return attempted.Value;
                        }

                        if (moved)
                        {
                            recoverSouthDetours = 0;
                            continue;
                        }
                    }
                    else if (ScriptCanMove(direction))
                    {
                        recoverSouthDetours = 0;
                    }
                    else if (options.RecoverSouthEdgeCycle &&
                             head.X == 0 &&
                             CanMove(Direction.East))
                    {
                        direction = Direction.East;
                        shortcuts++;
                        recoverSouthDetours = 0;
                        recoverSouthEdgeCycle = true;
                    }
                    else if (options.RecoverSouthSweep &&
                             TryChooseRecoverSouthSweepDirection(ref recoverSouthSweepDirection) is Direction sweepDirection)
                    {
                        direction = sweepDirection;
                        shortcuts++;
                        recoverSouthDetours = 0;
                    }
                    else if (options.RecoverSouthEdgeProbe &&
                             head.X == 0 &&
                             TryChooseRecoverSouthEdgeDirection() is Direction edgeDirection)
                    {
                        direction = edgeDirection;
                        shortcuts++;
                        recoverSouthDetours = 0;
                    }
                    else if (recoverSouthDetours < options.RecoverDetourMaxSteps)
                    {
                        Direction detour = cycle.NextDirection(head);
                        if (detour != direction)
                        {
                            direction = detour;
                            shortcuts++;
                            recoverSouthDetours++;
                        }
                    }
                }

                DinosaurTrialResult? result = UpdateAndMove(direction);
                if (result is not null)
                {
                    return result.Value;
                }
            }
        }

        phase = "cycle_finish";
        if (options.CycleEntryStats)
        {
            cycleEntryStats = new DinosaurCycleEntryStats(
                ScriptLength: scriptLength,
                GridDinosaurCount: dinosaurs.Count,
                RemainingApples: targetDinosaurCount - dinosaurs.Count,
                Moves: moves,
                ActionTicks: actionTicks,
                CanMoveChecks: canMoveChecks,
                MeasureChecks: measureChecks);
        }

        bool updateCycleMeasure = options.CycleBfsShortcut ||
                                  options.CycleAdjacentMaxSkip > 0 ||
                                  options.CycleGreedyShortcutMaxSkip > 0;
        int cycleMovesSinceApple = 0;
        while (moves < options.MaxMoves && dinosaurs.Count < targetDinosaurCount)
        {
            GridPoint? cycleTargetApple = targetApple;
            if (options.CycleWaitStats && cycleTargetApple is not null)
            {
                cycleWaitStats = cycleWaitStats.RecordOpportunity(
                    cycle.ForwardDistance(head, cycleTargetApple.Value),
                    head.ManhattanTo(cycleTargetApple.Value));
            }

            Direction direction = TryChooseCycleBfsShortcut() ??
                                  TryChooseCycleGreedyShortcut() ??
                                  TryChooseCycleAdjacentShortcut() ??
                                  cycle.NextDirection(head);
            if (direction != cycle.NextDirection(head))
            {
                shortcuts++;
            }

            DinosaurTrialResult? result = SimpleUpdateAndMove(direction, updateCycleMeasure, out bool moved);
            if (result is not null)
            {
                return result.Value;
            }

            if (!moved)
            {
                break;
            }

            cycleMovesSinceApple++;
            if (cycleTargetApple is not null && head == cycleTargetApple.Value)
            {
                cycleWaitStats = cycleWaitStats.RecordAppleWait(cycleMovesSinceApple);
                cycleMovesSinceApple = 0;
            }
        }

        if (dinosaurs.Count >= targetDinosaurCount)
        {
            return WithScriptStats(DinosaurTrialResult.Completed(moves, actionTicks, apples, dinosaurs.Count, shortcuts, PhaseStatsSnapshot()));
        }

        return moves >= options.MaxMoves
            ? WithScriptStats(DinosaurTrialResult.MoveLimit(moves, actionTicks, apples, dinosaurs.Count, shortcuts, "cycle_finish move limit", PhaseStatsSnapshot()))
            : WithScriptStats(DinosaurTrialResult.Collision(moves, actionTicks, apples, dinosaurs.Count, shortcuts, cycleFinishBlockedDetail ?? "cycle_finish blocked", PhaseStatsSnapshot()));

        Direction? TryChooseRecoverSouthEdgeDirection()
        {
            foreach (Direction candidate in new[] { Direction.East, Direction.North })
            {
                if (CanMove(candidate))
                {
                    return candidate;
                }
            }

            return null;
        }

        Direction? TryChooseRecoverSouthSweepDirection(ref Direction lateralDirection)
        {
            Direction opposite = lateralDirection == Direction.East ? Direction.West : Direction.East;
            if (ScriptCanMove(lateralDirection))
            {
                return lateralDirection;
            }

            if (ScriptCanMove(opposite))
            {
                lateralDirection = opposite;
                return opposite;
            }

            if (ScriptCanMove(Direction.North))
            {
                return Direction.North;
            }

            return null;
        }

        Queue<Direction>? TryBuildRecoverPathToOrigin()
        {
            var origin = new GridPoint(0, 0);
            if (head == origin)
            {
                return null;
            }

            bool CanRecoverEnter(GridPoint point)
            {
                return !dinosaurs.TryGetValue(point, out DinosaurTailSegment? dinosaur) || dinosaur.CanMoveTo;
            }

            List<Direction>? path = FindPathWithPassability(
                size,
                head,
                origin,
                point => point == origin || CanRecoverEnter(point),
                options.RecoverBfsMaxDepth,
                options.RecoverBfsMaxNodes);
            if (path is not { Count: > 0 } || path[^1] != Direction.South)
            {
                return null;
            }

            if (!IsRecoverPathCycleReady(path))
            {
                return null;
            }

            return new Queue<Direction>(path);
        }

        bool IsRecoverPathCycleReady(IReadOnlyList<Direction> path)
        {
            GridPoint virtualHead = head;
            var virtualTail = new LinkedList<DinosaurTailSegment>(
                tail.Select(segment => new DinosaurTailSegment(segment.Position)
                {
                    CanMoveTo = segment.CanMoveTo,
                }));
            var virtualDinosaurs = new Dictionary<GridPoint, DinosaurTailSegment>();
            foreach (DinosaurTailSegment segment in virtualTail)
            {
                virtualDinosaurs[segment.Position] = segment;
            }

            GridPoint? virtualTargetApple = targetApple;
            GridPoint? virtualTargetNext = targetNext;

            bool VirtualCanMove(Direction direction)
            {
                GridPoint next = virtualHead.Move(direction);
                return Inside(next, size) &&
                       (!virtualDinosaurs.TryGetValue(next, out DinosaurTailSegment? dinosaur) || dinosaur.CanMoveTo);
            }

            foreach (Direction direction in path)
            {
                if (!VirtualCanMove(direction))
                {
                    return false;
                }

                GridPoint old = virtualHead;
                GridPoint next = virtualHead.Move(direction);
                bool ateApple = virtualTargetApple is not null && virtualTargetApple.Value == old;

                if (ateApple)
                {
                    virtualTargetApple = virtualTargetNext;
                    virtualTargetNext = null;
                }

                if (ateApple || virtualTail.Count > 0)
                {
                    var newSegment = new DinosaurTailSegment(old);
                    virtualTail.AddFirst(newSegment);
                    virtualDinosaurs[old] = newSegment;

                    if (!ateApple)
                    {
                        LinkedListNode<DinosaurTailSegment>? last = virtualTail.Last;
                        if (last is not null)
                        {
                            virtualDinosaurs.Remove(last.Value.Position);
                            virtualTail.RemoveLast();
                        }
                    }

                    if (virtualTail.Count < maxTailLength &&
                        virtualTail.Count > 1 &&
                        virtualTargetApple is not null &&
                        next != virtualTargetApple.Value &&
                        virtualTail.Last is not null)
                    {
                        virtualTail.Last.Value.CanMoveTo = true;
                    }
                }

                virtualHead = next;
            }

            return virtualHead == new GridPoint(0, 0) &&
                   Inside(virtualHead.Move(cycle.NextDirection(virtualHead)), size) &&
                   VirtualCanMove(cycle.NextDirection(virtualHead));
        }
    }

    private static Queue<Direction>? TryBuildVirtualSafeApplePath(
        int size,
        LinkedList<GridPoint> body,
        HashSet<GridPoint> occupied,
        GridPoint apple)
    {
        List<Direction>? path = FindPath(size, body.First!.Value, apple, occupied, allowedOccupiedTarget: null, blockedPoint: null);
        if (path is null || path.Count == 0)
        {
            return null;
        }

        if (!IsApplePathSafeAfterVirtualRun(size, body, occupied, apple, path))
        {
            return null;
        }

        return new Queue<Direction>(path);
    }

    private static bool IsApplePathSafeAfterVirtualRun(
        int size,
        LinkedList<GridPoint> body,
        HashSet<GridPoint> occupied,
        GridPoint apple,
        IReadOnlyList<Direction> path)
    {
        var virtualBody = new LinkedList<GridPoint>(body);
        var virtualOccupied = new HashSet<GridPoint>(occupied);
        GridPoint head = virtualBody.First!.Value;

        foreach (Direction direction in path)
        {
            GridPoint next = head.Move(direction);
            if (!Inside(next, size))
            {
                return false;
            }

            bool grow = next == apple;
            if (!grow)
            {
                GridPoint tail = virtualBody.Last!.Value;
                virtualBody.RemoveLast();
                virtualOccupied.Remove(tail);
            }

            if (virtualOccupied.Contains(next))
            {
                return false;
            }

            virtualBody.AddFirst(next);
            virtualOccupied.Add(next);
            head = next;
        }

        if (head != apple)
        {
            return false;
        }

        if (virtualBody.Count >= size * size - 2)
        {
            return true;
        }

        GridPoint virtualTail = virtualBody.Last!.Value;
        return FindPath(size, head, virtualTail, virtualOccupied, allowedOccupiedTarget: virtualTail, blockedPoint: null) is not null;
    }

    private static List<Direction>? FindPath(
        int size,
        GridPoint start,
        GridPoint target,
        HashSet<GridPoint> occupied,
        GridPoint? allowedOccupiedTarget,
        GridPoint? blockedPoint)
    {
        var nodes = new List<GridPoint> { start };
        var parents = new List<int> { -1 };
        var parentDirections = new List<Direction?> { null };
        var visited = new HashSet<GridPoint> { start };
        int queueHead = 0;
        int found = start == target ? 0 : -1;

        while (queueHead < nodes.Count && found < 0)
        {
            GridPoint current = nodes[queueHead];
            foreach (Direction direction in OrderedDirectionsTo(current, target))
            {
                GridPoint next = current.Move(direction);
                if (!Inside(next, size))
                {
                    continue;
                }

                if (blockedPoint is not null && next == blockedPoint.Value)
                {
                    continue;
                }

                bool allowedOccupied = allowedOccupiedTarget is not null && next == allowedOccupiedTarget.Value;
                if (occupied.Contains(next) && !allowedOccupied)
                {
                    continue;
                }

                if (!visited.Add(next))
                {
                    continue;
                }

                nodes.Add(next);
                parents.Add(queueHead);
                parentDirections.Add(direction);

                if (next == target)
                {
                    found = nodes.Count - 1;
                    break;
                }
            }

            queueHead++;
        }

        if (found < 0)
        {
            return null;
        }

        var reverse = new List<Direction>();
        int node = found;
        while (node > 0)
        {
            reverse.Add(parentDirections[node]!.Value);
            node = parents[node];
        }

        reverse.Reverse();
        return reverse;
    }

    private static List<Direction>? FindPathWithPassability(
        int size,
        GridPoint start,
        GridPoint target,
        Func<GridPoint, bool> canEnter,
        int maxDepth,
        int maxNodes)
    {
        var nodes = new List<GridPoint> { start };
        var depths = new List<int> { 0 };
        var parents = new List<int> { -1 };
        var parentDirections = new List<Direction?> { null };
        var visited = new HashSet<GridPoint> { start };
        int queueHead = 0;
        int found = start == target ? 0 : -1;

        while (queueHead < nodes.Count && found < 0 && nodes.Count < maxNodes)
        {
            GridPoint current = nodes[queueHead];
            int depth = depths[queueHead];
            if (depth >= maxDepth)
            {
                queueHead++;
                continue;
            }

            foreach (Direction direction in OrderedDirectionsTo(current, target))
            {
                GridPoint next = current.Move(direction);
                if (!Inside(next, size) || !canEnter(next))
                {
                    continue;
                }

                if (!visited.Add(next))
                {
                    continue;
                }

                nodes.Add(next);
                depths.Add(depth + 1);
                parents.Add(queueHead);
                parentDirections.Add(direction);

                if (next == target)
                {
                    found = nodes.Count - 1;
                    break;
                }

                if (nodes.Count >= maxNodes)
                {
                    break;
                }
            }

            queueHead++;
        }

        if (found < 0)
        {
            return null;
        }

        var reverse = new List<Direction>();
        int node = found;
        while (node > 0)
        {
            reverse.Add(parentDirections[node]!.Value);
            node = parents[node];
        }

        reverse.Reverse();
        return reverse;
    }

    private static IEnumerable<Direction> OrderedDirectionsTo(GridPoint current, GridPoint target)
    {
        return ShortcutDirections
            .OrderBy(direction => current.Move(direction).ManhattanTo(target))
            .ThenBy(direction => direction);
    }

    private static Direction ChooseGifSafeChaseDirection(
        HamiltonCycle cycle,
        GridPoint head,
        GridPoint apple,
        LinkedList<GridPoint> body,
        HashSet<GridPoint> occupied)
    {
        Direction pathDirection = cycle.NextDirection(head);
        int targetDistance = cycle.ForwardDistance(head, apple);
        if (targetDistance <= 1)
        {
            return pathDirection;
        }

        int tailDistance = body.Count <= 1
            ? cycle.Size * cycle.Size
            : cycle.ForwardDistance(head, body.Last!.Value);
        if (targetDistance >= tailDistance)
        {
            return pathDirection;
        }

        int currentManhattan = head.ManhattanTo(apple);
        Direction bestDirection = pathDirection;
        int bestDistance = currentManhattan;
        int bestForward = 1;

        foreach (Direction direction in ShortcutDirections)
        {
            GridPoint next = head.Move(direction);
            if (!Inside(next, cycle.Size))
            {
                continue;
            }

            if (occupied.Contains(next) && next != apple)
            {
                continue;
            }

            int forward = cycle.ForwardDistance(head, next);
            if (forward <= 0 || forward > targetDistance || forward >= tailDistance)
            {
                continue;
            }

            int distance = next.ManhattanTo(apple);
            if (distance > bestDistance)
            {
                continue;
            }

            if (distance < bestDistance || forward > bestForward)
            {
                bestDistance = distance;
                bestForward = forward;
                bestDirection = direction;
            }
        }

        return bestDirection;
    }

    private static Queue<Direction>? TryBuildMonotonicShortcut(
        HamiltonCycle cycle,
        GridPoint head,
        GridPoint apple,
        LinkedList<GridPoint> body,
        HashSet<GridPoint> occupied)
    {
        int targetDistance = cycle.ForwardDistance(head, apple);
        if (targetDistance <= 1)
        {
            return null;
        }

        int tailDistance = body.Count <= 1
            ? cycle.Size * cycle.Size
            : cycle.ForwardDistance(head, body.Last!.Value);
        if (targetDistance >= tailDistance)
        {
            return null;
        }

        var nodes = new List<GridPoint> { head };
        var distances = new List<int> { 0 };
        var parents = new List<int> { -1 };
        var parentDirections = new List<Direction?> { null };
        var visited = new HashSet<GridPoint> { head };

        int queueHead = 0;
        int found = -1;
        while (queueHead < nodes.Count)
        {
            GridPoint current = nodes[queueHead];
            int currentDistance = distances[queueHead];

            foreach (Direction direction in ShortcutDirections)
            {
                GridPoint next = current.Move(direction);
                if (!Inside(next, cycle.Size))
                {
                    continue;
                }

                int nextDistance = cycle.ForwardDistance(head, next);
                if (nextDistance <= currentDistance || nextDistance > targetDistance || nextDistance >= tailDistance)
                {
                    continue;
                }

                if (occupied.Contains(next) && next != apple)
                {
                    continue;
                }

                if (!visited.Add(next))
                {
                    continue;
                }

                nodes.Add(next);
                distances.Add(nextDistance);
                parents.Add(queueHead);
                parentDirections.Add(direction);

                if (next == apple)
                {
                    found = nodes.Count - 1;
                    queueHead = nodes.Count;
                    break;
                }
            }

            queueHead++;
        }

        if (found < 0)
        {
            return null;
        }

        var reverse = new List<Direction>();
        int node = found;
        while (node > 0)
        {
            reverse.Add(parentDirections[node]!.Value);
            node = parents[node];
        }

        reverse.Reverse();
        return new Queue<Direction>(reverse);
    }

    private static Queue<Direction>? TryBuildShortcut(
        HamiltonCycle cycle,
        GridPoint head,
        GridPoint apple,
        int length,
        HashSet<GridPoint> occupied)
    {
        int size = cycle.Size;
        int maxDepth = size + size / 2;
        int maxNodes = size * 5;
        int targetDistance = cycle.ForwardDistance(head, apple);
        if (targetDistance <= 1)
        {
            return null;
        }

        int safeDistance = size * size - length;
        if (targetDistance >= safeDistance)
        {
            return null;
        }

        if (head.ManhattanTo(apple) > maxDepth)
        {
            return null;
        }

        var nodes = new List<GridPoint> { head };
        var depths = new List<int> { 0 };
        var parents = new List<int> { -1 };
        var parentDirections = new List<Direction?> { null };
        var visited = new Dictionary<GridPoint, int> { [head] = 0 };

        int queueHead = 0;
        int found = -1;
        while (queueHead < nodes.Count && nodes.Count < maxNodes)
        {
            GridPoint current = nodes[queueHead];
            int depth = depths[queueHead];
            if (depth >= maxDepth)
            {
                queueHead++;
                continue;
            }

            foreach (Direction direction in ShortcutDirections)
            {
                GridPoint next = current.Move(direction);
                if (!Inside(next, size))
                {
                    continue;
                }

                int distance = cycle.ForwardDistance(head, next);
                if (distance <= 0 || distance > targetDistance || distance >= safeDistance)
                {
                    continue;
                }

                if (occupied.Contains(next) && next != apple)
                {
                    continue;
                }

                if (visited.ContainsKey(next))
                {
                    continue;
                }

                visited[next] = nodes.Count;
                nodes.Add(next);
                depths.Add(depth + 1);
                parents.Add(queueHead);
                parentDirections.Add(direction);

                if (next == apple)
                {
                    found = nodes.Count - 1;
                    queueHead = nodes.Count;
                    break;
                }

                if (nodes.Count >= maxNodes)
                {
                    break;
                }
            }

            queueHead++;
        }

        if (found < 0)
        {
            return null;
        }

        var reverse = new List<Direction>();
        int node = found;
        while (node > 0)
        {
            reverse.Add(parentDirections[node]!.Value);
            node = parents[node];
        }

        reverse.Reverse();
        return new Queue<Direction>(reverse);
    }

    private static GridPoint ChooseApple(int size, HashSet<GridPoint> occupied, Random random)
    {
        int free = size * size - occupied.Count;
        if (free <= 0)
        {
            throw new InvalidOperationException("No free cell is available for apple placement.");
        }

        int selected = random.Next(free);
        int seen = 0;
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                var point = new GridPoint(x, y);
                if (occupied.Contains(point))
                {
                    continue;
                }

                if (seen == selected)
                {
                    return point;
                }

                seen++;
            }
        }

        throw new InvalidOperationException("Failed to select apple placement.");
    }

    private static GridPoint? ChooseGameApple(
        int size,
        IReadOnlyDictionary<GridPoint, DinosaurTailSegment> dinosaurs,
        GridPoint? currentApple,
        Random random)
    {
        int free = size * size - dinosaurs.Count;
        if (currentApple is not null)
        {
            free--;
        }

        if (free <= 0)
        {
            return null;
        }

        int selected = random.Next(free);
        int seen = 0;
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                var point = new GridPoint(x, y);
                if (dinosaurs.ContainsKey(point) ||
                    (currentApple is not null && point == currentApple.Value))
                {
                    continue;
                }

                if (seen == selected)
                {
                    return point;
                }

                seen++;
            }
        }

        return null;
    }

    private static bool Inside(GridPoint point, int size)
    {
        return point.X >= 0 && point.Y >= 0 && point.X < size && point.Y < size;
    }

    private static void ValidateOptions(DinosaurOptions options)
    {
        if (options.Size < 4 || options.Size % 2 != 0)
        {
            throw new ArgumentException("Dinosaur model requires an even size >= 4.");
        }

        if (options.Runs <= 0)
        {
            throw new ArgumentException("Dinosaur runs must be positive.");
        }

        if (options.FillStepDenominator <= 0)
        {
            throw new ArgumentException("Dinosaur fill step denominator must be positive.");
        }

        if (options.FillStepNumerator < 0)
        {
            throw new ArgumentException("Dinosaur fill step numerator cannot be negative.");
        }

        if (options.ExtraChaseFillStepDenominator <= 0)
        {
            throw new ArgumentException("Dinosaur extra chase fill step denominator must be positive.");
        }

        if (options.ExtraChaseFillStepNumerator < -1)
        {
            throw new ArgumentException("Dinosaur extra chase fill step numerator cannot be less than -1.");
        }

        if (options.ChaseLimitDenominator <= 0 ||
            options.ChaseLateAbortDenominator <= 0 ||
            options.ExtraChaseLimitDenominator <= 0)
        {
            throw new ArgumentException("Dinosaur chase limit denominator must be positive.");
        }

        if (options.ChaseLimitNumerator < 0 ||
            options.ChaseLateAbortNumerator < 0 ||
            options.ExtraChaseLimitNumerator < 0)
        {
            throw new ArgumentException("Dinosaur chase limit numerator cannot be negative.");
        }

        if (options.ChaseLateAbortMinAppleX < 0 || options.ChaseLateAbortMinAppleX >= options.Size)
        {
            throw new ArgumentException("Dinosaur chase late abort min apple X must be within the grid.");
        }

        if (options.ExtraChaseMinAppleX < 0 || options.ExtraChaseMinAppleX >= options.Size)
        {
            throw new ArgumentException("Dinosaur extra chase min apple X must be within the grid.");
        }

        if (options.CycleAdjacentMaxSkip < 0)
        {
            throw new ArgumentException("Dinosaur cycle adjacent max skip cannot be negative.");
        }

        if (options.CycleGreedyShortcutMaxSkip < 0)
        {
            throw new ArgumentException("Dinosaur cycle greedy shortcut max skip cannot be negative.");
        }

        if (options.CheckTickCost < 0)
        {
            throw new ArgumentException("Dinosaur check tick cost cannot be negative.");
        }

        if (options.RecoverWestStopX < 0 || options.RecoverWestStopX >= options.Size)
        {
            throw new ArgumentException("Dinosaur recover west stop X must be within the grid.");
        }

        if (options.RecoverBfsMaxDepth < 0)
        {
            throw new ArgumentException("Dinosaur recover BFS max depth cannot be negative.");
        }

        if (options.RecoverBfsMaxNodes <= 0)
        {
            throw new ArgumentException("Dinosaur recover BFS max nodes must be positive.");
        }

        if (options.CycleUseMoveResult && (options.CycleAdjacentMaxSkip > 0 || options.CycleGreedyShortcutMaxSkip > 0 || options.CycleBfsShortcut))
        {
            throw new ArgumentException("Dinosaur cycle move-result mode only supports the fixed cycle_finish path.");
        }

        if (options.UseMoveResult && (options.CycleAdjacentMaxSkip > 0 || options.CycleGreedyShortcutMaxSkip > 0 || options.CycleBfsShortcut))
        {
            throw new ArgumentException("Dinosaur global move-result mode only supports the fixed cycle_finish path.");
        }
    }
}

internal enum DinosaurPolicy
{
    LbCurrentGame,
    Cycle,
    GifSafeChase,
    GifBfsSafeChase,
    GifVirtualSafeChase,
    HamiltonShortcutProbe,
}

internal sealed class DinosaurTailSegment
{
    public DinosaurTailSegment(GridPoint position)
    {
        Position = position;
    }

    public GridPoint Position { get; }

    public bool CanMoveTo { get; set; }
}

internal sealed class DinosaurAggregate
{
    private long moves;
    private long actionTicks;
    private long apples;
    private long finalLength;
    private long shortcuts;
    private long canMoveChecks;
    private long measureChecks;
    private DinosaurCycleWaitStats cycleWaitStats = new();
    private DinosaurCycleEntryStats cycleEntryStats = new();
    private string? firstFailureDetail;
    private readonly Dictionary<string, DinosaurPhaseStats> phaseStats = new(StringComparer.Ordinal);

    public DinosaurAggregate(string policy, int runs)
    {
        Policy = policy;
        Runs = runs;
    }

    public string Policy { get; }

    public int Runs { get; }

    public int Completed { get; private set; }

    public int Collisions { get; private set; }

    public int Walls { get; private set; }

    public int MoveLimits { get; private set; }

    public double CompletionRate => (double)Completed / Runs;

    public double AverageMoves => (double)moves / Runs;

    public double AverageActionTicks => (double)actionTicks / Runs;

    public long TotalActionTicks => actionTicks;

    public double AverageApples => (double)apples / Runs;

    public double AverageFinalLength => (double)finalLength / Runs;

    public double AverageShortcuts => (double)shortcuts / Runs;

    public double AverageCanMoveChecks => (double)canMoveChecks / Runs;

    public double AverageMeasureChecks => (double)measureChecks / Runs;

    public double AverageScriptChecks => (double)(canMoveChecks + measureChecks) / Runs;

    public double AverageMovesPerApple => apples == 0 ? double.PositiveInfinity : (double)moves / apples;

    public double AverageActionTicksPerApple => apples == 0 ? double.PositiveInfinity : (double)actionTicks / apples;

    public string? FirstFailureDetail => firstFailureDetail;

    public IReadOnlyDictionary<string, DinosaurPhaseStats> PhaseStats => phaseStats;

    public DinosaurCycleWaitStats CycleWaitStats => cycleWaitStats;

    public DinosaurCycleEntryStats CycleEntryStats => cycleEntryStats;

    public void Add(DinosaurTrialResult result)
    {
        moves += result.Moves;
        actionTicks += result.ActionTicks;
        apples += result.Apples;
        finalLength += result.FinalLength;
        shortcuts += result.Shortcuts;
        canMoveChecks += result.CanMoveChecks;
        measureChecks += result.MeasureChecks;
        if (result.CycleWaitStats is DinosaurCycleWaitStats waitStats)
        {
            cycleWaitStats = cycleWaitStats.Add(waitStats);
        }

        if (result.CycleEntryStats is DinosaurCycleEntryStats entryStats)
        {
            cycleEntryStats = cycleEntryStats.Add(entryStats);
        }

        if (result.PhaseStats is not null)
        {
            foreach ((string phase, DinosaurPhaseStats stats) in result.PhaseStats)
            {
                phaseStats.TryGetValue(phase, out DinosaurPhaseStats current);
                phaseStats[phase] = current.Add(stats);
            }
        }

        switch (result.Status)
        {
            case DinosaurTrialStatus.Completed:
                Completed++;
                break;
            case DinosaurTrialStatus.Collision:
                Collisions++;
                break;
            case DinosaurTrialStatus.Wall:
                Walls++;
                break;
            case DinosaurTrialStatus.MoveLimit:
                MoveLimits++;
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(result), result.Status, null);
        }

        if (result.Status != DinosaurTrialStatus.Completed && firstFailureDetail is null)
        {
            firstFailureDetail = result.Detail;
        }
    }
}

internal enum DinosaurTrialStatus
{
    Completed,
    Collision,
    Wall,
    MoveLimit,
}

internal readonly record struct DinosaurTrialResult(
    DinosaurTrialStatus Status,
    int Moves,
    long ActionTicks,
    int Apples,
    int FinalLength,
    int Shortcuts,
    long CanMoveChecks = 0,
    long MeasureChecks = 0,
    string? Detail = null,
    IReadOnlyDictionary<string, DinosaurPhaseStats>? PhaseStats = null,
    DinosaurCycleWaitStats? CycleWaitStats = null,
    DinosaurCycleEntryStats? CycleEntryStats = null)
{
    public static DinosaurTrialResult Completed(
        int moves,
        long actionTicks,
        int apples,
        int finalLength,
        int shortcuts,
        IReadOnlyDictionary<string, DinosaurPhaseStats>? phaseStats = null)
    {
        return new DinosaurTrialResult(DinosaurTrialStatus.Completed, moves, actionTicks, apples, finalLength, shortcuts, PhaseStats: phaseStats);
    }

    public static DinosaurTrialResult Collision(
        int moves,
        long actionTicks,
        int apples,
        int finalLength,
        int shortcuts,
        string? detail = null,
        IReadOnlyDictionary<string, DinosaurPhaseStats>? phaseStats = null)
    {
        return new DinosaurTrialResult(DinosaurTrialStatus.Collision, moves, actionTicks, apples, finalLength, shortcuts, Detail: detail, PhaseStats: phaseStats);
    }

    public static DinosaurTrialResult Wall(
        int moves,
        long actionTicks,
        int apples,
        int finalLength,
        int shortcuts,
        string? detail = null,
        IReadOnlyDictionary<string, DinosaurPhaseStats>? phaseStats = null)
    {
        return new DinosaurTrialResult(DinosaurTrialStatus.Wall, moves, actionTicks, apples, finalLength, shortcuts, Detail: detail, PhaseStats: phaseStats);
    }

    public static DinosaurTrialResult MoveLimit(
        int moves,
        long actionTicks,
        int apples,
        int finalLength,
        int shortcuts,
        string? detail = null,
        IReadOnlyDictionary<string, DinosaurPhaseStats>? phaseStats = null)
    {
        return new DinosaurTrialResult(DinosaurTrialStatus.MoveLimit, moves, actionTicks, apples, finalLength, shortcuts, Detail: detail, PhaseStats: phaseStats);
    }
}

internal readonly record struct DinosaurPhaseStats(long Moves, long ActionTicks, long Apples)
{
    public DinosaurPhaseStats Add(DinosaurPhaseStats other)
    {
        return new DinosaurPhaseStats(Moves + other.Moves, ActionTicks + other.ActionTicks, Apples + other.Apples);
    }
}

internal readonly record struct DinosaurCycleEntryStats(
    long Samples,
    long ScriptLength,
    long GridDinosaurCount,
    long RemainingApples,
    long Moves,
    long ActionTicks,
    long CanMoveChecks,
    long MeasureChecks)
{
    public DinosaurCycleEntryStats(
        int ScriptLength,
        int GridDinosaurCount,
        int RemainingApples,
        int Moves,
        long ActionTicks,
        long CanMoveChecks,
        long MeasureChecks)
        : this(1, ScriptLength, GridDinosaurCount, RemainingApples, Moves, ActionTicks, CanMoveChecks, MeasureChecks)
    {
    }

    public bool IsEmpty => Samples == 0;

    public double AverageScriptLength => Average(ScriptLength);

    public double AverageGridDinosaurCount => Average(GridDinosaurCount);

    public double AverageRemainingApples => Average(RemainingApples);

    public double AverageMoves => Average(Moves);

    public double AverageActionTicks => Average(ActionTicks);

    public double AverageCanMoveChecks => Average(CanMoveChecks);

    public double AverageMeasureChecks => Average(MeasureChecks);

    public DinosaurCycleEntryStats Add(DinosaurCycleEntryStats other)
    {
        return new DinosaurCycleEntryStats(
            Samples + other.Samples,
            ScriptLength + other.ScriptLength,
            GridDinosaurCount + other.GridDinosaurCount,
            RemainingApples + other.RemainingApples,
            Moves + other.Moves,
            ActionTicks + other.ActionTicks,
            CanMoveChecks + other.CanMoveChecks,
            MeasureChecks + other.MeasureChecks);
    }

    private double Average(long value)
    {
        return Samples == 0 ? 0.0 : (double)value / Samples;
    }
}

internal readonly record struct DinosaurCycleWaitStats(
    long OpportunitySamples,
    long WaitedApples,
    long TotalWaitMoves,
    long ForwardDistanceSum,
    long ManhattanDistanceSum,
    long ForwardLe1,
    long ForwardLe2,
    long ForwardLe4,
    long ForwardLe8,
    long ManhattanLe1,
    long ManhattanLe2,
    long ManhattanLe4)
{
    public bool IsEmpty => OpportunitySamples == 0 && WaitedApples == 0;

    public double AverageWaitMoves => WaitedApples == 0 ? 0.0 : (double)TotalWaitMoves / WaitedApples;

    public double AverageForwardDistance => OpportunitySamples == 0 ? 0.0 : (double)ForwardDistanceSum / OpportunitySamples;

    public double AverageManhattanDistance => OpportunitySamples == 0 ? 0.0 : (double)ManhattanDistanceSum / OpportunitySamples;

    public double ForwardLe1Rate => Ratio(ForwardLe1, OpportunitySamples);

    public double ForwardLe2Rate => Ratio(ForwardLe2, OpportunitySamples);

    public double ForwardLe4Rate => Ratio(ForwardLe4, OpportunitySamples);

    public double ForwardLe8Rate => Ratio(ForwardLe8, OpportunitySamples);

    public double ManhattanLe1Rate => Ratio(ManhattanLe1, OpportunitySamples);

    public double ManhattanLe2Rate => Ratio(ManhattanLe2, OpportunitySamples);

    public double ManhattanLe4Rate => Ratio(ManhattanLe4, OpportunitySamples);

    public DinosaurCycleWaitStats Add(DinosaurCycleWaitStats other)
    {
        return new DinosaurCycleWaitStats(
            OpportunitySamples + other.OpportunitySamples,
            WaitedApples + other.WaitedApples,
            TotalWaitMoves + other.TotalWaitMoves,
            ForwardDistanceSum + other.ForwardDistanceSum,
            ManhattanDistanceSum + other.ManhattanDistanceSum,
            ForwardLe1 + other.ForwardLe1,
            ForwardLe2 + other.ForwardLe2,
            ForwardLe4 + other.ForwardLe4,
            ForwardLe8 + other.ForwardLe8,
            ManhattanLe1 + other.ManhattanLe1,
            ManhattanLe2 + other.ManhattanLe2,
            ManhattanLe4 + other.ManhattanLe4);
    }

    public DinosaurCycleWaitStats RecordOpportunity(int forwardDistance, int manhattanDistance)
    {
        return new DinosaurCycleWaitStats(
            OpportunitySamples + 1,
            WaitedApples,
            TotalWaitMoves,
            ForwardDistanceSum + forwardDistance,
            ManhattanDistanceSum + manhattanDistance,
            ForwardLe1 + (forwardDistance <= 1 ? 1 : 0),
            ForwardLe2 + (forwardDistance <= 2 ? 1 : 0),
            ForwardLe4 + (forwardDistance <= 4 ? 1 : 0),
            ForwardLe8 + (forwardDistance <= 8 ? 1 : 0),
            ManhattanLe1 + (manhattanDistance <= 1 ? 1 : 0),
            ManhattanLe2 + (manhattanDistance <= 2 ? 1 : 0),
            ManhattanLe4 + (manhattanDistance <= 4 ? 1 : 0));
    }

    public DinosaurCycleWaitStats RecordAppleWait(int moves)
    {
        return this with
        {
            WaitedApples = WaitedApples + 1,
            TotalWaitMoves = TotalWaitMoves + moves,
        };
    }

    private static double Ratio(long numerator, long denominator)
    {
        return denominator == 0 ? 0.0 : (double)numerator / denominator;
    }
}

internal sealed class HamiltonCycle
{
    private readonly Direction[,] directions;
    private readonly int[,] indexes;

    private HamiltonCycle(int size, Direction[,] directions, int[,] indexes)
    {
        Size = size;
        this.directions = directions;
        this.indexes = indexes;
    }

    public int Size { get; }

    public static HamiltonCycle Build(int size)
    {
        var directions = new Direction[size, size];
        var assigned = new bool[size, size];

        void Set(int x, int y, Direction direction)
        {
            directions[x, y] = direction;
            assigned[x, y] = true;
        }

        for (int i = 0; i < size - 1; i++)
        {
            Set(i, 0, Direction.East);
        }

        Set(size - 1, 0, Direction.North);

        int line = size - 1;
        for (int repeat = 0; repeat < size / 2; repeat++)
        {
            for (int i = 1; i < size - 1; i++)
            {
                Set(line, i, Direction.North);
            }

            Set(line, size - 1, Direction.West);
            line--;

            for (int i = 2; i < size; i++)
            {
                Set(line, i, Direction.South);
            }

            Set(line, 1, Direction.West);
            line--;
        }

        Set(0, 1, Direction.South);

        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                if (!assigned[x, y])
                {
                    throw new InvalidOperationException($"Hamilton path missing direction at {x},{y}.");
                }
            }
        }

        var indexes = new int[size, size];
        var current = new GridPoint(0, 0);
        for (int index = 0; index < size * size; index++)
        {
            indexes[current.X, current.Y] = index;
            current = current.Move(directions[current.X, current.Y]);
        }

        if (current != new GridPoint(0, 0))
        {
            throw new InvalidOperationException("Hamilton path does not return to origin.");
        }

        return new HamiltonCycle(size, directions, indexes);
    }

    public Direction NextDirection(GridPoint point)
    {
        return directions[point.X, point.Y];
    }

    public int ForwardDistance(GridPoint from, GridPoint to)
    {
        int distance = indexes[to.X, to.Y] - indexes[from.X, from.Y];
        if (distance < 0)
        {
            distance += Size * Size;
        }

        return distance;
    }
}
