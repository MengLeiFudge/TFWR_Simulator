using System.Diagnostics;
using System.Globalization;
using System.Text.Json;
using Platforms;
using UnityEngine;

public sealed class HeadlessRunner : ISimRunner {
    public Transform SceneScaler=>new();
    public Logger Logger {get;}=new();
    public int RenderLayer=>0;
    public Vector3 PiggyBankPosition=>Vector3.zero;
    public double TimeFactor {get;set;}=1;
    public bool StepByStepMode {get;set;}
    public int HarvestFactor=>1;
    public bool RecordsAchievements=>false;
    public EDlcMask InstalledDlcs=>EDlcMask.All;
    public RenderPackage GetRenderPackage()=>new();
    public void ScheduleLeaderboardStart(MainSim.LeaderboardStartArgs args)=>throw new NotSupportedException("Use the CLI scenario options instead of nested simulate/run_leaderboard");
    public void PlaySound(SoundEffectType sound,Vector2Int pos) { }
    public void PlayEffect(VFXType effect,Vector3 pos,bool changeColor=false,Color color=default,string? text=null,float lifetime=0,float crumblePushAngle=0) { }
    public void CollectItemEffect(int item,Vector3 pos) { }
    public void CrumbleEffect(Vector3Int pos) { }
    public void SlideBlockEffect(Vector2Int source,Vector2Int target) { }
    public void SlideAndPopBlockEffect(Vector2Int source,Vector2Int target,int depth,int lifetime) { }
    public void DelayedPopBlockEffect(Vector3Int pos,float delay,Vector3 velocity) { }
    public void BlinkEffect(Node node) { }
    public void SetDirty() { }
}
public static class SimulatorCli
{
    public static async Task<int> Main(string[] args)
    {
        Console.OutputEncoding = System.Text.Encoding.UTF8;
        CultureInfo.DefaultThreadCurrentCulture = CultureInfo.InvariantCulture;
        if (args.Length == 0 || args[0] == "--help") { Console.WriteLine(SimulationOptions.Help); return 0; }
        SimulationOptions? options = null;
        System.Text.Json.Nodes.JsonObject report;
        try
        {
            options = SimulationOptions.Parse(args);
            report = options.Worker ? SimulationWorker.Run(options) : await SimulationSupervisor.Run(options);
        }
        catch (Exception ex)
        {
            report = new System.Text.Json.Nodes.JsonObject { ["backend"] = "csharp-native", ["stop_reason"] = "error", ["state_complete"] = false, ["error"] = ex.ToString() };
        }
        try
        {
            if (options?.Output != null) File.WriteAllText(options.Output, report.ToJsonString(new JsonSerializerOptions { WriteIndented = true }) + "\n");
        }
        catch (IOException ex)
        {
            report["error"] = $"Cannot write report: {ex.Message}";
            report["stop_reason"] = "report_write_error";
        }
        catch (UnauthorizedAccessException ex)
        {
            report["error"] = $"Cannot write report: {ex.Message}";
            report["stop_reason"] = "report_write_error";
        }
        Console.WriteLine(report.ToJsonString(new JsonSerializerOptions { WriteIndented = true }));
        if (report["reports"] is System.Text.Json.Nodes.JsonArray reports)
            return report["error"] != null || reports.Any(r => r?["error"] != null) ? 1 : 0;
        return report["error"] != null ? 1 : 0;
    }
}
