namespace TFWRMechanismModel;

internal sealed record CactusOptions
{
    public int Size { get; init; } = 32;
    public int Samples { get; init; } = 1_000;
    public int Seed { get; init; } = 20260625;
    public int ActionTick { get; init; } = 200;
}

internal static class CactusModel
{
    public static CactusSummary Run(CactusOptions options)
    {
        ValidateOptions(options);

        var random = new Random(options.Seed);
        var summary = new CactusSummary(options.Samples);

        for (int sample = 0; sample < options.Samples; sample++)
        {
            int[,] board = CreateBoard(options.Size, random);
            CactusBoardCost cost = SortRowsThenColumns(board);
            summary.Add(cost);
        }

        return summary;
    }

    private static int[,] CreateBoard(int size, Random random)
    {
        var board = new int[size, size];
        for (int y = 0; y < size; y++)
        {
            for (int x = 0; x < size; x++)
            {
                // Core.decompiled.cs Cactus.OnRestart(): randomCactus.Next(10).
                board[x, y] = random.Next(10);
            }
        }

        return board;
    }

    private static CactusBoardCost SortRowsThenColumns(int[,] board)
    {
        int size = board.GetLength(0);
        var total = new CactusBoardCost();

        for (int y = 0; y < size; y++)
        {
            int[] values = new int[size];
            for (int x = 0; x < size; x++)
            {
                values[x] = board[x, y];
            }

            CactusLineSortResult sorted = SortWindow3(values);
            total.AddRow(sorted.Cost);
            for (int x = 0; x < size; x++)
            {
                board[x, y] = sorted.Values[x];
            }
        }

        for (int x = 0; x < size; x++)
        {
            int[] values = new int[size];
            for (int y = 0; y < size; y++)
            {
                values[y] = board[x, y];
            }

            CactusLineSortResult sorted = SortWindow3(values);
            total.AddColumn(sorted.Cost);
            for (int y = 0; y < size; y++)
            {
                board[x, y] = sorted.Values[y];
            }
        }

        if (!IsRowsAndColumnsSorted(board))
        {
            total.Failures++;
        }

        return total;
    }

    private static CactusLineSortResult SortWindow3(int[] input)
    {
        int[] values = (int[])input.Clone();
        var cost = new CactusLineCost();
        int boundLow = 0;
        int boundHigh = values.Length - 1;
        int pos = 0;

        void MoveTo(int target)
        {
            cost.Moves += Math.Abs(target - pos);
            pos = target;
        }

        while (true)
        {
            int swapPosLast = -1;
            MoveTo(boundLow);
            int i = boundLow;
            while (i < boundHigh - 1)
            {
                i++;
                cost.Moves++;
                pos = i;
                cost.Measures += 3;

                if (values[i - 1] > values[i])
                {
                    Swap(values, i - 1, i);
                    cost.Swaps++;
                    swapPosLast = Math.Max(swapPosLast, i);
                }

                if (values[i] > values[i + 1])
                {
                    Swap(values, i, i + 1);
                    cost.Swaps++;
                    swapPosLast = Math.Max(swapPosLast, i + 1);

                    if (values[i - 1] > values[i])
                    {
                        Swap(values, i - 1, i);
                        cost.Swaps++;
                    }
                }
            }

            if (swapPosLast == -1)
            {
                break;
            }

            boundHigh = swapPosLast - 2;
            if (boundLow >= boundHigh)
            {
                break;
            }

            int swapPosFirst = values.Length;
            MoveTo(boundHigh);
            i = boundHigh;
            while (i > boundLow + 1)
            {
                i--;
                cost.Moves++;
                pos = i;
                cost.Measures += 3;

                if (values[i] > values[i + 1])
                {
                    Swap(values, i, i + 1);
                    cost.Swaps++;
                    swapPosFirst = Math.Min(swapPosFirst, i);
                }

                if (values[i - 1] > values[i])
                {
                    Swap(values, i - 1, i);
                    cost.Swaps++;
                    swapPosFirst = Math.Min(swapPosFirst, i - 1);

                    if (values[i] > values[i + 1])
                    {
                        Swap(values, i, i + 1);
                        cost.Swaps++;
                    }
                }
            }

            if (swapPosFirst == values.Length)
            {
                break;
            }

            boundLow = swapPosFirst + 2;
            if (boundLow >= boundHigh)
            {
                break;
            }
        }

        if (boundLow + 1 == boundHigh)
        {
            MoveTo(boundLow);
            cost.Measures += 2;
            if (values[boundLow] > values[boundLow + 1])
            {
                Swap(values, boundLow, boundLow + 1);
                cost.Swaps++;
            }
        }

        if (!IsSorted(values))
        {
            cost.Failures++;
        }

        return new CactusLineSortResult(values, cost);
    }

    private static bool IsRowsAndColumnsSorted(int[,] board)
    {
        int size = board.GetLength(0);
        for (int y = 0; y < size; y++)
        {
            for (int x = 1; x < size; x++)
            {
                if (board[x - 1, y] > board[x, y])
                {
                    return false;
                }
            }
        }

        for (int x = 0; x < size; x++)
        {
            for (int y = 1; y < size; y++)
            {
                if (board[x, y - 1] > board[x, y])
                {
                    return false;
                }
            }
        }

        return true;
    }

    private static bool IsSorted(int[] values)
    {
        for (int i = 1; i < values.Length; i++)
        {
            if (values[i - 1] > values[i])
            {
                return false;
            }
        }

        return true;
    }

    private static void Swap(int[] values, int left, int right)
    {
        (values[left], values[right]) = (values[right], values[left]);
    }

    private static void ValidateOptions(CactusOptions options)
    {
        if (options.Size <= 1)
        {
            throw new ArgumentException("Cactus size must be greater than 1.");
        }

        if (options.Samples <= 0)
        {
            throw new ArgumentException("Cactus samples must be positive.");
        }
    }
}

internal sealed class CactusSummary
{
    private long rowMoves;
    private long rowSwaps;
    private long rowMeasures;
    private long columnMoves;
    private long columnSwaps;
    private long columnMeasures;
    private long rowWallActions;
    private long columnWallActions;
    private int failures;

    public CactusSummary(int samples)
    {
        Samples = samples;
    }

    public int Samples { get; }

    public double AverageRowMoves => (double)rowMoves / Samples;

    public double AverageRowSwaps => (double)rowSwaps / Samples;

    public double AverageRowMeasures => (double)rowMeasures / Samples;

    public double AverageColumnMoves => (double)columnMoves / Samples;

    public double AverageColumnSwaps => (double)columnSwaps / Samples;

    public double AverageColumnMeasures => (double)columnMeasures / Samples;

    public double AverageSortActions => (double)(rowMoves + rowSwaps + columnMoves + columnSwaps) / Samples;

    public double AverageMeasureCount => (double)(rowMeasures + columnMeasures) / Samples;

    public double AverageWallActions => (double)(rowWallActions + columnWallActions) / Samples;

    public int Failures => failures;

    public void Add(CactusBoardCost cost)
    {
        rowMoves += cost.RowMoves;
        rowSwaps += cost.RowSwaps;
        rowMeasures += cost.RowMeasures;
        columnMoves += cost.ColumnMoves;
        columnSwaps += cost.ColumnSwaps;
        columnMeasures += cost.ColumnMeasures;
        rowWallActions += cost.RowWallActions;
        columnWallActions += cost.ColumnWallActions;
        failures += cost.Failures;
    }
}

internal sealed class CactusBoardCost
{
    public long RowMoves { get; private set; }

    public long RowSwaps { get; private set; }

    public long RowMeasures { get; private set; }

    public long ColumnMoves { get; private set; }

    public long ColumnSwaps { get; private set; }

    public long ColumnMeasures { get; private set; }

    public long RowWallActions { get; private set; }

    public long ColumnWallActions { get; private set; }

    public int Failures { get; set; }

    public void AddRow(CactusLineCost cost)
    {
        RowMoves += cost.Moves;
        RowSwaps += cost.Swaps;
        RowMeasures += cost.Measures;
        RowWallActions = Math.Max(RowWallActions, cost.Actions);
        Failures += cost.Failures;
    }

    public void AddColumn(CactusLineCost cost)
    {
        ColumnMoves += cost.Moves;
        ColumnSwaps += cost.Swaps;
        ColumnMeasures += cost.Measures;
        ColumnWallActions = Math.Max(ColumnWallActions, cost.Actions);
        Failures += cost.Failures;
    }
}

internal sealed class CactusLineCost
{
    public long Moves { get; set; }

    public long Swaps { get; set; }

    public long Measures { get; set; }

    public int Failures { get; set; }

    public long Actions => Moves + Swaps;
}

internal sealed record CactusLineSortResult(int[] Values, CactusLineCost Cost);
