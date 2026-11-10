// 无界面宿主：脚本输入、诊断和效果边界；不连接Steam或真实存档。
#nullable disable
using Platforms;
using UnityEngine;

namespace Platforms {
    public enum EDlcType { None, Mining }
    [Flags] public enum EDlcMask { None=0, Minig=1, All=-1 }
}
namespace Core.Platform {
    public static class PlatformManager {
        public static EDlcMask InstalledDlcs = EDlcMask.All;
        public static EDlcMask DlcTypeToMask(EDlcType dlc)=>(EDlcMask)(1<<((int)dlc-1));
        public static bool IsDlcInstalled(EDlcType dlc)=>IsDlcInstalled(dlc,InstalledDlcs);
        public static bool IsDlcInstalled(EDlcType dlc,EDlcMask mask)=>dlc==EDlcType.None || mask.HasFlag(DlcTypeToMask(dlc));
    }
}
public partial class MainSim {
    public static MainSim Inst = new();
    public int harvestFactor=1;
    public Workspace workspace=new();
}
public class Workspace
{
    public Dictionary<string, CodeWindow> codeWindows = new(StringComparer.Ordinal);
    public Dictionary<string, string> SourceHashes { get; } = new();
    public Node Load(string entry)
    {
        string folder = Path.GetDirectoryName(entry);
        string name = Path.GetFileNameWithoutExtension(entry);
        var queue = new Queue<string>();
        queue.Enqueue(name);
        while (queue.TryDequeue(out string module))
        {
            if (module is "__builtins__" or "builtins" || codeWindows.ContainsKey(module)) continue;
            if (module != name && !System.Text.RegularExpressions.Regex.IsMatch(module, @"^[a-zA-Z_]\w*$")) throw new ArgumentException($"Invalid game module: {module}");
            string path = Path.Combine(folder, module + ".py");
            byte[] bytes = File.ReadAllBytes(path);
            var window = new CodeWindow { fileName = module, SourcePath = path, CodeInput = new CodeInput { text = System.Text.Encoding.UTF8.GetString(bytes).TrimStart('\uFEFF').Replace("\r\n", "\n") } };
            codeWindows.Add(module, window);
            window.Parse();
            SourceHashes[path] = Convert.ToHexStringLower(System.Security.Cryptography.SHA256.HashData(bytes));
            foreach (string imported in window.Imports) queue.Enqueue(imported);
        }
        return codeWindows[name].Parse();
    }
}
public class CodeInput { public string text; }
public class CodeWindow {
    public string fileName;
    public string SourcePath;
    public IEnumerable<string> Imports
    {
        get
        {
            var nodes = new Stack<Node>();
            nodes.Push(program.syntaxTree);
            while (nodes.TryPop(out var node))
            {
                if (node is ImportNode import)
                    foreach (string name in import.ModuleNames) yield return name;
                foreach (var child in node.slots) if (child != null) nodes.Push(child);
            }
        }
    }
    public CodeInput CodeInput=new();
    public Dictionary<string,FunctionNode> parsedFunctions=new();
    private Program program;
    public Node Parse() {
        if (program == null)
        {
            try
            {
                Tokenizer.Tokenize(CodeInput.text, out var stream);
                program = Parser.Parse(stream, this);
                program.syntaxTree.CheckForNonsensicalCode();
            }
            catch (ParseException ex)
            {
                int index = Math.Clamp(ex.startIndex, 0, CodeInput.text.Length);
                int line = CodeInput.text[..index].Count(c => c == '\n') + 1;
                int column = index - CodeInput.text.LastIndexOf('\n', Math.Max(0, index - 1));
                throw new FormatException($"{SourcePath}:{line}:{column}: {ex.Message}", ex);
            }
        }
        return program.syntaxTree;
    }
    public void SetErrorMessage(string message,int start,int end) { }
}
public class Logger {
    public List<string> Messages=new();
    public string Error;
    private HashSet<Node> warnings=new();
    public int Dropped { get; private set; }
    public void Log(string message) { if (Messages.Count < 10000) Messages.Add(message); else Dropped++; }
    public void LogWarning(string message,ProgramState state) { if(warnings.Add(state.CurrentExecutingNode)) Log("Warning: "+message); }
    public void LogError(string message,ProgramState state) { Error=message+"\n"+state.GetTrace(); Log(Error); }
    public void Close() { }
}
public static class Localizer { public static string Localize(string text)=>text??""; }
public static class OptionHolder {
    public static string GetString(string key,string fallback="disabled")=>key=="avalanche particles"?"disabled":fallback;
}
public static class Achievements {
    public static HashSet<string> Unlocked=new();
    public static void UnlockAchievement(string name)=>Unlocked.Add(name);
    public static void IncrementStat(string name,int count) { }
    public static void CollectItem(int item,double number,Duration now,Duration duration,bool trackRate,bool trackTotal) { }
}
public class RenderPackage { }
public class OptionSO : ScriptableObject { }
public class FarmRenderer { public enum FaceDirection { Top, Bottom, North, East, South, West } }
namespace UnityEngine {
    public static class Resources {
        public static List<Object> Objects=new();
        public static T[] LoadAll<T>(string path) where T:Object=>Objects.OfType<T>().ToArray();
        public static T Load<T>(string path) where T:Object=>Objects.OfType<T>().FirstOrDefault();
    }
}
