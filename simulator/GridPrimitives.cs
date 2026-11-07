namespace TFWRMechanismModel;

internal enum Direction
{
    North,
    East,
    South,
    West,
}

internal static class DirectionExtensions
{
    public static GridPoint Delta(this Direction direction)
    {
        return direction switch
        {
            Direction.North => new GridPoint(0, 1),
            Direction.East => new GridPoint(1, 0),
            Direction.South => new GridPoint(0, -1),
            Direction.West => new GridPoint(-1, 0),
            _ => throw new ArgumentOutOfRangeException(nameof(direction), direction, null),
        };
    }

    public static string ShortName(this Direction direction)
    {
        return direction switch
        {
            Direction.North => "N",
            Direction.East => "E",
            Direction.South => "S",
            Direction.West => "W",
            _ => "?",
        };
    }
}

internal readonly record struct GridPoint(int X, int Y)
{
    public GridPoint Move(Direction direction)
    {
        GridPoint delta = direction.Delta();
        return new GridPoint(X + delta.X, Y + delta.Y);
    }

    public GridPoint Wrap(int size)
    {
        return new GridPoint(WrapAxis(X, size), WrapAxis(Y, size));
    }

    public int ManhattanTo(GridPoint other)
    {
        return Math.Abs(X - other.X) + Math.Abs(Y - other.Y);
    }

    public override string ToString()
    {
        return $"{X},{Y}";
    }

    private static int WrapAxis(int value, int size)
    {
        int wrapped = value % size;
        return wrapped < 0 ? wrapped + size : wrapped;
    }
}

internal static class ModelMath
{
    public static double Percent(double ratio)
    {
        return ratio * 100.0;
    }

    public static string FormatDouble(double value, int digits = 3)
    {
        return value.ToString($"F{digits}", System.Globalization.CultureInfo.InvariantCulture);
    }

    public static string FormatPercent(double ratio, int digits = 2)
    {
        return Percent(ratio).ToString($"F{digits}", System.Globalization.CultureInfo.InvariantCulture) + "%";
    }
}
