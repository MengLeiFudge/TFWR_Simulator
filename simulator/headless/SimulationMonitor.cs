using System.Diagnostics;
using System.Text.Json;

public sealed class SimulationLimitException(string reason) : Exception(reason);

// 原生解释器中的观察钩子不增加游戏tick；每个工作进程持有一份。
public sealed class SimulationMonitor : IDisposable
{
    public static SimulationMonitor? Current { get; set; }
    private readonly Stopwatch clock;
    private readonly double wallLimit;
    private readonly long callLimit;
    private readonly long nodeLimit;
    private readonly StreamWriter? trace;
    private readonly string? profilePath;
    private readonly Dictionary<ProgramState, (long id, string name, object?[] args, ExecutionProfile.Fee? fee, long startedNs)> pending = new();
    public Dictionary<string, long> Calls { get; } = new();
    public Dictionary<string, double> ApiTicks { get; } = new();
    public long CallCount { get; private set; }
    public long NodeCount { get; private set; }
    public string? LimitReason { get; private set; }
    public ExecutionProfile? Profile { get; }

    public SimulationMonitor(Stopwatch clock, double wallLimit, long callLimit, long nodeLimit, string? tracePath, string? profilePath = null)
    {
        this.clock = clock;
        this.wallLimit = wallLimit;
        this.callLimit = callLimit;
        this.nodeLimit = nodeLimit;
        if (tracePath != null) trace = new StreamWriter(tracePath, false, System.Text.Encoding.UTF8);
        this.profilePath = profilePath;
        if (profilePath != null) Profile = new ExecutionProfile();
    }
    public void CheckNode(Node node, ProgramState state)
    {
        if (++NodeCount > nodeLimit) Stop("node_limit");
        if ((NodeCount & 1023) == 0 && clock.Elapsed.TotalSeconds >= wallLimit) Stop("wall_time_limit");
        Profile?.CountNode(node, state);
    }
    public void Charge(Node node, ProgramState state, double ticks, bool apiCall)
    {
        if (!apiCall) Profile?.Charge(node, state, ticks);
    }
    public void Begin(ProgramState state, string name, List<IPyObject> args, Simulation sim)
    {
        if (CallCount >= callLimit) Stop("api_call_limit");
        CallCount++;
        Calls[name] = Calls.GetValueOrDefault(name) + 1;
        pending[state] = (CallCount, name, trace == null ? [] : args.Select(a => Value(a)).ToArray(),
                          Profile?.Begin(state.CurrentExecutingNode, state), sim.CurrentTime.nanoseconds);
    }
    public void Complete(ProgramState state, Simulation sim, double ticks)
    {
        if (!pending.Remove(state, out var call)) return;
        ApiTicks[call.name] = ApiTicks.GetValueOrDefault(call.name) + ticks;
        if (call.fee != null) ExecutionProfile.Complete(call.fee, call.name, ticks, sim.CurrentTime.nanoseconds - call.startedNs);
        if (trace != null)
            trace.WriteLine(JsonSerializer.Serialize(new { id = call.id, function = call.name, drone = state.DroneId,
                applied_ns = sim.CurrentTime.nanoseconds, ticks, args = call.args, result = Value(state.ReturnValue) }));
    }
    public void WriteProfile(Simulation sim, bool stateComplete, IReadOnlyDictionary<string, string> sources)
    {
        if (Profile == null || profilePath == null) return;
        object report = Profile.Report(sim, stateComplete, sources, pending.Count);
        File.WriteAllText(profilePath, JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true }) + "\n");
    }
    private void Stop(string reason)
    {
        LimitReason = reason;
        throw new SimulationLimitException(reason);
    }
    private static object? Value(IPyObject? value, int depth = 0)
    {
        if (depth > 16) return "<depth limit>";
        return value switch
        {
            null or PyNone => null,
            PyBool boolean => boolean.num != 0,
            PyNumber number => double.IsFinite(number.num) ? (object)number.num : number.num.ToString(System.Globalization.CultureInfo.InvariantCulture),
            PyString text => text.str,
            PyDict dict => dict.dict.Select(p => new[] { Value(p.Key, depth + 1), Value(p.Value.obj, depth + 1) }).ToArray(),
            IEnumerable<IPyObject> sequence => sequence.Take(4096).Select(v => Value(v, depth + 1)).ToArray(),
            _ => value.ToString()
        };
    }
    public void Dispose()
    {
        trace?.Dispose();
        if (Current == this) Current = null;
    }
}
