namespace TFWRMechanismModel;

internal sealed record CompanionOptions
{
    public int Size { get; init; } = 5;
    public int Samples { get; init; } = 100_000;
    public int Seed { get; init; } = 20260625;
    public string Crop { get; init; } = "grass";
    public string AcceptEntity { get; init; } = "bush";
    public GridPoint Target { get; init; } = new(4, 3);
    public IReadOnlySet<GridPoint> Blocked { get; init; } = new HashSet<GridPoint> { new(4, 4) };
    public IReadOnlySet<GridPoint>? Support { get; init; }
}

internal static class CompanionModel
{
    private static readonly string[] CompanionTypes =
    [
        "grass",
        "bush",
        "carrot",
        "tree",
    ];

    public static CompanionSummary Run(CompanionOptions options)
    {
        ValidateOptions(options);

        IReadOnlySet<GridPoint> support = options.Support ?? BuildRadiusSupport(options.Size, options.Target, options.Blocked);
        var random = new Random(options.Seed);
        var summary = new CompanionSummary(options.Samples, support.Count);

        for (int sample = 0; sample < options.Samples; sample++)
        {
            CompanionRequest request = CreateRequest(options, random);
            bool typeMatched = request.Entity == options.AcceptEntity;
            bool blocked = options.Blocked.Contains(request.Position);
            bool supported = support.Contains(request.Position);
            bool success = typeMatched && !blocked && supported;
            summary.Add(request, success, typeMatched, blocked, supported);
        }

        return summary;
    }

    private static CompanionRequest CreateRequest(CompanionOptions options, Random random)
    {
        GridPoint position;
        while (true)
        {
            int dx = random.Next(-3, 4);
            int dy = random.Next(-3, 4);
            position = new GridPoint(options.Target.X + dx, options.Target.Y + dy).Wrap(options.Size);

            // Core.decompiled.cs Growable.ChooseCompanion(): radius 3, wrapped,
            // not the current tile when world height > 1.
            if ((position == options.Target || Math.Abs(dx) + Math.Abs(dy) > 3) && options.Size != 1)
            {
                continue;
            }

            break;
        }

        string entity;
        do
        {
            entity = CompanionTypes[random.Next(CompanionTypes.Length)];
        }
        while (entity == options.Crop);

        return new CompanionRequest(entity, position);
    }

    private static IReadOnlySet<GridPoint> BuildRadiusSupport(int size, GridPoint target, IReadOnlySet<GridPoint> blocked)
    {
        var support = new HashSet<GridPoint>();
        for (int dx = -3; dx <= 3; dx++)
        {
            for (int dy = -3; dy <= 3; dy++)
            {
                GridPoint position = new GridPoint(target.X + dx, target.Y + dy).Wrap(size);
                if ((position == target || Math.Abs(dx) + Math.Abs(dy) > 3) && size != 1)
                {
                    continue;
                }

                if (blocked.Contains(position))
                {
                    continue;
                }

                support.Add(position);
            }
        }

        return support;
    }

    private static void ValidateOptions(CompanionOptions options)
    {
        if (options.Size <= 0)
        {
            throw new ArgumentException("Companion size must be positive.");
        }

        if (options.Samples <= 0)
        {
            throw new ArgumentException("Companion samples must be positive.");
        }

        if (!CompanionTypes.Contains(options.Crop))
        {
            throw new ArgumentException($"Unknown crop entity: {options.Crop}");
        }

        if (!CompanionTypes.Contains(options.AcceptEntity))
        {
            throw new ArgumentException($"Unknown accepted companion entity: {options.AcceptEntity}");
        }
    }
}

internal sealed class CompanionSummary
{
    private int success;
    private int typeMatched;
    private int blocked;
    private int unsupported;
    private readonly Dictionary<string, int> typeCounts = new(StringComparer.Ordinal);

    public CompanionSummary(int samples, int supportCount)
    {
        Samples = samples;
        SupportCount = supportCount;
    }

    public int Samples { get; }

    public int SupportCount { get; }

    public int Success => success;

    public double SuccessRate => (double)success / Samples;

    public double AverageRequestsPerSuccess => success == 0 ? double.PositiveInfinity : (double)Samples / success;

    public double AverageFailedRerollsBeforeSuccess => success == 0 ? double.PositiveInfinity : ((double)Samples - success) / success;

    public double TypeMatchRate => (double)typeMatched / Samples;

    public double BlockedRate => (double)blocked / Samples;

    public double UnsupportedRate => (double)unsupported / Samples;

    public IReadOnlyDictionary<string, int> TypeCounts => typeCounts;

    public void Add(CompanionRequest request, bool isSuccess, bool isTypeMatched, bool isBlocked, bool isSupported)
    {
        if (!typeCounts.TryAdd(request.Entity, 1))
        {
            typeCounts[request.Entity]++;
        }

        if (isSuccess)
        {
            success++;
        }

        if (isTypeMatched)
        {
            typeMatched++;
        }

        if (isBlocked)
        {
            blocked++;
        }

        if (!isSupported)
        {
            unsupported++;
        }
    }
}

internal readonly record struct CompanionRequest(string Entity, GridPoint Position);
