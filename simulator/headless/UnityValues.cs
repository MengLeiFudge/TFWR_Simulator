// Unity值类型的无引擎实现；渲染句柄只保留数据，不创建场景对象。
using System.Globalization;
namespace UnityEngine;

public class Object {
    public string name = "";
    public static implicit operator bool(Object? value) => value is not null;
    public static T Instantiate<T>(T original) where T:Object => (T)AssetLoader.Clone(original);
}
public class ScriptableObject : Object { public static T CreateInstance<T>() where T:ScriptableObject,new() {var obj=new T();AssetLoader.Enable(obj);return obj;} }
public class MonoBehaviour : Object { }
public class Mesh : Object { }
public class Sprite : Object { }
public class Material : Object { }
public class Texture2D : Object { }
public class AudioClip : Object { }
public class GameObject : Object { }
public class Transform : Object { }
public class Gradient {
    public GradientColorKey[] colorKeys = []; public GradientAlphaKey[] alphaKeys = [];
    public void SetKeys(GradientColorKey[] colors,GradientAlphaKey[] alphas) {colorKeys=(GradientColorKey[])colors.Clone();alphaKeys=(GradientAlphaKey[])alphas.Clone();}
    public Color Evaluate(float t) {
        if(colorKeys.Length==0) return Color.white;
        if(t<=colorKeys[0].time) return colorKeys[0].color;
        for(int i=1;i<colorKeys.Length;i++) if(t<colorKeys[i].time) return Color.Lerp(colorKeys[i-1].color,colorKeys[i].color,(t-colorKeys[i-1].time)/(colorKeys[i].time-colorKeys[i-1].time));
        return colorKeys[^1].color;
    }
}
public struct GradientColorKey(Color color, float time) { public Color color = color; public float time = time; }
public struct GradientAlphaKey(float alpha, float time) { public float alpha = alpha; public float time = time; }
public struct Color(float r, float g, float b, float a = 1) { public float r=r,g=g,b=b,a=a; public static Color black => new(0,0,0); public static Color white => new(1,1,1); public static Color Lerp(Color x,Color y,float t)=>new(Mathf.Lerp(x.r,y.r,t),Mathf.Lerp(x.g,y.g,t),Mathf.Lerp(x.b,y.b,t),Mathf.Lerp(x.a,y.a,t)); }
public enum WeightedMode { None, In, Out, Both }
public struct Keyframe(float time, float value, float inTangent=0, float outTangent=0, float inWeight=0, float outWeight=0) { public float time=time,value=value,inTangent=inTangent,outTangent=outTangent,inWeight=inWeight,outWeight=outWeight; public WeightedMode weightedMode; }
public class AnimationCurve(params Keyframe[] keys) {
    public Keyframe[] keys = keys;
    public float Evaluate(float time) {
        if(keys.Length==0) return 0;
        if(time<=keys[0].time) return keys[0].value;
        for(int i=1;i<keys.Length;i++) if(time<keys[i].time) {
            var a=keys[i-1]; var b=keys[i];
            if(a.weightedMode!=WeightedMode.None || b.weightedMode!=WeightedMode.None) throw new NotSupportedException("Weighted animation curves require a verified adapter");
            float dt=b.time-a.time, t=(time-a.time)/dt, t2=t*t, t3=t2*t;
            return (2*t3-3*t2+1)*a.value+(t3-2*t2+t)*dt*a.outTangent+(-2*t3+3*t2)*b.value+(t3-t2)*dt*b.inTangent;
        }
        return keys[^1].value;
    }
}
public struct Vector2Int(int x, int y) : IEquatable<Vector2Int> {
    public int x=x,y=y;
    public int this[int i] {get=>i switch {0=>x,1=>y,_=>throw new IndexOutOfRangeException()};set {if(i==0)x=value;else if(i==1)y=value;else throw new IndexOutOfRangeException();}}
    public static Vector2Int operator *(int a,Vector2Int b)=>b*a;
    public static Vector2Int zero=>new(0,0); public static Vector2Int one=>new(1,1);
    public static Vector2Int up=>new(0,1); public static Vector2Int down=>new(0,-1); public static Vector2Int left=>new(-1,0); public static Vector2Int right=>new(1,0);
    public static Vector2Int operator +(Vector2Int a,Vector2Int b)=>new(a.x+b.x,a.y+b.y);
    public static Vector2Int operator -(Vector2Int a,Vector2Int b)=>new(a.x-b.x,a.y-b.y);
    public static Vector2Int operator -(Vector2Int a)=>new(-a.x,-a.y);
    public static Vector2Int operator *(Vector2Int a,int b)=>new(a.x*b,a.y*b);
    public static Vector2Int operator /(Vector2Int a,int b)=>new(a.x/b,a.y/b);
    public static bool operator ==(Vector2Int a,Vector2Int b)=>a.Equals(b); public static bool operator !=(Vector2Int a,Vector2Int b)=>!a.Equals(b);
    public bool Equals(Vector2Int b)=>x==b.x&&y==b.y; public override bool Equals(object? o)=>o is Vector2Int b&&Equals(b);
    public override int GetHashCode()=>x^(y<<2)^(y>>30);
    public static Vector2Int Min(Vector2Int a,Vector2Int b)=>new(Math.Min(a.x,b.x),Math.Min(a.y,b.y));
    public static float Distance(Vector2Int a,Vector2Int b)=>MathF.Sqrt((a.x-b.x)*(a.x-b.x)+(a.y-b.y)*(a.y-b.y));
    public override string ToString()=>$"({x}, {y})";
    public static implicit operator Vector2(Vector2Int v)=>new(v.x,v.y);
    public static implicit operator Vector3(Vector2Int v)=>new(v.x,v.y,0);
}
public struct Vector3Int(int x,int y,int z) : IEquatable<Vector3Int>, IFormattable {
    public int x=x,y=y,z=z;
    public int this[int i] {get=>i switch {0=>x,1=>y,2=>z,_=>throw new IndexOutOfRangeException()};set {if(i==0)x=value;else if(i==1)y=value;else if(i==2)z=value;else throw new IndexOutOfRangeException();}}
    public float magnitude=>MathF.Sqrt(x*x+y*y+z*z);
    public static explicit operator Vector3Int(Vector2Int v)=>new(v.x,v.y,0);
    public static Vector3Int zero=>new(0,0,0); public static Vector3Int one=>new(1,1,1);
    public static Vector3Int operator +(Vector3Int a,Vector3Int b)=>new(a.x+b.x,a.y+b.y,a.z+b.z);
    public static Vector3Int operator -(Vector3Int a,Vector3Int b)=>new(a.x-b.x,a.y-b.y,a.z-b.z);
    public static Vector3Int operator *(Vector3Int a,int b)=>new(a.x*b,a.y*b,a.z*b);
    public static bool operator ==(Vector3Int a,Vector3Int b)=>a.Equals(b); public static bool operator !=(Vector3Int a,Vector3Int b)=>!a.Equals(b);
    public bool Equals(Vector3Int b)=>x==b.x&&y==b.y&&z==b.z; public override bool Equals(object? o)=>o is Vector3Int b&&Equals(b);
    public override int GetHashCode()=>x^(y<<4)^(y>>28)^(z>>4)^(z<<28);
    public override string ToString()=>$"({x}, {y}, {z})"; public string ToString(string? format,IFormatProvider? provider)=>ToString();
    public static implicit operator Vector3(Vector3Int v)=>new(v.x,v.y,v.z);
    public static explicit operator Vector2Int(Vector3Int v)=>new(v.x,v.y);
}
public struct Vector2(float x,float y) {
    public float x=x,y=y;
    public float magnitude=>MathF.Sqrt(x*x+y*y); public Vector2 normalized=>magnitude>1e-5f?this/magnitude:new();
    public static Vector2 operator +(Vector2 a,Vector2 b)=>new(a.x+b.x,a.y+b.y);
    public static Vector2 operator -(Vector2 a,Vector2 b)=>new(a.x-b.x,a.y-b.y);
    public static Vector2 operator *(Vector2 a,float b)=>new(a.x*b,a.y*b); public static Vector2 operator /(Vector2 a,float b)=>new(a.x/b,a.y/b);
}
public struct Vector3(float x,float y,float z) {
    public float x=x,y=y,z=z;
    public static Vector3 zero=>new(); public static Vector3 one=>new(1,1,1); public static Vector3 left=>new(-1,0,0); public static Vector3 right=>new(1,0,0); public static Vector3 down=>new(0,-1,0); public static Vector3 forward=>new(0,0,1);
    public float magnitude=>MathF.Sqrt(x*x+y*y+z*z); public Vector3 normalized=>magnitude>1e-5f?this/magnitude:new();
    public static Vector3 operator +(Vector3 a,Vector3 b)=>new(a.x+b.x,a.y+b.y,a.z+b.z);
    public static Vector3 operator -(Vector3 a,Vector3 b)=>new(a.x-b.x,a.y-b.y,a.z-b.z);
    public static Vector3 operator *(float a,Vector3 b)=>b*a;
    public static Vector3 operator *(Vector3 a,float b)=>new(a.x*b,a.y*b,a.z*b); public static Vector3 operator /(Vector3 a,float b)=>new(a.x/b,a.y/b,a.z/b);
    public static Vector3 Lerp(Vector3 a,Vector3 b,float t)=>a+(b-a)*Mathf.Clamp01(t);
    public static float Distance(Vector3 a,Vector3 b)=>(a-b).magnitude;
}
// 模型只在动画状态和效果坐标中使用以下矩阵接口。
public struct Quaternion {
    public static Quaternion identity=>new();
    public static Quaternion Slerp(Quaternion a,Quaternion b,float t)=>new();
    public static Quaternion AngleAxis(float angle,Vector3 axis)=>new();
}
public struct Matrix4x4 {
    private Vector3 position;
    public Quaternion rotation=>Quaternion.identity; public Vector3 lossyScale=>Vector3.one;
    public static Matrix4x4 TRS(Vector3 pos,Quaternion q,Vector3 scale)=>new(){position=pos};
    public static Matrix4x4 Translate(Vector3 pos)=>new(){position=pos};
    public static Matrix4x4 Scale(Vector3 scale)=>new(); public static Matrix4x4 Rotate(Quaternion q)=>new();
    public static Matrix4x4 operator *(Matrix4x4 a,Matrix4x4 b)=>new(){position=a.position+b.position};
    public Vector3 GetPosition()=>position;
    public Matrix4x4 inverse=>throw new NotSupportedException("Headless raycasting is not available");
    public Vector3 MultiplyPoint(Vector3 v)=>throw new NotSupportedException("Headless raycasting is not available");
    public Vector3 MultiplyVector(Vector3 v)=>throw new NotSupportedException("Headless raycasting is not available");
}
public struct Ray(Vector3 origin,Vector3 direction) { public Vector3 origin=origin,direction=direction; }
public struct RectInt(Vector2Int position,Vector2Int size) {
    public Vector2Int position=position,size=size;
    public Vector2Int min {get=>position;set {var oldMax=max;position=value;size=oldMax-position;}}
    public Vector2Int max {get=>position+size;set=>size=value-position;}
    public int xMin=>position.x; public int yMin=>position.y; public int xMax=>max.x; public int yMax=>max.y;
    public int width=>size.x; public int height=>size.y;
    public bool Contains(Vector2Int p)=>p.x>=xMin&&p.y>=yMin&&p.x<xMax&&p.y<yMax;
}
public static class Mathf {
    public static int Min(int a,int b)=>Math.Min(a,b); public static int Min(params int[] v)=>v.Min();
    public static float Min(float a,float b)=>MathF.Min(a,b); public static float Min(params float[] v)=>v.Min();
    public static int Max(int a,int b)=>Math.Max(a,b); public static float Max(float a,float b)=>MathF.Max(a,b);
    public static int Abs(int x)=>Math.Abs(x); public static float Abs(float x)=>MathF.Abs(x);
    public static float Pow(float x,float y)=>MathF.Pow(x,y); public static float Sqrt(float x)=>MathF.Sqrt(x);
    public static float Sign(float x)=>x>=0?1:-1;
    public static int FloorToInt(float x)=>(int)MathF.Floor(x); public static int CeilToInt(float x)=>(int)MathF.Ceiling(x); public static int RoundToInt(float x)=>(int)MathF.Round(x);
    public static float Clamp01(float x)=>Math.Clamp(x,0,1); public static float Lerp(float a,float b,float t)=>a+(b-a)*Clamp01(t);
}
public struct Color32(byte r,byte g,byte b,byte a) {public static implicit operator Color(Color32 c)=>new(c.r/255f,c.g/255f,c.b/255f,c.a/255f); private byte r=r,g=g,b=b,a=a;}
public static class Debug { public static void LogWarning(object message)=>Console.Error.WriteLine(message); public static void LogException(object message)=>throw new InvalidOperationException("Native world generation failed", message as Exception); public static void LogError(object message)=>Console.Error.WriteLine(message); public static void Log(object message)=>Console.Error.WriteLine(message); }
public static class Random { private static System.Random rng=new(0); public static void InitState(int seed)=>rng=new(seed); public static float value=>(float)rng.NextDouble(); public static int Range(int min,int max)=>rng.Next(min,max); }
