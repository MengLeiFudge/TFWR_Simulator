using System.Buffers.Binary;
using System.Security.Cryptography;

namespace TFWRMechanismModel;

internal sealed record RandomSequenceResult(
    int Seed,
    IReadOnlyDictionary<string, int> StreamSeeds,
    int[] ScriptRandomMillionths,
    int[] CactusValues);

// 仅复现流初始化和首台无人机的抽样，不推进世界事件或执行脚本。
internal static class RandomSequenceModel
{
    public static RandomSequenceResult Generate(int seed, int samples)
    {
        if (seed < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(seed), "Seed must be nonnegative.");
        }
        if (samples is < 1 or > 10_000)
        {
            throw new ArgumentOutOfRangeException(nameof(samples), "Samples must be between 1 and 10000.");
        }

        // Simulation 构造顺序；Helper.JustSha256It 每次消耗主流 16 字节。
        string[] names = ["various", "maze", "snake", "cactus", "sunflower", "pumpkin", "poly", "random"];
        var master = new Random(seed);
        var streamSeeds = new Dictionary<string, int>();
        byte[] input = new byte[16];
        foreach (string name in names)
        {
            master.NextBytes(input);
            streamSeeds[name] = BinaryPrimitives.ReadInt32LittleEndian(SHA256.HashData(input)) & int.MaxValue;
        }

        // ProgramState 再从 random 流取一个 seed；不能直接用该流生成 random()。
        var script = new Random(new Random(streamSeeds["random"]).Next());
        var cactus = new Random(streamSeeds["cactus"]);
        int[] scriptValues = new int[samples];
        int[] cactusValues = new int[samples];
        for (int index = 0; index < samples; index++)
        {
            scriptValues[index] = (int)Math.Floor(script.NextDouble() * 1_000_000);
            cactusValues[index] = cactus.Next(10);
        }
        return new RandomSequenceResult(seed, streamSeeds, scriptValues, cactusValues);
    }
}
