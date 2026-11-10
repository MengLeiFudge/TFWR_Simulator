using UnityEngine;

public static class MathUtil {
    public static int FloorDiv(int numerator,int denominator) {
        int quotient=numerator/denominator;
        return numerator%denominator!=0&&((numerator<0)!=(denominator<0))?quotient-1:quotient;
    }
}
// 原版tap()的外部IPC适配器只记次数，不访问操作系统。
public sealed class Ipc {
    public static Ipc Instance {get;}=new();
    public long Count {get;private set;}
    public void Increment()=>Count++;
}
public static class SoundManager { public static Vector3 ZoomAdjustedPosition(Vector3 position)=>position; }
