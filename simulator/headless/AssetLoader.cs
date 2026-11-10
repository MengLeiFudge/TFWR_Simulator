using System.Collections;
using System.Reflection;
using System.Text.Json;
using UnityEngine;
using UObject=UnityEngine.Object;

// 保留原版资源顺序、字段精度和对象引用；图形资源只建立空句柄。
public static class AssetLoader {
    private static readonly Dictionary<string,UObject> objects=new(StringComparer.Ordinal);
    public static void Load(string path) {
        using var document=JsonDocument.Parse(File.ReadAllText(path));
        var rows=document.RootElement.GetProperty("objects");
        var types=typeof(AssetLoader).Assembly.GetTypes().Where(t=>typeof(UObject).IsAssignableFrom(t)).ToDictionary(t=>t.Name);
        objects.Clear(); Resources.Objects.Clear();
        foreach(var row in rows.EnumerateArray()) {
            string name=row.GetProperty("type").GetString()!;
            if(!types.TryGetValue(name,out var type)) throw new InvalidDataException($"Unknown resource type: {name}");
            var obj=(UObject)Activator.CreateInstance(type)!;
            obj.name=row.GetProperty("name").GetString()!;
            objects.Add(row.GetProperty("id").GetString()!,obj);
            Resources.Objects.Add(obj);
        }
        foreach(var row in rows.EnumerateArray()) Populate(objects[row.GetProperty("id").GetString()!],row.GetProperty("fields"));
        foreach(var obj in Resources.Objects) Enable(obj);
        var design=Resources.Objects.OfType<DesignConstants>().Single();
        typeof(DesignConstants).GetProperty("Inst")!.SetValue(null,design);
        ResourceManager.LoadAll();
        design.Start();
    }
    private static void Populate(object obj,JsonElement json) {
        foreach(var member in json.EnumerateObject()) {
            var field=obj.GetType().GetField(member.Name,BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance);
            if(field==null) continue; // Unity serialization metadata and removed graphics-only fields.
            field.SetValue(obj,Read(field.FieldType,member.Value));
        }
    }
    private static object? Read(Type type,JsonElement json) {
        if(json.ValueKind==JsonValueKind.Null) return null;
        if(type==typeof(string)) return json.GetString();
        if(type==typeof(bool)) return json.ValueKind is JsonValueKind.True or JsonValueKind.False?json.GetBoolean():json.GetInt32()!=0;
        if(type.IsEnum) return Enum.ToObject(type,json.GetInt32());
        if(type.IsPrimitive) return JsonSerializer.Deserialize(json.GetRawText(),type);
        if(json.ValueKind==JsonValueKind.Object && json.TryGetProperty("ref",out var reference)) {
            string key=reference.GetString()!;
            if(objects.TryGetValue(key,out var obj)) return obj;
            if(type==typeof(Mesh)||type==typeof(Sprite)||type==typeof(AudioClip)||type==typeof(GameObject)||type==typeof(Material)||type==typeof(Texture2D)) return Activator.CreateInstance(type);
            throw new InvalidDataException($"Unresolved {type.Name} reference: {key}");
        }
        if(type.IsArray) {
            var elementType=type.GetElementType()!;
            var array=Array.CreateInstance(elementType,json.GetArrayLength()); int i=0;
            foreach(var element in json.EnumerateArray()) array.SetValue(Read(elementType,element),i++);
            return array;
        }
        if(type.IsGenericType && type.GetGenericTypeDefinition()==typeof(List<>)) {
            var list=(IList)Activator.CreateInstance(type)!;
            foreach(var element in json.EnumerateArray()) list.Add(Read(type.GenericTypeArguments[0],element));
            return list;
        }
        if(type==typeof(AnimationCurve)) {
            var keys=json.GetProperty("m_Curve").EnumerateArray().Select(k=>new Keyframe(k.GetProperty("time").GetSingle(),k.GetProperty("value").GetSingle(),k.GetProperty("inSlope").GetSingle(),k.GetProperty("outSlope").GetSingle(),k.GetProperty("inWeight").GetSingle(),k.GetProperty("outWeight").GetSingle()) {weightedMode=(WeightedMode)k.GetProperty("weightedMode").GetInt32()}).ToArray();
            return new AnimationCurve(keys);
        }
        if(type==typeof(Gradient)) {
            var gradient=new Gradient();
            int count=json.GetProperty("m_NumColorKeys").GetInt32();
            gradient.colorKeys=Enumerable.Range(0,count).Select(i=>new GradientColorKey((Color)Read(typeof(Color),json.GetProperty($"key{i}"))!,json.GetProperty($"ctime{i}").GetInt32()/65535f)).ToArray();
            count=json.GetProperty("m_NumAlphaKeys").GetInt32();
            gradient.alphaKeys=Enumerable.Range(0,count).Select(i=>new GradientAlphaKey(json.GetProperty($"key{i}").GetProperty("a").GetSingle(),json.GetProperty($"atime{i}").GetInt32()/65535f)).ToArray();
            return gradient;
        }
        var result=Activator.CreateInstance(type)??throw new InvalidDataException($"Cannot initialize {type.Name}");
        Populate(result,json);
        return result;
    }
    public static object Clone(object original) {
        var copy=CloneValue(original,true)!;
        Enable(copy);
        return copy;
    }
    public static void Enable(object obj) => obj.GetType().GetMethod("OnEnable",BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic)?.Invoke(obj,null);
    private static object? CloneValue(object? value,bool root=false) {
        if(value==null) return null;
        var type=value.GetType();
        if(type.IsValueType||value is string||(!root&&value is UObject)) return value;
        if(value is Array array) {
            var copy=(Array)array.Clone();
            for(int i=0;i<copy.Length;i++) copy.SetValue(CloneValue(array.GetValue(i)),i);
            return copy;
        }
        var result=Activator.CreateInstance(type)!;
        foreach(var field in type.GetFields(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance)) {
            if(field.IsDefined(typeof(NonSerializedAttribute))) continue;
            field.SetValue(result,CloneValue(field.GetValue(value)));
        }
        return result;
    }
}
