using System.Diagnostics;

namespace TFWRMechanismModel;

/// <summary>
/// Ground types needed by the first native underground kernel.
/// The full resource catalog will be migrated after the storage and propagation
/// contract has been checked against the Python model.
/// </summary>
internal enum KernelGroundKind : byte
{
    Dirt,
    Rock,
    Dynamite,
    Soot,
    Bedrock,
}

internal readonly record struct KernelGround(
    KernelGroundKind Kind,
    byte Hardness,
    byte Stability,
    bool AutoDestroyWhenDugBeside);

/// <summary>
/// Dense, headless underground state for benchmarking the original explosion
/// and cave-in data path. Depth is positive downwards and denotes the exposed
/// top of a column, matching the local simulator's internal coordinates.
/// </summary>
internal sealed class UndergroundKernel
{
    private const int ChunkDepth = 16;
    private readonly int width;
    private readonly int height;
    private readonly int maxDepth;
    private readonly int[] depths;
    private readonly KernelGround[] grounds;
    private readonly float[] energies;
    private readonly int[] energyMarks;
    private readonly int[] closedMarks;
    private int explosionGeneration;

    public UndergroundKernel(int width, int height, int maxDepth)
    {
        if (width <= 0 || height <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(width), "地下尺寸必须为正数。");
        }

        if (maxDepth <= 0 || maxDepth % ChunkDepth != 0)
        {
            throw new ArgumentOutOfRangeException(nameof(maxDepth), "最大深度必须为正数且是16的倍数。");
        }

        long cellCount = (long)width * height * maxDepth;
        if (cellCount > int.MaxValue)
        {
            throw new ArgumentOutOfRangeException(nameof(maxDepth), "地下数组过大。");
        }

        this.width = width;
        this.height = height;
        this.maxDepth = maxDepth;
        depths = new int[width * height];
        grounds = new KernelGround[(int)cellCount];
        energies = new float[(int)cellCount];
        energyMarks = new int[(int)cellCount];
        closedMarks = new int[(int)cellCount];
        FillBenchmarkGround();
    }

    public int MaxColumnDepth => depths.Max();

    public long ClearedBlocks { get; private set; }

    public long ExplosionCount { get; private set; }

    public long CaveInVisits { get; private set; }

    public long RunExplosiveDrill(int steps, GridPoint origin)
    {
        if (steps < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(steps));
        }

        if (!IsInside(origin))
        {
            throw new ArgumentOutOfRangeException(nameof(origin), "爆破位置必须在地下地图内。");
        }

        long drops = 0;
        for (int step = 0; step < steps; step++)
        {
            int originDepth = GetDepth(origin);
            drops += Explode(origin, originDepth, 1000.0f, collectDrops: true);
            ClearWithCaveIns(origin, originDepth + 1);
        }

        return drops;
    }

    private void FillBenchmarkGround()
    {
        for (int z = 0; z < maxDepth; z++)
        {
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    KernelGroundKind kind = z % 64 == 0 ? KernelGroundKind.Dynamite : KernelGroundKind.Dirt;
                    KernelGround ground = kind == KernelGroundKind.Dynamite
                        ? new KernelGround(kind, 0, 1, false)
                        : new KernelGround(kind, 1, 1, true);
                    grounds[CellIndex(x, y, z)] = ground;
                }
            }
        }
    }

    private long Explode(GridPoint origin, int originDepth, float energy, bool collectDrops)
    {
        ExplosionCount++;
        explosionGeneration++;
        if (explosionGeneration == 0)
        {
            Array.Clear(energyMarks);
            Array.Clear(closedMarks);
            explosionGeneration = 1;
        }

        var pending = new Queue<ExplosionPoint>();
        var cleared = collectDrops ? new List<ExplosionPoint>() : null;
        ExplosionPoint originPoint = new(origin.X, origin.Y, originDepth);
        SetEnergy(originPoint, energy, pending);
        while (pending.Count > 0)
        {
            ExplosionPoint point = pending.Dequeue();
            int index = CellIndex(point.X, point.Y, point.Z);
            float value = energies[index] - GetGround(point.X, point.Y, point.Z).Hardness;
            closedMarks[index] = explosionGeneration;
            if (value >= 0 && IsPresent(point.X, point.Y, point.Z))
            {
                if (collectDrops)
                {
                    cleared!.Add(point);
                }
                else
                {
                    ClearWithCaveIns(new GridPoint(point.X, point.Y), point.Z);
                }
            }

            float spread = value * 0.2f;
            if (spread <= 0)
            {
                continue;
            }

            foreach (ExplosionPoint neighbor in Neighbors3D(point))
            {
                if (!IsInside(neighbor.X, neighbor.Y) || neighbor.Z < 0 || neighbor.Z >= maxDepth)
                {
                    continue;
                }

                int neighborIndex = CellIndex(neighbor.X, neighbor.Y, neighbor.Z);
                if (energyMarks[neighborIndex] != explosionGeneration)
                {
                    energyMarks[neighborIndex] = explosionGeneration;
                    energies[neighborIndex] = 0;
                    pending.Enqueue(neighbor);
                }

                if (closedMarks[neighborIndex] != explosionGeneration)
                {
                    energies[neighborIndex] += spread;
                }
            }
        }

        long drops = 0;
        if (cleared is null)
        {
            return drops;
        }

        foreach (ExplosionPoint point in cleared)
        {
            int currentDepth = GetDepth(new GridPoint(point.X, point.Y));
            if (point.Z > currentDepth)
            {
                drops += point.Z - currentDepth;
            }

            ClearColumn(new GridPoint(point.X, point.Y), point.Z);
        }

        foreach (ExplosionPoint point in cleared)
        {
            ClearWithCaveIns(new GridPoint(point.X, point.Y), point.Z);
        }

        return drops;
    }

    private void SetEnergy(ExplosionPoint point, float energy, Queue<ExplosionPoint> pending)
    {
        int index = CellIndex(point.X, point.Y, point.Z);
        energyMarks[index] = explosionGeneration;
        energies[index] = energy;
        pending.Enqueue(point);
    }

    private void ClearWithCaveIns(GridPoint position, int upToDepth)
    {
        ClearColumn(position, upToDepth);
        var pending = new Queue<GridPoint>();
        foreach (GridPoint neighbor in Neighbors4(position))
        {
            if (!IsInside(neighbor))
            {
                continue;
            }

            if (GetGround(neighbor).AutoDestroyWhenDugBeside)
            {
                ClearColumn(neighbor, upToDepth - 1);
            }
            else
            {
                pending.Enqueue(neighbor);
            }
        }

        foreach (GridPoint diagonal in Diagonals(position))
        {
            if (IsInside(diagonal))
            {
                pending.Enqueue(diagonal);
            }
        }

        foreach (GridPoint ringPoint in RingAtDistanceTwo(position))
        {
            if (IsInside(ringPoint) && ringPoint.X - position.X != ringPoint.Y - position.Y)
            {
                pending.Enqueue(ringPoint);
            }
        }

        while (pending.Count > 0)
        {
            GridPoint target = pending.Dequeue();
            CaveInVisits++;
            GridPoint[] adjacent = Neighbors4(target).Where(IsInside).ToArray();
            int deepest = adjacent.Length == 0 ? 0 : adjacent.Max(GetDepth);
            int currentDepth = GetDepth(target);
            for (int z = deepest - 1; z >= currentDepth; z--)
            {
                if (GetGround(target, z).Stability < deepest - z)
                {
                    int newDepth = z + 1;
                    ClearColumn(target, newDepth);
                    foreach (GridPoint neighbor in adjacent)
                    {
                        if (GetDepth(neighbor) < newDepth)
                        {
                            pending.Enqueue(neighbor);
                        }
                    }

                    break;
                }
            }
        }
    }

    private void ClearColumn(GridPoint position, int depth)
    {
        int columnIndex = ColumnIndex(position);
        int clampedDepth = Math.Clamp(depth, depths[columnIndex], maxDepth);
        ClearedBlocks += clampedDepth - depths[columnIndex];
        depths[columnIndex] = clampedDepth;
    }

    private KernelGround GetGround(GridPoint position)
    {
        return GetGround(position, GetDepth(position));
    }

    private KernelGround GetGround(GridPoint position, int depth)
    {
        return GetGround(position.X, position.Y, depth);
    }

    private KernelGround GetGround(int x, int y, int depth)
    {
        if (depth < 0 || depth >= maxDepth)
        {
            return new KernelGround(KernelGroundKind.Bedrock, 255, 1, true);
        }

        return grounds[CellIndex(x, y, depth)];
    }

    private bool IsPresent(int x, int y, int depth)
    {
        return depth >= GetDepth(new GridPoint(x, y)) && depth < maxDepth;
    }

    private int GetDepth(GridPoint position)
    {
        return depths[ColumnIndex(position)];
    }

    private int CellIndex(int x, int y, int depth)
    {
        return (depth * height + y) * width + x;
    }

    private int ColumnIndex(GridPoint position)
    {
        return position.Y * width + position.X;
    }

    private bool IsInside(GridPoint point)
    {
        return IsInside(point.X, point.Y);
    }

    private bool IsInside(int x, int y)
    {
        return x >= 0 && x < width && y >= 0 && y < height;
    }

    private static IEnumerable<GridPoint> Neighbors4(GridPoint point)
    {
        yield return new GridPoint(point.X, point.Y + 1);
        yield return new GridPoint(point.X + 1, point.Y);
        yield return new GridPoint(point.X, point.Y - 1);
        yield return new GridPoint(point.X - 1, point.Y);
    }

    private static IEnumerable<GridPoint> Diagonals(GridPoint point)
    {
        yield return new GridPoint(point.X + 1, point.Y + 1);
        yield return new GridPoint(point.X + 1, point.Y - 1);
        yield return new GridPoint(point.X - 1, point.Y - 1);
        yield return new GridPoint(point.X - 1, point.Y + 1);
    }

    private static IEnumerable<GridPoint> RingAtDistanceTwo(GridPoint point)
    {
        (int X, int Y)[] directions = { (1, 0), (0, 1), (-1, 0), (0, -1) };
        for (int index = 0; index < directions.Length; index++)
        {
            (int dx, int dy) = directions[index];
            (int nx, int ny) = directions[(index + 1) % directions.Length];
            for (int step = 0; step < 4; step++)
            {
                yield return new GridPoint(
                    point.X - 2 * dx - 2 * nx + step * dx,
                    point.Y - 2 * dy - 2 * ny + step * dy);
            }
        }
    }

    private static IEnumerable<ExplosionPoint> Neighbors3D(ExplosionPoint point)
    {
        yield return new ExplosionPoint(point.X, point.Y + 1, point.Z);
        yield return new ExplosionPoint(point.X + 1, point.Y, point.Z);
        yield return new ExplosionPoint(point.X, point.Y - 1, point.Z);
        yield return new ExplosionPoint(point.X - 1, point.Y, point.Z);
        yield return new ExplosionPoint(point.X, point.Y, point.Z + 1);
        yield return new ExplosionPoint(point.X, point.Y, point.Z - 1);
    }

    private readonly record struct ExplosionPoint(int X, int Y, int Z);
}

internal static class UndergroundKernelBenchmark
{
    public static void Run(ArgumentReader reader)
    {
        int width = reader.GetInt("width", 32);
        int height = reader.GetInt("height", 32);
        int maxDepth = reader.GetInt("max-depth", 4096);
        int steps = reader.GetInt("steps", 1000);
        GridPoint origin = reader.GetPoint("origin", new GridPoint(width / 2, height / 2));

        var stopwatch = Stopwatch.StartNew();
        var kernel = new UndergroundKernel(width, height, maxDepth);
        long drops = kernel.RunExplosiveDrill(steps, origin);
        stopwatch.Stop();

        Console.WriteLine("C# underground kernel benchmark");
        Console.WriteLine($"  size={width}x{height} max_depth={maxDepth} steps={steps} origin={origin}");
        Console.WriteLine($"  wall_seconds={stopwatch.Elapsed.TotalSeconds.ToString("F6", System.Globalization.CultureInfo.InvariantCulture)}");
        Console.WriteLine($"  max_column_depth={kernel.MaxColumnDepth} drops={drops} cleared_blocks={kernel.ClearedBlocks}");
        Console.WriteLine($"  explosions={kernel.ExplosionCount} cave_in_visits={kernel.CaveInVisits}");
    }
}
