using System;
using System.CodeDom.Compiler;
using System.Collections;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Collections.Generic.Integrations;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using Steamworks;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Events;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: AssemblyVersion("0.0.0.0")]
public static class Achievements
{
	private struct ItemAddition
	{
		public int itemId;

		public double number;

		public Duration time;

		public ItemAddition(int itemId, double number, Duration time)
		{
			this.itemId = itemId;
			this.number = number;
			this.time = time;
		}
	}

	private static readonly Duration COLLECTIION_TIME_THRESHOLD = Duration.FromSeconds(1.0);

	private static readonly Duration MEASURE_INTERVAL = Duration.FromSeconds(60.0);

	private const int STATS_VERSION = 3;

	private static ItemBlock best;

	private static ItemBlock sum;

	private static ItemBlock total_stats;

	private static Deque<ItemAddition> window = new Deque<ItemAddition>();

	private static HashSet<string> unlockedAchievements = new HashSet<string>();

	private static HashSet<int> unlockedItemHats = new HashSet<int>();

	private static int richPresenceItemId = -1;

	private static object lockObject = new object();

	public static volatile bool enabled = true;

	public static string RichPresenceDisplay { get; set; } = null;

	public static string RichPresenceQuantity { get; set; } = null;

	public static void LoadStats()
	{
		lock (lockObject)
		{
			window.Clear();
			best = ItemBlock.CreateEmpty();
			sum = ItemBlock.CreateEmpty();
			total_stats = ItemBlock.CreateEmpty();
			if (!SteamManager.Initialized || !best.IsEmpty())
			{
				return;
			}
			SteamUserStats.RequestCurrentStats();
			SteamUserStats.GetStat("version", out int pData);
			if (pData != 3)
			{
				SteamUserStats.ResetAllStats(bAchievementsToo: false);
				SteamUserStats.SetStat("version", 3);
				SteamUserStats.StoreStats();
			}
			ItemSO[] array = Resources.LoadAll<ItemSO>("Items/");
			foreach (ItemSO itemSO in array)
			{
				if (itemSO.trackStats)
				{
					SteamUserStats.GetStat(itemSO.itemName, out int pData2);
					best.AddItem(itemSO.itemId, pData2);
					UnlockGoldenHats(itemSO.itemName, pData2);
					SteamUserStats.GetStat("total_" + itemSO.itemName, out int pData3);
					total_stats.AddItem(itemSO.itemId, pData3);
					UnlockFarmHats(itemSO.itemId);
				}
			}
			SteamFriends.SetRichPresence("steam_display", "#default_status");
		}
	}

	public static ItemBlock GetBest()
	{
		lock (lockObject)
		{
			return new ItemBlock(best);
		}
	}

	public static ItemBlock GetSum()
	{
		lock (lockObject)
		{
			return new ItemBlock(sum);
		}
	}

	public static void CollectItem(int itemId, double number, Duration currentTime, Duration collectionDuration)
	{
		if (!enabled)
		{
			return;
		}
		lock (lockObject)
		{
			double n = number;
			if (collectionDuration > MEASURE_INTERVAL)
			{
				number = ScaleNumberToNewDuration(number, collectionDuration, MEASURE_INTERVAL);
				collectionDuration = MEASURE_INTERVAL;
			}
			if (collectionDuration > COLLECTIION_TIME_THRESHOLD)
			{
				int num = (int)(collectionDuration / COLLECTIION_TIME_THRESHOLD);
				double number2 = number / (double)num;
				Duration duration = currentTime;
				for (int i = 0; i < num; i++)
				{
					ItemAddition item = new ItemAddition(itemId, number2, duration);
					duration -= COLLECTIION_TIME_THRESHOLD;
					int j;
					for (j = 0; j < window.Count && window[j].time > duration; j++)
					{
					}
					window.Insert(j, item);
				}
			}
			else
			{
				window.Enqueue(new ItemAddition(itemId, number, currentTime));
			}
			sum.AddItem(itemId, number);
			UpdateSum(currentTime);
			double number3 = sum.GetNumber(itemId);
			if (number3 > best.GetNumber(itemId))
			{
				best.AddItem(itemId, number3 - best.GetNumber(itemId));
				string itemName = StringIds.GetItemName(itemId);
				if (SteamManager.Initialized)
				{
					SteamUserStats.SetStat(itemName, (int)number3);
				}
				UnlockGoldenHats(itemName, number3);
			}
			total_stats.AddItem(itemId, n);
			if (SteamManager.Initialized)
			{
				string itemName2 = StringIds.GetItemName(itemId);
				SteamUserStats.SetStat("total_" + itemName2, (int)total_stats.GetNumber(itemId));
			}
			UnlockFarmHats(itemId);
			UpdateRichPresence(itemId);
		}
	}

	public static void UnlockGoldenHats(string itemName, double newTotal)
	{
		switch (itemName)
		{
		case "carrot":
			if (newTotal >= 200000000.0)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("golden_carrot_hat"));
			}
			break;
		case "cactus":
			if (newTotal >= 20000000.0)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("golden_cactus_hat"));
			}
			break;
		case "gold":
			if (newTotal >= 2000000.0)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("golden_gold_hat"));
			}
			break;
		case "wood":
			if (newTotal >= 1000000000.0)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("golden_tree_hat"));
			}
			break;
		case "pumpkin":
			if (newTotal >= 20000000.0)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("golden_pumpkin_hat"));
			}
			break;
		case "power":
			if (newTotal >= 12000.0)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("golden_sunflower_hat"));
			}
			break;
		}
	}

	public static void UnlockFarmHats(int itemId)
	{
		if (!(total_stats.GetNumber(itemId) < 1000.0) && !unlockedItemHats.Contains(itemId))
		{
			unlockedItemHats.Add(itemId);
			switch (StringIds.GetItemName(itemId))
			{
			case "carrot":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("carrot_hat"));
				break;
			case "cactus":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("cactus_hat"));
				break;
			case "gold":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("gold_hat"));
				break;
			case "wood":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("tree_hat"));
				break;
			case "pumpkin":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("pumpkin_hat"));
				break;
			case "power":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("sunflower_hat"));
				break;
			}
		}
	}

	public static void IncrementStat(string statName, int increment)
	{
		if (!enabled)
		{
			return;
		}
		lock (lockObject)
		{
			if (SteamManager.Initialized)
			{
				SteamUserStats.GetStat(statName, out int pData);
				pData += increment;
				SteamUserStats.SetStat(statName, pData);
			}
		}
	}

	private static double ScaleNumberToNewDuration(double number, Duration oldDuration, Duration newDuration)
	{
		return Math.Max(0.0, number * (newDuration / oldDuration));
	}

	public static void UpdateSum(Duration currentTime)
	{
		lock (lockObject)
		{
			while (window.Count > 0 && currentTime - window.Peek().time > MEASURE_INTERVAL)
			{
				ItemAddition itemAddition = window.Dequeue();
				if (!sum.RemoveItem(itemAddition.itemId, itemAddition.number))
				{
					sum.SetNumber(itemAddition.itemId, 0.0);
				}
			}
		}
	}

	public static void UnlockAchievement(string achievement)
	{
		if (!enabled)
		{
			return;
		}
		lock (lockObject)
		{
			if (!unlockedAchievements.Contains(achievement))
			{
				unlockedAchievements.Add(achievement);
				switch (achievement)
				{
				case "CAUSE_A_RUNTIME_ERROR":
					MainSim.Inst.UnlockHat(ResourceManager.GetHat("traffic_cone"));
					break;
				case "STACK_OVERFLOW":
					MainSim.Inst.UnlockHat(ResourceManager.GetHat("traffic_cone_stack"));
					break;
				case "HIGHER_ORDER_PROGRAMMING":
					MainSim.Inst.UnlockHat(ResourceManager.GetHat("wizard_hat"));
					break;
				}
				if (SteamManager.Initialized)
				{
					SteamUserStats.SetAchievement(achievement);
					SteamUserStats.StoreStats();
				}
			}
		}
	}

	public static void UpdateRichPresence(int itemId)
	{
		if (SteamManager.Initialized && (richPresenceItemId < 0 || !(sum.GetNumber(richPresenceItemId) > sum.GetNumber(itemId))))
		{
			string itemName = StringIds.GetItemName(itemId);
			RichPresenceDisplay = "#farming_" + itemName;
			RichPresenceQuantity = ((long)sum.GetNumber(itemId)).ToString();
			richPresenceItemId = itemId;
		}
	}
}
public class CheatConsole : MonoBehaviour
{
	private bool showConsole;

	private string input;

	private void OnGUI()
	{
		if (showConsole)
		{
			GUI.Box(new Rect(0f, Screen.height - 25, Screen.width, 25f), "");
			GUI.backgroundColor = new Color(0f, 0f, 0f, 0f);
			input = GUI.TextField(new Rect(5f, (float)Screen.height - 23f, (float)Screen.width - 10f, 21f), input);
		}
	}

	private void Update()
	{
		if (showConsole && Input.GetKeyDown(KeyCode.Return))
		{
			InvokeCommand();
			input = "";
		}
	}

	private void InvokeCommand()
	{
		if (input == "aint nobody got time for this")
		{
			ToggleFastMode();
		}
	}

	private void GetRichQuickly()
	{
		foreach (UnlockSO allUnlock in ResourceManager.GetAllUnlocks())
		{
			MainSim.Inst.UnlockOrUpgrade(allUnlock);
		}
	}

	private void ToggleFastMode()
	{
		if (MainSim.Inst.harvestFactor == 1)
		{
			MainSim.Inst.harvestFactor = 10;
		}
		else
		{
			MainSim.Inst.harvestFactor = 1;
		}
	}
}
public class Apple : Growable
{
	public Vector2Int nextPos;

	private bool hasNextPos;

	public override bool Harvestable => false;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		collectionDuration = default(Duration);
		return ItemBlock.CreateEmpty();
	}

	public override IPyObject Measure()
	{
		if (hasNextPos)
		{
			return new PyTuple(new List<IPyObject>
			{
				new PyNumber(nextPos.x),
				new PyNumber(nextPos.y)
			});
		}
		return new PyNone();
	}

	public void ChooseTarget()
	{
		if (sim.farm.grid.WorldSize.y > 1)
		{
			GridManager grid = sim.farm.grid;
			FarmObject valueOrDefault;
			do
			{
				nextPos = new Vector2Int(sim.randomSnake.Next(sim.farm.grid.WorldSize.x), sim.randomSnake.Next(0, sim.farm.grid.WorldSize.y));
				valueOrDefault = grid.entities.GetValueOrDefault(nextPos);
			}
			while (valueOrDefault is Dinosaur || valueOrDefault is Apple);
			hasNextPos = true;
		}
	}
}
public class BushPlant : Growable
{
	public void GenerateHedgeMaze(int desired_size)
	{
		int num = Mathf.Min(desired_size, sim.farm.grid.WorldSize.x);
		Vector2Int vector2Int = Vector2Int.Max(Vector2Int.zero, pos - new Vector2Int(num / 2, num / 2));
		while (vector2Int.x + num > sim.farm.grid.WorldSize.x)
		{
			vector2Int.x--;
		}
		while (vector2Int.y + num > sim.farm.grid.WorldSize.y)
		{
			vector2Int.y--;
		}
		bool[][] array = new bool[num * num][];
		int num2 = sim.randomMaze.Next(num * num);
		array[num2] = new bool[4] { true, true, true, true };
		List<int> list = new List<int> { num2 };
		bool flag = false;
		List<int> list2 = new List<int>();
		while (list.Count > 0)
		{
			int num3 = list[list.Count - 1];
			int num4 = num3 % num;
			int num5 = num3 / num;
			foreach (GridDirection item in ((GridDirection[])Enum.GetValues(typeof(GridDirection))).OrderBy((GridDirection k) => sim.randomMaze.Next()))
			{
				Vector2Int directionVector = item.GetDirectionVector();
				int num6 = num4 + directionVector.x;
				int num7 = num5 + directionVector.y;
				if (num6 >= 0 && num7 >= 0 && num6 < num && num7 < num && array[num6 + num * num7] == null)
				{
					list.Add(num6 + num * num7);
					array[num6 + num * num7] = new bool[4] { true, true, true, true };
					array[num6 + num * num7][(int)item.Reverse()] = false;
					array[num3][(int)item] = false;
					flag = false;
					break;
				}
			}
			if (list[list.Count - 1] == num3)
			{
				list.RemoveAt(list.Count - 1);
				if (!flag)
				{
					list2.Add(num3);
					flag = true;
				}
			}
		}
		int num8 = list2[sim.randomMaze.Next(list2.Count - 1)];
		for (int num9 = 0; num9 < num; num9++)
		{
			for (int num10 = 0; num10 < num; num10++)
			{
				bool flag2 = num8 == num9 + num * num10;
				sim.farm.grid.SetGround(new Vector2Int(num9, num10) + vector2Int, "grassland");
				HedgePlant hedgePlant = (HedgePlant)sim.farm.grid.SetEntity(new Vector2Int(num9, num10) + vector2Int, flag2 ? "treasure" : "hedge");
				hedgePlant.walls = array[num9 + num * num10];
				hedgePlant.lowLeftCorner = vector2Int;
				hedgePlant.mazeSize = num;
				if (flag2)
				{
					((Treasure)hedgePlant).ChooseNextPosition();
				}
			}
		}
		if (sim.leaderboardType == LeaderboardType.none)
		{
			Achievements.UnlockAchievement("SPAWN_MAZE");
		}
	}
}
public class Cactus : Growable
{
	private int number;

	private bool isPopped;

	private Duration plantTime;

	protected override double YieldFactor => base.YieldFactor;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		collectionDuration = sim.CurrentTime - plantTime;
		if (!Harvestable)
		{
			HarvestEffects();
			sim.farm.grid.RemoveEntity(pos);
			return ItemBlock.CreateEmpty();
		}
		List<Cactus> list = new List<Cactus>();
		int numWeird = 0;
		Pop(list, ref numWeird);
		int count = list.Count;
		foreach (Cactus item in list)
		{
			sim.farm.grid.RemoveEntity(item.pos);
		}
		return GetDrops(count, numWeird);
	}

	protected override void OnFullyGrown()
	{
		base.OnFullyGrown();
		sim.farm.grid.cactusNumbers[pos.x, pos.y] = -1;
		CheckWrongOrderAchievement();
	}

	public override void OnSwapped()
	{
		base.OnSwapped();
		CheckWrongOrderAchievement();
	}

	private void CheckWrongOrderAchievement()
	{
		if (sim.leaderboardType == LeaderboardType.none && sim.farm.grid.entities.Count == sim.farm.grid.WorldSize.x * sim.farm.grid.WorldSize.y && IsReverseSorted() && sim.farm.grid.entities.Values.OfType<Cactus>().All((Cactus c) => c.IsReverseSorted()) && sim.farm.grid.entities.Values.OfType<Cactus>().Count() == sim.farm.grid.WorldSize.x * sim.farm.grid.WorldSize.y)
		{
			Achievements.UnlockAchievement("WRONG_ORDER");
		}
	}

	public override ItemBlock GetYield()
	{
		CountSorted(out var count, out var numWeird);
		return GetDrops(count, numWeird);
	}

	private ItemBlock GetDrops(int numPopped, int numWeird)
	{
		double num = YieldFactor * (double)numPopped;
		double num2 = Math.Floor(0.5 * (double)numWeird * num);
		double n = (double)numPopped * num - num2;
		ItemBlock itemBlock = new ItemBlock(StringIds.CactusItemId, n);
		if (num2 > 0.0)
		{
			itemBlock.AddItem(StringIds.WeirdSubstanceItemId, num2);
		}
		return itemBlock;
	}

	private void Pop(List<Cactus> popped, ref int numWeird)
	{
		if (isPopped || !Harvestable)
		{
			return;
		}
		isPopped = true;
		popped.Add(this);
		if (weird)
		{
			numWeird++;
		}
		HarvestEffects();
		FarmObject[] neighbors = sim.farm.grid.GetNeighbors(pos);
		if (neighbors.All((FarmObject f) => !(f is Cactus cactus) || cactus.IsSorted()))
		{
			FarmObject[] array = neighbors;
			for (int num = 0; num < array.Length; num++)
			{
				(array[num] as Cactus)?.Pop(popped, ref numWeird);
			}
		}
	}

	private void CountSorted(out int count, out int numWeird)
	{
		if (!IsSorted())
		{
			count = 0;
			numWeird = 0;
			return;
		}
		numWeird = 0;
		HashSet<Vector2Int> hashSet = new HashSet<Vector2Int>();
		List<Vector2Int> list = new List<Vector2Int> { pos };
		while (list.Count > 0)
		{
			Vector2Int vector2Int = list[list.Count - 1];
			list.RemoveAt(list.Count - 1);
			if (!hashSet.Contains(vector2Int) && sim.farm.grid.entities.TryGetValue(vector2Int, out var value) && value is Cactus { Harvestable: not false } cactus && cactus.IsSorted())
			{
				hashSet.Add(vector2Int);
				if (cactus.weird)
				{
					numWeird++;
				}
				Vector2Int[] array = sim.farm.grid.NeighborPositions(vector2Int);
				foreach (Vector2Int item in array)
				{
					list.Add(item);
				}
			}
		}
		count = hashSet.Count;
	}

	private bool IsSorted()
	{
		FarmObject[] neighbors = sim.farm.grid.GetNeighbors(pos);
		if (neighbors.Take(2).All((FarmObject f) => !(f is Cactus cactus) || (cactus.Harvestable && cactus.number >= number)))
		{
			return neighbors.Skip(2).All((FarmObject f) => !(f is Cactus cactus) || (cactus.Harvestable && cactus.number <= number));
		}
		return false;
	}

	private bool IsReverseSorted()
	{
		FarmObject[] neighbors = sim.farm.grid.GetNeighbors(pos);
		if (neighbors.Take(2).All((FarmObject f) => !(f is Cactus cactus) || (cactus.Harvestable && cactus.number <= number)))
		{
			return neighbors.Skip(2).All((FarmObject f) => !(f is Cactus cactus) || (cactus.Harvestable && cactus.number >= number));
		}
		return false;
	}

	public override IPyObject Measure()
	{
		return new PyNumber(number);
	}

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		Matrix4x4 transform = GetTransform();
		yield return (objectSO.meshes[(!Harvestable || IsSorted()) ? number : (10 + number)], transform);
		if (weird)
		{
			yield return (objectSO.gooMeshes[gooIndex], Matrix4x4.Translate(GridManager.CellToLocal(pos)));
		}
	}

	public override void OnRestart()
	{
		base.OnRestart();
		if (sim.farm.grid.cactusNumbers[pos.x, pos.y] == -1)
		{
			sim.farm.grid.cactusNumbers[pos.x, pos.y] = sim.randomCactus.Next(10);
		}
		number = sim.farm.grid.cactusNumbers[pos.x, pos.y];
		isPopped = false;
		plantTime = sim.CurrentTime;
	}
}
public class DeadPumpkin : FarmObject
{
	public override bool Harvestable => false;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		sim.farm.grid.RemoveEntity(pos);
		return base.Harvest(out collectionDuration);
	}
}
public class Dinosaur : FarmObject
{
	public bool isInSnake = true;

	public bool canMoveTo;

	public Drone drone;

	public void FirstTailAnim(double ops)
	{
		scaleStart = new Vector3(1f, 0f, 1f);
		scaleEnd = Vector3.one;
		scaleDuration = sim.GetActionTime(ops);
		scaleEndTime = sim.CurrentTime + scaleDuration;
		Vector3 localPosition = base.LocalPosition;
		Vector3 vector = GridManager.CellToLocal(pos + base.Orientation.Reverse().GetDirectionVector()) - localPosition;
		positionStart = localPosition + 0.9f * vector;
		positionEnd = localPosition;
		moveDuration = scaleDuration;
		moveEndTime = sim.CurrentTime + scaleDuration;
	}

	public void LastTailAnim(double ops)
	{
		scaleEnd = new Vector3(1f, 0f, 1f);
		scaleStart = Vector3.one;
		scaleDuration = sim.GetActionTime(ops);
		scaleEndTime = sim.CurrentTime + scaleDuration;
		Vector3 localPosition = base.LocalPosition;
		Vector3 vector = GridManager.CellToLocal(pos + base.Orientation.GetDirectionVector()) - localPosition;
		positionStart = localPosition;
		positionEnd = localPosition + 0.1f * vector;
		moveDuration = scaleDuration;
		moveEndTime = sim.CurrentTime + scaleDuration;
	}

	public void DoubleTailAnim()
	{
		scaleEnd = new Vector3(0f, 0f, 0f);
	}

	public override bool CanDroneMoveToFrom(GridDirection direction)
	{
		return canMoveTo;
	}

	public override void OnRestart()
	{
		base.OnRestart();
		if (!(sim.farm.grid.grounds[pos] is Soil))
		{
			sim.farm.grid.SetGround(pos, "soil");
		}
	}

	public override void OnFree()
	{
		base.OnFree();
		if (isInSnake && drone.hat.hatSO.hatName == "dinosaur_hat")
		{
			drone.ChangeHat(ResourceManager.GetHat("straw_hat"), null);
		}
	}

	public override ItemBlock GetYield()
	{
		if (!isInSnake || !(drone.hat is DinosaurHat dinosaurHat))
		{
			return base.GetYield();
		}
		ItemBlock itemBlock = ItemBlock.CreateEmpty();
		itemBlock.AddItem(StringIds.BoneItemId, dinosaurHat.BoneCount());
		return itemBlock;
	}
}
public class FarmObject
{
	public FarmObjectSO objectSO;

	public Vector2Int pos;

	private GridDirection orientation;

	protected Quaternion rotationStart;

	protected Quaternion rotationEnd = Quaternion.identity;

	protected Duration rotationDuration;

	protected Duration rotationEndTime;

	protected Vector3 positionStart;

	protected Vector3 positionEnd = Vector3.zero;

	protected Duration moveDuration;

	protected Duration moveEndTime;

	protected Vector3 scaleStart;

	protected Vector3 scaleEnd = Vector3.one;

	protected Duration scaleDuration;

	protected Duration scaleEndTime;

	[NonSerialized]
	public Simulation sim;

	public GridDirection Orientation
	{
		get
		{
			return orientation;
		}
		set
		{
			orientation = value;
			rotationEnd = orientation.GetQuaternion();
		}
	}

	public virtual bool Harvestable => true;

	public Vector3 LocalPosition
	{
		get
		{
			if (moveEndTime > sim.CurrentTime)
			{
				float t = 1f - (float)((moveEndTime - sim.CurrentTime) / moveDuration);
				return Vector3.Lerp(positionStart, positionEnd, t);
			}
			return positionEnd;
		}
		set
		{
			positionEnd = value;
		}
	}

	protected virtual double YieldFactor => Math.Max(1 << sim.farm.NumUnlocked(objectSO.yieldUpgradeName) - 1, 1) * MainSim.Inst.harvestFactor;

	public void AnimateMove(Vector3 destination, Duration duration)
	{
		positionStart = LocalPosition;
		positionEnd = destination;
		moveDuration = duration;
		moveEndTime = sim.CurrentTime + duration;
	}

	public void AnimateRotation(GridDirection destination, Duration duration)
	{
		rotationStart = rotationEnd;
		Orientation = destination;
		rotationDuration = duration;
		rotationEndTime = sim.CurrentTime + duration;
	}

	public Matrix4x4 GetTransform()
	{
		Vector3 vector = positionEnd;
		Vector3 s = scaleEnd;
		if (moveEndTime > sim.CurrentTime)
		{
			float t = 1f - (float)((moveEndTime - sim.CurrentTime) / moveDuration);
			vector = Vector3.Lerp(positionStart, positionEnd, t);
		}
		if (scaleEndTime > sim.CurrentTime)
		{
			float t2 = 1f - (float)((scaleEndTime - sim.CurrentTime) / scaleDuration);
			s = Vector3.Lerp(scaleStart, scaleEnd, t2);
		}
		Quaternion q;
		if (rotationEndTime > sim.CurrentTime)
		{
			float t3 = 1f - (float)((rotationEndTime - sim.CurrentTime) / rotationDuration);
			q = Quaternion.Slerp(rotationStart, rotationEnd, t3);
		}
		else
		{
			q = rotationEnd;
		}
		if (s.x == 0f || s.y == 0f || s.z == 0f)
		{
			s = Vector3.zero;
		}
		return Matrix4x4.TRS(vector, q, s);
	}

	public virtual IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		yield return (objectSO.meshes[0], GetTransform());
	}

	public virtual ItemBlock GetYield()
	{
		return null;
	}

	public virtual ItemBlock Harvest(out Duration collectionDuration)
	{
		collectionDuration = Duration.FromSeconds(0.0);
		return null;
	}

	public virtual void OnFree()
	{
	}

	public virtual void OnRestart()
	{
		if (objectSO.randomRotation)
		{
			Orientation = GridDirectionMethods.RandomGridDirection(sim.randomVarious);
		}
		else
		{
			Orientation = GridDirection.South;
		}
	}

	public virtual void OnPlanted(Drone drone)
	{
	}

	public virtual void UpdateFarmObject()
	{
	}

	public virtual IPyObject Measure()
	{
		return null;
	}

	public void UpdateNeighbors()
	{
		FarmObject[] neighbors = sim.farm.grid.GetNeighbors(pos);
		for (int i = 0; i < neighbors.Length; i++)
		{
			neighbors[i]?.UpdateFarmObject();
		}
	}

	public virtual bool CanDroneMoveToFrom(GridDirection direction)
	{
		return true;
	}

	public virtual bool CanDroneMoveAwayTo(GridDirection direction)
	{
		return true;
	}

	public virtual string ToSerializeString()
	{
		return "type = " + objectSO.objectName;
	}

	public virtual void SetValues(Dictionary<string, string> values)
	{
	}

	public virtual void OnSwapped()
	{
	}

	public override string ToString()
	{
		return "Entities." + CodeUtilities.ToUpperSnake(objectSO.objectName);
	}

	public void HarvestEffects(bool addStars = false)
	{
		if (sim.mainSim != null && sim.mainSim.TimeFactor == 1.0)
		{
			Vector3 localPosition = LocalPosition;
			sim.mainSim.PlayEffect(VFXType.dust, localPosition);
			sim.mainSim.PlayEffect(VFXType.hit, localPosition, changeColor: true, objectSO.color);
			if (addStars)
			{
				sim.mainSim.PlayEffect(VFXType.stars, localPosition);
			}
		}
	}
}
[CreateAssetMenu(fileName = "FarmObject", menuName = "ScriptableObjects/FarmObject", order = 1)]
public class FarmObjectSO : ScriptableObject, IPyObject
{
	[Header("Farm Object")]
	public string className;

	public bool isGround;

	public string objectName;

	public string description;

	public string docs;

	public Color color;

	public List<Mesh> meshes;

	public List<Mesh> gooMeshes;

	public bool canBeSwapped;

	public List<string> placeableOn;

	public SoundEffectType harvestSound;

	[Header("Growable")]
	public bool verticalGrowth;

	public float meanGrowTime;

	public float growTimeDeviationPercent;

	public bool canHaveCompanion;

	public bool randomRotation = true;

	public bool canBePlanted = true;

	public bool canBeOverplanted;

	[Header("Drops")]
	public string dropItem;

	[NonSerialized]
	public int dropItemId;

	public double dropAmount = 1.0;

	public string yieldUpgradeName;

	public ItemBlock cost;

	public IPyObject DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}

	public string GetDescription()
	{
		if (meanGrowTime > 0f && className != "Apple")
		{
			float num = meanGrowTime * (1f - growTimeDeviationPercent);
			float num2 = meanGrowTime * (1f + growTimeDeviationPercent);
			return string.Format(Localizer.Localize("plant_tooltip_template"), Localizer.Localize(description), num, num2, string.Join(" or ", placeableOn));
		}
		return Localizer.Localize(description);
	}

	public override string ToString()
	{
		if (isGround)
		{
			return "Grounds." + CodeUtilities.ToUpperSnake(objectName);
		}
		return "Entities." + CodeUtilities.ToUpperSnake(objectName);
	}
}
public class Ground : FarmObject
{
	public override string ToString()
	{
		return "Grounds." + CodeUtilities.ToUpperSnake(objectSO.objectName);
	}
}
public class Growable : FarmObject
{
	private bool isGrown;

	private Duration growTime;

	private double prevGrowTimeFactor = 1.0;

	private Duration growStart;

	private double grownPercent;

	private float randomFactor;

	public bool canBePlanted = true;

	public List<string> growsOn;

	private FarmObjectSO companionType;

	private Vector2Int companionPos;

	public bool weird;

	protected int gooIndex;

	private Simulation.Timer growTimer;

	public Duration GrowTime => growTime;

	public double GrownPercent
	{
		get
		{
			if (!isGrown)
			{
				return grownPercent + (sim.CurrentTime - growStart) / growTime;
			}
			return 1.0;
		}
	}

	public override bool Harvestable => isGrown;

	public float MeanGrowTime => objectSO.meanGrowTime;

	protected virtual double GrowTimeFactor
	{
		get
		{
			double num = 1.0;
			if (sim.farm.grid.grounds[pos] is Ground)
			{
				num += sim.farm.grid.waterVolume[pos.x, pos.y] * 4.0;
			}
			return 1.0 / num;
		}
	}

	protected override double YieldFactor => base.YieldFactor * (double)((!HasCompanion()) ? 1 : (5 << sim.farm.NumUnlocked("polyculture")));

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		foreach (var mesh in base.GetMeshes())
		{
			yield return mesh;
		}
		if (weird)
		{
			yield return (objectSO.gooMeshes[gooIndex], Matrix4x4.Translate(GridManager.CellToLocal(pos)));
		}
	}

	public void Grow()
	{
		isGrown = true;
		scaleEnd = Vector3.one;
		OnFullyGrown();
		UpdateNeighbors();
	}

	public override void UpdateFarmObject()
	{
		base.UpdateFarmObject();
		if (prevGrowTimeFactor != GrowTimeFactor)
		{
			TryScheduleGrow();
		}
	}

	private void TryScheduleGrow()
	{
		if (isGrown)
		{
			return;
		}
		StopGrowing();
		growTime = GetGrowTime();
		growStart = sim.CurrentTime;
		Duration duration = growTime * (1.0 - grownPercent);
		if (duration.nanoseconds == 0L)
		{
			Grow();
			return;
		}
		growTimer = sim.StartTimer(Grow, duration);
		float num = (float)grownPercent * 0.9f + 0.1f;
		if (objectSO.verticalGrowth)
		{
			scaleStart = new Vector3(1f, 1f, num);
		}
		else
		{
			scaleStart = Vector3.one * num;
		}
		scaleEnd = Vector3.one;
		scaleDuration = duration;
		scaleEndTime = sim.CurrentTime + duration;
	}

	private Duration GetGrowTime()
	{
		prevGrowTimeFactor = GrowTimeFactor;
		return Duration.FromSeconds(prevGrowTimeFactor * (double)objectSO.meanGrowTime * (double)randomFactor);
	}

	protected virtual void OnFullyGrown()
	{
	}

	public void StopGrowing()
	{
		if (!isGrown)
		{
			if (growTimer != null)
			{
				growTimer.stopped = true;
			}
			grownPercent += (sim.CurrentTime - growStart) / growTime;
		}
	}

	public override ItemBlock GetYield()
	{
		ItemBlock itemBlock = ItemBlock.CreateEmpty();
		if (objectSO.dropAmount <= 0.0)
		{
			return itemBlock;
		}
		double num = objectSO.dropAmount * YieldFactor;
		if (weird)
		{
			num *= 0.5;
			itemBlock.AddItem(StringIds.WeirdSubstanceItemId, Math.Truncate(num));
			num = Math.Ceiling(num);
		}
		itemBlock.AddItem(objectSO.dropItemId, num);
		return itemBlock;
	}

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		base.Harvest(out collectionDuration);
		ItemBlock result = (Harvestable ? GetYield() : ItemBlock.CreateEmpty());
		sim.farm.grid.RemoveEntity(pos);
		HarvestEffects(HasCompanion());
		return result;
	}

	public void Fertilize(int number)
	{
		weird = true;
		if (!isGrown)
		{
			StopGrowing();
			grownPercent = Math.Min(grownPercent + Duration.FromSeconds(2 * number) / GetGrowTime(), 1.0);
			TryScheduleGrow();
		}
	}

	public void ToggleWeird()
	{
		weird = !weird;
		gooIndex = sim.randomVarious.Next(objectSO.gooMeshes.Count - 1);
		bool flag = !weird;
		FarmObject[] neighbors = sim.farm.grid.GetNeighbors(pos);
		for (int i = 0; i < neighbors.Length; i++)
		{
			if (neighbors[i] is Growable growable)
			{
				growable.weird = !growable.weird;
				growable.gooIndex = sim.randomVarious.Next(growable.objectSO.gooMeshes.Count - 1);
				flag = flag || !growable.weird;
			}
		}
		if (sim.leaderboardType == LeaderboardType.none && flag)
		{
			Achievements.UnlockAchievement("HEALER");
		}
	}

	private bool HasCompanion()
	{
		if (!objectSO.canHaveCompanion || !sim.farm.grid.entities.ContainsKey(companionPos))
		{
			return false;
		}
		if (sim.farm.grid.entities[companionPos].objectSO.objectName == companionType.objectName)
		{
			return true;
		}
		return false;
	}

	public IPyObject GetCompanion()
	{
		if (!objectSO.canHaveCompanion)
		{
			return new PyNone();
		}
		return new PyTuple(new List<IPyObject>
		{
			companionType,
			new PyTuple(new List<IPyObject>
			{
				new PyNumber(companionPos.x),
				new PyNumber(companionPos.y)
			})
		});
	}

	private void ChooseCompanion()
	{
		int num = 3;
		do
		{
			companionPos = new Vector2Int(sim.randomPoly.Next(-num, num + 1), sim.randomPoly.Next(-num, num + 1));
		}
		while ((sim.farm.grid.Wrap(pos + companionPos) == pos || Mathf.Abs(companionPos.x) + Mathf.Abs(companionPos.y) > num) && sim.farm.grid.WorldSize.y != 1);
		companionPos = sim.farm.grid.Wrap(pos + companionPos);
		do
		{
			companionType = sim.randomPoly.Next(4) switch
			{
				2 => ResourceManager.GetFarmObject("carrot"), 
				1 => ResourceManager.GetFarmObject("bush"), 
				0 => ResourceManager.GetFarmObject("grass"), 
				_ => ResourceManager.GetFarmObject("tree"), 
			};
		}
		while (companionType.objectName == objectSO.objectName);
	}

	public override void OnFree()
	{
		base.OnFree();
		StopGrowing();
	}

	public override void OnRestart()
	{
		base.OnRestart();
		gooIndex = sim.randomVarious.Next(objectSO.gooMeshes.Count - 1);
		if (objectSO.canHaveCompanion)
		{
			ChooseCompanion();
		}
		isGrown = false;
		growStart = sim.CurrentTime;
		grownPercent = 0.0;
		randomFactor = (float)sim.randomVarious.NextDouble() * objectSO.growTimeDeviationPercent * 2f + 1f - objectSO.growTimeDeviationPercent;
		growTime = GetGrowTime();
		weird = false;
		TryScheduleGrow();
	}

	public override void SetValues(Dictionary<string, string> values)
	{
		base.SetValues(values);
		StopGrowing();
		if (values.ContainsKey("grown percent") && double.TryParse(values["grown percent"], NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture, out var result))
		{
			grownPercent = result;
		}
		TryScheduleGrow();
	}

	public override string ToSerializeString()
	{
		return $"{base.ToSerializeString()},grown percent = {grownPercent + (sim.CurrentTime - growStart) / growTime}";
	}
}
public class HedgePlant : FarmObject
{
	public bool[] walls;

	public int mazeSize;

	public Vector2Int lowLeftCorner;

	public bool removed;

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		for (int i = 0; i < 4; i++)
		{
			if (walls[i] && (i < 2 || pos.x == lowLeftCorner.x || pos.y == lowLeftCorner.y))
			{
				Quaternion q = Quaternion.AngleAxis(90 * i, Vector3.forward);
				yield return (objectSO.meshes[0], Matrix4x4.TRS(positionEnd, q, Vector3.one));
			}
		}
	}

	private void RemoveMaze()
	{
		if (removed)
		{
			return;
		}
		for (int i = 0; i < mazeSize; i++)
		{
			for (int j = 0; j < mazeSize; j++)
			{
				Vector2Int key = new Vector2Int(i, j) + lowLeftCorner;
				if (sim.farm.grid.entities.GetValueOrDefault(key) is HedgePlant { removed: false } hedgePlant)
				{
					hedgePlant.removed = true;
					sim.farm.grid.RemoveEntity(key);
				}
			}
		}
	}

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		RemoveMaze();
		HarvestEffects();
		return base.Harvest(out collectionDuration);
	}

	public override bool CanDroneMoveToFrom(GridDirection direction)
	{
		return !walls[(int)direction];
	}

	public override bool CanDroneMoveAwayTo(GridDirection direction)
	{
		return !walls[(int)direction];
	}

	public override string ToSerializeString()
	{
		return $"{base.ToSerializeString()},north = {walls[0]},east = {walls[1]},south = {walls[2]},west = {walls[3]}";
	}

	public override void SetValues(Dictionary<string, string> values)
	{
		base.SetValues(values);
		walls = new bool[4];
		if (values.ContainsKey("north") && bool.TryParse(values["north"], out var result))
		{
			walls[0] = result;
		}
		if (values.ContainsKey("east") && bool.TryParse(values["east"], out var result2))
		{
			walls[1] = result2;
		}
		if (values.ContainsKey("south") && bool.TryParse(values["south"], out var result3))
		{
			walls[2] = result3;
		}
		if (values.ContainsKey("west") && bool.TryParse(values["west"], out var result4))
		{
			walls[3] = result4;
		}
	}

	public override void OnFree()
	{
		base.OnFree();
		RemoveMaze();
	}

	public override IPyObject Measure()
	{
		for (int i = lowLeftCorner.x; i < lowLeftCorner.x + mazeSize; i++)
		{
			for (int j = lowLeftCorner.y; j < lowLeftCorner.y + mazeSize; j++)
			{
				if (sim.farm.grid.entities.GetValueOrDefault(new Vector2Int(i, j)) is Treasure)
				{
					return new PyTuple(new List<IPyObject>
					{
						new PyNumber(i),
						new PyNumber(j)
					});
				}
			}
		}
		return PyNone.Instance;
	}
}
public class Pumpkin : Growable
{
	private const double BREAK_PROBABILITY = 0.2;

	private int meshIndex;

	public double mysteriousNumber;

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		Matrix4x4 transform = GetTransform();
		yield return (objectSO.meshes[meshIndex], transform);
		if (weird)
		{
			yield return (objectSO.gooMeshes[gooIndex], transform);
		}
	}

	protected override void OnFullyGrown()
	{
		base.OnFullyGrown();
		if (sim.randomPumpkin.NextDouble() <= 0.2)
		{
			sim.farm.grid.SetEntity(pos, "dead_pumpkin");
		}
		else
		{
			sim.farm.grid.pumpkinController.AddPumpkin(this);
		}
	}

	public override ItemBlock GetYield()
	{
		int numWeird;
		Vector2Int size = sim.farm.grid.pumpkinController.GetSize(this, out numWeird);
		return GetDrops(size, numWeird);
	}

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		HarvestEffects();
		int numWeird;
		Vector2Int size = sim.farm.grid.pumpkinController.RemovePumpkin(this, out numWeird);
		if (size.x == 32 && sim.leaderboardType == LeaderboardType.none)
		{
			Achievements.UnlockAchievement("GIANT_PUMPKIN");
		}
		collectionDuration = Duration.FromSeconds(0.0);
		return GetDrops(size, numWeird);
	}

	private ItemBlock GetDrops(Vector2Int size, int numWeird)
	{
		double num = (double)Mathf.Min(size.x, 6) * YieldFactor;
		double num2 = Math.Floor((double)numWeird * 0.5 * num);
		double n = (double)(size.x * size.x) * num - num2;
		ItemBlock itemBlock = new ItemBlock(objectSO.dropItemId, n);
		if (num2 > 0.0)
		{
			itemBlock.AddItem(StringIds.WeirdSubstanceItemId, num2);
		}
		return itemBlock;
	}

	public void SetMesh(int m, GridDirection orientation)
	{
		meshIndex = m;
		base.Orientation = orientation;
	}

	public override void OnRestart()
	{
		base.OnRestart();
		meshIndex = 0;
		mysteriousNumber = Helper.JustSha256It(sim.randomPumpkin);
	}

	public override void OnFree()
	{
		base.OnFree();
		sim.farm.grid.pumpkinController.RemovePumpkin(this, out var _);
	}

	public override IPyObject Measure()
	{
		return new PyNumber(mysteriousNumber);
	}
}
public class PumpkinController
{
	private const int greenOffset = 5;

	private GridManager gm;

	private Dictionary<Vector2Int, Pumpkin> pumpkins = new Dictionary<Vector2Int, Pumpkin>();

	private Dictionary<Pumpkin, RectInt> groups = new Dictionary<Pumpkin, RectInt>();

	public PumpkinController(GridManager gm)
	{
		this.gm = gm;
	}

	public void AddPumpkin(Pumpkin p)
	{
		Vector2Int pos = p.pos;
		pumpkins[pos] = p;
		MergeWithOthers(pos);
		RectInt r = groups[p];
		foreach (Vector2Int item in IterPositions(r))
		{
			bool[] array = new bool[4]
			{
				item.y < r.yMax,
				item.x < r.xMax,
				item.y > r.yMin,
				item.x > r.xMin
			};
			int num;
			GridDirection orientation;
			switch ((array[0] ? 1 : 0) + (array[1] ? 1 : 0) + (array[2] ? 1 : 0) + (array[3] ? 1 : 0))
			{
			case 4:
				num = 5;
				orientation = GridDirection.North;
				break;
			case 3:
				num = 4;
				orientation = ((!array[0]) ? GridDirection.South : ((!array[3]) ? GridDirection.East : (array[2] ? GridDirection.West : GridDirection.North)));
				break;
			case 2:
				if (array[0] && array[2])
				{
					num = 2;
					orientation = GridDirection.North;
				}
				else if (array[1] && array[3])
				{
					num = 2;
					orientation = GridDirection.East;
				}
				else
				{
					num = 3;
					orientation = ((!array[0]) ? ((!array[3]) ? GridDirection.East : GridDirection.South) : (array[3] ? GridDirection.West : GridDirection.North));
				}
				break;
			case 1:
				num = 1;
				orientation = ((!array[0]) ? (array[3] ? GridDirection.West : ((!array[2]) ? GridDirection.East : GridDirection.South)) : GridDirection.North);
				break;
			default:
				num = 0;
				orientation = GridDirection.North;
				break;
			}
			if (num != 0 && item == (r.max + Vector2Int.one) / 2)
			{
				num += 5;
			}
			pumpkins[item].SetMesh(num, orientation);
		}
	}

	public Vector2Int RemovePumpkin(Pumpkin p, out int numWeird)
	{
		numWeird = 0;
		if (!groups.ContainsKey(p))
		{
			gm.RemoveEntity(p.pos);
			return Vector2Int.zero;
		}
		Vector2Int size = groups[p].size;
		foreach (Vector2Int item in IterPositions(groups[p]))
		{
			groups.Remove(pumpkins[item]);
			Pumpkin pumpkin = gm.entities.GetValueOrDefault(item) as Pumpkin;
			if (pumpkin != null && pumpkin.weird)
			{
				numWeird++;
			}
			pumpkin?.HarvestEffects();
			gm.RemoveEntity(item);
			pumpkins.Remove(item);
		}
		return size + Vector2Int.one;
	}

	public Vector2Int GetSize(Pumpkin p, out int numWeird)
	{
		numWeird = 0;
		if (!groups.ContainsKey(p))
		{
			return Vector2Int.zero;
		}
		Vector2Int size = groups[p].size;
		foreach (Vector2Int item in IterPositions(groups[p]))
		{
			if (gm.entities.GetValueOrDefault(item) is Pumpkin { weird: not false })
			{
				numWeird++;
			}
		}
		return size + Vector2Int.one;
	}

	private void MergeWithOthers(Vector2Int pos)
	{
		int y = gm.farm.grid.WorldSize.y;
		int[] array = new int[y * y];
		for (int i = 0; i < array.Length; i++)
		{
			array[i] = (pumpkins.ContainsKey(new Vector2Int(i % y, i / y)) ? 1 : 0);
		}
		bool flag = true;
		int num = 1;
		while (flag)
		{
			num++;
			flag = false;
			for (int j = 0; j < array.Length; j++)
			{
				int num2 = j % y;
				int num3 = j / y;
				if (num2 + 1 < y && num3 + 1 < y && array[j] == num - 1 && array[num2 + 1 + y * num3] == num - 1 && array[num2 + y * (num3 + 1)] == num - 1 && array[num2 + 1 + y * (num3 + 1)] == num - 1)
				{
					array[j] = num;
					flag = true;
				}
			}
		}
		num--;
		RectInt rectInt = LargestSquare(array, y, num, pos);
		Pumpkin pumpkin = pumpkins[IterPositions(rectInt).First()];
		foreach (Vector2Int item in IterPositions(rectInt))
		{
			groups[pumpkins[item]] = rectInt;
			pumpkins[item].mysteriousNumber = pumpkin.mysteriousNumber;
		}
	}

	private void PrintDP(int[] dp, int n)
	{
		string text = "";
		for (int i = 0; i < n; i++)
		{
			for (int j = 0; j < n; j++)
			{
				text += dp[j + n * i];
			}
			text += "\n";
		}
		UnityEngine.Debug.Log(text);
	}

	private RectInt LargestSquare(int[] dp, int n, int squareSize, Vector2Int pos)
	{
		while (squareSize > 1)
		{
			for (int i = 0; i < dp.Length; i++)
			{
				RectInt rectInt = new RectInt(new Vector2Int(i % n, i / n), new Vector2Int(squareSize - 1, squareSize - 1));
				if (dp[i] >= squareSize && IsInRect(rectInt, pos) && !HasOverlaps(rectInt))
				{
					return rectInt;
				}
			}
			squareSize--;
		}
		return new RectInt(pos, Vector2Int.zero);
	}

	private bool HasOverlaps(RectInt r)
	{
		foreach (Vector2Int item in IterPositions(r))
		{
			if (groups.ContainsKey(pumpkins[item]))
			{
				RectInt rectInt = groups[pumpkins[item]];
				if (rectInt.max.x > r.max.x || rectInt.max.y > r.max.y || rectInt.min.x < r.min.x || rectInt.min.y < r.min.y)
				{
					return true;
				}
			}
		}
		return false;
	}

	private bool IsInRect(RectInt r, Vector2Int pos)
	{
		if (pos.x >= r.xMin && pos.y >= r.yMin && pos.x <= r.xMax)
		{
			return pos.y <= r.yMax;
		}
		return false;
	}

	private IEnumerable<Vector2Int> IterPositions(RectInt r)
	{
		int xMax = r.xMax;
		int yMax = r.yMax;
		for (int i = r.xMin; i <= xMax; i++)
		{
			for (int j = r.yMin; j <= yMax; j++)
			{
				yield return new Vector2Int(i, j);
			}
		}
	}
}
public class Soil : Ground
{
	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		double num = sim.farm.grid.waterVolume[pos.x, pos.y];
		int index = ((num != 1.0) ? ((int)Math.Floor(num * (double)objectSO.meshes.Count)) : (objectSO.meshes.Count - 1));
		yield return (objectSO.meshes[index], GetTransform());
	}
}
public class Sunflower : Growable
{
	private int number;

	private bool getBoost;

	protected override double YieldFactor
	{
		get
		{
			sim.farm.grid.entities.Values.Where((FarmObject f) => f is Sunflower);
			if (getBoost)
			{
				return 8.0 * base.YieldFactor;
			}
			return base.YieldFactor;
		}
	}

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		IEnumerable<FarmObject> source = sim.farm.grid.entities.Values.Where((FarmObject f) => f is Sunflower);
		getBoost = number == source.Max((FarmObject s) => ((Sunflower)s).number) && source.Count() >= 10;
		bool hadIncorrectSunflowerHarvest = sim.farm.grid.hadIncorrectSunflowerHarvest;
		sim.farm.grid.hadIncorrectSunflowerHarvest = !getBoost;
		if (hadIncorrectSunflowerHarvest)
		{
			getBoost = false;
		}
		if (getBoost)
		{
			sim.mainSim.PlayEffect(VFXType.stars, base.LocalPosition);
		}
		return base.Harvest(out collectionDuration);
	}

	public override ItemBlock GetYield()
	{
		IEnumerable<FarmObject> source = sim.farm.grid.entities.Values.Where((FarmObject f) => f is Sunflower);
		getBoost = number == source.Max((FarmObject s) => ((Sunflower)s).number) && source.Count() >= 10;
		return base.GetYield();
	}

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		Matrix4x4 transform = GetTransform();
		yield return (objectSO.meshes[number - 7], transform);
		if (weird)
		{
			yield return (objectSO.gooMeshes[gooIndex], Matrix4x4.Translate(GridManager.CellToLocal(pos)));
		}
	}

	public override void OnFree()
	{
		base.OnFree();
	}

	public override void OnRestart()
	{
		base.OnRestart();
		number = sim.randomSunflower.Next(7, 16);
	}

	public override IPyObject Measure()
	{
		return new PyNumber(number);
	}
}
public class Treasure : HedgePlant
{
	private const int MAX_TREASURE_FACTOR = 301;

	private int treasureFactor = 1;

	private Vector2Int nextPos;

	private Duration startTime;

	private bool repositioning;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		base.Harvest(out collectionDuration);
		if (sim.leaderboardType == LeaderboardType.none && mazeSize == sim.farm.grid.WorldSize.x)
		{
			Achievements.UnlockAchievement("TREASURE_HUNTER");
		}
		collectionDuration = Duration.FromSeconds(0.0);
		double n = objectSO.dropAmount * (double)mazeSize * (double)mazeSize * YieldFactor;
		return new ItemBlock(objectSO.dropItemId, n);
	}

	public override ItemBlock GetYield()
	{
		double n = objectSO.dropAmount * (double)mazeSize * (double)mazeSize * YieldFactor;
		return new ItemBlock(objectSO.dropItemId, n);
	}

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		return base.GetMeshes().Append((objectSO.meshes[1], GetTransform()));
	}

	public bool RepositionTreasure(int desired_size, out bool useActionTicks)
	{
		if (mazeSize <= 1 || desired_size < mazeSize || treasureFactor >= 301)
		{
			useActionTicks = false;
			return false;
		}
		if (repositioning)
		{
			useActionTicks = true;
			return false;
		}
		repositioning = true;
		double n = objectSO.dropAmount * (double)mazeSize * (double)mazeSize * YieldFactor;
		sim.farm.CollectItems(new ItemBlock(objectSO.dropItemId, n), GetTransform().GetPosition(), Duration.FromSeconds(0.0));
		sim.mainSim?.PlaySound(SoundEffectType.HarvestTreasureChest, pos);
		Vector3 localPosition = base.LocalPosition;
		sim.mainSim?.PlayEffect(VFXType.hit, localPosition, changeColor: true, objectSO.color);
		sim.mainSim?.PlayEffect(VFXType.dust, localPosition);
		sim.StartTimer(CompleteRepositioning, sim.OpDuration * 200.0);
		useActionTicks = true;
		return true;
	}

	private void CompleteRepositioning()
	{
		if (!repositioning || removed)
		{
			return;
		}
		repositioning = false;
		HedgePlant hedgePlant = sim.farm.grid.entities[nextPos] as HedgePlant;
		hedgePlant.removed = true;
		Treasure treasure = (Treasure)sim.farm.grid.SetEntity(nextPos, "treasure");
		treasure.walls = hedgePlant.walls;
		treasure.treasureFactor = treasureFactor + 1;
		treasure.startTime = startTime;
		treasure.mazeSize = mazeSize;
		treasure.lowLeftCorner = lowLeftCorner;
		treasure.ChooseNextPosition();
		if (sim.leaderboardType == LeaderboardType.none && treasure.treasureFactor >= 300)
		{
			Achievements.UnlockAchievement("RECYCLING");
		}
		removed = true;
		HedgePlant obj = (HedgePlant)sim.farm.grid.SetEntity(pos, "hedge");
		obj.walls = walls;
		obj.mazeSize = mazeSize;
		obj.lowLeftCorner = lowLeftCorner;
		for (int i = lowLeftCorner.x; i < lowLeftCorner.x + mazeSize; i++)
		{
			for (int j = lowLeftCorner.y; j < lowLeftCorner.y + mazeSize; j++)
			{
				if ((i + j) % 2 == 1)
				{
					continue;
				}
				Vector2Int vector2Int = new Vector2Int(i, j);
				foreach (GridDirection item in from d in Enumerable.Range(0, 4)
					select (GridDirection)d)
				{
					Vector2Int key = vector2Int + item.GetDirectionVector();
					if (!(sim.randomMaze.NextDouble() > 0.002) && key.x >= lowLeftCorner.x && key.y >= lowLeftCorner.y && key.x < lowLeftCorner.x + mazeSize && key.y < lowLeftCorner.y + mazeSize)
					{
						((HedgePlant)sim.farm.grid.entities[vector2Int]).walls[(int)item] = false;
						((HedgePlant)sim.farm.grid.entities[key]).walls[(int)item.Reverse()] = false;
					}
				}
			}
		}
	}

	public override void OnRestart()
	{
		base.OnRestart();
		treasureFactor = 1;
		startTime = sim.CurrentTime;
		repositioning = false;
	}

	public override IPyObject Measure()
	{
		return new PyTuple(new List<IPyObject>
		{
			new PyNumber(pos.x),
			new PyNumber(pos.y)
		});
	}

	public override string ToSerializeString()
	{
		return $"{base.ToSerializeString()},treasureFactor = {treasureFactor},nextX = {nextPos.x},nextY = {nextPos.y},lifetime = {sim.CurrentTime - startTime}";
	}

	public override void SetValues(Dictionary<string, string> values)
	{
		base.SetValues(values);
		if (values.ContainsKey("treasureFactor") && int.TryParse(values["treasureFactor"], out var result))
		{
			treasureFactor = result;
		}
		if (values.ContainsKey("nextX") && int.TryParse(values["nextX"], out var result2))
		{
			nextPos.x = result2;
		}
		if (values.ContainsKey("nextY") && int.TryParse(values["nextY"], out var result3))
		{
			nextPos.x = result3;
		}
		if (values.ContainsKey("lifetime") && double.TryParse(values["lifetime"], out var result4))
		{
			startTime = sim.CurrentTime - Duration.FromSeconds(result4);
		}
	}

	public void ChooseNextPosition()
	{
		if (mazeSize > 1)
		{
			do
			{
				nextPos = new Vector2Int(sim.randomMaze.Next(mazeSize), sim.randomMaze.Next(mazeSize)) + lowLeftCorner;
			}
			while (nextPos == pos);
		}
	}
}
public class TreePlant : Growable
{
	protected override double GrowTimeFactor
	{
		get
		{
			FarmObject[] neighbors = sim.farm.grid.GetNeighbors(pos);
			double num = 1.0;
			FarmObject[] array = neighbors;
			for (int i = 0; i < array.Length; i++)
			{
				if (array[i]?.objectSO.objectName == "tree")
				{
					num *= 2.0;
				}
			}
			return base.GrowTimeFactor * num;
		}
	}

	public override void OnRestart()
	{
		base.OnRestart();
		UpdateNeighbors();
	}
}
public class DinosaurHat : Hat
{
	private LinkedList<Dinosaur> tail = new LinkedList<Dinosaur>();

	public Apple target;

	private int ops = 400;

	private Duration equipTime;

	public override void OnEquip(Drone drone, ProgramState programState)
	{
		base.OnEquip(drone, programState);
		equipTime = base.sim.CurrentTime;
		if (base.sim.leaderboardType == LeaderboardType.none)
		{
			Achievements.UnlockAchievement("EQUIP_DINO_HAT");
		}
		if (!base.sim.farm.grid.entities.ContainsKey(drone.pos) || drone.EntityUnderDrone().objectSO.canBeOverplanted)
		{
			if (base.sim.farm.drones.Where((Drone d) => d?.hat.hatSO.hatName == "dinosaur_hat").Count() > 1)
			{
				drone.hat = Hat.CreateHat(ResourceManager.GetHat("straw_hat"), base.sim, drone);
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_dino_hat_already_used"));
			}
			int num = Mathf.Max(0, base.sim.farm.NumUnlocked("dinosaurs") - 1);
			if (base.sim.farm.Items.Remove(ResourceManager.GetFarmObject("apple").cost * Mathf.Max(1, 1 << num)))
			{
				target = (Apple)base.sim.farm.grid.SetEntity(drone.pos, "apple");
				target.ChooseTarget();
			}
			else
			{
				Logger.LogWarning(CodeUtilities.LocalizeAndFormat("warning_missing_seed", ResourceManager.GetFarmObject("apple")), programState);
			}
		}
	}

	public override void OnUnequip()
	{
		base.OnUnequip();
		if (tail.Count > 0)
		{
			base.sim.mainSim?.PlaySound(SoundEffectType.DinosaurDie, base.drone.pos);
			base.sim.farm.CollectItem(StringIds.BoneItemId, BoneCount(), tail.First.Value.LocalPosition, base.sim.CurrentTime - equipTime);
		}
		foreach (Dinosaur item in tail)
		{
			item.HarvestEffects();
			item.isInSnake = false;
			base.sim.farm.grid.RemoveEntity(item.pos);
		}
		if (target != null)
		{
			base.sim.farm.grid.RemoveEntity(target.pos);
		}
		tail.Clear();
	}

	public double BoneCount()
	{
		int num = base.sim.farm.grid.entities.Count((KeyValuePair<Vector2Int, FarmObject> e) => e.Value is Dinosaur);
		int num2 = Mathf.Max(0, base.sim.farm.NumUnlocked("dinosaurs") - 1);
		return Math.Floor(Math.Pow(num, 2.0)) * (double)(1 << num2);
	}

	public override int OnMove(Vector2Int oldPos, Vector2Int newPos, ProgramState programState)
	{
		base.OnMove(oldPos, newPos, programState);
		bool flag = false;
		int num = base.sim.farm.grid.WorldSize.x * base.sim.farm.grid.WorldSize.y - 2;
		Apple apple = target;
		if (apple != null && apple.pos == oldPos && base.sim.farm.grid.entities.GetValueOrDefault(oldPos) == target)
		{
			int num2 = Mathf.Max(0, base.sim.farm.NumUnlocked("dinosaurs") - 1);
			flag = true;
			if (tail.Count < num && (!base.sim.farm.grid.entities.TryGetValue(target.nextPos, out var value) || value.objectSO.canBeOverplanted) && base.sim.farm.Items.Remove(target.objectSO.cost * (1 << num2)))
			{
				base.sim.mainSim?.PlaySound(SoundEffectType.DinosaurEatApple, newPos);
				base.sim.mainSim?.PlayEffect(VFXType.hit, target.LocalPosition, changeColor: true, target.objectSO.color);
				target = (Apple)base.sim.farm.grid.SetEntity(target.nextPos, "apple");
				target.ChooseTarget();
				ops -= (int)Math.Floor((double)ops * 0.03);
			}
			else
			{
				if (!base.sim.farm.Items.Contains(target.objectSO.cost * (1 << num2)))
				{
					Logger.LogWarning(CodeUtilities.LocalizeAndFormat("warning_missing_seed", ResourceManager.GetFarmObject("apple")), programState);
				}
				target = null;
			}
		}
		if (flag || tail.Count > 0)
		{
			Dinosaur dinosaur = (Dinosaur)base.sim.farm.grid.SetEntity(oldPos, "dinosaur");
			dinosaur.drone = base.drone;
			if (tail.Count > 0)
			{
				dinosaur.Orientation = GridDirectionMethods.FromVector(oldPos - tail.First.Value.pos);
				if (!flag)
				{
					tail.Last.Value.isInSnake = false;
					base.sim.farm.grid.RemoveEntity(tail.Last.Value.pos);
					tail.RemoveLast();
				}
			}
			else
			{
				dinosaur.Orientation = GridDirectionMethods.FromVector(newPos - oldPos);
			}
			tail.AddFirst(dinosaur);
			if (tail.Count == num && base.sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.UnlockAchievement("LONG_DINOSAUR");
			}
			else if (tail.Count >= 1000 && base.sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.UnlockAchievement("SIZE_MATTERS");
			}
			if (tail.Count < num && tail.Count > 1 && base.sim.farm.grid.entities.GetValueOrDefault(newPos) != target)
			{
				tail.Last.Value.canMoveTo = true;
			}
			if (!flag && tail.Count > 1)
			{
				tail.Last.Value.LastTailAnim(ops);
				tail.First.Value.FirstTailAnim(ops);
			}
			else if (tail.Count == 1)
			{
				tail.First.Value.DoubleTailAnim();
			}
			else
			{
				tail.First.Value.FirstTailAnim(ops);
			}
		}
		while (true)
		{
			Apple apple2 = target;
			if (apple2 == null || !(apple2.nextPos == oldPos) || tail.Count >= num)
			{
				break;
			}
			target.ChooseTarget();
		}
		return ops;
	}
}
public class Hat
{
	private static Dictionary<string, Type> hatTypes;

	public HatSO hatSO { get; private set; }

	public Simulation sim { get; private set; }

	public Drone drone { get; private set; }

	public virtual int OnMove(Vector2Int oldPos, Vector2Int newPos, ProgramState programState)
	{
		return -1;
	}

	public virtual void OnUnequip()
	{
	}

	public virtual void OnEquip(Drone drone, ProgramState programState)
	{
	}

	public static Hat CreateHat(HatSO hatType, Simulation sim, Drone drone)
	{
		if (hatTypes == null)
		{
			hatTypes = (from type in typeof(Hat).Assembly.GetTypes()
				where type.IsSubclassOf(typeof(Hat)) || type == typeof(Hat)
				select type).ToDictionary((Type t) => t.Name, (Type t) => t);
		}
		Hat obj = (Hat)Activator.CreateInstance(hatTypes[hatType.className]);
		obj.hatSO = hatType;
		obj.sim = sim;
		obj.drone = drone;
		return obj;
	}
}
[CreateAssetMenu(fileName = "Hat", menuName = "ScriptableObjects/Hat", order = 3)]
public class HatSO : ScriptableObject, IPyObject
{
	public string className;

	public string hatName;

	public Mesh hatMesh;

	public bool isGolden;

	public bool preventWrapping;

	public bool rotateDroneToMove;

	public float droneFlyHeight;

	public bool hidden;

	public AudioClip sound1;

	public AudioClip sound2;

	public override string ToString()
	{
		return "Hats." + CodeUtilities.ToUpperSnake(hatName);
	}

	public IPyObject DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}
}
[CreateAssetMenu(fileName = "Leaderboard", menuName = "ScriptableObjects/Leaderboard", order = 1)]
public class LeaderboardSO : ScriptableObject, IPyObject
{
	public string leaderboardName;

	public string steamLeaderboardName;

	public LeaderboardType leaderboardType;

	public ItemBlock startItems;

	public bool everythingUnlocked;

	public bool singleDrone;

	public ItemBlock goalItems;

	public override string ToString()
	{
		return "Leaderboards." + CodeUtilities.ToUpperSnake(leaderboardName);
	}

	public IPyObject DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}
}
public enum LeaderboardType
{
	none,
	simulation,
	reset,
	farm_resources
}
public class ResourceManager
{
	private static Dictionary<string, FarmObjectSO> farmObjects;

	private static DroneSO drone;

	private static Dictionary<string, HatSO> hats;

	private static Dictionary<string, LeaderboardSO> leaderboards;

	private static Dictionary<string, UnlockSO> unlocks;

	private static ItemSO[] items;

	public static void LoadAll()
	{
		if (farmObjects != null || drone != null || hats != null || leaderboards != null || unlocks != null || items != null)
		{
			return;
		}
		items = (from x in Resources.LoadAll<ItemSO>("Items/")
			orderby x.priority
			select x).ToArray();
		for (int num = 0; num < items.Length; num++)
		{
			items[num].itemId = num;
		}
		StringIds.SetItemIds(items.Select((ItemSO x) => x.itemName));
		farmObjects = new Dictionary<string, FarmObjectSO>();
		FarmObjectSO[] array = Resources.LoadAll<FarmObjectSO>("FarmObjects/");
		foreach (FarmObjectSO farmObjectSO in array)
		{
			farmObjectSO.cost.Deserialize();
			farmObjectSO.dropItemId = StringIds.GetItemId(farmObjectSO.dropItem);
			farmObjects[farmObjectSO.objectName] = farmObjectSO;
		}
		drone = Resources.Load<DroneSO>("FarmObjects/drone");
		hats = new Dictionary<string, HatSO>();
		HatSO[] array2 = Resources.LoadAll<HatSO>("Hats/");
		foreach (HatSO hatSO in array2)
		{
			hats[hatSO.hatName] = hatSO;
		}
		leaderboards = new Dictionary<string, LeaderboardSO>();
		LeaderboardSO[] array3 = Resources.LoadAll<LeaderboardSO>("Leaderboards/");
		foreach (LeaderboardSO leaderboardSO in array3)
		{
			leaderboardSO.startItems.Deserialize();
			leaderboardSO.goalItems.Deserialize();
			leaderboards[leaderboardSO.leaderboardName] = leaderboardSO;
		}
		unlocks = new Dictionary<string, UnlockSO>();
		UnlockSO[] array4 = Resources.LoadAll<UnlockSO>("Unlocks/");
		foreach (UnlockSO unlockSO in array4)
		{
			foreach (ItemBlock item in unlockSO.multiUnlockCost)
			{
				item.Deserialize();
			}
			unlockSO.unlockCost.Deserialize();
			unlocks[unlockSO.unlockName] = unlockSO;
		}
	}

	public static FarmObjectSO GetFarmObject(string name)
	{
		return farmObjects.GetValueOrDefault(name);
	}

	public static DroneSO GetDrone()
	{
		return drone;
	}

	public static HatSO GetHat(string name)
	{
		return hats.GetValueOrDefault(name);
	}

	public static LeaderboardSO GetLeaderboard(string name)
	{
		return leaderboards.GetValueOrDefault(name);
	}

	public static UnlockSO GetUnlock(string name)
	{
		return unlocks.GetValueOrDefault(name);
	}

	public static ItemSO GetItem(int itemId)
	{
		return items[itemId];
	}

	public static Sprite GetSprite(string name)
	{
		return Resources.Load<Sprite>("Sprites/" + name);
	}

	public static IEnumerable<ItemSO> GetAllItems()
	{
		return items;
	}

	public static IEnumerable<FarmObjectSO> GetAllFarmObjects()
	{
		return farmObjects.Values;
	}

	public static IEnumerable<UnlockSO> GetAllUnlocks()
	{
		return unlocks.Values;
	}

	public static IEnumerable<LeaderboardSO> GetAllLeaderboards()
	{
		return leaderboards.Values;
	}

	public static IEnumerable<HatSO> GetAllHats()
	{
		return hats.Values;
	}

	public static IEnumerable<OptionSO> GetAllOptions()
	{
		return Resources.LoadAll<OptionSO>("Options/");
	}
}
[CreateAssetMenu(fileName = "Trade", menuName = "ScriptableObjects/Trade", order = 1)]
public class TradeSO : ScriptableObject, IPyObject
{
	public string itemName;

	public string descr;

	public ItemBlock input;

	public string unlockToScaleWith;

	public IPyObject DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}
}
[CreateAssetMenu(fileName = "Unlock", menuName = "ScriptableObjects/Unlock", order = 1)]
public class UnlockSO : ScriptableObject, IPyObject
{
	public string unlockName;

	public string description;

	public string docs;

	public Mesh mesh;

	public string displayCode;

	public List<string> unlocks;

	public string parentUnlock;

	public string unlockedHat;

	public int order;

	public ItemBlock unlockCost;

	public List<ItemBlock> multiUnlockCost;

	public float multiUnlockFactor = 2f;

	public string multiUnlockDescr;

	public MultiUnlockDescrMode multiUnlockDescrMode;

	public float additivePercentStart;

	public float additivePercentFactor = 2f;

	public int maxUnlockLevel = 1;

	public bool enabled = true;

	public bool IsMultiUnlock => maxUnlockLevel > 1;

	public override string ToString()
	{
		return "Unlocks." + CodeUtilities.ToUpperSnake(unlockName);
	}

	public IPyObject DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}
}
public enum MultiUnlockDescrMode
{
	None,
	AdditivePercent,
	GridSize,
	Megafarm,
	Per10Seconds
}
public class Drone
{
	private enum DroneState
	{
		idle,
		moving,
		action,
		flipping,
		printing,
		petting
	}

	public Vector2Int pos;

	private Simulation sim;

	private DroneSO droneSO;

	public Hat hat;

	private DroneState droneState;

	private Duration animDuration;

	private Duration actionStartTime;

	private Vector3 startPosition;

	private Vector3 endPosition;

	private Quaternion startRotation = Quaternion.identity;

	private Quaternion endRotation = Quaternion.identity;

	private float printWidth;

	private float prevRealTime = -1f;

	private Vector3 prevSpeedMeasurement = Vector3.zero;

	public int DroneId { get; set; }

	public Drone(Simulation sim, Vector2Int pos, int droneId)
	{
		this.sim = sim;
		droneSO = ResourceManager.GetDrone();
		this.pos = pos;
		endPosition = GridManager.CellToLocal(pos);
		droneState = DroneState.idle;
		DroneId = droneId;
		hat = Hat.CreateHat(ResourceManager.GetHat("straw_hat"), sim, this);
		hat.OnEquip(this, null);
	}

	private float ExtendedLerp(float a, float b, float t)
	{
		return a + (b - a) * t;
	}

	private float EaseInOutCubic(float t)
	{
		if (!((double)t < 0.5))
		{
			return 1f - Mathf.Pow(-2f * t + 2f, 3f) / 2f;
		}
		return 4f * t * t * t;
	}

	private float EaseOutCubic(float t)
	{
		return 1f - Mathf.Pow(1f - t, 3f);
	}

	public Matrix4x4 GetTransform()
	{
		float num = (float)((sim.CurrentTime - actionStartTime) / animDuration);
		if (num > 1f)
		{
			droneState = DroneState.idle;
		}
		float x;
		float y;
		float z;
		Quaternion q;
		switch (droneState)
		{
		case DroneState.idle:
			x = endPosition.x;
			y = endPosition.y;
			z = hat.hatSO.droneFlyHeight;
			q = endRotation;
			break;
		case DroneState.moving:
			x = ExtendedLerp(startPosition.x, endPosition.x, num);
			y = ExtendedLerp(startPosition.y, endPosition.y, num);
			z = hat.hatSO.droneFlyHeight;
			q = Quaternion.Slerp(startRotation, endRotation, num);
			break;
		case DroneState.action:
			x = endPosition.x;
			y = endPosition.y;
			z = ExtendedLerp(hat.hatSO.droneFlyHeight, hat.hatSO.droneFlyHeight - 0.4f, droneSO.actionZCurve.Evaluate(num));
			q = endRotation;
			break;
		case DroneState.flipping:
			x = endPosition.x;
			y = endPosition.y;
			z = ExtendedLerp(hat.hatSO.droneFlyHeight, hat.hatSO.droneFlyHeight + 1f, droneSO.flipZCuve.Evaluate(num));
			q = Quaternion.AngleAxis(ExtendedLerp(0f, 360f, EaseOutCubic(num)), Vector3.right);
			break;
		case DroneState.printing:
			x = ExtendedLerp(endPosition.x, endPosition.x + printWidth, droneSO.printXCurve.Evaluate(num));
			y = endPosition.y;
			z = ExtendedLerp(hat.hatSO.droneFlyHeight, hat.hatSO.droneFlyHeight + 1f, droneSO.printZCurve.Evaluate(num));
			q = Quaternion.AngleAxis(ExtendedLerp(0f, 360f, droneSO.printRotationCurve.Evaluate(num)), Vector3.down);
			break;
		case DroneState.petting:
			x = ExtendedLerp(endPosition.x, startPosition.x, droneSO.petMoveXYCurve.Evaluate(num));
			y = ExtendedLerp(endPosition.y, startPosition.y, droneSO.petMoveXYCurve.Evaluate(num));
			z = ExtendedLerp(hat.hatSO.droneFlyHeight, startPosition.z, droneSO.petMoveZCurve.Evaluate(num));
			q = endRotation;
			break;
		default:
			throw new Exception("this case shouldn't be reachable");
		}
		return Matrix4x4.TRS(new Vector3(x, y, z), q, Vector3.one);
	}

	public void ChangeHat(HatSO hatSO, ProgramState programState)
	{
		if (!hatSO.hidden && !sim.farm.IsUnlocked(hatSO.hatName))
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_missing_x_unlock", hatSO));
		}
		Hat obj = hat;
		hat = Hat.CreateHat(hatSO, sim, this);
		obj?.OnUnequip();
		hat.OnEquip(this, programState);
		if (!hat.hatSO.rotateDroneToMove)
		{
			endRotation = Quaternion.identity;
		}
		if (sim.leaderboardType == LeaderboardType.none)
		{
			if (hatSO.hatName != "straw_hat")
			{
				Achievements.UnlockAchievement("EQUIP_A_NEW_HAT");
			}
			if ((from d in sim.farm.drones
				where d != null
				select d.hat.hatSO).Distinct().Count() >= 5)
			{
				Achievements.UnlockAchievement("FASHION_SHOW");
			}
		}
	}

	public void DoAFlip()
	{
		if (!hat.hatSO.rotateDroneToMove)
		{
			droneState = DroneState.flipping;
			actionStartTime = sim.CurrentTime;
			animDuration = Duration.FromSeconds(1.0);
			if (sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.IncrementStat("flips", 1);
			}
		}
	}

	public void PetThePiggy()
	{
		if (!hat.hatSO.rotateDroneToMove)
		{
			droneState = DroneState.petting;
			actionStartTime = sim.CurrentTime;
			animDuration = Duration.FromSeconds(1.0);
			endPosition = GetTransform().GetPosition();
			startPosition = MainSim.Inst.pb.Position;
			endRotation = Quaternion.identity;
			startRotation = Quaternion.identity;
			sim.mainSim?.PlayEffect(VFXType.hearts, startPosition);
			if (sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.UnlockAchievement("PET_THE_PIGGY");
			}
		}
	}

	public void PrintToAir(string s)
	{
		if (!hat.hatSO.rotateDroneToMove)
		{
			droneState = DroneState.printing;
			actionStartTime = sim.CurrentTime;
			animDuration = Duration.FromSeconds(1.0);
		}
		if (sim.mainSim != null)
		{
			sim.mainSim?.PlayEffect(VFXType.print_sign, GetTransform().GetPosition(), changeColor: false, default(Color), s);
			printWidth = droneSO.extraPrintWidth + (float)Mathf.Min(droneSO.charactersAtMaxPrintWidth, s.Length) * droneSO.characterPrintWidth;
		}
	}

	public bool Move(GridDirection direction, ProgramState programState, out double ops)
	{
		ops = 1.0;
		Vector2Int newPos = pos + direction.GetDirectionVector();
		Vector2Int b = sim.farm.grid.Wrap(newPos);
		if (!CanMove(direction))
		{
			return false;
		}
		ops = hat.OnMove(pos, newPos, programState);
		if (ops <= 0.0)
		{
			ops = 200.0;
		}
		if (hat.hatSO.rotateDroneToMove)
		{
			startRotation = endRotation;
			endRotation = direction.GetQuaternion();
		}
		float num = Vector2Int.Distance(pos, b);
		pos = b;
		if (num > 8f)
		{
			UpdatePosition(0.0);
		}
		else
		{
			UpdatePosition(ops);
		}
		return true;
	}

	public bool CanMove(GridDirection direction)
	{
		Vector2Int vector2Int = pos + direction.GetDirectionVector();
		Vector2Int vector2Int2 = sim.farm.grid.Wrap(vector2Int);
		if (hat.hatSO.preventWrapping && vector2Int2 != vector2Int)
		{
			return false;
		}
		FarmObject valueOrDefault = sim.farm.grid.entities.GetValueOrDefault(vector2Int2, null);
		FarmObject valueOrDefault2 = sim.farm.grid.entities.GetValueOrDefault(pos, null);
		if ((valueOrDefault != null && !valueOrDefault.CanDroneMoveToFrom(direction.Reverse())) || (valueOrDefault2 != null && !valueOrDefault2.CanDroneMoveAwayTo(direction)))
		{
			return false;
		}
		return true;
	}

	public bool Swap(GridDirection dir, ProgramState state)
	{
		if (sim.farm.grid.Swap(pos, dir))
		{
			sim.mainSim?.PlaySound(SoundEffectType.SwapPlants, pos);
			ActionTween();
			return true;
		}
		Vector2Int vector2Int = pos + dir.GetDirectionVector();
		if (!sim.farm.grid.IsWithinBounds(vector2Int))
		{
			Logger.LogWarning(Localizer.Localize("warning_failed_swap_wrap"), state);
		}
		else
		{
			Logger.LogWarning(string.Format(Localizer.Localize("warning_failed_swap_unswappable"), EntityUnderDrone()), state);
		}
		return false;
	}

	public bool Harvest()
	{
		FarmObject farmObject = EntityUnderDrone();
		if (farmObject == null)
		{
			return false;
		}
		sim.farm.CollectItems(farmObject.Harvest(out var collectionDuration), GetTransform().GetPosition(), collectionDuration);
		ActionTween();
		sim.mainSim?.PlaySound(farmObject.objectSO.harvestSound, pos);
		return true;
	}

	public bool CanHarvest()
	{
		return EntityUnderDrone()?.Harvestable ?? false;
	}

	public bool IsOver(string objName)
	{
		string text = (sim.farm.grid.entities.ContainsKey(pos) ? EntityUnderDrone().objectSO.objectName : "");
		string objectName = GroundUnderDrone().objectSO.objectName;
		if (!(objName == text))
		{
			return objName == objectName;
		}
		return true;
	}

	public void ChangeGround(string ground)
	{
		if (!(EntityUnderDrone() is HedgePlant))
		{
			sim.farm.grid.RemoveEntity(pos, regrowGrass: false);
		}
		if (IsOver(ground))
		{
			sim.farm.grid.SetGround(pos, "grassland");
			if (!(EntityUnderDrone() is HedgePlant))
			{
				sim.farm.grid.SetEntity(pos, "grass");
			}
		}
		else
		{
			sim.farm.grid.SetGround(pos, ground);
		}
		ActionTween();
		sim.mainSim?.PlaySound(SoundEffectType.Till, pos);
	}

	public bool Plant(FarmObjectSO growable, ProgramState state)
	{
		if (sim.farm.grid.entities.ContainsKey(pos) && !EntityUnderDrone().objectSO.canBeOverplanted)
		{
			return false;
		}
		if (!growable.canBePlanted || !growable.placeableOn.Contains(sim.farm.grid.grounds[pos].objectSO.objectName))
		{
			Logger.LogWarning(string.Format(Localizer.Localize("warning_cant_plant_on_ground"), growable, sim.farm.grid.grounds[pos]), state);
			return false;
		}
		sim.farm.AssertUnlocked(growable.objectName);
		int num = Mathf.Max(0, sim.farm.NumUnlocked(growable.yieldUpgradeName) - 1);
		if (!sim.farm.Items.Remove(growable.cost * Mathf.Max(1, 1 << num)))
		{
			Logger.LogWarning(string.Format(Localizer.Localize("warning_missing_seed"), growable), state);
			return false;
		}
		sim.farm.grid.SetEntity(pos, growable.objectName).OnPlanted(this);
		if (sim.mainSim != null)
		{
			ActionTween();
			sim.mainSim?.PlaySound(SoundEffectType.Plant, pos);
			if (sim.leaderboardType == LeaderboardType.none)
			{
				switch (growable.objectName)
				{
				case "bush":
					Achievements.UnlockAchievement("PLANT_BUSH");
					break;
				case "carrot":
					Achievements.UnlockAchievement("PLANT_CARROTS");
					break;
				case "tree":
					Achievements.UnlockAchievement("PLANT_TREE");
					break;
				case "pumpkin":
					Achievements.UnlockAchievement("PLANT_PUMPKIN");
					break;
				case "sunflower":
					Achievements.UnlockAchievement("PLANT_SUNFLOWER");
					break;
				case "cactus":
					Achievements.UnlockAchievement("PLANT_CACTUS");
					break;
				}
			}
		}
		return true;
	}

	public bool Water(int number)
	{
		sim.farm.grid.SetWaterVolume(pos, sim.farm.grid.waterVolume[pos.x, pos.y] + 0.25 * (double)number);
		if (sim.leaderboardType == LeaderboardType.none && sim.farm.grid.waterVolume.Cast<double>().All((double v) => v >= 0.5))
		{
			Achievements.UnlockAchievement("MUD_FARM");
		}
		if (sim.mainSim != null && sim.mainSim.TimeFactor == 1.0)
		{
			sim.mainSim.PlayEffect(VFXType.water, GetTransform().GetPosition());
			sim.mainSim?.PlaySound(SoundEffectType.UseWater, pos);
		}
		return true;
	}

	public double GetWater()
	{
		return sim.farm.grid.waterVolume[pos.x, pos.y];
	}

	public bool Fertilize(int number)
	{
		Growable growable = GrowableUnderDrone();
		if (growable == null)
		{
			return false;
		}
		growable.Fertilize(number);
		sim.mainSim?.PlaySound(SoundEffectType.UseFertilizer, pos);
		return true;
	}

	public void ResetPos()
	{
		if (pos != Vector2Int.zero)
		{
			pos = Vector2Int.zero;
			UpdatePosition(200.0);
		}
		ChangeHat(ResourceManager.GetHat("straw_hat"), null);
	}

	public Growable GrowableUnderDrone()
	{
		return EntityUnderDrone() as Growable;
	}

	public Ground GroundUnderDrone()
	{
		return (Ground)sim.farm.grid.grounds[pos];
	}

	public FarmObject EntityUnderDrone()
	{
		return sim.farm.grid.entities.GetValueOrDefault(pos);
	}

	private void UpdatePosition(double ops)
	{
		animDuration = sim.GetActionTime(ops);
		startPosition = endPosition;
		endPosition = GridManager.CellToLocal(pos);
		actionStartTime = sim.CurrentTime;
		droneState = DroneState.moving;
	}

	public (float speed, Vector3 position) GetSpeedAndPos(float realTime)
	{
		Vector3 position = GetTransform().GetPosition();
		if (prevRealTime < 0f)
		{
			prevRealTime = realTime;
			return (speed: 0f, position: position);
		}
		float num = realTime - prevRealTime;
		float item = Vector3.Distance(position, prevSpeedMeasurement) / num;
		prevRealTime = realTime;
		prevSpeedMeasurement = position;
		return (speed: item, position: SoundManager.ZoomAdjustedPosition(position));
	}

	private void ActionTween()
	{
		actionStartTime = sim.CurrentTime;
		droneState = DroneState.action;
		animDuration = sim.GetActionTime(200.0);
	}
}
[CreateAssetMenu(fileName = "Drone", menuName = "ScriptableObjects/Drone", order = 2)]
public class DroneSO : ScriptableObject
{
	public AudioClip dirtSound;

	public AudioClip plantSound;

	public AudioClip harvestSound;

	public AudioClip pickupSound;

	public AudioClip waterSound;

	public AnimationCurve actionZCurve;

	public AnimationCurve flipZCuve;

	public AnimationCurve printZCurve;

	public AnimationCurve printXCurve;

	public AnimationCurve printRotationCurve;

	public AnimationCurve petMoveXYCurve;

	public AnimationCurve petMoveZCurve;

	public float extraPrintWidth;

	public float characterPrintWidth;

	public int charactersAtMaxPrintWidth;
}
public class Farm
{
	private const double FILL_INTERVAL = 10.0;

	private const double USE_POWER_INTERVAL = 0.2;

	public GridManager grid;

	public List<Drone> drones = new List<Drone>();

	public int mainDroneId;

	public Simulation sim;

	public int droneGeneration;

	private readonly ItemBlock _items;

	public static List<string> startUnlocks = new List<string> { "grass", "soil", "harvest", "pass", "do_a_flip", "pet_the_piggy", "grassland", "hay", "straw_hat", "tap" };

	private Dictionary<string, int> unlocks = new Dictionary<string, int>();

	public static HashSet<string> allKeyWords = new HashSet<string>
	{
		"def", "while", "for", "if", "else", "elif", "and", "or", "not", "True",
		"False", "None", "Entities", "Grounds", "Items", "Unlocks", "Leaderboards", "Hats", "North", "South",
		"West", "East", "pass", "break", "continue", "return", "global", "import", "from"
	};

	public HashSet<string> unlockedKeyWords = new HashSet<string>();

	private Dictionary<string, UnlockSO> unlockedIn;

	public ItemBlock Items => _items;

	public double UsedPower { get; set; }

	public int NumSpeedUpgrades { get; private set; }

	public Farm(Simulation sim, IEnumerable<string> unlocks, ItemBlock itemBlock, List<SFO> loadedGrounds = null, List<SFO> loadedEntities = null, bool resetUnlocks = false)
	{
		this.sim = sim;
		sim.farm = this;
		drones.Add(new Drone(sim, Vector2Int.zero, 0));
		grid = new GridManager(this, loadedGrounds, loadedEntities);
		_items = itemBlock;
		foreach (string startUnlock in startUnlocks)
		{
			Unlock(startUnlock, 1);
		}
		foreach (string unlock3 in unlocks)
		{
			int num = unlock3.LastIndexOf('_');
			string text;
			if (num != -1 && int.TryParse(unlock3.Substring(num + 1), out var result) && !unlock3.StartsWith("debug"))
			{
				text = unlock3.Substring(0, num);
				if (resetUnlocks)
				{
					UnlockSO unlock = ResourceManager.GetUnlock(text);
					if (unlock != null)
					{
						result = (int)Math.Clamp(Math.Log(result + 1, 2.0), 1.0, unlock.maxUnlockLevel);
					}
				}
				Unlock(text, result);
			}
			else
			{
				text = unlock3;
				result = 1;
			}
			if (ResourceManager.GetUnlock(text) != null)
			{
				UnlockSO unlock2 = ResourceManager.GetUnlock(text);
				UnlockAllIn(unlock2);
			}
			Unlock(text, result);
		}
		sim.StartTimer(ReceiveWater, Duration.FromSeconds(20.0 / (double)(1 << NumUnlocked("watering"))));
		sim.StartTimer(ReceiveFertilizer, Duration.FromSeconds(20.0 / (double)(1 << NumUnlocked("fertilizer"))));
		sim.StartTimer(UsePower, Duration.FromSeconds(0.2));
	}

	public void CollectItems(ItemBlock items, Vector3 localPos, Duration collectionDuration = default(Duration))
	{
		if (items == null || items.IsEmpty())
		{
			return;
		}
		if (Items.GetNumber(StringIds.PowerItemId) == 0.0 && items.GetNumber(StringIds.PowerItemId) > 0.0 && sim.SpeedFactor == MaxSpeedFactor())
		{
			UsedPower = 0.0;
			Items.Add(items);
			sim.ChangeExecutionSpeed(MaxSpeedFactor());
		}
		else
		{
			Items.Add(items);
		}
		if (!(sim.mainSim != null))
		{
			return;
		}
		if (sim.leaderboardType == LeaderboardType.none)
		{
			for (int i = 0; i < items.items.Length; i++)
			{
				if (items.items[i] > 0.0)
				{
					ItemSO item = ResourceManager.GetItem(i);
					if (item != null && item.trackStats)
					{
						Achievements.CollectItem(item.itemId, items.items[i], sim.CurrentTime, collectionDuration);
					}
				}
			}
		}
		if (sim.mainSim.TimeFactor == 1.0)
		{
			sim.mainSim.CollectItemEffect(items.ItemIds().First(), localPos);
		}
	}

	public void CollectItem(int itemId, double n, Vector3 localPos, Duration collectionDuration = default(Duration))
	{
		CollectItems(new ItemBlock(itemId, n), localPos, collectionDuration);
	}

	public ItemBlock GetUnlockCost(UnlockSO unlockSO, int numUnlocked = -1)
	{
		int num = ((numUnlocked >= 0) ? numUnlocked : NumUnlocked(unlockSO.unlockName));
		if (num >= unlockSO.maxUnlockLevel)
		{
			return ItemBlock.CreateEmpty();
		}
		if (unlockSO.IsMultiUnlock)
		{
			int count = unlockSO.multiUnlockCost.Count;
			if (num > 0)
			{
				if (count < num)
				{
					ItemBlock itemBlock = unlockSO.multiUnlockCost[count - 1] * Mathf.Pow(unlockSO.multiUnlockFactor, num - count);
					foreach (int item in itemBlock.ItemIds())
					{
						itemBlock.items[item] = Helper.RoundToNDecimalDigits(itemBlock.items[item], 3);
					}
					itemBlock.TruncateNumbers();
					return itemBlock;
				}
				return unlockSO.multiUnlockCost[num - 1];
			}
		}
		return unlockSO.unlockCost;
	}

	public List<string> SerializeUnlocks()
	{
		List<string> list = new List<string>();
		foreach (KeyValuePair<string, int> unlock in unlocks)
		{
			if (unlock.Value > 1)
			{
				list.Add($"{unlock.Key}_{unlock.Value}");
			}
			else
			{
				list.Add(unlock.Key);
			}
		}
		return list;
	}

	public UnlockSO GetUnlockOf(string name)
	{
		if (unlockedIn == null)
		{
			unlockedIn = new Dictionary<string, UnlockSO>();
			foreach (UnlockSO allUnlock in ResourceManager.GetAllUnlocks())
			{
				unlockedIn[allUnlock.unlockName] = allUnlock;
				foreach (string unlock in allUnlock.unlocks)
				{
					unlockedIn[unlock] = allUnlock;
				}
			}
		}
		return unlockedIn.GetValueOrDefault(name);
	}

	public bool IsUnlocked(string s)
	{
		return NumUnlocked(s.ToLower()) > 0;
	}

	public void AssertUnlocked(string dependency, int wordStart = -1, int wordEnd = -1)
	{
		if (IsUnlocked(dependency))
		{
			return;
		}
		string text = dependency.ToLower();
		UnlockSO unlockSO = null;
		foreach (UnlockSO allUnlock in ResourceManager.GetAllUnlocks())
		{
			if (allUnlock.unlocks.Contains(dependency) || allUnlock.unlocks.Contains(text) || allUnlock.unlockName == text)
			{
				unlockSO = allUnlock;
				break;
			}
		}
		if (unlockSO != null)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_missing_x_unlock", unlockSO), wordStart, wordEnd);
		}
		throw new ExecuteException(Localizer.Localize("error_missing_unlock"), wordStart, wordEnd);
	}

	public bool UnlockOrUpgrade(UnlockSO unlockSO, bool requireParent = true)
	{
		if ((requireParent && !string.IsNullOrEmpty(unlockSO.parentUnlock) && !IsUnlocked(unlockSO.parentUnlock)) || NumUnlocked(unlockSO) >= unlockSO.maxUnlockLevel || (sim.singleDrone && (unlockSO.unlockName == "megafarm" || unlockSO.unlockName == "expand")))
		{
			return false;
		}
		ItemBlock unlockCost = GetUnlockCost(unlockSO);
		if (unlockCost == null)
		{
			return false;
		}
		if (!Items.Remove(unlockCost))
		{
			return false;
		}
		Unlock(unlockSO.unlockName, NumUnlocked(unlockSO) + 1);
		UnlockAllIn(unlockSO);
		return true;
	}

	public void Unlock(string s, int level)
	{
		string text = s.ToLower();
		int num = NumUnlocked(text);
		if (num == level)
		{
			return;
		}
		unlocks[text] = level;
		if (allKeyWords.Contains(text))
		{
			unlockedKeyWords.Add(text);
		}
		if (allKeyWords.Contains(CodeUtilities.ToUpperSnake(text)))
		{
			unlockedKeyWords.Add(CodeUtilities.ToUpperSnake(text));
		}
		if (text == "expand")
		{
			grid.GenerateWorld(num > level);
			if (sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.UnlockAchievement("EXPAND");
				if (level >= 9)
				{
					Achievements.UnlockAchievement("BIG_FARM");
				}
			}
		}
		else if (text == "speed")
		{
			double num2 = MaxSpeedFactor();
			NumSpeedUpgrades = level;
			if (sim.SpeedFactor == num2)
			{
				sim.ChangeExecutionSpeed(MaxSpeedFactor());
			}
		}
	}

	public void UnlockAllIn(UnlockSO unlockSO)
	{
		foreach (string unlock in unlockSO.unlocks)
		{
			if (char.IsDigit(unlock[0]))
			{
				if (int.Parse(unlock[0].ToString()) <= NumUnlocked(unlockSO.unlockName))
				{
					Unlock(unlock.Substring(1), 1);
				}
			}
			else
			{
				Unlock(unlock, 1);
			}
		}
	}

	public void UnlockAll(IEnumerable<string> unlocks)
	{
		foreach (string unlock in unlocks)
		{
			Unlock(unlock, 1);
		}
	}

	public bool UnlockHat(HatSO hat)
	{
		if (IsUnlocked(hat.hatName))
		{
			return false;
		}
		Unlock(hat.hatName, 1);
		return true;
	}

	public Dictionary<string, int> GetUnlocks()
	{
		return new Dictionary<string, int>(unlocks);
	}

	public int NumUnlocked(UnlockSO unlockSO)
	{
		return unlocks.GetValueOrDefault(unlockSO.unlockName, 0);
	}

	public int NumUnlocked(string unlock)
	{
		return unlocks.GetValueOrDefault(unlock, 0);
	}

	public void ResetUnlocksToMax()
	{
		foreach (UnlockSO allUnlock in ResourceManager.GetAllUnlocks())
		{
			if (allUnlock.IsMultiUnlock && NumUnlocked(allUnlock) > allUnlock.maxUnlockLevel)
			{
				Unlock(allUnlock.unlockName, allUnlock.maxUnlockLevel);
			}
		}
	}

	public double MaxSpeedFactor()
	{
		double num = Math.Pow(1.5, NumSpeedUpgrades);
		if (Items.GetNumber(StringIds.PowerItemId) > 0.0)
		{
			num *= 2.0;
		}
		return num;
	}

	private void UsePower()
	{
		if (sim.farm.Items.GetNumber(StringIds.PowerItemId) > 0.0 && !sim.farm.Items.Remove(StringIds.PowerItemId, UsedPower))
		{
			sim.farm.Items.SetNumber(StringIds.PowerItemId, 0.0);
			if (sim.SpeedFactor > sim.farm.MaxSpeedFactor())
			{
				sim.ChangeExecutionSpeed(sim.farm.MaxSpeedFactor());
			}
		}
		UsedPower = 0.0;
		sim.StartTimer(UsePower, Duration.FromSeconds(0.2));
	}

	private void ReceiveWater()
	{
		if (NumUnlocked("watering") > 0)
		{
			Items.AddItem(StringIds.WaterItemId, sim.mainSim.harvestFactor);
		}
		sim.StartTimer(ReceiveWater, Duration.FromSeconds(20.0 / (double)(1 << NumUnlocked("watering"))));
	}

	private void ReceiveFertilizer()
	{
		if (NumUnlocked("fertilizer") > 0)
		{
			Items.AddItem(StringIds.FertilizerItemId, sim.mainSim.harvestFactor);
		}
		sim.StartTimer(ReceiveFertilizer, Duration.FromSeconds(20.0 / (double)(1 << NumUnlocked("fertilizer"))));
	}

	public int AddDrone(int droneId)
	{
		droneGeneration++;
		for (int i = 0; i < drones.Count; i++)
		{
			if (drones[i] == null)
			{
				drones[i] = new Drone(sim, drones[droneId].pos, i);
				return i;
			}
		}
		if (drones.Count >= Helper.NumDrones(NumUnlocked("megafarm")))
		{
			throw new ExecuteException(Localizer.Localize("error_max_drones_reached"));
		}
		Drone item = new Drone(sim, drones[droneId].pos, drones.Count);
		drones.Add(item);
		return drones.Count - 1;
	}

	public void RemoveSpawnedDrones()
	{
		for (int num = drones.Count - 1; num >= 0; num--)
		{
			if (num != mainDroneId)
			{
				if (drones[num] != null)
				{
					drones[num].hat.OnUnequip();
				}
				drones.RemoveAt(num);
			}
		}
		mainDroneId = 0;
		drones[0].DroneId = 0;
	}

	public void RemoveDrone(int droneId)
	{
		if (droneId == mainDroneId)
		{
			for (int i = 0; i < drones.Count; i++)
			{
				if (drones[i] != null && i != mainDroneId)
				{
					mainDroneId = i;
					break;
				}
			}
		}
		drones[droneId].hat.OnUnequip();
		drones[droneId] = null;
	}
}
public class FarmRenderer : MonoBehaviour
{
	[SerializeField]
	private Material material;

	[SerializeField]
	private Material propellerMaterial;

	[SerializeField]
	private Material golddenHatMaterial;

	[Header("Drone")]
	[SerializeField]
	private Mesh droneMesh;

	[SerializeField]
	private Mesh propellerMesh;

	[SerializeField]
	private Mesh hoverMesh;

	[SerializeField]
	private Mesh droneHighlightArrowMesh;

	[SerializeField]
	private Vector3 propellerOffset1;

	[SerializeField]
	private Vector3 propellerOffset2;

	[SerializeField]
	private Vector3 propellerOffset3;

	[SerializeField]
	private Vector3 propellerOffset4;

	[SerializeField]
	private bool renderDrones = true;

	[SerializeField]
	private bool renderFarm = true;

	private Dictionary<Mesh, List<Matrix4x4>> farmMeshes = new Dictionary<Mesh, List<Matrix4x4>>();

	private Dictionary<Mesh, List<Matrix4x4>> droneMeshes = new Dictionary<Mesh, List<Matrix4x4>>();

	private Dictionary<Mesh, List<Matrix4x4>> goldenHatMeshes = new Dictionary<Mesh, List<Matrix4x4>>();

	private List<Matrix4x4> propellerMeshes = new List<Matrix4x4>();

	private void Update()
	{
		Transform sceneScaler = MainSim.Inst.sceneScaler;
		foreach (Mesh key in farmMeshes.Keys)
		{
			farmMeshes[key].Clear();
		}
		foreach (Mesh key2 in droneMeshes.Keys)
		{
			droneMeshes[key2].Clear();
		}
		foreach (Mesh key3 in goldenHatMeshes.Keys)
		{
			goldenHatMeshes[key3].Clear();
		}
		propellerMeshes.Clear();
		if (!droneMeshes.ContainsKey(droneMesh))
		{
			droneMeshes[droneMesh] = new List<Matrix4x4>();
		}
		foreach (var droneMesh in MainSim.Inst.GetDroneMeshes())
		{
			Matrix4x4 matrix4x = sceneScaler.localToWorldMatrix * droneMesh.Item3;
			if (!IsMatrixValid(matrix4x))
			{
				continue;
			}
			Quaternion q = Quaternion.Euler(0f, 180f, 0f);
			droneMeshes[this.droneMesh].Add(matrix4x);
			if (droneMesh.Item1.isGolden)
			{
				if (!goldenHatMeshes.ContainsKey(droneMesh.Item1.hatMesh))
				{
					goldenHatMeshes[droneMesh.Item1.hatMesh] = new List<Matrix4x4>();
				}
				goldenHatMeshes[droneMesh.Item1.hatMesh].Add(matrix4x);
			}
			else
			{
				if (!droneMeshes.ContainsKey(droneMesh.Item1.hatMesh))
				{
					droneMeshes[droneMesh.Item1.hatMesh] = new List<Matrix4x4>();
				}
				droneMeshes[droneMesh.Item1.hatMesh].Add(matrix4x);
			}
			if (droneMesh.highlight)
			{
				droneMeshes[droneHighlightArrowMesh] = new List<Matrix4x4> { matrix4x };
			}
			Matrix4x4 item = matrix4x * Matrix4x4.Translate(propellerOffset1) * Matrix4x4.Rotate(q);
			propellerMeshes.Add(item);
			Matrix4x4 item2 = matrix4x * Matrix4x4.Translate(propellerOffset2);
			propellerMeshes.Add(item2);
			Matrix4x4 item3 = matrix4x * Matrix4x4.Translate(propellerOffset3) * Matrix4x4.Rotate(q);
			propellerMeshes.Add(item3);
			Matrix4x4 item4 = matrix4x * Matrix4x4.Translate(propellerOffset4);
			propellerMeshes.Add(item4);
		}
		foreach (var farmMesh in MainSim.Inst.GetFarmMeshes())
		{
			if (!farmMeshes.ContainsKey(farmMesh.Item1))
			{
				farmMeshes[farmMesh.Item1] = new List<Matrix4x4>();
			}
			farmMeshes[farmMesh.Item1].Add(sceneScaler.localToWorldMatrix * farmMesh.Item2);
		}
		if (renderFarm)
		{
			foreach (Mesh key4 in farmMeshes.Keys)
			{
				for (int i = 0; i < farmMeshes[key4].Count; i += 1023)
				{
					int count = Mathf.Min(1023, farmMeshes[key4].Count - i);
					Graphics.DrawMeshInstanced(key4, 0, material, farmMeshes[key4].GetRange(i, count));
				}
			}
		}
		if (renderDrones)
		{
			foreach (Mesh key5 in droneMeshes.Keys)
			{
				for (int j = 0; j < droneMeshes[key5].Count; j += 1023)
				{
					int count2 = Mathf.Min(1023, droneMeshes[key5].Count - j);
					Graphics.DrawMeshInstanced(key5, 0, material, droneMeshes[key5].GetRange(j, count2));
				}
			}
			foreach (Mesh key6 in goldenHatMeshes.Keys)
			{
				for (int k = 0; k < goldenHatMeshes[key6].Count; k += 1023)
				{
					int count3 = Mathf.Min(1023, goldenHatMeshes[key6].Count - k);
					Graphics.DrawMeshInstanced(key6, 0, golddenHatMaterial, goldenHatMeshes[key6].GetRange(k, count3));
				}
			}
			for (int l = 0; l < propellerMeshes.Count; l += 1023)
			{
				int count4 = Mathf.Min(1023, propellerMeshes.Count - l);
				Graphics.DrawMeshInstanced(propellerMesh, 0, propellerMaterial, propellerMeshes.GetRange(l, count4));
			}
		}
		if (MainSim.Inst.hoveredCell.x >= 0 && MainSim.Inst.hoveredCell.y >= 0)
		{
			Graphics.DrawMesh(hoverMesh, sceneScaler.localToWorldMatrix * Matrix4x4.Translate(new Vector3(-MainSim.Inst.hoveredCell.x, MainSim.Inst.hoveredCell.y, 0f)), material, 0);
		}
	}

	private bool IsMatrixValid(Matrix4x4 m)
	{
		for (int i = 0; i < 16; i++)
		{
			float f = m[i];
			if (float.IsNaN(f) || float.IsInfinity(f))
			{
				return false;
			}
		}
		return true;
	}
}
public class GridManager
{
	private const double MAX_WATER_VOLUME = 1.0;

	private const double WATER_DECAY_INTERVAL = 0.1;

	private const double WATER_DECAY_PROBABILITY = 0.1;

	private const double WATER_DECAY_FACTOR = 0.99;

	public Farm farm;

	public PumpkinController pumpkinController;

	private static Dictionary<string, Type> farmObjectTypes;

	private int sizeLimit;

	public Dictionary<Vector2Int, FarmObject> entities = new Dictionary<Vector2Int, FarmObject>();

	public Dictionary<Vector2Int, FarmObject> grounds = new Dictionary<Vector2Int, FarmObject>();

	public double[,] waterVolume;

	public int[,] cactusNumbers;

	public bool hadIncorrectSunflowerHarvest;

	public Vector2Int WorldSize
	{
		get
		{
			int num = Helper.WorldSizeScale(farm.NumUnlocked("expand"));
			if (sizeLimit > 0 && sizeLimit < num)
			{
				return new Vector2Int(sizeLimit, sizeLimit);
			}
			if (num != 2)
			{
				return new Vector2Int(num, num);
			}
			return new Vector2Int(1, 3);
		}
	}

	public int SizeLimit
	{
		get
		{
			return sizeLimit;
		}
		set
		{
			if (value > 2)
			{
				if (value < WorldSize.y)
				{
					sizeLimit = value;
					GenerateWorld(shrinkFarm: true);
				}
				else if (value > WorldSize.y)
				{
					sizeLimit = value;
					GenerateWorld();
				}
			}
			else if (sizeLimit > 0)
			{
				sizeLimit = 0;
				GenerateWorld();
			}
		}
	}

	public Vector3 midPoint => (CellToLocal(WorldSize) + CellToLocal(Vector2Int.zero) + Vector3.left) / 2f;

	public GridManager(Farm farm, List<SFO> loadedGrounds = null, List<SFO> loadedEntities = null)
	{
		this.farm = farm;
		farm.grid = this;
		pumpkinController = new PumpkinController(this);
		GenerateWorld(shrinkFarm: true);
		if (loadedGrounds != null && loadedGrounds.Count > 0)
		{
			ClearGrid(spawnGrass: false);
			foreach (SFO loadedGround in loadedGrounds)
			{
				LoadFromString(loadedGround.pos, loadedGround.data, isGround: true);
			}
		}
		if (loadedEntities != null)
		{
			foreach (SFO loadedEntity in loadedEntities)
			{
				LoadFromString(loadedEntity.pos, loadedEntity.data, isGround: false);
			}
		}
		farm.sim.StartTimer(WaterDecay, Duration.FromSeconds(0.1));
	}

	public void SetWaterVolume(Vector2Int pos, double volume)
	{
		double num = waterVolume[pos.x, pos.y];
		waterVolume[pos.x, pos.y] = Math.Clamp(volume, 0.0, 1.0);
		if (waterVolume[pos.x, pos.y] != num && entities.TryGetValue(pos, out var value) && value is Growable growable)
		{
			growable.UpdateFarmObject();
		}
	}

	private void WaterDecay()
	{
		for (int i = 0; i < waterVolume.GetLength(0); i++)
		{
			for (int j = 0; j < waterVolume.GetLength(1); j++)
			{
				Vector2Int pos = new Vector2Int(i, j);
				if (farm.sim.randomVarious.NextDouble() < 0.1)
				{
					SetWaterVolume(pos, waterVolume[i, j] * 0.99);
				}
			}
		}
		farm.sim.StartTimer(WaterDecay, Duration.FromSeconds(0.1));
	}

	public void ClearGrid(bool spawnGrass = true)
	{
		Vector2Int worldSize = WorldSize;
		for (int i = 0; i < worldSize.x; i++)
		{
			for (int j = 0; j < worldSize.y; j++)
			{
				Vector2Int vector2Int = new Vector2Int(i, j);
				if (!grounds.ContainsKey(vector2Int) || grounds[vector2Int].objectSO.objectName != "grassland")
				{
					SetGround(vector2Int, "grassland");
				}
				if (spawnGrass)
				{
					SetEntity(vector2Int, "grass");
				}
				else
				{
					RemoveEntity(vector2Int, regrowGrass: false);
				}
			}
		}
	}

	public void GenerateWorld(bool shrinkFarm = false)
	{
		if (shrinkFarm)
		{
			Vector2Int[] array = grounds.Keys.ToArray();
			foreach (Vector2Int vector2Int in array)
			{
				if (!IsWithinBounds(vector2Int))
				{
					Free(grounds[vector2Int]);
					grounds.Remove(vector2Int);
					if (entities.ContainsKey(vector2Int))
					{
						RemoveEntity(vector2Int, regrowGrass: false);
					}
				}
			}
		}
		Vector2Int worldSize = WorldSize;
		double[,] array2 = new double[WorldSize.x, WorldSize.y];
		for (int j = 0; j < worldSize.x; j++)
		{
			for (int k = 0; k < worldSize.y; k++)
			{
				if (waterVolume == null || j >= waterVolume.GetLength(0) || k >= waterVolume.GetLength(1))
				{
					array2[j, k] = 0.0;
				}
				else
				{
					array2[j, k] = waterVolume[j, k];
				}
			}
		}
		waterVolume = array2;
		int[,] array3 = new int[WorldSize.x, WorldSize.y];
		for (int l = 0; l < worldSize.x; l++)
		{
			for (int m = 0; m < worldSize.y; m++)
			{
				if (cactusNumbers == null || l >= cactusNumbers.GetLength(0) || m >= cactusNumbers.GetLength(1))
				{
					array3[l, m] = -1;
				}
				else
				{
					array3[l, m] = cactusNumbers[l, m];
				}
			}
		}
		cactusNumbers = array3;
		ClearGrid();
	}

	public bool Swap(Vector2Int pos, GridDirection dir)
	{
		FarmObject valueOrDefault = farm.grid.entities.GetValueOrDefault(pos);
		Vector2Int vector2Int = pos + dir.GetDirectionVector();
		if (!IsWithinBounds(vector2Int))
		{
			return false;
		}
		FarmObject valueOrDefault2 = farm.grid.entities.GetValueOrDefault(vector2Int);
		if ((valueOrDefault != null && !valueOrDefault.objectSO.canBeSwapped) || (valueOrDefault2 != null && !valueOrDefault2.objectSO.canBeSwapped))
		{
			return false;
		}
		if (farm.sim.mainSim != null && farm.sim.mainSim.TimeFactor == 1.0)
		{
			farm.sim.mainSim.PlayEffect(VFXType.light_dust, CellToLocal(pos));
			farm.sim.mainSim.PlayEffect(VFXType.light_dust, CellToLocal(vector2Int));
		}
		int num = cactusNumbers[pos.x, pos.y];
		cactusNumbers[pos.x, pos.y] = cactusNumbers[vector2Int.x, vector2Int.y];
		cactusNumbers[vector2Int.x, vector2Int.y] = num;
		if (valueOrDefault != null)
		{
			farm.grid.entities[vector2Int] = valueOrDefault;
			valueOrDefault.AnimateMove(CellToLocal(vector2Int), Duration.FromSeconds(0.1));
			valueOrDefault.pos = vector2Int;
			valueOrDefault.UpdateFarmObject();
			valueOrDefault.UpdateNeighbors();
			valueOrDefault.OnSwapped();
		}
		else
		{
			farm.grid.entities.Remove(vector2Int);
		}
		if (valueOrDefault2 != null)
		{
			farm.grid.entities[pos] = valueOrDefault2;
			valueOrDefault2.AnimateMove(CellToLocal(pos), Duration.FromSeconds(0.1));
			valueOrDefault2.pos = pos;
			valueOrDefault2.UpdateFarmObject();
			valueOrDefault2.UpdateNeighbors();
			valueOrDefault2.OnSwapped();
		}
		else
		{
			farm.grid.entities.Remove(pos);
		}
		return true;
	}

	public FarmObject SetGround(Vector2Int pos, string newGround)
	{
		if (grounds.GetValueOrDefault(pos) != null)
		{
			Free(grounds[pos]);
		}
		return SetFarmObject(pos, newGround, isGround: true);
	}

	public FarmObject SetEntity(Vector2Int pos, string newObject)
	{
		if (entities.GetValueOrDefault(pos) != null)
		{
			Free(entities[pos]);
		}
		return SetFarmObject(pos, newObject, isGround: false);
	}

	public void RemoveEntity(Vector2Int pos, bool regrowGrass = true)
	{
		if (entities.ContainsKey(pos))
		{
			Free(entities[pos]);
			if (regrowGrass && grounds[pos].objectSO.objectName == "grassland")
			{
				SetEntity(pos, "grass");
			}
		}
	}

	public Vector2Int[] NeighborPositions(Vector2Int pos)
	{
		return new Vector2Int[4]
		{
			pos + new Vector2Int(0, 1),
			pos + new Vector2Int(1, 0),
			pos + new Vector2Int(0, -1),
			pos + new Vector2Int(-1, 0)
		};
	}

	public FarmObject[] GetNeighbors(Vector2Int pos)
	{
		FarmObject[] array = new FarmObject[4];
		entities.TryGetValue(pos + new Vector2Int(0, 1), out array[0]);
		entities.TryGetValue(pos + new Vector2Int(1, 0), out array[1]);
		entities.TryGetValue(pos + new Vector2Int(0, -1), out array[2]);
		entities.TryGetValue(pos + new Vector2Int(-1, 0), out array[3]);
		return array;
	}

	public Vector2Int Wrap(Vector2Int pos)
	{
		return new Vector2Int((pos.x + WorldSize.x) % WorldSize.x, (pos.y + WorldSize.y) % WorldSize.y);
	}

	public bool IsWithinBounds(Vector2Int pos)
	{
		if (pos.x >= 0 && pos.y >= 0 && pos.x < WorldSize.x)
		{
			return pos.y < WorldSize.y;
		}
		return false;
	}

	public static Vector3 CellToLocal(Vector2Int pos)
	{
		return new Vector3(-pos.x, pos.y, 0f);
	}

	public static Vector2Int LocalToCell(Vector3 localPos)
	{
		return new Vector2Int(Mathf.RoundToInt(0f - localPos.x), Mathf.RoundToInt(localPos.y));
	}

	private void LoadFromString(Vector2Int pos, string s, bool isGround)
	{
		if (string.IsNullOrEmpty(s) || pos.x >= WorldSize.x || pos.y >= WorldSize.y)
		{
			return;
		}
		Dictionary<string, string> dictionary = new Dictionary<string, string>();
		string[] array = s.Split(',');
		for (int i = 0; i < array.Length; i++)
		{
			string[] array2 = array[i].Split(" = ");
			if (array2.Length == 2)
			{
				dictionary[array2[0]] = array2[1];
			}
		}
		if (dictionary.ContainsKey("type"))
		{
			if (isGround)
			{
				SetGround(pos, dictionary["type"]);
				grounds[pos].SetValues(dictionary);
			}
			else
			{
				SetEntity(pos, dictionary["type"]);
				entities[pos].SetValues(dictionary);
			}
		}
	}

	private FarmObject CreateFarmObject(FarmObjectSO objectSO)
	{
		if (farmObjectTypes == null)
		{
			farmObjectTypes = (from type in typeof(FarmObject).Assembly.GetTypes()
				where type.IsSubclassOf(typeof(FarmObject)) || type == typeof(FarmObject)
				select type).ToDictionary((Type t) => t.Name, (Type t) => t);
		}
		return (FarmObject)Activator.CreateInstance(farmObjectTypes[objectSO.className]);
	}

	private FarmObject SetFarmObject(Vector2Int pos, string objName, bool isGround)
	{
		FarmObjectSO farmObject = ResourceManager.GetFarmObject(objName);
		FarmObject farmObject2 = CreateFarmObject(farmObject);
		farmObject2.objectSO = farmObject;
		farmObject2.pos = pos;
		farmObject2.LocalPosition = CellToLocal(pos);
		farmObject2.sim = farm.sim;
		if (isGround)
		{
			grounds[pos] = farmObject2;
		}
		else
		{
			entities[pos] = farmObject2;
		}
		farmObject2.OnRestart();
		if (farm.sim.mainSim != null)
		{
			farm.sim.mainSim.dirty = true;
		}
		return farmObject2;
	}

	public void Free(FarmObject obj)
	{
		if (entities.GetValueOrDefault(obj.pos) == obj)
		{
			entities.Remove(obj.pos);
		}
		obj.OnFree();
	}

	public void PrintGrid()
	{
		StringBuilder stringBuilder = new StringBuilder();
		for (int i = 0; i < WorldSize.y; i++)
		{
			for (int j = 0; j < WorldSize.x; j++)
			{
				if (j != 0)
				{
					stringBuilder.Append(" ");
				}
				if (entities.TryGetValue(new Vector2Int(j, i), out var value))
				{
					stringBuilder.Append(value.objectSO.objectName.First());
				}
				else
				{
					stringBuilder.Append("-");
				}
			}
			stringBuilder.Append("\n");
		}
		UnityEngine.Debug.Log(stringBuilder.ToString());
	}
}
public class ItemEffect : MonoBehaviour
{
	[SerializeField]
	private MeshFilter meshFilter;

	public void Setup(int itemId)
	{
		ItemSO item = ResourceManager.GetItem(itemId);
		meshFilter.mesh = item.mesh;
	}
}
public class MainSim : MonoBehaviour
{
	public class LeaderboardStartArgs
	{
		public string fileName;

		public IEnumerable<string> unlocks;

		public ItemBlock items;

		public List<KeyValuePair<string, IPyObject>> globals;

		public string leaderboardName;

		public string steamLeaderboardName;

		public LeaderboardType leaderboardType;

		public int seed;

		public bool singleDrone;

		public LeaderboardStartArgs(string fileName, IEnumerable<string> unlocks, ItemBlock items, List<KeyValuePair<string, IPyObject>> globals, string leaderboardName, string steamLeaderboardName, LeaderboardType leaderboardType, int seed = -1, bool singleDrone = false)
		{
			this.fileName = fileName;
			this.unlocks = unlocks;
			this.items = items;
			this.globals = globals;
			this.leaderboardName = leaderboardName;
			this.steamLeaderboardName = steamLeaderboardName;
			this.leaderboardType = leaderboardType;
			this.seed = seed;
			this.singleDrone = singleDrone;
		}
	}

	private static MainSim _instance;

	private const float MAX_SIM_TIME_PER_FRAME = 0.2f;

	private const long MIN_LEADERBOARD_TIME = 7200000000000L;

	public PiggyBank pb;

	public Transform sceneScaler;

	public LeaderboardManager leaderboardManager;

	public Workspace workspace;

	public WarningPopup warningPopup;

	public WarningIcon warningIcon;

	public ResearchMenu researchMenu;

	public Menu menu;

	public BlinkManager blinkManager;

	[NonSerialized]
	public Camera mainCamera;

	public Inventory inv;

	private ConcurrentQueue<HatSO> hatsToUnlock = new ConcurrentQueue<HatSO>();

	public int harvestFactor = 1;

	[SerializeField]
	private double timeFactor = 1.0;

	[NonSerialized]
	public Vector2Int hoveredCell = new Vector2Int(-1, -1);

	private double lastHoveredTime;

	private Simulation sim;

	public Simulation storedSim;

	private Duration goalTime;

	public Duration totalLeaderboardTime;

	public int numLeaderboardRuns;

	private bool leaderboardCancelled;

	private LeaderboardStartArgs startLeaderboardNow;

	private LeaderboardStartArgs prevLeaderboardStart;

	private CodeWindow activeCodeWindow;

	public int executionId;

	public volatile bool dirty;

	private object lockSimulation = new object();

	private volatile bool disposed;

	private bool prevStepByStepMode;

	public static MainSim Inst => _instance;

	public double TimeFactor
	{
		get
		{
			return timeFactor;
		}
		set
		{
			if (value < 0.0 || value > 1000000.0 || double.IsNaN(value) || double.IsInfinity(value))
			{
				timeFactor = 1000000.0;
			}
			else if (value < 0.01)
			{
				timeFactor = 0.01;
			}
			else
			{
				timeFactor = value;
			}
		}
	}

	public bool StepByStepMode
	{
		get
		{
			lock (lockSimulation)
			{
				if (sim.IsExecuting())
				{
					return sim.stepByStepMode;
				}
				return false;
			}
		}
		set
		{
			lock (lockSimulation)
			{
				if (sim.IsExecuting() && sim.stepByStepMode != value)
				{
					sim.stepByStepMode = value;
					sim.NextExecutionStep();
				}
			}
		}
	}

	private void Awake()
	{
		if (_instance != null && _instance != this)
		{
			UnityEngine.Object.Destroy(base.gameObject);
		}
		else
		{
			_instance = this;
		}
		mainCamera = Camera.main;
	}

	private void Start()
	{
		Thread thread = new Thread(SimulationLoop);
		thread.IsBackground = true;
		thread.Priority = System.Threading.ThreadPriority.AboveNormal;
		thread.Start();
	}

	private void SimulationLoop()
	{
		while (!disposed)
		{
			sim.RunNextStep(goalTime, lockSimulation, sim.leaderboardType != LeaderboardType.none);
		}
	}

	private void OnDestroy()
	{
		disposed = true;
	}

	private void Update()
	{
		Saver.ApplyCodeChanges(workspace);
		lock (lockSimulation)
		{
			float num = Mathf.Min(Time.deltaTime, 0.2f);
			goalTime = sim.CurrentTime + Duration.FromSeconds((double)num * TimeFactor);
			if (sim.leaderboardType != LeaderboardType.none && !sim.IsExecuting())
			{
				LeaderboardExecutionFinished();
			}
			if (startLeaderboardNow != null)
			{
				StartLeaderboard(startLeaderboardNow);
				startLeaderboardNow = null;
			}
			activeCodeWindow?.SetExecutionColor();
			if (sim.IsExecuting() && sim.Execution.MainState != null && sim.Execution.MainState.CurrentExecutingNode?.boxedParams.codeWindow != activeCodeWindow)
			{
				CodeWindow codeWindow = sim.Execution.MainState.CurrentExecutingNode?.boxedParams.codeWindow;
				if (codeWindow != null)
				{
					activeCodeWindow = codeWindow;
					activeCodeWindow.StartExecutionMode(closeErrors: false);
					if (StepByStepMode)
					{
						activeCodeWindow.StartStepByStepMode();
					}
					Transform obj = activeCodeWindow.transform;
					obj.SetSiblingIndex(obj.parent.childCount - 1);
				}
			}
			else if (!sim.IsExecuting() && activeCodeWindow != null)
			{
				activeCodeWindow = null;
				foreach (CodeWindow value in workspace.codeWindows.Values)
				{
					value.StopExecutionMode();
				}
			}
			if (prevStepByStepMode != StepByStepMode)
			{
				foreach (CodeWindow value2 in workspace.codeWindows.Values)
				{
					if (value2.isExecuting)
					{
						if (StepByStepMode)
						{
							value2.StartStepByStepMode();
						}
						else
						{
							value2.StartExecutionMode();
						}
					}
				}
				prevStepByStepMode = StepByStepMode;
			}
			if (sim.farm != null && sim.farm.drones != null && sim.leaderboardType == LeaderboardType.none)
			{
				FMODSoundManager.UpdateDroneParams((from d in sim.farm.drones
					where d != null
					select d.GetSpeedAndPos(Time.time)).ToArray());
				FMODSoundManager.SetGameSpeedParam((float)(Duration.FromSeconds(0.0025) / sim.OpDuration * (double)sim.farm.drones.Where((Drone d) => d != null).Count()));
			}
			Vector2Int vector2Int = GetHoveredCell();
			if (!Input.GetMouseButton(0) && !Input.GetMouseButton(1) && sim.farm.grid.IsWithinBounds(vector2Int))
			{
				bool flag = workspace.tooltip.CanShowTooltipImmediate();
				if (vector2Int != hoveredCell)
				{
					hoveredCell = vector2Int;
					lastHoveredTime = Time.time;
				}
				else if ((double)Time.time - lastHoveredTime > 0.4000000059604645)
				{
					hoveredCell = vector2Int;
					if (!menu.gameObject.activeInHierarchy && !researchMenu.IsOpen)
					{
						workspace.tooltip.SetTooltipImmediate(GetHoveredTooltip());
					}
					else
					{
						flag = false;
					}
				}
				if (flag)
				{
					hoveredCell = vector2Int;
				}
				else
				{
					hoveredCell = new Vector2Int(-1, -1);
				}
			}
			else
			{
				hoveredCell = new Vector2Int(-1, -1);
				workspace.tooltip.SetTooltipImmediate(null);
			}
			if (hatsToUnlock.TryDequeue(out var result) && sim.farm != null)
			{
				if (IsSimulating() && storedSim != null)
				{
					if (storedSim.farm.UnlockHat(result))
					{
						HatPopup.Inst.ShowPopup(result);
					}
				}
				else if (sim.farm.UnlockHat(result) || result.hatName == "the_farmers_remains")
				{
					HatPopup.Inst.ShowPopup(result);
				}
			}
			Monitor.Pulse(lockSimulation);
		}
	}

	public void SetupSim(IEnumerable<string> unlocks, ItemBlock items, List<SFO> loadedGrounds = null, List<SFO> loadedEntities = null, bool resetUnlocks = false)
	{
		lock (lockSimulation)
		{
			sim = new Simulation(this, unlocks, items, "", "", LeaderboardType.none, -1, loadedGrounds, loadedEntities, resetUnlocks);
			foreach (UnlockSO allUnlock in ResourceManager.GetAllUnlocks())
			{
				if (sim.farm.IsUnlocked(allUnlock.unlockName))
				{
					researchMenu.openedUnlockDocs.Add(allUnlock.docs);
				}
			}
			if (sim.farm.NumUnlocked("expand") >= 2)
			{
				researchMenu.openedUnlockDocs.Add("docs/unlocks/expand_2.md");
			}
		}
	}

	private void StartLeaderboard(LeaderboardStartArgs startArgs)
	{
		if (workspace.codeWindows.TryGetValue(startArgs.fileName, out var value))
		{
			Node node = value.Parse();
			if (node != null && node != null)
			{
				if (startArgs.leaderboardType != LeaderboardType.simulation)
				{
					StopMainExecution();
				}
				else
				{
					sim.Paused = true;
				}
				storedSim = sim;
				sim = new Simulation(this, startArgs.unlocks, startArgs.items, startArgs.leaderboardName, startArgs.steamLeaderboardName, startArgs.leaderboardType, startArgs.seed)
				{
					singleDrone = startArgs.singleDrone
				};
				Execution execution = new Execution(sim, node, executionId);
				executionId++;
				value.StartExecutionMode();
				foreach (KeyValuePair<string, IPyObject> global in startArgs.globals)
				{
					Dictionary<object, object> copies = new Dictionary<object, object>();
					execution.MainState.moduleState.globalScope.SetVar(global.Key, global.Value.DeepCopy(copies), checkShadow: false);
				}
				sim.StartProgramExecution(execution);
				goalTime = Duration.FromSeconds(0.0);
				prevLeaderboardStart = startArgs;
				prevLeaderboardStart.items = new ItemBlock(prevLeaderboardStart.items);
				leaderboardManager.StartLeaderboardRun(startArgs.leaderboardType != LeaderboardType.simulation);
				return;
			}
		}
		sim.Paused = false;
		TimeFactor = 1.0;
	}

	public void ScheduleLeaderboardStart(LeaderboardStartArgs startArgs)
	{
		startLeaderboardNow = startArgs;
	}

	private void LeaderboardExecutionFinished()
	{
		if (!leaderboardManager.IsRunning)
		{
			return;
		}
		double num = TimeFactor;
		TimeFactor = 1.0;
		if (sim.leaderboardType != LeaderboardType.simulation)
		{
			sim.Paused = true;
			bool flag = sim.leaderboardType switch
			{
				LeaderboardType.reset => sim.farm.IsUnlocked("leaderboard"), 
				LeaderboardType.farm_resources => sim.farm.Items.Contains(ResourceManager.GetLeaderboard(sim.leaderboardName).goalItems), 
				_ => false, 
			};
			totalLeaderboardTime += sim.CurrentTime;
			numLeaderboardRuns++;
			if (leaderboardCancelled)
			{
				leaderboardCancelled = false;
				flag = false;
			}
			if (totalLeaderboardTime >= new Duration(7200000000000L) || !flag)
			{
				leaderboardManager.StopLeaderboardRun(flag, sim.leaderboardName, sim.steamLeaderboardName, totalLeaderboardTime.ToTimeSpan() / numLeaderboardRuns);
				totalLeaderboardTime = new Duration(0L);
				numLeaderboardRuns = 0;
				return;
			}
			_ = sim.leaderboardName;
			_ = sim.leaderboardType;
			int seed = Mathf.Abs(sim.randomVarious.Next() + sim.randomSunflower.Next() + sim.randomSnake.Next() + sim.randomRandom.Next() + sim.randomPumpkin.Next() + sim.randomPoly.Next() + sim.randomMaze.Next() + sim.randomCactus.Next());
			RestoreMainSim();
			prevLeaderboardStart.seed = seed;
			StartLeaderboard(prevLeaderboardStart);
			TimeFactor = num;
		}
		else
		{
			leaderboardManager.RemoveOverlay();
			if (storedSim.IsExecuting())
			{
				storedSim.Execution.MainState.ReturnValue = new PyNumber(sim.CurrentTime.Seconds);
			}
			RestoreMainSim();
			sim.Paused = false;
		}
	}

	public void RestoreMainSim()
	{
		lock (lockSimulation)
		{
			sim = storedSim;
			storedSim = null;
			goalTime = sim.CurrentTime;
		}
	}

	public void StartMainExecution(CodeWindow cw, Node syntaxTree)
	{
		lock (lockSimulation)
		{
			if (IsExecuting())
			{
				return;
			}
			activeCodeWindow = cw;
			if (activeCodeWindow != null)
			{
				activeCodeWindow.SetExecutionColor();
				activeCodeWindow.StartExecutionMode(closeErrors: false);
				if (StepByStepMode)
				{
					activeCodeWindow.StartStepByStepMode();
				}
				Transform obj = activeCodeWindow.transform;
				obj.SetSiblingIndex(obj.parent.childCount - 1);
			}
			Execution execution = new Execution(sim, syntaxTree, executionId);
			executionId++;
			Logger.Clear();
			sim.StartProgramExecution(execution);
		}
		if (sim.leaderboardType == LeaderboardType.none)
		{
			Achievements.UnlockAchievement("RUN_YOUR_FIRST_CODE");
		}
	}

	public void StopMainExecution()
	{
		lock (lockSimulation)
		{
			if (sim.leaderboardType != LeaderboardType.none && sim.leaderboardType != LeaderboardType.simulation)
			{
				leaderboardCancelled = true;
			}
			storedSim?.StopProgramExecution();
			sim.StopProgramExecution();
		}
	}

	public void PlaySound(SoundEffectType sound, Vector2Int farmPos)
	{
		if (TimeFactor < 2.0)
		{
			SoundManager.EnqueueSound(sound, GridManager.CellToLocal(farmPos));
		}
	}

	public void PlayEffect(VFXType effect, Vector3 localPos, bool changeColor = false, Color color = default(Color), string text = null)
	{
		if (TimeFactor < 2.0)
		{
			VFXManager.EnqueueEffect(effect, localPos, changeColor, color, text);
		}
	}

	public void CollectItemEffect(int item, Vector3 localPos)
	{
		if (TimeFactor < 2.0)
		{
			pb.EnqueueCollect(item, localPos);
		}
	}

	public void BlinkEffect(Node node)
	{
		blinkManager.EnqueueBlink(node);
	}

	public List<(FunctionNode func, Node callNode)> GetCallStack()
	{
		lock (lockSimulation)
		{
			if (!sim.IsExecuting())
			{
				return null;
			}
			lock (sim.Execution.lockExecution)
			{
				return sim.Execution?.MainState?.GetCallStack();
			}
		}
	}

	public bool IsUnlocked(string unlock)
	{
		lock (lockSimulation)
		{
			return sim.farm.IsUnlocked(unlock);
		}
	}

	public int NumUnlocked(string unlock)
	{
		lock (lockSimulation)
		{
			return sim.farm.NumUnlocked(unlock);
		}
	}

	public Dictionary<string, int> GetUnlocks()
	{
		lock (lockSimulation)
		{
			return sim.farm.GetUnlocks();
		}
	}

	public double GetNumItem(int itemId)
	{
		lock (lockSimulation)
		{
			return sim.farm.Items.GetNumber(itemId);
		}
	}

	public ItemBlock GetInventory()
	{
		lock (lockSimulation)
		{
			return new ItemBlock(sim.farm.Items);
		}
	}

	public HashSet<string> GetUnlockedKeywords()
	{
		lock (lockSimulation)
		{
			return new HashSet<string>(sim.farm.unlockedKeyWords);
		}
	}

	public ItemBlock GetUnlockCost(UnlockSO unlock)
	{
		lock (lockSimulation)
		{
			return sim.farm.GetUnlockCost(unlock);
		}
	}

	public bool EvaluateName(string name, out IPyObject value)
	{
		lock (lockSimulation)
		{
			if (sim.IsExecuting())
			{
				return sim.EvaluateName(name, out value);
			}
			value = null;
			return false;
		}
	}

	public void NextExecutionStep()
	{
		lock (lockSimulation)
		{
			sim.NextExecutionStep();
		}
	}

	public bool UnlockOrUpgrade(UnlockSO unlockSO)
	{
		lock (lockSimulation)
		{
			if (IsSimulating())
			{
				return false;
			}
			return sim.farm.UnlockOrUpgrade(unlockSO);
		}
	}

	public void UnlockHat(HatSO hatSO)
	{
		hatsToUnlock.Enqueue(hatSO);
	}

	public void ResetUnlocksToMax()
	{
		lock (lockSimulation)
		{
			if (!IsSimulating())
			{
				sim.farm.ResetUnlocksToMax();
			}
		}
	}

	public bool IsSimulating()
	{
		lock (lockSimulation)
		{
			return sim.leaderboardType != LeaderboardType.none;
		}
	}

	public bool MightBeSimulating()
	{
		return storedSim != null;
	}

	public bool IsExecuting()
	{
		lock (lockSimulation)
		{
			return sim.IsExecuting() || storedSim != null;
		}
	}

	public List<string> GetSerializedUnlocks()
	{
		lock (lockSimulation)
		{
			return sim.farm.SerializeUnlocks();
		}
	}

	public List<(Mesh, Matrix4x4)> GetFarmMeshes()
	{
		lock (lockSimulation)
		{
			List<(Mesh, Matrix4x4)> list = new List<(Mesh, Matrix4x4)>();
			foreach (FarmObject item in sim.farm.grid.entities.Values.Concat(sim.farm.grid.grounds.Values))
			{
				foreach (var mesh in item.GetMeshes())
				{
					list.Add(mesh);
				}
			}
			return list;
		}
	}

	public List<(HatSO, bool highlight, Matrix4x4)> GetDroneMeshes()
	{
		lock (lockSimulation)
		{
			List<(HatSO, bool, Matrix4x4)> list = new List<(HatSO, bool, Matrix4x4)>();
			foreach (Drone item in sim.farm.drones.Where((Drone d) => d != null))
			{
				list.Add((item.hat.hatSO, IsExecuting() && sim.farm.mainDroneId == item.DroneId && (sim.Paused || StepByStepMode), item.GetTransform()));
			}
			return list;
		}
	}

	public Duration GetCurrentTime()
	{
		lock (lockSimulation)
		{
			return sim.CurrentTime;
		}
	}

	public Vector2Int GetWorldSize()
	{
		lock (lockSimulation)
		{
			return sim.farm.grid.WorldSize;
		}
	}

	private TooltipInfo GetHoveredTooltip()
	{
		ItemBlock itemBlock = null;
		if (sim.farm.grid.IsWithinBounds(hoveredCell))
		{
			StringBuilder stringBuilder = new StringBuilder();
			stringBuilder.Append("`x = ").Append(hoveredCell.x).Append(", y = ")
				.Append(hoveredCell.y)
				.Append("`")
				.Append("\n\n");
			if (sim.farm.grid.entities.TryGetValue(hoveredCell, out var value))
			{
				stringBuilder.Append("### `").Append(CodeUtilities.ToNiceString(value.objectSO)).Append("`");
				if (value is Growable growable && value.objectSO.className != "Apple")
				{
					stringBuilder.Append("\n").Append(CodeUtilities.LocalizeAndFormat("runtime_growable_tooltip", new PyNumber(growable.GrowTime.Seconds), new PyNumber(growable.GrownPercent * 100.0)));
				}
				IPyObject pyObject = value.Measure();
				if (pyObject != null && !(pyObject is PyNone) && IsUnlocked("measure"))
				{
					stringBuilder.Append("\n");
					stringBuilder.Append("`measure(): " + CodeUtilities.ToNiceString(pyObject) + "`");
				}
				stringBuilder.Append("\n").Append(Localizer.Localize("runtime_entity_tooltip"));
				stringBuilder.Append("\n\n");
				itemBlock = value.GetYield();
			}
			stringBuilder.Append("### `").Append(CodeUtilities.ToNiceString(sim.farm.grid.grounds[hoveredCell].objectSO)).Append("`")
				.Append("\n")
				.Append(CodeUtilities.LocalizeAndFormat("runtime_ground_tooltip", new PyNumber(sim.farm.grid.waterVolume[hoveredCell.x, hoveredCell.y])));
			return new TooltipInfo(stringBuilder.ToString(), 0.2f)
			{
				itemBlock = itemBlock
			};
		}
		hoveredCell = new Vector2Int(-1, -1);
		return null;
	}

	private Vector2Int GetHoveredCell()
	{
		Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);
		return GridManager.LocalToCell((ray.origin + ray.direction * ((0f - ray.origin.z + base.transform.position.z) / ray.direction.z) - base.transform.position) / sceneScaler.localScale.x);
	}
}
public class PiggyBank : MonoBehaviour
{
	private struct ActiveEffect
	{
		public ItemEffect effect;

		public float speed;

		public float zVelocity;

		public ActiveEffect(ItemEffect effect, float zVelocity, float speed)
		{
			this.effect = effect;
			this.zVelocity = zVelocity;
			this.speed = speed;
		}
	}

	[SerializeField]
	private float maxSpeed;

	[SerializeField]
	private float acceleration;

	[SerializeField]
	private float accelerationTowardsCursor;

	[SerializeField]
	private float maxRotation;

	[SerializeField]
	private float maxDistance;

	[SerializeField]
	private float effectAcceleration;

	[SerializeField]
	private float effectStartZVelocity;

	[SerializeField]
	private float effectGravity;

	[SerializeField]
	private float effectMaxSpeed;

	[SerializeField]
	private float effectShrinkSpeed;

	[SerializeField]
	private AnimationCurve throwZCurve;

	[SerializeField]
	private Transform piggyMesh;

	[SerializeField]
	private Camera cam;

	[SerializeField]
	private Transform slot;

	[SerializeField]
	private AudioClip sellSound;

	[SerializeField]
	private ItemEffect itemEffectPrefab;

	private Stack<ItemEffect> itemPool = new Stack<ItemEffect>();

	private List<ActiveEffect> activeEffects = new List<ActiveEffect>();

	private Vector3 velLocal;

	private ConcurrentQueue<(int, Vector3)> collectQueue = new ConcurrentQueue<(int, Vector3)>();

	public Vector3 Position => piggyMesh.localPosition;

	private void Update()
	{
		(int, Vector3) result;
		while (collectQueue.TryDequeue(out result))
		{
			CollectItem(result.Item1, result.Item2);
		}
		Ray ray = cam.ScreenPointToRay(Input.mousePosition);
		Vector3 position = (Vector3)(-(Vector2)ray.direction * ((ray.origin.z - piggyMesh.position.z) / ray.direction.z)) + ray.origin;
		position = MainSim.Inst.sceneScaler.InverseTransformPoint(position);
		position.z = piggyMesh.localPosition.z;
		bool flag = (piggyMesh.localPosition - position).magnitude < maxDistance;
		Vector3 vector = (flag ? position : MainSim.Inst.GetDroneMeshes()[0].Item3.GetPosition()) - piggyMesh.localPosition;
		vector.z = 0f;
		velLocal += vector * Time.deltaTime * (flag ? accelerationTowardsCursor : acceleration);
		velLocal = velLocal.normalized * Mathf.Min(velLocal.magnitude, maxSpeed);
		piggyMesh.localPosition += velLocal * Time.deltaTime;
		Quaternion to = Quaternion.AngleAxis(Mathf.Atan2(velLocal.y, velLocal.x) * 57.29578f + 180f, Vector3.forward);
		piggyMesh.localRotation = Quaternion.RotateTowards(piggyMesh.localRotation, to, maxRotation * Time.deltaTime);
		for (int num = activeEffects.Count - 1; num >= 0; num--)
		{
			ActiveEffect value = activeEffects[num];
			Vector3 vector2 = piggyMesh.position - value.effect.transform.position;
			if (vector2.magnitude < value.speed * Time.deltaTime)
			{
				EndCollect(activeEffects[num].effect);
				activeEffects.RemoveAt(num);
			}
			else
			{
				value.effect.transform.position += (value.speed * vector2.normalized + Vector3.forward * value.zVelocity) * Time.deltaTime;
				float num2 = Mathf.Max(value.effect.transform.localScale.x - effectShrinkSpeed * Time.deltaTime, 0.2f);
				value.effect.transform.localScale = new Vector3(num2, num2, num2);
				value.speed = Mathf.Min(value.speed + effectAcceleration * Time.deltaTime, effectMaxSpeed);
				value.zVelocity = Mathf.Max(value.zVelocity - effectGravity * Time.deltaTime, 0f);
				activeEffects[num] = value;
			}
		}
	}

	public void EnqueueCollect(int item, Vector3 localPos)
	{
		collectQueue.Enqueue((item, localPos));
	}

	private void CollectItem(int itemId, Vector3 localPos)
	{
		float num = OptionHolder.GetFloat("vfx limit", 50f);
		float num2 = (float)activeEffects.Count / num;
		float num3 = num2 * num2;
		if (!(UnityEngine.Random.Range(0f, 1f) < num3))
		{
			ItemEffect itemEffect = ((itemPool.Count <= 0) ? UnityEngine.Object.Instantiate(itemEffectPrefab, base.transform) : itemPool.Pop());
			itemEffect.Setup(itemId);
			itemEffect.transform.position = MainSim.Inst.sceneScaler.TransformPoint(localPos);
			itemEffect.transform.localScale = Vector3.one;
			itemEffect.gameObject.SetActive(value: true);
			activeEffects.Add(new ActiveEffect(itemEffect, effectStartZVelocity, 0f));
		}
	}

	private void EndCollect(ItemEffect obj)
	{
		obj.gameObject.SetActive(value: false);
		itemPool.Push(obj);
		VFXManager.Play(VFXType.coins, slot.localPosition + piggyMesh.localPosition);
		LeanTween.cancel(piggyMesh.gameObject);
		piggyMesh.localScale = Vector3.one;
		LeanTween.scale(piggyMesh.gameObject, Vector3.one * 1.2f, 0.1f).setLoopPingPong(1);
		FMODSoundManager.PlaySound(SoundEffectType.PickUpItem, piggyMesh.position / MainSim.Inst.sceneScaler.localScale.x);
	}
}
public class Simulation
{
	public class Timer
	{
		public Action func;

		public bool stopped;
	}

	public const double BASE_OP_DURATION = 0.0025;

	public Farm farm;

	private Execution execution;

	public MainSim mainSim;

	private bool hasError;

	private PriorityQueue<Timer, Duration> timers = new PriorityQueue<Timer, Duration>();

	public bool stepByStepMode;

	private System.Random random;

	public System.Random randomVarious;

	public System.Random randomMaze;

	public System.Random randomSnake;

	public System.Random randomCactus;

	public System.Random randomSunflower;

	public System.Random randomPumpkin;

	public System.Random randomPoly;

	public System.Random randomRandom;

	public string leaderboardName;

	public string steamLeaderboardName;

	public LeaderboardType leaderboardType;

	public bool singleDrone;

	public double SpeedFactor { get; private set; } = 1.0;

	public Duration OpDuration { get; private set; } = Duration.FromSeconds(0.0025);

	public Duration CurrentTime { get; private set; }

	public bool Paused { get; set; }

	public Execution Execution => execution;

	public Simulation(MainSim mainSim, IEnumerable<string> unlocks, ItemBlock items, string leaderboardName, string steamLeaderboardName, LeaderboardType leaderboardType, int seed = -1, List<SFO> loadedGrounds = null, List<SFO> loadedEntities = null, bool resetUnlocks = false)
	{
		this.mainSim = mainSim;
		this.leaderboardName = leaderboardName;
		this.steamLeaderboardName = steamLeaderboardName;
		this.leaderboardType = leaderboardType;
		CurrentTime = new Duration(0L);
		if (seed >= 0)
		{
			random = new System.Random(seed);
		}
		else
		{
			random = new System.Random();
		}
		randomVarious = new System.Random(Helper.JustSha256It(random));
		randomMaze = new System.Random(Helper.JustSha256It(random));
		randomSnake = new System.Random(Helper.JustSha256It(random));
		randomCactus = new System.Random(Helper.JustSha256It(random));
		randomSunflower = new System.Random(Helper.JustSha256It(random));
		randomPumpkin = new System.Random(Helper.JustSha256It(random));
		randomPoly = new System.Random(Helper.JustSha256It(random));
		randomRandom = new System.Random(Helper.JustSha256It(random));
		farm = new Farm(this, unlocks, items, loadedGrounds, loadedEntities, resetUnlocks);
		ChangeExecutionSpeed(farm.MaxSpeedFactor());
	}

	public bool IsExecuting()
	{
		return Execution != null;
	}

	public void StartProgramExecution(Execution execution)
	{
		if (IsExecuting())
		{
			throw new Exception("Tried to start a simulation twice");
		}
		this.execution = execution;
		NextExecutionStep();
	}

	public void StopProgramExecution()
	{
		if (IsExecuting())
		{
			lock (execution.lockExecution)
			{
				execution.StopExecution();
				execution = null;
			}
			ChangeExecutionSpeed(farm.MaxSpeedFactor());
			hasError = false;
			farm.grid.SizeLimit = 0;
			farm.RemoveSpawnedDrones();
			stepByStepMode = false;
			Paused = false;
			Logger.Close();
		}
	}

	public void Error()
	{
		hasError = true;
		Paused = true;
	}

	public Timer StartTimer(Action func, Duration time)
	{
		Timer timer = new Timer();
		timer.func = func;
		Insert(timer, CurrentTime + time);
		return timer;
	}

	private void Insert(Timer timer, Duration finishTime)
	{
		timers.Enqueue(timer, finishTime);
	}

	public void ChangeExecutionSpeed(double speedFactor)
	{
		OpDuration = new Duration((long)Math.Ceiling(2500000.0 / speedFactor));
		SpeedFactor = speedFactor;
	}

	public void RunNextStep(Duration goalTime, object lockSimulation, bool stopOnFinished = false)
	{
		Duration priority2;
		lock (lockSimulation)
		{
			if (Paused || (stopOnFinished && !IsExecuting()))
			{
				Monitor.Wait(lockSimulation);
				return;
			}
			if (IsExecuting() && hasError)
			{
				StopProgramExecution();
			}
			Timer element;
			Duration priority;
			while (timers.TryPeek(out element, out priority) && CurrentTime < goalTime && element.stopped)
			{
				timers.Dequeue();
			}
			if ((!IsExecuting() || !(execution.NextExecutionTime <= goalTime)) && (!timers.TryPeek(out var _, out priority2) || !(priority2 <= goalTime)))
			{
				CurrentTime = goalTime;
				Monitor.Wait(lockSimulation);
				return;
			}
			if (timers.TryPeek(out var element3, out priority2) && (!IsExecuting() || execution.NextExecutionTime >= priority2))
			{
				CurrentTime = priority2;
				timers.Dequeue();
				element3.func();
				return;
			}
			CurrentTime = execution.NextExecutionTime;
			Paused = false;
		}
		priority2.nanoseconds--;
		Duration targetRunTime = Duration.Min(priority2, goalTime) - CurrentTime;
		execution.Execute(targetRunTime, lockSimulation);
	}

	public void NextExecutionStep()
	{
		if (execution != null && !execution.IsPerformingAStep)
		{
			Paused = false;
			execution.NextExecutionTime = CurrentTime;
		}
	}

	public void AddOpsToCurrentTime(double ops)
	{
		CurrentTime += OpDuration * ops;
	}

	public bool EvaluateName(string name, out IPyObject value)
	{
		lock (execution.lockExecution)
		{
			if (execution.MainState == null)
			{
				value = null;
				return false;
			}
			return execution.MainState.EvaluateVarAlongCallstack(name, out value);
		}
	}

	public Duration GetActionTime(double ops)
	{
		return OpDuration * ops;
	}
}
public class InputBoss : MonoBehaviour
{
	[SerializeField]
	private float wasdSpeed;

	[SerializeField]
	private GameObject[] UIsToHide;

	private void Update()
	{
		if (0f > Input.mousePosition.x || 0f > Input.mousePosition.y || (float)Screen.width < Input.mousePosition.x || (float)Screen.height < Input.mousePosition.y)
		{
			return;
		}
		float axisRaw = Input.GetAxisRaw("ScrollWheel");
		if (axisRaw != 0f && !MainSim.Inst.menu.gameObject.activeInHierarchy)
		{
			if (MainSim.Inst.researchMenu.IsOpen)
			{
				MainSim.Inst.researchMenu.Scroll(axisRaw);
			}
			else if (MainSim.Inst.workspace.codeCompleter.IsOpen && RectTransformUtility.RectangleContainsScreenPoint((RectTransform)MainSim.Inst.workspace.codeCompleter.transform, Input.mousePosition, MainSim.Inst.workspace.uiCam))
			{
				MainSim.Inst.workspace.codeCompleter.Scroll(axisRaw);
			}
			else
			{
				MainSim.Inst.workspace.Scroll(axisRaw);
			}
		}
		if (OptionHolder.GetKeyCombination("menu").IsKeyPressed(pressedRightThisFrame: true))
		{
			if (MainSim.Inst.workspace.codeCompleter.IsOpen)
			{
				MainSim.Inst.workspace.codeCompleter.Close();
			}
			else if (MainSim.Inst.menu.gameObject.activeInHierarchy)
			{
				MainSim.Inst.menu.Play();
			}
			else if (MainSim.Inst.researchMenu.IsOpen)
			{
				MainSim.Inst.researchMenu.OpenCloseMenu();
			}
			else if (MainSim.Inst.leaderboardManager.IsLeaderBoardScreenOpen)
			{
				MainSim.Inst.leaderboardManager.OkPressed();
			}
			else if (MainSim.Inst.workspace.searchBox.gameObject.activeInHierarchy)
			{
				MainSim.Inst.workspace.searchBox.CloseSearchBox();
			}
			else
			{
				EventSystem.current?.SetSelectedGameObject(null);
				MainSim.Inst.menu.Open();
			}
		}
		GameObject gameObject = EventSystem.current?.currentSelectedGameObject;
		if (OptionHolder.GetKeyCombination("search").IsKeyPressed(pressedRightThisFrame: true))
		{
			if (gameObject != null && gameObject.TryGetComponent<CodeInputField>(out var component) && component.selectionAnchorPosition != component.selectionFocusPosition)
			{
				int num = Mathf.Min(component.selectionAnchorPosition, component.selectionFocusPosition);
				int num2 = Mathf.Max(component.selectionAnchorPosition, component.selectionFocusPosition);
				string searchTerm = component.text.Substring(num, num2 - num);
				MainSim.Inst.workspace.searchBox.StartSearch(searchTerm);
			}
			else
			{
				MainSim.Inst.workspace.searchBox.StartSearch();
			}
		}
		if (OptionHolder.GetKeyCombination("redo 1").IsKeyPressed(pressedRightThisFrame: true) || OptionHolder.GetKeyCombination("redo 2").IsKeyPressed(pressedRightThisFrame: true))
		{
			MainSim.Inst.workspace.Redo();
		}
		else if (OptionHolder.GetKeyCombination("undo").IsKeyPressed(pressedRightThisFrame: true))
		{
			MainSim.Inst.workspace.Undo();
		}
		if (OptionHolder.GetKeyCombination("save").IsKeyPressed(pressedRightThisFrame: true))
		{
			Saver.Save(MainSim.Inst);
		}
		if (gameObject == null || (gameObject?.GetComponent<CodeInputField>() == null && gameObject?.GetComponent<TMP_InputField>() == null && !MainSim.Inst.menu.gameObject.activeInHierarchy && !MainSim.Inst.researchMenu.IsOpen))
		{
			if (OptionHolder.GetKeyCombination("move up").IsKeyPressed(pressedRightThisFrame: false))
			{
				MainSim.Inst.workspace.container.anchoredPosition += new Vector2(0f, (0f - wasdSpeed) * Time.deltaTime);
			}
			if (OptionHolder.GetKeyCombination("move left").IsKeyPressed(pressedRightThisFrame: false))
			{
				MainSim.Inst.workspace.container.anchoredPosition += new Vector2(wasdSpeed * Time.deltaTime, 0f);
			}
			if (OptionHolder.GetKeyCombination("move down").IsKeyPressed(pressedRightThisFrame: false))
			{
				MainSim.Inst.workspace.container.anchoredPosition += new Vector2(0f, wasdSpeed * Time.deltaTime);
			}
			if (OptionHolder.GetKeyCombination("move right").IsKeyPressed(pressedRightThisFrame: false))
			{
				MainSim.Inst.workspace.container.anchoredPosition += new Vector2((0f - wasdSpeed) * Time.deltaTime, 0f);
			}
		}
		if (OptionHolder.GetKeyCombination("start execution").IsKeyPressed(pressedRightThisFrame: true))
		{
			CodeWindow component2 = MainSim.Inst.workspace.activeWindow.GetComponent<CodeWindow>();
			if (component2 != null)
			{
				if (EventSystem.current.currentSelectedGameObject == component2.CodeInput.gameObject)
				{
					EventSystem.current.SetSelectedGameObject(null);
				}
				if (MainSim.Inst.StepByStepMode)
				{
					MainSim.Inst.StepByStepMode = false;
					MainSim.Inst.NextExecutionStep();
				}
				else
				{
					Node node = component2.Parse();
					if (node != null)
					{
						MainSim.Inst.StartMainExecution(component2, node);
					}
				}
			}
		}
		if (OptionHolder.GetKeyCombination("stop execution").IsKeyPressed(pressedRightThisFrame: true) && MainSim.Inst.IsExecuting())
		{
			MainSim.Inst.StopMainExecution();
		}
		if (OptionHolder.GetKeyCombination("next step").IsKeyPressed(pressedRightThisFrame: true) && MainSim.Inst.StepByStepMode)
		{
			MainSim.Inst.NextExecutionStep();
		}
		if (OptionHolder.GetKeyCombination("pause execution").IsKeyPressed(pressedRightThisFrame: true))
		{
			MainSim.Inst.StepByStepMode = true;
		}
		if (OptionHolder.GetKeyCombination("hide UI").IsKeyPressed(pressedRightThisFrame: true))
		{
			GameObject[] uIsToHide = UIsToHide;
			foreach (GameObject obj in uIsToHide)
			{
				obj.SetActive(!obj.activeInHierarchy);
			}
		}
	}
}
public static class BuiltinFunctions
{
	private static List<PyFunction> functionList = new List<PyFunction>
	{
		new PyFunction("harvest", Harvest),
		new PyFunction("can_harvest", CanHarvest),
		new PyFunction("swap", Swap),
		new PyFunction("range", Range),
		new PyFunction("plant", Plant),
		new PyFunction("move", Move),
		new PyFunction("can_move", CanMove),
		new PyFunction("till", Till),
		new PyFunction("get_pos_x", GetPosX),
		new PyFunction("get_pos_y", GetPosY),
		new PyFunction("get_world_size", GetWorldSize),
		new PyFunction("get_entity_type", GetEntityType),
		new PyFunction("get_ground_type", GetGroundType),
		new PyFunction("get_time", GetTime, null, isFree: true),
		new PyFunction("get_tick_count", GetTickCount, null, isFree: true),
		new PyFunction("use_item", UseItem),
		new PyFunction("get_water", GetWater),
		new PyFunction("do_a_flip", DoAFlip),
		new PyFunction("change_hat", ChangeHat),
		new PyFunction("print", Print),
		new PyFunction("quick_print", QuickPrint, null, isFree: true),
		new PyFunction("len", Len),
		new PyFunction("num_items", NumItems),
		new PyFunction("get_cost", GetCost),
		new PyFunction("clear", Clear),
		new PyFunction("get_companion", GetCompanion),
		new PyFunction("unlock", Unlock),
		new PyFunction("num_unlocked", NumUnlocked),
		new PyFunction("leaderboard_run", LeaderboardRun),
		new PyFunction("measure", Measure),
		new PyFunction("min", Min),
		new PyFunction("max", Max),
		new PyFunction("abs", Abs),
		new PyFunction("str", StringConstructor),
		new PyFunction("random", Random),
		new PyFunction("simulate", Simulate),
		new PyFunction("list", ListConstructor),
		new PyFunction("set", SetConstructor),
		new PyFunction("dict", DictConstructor),
		new PyFunction("set_execution_speed", SetExecutionSpeed),
		new PyFunction("set_world_size", SetWorldSize),
		new PyFunction("spawn_drone", SpawnDrone),
		new PyFunction("num_drones", NumDrones),
		new PyFunction("max_drones", MaxDrones),
		new PyFunction("wait_for", Await),
		new PyFunction("has_finished", HasFinished),
		new PyFunction("pet_the_piggy", PetThePiggy),
		new PyFunction("tap", IncrementTapTapLootCounter)
	};

	private static List<PyFunction> methodList = new List<PyFunction>
	{
		new PyFunction("append", Append),
		new PyFunction("add", Add),
		new PyFunction("remove", Remove),
		new PyFunction("pop", Pop),
		new PyFunction("insert", Insert)
	};

	private static Dictionary<string, PyFunction> functions;

	private static Dictionary<string, PyFunction> methods;

	private static List<string> resetUnlocks = new List<string>
	{
		"loops", "for", "range", "if", "else", "elif", "debug", "debug_2", "timing", "lists",
		"dictionaries", "costs", "auto_unlock", "operators", "variables", "Items", "clear", "senses", "utilities", "can_harvest",
		"Entities", "get_world_size", "till", "use_item", "trade", "move", "multi_trade", "get_active_power", "North", "East",
		"South", "West", "functions", "import", "simulation", "get_water", "measure", "max_drones", "num_drones", "get_drone_id",
		"spawn_drone", "send", "receive"
	};

	public static Dictionary<string, PyFunction> Functions
	{
		get
		{
			if (functions == null)
			{
				functions = functionList.ToDictionary((PyFunction f) => f.functionName);
			}
			return functions;
		}
	}

	public static Dictionary<string, PyFunction> Methods
	{
		get
		{
			if (methods == null)
			{
				methods = methodList.ToDictionary((PyFunction f) => f.functionName);
			}
			return methods;
		}
	}

	public static IPyObject ItemsToNewDict(ItemBlock items)
	{
		if (items == null)
		{
			return new PyNone();
		}
		Dictionary<IPyObject, PyObjectBox> dictionary = new Dictionary<IPyObject, PyObjectBox>();
		for (int i = 0; i < items.items.Length; i++)
		{
			if (items.items[i] > 0.0)
			{
				dictionary.Add(ResourceManager.GetItem(i), new PyObjectBox(new PyNumber(items.items[i])));
			}
		}
		return new PyDict(dictionary);
	}

	private static void CorrectParams(List<IPyObject> parameters, List<Type> types, string function)
	{
		if (parameters.Count != types.Count)
		{
			PyTuple pyTuple = new PyTuple(parameters);
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_wrong_number_args", function + "()", types.Count, pyTuple));
		}
		for (int i = 0; i < parameters.Count; i++)
		{
			if (!types[i].IsInstanceOfType(parameters[i]))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_wrong_args", i + 1, function + "()", parameters[i]));
			}
		}
	}

	private static void NoParams(List<IPyObject> parameters, string function)
	{
		if (parameters != null && parameters.Count > 0)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_expected_no_args", function + "()"));
		}
	}

	private static double DoAFlip(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "do_a_flip");
		exec.States[droneId].currentSideEffect = SideEffect.DoAFlip;
		return 0.0;
	}

	private static double PetThePiggy(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "pet_the_piggy");
		exec.States[droneId].currentSideEffect = SideEffect.PetThePiggy;
		return 0.0;
	}

	private static double IncrementTapTapLootCounter(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "tap");
		if (sim.leaderboardType == LeaderboardType.none)
		{
			Ipc.Instance.Increment();
		}
		return Math.Floor(0.1 / sim.OpDuration.Seconds);
	}

	private static double Print(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			throw new ExecuteException("error_empty_print");
		}
		string s = string.Join(' ', parameters.Select((IPyObject p) => CodeUtilities.ToNiceString(p)));
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Print;
		programState.currentSideEffectArgument = new PyString(s);
		return 0.0;
	}

	private static double QuickPrint(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			throw new ExecuteException("error_empty_print");
		}
		Logger.Log(string.Join(' ', parameters.Select((IPyObject p) => CodeUtilities.ToNiceString(p))));
		exec.States[droneId].ReturnValue = new PyNone();
		return 0.0;
	}

	private static double ChangeHat(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(HatSO) }, "change_hat");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.ChangeHat;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double Min(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		return MinOrMax(parameters, isMax: false, exec, droneId);
	}

	private static double Max(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		return MinOrMax(parameters, isMax: true, exec, droneId);
	}

	private static double MinOrMax(List<IPyObject> parameters, bool isMax, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat(isMax ? "error_wrong_use_of_max" : "error_wrong_use_of_min", new PyList(new List<IPyObject>())));
		}
		IEnumerable<IPyObject> enumerable = parameters;
		if (parameters.Count == 1)
		{
			CorrectParams(parameters, new List<Type> { typeof(IEnumerable<IPyObject>) }, isMax ? "max" : "min");
			enumerable = (IEnumerable<IPyObject>)parameters[0];
		}
		if (!enumerable.Any())
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat(isMax ? "error_wrong_use_of_max" : "error_wrong_use_of_min", parameters[0]));
		}
		int steps = 0;
		IPyObject pyObject = enumerable.First();
		foreach (IPyObject item in enumerable)
		{
			if (CodeUtilities.DeepCompare(item, pyObject, isMax ? "max" : "min", ref steps) * (isMax ? 1 : (-1)) > 0)
			{
				pyObject = item;
			}
		}
		exec.States[droneId].ReturnValue = pyObject;
		return 1.0 * (double)Mathf.Max(steps, 1);
	}

	private static double Abs(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyNumber) }, "abs");
		exec.States[droneId].ReturnValue = new PyNumber(Math.Abs((PyNumber)parameters[0]));
		return 1.0;
	}

	private static double Swap(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "swap");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Swap;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double Harvest(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "harvest");
		exec.States[droneId].currentSideEffect = SideEffect.Harvest;
		return 0.0;
	}

	private static double CanHarvest(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "can_harvest");
		exec.States[droneId].currentSideEffect = SideEffect.CanHarvest;
		return 0.0;
	}

	private static double Plant(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(FarmObjectSO) }, "plant");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Plant;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double Till(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "till");
		exec.States[droneId].currentSideEffect = SideEffect.Till;
		return 0.0;
	}

	private static double UseItem(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		int num;
		if (parameters.Count == 1)
		{
			CorrectParams(parameters, new List<Type> { typeof(ItemSO) }, "use_item");
			num = 1;
		}
		else
		{
			CorrectParams(parameters, new List<Type>
			{
				typeof(ItemSO),
				typeof(PyNumber)
			}, "use_item");
			num = (int)(double)(PyNumber)parameters[1];
		}
		ItemSO currentSideEffectArgument = (ItemSO)parameters[0];
		if (num < 1)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_negative_use_item", num));
		}
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.UseItem;
		programState.currentSideEffectArgument = currentSideEffectArgument;
		programState.currentSideEffectArgument2 = new PyNumber(num);
		return 0.0;
	}

	private static double GetWater(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_water");
		exec.States[droneId].currentSideEffect = SideEffect.GetWater;
		return 0.0;
	}

	private static double Move(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "move");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Move;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double CanMove(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "can_move");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.CanMove;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double GetEntityType(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_entity_type");
		exec.States[droneId].currentSideEffect = SideEffect.GetEntityType;
		return 0.0;
	}

	private static double GetGroundType(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_ground_type");
		exec.States[droneId].currentSideEffect = SideEffect.GetGroundType;
		return 0.0;
	}

	private static double GetTime(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_time");
		exec.States[droneId].currentSideEffect = SideEffect.GetTime;
		return 0.0;
	}

	private static double GetTickCount(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_tick_count");
		exec.States[droneId].ReturnValue = new PyNumber(exec.States[droneId].OpCount - exec.States[droneId].StartOpCount);
		return 0.0;
	}

	private static double Random(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "random");
		exec.States[droneId].ReturnValue = new PyNumber(exec.States[droneId].randomRandom.NextDouble());
		return 1.0;
	}

	private static double GetPosX(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_pos_x");
		exec.States[droneId].currentSideEffect = SideEffect.GetPosX;
		return 0.0;
	}

	private static double GetPosY(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_pos_y");
		exec.States[droneId].currentSideEffect = SideEffect.GetPosY;
		return 0.0;
	}

	private static double GetWorldSize(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_world_size");
		exec.States[droneId].currentSideEffect = SideEffect.GetWorldSize;
		return 0.0;
	}

	private static double Range(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count >= 3)
		{
			CorrectParams(parameters, new List<Type>
			{
				typeof(PyNumber),
				typeof(PyNumber),
				typeof(PyNumber)
			}, "range");
			exec.States[droneId].ReturnValue = new PyRange((PyNumber)parameters[0], (PyNumber)parameters[1], (PyNumber)parameters[2]);
		}
		else if (parameters.Count == 2)
		{
			CorrectParams(parameters, new List<Type>
			{
				typeof(PyNumber),
				typeof(PyNumber)
			}, "range");
			exec.States[droneId].ReturnValue = new PyRange((PyNumber)parameters[0], (PyNumber)parameters[1]);
		}
		else if (parameters.Count <= 1)
		{
			CorrectParams(parameters, new List<Type> { typeof(PyNumber) }, "range");
			exec.States[droneId].ReturnValue = new PyRange((PyNumber)parameters[0]);
		}
		return 1.0;
	}

	private static double Len(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count > 0 && parameters[0] is ICollection<IPyObject>)
		{
			exec.States[droneId].ReturnValue = new PyNumber(((ICollection<IPyObject>)parameters[0]).Count);
		}
		else
		{
			CorrectParams(parameters, new List<Type> { typeof(IReadOnlyCollection<IPyObject>) }, "len");
			exec.States[droneId].ReturnValue = new PyNumber(((IReadOnlyCollection<IPyObject>)parameters[0]).Count);
		}
		return 1.0;
	}

	private static double NumItems(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(ItemSO) }, "num_items");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.NumItems;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double GetCost(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count >= 1 && parameters[0] is UnlockSO)
		{
			ProgramState programState = exec.States[droneId];
			programState.currentSideEffect = SideEffect.GetCost;
			programState.currentSideEffectArgument = parameters[0];
			if (parameters.Count == 1)
			{
				CorrectParams(parameters, new List<Type> { typeof(UnlockSO) }, "get_cost");
				programState.currentSideEffectArgument2 = null;
			}
			else
			{
				CorrectParams(parameters, new List<Type>
				{
					typeof(UnlockSO),
					typeof(PyNumber)
				}, "get_cost");
				programState.currentSideEffectArgument2 = parameters[1];
			}
		}
		else
		{
			CorrectParams(parameters, new List<Type> { typeof(FarmObjectSO) }, "get_cost");
			ProgramState programState2 = exec.States[droneId];
			programState2.currentSideEffect = SideEffect.GetCost;
			programState2.currentSideEffectArgument = parameters[0];
		}
		return 0.0;
	}

	private static double GetCompanion(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_companion");
		exec.States[droneId].currentSideEffect = SideEffect.GetCompanion;
		return 0.0;
	}

	private static double Measure(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Measure;
		if (parameters.Count == 0 || (parameters.Count == 1 && parameters[0] is PyNone))
		{
			programState.currentSideEffectArgument = null;
		}
		else
		{
			CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "measure");
			programState.currentSideEffectArgument = parameters[0];
		}
		return 0.0;
	}

	private static double Clear(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "clear");
		exec.States[droneId].currentSideEffect = SideEffect.Clear;
		return 0.0;
	}

	private static double Unlock(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(UnlockSO) }, "unlock");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Unlock;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double NumUnlocked(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.NumUnlocked;
		if (parameters.Count == 1 && parameters[0] is UnlockSO)
		{
			CorrectParams(parameters, new List<Type> { typeof(UnlockSO) }, "num_unlocked");
			programState.currentSideEffectArgument = parameters[0];
		}
		else if (parameters.Count == 1 && parameters[0] is ItemSO)
		{
			CorrectParams(parameters, new List<Type> { typeof(ItemSO) }, "num_unlocked");
			programState.currentSideEffectArgument = parameters[0];
		}
		else if (parameters.Count == 1 && parameters[0] is HatSO)
		{
			CorrectParams(parameters, new List<Type> { typeof(HatSO) }, "num_unlocked");
			programState.currentSideEffectArgument = parameters[0];
		}
		else
		{
			CorrectParams(parameters, new List<Type> { typeof(FarmObjectSO) }, "num_unlocked");
			programState.currentSideEffectArgument = parameters[0];
		}
		return 0.0;
	}

	private static double LeaderboardRun(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type>
		{
			typeof(LeaderboardSO),
			typeof(PyString),
			typeof(PyNumber)
		}, "leaderboard_run");
		LeaderboardSO leaderboardSO = (LeaderboardSO)parameters[0];
		PyString obj = (PyString)parameters[1];
		PyNumber currentSideEffectArgument = (PyNumber)parameters[2];
		MainSim.LeaderboardStartArgs currentSideEffectArgument2 = new MainSim.LeaderboardStartArgs(unlocks: leaderboardSO.everythingUnlocked ? GetUnlockStrings(ResourceManager.GetAllUnlocks(), leaderboardSO.singleDrone) : resetUnlocks, items: new ItemBlock(leaderboardSO.startItems), fileName: obj.str, globals: new List<KeyValuePair<string, IPyObject>>(), leaderboardName: leaderboardSO.leaderboardName, steamLeaderboardName: leaderboardSO.steamLeaderboardName, leaderboardType: leaderboardSO.leaderboardType, seed: -1, singleDrone: leaderboardSO.singleDrone);
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.RunLeaderboard;
		programState.currentSideEffectArgument = currentSideEffectArgument;
		programState.currentSideEffectArgument2 = currentSideEffectArgument2;
		return 0.0;
	}

	private static List<string> GetUnlockStrings(IEnumerable<IPyObject> unlocks, bool isSingleDrone = false)
	{
		List<string> list = new List<string>(resetUnlocks);
		if (unlocks is PyDict pyDict)
		{
			foreach (KeyValuePair<IPyObject, PyObjectBox> item in pyDict.dict)
			{
				if (item.Key is UnlockSO unlockSO && item.Value.obj is PyNumber { num: var num })
				{
					if (num < 0.0 || num > (double)unlockSO.maxUnlockLevel)
					{
						num = unlockSO.maxUnlockLevel;
					}
					else if (num < 1.0)
					{
						continue;
					}
					list.Add(unlockSO.unlockName);
					if (unlockSO.IsMultiUnlock)
					{
						list.Add($"{unlockSO.unlockName}_{num}");
					}
					continue;
				}
				throw new ExecuteException("error_invalid_sim_unlocks");
			}
		}
		else
		{
			foreach (IPyObject unlock in unlocks)
			{
				if (unlock is UnlockSO unlockSO2)
				{
					if (!isSingleDrone || unlockSO2.unlockName != "megafarm")
					{
						list.Add(unlockSO2.unlockName);
					}
					if (unlockSO2.IsMultiUnlock)
					{
						if (isSingleDrone && unlockSO2.unlockName == "expand")
						{
							list.Add($"{unlockSO2.unlockName}_{5}");
						}
						else if (!isSingleDrone || unlockSO2.unlockName != "megafarm")
						{
							list.Add($"{unlockSO2.unlockName}_{unlockSO2.maxUnlockLevel}");
						}
					}
				}
				else
				{
					if (!(unlock is PyTuple pyTuple))
					{
						throw new ExecuteException("error_invalid_sim_unlocks");
					}
					if (pyTuple.Count != 2 || !(pyTuple[0] is UnlockSO unlockSO3) || !(pyTuple[1] is PyNumber pyNumber2) || !((double)pyNumber2 >= 1.0) || !((double)pyNumber2 <= (double)unlockSO3.maxUnlockLevel))
					{
						throw new ExecuteException("error_invalid_sim_unlocks");
					}
					list.Add(unlockSO3.unlockName);
					list.Add($"{unlockSO3.unlockName}_{(int)(double)pyNumber2}");
				}
			}
		}
		return list;
	}

	private static ItemBlock GetItemBlock(PyDict dict)
	{
		ItemBlock itemBlock = ItemBlock.CreateEmpty();
		foreach (KeyValuePair<IPyObject, PyObjectBox> item in dict.dict)
		{
			if (item.Key is ItemSO itemSO && item.Value.obj is PyNumber pyNumber)
			{
				itemBlock.AddItem(itemSO.itemId, Math.Max(0.0, pyNumber));
				continue;
			}
			throw new ExecuteException("error_invalid_sim_items");
		}
		return itemBlock;
	}

	private static List<KeyValuePair<string, IPyObject>> GetGlobals(PyDict dict)
	{
		List<KeyValuePair<string, IPyObject>> list = new List<KeyValuePair<string, IPyObject>>();
		foreach (KeyValuePair<IPyObject, PyObjectBox> item in dict.dict)
		{
			if (item.Key is PyString pyString)
			{
				IPyObject obj = item.Value.obj;
				if (obj != null)
				{
					list.Add(new KeyValuePair<string, IPyObject>(pyString.str, obj));
					continue;
				}
			}
			throw new ExecuteException("error_invalid_sim_globals");
		}
		return list;
	}

	private static double Simulate(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (exec.States[droneId] != exec.MainState)
		{
			throw new ExecuteException("simulate can only be called from the main execution");
		}
		CorrectParams(parameters, new List<Type>
		{
			typeof(PyString),
			typeof(IEnumerable<IPyObject>),
			typeof(PyDict),
			typeof(PyDict),
			typeof(PyNumber),
			typeof(PyNumber)
		}, "simulate");
		PyString obj = (PyString)parameters[0];
		List<string> unlockStrings = GetUnlockStrings((IEnumerable<IPyObject>)parameters[1]);
		ItemBlock itemBlock = GetItemBlock((PyDict)parameters[2]);
		List<KeyValuePair<string, IPyObject>> globals = GetGlobals((PyDict)parameters[3]);
		PyNumber pyNumber = (PyNumber)parameters[4];
		PyNumber currentSideEffectArgument = (PyNumber)parameters[5];
		MainSim.LeaderboardStartArgs currentSideEffectArgument2 = new MainSim.LeaderboardStartArgs(obj.str, unlockStrings, itemBlock, globals, "", "", LeaderboardType.simulation, (int)(double)pyNumber);
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Simulate;
		programState.currentSideEffectArgument = currentSideEffectArgument;
		programState.currentSideEffectArgument2 = currentSideEffectArgument2;
		return 0.0;
	}

	private static double SimulateAsync(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		return 200.0;
	}

	private static double SpawnDrone(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters.Take(1).ToList(), new List<Type> { typeof(PyFunction) }, "spawn_drone");
		ProgramState programState = exec.States[droneId];
		if (((PyFunction)parameters[0]).syntaxTree == null)
		{
			throw new ExecuteException("error_spawn_drone_builtin");
		}
		programState.currentSideEffect = SideEffect.SpawnDrone;
		programState.currentSideEffectArgument = new PyList(parameters);
		return 0.0;
	}

	private static double Await(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyDroneHandle) }, "wait_for");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Await;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double HasFinished(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyDroneHandle) }, "has_finished");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.HasFinished;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double GetDroneId(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_drone_id");
		exec.States[droneId].currentSideEffect = SideEffect.GetDroneId;
		return 0.0;
	}

	private static double NumDrones(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "num_drones");
		exec.States[droneId].currentSideEffect = SideEffect.NumDrones;
		return 0.0;
	}

	private static double MaxDrones(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "max_drones");
		exec.States[droneId].currentSideEffect = SideEffect.MaxDrones;
		return 0.0;
	}

	private static double Send(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type>
		{
			typeof(IPyObject),
			typeof(PyNumber)
		}, "send");
		IPyObject pyObject = parameters[0];
		int num = (int)(double)(PyNumber)parameters[1];
		if (num < 0 || num >= sim.farm.drones.Count)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_invalid_drone_id", num));
		}
		double num2 = pyObject.Size();
		exec.MessageChannel.Enqueue((pyObject, droneId, num), exec.States[droneId].OpCount + num2);
		exec.States[droneId].ReturnValue = new PyNone();
		return Math.Max(1.0, num2);
	}

	private static double Receive(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		int num = -1;
		if (parameters.Count > 0)
		{
			CorrectParams(parameters, new List<Type> { typeof(PyNumber) }, "receive");
			num = (int)(double)(PyNumber)parameters[0];
		}
		if (num >= sim.farm.drones.Count)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_invalid_drone_id", num));
		}
		IPyObject item2;
		if (num < 0)
		{
			if (exec.States[droneId].AllMessagesQueue.TryDequeue(out (IPyObject, int) item))
			{
				exec.States[droneId].ReturnValue = item.Item1;
				exec.States[droneId].MessageQueues[item.Item2].Dequeue();
			}
			else
			{
				exec.States[droneId].ReturnValue = new PyNone();
			}
		}
		else if (exec.States[droneId].MessageQueues[num].TryDequeue(out item2))
		{
			exec.States[droneId].ReturnValue = item2;
			exec.States[droneId].AllMessagesQueue.Remove((item2, num));
		}
		else
		{
			exec.States[droneId].ReturnValue = new PyNone();
		}
		return 1.0;
	}

	private static double ListConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PyList(new List<IPyObject>());
			return 1.0;
		}
		CorrectParams(parameters, new List<Type> { typeof(IEnumerable<IPyObject>) }, "list");
		if (parameters[0] is IPySequence && ((IPySequence)parameters[0]).Count > 100000)
		{
			throw new ExecuteException("error_sequence_too_large");
		}
		PyList pyList = new PyList(((IEnumerable<IPyObject>)parameters[0]).ToList());
		exec.States[droneId].ReturnValue = pyList;
		return 1.0 * (double)(1 + pyList.Count);
	}

	private static double SetConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PySet(new HashSet<IPyObject>());
			return 1.0;
		}
		CorrectParams(parameters, new List<Type> { typeof(IEnumerable<IPyObject>) }, "set");
		if (parameters[0] is IPySequence && ((IPySequence)parameters[0]).Count > 100000)
		{
			throw new ExecuteException("error_sequence_too_large");
		}
		PySet pySet = new PySet(((IEnumerable<IPyObject>)parameters[0]).ToHashSet());
		foreach (IPyObject item in pySet)
		{
			if (item is PyDict || item is PyList || item is PySet || item is PyModule)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_key", item));
			}
		}
		exec.States[droneId].ReturnValue = pySet;
		return 1.0 * (double)(1 + pySet.Count);
	}

	private static double DictConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PyDict(new Dictionary<IPyObject, PyObjectBox>());
			return 1.0;
		}
		CorrectParams(parameters, new List<Type> { typeof(PyDict) }, "dict");
		PyDict pyDict = new PyDict(((PyDict)parameters[0]).dict.ToDictionary((KeyValuePair<IPyObject, PyObjectBox> pair) => pair.Key, (KeyValuePair<IPyObject, PyObjectBox> pair) => new PyObjectBox(pair.Value.obj)));
		exec.States[droneId].ReturnValue = pyDict;
		return 1.0 * (double)(1 + 2 * pyDict.Count);
	}

	private static double StringConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PyString("");
			return 1.0;
		}
		CorrectParams(parameters, new List<Type> { typeof(IPyObject) }, "str");
		PyString returnValue = new PyString(CodeUtilities.ToNiceString(parameters[0]));
		exec.States[droneId].ReturnValue = returnValue;
		return 1.0;
	}

	private static double SetExecutionSpeed(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyNumber) }, "set_execution_speed");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.SetExecutionSpeed;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double SetWorldSize(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyNumber) }, "set_world_size");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.SetWorldSize;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double Append(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type>
		{
			typeof(PyList),
			typeof(IPyObject)
		}, "append");
		((PyList)parameters[0]).Add(parameters[1]);
		exec.States[droneId].ReturnValue = new PyNone();
		return 1.0;
	}

	private static double Add(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type>
		{
			typeof(PySet),
			typeof(IPyObject)
		}, "add");
		IPyObject pyObject = parameters[1];
		if (pyObject is PyList || pyObject is PySet || pyObject is PyDict || pyObject is PyModule)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_key", parameters[1]));
		}
		((PySet)parameters[0]).set.Add(parameters[1]);
		exec.States[droneId].ReturnValue = new PyNone();
		return 1.0 * (double)parameters[1].Size();
	}

	private static double Remove(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count > 0 && parameters[0] is PyList)
		{
			CorrectParams(parameters, new List<Type>
			{
				typeof(PyList),
				typeof(IPyObject)
			}, "remove");
			PyList pyList = (PyList)parameters[0];
			int steps = 0;
			bool flag = false;
			for (int i = 0; i < pyList.Count; i++)
			{
				if (CodeUtilities.DeepEquals(pyList[i], parameters[1], ref steps))
				{
					pyList.RemoveAt(i);
					flag = true;
					steps += pyList.Count - i;
					break;
				}
			}
			if (!flag)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_list_element_not_found", parameters[1]));
			}
			exec.States[droneId].ReturnValue = new PyNone();
			return 1.0 * (double)steps;
		}
		if (parameters.Count > 0 && parameters[0] is PySet)
		{
			CorrectParams(parameters, new List<Type>
			{
				typeof(PySet),
				typeof(IPyObject)
			}, "remove");
			PySet pySet = (PySet)parameters[0];
			if (!pySet.Contains(parameters[1]))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_set_element_not_found", parameters[1]));
			}
			pySet.set.Remove(parameters[1]);
			exec.States[droneId].ReturnValue = new PyNone();
			return 1.0 * (double)parameters[1].Size();
		}
		object[] array = new object[1];
		IPyObject pyObject2;
		if (parameters.Count <= 0)
		{
			IPyObject pyObject = new PyNone();
			pyObject2 = pyObject;
		}
		else
		{
			pyObject2 = parameters[0];
		}
		array[0] = pyObject2;
		throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_remove_on_non_list_or_set", array));
	}

	private static double Pop(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count > 0 && parameters[0] is PyList)
		{
			PyList pyList = (PyList)parameters[0];
			int num = -1;
			if (parameters.Count > 1)
			{
				CorrectParams(parameters, new List<Type>
				{
					typeof(PyList),
					typeof(PyNumber)
				}, "pop");
				num = (int)Math.Floor((PyNumber)parameters[1]);
			}
			if (num < 0)
			{
				num = pyList.Count + num;
			}
			if (num < 0 || num >= pyList.Count)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index_out_of_bounds", num, pyList), 1, 1);
			}
			IPyObject returnValue = pyList[num];
			pyList.RemoveAt(num);
			exec.States[droneId].ReturnValue = returnValue;
			return 1.0 * (double)(pyList.Count - num + 1);
		}
		if (parameters.Count > 0 && parameters[0] is PyDict)
		{
			PyDict pyDict = (PyDict)parameters[0];
			CorrectParams(parameters, new List<Type>
			{
				typeof(PyDict),
				typeof(IPyObject)
			}, "pop");
			if (!pyDict.dict.ContainsKey(parameters[1]))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_set_element_not_found", parameters[1]));
			}
			exec.States[droneId].ReturnValue = pyDict.dict[parameters[1]].obj;
			pyDict.dict.Remove(parameters[1]);
			return 1.0 * (double)parameters[1].Size();
		}
		object[] array = new object[1];
		IPyObject pyObject2;
		if (parameters.Count <= 0)
		{
			IPyObject pyObject = new PyNone();
			pyObject2 = pyObject;
		}
		else
		{
			pyObject2 = parameters[0];
		}
		array[0] = pyObject2;
		throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_pop_on_non_dict_or_list", array));
	}

	private static double Insert(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type>
		{
			typeof(PyList),
			typeof(PyNumber),
			typeof(IPyObject)
		}, "insert");
		PyList pyList = (PyList)parameters[0];
		int num = (int)Math.Floor((PyNumber)parameters[1]);
		if (num < 0)
		{
			num = pyList.Count + num;
		}
		if (num < 0 || num > pyList.Count)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index_out_of_bounds", num, pyList), 1, 1);
		}
		double result = 1.0 * (double)(pyList.Count - num + 1);
		pyList.Insert(num, parameters[2]);
		exec.States[droneId].ReturnValue = new PyNone();
		return result;
	}
}
public class Execution
{
	public const double ACTION_OPS = 200.0;

	public const double OPERATION_OPS = 1.0;

	public Simulation sim;

	private List<ProgramState> states;

	private bool activeDroneExecutedStep;

	private bool stopped;

	public object lockExecution = new object();

	public ProgramState MainState { get; private set; }

	public List<ProgramState> States => states;

	public PriorityQueue<(IPyObject data, int senderId, int receiverId), double> MessageChannel { get; } = new PriorityQueue<(IPyObject, int, int), double>();

	public double GlobalOpCount { get; private set; }

	public bool IsPerformingAStep { get; private set; }

	public int Id { get; private set; }

	public Duration NextExecutionTime { get; set; }

	public Execution(Simulation sim, Node syntaxTree, int id)
	{
		this.sim = sim;
		states = new List<ProgramState>();
		AddProgramState(0, syntaxTree, 0.0);
		MainState = states[0];
		Id = id;
		NextExecutionTime = sim.CurrentTime;
	}

	public void StopExecution()
	{
		if (!stopped)
		{
			stopped = true;
			if (sim.IsExecuting())
			{
				sim.StopProgramExecution();
			}
		}
	}

	public void AddProgramState(int droneId, Node syntaxTree, double opCount)
	{
		ProgramState programState = new ProgramState(opCount, sim.randomRandom, droneId);
		foreach (PyFunction item in BuiltinFunctions.Functions.Values.Concat(BuiltinFunctions.Methods.Values))
		{
			programState.moduleState.globalScope.SetVar(item.functionName, item, checkShadow: false, isStatic: true);
		}
		programState.PushOntoExecutionStack(syntaxTree.Execute(programState, this, 0));
		if (droneId >= states.Count)
		{
			states.Add(programState);
		}
		else
		{
			states[droneId] = programState;
		}
	}

	public void Execute(Duration targetRunTime, object lockSimulation)
	{
		IsPerformingAStep = true;
		double num = Math.Floor(GlobalOpCount + Math.Min(199.0, targetRunTime / sim.OpDuration));
		if (sim.stepByStepMode && activeDroneExecutedStep)
		{
			lock (lockSimulation)
			{
				sim.Paused = true;
				IsPerformingAStep = false;
				activeDroneExecutedStep = false;
				return;
			}
		}
		while (true)
		{
			double globalOpCount = GlobalOpCount;
			lock (lockExecution)
			{
				if (stopped)
				{
					break;
				}
				for (int i = 0; i < States.Count; i++)
				{
					if (States[i] != null && States[i].currentSideEffect == SideEffect.None && !(States[i].OpCount > num) && States[i].awaitedDroneId < 0)
					{
						States[i].PerformExecutionStep(num, out var flag);
						activeDroneExecutedStep |= flag;
					}
				}
				try
				{
					GlobalOpCount = States.Where((ProgramState s) => s != null && s.awaitedDroneId < 0).Min((ProgramState s) => s.OpCount);
				}
				catch (InvalidOperationException)
				{
					GlobalOpCount = num;
				}
			}
			lock (lockSimulation)
			{
				double num2 = 0.0;
				double num3 = num;
				for (int num4 = 0; num4 < States.Count; num4++)
				{
					if (States[num4] != null && States[num4].currentDependencies.Count > 0)
					{
						try
						{
							foreach (var (dependency, wordStart, wordEnd) in States[num4].currentDependencies)
							{
								sim.farm.AssertUnlocked(dependency, wordStart, wordEnd);
							}
							States[num4].currentDependencies.Clear();
						}
						catch (ExecuteException currentExecuteException)
						{
							States[num4].currentExecuteException = currentExecuteException;
							States[num4].currentSideEffect = SideEffect.Error;
							ApplySideEffect(num4);
						}
					}
					if (States[num4] != null && States[num4].awaitedDroneId < 0)
					{
						num3 = Math.Min(num3, States[num4].OpCount);
					}
				}
				sim.AddOpsToCurrentTime(num3 - globalOpCount);
				if (!stopped && !sim.Paused)
				{
					for (int num5 = 0; num5 < States.Count; num5++)
					{
						if (States[num5] != null)
						{
							num2 += States[num5].ConsumeOps();
						}
					}
					for (int num6 = 0; num6 < States.Count; num6++)
					{
						if (GlobalOpCount > num)
						{
							break;
						}
						if (States[num6] == null || States[num6].awaitedDroneId >= 0)
						{
							continue;
						}
						if (States[num6].hitBreakpoint)
						{
							sim.mainSim.StepByStepMode = true;
							States[num6].hitBreakpoint = false;
							sim.farm.mainDroneId = num6;
							MainState = States[num6];
						}
						else if (States[num6].currentSideEffect != SideEffect.None && !(States[num6].OpCount > GlobalOpCount))
						{
							try
							{
								ApplySideEffect(num6);
							}
							catch (ExecuteException currentExecuteException2)
							{
								States[num6].currentExecuteException = currentExecuteException2;
								States[num6].currentSideEffect = SideEffect.Error;
								ApplySideEffect(num6);
							}
							if (States.Count > num6 && States[num6] != null)
							{
								num2 += States[num6].ConsumeOps();
								States[num6].currentSideEffect = SideEffect.None;
								States[num6].currentSideEffectArgument = null;
								States[num6].currentSideEffectArgument2 = null;
							}
						}
					}
					sim.farm.UsedPower += num2 / 200.0 / 30.0;
				}
				try
				{
					GlobalOpCount = States.Where((ProgramState s) => s != null && s.awaitedDroneId < 0).Min((ProgramState s) => s.OpCount);
				}
				catch (InvalidOperationException)
				{
					GlobalOpCount = num;
				}
				NextExecutionTime = sim.CurrentTime + sim.OpDuration * (GlobalOpCount - num3);
				sim.AddOpsToCurrentTime(Math.Min(GlobalOpCount, num) - num3);
				if ((sim.stepByStepMode && activeDroneExecutedStep) || GlobalOpCount > num || sim.Paused)
				{
					break;
				}
			}
		}
	}

	private double ApplySideEffect(int droneId)
	{
		double num = 0.0;
		ProgramState programState = States[droneId];
		IPyObject currentSideEffectArgument = programState.currentSideEffectArgument;
		object currentSideEffectArgument2 = programState.currentSideEffectArgument2;
		SideEffect currentSideEffect = programState.currentSideEffect;
		bool flag = true;
		switch (currentSideEffect)
		{
		case SideEffect.Harvest:
		{
			bool flag2 = sim.farm.drones[droneId].Harvest();
			programState.ReturnValue = new PyBool(flag2);
			num = (flag2 ? 200.0 : 1.0);
			break;
		}
		case SideEffect.CanHarvest:
			programState.ReturnValue = new PyBool(sim.farm.drones[droneId].CanHarvest());
			num = 1.0;
			break;
		case SideEffect.Swap:
		{
			bool flag3 = sim.farm.drones[droneId].Swap((PyGridDirection)currentSideEffectArgument, programState);
			programState.ReturnValue = new PyBool(flag3);
			num = (flag3 ? 200.0 : 1.0);
			break;
		}
		case SideEffect.Plant:
		{
			FarmObjectSO farmObjectSO2 = (FarmObjectSO)currentSideEffectArgument;
			bool flag4 = farmObjectSO2.canBePlanted && sim.farm.drones[droneId].Plant(farmObjectSO2, programState);
			programState.ReturnValue = new PyBool(flag4);
			num = (flag4 ? 200.0 : 1.0);
			break;
		}
		case SideEffect.Move:
		{
			double ops;
			bool b = sim.farm.drones[droneId].Move((PyGridDirection)currentSideEffectArgument, programState, out ops);
			programState.ReturnValue = new PyBool(b);
			num = ops;
			break;
		}
		case SideEffect.CanMove:
			programState.ReturnValue = new PyBool(sim.farm.drones[droneId].CanMove((PyGridDirection)currentSideEffectArgument));
			num = 1.0;
			break;
		case SideEffect.Till:
			sim.farm.drones[droneId].ChangeGround("soil");
			programState.ReturnValue = new PyNone();
			num = 200.0;
			break;
		case SideEffect.GetPosX:
			programState.ReturnValue = new PyNumber(sim.farm.drones[droneId].pos.x);
			num = 1.0;
			break;
		case SideEffect.GetPosY:
			programState.ReturnValue = new PyNumber(sim.farm.drones[droneId].pos.y);
			num = 1.0;
			break;
		case SideEffect.GetWorldSize:
			programState.ReturnValue = new PyNumber(sim.farm.grid.WorldSize.y);
			num = 1.0;
			break;
		case SideEffect.GetEntityType:
			if (sim.farm.drones[droneId].EntityUnderDrone() != null)
			{
				programState.ReturnValue = sim.farm.drones[droneId].EntityUnderDrone().objectSO;
			}
			else
			{
				programState.ReturnValue = new PyNone();
			}
			num = 1.0;
			break;
		case SideEffect.GetGroundType:
			programState.ReturnValue = sim.farm.drones[droneId].GroundUnderDrone().objectSO;
			num = 1.0;
			break;
		case SideEffect.UseItem:
		{
			ItemSO itemSO2 = (ItemSO)currentSideEffectArgument;
			int num8 = (int)((PyNumber)currentSideEffectArgument2).num;
			if (!sim.farm.Items.Contains(itemSO2.itemId, num8))
			{
				Logger.LogWarning(string.Format(Localizer.Localize("warning_no_item_to_use"), itemSO2), States[droneId]);
				programState.ReturnValue = new PyBool(b: false);
				num = 1.0;
				break;
			}
			bool flag6 = false;
			bool useActionTicks = false;
			switch (itemSO2.itemName)
			{
			case "water":
				flag6 = sim.farm.drones[droneId].Water(num8);
				useActionTicks = flag6;
				break;
			case "fertilizer":
				flag6 = sim.farm.drones[droneId].Fertilize(num8);
				useActionTicks = flag6;
				break;
			case "weird_substance":
			{
				FarmObject farmObject = sim.farm.drones[droneId].EntityUnderDrone();
				if (farmObject is BushPlant bushPlant && sim.farm.IsUnlocked("mazes"))
				{
					int num9 = 1 << sim.farm.NumUnlocked("mazes") - 1;
					if (num8 % num9 != 0)
					{
						Logger.LogWarning(Localizer.Localize("warning_weird_substance_not_divisible"), States[droneId]);
					}
					int num10 = num8 / num9;
					if (num10 < 1)
					{
						bushPlant.ToggleWeird();
						break;
					}
					bushPlant.GenerateHedgeMaze(num10);
					flag6 = true;
					useActionTicks = flag6;
				}
				else if (farmObject is Treasure treasure && sim.farm.IsUnlocked("mazes"))
				{
					int num11 = num8 / (1 << sim.farm.NumUnlocked("mazes") - 1);
					if (num11 >= 1)
					{
						flag6 = treasure.RepositionTreasure(num11, out useActionTicks);
					}
				}
				else if (farmObject is Growable growable)
				{
					growable.ToggleWeird();
					flag6 = true;
					useActionTicks = flag6;
				}
				break;
			}
			}
			programState.ReturnValue = new PyBool(flag6);
			if (flag6)
			{
				sim.farm.Items.RemoveItem(itemSO2.itemId, num8);
			}
			num = (useActionTicks ? 200.0 : 1.0);
			break;
		}
		case SideEffect.GetWater:
			programState.ReturnValue = new PyNumber(sim.farm.drones[droneId].GetWater());
			num = 1.0;
			break;
		case SideEffect.ChangeHat:
			sim.farm.drones[droneId].ChangeHat((HatSO)currentSideEffectArgument, programState);
			programState.ReturnValue = new PyNone();
			num = 200.0;
			break;
		case SideEffect.NumItems:
			programState.ReturnValue = new PyNumber(sim.farm.Items.GetNumber(((ItemSO)currentSideEffectArgument).itemId));
			num = 1.0;
			break;
		case SideEffect.GetCost:
			if (currentSideEffectArgument is UnlockSO unlockSO2)
			{
				int numUnlocked = ((!(currentSideEffectArgument2 is PyNumber pyNumber)) ? (-1) : ((int)(double)pyNumber));
				States[droneId].ReturnValue = BuiltinFunctions.ItemsToNewDict(sim.farm.GetUnlockCost(unlockSO2, numUnlocked));
			}
			else if (currentSideEffectArgument is FarmObjectSO farmObjectSO3)
			{
				if (string.IsNullOrEmpty(farmObjectSO3.yieldUpgradeName))
				{
					States[droneId].ReturnValue = BuiltinFunctions.ItemsToNewDict(farmObjectSO3.cost);
				}
				else
				{
					int num6 = Mathf.Max(0, sim.farm.NumUnlocked(farmObjectSO3.yieldUpgradeName) - 1);
					States[droneId].ReturnValue = BuiltinFunctions.ItemsToNewDict(farmObjectSO3.cost * (1 << num6));
				}
			}
			num = 1.0;
			break;
		case SideEffect.Clear:
			sim.farm.RemoveSpawnedDrones();
			sim.farm.drones[0].ResetPos();
			sim.farm.grid.ClearGrid();
			MainState = States[droneId];
			States.RemoveAll((ProgramState s) => s != MainState);
			MainState.DroneId = 0;
			if (MainState.awaitedDroneId >= 0)
			{
				MainState.awaitedDroneId = -1;
				MainState.OpCount = GlobalOpCount;
				MainState.ReturnValue = PyNone.Instance;
			}
			num = 200.0;
			programState.ReturnValue = PyNone.Instance;
			break;
		case SideEffect.GetCompanion:
		{
			IPyObject returnValue2 = ((!sim.farm.grid.entities.ContainsKey(sim.farm.drones[droneId].pos) || !(sim.farm.grid.entities[sim.farm.drones[droneId].pos] is Growable)) ? new PyNone() : ((Growable)sim.farm.grid.entities[sim.farm.drones[droneId].pos]).GetCompanion());
			programState.ReturnValue = returnValue2;
			num = 1.0;
			break;
		}
		case SideEffect.Unlock:
		{
			bool flag5 = sim.farm.UnlockOrUpgrade((UnlockSO)currentSideEffectArgument, requireParent: false);
			programState.ReturnValue = new PyBool(flag5);
			num = (flag5 ? 200.0 : 1.0);
			break;
		}
		case SideEffect.NumUnlocked:
			if (currentSideEffectArgument is UnlockSO unlockSO)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(unlockSO));
			}
			else if (currentSideEffectArgument is ItemSO itemSO)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(itemSO.itemName));
			}
			else if (currentSideEffectArgument is FarmObjectSO farmObjectSO)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(farmObjectSO.objectName));
			}
			else if (currentSideEffectArgument is HatSO hatSO)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(hatSO.hatName));
			}
			num = 1.0;
			break;
		case SideEffect.Measure:
		{
			Vector2Int key;
			if (currentSideEffectArgument == null || currentSideEffectArgument is PyNone)
			{
				key = sim.farm.drones[droneId].pos;
			}
			else
			{
				GridDirection dir = (PyGridDirection)currentSideEffectArgument;
				key = sim.farm.grid.Wrap(sim.farm.drones[droneId].pos + dir.GetDirectionVector());
			}
			IPyObject pyObject = sim.farm.grid.entities.GetValueOrDefault(key)?.Measure();
			IPyObject returnValue;
			if (pyObject == null)
			{
				IPyObject pyObject2 = new PyNone();
				returnValue = pyObject2;
			}
			else
			{
				returnValue = pyObject;
			}
			programState.ReturnValue = returnValue;
			num = 1.0;
			break;
		}
		case SideEffect.SetExecutionSpeed:
		{
			double num7 = (PyNumber)currentSideEffectArgument;
			if (double.IsNaN(num7) || num7 > sim.farm.MaxSpeedFactor() || num7 < 0.1)
			{
				sim.ChangeExecutionSpeed(sim.farm.MaxSpeedFactor());
			}
			else
			{
				sim.ChangeExecutionSpeed(num7);
			}
			programState.ReturnValue = new PyNone();
			num = 200.0;
			break;
		}
		case SideEffect.SetWorldSize:
			if ((int)(double)(PyNumber)currentSideEffectArgument != sim.farm.grid.WorldSize.y)
			{
				foreach (Drone drone in sim.farm.drones)
				{
					drone?.ResetPos();
				}
				sim.farm.grid.SizeLimit = (int)(double)(PyNumber)currentSideEffectArgument;
			}
			programState.ReturnValue = new PyNone();
			num = 200.0;
			break;
		case SideEffect.GetTime:
			programState.ReturnValue = new PyNumber(sim.CurrentTime.Seconds);
			num = 0.0;
			break;
		case SideEffect.SpawnDrone:
		{
			int num2 = States.Where((ProgramState s) => s != null).Count();
			int num3 = Helper.NumDrones(sim.farm.NumUnlocked("megafarm"));
			if (num2 >= num3)
			{
				programState.ReturnValue = PyNone.Instance;
				num = 1.0;
				break;
			}
			PyList obj = (PyList)currentSideEffectArgument;
			PyFunction pyFunction = (PyFunction)obj[0];
			Dictionary<object, object> copies2 = new Dictionary<object, object>();
			pyFunction = (PyFunction)pyFunction.DeepCopy(copies2);
			int num4 = sim.farm.AddDrone(droneId);
			FunctionNode functionNode = (FunctionNode)pyFunction.syntaxTree;
			List<IPyObject> list = new List<IPyObject>();
			foreach (IPyObject item in obj.list.Skip(1))
			{
				list.Add(item.DeepCopy(copies2));
			}
			functionNode.Arguments = list;
			AddProgramState(num4, functionNode, GlobalOpCount + 200.0);
			States[num4].PushScope(new Scope(functionNode, null, pyFunction.parentScope, functionNode.Vars));
			PyDroneHandle pyDroneHandle2 = new PyDroneHandle(num4, sim.farm.droneGeneration);
			States[num4].DroneHandle = pyDroneHandle2;
			States[num4].CurrentExecutingNode = programState.CurrentExecutingNode;
			programState.ReturnValue = pyDroneHandle2;
			num = 200.0;
			if (sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.UnlockAchievement("USE_MULTIPLE_DRONES");
				if (num2 + 1 == 32)
				{
					Achievements.UnlockAchievement("SWARM");
				}
			}
			break;
		}
		case SideEffect.GetDroneId:
			programState.ReturnValue = new PyNumber(droneId);
			num = 1.0;
			break;
		case SideEffect.NumDrones:
			programState.ReturnValue = new PyNumber(States.Where((ProgramState s) => s != null).Count());
			num = 1.0;
			break;
		case SideEffect.MaxDrones:
			programState.ReturnValue = new PyNumber(Helper.NumDrones(sim.farm.NumUnlocked("megafarm")));
			num = 1.0;
			break;
		case SideEffect.Await:
		{
			PyDroneHandle pyDroneHandle = (PyDroneHandle)currentSideEffectArgument;
			if (pyDroneHandle.returnValue != null)
			{
				Dictionary<object, object> copies = new Dictionary<object, object>();
				programState.ReturnValue = pyDroneHandle.returnValue.DeepCopy(copies);
				num = 1.0;
			}
			else
			{
				programState.awaitedDroneId = pyDroneHandle.id;
				num = 1.0;
			}
			break;
		}
		case SideEffect.HasFinished:
			if (((PyDroneHandle)currentSideEffectArgument).returnValue != null)
			{
				programState.ReturnValue = new PyBool(b: true);
			}
			else
			{
				programState.ReturnValue = new PyBool(b: false);
			}
			num = 1.0;
			break;
		case SideEffect.Terminated:
		{
			for (int num5 = 0; num5 < States.Count; num5++)
			{
				if (States[num5] != null && States[num5].awaitedDroneId == droneId)
				{
					States[num5].awaitedDroneId = -1;
					States[num5].OpCount = GlobalOpCount;
					Dictionary<object, object> copies3 = new Dictionary<object, object>();
					States[num5].ReturnValue = States[droneId].ReturnValue.DeepCopy(copies3);
				}
			}
			if (States[droneId].DroneHandle != null)
			{
				States[droneId].DroneHandle.returnValue = States[droneId].ReturnValue;
			}
			if (States[droneId] == MainState)
			{
				MainState = null;
			}
			States[droneId] = null;
			if (States.All((ProgramState s) => s == null))
			{
				IsPerformingAStep = false;
				StopExecution();
			}
			else
			{
				sim.farm.RemoveDrone(droneId);
				MainState = States[sim.farm.mainDroneId];
			}
			break;
		}
		case SideEffect.Error:
		{
			ExecuteException currentExecuteException = States[droneId].currentExecuteException;
			Node currentExecutingNode = States[droneId].CurrentExecutingNode;
			int startIndex = ((currentExecuteException.startIndex >= 0) ? currentExecuteException.startIndex : currentExecutingNode.boxedParams.wordStart);
			int endIndex = ((currentExecuteException.endIndex >= 0) ? currentExecuteException.endIndex : currentExecutingNode.boxedParams.wordEnd);
			States[droneId].CurrentExecutingNode?.boxedParams.codeWindow?.SetErrorMessage(currentExecuteException.Message, startIndex, endIndex);
			Logger.LogError(Localizer.Localize(currentExecuteException.Message), States[droneId]);
			sim.Error();
			IsPerformingAStep = false;
			sim.farm.mainDroneId = droneId;
			MainState = States[droneId];
			if (sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.UnlockAchievement("CAUSE_A_RUNTIME_ERROR");
			}
			break;
		}
		case SideEffect.DoAFlip:
			sim.farm.drones[droneId].DoAFlip();
			programState.ReturnValue = new PyNone();
			num = Math.Floor(1.0 / sim.OpDuration.Seconds);
			flag = false;
			break;
		case SideEffect.PetThePiggy:
			sim.farm.drones[droneId].PetThePiggy();
			programState.ReturnValue = new PyNone();
			num = Math.Floor(1.0 / sim.OpDuration.Seconds);
			flag = false;
			break;
		case SideEffect.Print:
		{
			string str = ((PyString)currentSideEffectArgument).str;
			sim.farm.drones[droneId].PrintToAir(str);
			Logger.Log(str);
			programState.ReturnValue = new PyNone();
			num = Math.Floor(1.0 / sim.OpDuration.Seconds);
			flag = false;
			break;
		}
		case SideEffect.Simulate:
			if (sim.mainSim != null && sim.leaderboardType == LeaderboardType.none)
			{
				MainSim.LeaderboardStartArgs startArgs2 = (MainSim.LeaderboardStartArgs)currentSideEffectArgument2;
				sim.mainSim.TimeFactor = (PyNumber)currentSideEffectArgument;
				sim.mainSim.ScheduleLeaderboardStart(startArgs2);
				sim.Paused = true;
			}
			else
			{
				Logger.LogWarning(Localizer.Localize("warning_recursive_simulation"), programState);
			}
			programState.ReturnValue = new PyNone();
			num = 200.0;
			break;
		case SideEffect.RunLeaderboard:
			if (sim.mainSim != null && sim.leaderboardType == LeaderboardType.none)
			{
				MainSim.LeaderboardStartArgs startArgs = (MainSim.LeaderboardStartArgs)currentSideEffectArgument2;
				sim.mainSim.TimeFactor = (PyNumber)currentSideEffectArgument;
				sim.mainSim.ScheduleLeaderboardStart(startArgs);
				sim.Paused = true;
			}
			else
			{
				Logger.LogWarning(Localizer.Localize("warning_recursive_simulation"), programState);
			}
			programState.ReturnValue = new PyNone();
			num = 200.0;
			break;
		}
		if (programState != null)
		{
			if (flag)
			{
				programState.OpCount += num;
			}
			else
			{
				programState.AddAndConsumeOps(num);
			}
		}
		return num;
	}
}
public enum SideEffect
{
	None,
	Harvest,
	CanHarvest,
	Swap,
	Plant,
	Move,
	CanMove,
	Till,
	GetPosX,
	GetPosY,
	GetWorldSize,
	GetEntityType,
	GetGroundType,
	UseItem,
	GetWater,
	ChangeHat,
	NumItems,
	GetCost,
	Clear,
	GetCompanion,
	Unlock,
	NumUnlocked,
	Measure,
	SetExecutionSpeed,
	SetWorldSize,
	GetTime,
	SpawnDrone,
	GetDroneId,
	NumDrones,
	MaxDrones,
	Await,
	HasFinished,
	Terminated,
	Error,
	DoAFlip,
	PetThePiggy,
	Print,
	Simulate,
	RunLeaderboard
}
public static class Logger
{
	public delegate void PrintAction();

	public const int NUM_OUTPUT_LIMIT = 100;

	public const int MESSAGE_LENGTH_LIMIT = 1000;

	private static HashSet<Node> warningNodes = new HashSet<Node>();

	private static LinkedList<string> output = new LinkedList<string>();

	private static StreamWriter logWriter = null;

	private static string persistentDataPath = Helper.persistentDataPath;

	private static object outputLock = new object();

	public static event PrintAction OnOutputChanged;

	public static void Log(string logMessage)
	{
		WriteLog(logMessage, addSeparator: false);
	}

	public static void LogError(string errorMessage, ProgramState state)
	{
		WriteLog("Error: " + errorMessage + "\nIn: " + state.GetTrace(), addSeparator: true);
	}

	public static void LogWarning(string warningMessage, ProgramState state)
	{
		if (!(OptionHolder.GetString("print warnings") == "disabled") && !warningNodes.Contains(state.CurrentExecutingNode))
		{
			WriteLog("Warning: " + warningMessage + "\nIn: " + state.GetTrace(), addSeparator: true);
			MainSim.Inst.warningIcon.PopUp();
			warningNodes.Add(state.CurrentExecutingNode);
		}
	}

	public static void Close()
	{
		logWriter?.Dispose();
		logWriter = null;
	}

	public static void Clear()
	{
		lock (outputLock)
		{
			output.Clear();
		}
		warningNodes.Clear();
		MainSim.Inst.warningIcon.Dismiss();
		try
		{
			File.WriteAllText(Path.Combine(persistentDataPath, "output.txt"), "");
		}
		catch (IOException message)
		{
			UnityEngine.Debug.LogError(message);
		}
		if (logWriter != null)
		{
			logWriter = null;
		}
		Logger.OnOutputChanged?.Invoke();
	}

	public static string GetOutputString()
	{
		lock (outputLock)
		{
			return string.Join("\n", output);
		}
	}

	private static void WriteLog(string logMessage, bool addSeparator)
	{
		if (addSeparator)
		{
			logMessage += "\n--------------------------------------------------------------------";
		}
		try
		{
			if (logWriter == null)
			{
				logWriter = new StreamWriter(Path.Combine(persistentDataPath, "output.txt"), append: true);
			}
			logWriter.WriteLine(CodeUtilities.RemoveSyntaxTags(logMessage));
			logWriter.Flush();
		}
		catch (IOException message)
		{
			UnityEngine.Debug.LogError(message);
		}
		if (logMessage.Length > 1000)
		{
			logMessage = logMessage.Substring(0, 1000);
		}
		lock (outputLock)
		{
			output.AddLast(logMessage);
			if (output.Count >= 100)
			{
				output.RemoveFirst();
			}
			Logger.OnOutputChanged?.Invoke();
		}
	}
}
public class ModuleState
{
	public Scope globalScope;

	public Stack<Scope> callStack = new Stack<Scope>();

	public IPyObject returnValue;

	public bool isExpressionStatic;

	public Node currentExecutingNode;
}
public class AssignmentNode : Node
{
	private string op;

	public override string NodeName => "assign";

	public AssignmentNode(string op, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.op = op;
	}

	public AssignmentNode(string op, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.op = op;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[1].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		Blink(state, execution);
		IPyObject returnValue = state.ReturnValue;
		state.CurrentExecutingNode = this;
		foreach (double item2 in Assign(state, execution, depth, slots[0], returnValue, op, boxedParams.codeWindow.fileName))
		{
			yield return item2;
		}
		state.ReturnValue = new PyNone();
	}

	public static IEnumerable<double> Assign(ProgramState state, Execution execution, int depth, Node lhs, IPyObject rhs, string op, string currentFileName)
	{
		if (lhs is ValueNode)
		{
			string value = ((ValueNode)lhs).value;
			IPyObject before = ((op == "=") ? null : state.CurrentScope.Evaluate(value, currentFileName).val);
			state.CurrentScope.SetVar(value, GetValueToAssign(before, rhs, op, out var execTime));
			lhs.Blink(state, execution);
			if (lhs.CheckIncrementOpCount(state, execution, 1.0 * execTime))
			{
				yield return 0.0;
			}
			yield break;
		}
		if (lhs is BinaryExprNode binaryExprNode)
		{
			foreach (double item in binaryExprNode.slots[0].Execute(state, execution, depth + 1))
			{
				yield return item;
			}
			if (binaryExprNode.op == ".")
			{
				if (!(state.ReturnValue is PyModule pyModule))
				{
					state.CurrentExecutingNode = lhs;
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_attribute_on_non_module", state.ReturnValue));
				}
				if (!(binaryExprNode.slots[1] is ValueNode))
				{
					throw new ExecuteException("error_invalid_const2", binaryExprNode.slots[1].boxedParams.wordStart, binaryExprNode.slots[1].boxedParams.wordEnd);
				}
				int num = ((!state.IsExpressionStatic) ? 1 : 0);
				string value2 = (binaryExprNode.slots[1] as ValueNode).value;
				IPyObject before2 = ((op == "=") ? null : pyModule.Evaluate(value2, binaryExprNode.slots[1].boxedParams.wordStart, binaryExprNode.slots[1].boxedParams.wordEnd).val);
				pyModule.SetAttribute(value2, GetValueToAssign(before2, rhs, op, out var execTime2));
				if (lhs.CheckIncrementOpCount(state, execution, 1.0 * (execTime2 + (double)num)))
				{
					yield return 0.0;
				}
				yield break;
			}
			if (binaryExprNode.op == "[]")
			{
				IPyObject returnValue = state.ReturnValue;
				if (!(returnValue is IPyIndexable indexable))
				{
					state.CurrentExecutingNode = lhs;
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index_on_non_indexable", state.ReturnValue));
				}
				foreach (double item2 in binaryExprNode.slots[1].Execute(state, execution, depth + 1))
				{
					yield return item2;
				}
				InternalPySequence indices = (InternalPySequence)state.ReturnValue;
				int steps = 0;
				IPyObject before3 = ((op == "=") ? null : indexable.At(indices, ref steps));
				steps = 0;
				indexable.At(indices, ref steps, GetValueToAssign(before3, rhs, op, out var execTime3));
				if (lhs.CheckIncrementOpCount(state, execution, 1.0 * ((double)steps + execTime3)))
				{
					yield return 0.0;
				}
				yield break;
			}
			state.CurrentExecutingNode = lhs;
			throw new ExecuteException("error_assign_type_mismatch");
		}
		if (lhs is ListNode || lhs is TupleNode)
		{
			if (!(rhs is IPySequence))
			{
				throw new ExecuteException("error_assign_type_mismatch");
			}
			List<Node> leftNodes = lhs.slots[0].slots;
			if (leftNodes.Count < ((IPySequence)rhs).Count)
			{
				throw new ExecuteException("error_too_many_values_to_unpack");
			}
			if (leftNodes.Count > ((IPySequence)rhs).Count)
			{
				throw new ExecuteException("error_not_enough_values");
			}
			List<IPyObject> rightValues = ((IPySequence)rhs).ToList();
			for (int i = 0; i < leftNodes.Count; i++)
			{
				foreach (double item3 in Assign(state, execution, depth, leftNodes[i], rightValues[i], op, currentFileName))
				{
					yield return item3;
				}
			}
			yield break;
		}
		if (lhs is BracketNode)
		{
			foreach (double item4 in Assign(state, execution, depth, lhs.slots[0], rhs, op, currentFileName))
			{
				yield return item4;
			}
			yield break;
		}
		throw new ExecuteException("error_assign_type_mismatch");
	}

	private static IPyObject GetValueToAssign(IPyObject before, IPyObject rhsValue, string op, out double execTime)
	{
		execTime = 0.0;
		switch (op)
		{
		case "+=":
			if ((!(before is PyNumber) || !(rhsValue is PyNumber)) && (!(before is PyList) || !(rhsValue is IEnumerable<object>)) && (!(before is PyTuple) || !(rhsValue is PyTuple)) && (!(before is PyString) || !(rhsValue is PyString)))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_bin_operator", op, before, rhsValue));
			}
			break;
		case "/":
		case "//":
			if (rhsValue is PyNumber pyNumber && (double)pyNumber == 0.0)
			{
				throw new ExecuteException("error_division_by_zero");
			}
			goto default;
		default:
			if (!(rhsValue is PyNumber) || !(before is PyNumber))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_arith_assign_not_used_on_number", op));
			}
			break;
		case "=":
			break;
		}
		IPyObject pyObject = null;
		switch (op)
		{
		case "=":
			pyObject = rhsValue;
			execTime = 0.0;
			break;
		case "+=":
			if (before is PyNumber)
			{
				pyObject = new PyNumber((double)(PyNumber)before + (double)(PyNumber)rhsValue);
				execTime = 1.0;
			}
			else if (before is PyList)
			{
				((PyList)before).list.AddRange((IEnumerable<IPyObject>)rhsValue);
				pyObject = before;
				execTime = ((IEnumerable<IPyObject>)rhsValue).Count();
			}
			else if (before is PyString)
			{
				pyObject = new PyString(((PyString)before).str + ((PyString)rhsValue).str);
				execTime = ((PyString)pyObject).Count;
			}
			else if (before is PyTuple)
			{
				pyObject = new PyTuple(((PyTuple)before).Concat((PyTuple)rhsValue).ToList());
				execTime = ((PyTuple)pyObject).Count;
			}
			break;
		case "-=":
			pyObject = new PyNumber((double)(PyNumber)before - (double)(PyNumber)rhsValue);
			execTime = 1.0;
			break;
		case "*=":
			pyObject = new PyNumber((double)(PyNumber)before * (double)(PyNumber)rhsValue);
			execTime = 1.0;
			break;
		case "/=":
			pyObject = new PyNumber((double)(PyNumber)before / (double)(PyNumber)rhsValue);
			execTime = 1.0;
			break;
		case "//=":
			pyObject = PyNumber.FloorDivision((PyNumber)before, (PyNumber)rhsValue);
			execTime = 1.0;
			break;
		case "%=":
			pyObject = PyNumber.Modulo((PyNumber)before, (PyNumber)rhsValue);
			execTime = 1.0;
			break;
		}
		return pyObject;
	}

	private IPyObject IndexInto(IPyObject indexable, IPyObject indexObject, IPyObject valueToSet = null, bool setValue = false)
	{
		if (indexable is PyList)
		{
			PyList pyList = (PyList)indexable;
			if (!(indexObject is PyNumber))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index", indexObject, indexable));
			}
			int num = (int)(double)(PyNumber)indexObject;
			if (num < 0)
			{
				num = pyList.Count + num;
			}
			if (num < 0 || num >= pyList.Count)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index_out_of_bounds", num, pyList));
			}
			if (setValue)
			{
				pyList[num] = valueToSet;
			}
			return pyList[num];
		}
		if (indexable is PyDict)
		{
			PyDict pyDict = (PyDict)indexable;
			if (indexObject is PyDict || indexObject is PyList || indexObject is PySet || indexObject is PyModule)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_key", indexObject));
			}
			if (setValue)
			{
				if (pyDict.dict.ContainsKey(indexObject))
				{
					pyDict.dict[indexObject].obj = valueToSet;
				}
				else
				{
					pyDict.dict[indexObject] = new PyObjectBox(valueToSet);
				}
			}
			return pyDict.dict.GetValueOrDefault(indexObject)?.obj;
		}
		if (indexable is PyTuple)
		{
			throw new ExecuteException("error_index_on_tuple");
		}
		throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index", indexObject, indexable));
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("variables", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new AssignmentNode(op, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class BinaryExprNode : Node
{
	public string op;

	public TokenType opTokenType;

	public override string NodeName => "binary";

	public BinaryExprNode(string op, TokenType opTokenType, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.op = op;
		this.opTokenType = opTokenType;
	}

	public BinaryExprNode(string op, TokenType opTokenType, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.op = op;
		this.opTokenType = opTokenType;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		IPyObject lhs = state.ReturnValue;
		if (op == "and" && !Scope.IsTrueValue(lhs))
		{
			Blink(state, execution);
			state.ReturnValue = lhs;
			if (CheckIncrementOpCount(state, execution, 1.0))
			{
				yield return 0.0;
			}
			yield break;
		}
		if (op == "or" && Scope.IsTrueValue(lhs))
		{
			Blink(state, execution);
			state.ReturnValue = lhs;
			if (CheckIncrementOpCount(state, execution, 1.0))
			{
				yield return 0.0;
			}
			yield break;
		}
		if (op == "." && lhs is IPyNameSpace nameSpace)
		{
			if (!(slots[1] is ValueNode))
			{
				throw new ExecuteException("error_invalid_const2", slots[1].boxedParams.wordStart, slots[1].boxedParams.wordEnd);
			}
			Blink(state, execution);
			yield return (!state.IsExpressionStatic) ? 1 : 0;
			bool flag;
			(state.ReturnValue, flag) = nameSpace.Evaluate(((ValueNode)slots[1]).value, slots[1].boxedParams.wordStart, slots[1].boxedParams.wordEnd);
			state.IsExpressionStatic &= flag;
			yield break;
		}
		foreach (double item2 in slots[1].Execute(state, execution, depth + 1))
		{
			yield return item2;
		}
		IPyObject returnValue = state.ReturnValue;
		Blink(state, execution);
		state.CurrentExecutingNode = this;
		if ((lhs is PyFunction || returnValue is PyFunction) && ((op != "and" && op != "or" && op != "." && op != "==" && op != "!=" && op != "in" && op != "not in") || ((op == "==" || op == "!=" || op == "in" || op == "not in") && OptionHolder.GetString("error forgot call") == "enabled")))
		{
			PyFunction pyFunction = (PyFunction)((lhs is PyFunction) ? lhs : returnValue);
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_function_in_operator", pyFunction.functionName, op));
		}
		if (!(op == "==") && !(op == "!=") && !(op == ">=") && !(op == "<=") && !(op == ">") && !(op == "<") && !(op == "and") && !(op == "or"))
		{
			if (op == "[]")
			{
				if (!(lhs is IPyIndexable))
				{
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index_on_non_indexable", lhs));
				}
			}
			else if (op == "+")
			{
				if ((!(lhs is PyNumber) || !(returnValue is PyNumber)) && (!(lhs is PyList) || !(returnValue is IPySequence)) && (!(lhs is PyTuple) || !(returnValue is PyTuple)) && (!(lhs is PyString) || !(returnValue is PyString)))
				{
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_bin_operator", op, lhs, returnValue));
				}
			}
			else
			{
				if ((op == "/" || op == "//" || op == "%") && returnValue is PyNumber pyNumber && (double)pyNumber == 0.0)
				{
					throw new ExecuteException("error_division_by_zero");
				}
				if (op == "in" || op == "not in")
				{
					if (!(returnValue is PyDict) && !(returnValue is PySet) && !(returnValue is IPySequence))
					{
						throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_unary_operator", op, returnValue));
					}
				}
				else if (op == ".")
				{
					if (!(returnValue is PyFunction))
					{
						throw new ExecuteException("error_unknown_method");
					}
				}
				else if (!(lhs is PyNumber) || !(returnValue is PyNumber))
				{
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_bin_operator", op, lhs, returnValue));
				}
			}
		}
		int steps = 0;
		switch (op)
		{
		case "+":
			if (lhs is PyNumber)
			{
				state.ReturnValue = new PyNumber((double)(PyNumber)lhs + (double)(PyNumber)returnValue);
				steps = 1;
			}
			else if (lhs is PyList)
			{
				state.ReturnValue = new PyList(((PyList)lhs).Concat((IPySequence)returnValue).ToList());
				steps = Mathf.Max(1, ((PyList)lhs).Count + ((IPySequence)returnValue).Count);
			}
			else if (lhs is PyString)
			{
				state.ReturnValue = new PyString(((PyString)lhs).str + ((PyString)returnValue).str);
				steps = Mathf.Max(1, ((PyString)lhs).Count + ((PyString)returnValue).Count);
			}
			else if (lhs is PyTuple)
			{
				state.ReturnValue = new PyTuple(((PyTuple)lhs).Concat((PyTuple)returnValue).ToList());
				steps = Mathf.Max(1, ((PyTuple)lhs).Count + ((PyTuple)returnValue).Count);
			}
			break;
		case "-":
			state.ReturnValue = new PyNumber((double)(PyNumber)lhs - (double)(PyNumber)returnValue);
			steps = 1;
			break;
		case "*":
			state.ReturnValue = new PyNumber((double)(PyNumber)lhs * (double)(PyNumber)returnValue);
			steps = 1;
			break;
		case "/":
			state.ReturnValue = new PyNumber((double)(PyNumber)lhs / (double)(PyNumber)returnValue);
			steps = 1;
			break;
		case "//":
			state.ReturnValue = PyNumber.FloorDivision((PyNumber)lhs, (PyNumber)returnValue);
			steps = 1;
			break;
		case "%":
			state.ReturnValue = PyNumber.Modulo((PyNumber)lhs, (PyNumber)returnValue);
			steps = 1;
			break;
		case "**":
			state.ReturnValue = new PyNumber(Math.Pow((PyNumber)lhs, (PyNumber)returnValue));
			steps = 1;
			break;
		case "==":
			state.ReturnValue = new PyBool(CodeUtilities.DeepEquals(lhs, returnValue, ref steps));
			break;
		case "!=":
			state.ReturnValue = new PyBool(!CodeUtilities.DeepEquals(lhs, returnValue, ref steps));
			break;
		case ">=":
			state.ReturnValue = new PyBool(CodeUtilities.DeepCompare(lhs, returnValue, op, ref steps) >= 0);
			break;
		case "<=":
			state.ReturnValue = new PyBool(CodeUtilities.DeepCompare(lhs, returnValue, op, ref steps) <= 0);
			break;
		case ">":
			state.ReturnValue = new PyBool(CodeUtilities.DeepCompare(lhs, returnValue, op, ref steps) > 0);
			break;
		case "<":
			state.ReturnValue = new PyBool(CodeUtilities.DeepCompare(lhs, returnValue, op, ref steps) < 0);
			break;
		case "and":
			state.ReturnValue = returnValue;
			steps = 1;
			break;
		case "or":
			state.ReturnValue = returnValue;
			steps = 1;
			break;
		case "[]":
			state.ReturnValue = ((IPyIndexable)lhs).At((InternalPySequence)returnValue, ref steps);
			break;
		case "in":
			if (returnValue is IPySequence)
			{
				IPySequence pySequence2 = (IPySequence)returnValue;
				state.ReturnValue = new PyBool(pySequence2.Contains(lhs, ref steps));
			}
			else if (returnValue is PyDict)
			{
				PyDict pyDict2 = (PyDict)returnValue;
				state.ReturnValue = new PyBool(lhs != null && pyDict2.dict.ContainsKey(lhs));
				steps = lhs.Size();
			}
			else if (returnValue is PySet)
			{
				PySet pySet2 = (PySet)returnValue;
				state.ReturnValue = new PyBool(pySet2.Contains(lhs));
				steps = lhs.Size();
			}
			break;
		case "not in":
			if (returnValue is IPySequence)
			{
				IPySequence pySequence = (IPySequence)returnValue;
				state.ReturnValue = new PyBool(!pySequence.Contains(lhs, ref steps));
			}
			else if (returnValue is PyDict)
			{
				PyDict pyDict = (PyDict)returnValue;
				state.ReturnValue = new PyBool(lhs == null || !pyDict.dict.ContainsKey(lhs));
				steps = lhs.Size();
			}
			else if (returnValue is PySet)
			{
				PySet pySet = (PySet)returnValue;
				state.ReturnValue = new PyBool(!pySet.Contains(lhs));
				steps = lhs.Size();
			}
			break;
		case ".":
		{
			PyFunction pyFunction2 = (PyFunction)returnValue;
			state.ReturnValue = new PyFunction(pyFunction2.functionName, pyFunction2.syntaxTree, pyFunction2.parentScope, pyFunction2.binding, lhs, pyFunction2.isFree);
			steps = 0;
			break;
		}
		}
		if (CheckIncrementOpCount(state, execution, steps))
		{
			yield return 0.0;
		}
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		if (op != ".")
		{
			state.currentDependencies.Add(("operators", boxedParams.wordStart, boxedParams.wordEnd));
		}
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new BinaryExprNode(op, opTokenType, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}

	public override void CheckForNonsensicalCode()
	{
		base.CheckForNonsensicalCode();
		CheckTautologicalOrExpressions();
	}

	private void CheckTautologicalOrExpressions()
	{
		if (op == "or" && slots[0] is ComparisonNode && slots[1] is LiteralNode literalNode)
		{
			throw new ParseException(CodeUtilities.LocalizeAndFormat("error_nonsensical_or", literalNode.value), boxedParams.wordStart, boxedParams.wordEnd);
		}
	}
}
public class BracketNode : Node
{
	public override string NodeName => "bracket";

	public BracketNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public BracketNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		return slots[0].Execute(state, execution, depth + 1);
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new BracketNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class BranchNode : Node
{
	private bool looping;

	public override string NodeName
	{
		get
		{
			if (!looping)
			{
				return "if";
			}
			return "while";
		}
	}

	public BranchNode(CodeWindow func, int startIndex, int endIndex, bool looping = false)
		: base(func, startIndex, endIndex)
	{
		this.looping = looping;
	}

	public BranchNode(BoxedNodeParams boxedParams, bool looping = false)
		: base(boxedParams)
	{
		this.looping = looping;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		bool firstLoop = true;
		while (true)
		{
			bool condition;
			if (IsLiteralNode(slots[0], out var literal))
			{
				condition = Scope.IsTrueValue(literal.value);
				if (execution.sim.leaderboardType == LeaderboardType.none)
				{
					Achievements.UnlockAchievement("INFINITE_LOOP");
				}
			}
			else
			{
				foreach (double item in slots[0].Execute(state, execution, depth + 1))
				{
					yield return item;
				}
				condition = Scope.IsTrueValue(state.ReturnValue);
			}
			Blink(state, execution);
			if (firstLoop)
			{
				if (CheckIncrementOpCount(state, execution, 1.0))
				{
					yield return 0.0;
				}
				firstLoop = false;
			}
			if (!condition)
			{
				break;
			}
			IEnumerator<double> enumerator2 = slots[1].Execute(state, execution, depth + 1).GetEnumerator();
			while (true)
			{
				double current;
				try
				{
					if (!enumerator2.MoveNext())
					{
						break;
					}
					current = enumerator2.Current;
					goto IL_0218;
				}
				catch (BreakStatement breakStatement)
				{
					if (!looping)
					{
						throw breakStatement;
					}
					yield break;
				}
				catch (ContinueStatement continueStatement)
				{
					if (!looping)
					{
						throw continueStatement;
					}
				}
				break;
				IL_0218:
				yield return current;
			}
			if (!looping)
			{
				state.ReturnValue = new PyNone();
				yield break;
			}
			ErrorsAndBreakpoints(state, execution, depth);
			yield return 0.0;
		}
		if (slots.Count > 2)
		{
			foreach (double item2 in slots[2].Execute(state, execution, depth + 1))
			{
				yield return item2;
			}
		}
		state.ReturnValue = new PyNone();
	}

	private bool IsLiteralNode(Node node, out LiteralNode literal)
	{
		while (node is BracketNode bracketNode && bracketNode.slots.Count > 0)
		{
			node = bracketNode.slots[0];
		}
		if (node is LiteralNode literalNode)
		{
			literal = literalNode;
			return true;
		}
		literal = null;
		return false;
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add((looping ? "while" : "if", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new BranchNode(boxedParams, looping)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}

	public override void CheckForNonsensicalCode()
	{
		base.CheckForNonsensicalCode();
		CheckWeirdAlwaysTrueConditions();
	}

	private void CheckWeirdAlwaysTrueConditions()
	{
		if (slots[0] is LiteralNode literalNode)
		{
			if (literalNode.value is ItemSO)
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_item_condition", literalNode.value), literalNode.boxedParams.wordStart, literalNode.boxedParams.wordEnd);
			}
			if (literalNode.value is FarmObjectSO { isGround: false })
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_entity_condition", literalNode.value), literalNode.boxedParams.wordStart, literalNode.boxedParams.wordEnd);
			}
			if (literalNode.value is FarmObjectSO { isGround: not false })
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_ground_condition", literalNode.value), literalNode.boxedParams.wordStart, literalNode.boxedParams.wordEnd);
			}
			if (literalNode.value is UnlockSO)
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_unlock_condition", literalNode.value), literalNode.boxedParams.wordStart, literalNode.boxedParams.wordEnd);
			}
		}
	}
}
public class BreakNode : Node
{
	public override string NodeName => "break";

	public BreakNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public BreakNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		Blink(state, execution);
		if (CheckIncrementOpCount(state, execution, 0.0))
		{
			yield return 0.0;
		}
		throw new BreakStatement(boxedParams.wordStart, boxedParams.wordEnd);
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new BreakNode(boxedParams);
		return (Node)copies[this];
	}
}
public class CallNode : Node
{
	public override string NodeName => "call";

	public CallNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public CallNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		IPyObject returnValue = state.ReturnValue;
		if (!(returnValue is PyFunction))
		{
			state.CurrentExecutingNode = this;
			throw new ExecuteException(Localizer.Localize("error_not_a_function"));
		}
		PyFunction func = (PyFunction)returnValue;
		bool isStatic = state.IsExpressionStatic;
		foreach (double item2 in slots[1].Execute(state, execution, depth + 1))
		{
			yield return item2;
		}
		List<IPyObject> parameters = ((InternalPySequence)state.ReturnValue).elements;
		Blink(state, execution);
		if (func.methodObject != null)
		{
			parameters.Insert(0, func.methodObject);
		}
		if (execution.sim.leaderboardType == LeaderboardType.none && parameters.Any((IPyObject p) => p is PyFunction))
		{
			Achievements.UnlockAchievement("HIGHER_ORDER_PROGRAMMING");
		}
		state.CurrentExecutingNode = this;
		if (func.syntaxTree != null)
		{
			if (CheckIncrementOpCount(state, execution, (!isStatic) ? 1 : 0))
			{
				yield return 0.0;
			}
			FunctionNode functionNode = (FunctionNode)func.syntaxTree;
			functionNode.Arguments = parameters;
			state.PushScope(new Scope(functionNode, state.CurrentExecutingNode, func.parentScope, functionNode.Vars));
			state.PushOntoExecutionStack(func.syntaxTree.Execute(state, execution, 0));
			yield return 0.0;
			yield break;
		}
		state.currentDependencies.Add((func.functionName, boxedParams.wordStart, boxedParams.wordEnd));
		if (func.binding == null)
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_name_not_defined", func.functionName));
		}
		double ops = func.binding(parameters, execution.sim, execution, state.DroneId);
		if (CheckIncrementOpCount(state, execution, ops))
		{
			yield return 0.0;
		}
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new CallNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class ComparisonNode : Node
{
	public List<string> ops;

	public override string NodeName => "comparison";

	public ComparisonNode(List<string> ops, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.ops = ops;
	}

	public ComparisonNode(List<string> ops, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.ops = ops;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		List<IPyObject> operands = new List<IPyObject>();
		foreach (Node slot in slots)
		{
			foreach (double item in slot.Execute(state, execution, depth + 1))
			{
				yield return item;
			}
			operands.Add(state.ReturnValue);
		}
		Blink(state, execution);
		state.CurrentExecutingNode = this;
		int steps = 0;
		bool flag = true;
		for (int i = 0; i < ops.Count; i++)
		{
			string text = ops[i];
			IPyObject pyObject = operands[i];
			IPyObject pyObject2 = operands[i + 1];
			if ((pyObject is PyFunction || pyObject2 is PyFunction) && ((text != "==" && text != "!=" && text != "in" && text != "not in") || OptionHolder.GetString("error forgot call") == "enabled"))
			{
				PyFunction pyFunction = (PyFunction)((pyObject is PyFunction) ? pyObject : pyObject2);
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_function_in_operator", pyFunction.functionName, text));
			}
			switch (text)
			{
			case "in":
			case "not in":
				if (!(pyObject2 is PyDict) && !(pyObject2 is PySet) && !(pyObject2 is IPySequence))
				{
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_unary_operator", text, pyObject2));
				}
				break;
			default:
				if (!(pyObject is PyNumber) || !(pyObject2 is PyNumber))
				{
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_bin_operator", text, pyObject, pyObject2));
				}
				break;
			case "==":
			case "!=":
			case ">=":
			case "<=":
			case ">":
			case "<":
				break;
			}
			bool flag2 = true;
			switch (text)
			{
			case "==":
				flag2 = CodeUtilities.DeepEquals(pyObject, pyObject2, ref steps);
				break;
			case "!=":
				flag2 = !CodeUtilities.DeepEquals(pyObject, pyObject2, ref steps);
				break;
			case ">=":
				flag2 = CodeUtilities.DeepCompare(pyObject, pyObject2, text, ref steps) >= 0;
				break;
			case "<=":
				flag2 = CodeUtilities.DeepCompare(pyObject, pyObject2, text, ref steps) <= 0;
				break;
			case ">":
				flag2 = CodeUtilities.DeepCompare(pyObject, pyObject2, text, ref steps) > 0;
				break;
			case "<":
				flag2 = CodeUtilities.DeepCompare(pyObject, pyObject2, text, ref steps) < 0;
				break;
			case "in":
				if (pyObject2 is IPySequence)
				{
					flag2 = ((IPySequence)pyObject2).Contains(pyObject, ref steps);
				}
				else if (pyObject2 is PyDict)
				{
					PyDict pyDict2 = (PyDict)pyObject2;
					flag2 = pyObject != null && pyDict2.dict.ContainsKey(pyObject);
					steps += pyObject.Size();
				}
				else if (pyObject2 is PySet)
				{
					flag2 = ((PySet)pyObject2).Contains(pyObject);
					steps += pyObject.Size();
				}
				break;
			case "not in":
				if (pyObject2 is IPySequence)
				{
					flag2 = !((IPySequence)pyObject2).Contains(pyObject, ref steps);
				}
				else if (pyObject2 is PyDict)
				{
					PyDict pyDict = (PyDict)pyObject2;
					flag2 = pyObject == null || !pyDict.dict.ContainsKey(pyObject);
					steps += pyObject.Size();
				}
				else if (pyObject2 is PySet)
				{
					flag2 = !((PySet)pyObject2).Contains(pyObject);
					steps += pyObject.Size();
				}
				break;
			}
			flag = flag && flag2;
			if (!flag)
			{
				break;
			}
		}
		state.ReturnValue = new PyBool(flag);
		if (CheckIncrementOpCount(state, execution, steps))
		{
			yield return 0.0;
		}
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("operators", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new ComparisonNode(ops, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}

	public override void CheckForNonsensicalCode()
	{
		base.CheckForNonsensicalCode();
		CheckFarmLiteralsComparedWithNumbers();
	}

	private void CheckFarmLiteralsComparedWithNumbers()
	{
		for (int i = 0; i < ops.Count; i++)
		{
			string text = ops[i];
			Node node = slots[i];
			Node node2 = slots[i + 1];
			LiteralNode literalNode2;
			Node node3;
			if (node is LiteralNode literalNode && IsFarmLiteral(literalNode.value))
			{
				literalNode2 = literalNode;
				node3 = node2;
			}
			else
			{
				if (!(node2 is LiteralNode literalNode3) || !IsFarmLiteral(literalNode3.value))
				{
					break;
				}
				literalNode2 = literalNode3;
				node3 = node;
			}
			switch (text)
			{
			case "==":
			case "!=":
			case "in":
			case "not in":
				if (!(node3 is LiteralNode literalNode4) || !(literalNode4.value is PyNumber))
				{
					return;
				}
				break;
			}
			if (literalNode2.value is ItemSO)
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_compared_item_with_number", literalNode2.value), boxedParams.wordStart, boxedParams.wordEnd);
			}
			if (literalNode2.value is FarmObjectSO)
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_compared_entity_with_number", literalNode2.value), boxedParams.wordStart, boxedParams.wordEnd);
			}
			if (literalNode2.value is UnlockSO)
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_compared_unlock_with_number", literalNode2.value), boxedParams.wordStart, boxedParams.wordEnd);
			}
		}
	}

	private bool IsFarmLiteral(IPyObject obj)
	{
		if (!(obj is ItemSO) && !(obj is FarmObjectSO))
		{
			return obj is UnlockSO;
		}
		return true;
	}
}
public class ContinueNode : Node
{
	public override string NodeName => "continue";

	public ContinueNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public ContinueNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		Blink(state, execution);
		if (CheckIncrementOpCount(state, execution, 0.0))
		{
			yield return 0.0;
		}
		throw new ContinueStatement(boxedParams.wordStart, boxedParams.wordEnd);
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new ContinueNode(boxedParams);
		return (Node)copies[this];
	}
}
public class DefNode : Node
{
	public string funcName;

	private bool isStatic;

	public override string NodeName => "def";

	public DefNode(string funcName, bool isStatic, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.funcName = funcName;
		this.isStatic = isStatic;
	}

	public DefNode(string funcName, bool isStatic, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.funcName = funcName;
		this.isStatic = isStatic;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		Blink(state, execution);
		state.CurrentScope.SetVar(funcName, new PyFunction(funcName, slots[0], state.CurrentScope), checkShadow: true, isStatic);
		state.ReturnValue = new PyNone();
		if (CheckIncrementOpCount(state, execution, 1.0))
		{
			yield return 0.0;
		}
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("functions", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new DefNode(funcName, isStatic, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class PyFunction : IPyObject
{
	public string functionName;

	public Node syntaxTree;

	public Scope parentScope;

	public Func<List<IPyObject>, Simulation, Execution, int, double> binding;

	public IPyObject methodObject;

	public bool isFree;

	public PyFunction(string functionName, Node syntaxTree, Scope parentScope, Func<List<IPyObject>, Simulation, Execution, int, double> binding, IPyObject methodObject, bool isFree)
	{
		this.functionName = functionName;
		this.syntaxTree = syntaxTree;
		this.parentScope = parentScope;
		this.binding = binding;
		this.methodObject = methodObject;
		this.isFree = isFree;
	}

	public PyFunction(string functionName, Func<List<IPyObject>, Simulation, Execution, int, double> binding, IPyObject methodObject = null, bool isFree = false)
	{
		this.functionName = functionName;
		syntaxTree = null;
		parentScope = null;
		this.methodObject = methodObject;
		this.isFree = isFree;
		this.binding = binding;
	}

	public PyFunction(string functionName, Node syntaxTree = null, Scope parentScope = null)
	{
		this.functionName = functionName;
		this.syntaxTree = syntaxTree;
		this.parentScope = parentScope;
		methodObject = null;
		isFree = false;
		binding = null;
	}

	public IPyObject DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.ContainsKey(this))
		{
			return (PyFunction)copies[this];
		}
		PyFunction pyFunction = (PyFunction)(copies[this] = new PyFunction(functionName, null, null, binding, methodObject, isFree));
		pyFunction.syntaxTree = syntaxTree?.DeepCopy(copies);
		pyFunction.parentScope = parentScope?.DeepCopy(copies);
		pyFunction.methodObject = methodObject?.DeepCopy(copies);
		return pyFunction;
	}

	public override string ToString()
	{
		return functionName;
	}
}
public class DictNode : Node
{
	public override string NodeName => "dict";

	public DictNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public DictNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		List<IPyObject> elements = ((InternalPySequence)state.ReturnValue).elements;
		Dictionary<IPyObject, PyObjectBox> dictionary = new Dictionary<IPyObject, PyObjectBox>();
		for (int i = 0; i < elements.Count; i += 2)
		{
			IPyObject pyObject = elements[i];
			if (pyObject is PyList || pyObject is PyDict || pyObject is PySet || pyObject is PyModule)
			{
				state.CurrentExecutingNode = this;
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_key", elements[i]));
			}
			dictionary[elements[i]] = new PyObjectBox(elements[i + 1]);
		}
		state.ReturnValue = new PyDict(dictionary);
		state.IsExpressionStatic = false;
		Blink(state, execution);
		if (CheckIncrementOpCount(state, execution, 1 + dictionary.Count))
		{
			yield return 0.0;
		}
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("dicts", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new DictNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class ForNode : Node
{
	public Node pattern;

	public override string NodeName => "for";

	public ForNode(Node pattern, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.pattern = pattern;
	}

	public ForNode(Node pattern, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.pattern = pattern;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		if (state.ReturnValue is IEnumerable<IPyObject>)
		{
			IEnumerable<IPyObject> enumerable = (IEnumerable<IPyObject>)state.ReturnValue;
			IEnumerator<IPyObject> enumerator2 = enumerable.GetEnumerator();
			(enumerator2 as PyCollectionEnumerator)?.SetErrorIndices(boxedParams.wordStart, boxedParams.wordEnd);
			if (CheckIncrementOpCount(state, execution, 1.0))
			{
				yield return 0.0;
			}
			while (enumerator2.MoveNext())
			{
				IPyObject current = enumerator2.Current;
				foreach (double item2 in AssignmentNode.Assign(state, execution, depth, pattern, current, "=", boxedParams.codeWindow.fileName))
				{
					yield return item2;
				}
				Blink(state, execution);
				IEnumerator<double> enumerator4 = slots[1].Execute(state, execution, depth + 1).GetEnumerator();
				while (true)
				{
					double current2;
					try
					{
						if (!enumerator4.MoveNext())
						{
							break;
						}
						current2 = enumerator4.Current;
						goto IL_02a9;
					}
					catch (BreakStatement)
					{
						yield break;
					}
					catch (ContinueStatement)
					{
					}
					break;
					IL_02a9:
					yield return current2;
				}
				ErrorsAndBreakpoints(state, execution, depth);
			}
			yield break;
		}
		state.CurrentExecutingNode = this;
		throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_for_requires_iterable", state.ReturnValue));
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("for", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new ForNode(pattern.DeepCopy(copies), boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class FunctionNode : Node
{
	private List<string> paramNames;

	private string funcName;

	public override string NodeName => "func";

	public string FuncName => funcName;

	public HashSet<string> Vars { get; set; }

	public List<IPyObject> Arguments { get; set; }

	public FunctionNode(List<string> paramNames, string funcName, bool global, CodeWindow codeWindow, int startIndex, int endIndex)
		: base(codeWindow, startIndex, endIndex)
	{
		this.paramNames = paramNames;
		this.funcName = funcName;
		if (global)
		{
			codeWindow.parsedFunctions[funcName] = this;
		}
	}

	public FunctionNode(List<string> paramNames, string funcName, bool global, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.paramNames = paramNames;
		this.funcName = funcName;
		if (global)
		{
			boxedParams.codeWindow.parsedFunctions[funcName] = this;
		}
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		int num = paramNames.Count - Arguments.Count;
		int numDefaultValues = slots.Count - 1;
		if (num < 0 || num > numDefaultValues)
		{
			PyTuple pyTuple = new PyTuple(Arguments);
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_wrong_number_args", funcName, paramNames.Count, pyTuple));
		}
		ErrorsAndBreakpoints(state, execution, depth);
		for (int i = numDefaultValues - num; i < numDefaultValues; i++)
		{
			foreach (double item in slots[i + 1].Execute(state, execution, depth + 1))
			{
				yield return item;
			}
			Arguments.Add(state.ReturnValue);
		}
		for (int j = 0; j < paramNames.Count; j++)
		{
			state.CurrentScope.SetVar(paramNames[j], Arguments[j]);
		}
		Blink(state, execution);
		IEnumerator<double> block = slots[0].Execute(state, execution, depth + 1).GetEnumerator();
		while (true)
		{
			double current;
			try
			{
				if (!block.MoveNext())
				{
					break;
				}
				current = block.Current;
				goto IL_0269;
			}
			catch (BreakStatement)
			{
				throw new ExecuteException("error_no_loop_to_break");
			}
			catch (ContinueStatement)
			{
				throw new ExecuteException("error_no_loop_to_continue");
			}
			catch (ReturnStatement)
			{
				state.PopScope();
				yield break;
			}
			IL_0269:
			yield return current;
		}
		state.ReturnValue = new PyNone();
		state.IsExpressionStatic = false;
		state.PopScope();
	}

	public string GetSignature()
	{
		return GetSubstringWithComments(boxedParams.codeWindow.CodeInput.text, boxedParams.wordStart, boxedParams.wordEnd);
	}

	private static string GetSubstringWithComments(string input, int index1, int index2)
	{
		string[] array = input.Split('\n');
		int lineIndexFromCharacterIndex = GetLineIndexFromCharacterIndex(array, index1);
		int lineIndexFromCharacterIndex2 = GetLineIndexFromCharacterIndex(array, index2);
		int num = lineIndexFromCharacterIndex;
		while (num > 0 && array[num - 1].StartsWith('#'))
		{
			num--;
		}
		int num2 = lineIndexFromCharacterIndex2;
		return string.Join(Environment.NewLine, array[num..(num2 + 1)]);
	}

	private static int GetLineIndexFromCharacterIndex(string[] lines, int characterIndex)
	{
		int num = 0;
		for (int i = 0; i < lines.Length; i++)
		{
			num += lines[i].Length + 1;
			if (num > characterIndex)
			{
				return i;
			}
		}
		return -1;
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new FunctionNode(paramNames, funcName, global: false, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList(),
			Vars = Vars
		};
		return (Node)copies[this];
	}
}
public class ImportNode : Node
{
	private List<string> moduleNames;

	private bool unpack;

	private bool unpackAll;

	private List<string> varsToUnpack;

	private bool isStatic;

	public override string NodeName => "import";

	public ImportNode(CodeWindow func, int startIndex, int endIndex, List<string> moduleNames, bool unpack, bool unpackAll, List<string> varsToUnpack, bool isStatic)
		: base(func, startIndex, endIndex)
	{
		this.moduleNames = moduleNames;
		this.unpack = unpack;
		this.unpackAll = unpackAll;
		this.varsToUnpack = varsToUnpack;
		this.isStatic = isStatic;
	}

	public ImportNode(BoxedNodeParams boxedParams, List<string> moduleNames, bool unpack, bool unpackAll, List<string> varsToUnpack, bool isStatic)
		: base(boxedParams)
	{
		this.moduleNames = moduleNames;
		this.unpack = unpack;
		this.unpackAll = unpackAll;
		this.varsToUnpack = varsToUnpack;
		this.isStatic = isStatic;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		Blink(state, execution);
		if (CheckIncrementOpCount(state, execution, 0.0))
		{
			yield return 0.0;
		}
		foreach (string name in moduleNames)
		{
			if (name == "__builtins__" || name == "builtins")
			{
				continue;
			}
			if (!state.ModuleCache.ContainsKey(name))
			{
				if (!MainSim.Inst.workspace.codeWindows.TryGetValue(name, out var value))
				{
					throw new ExecuteException("error_module_not_found");
				}
				Node node = value.Parse();
				if (state.DroneId > 0)
				{
					Dictionary<object, object> copies = new Dictionary<object, object>();
					node = node.DeepCopy(copies);
				}
				if (node == null)
				{
					throw new ExecuteException("error_syntax_error_in_import");
				}
				Dictionary<string, (IPyObject, bool)> dictionary = new Dictionary<string, (IPyObject, bool)>();
				dictionary["__name__"] = (new PyString(name), false);
				state.ModuleCache[name] = new PyModule(dictionary, name);
				Scope scope = new Scope(null, null, null, dictionary);
				foreach (PyFunction item in BuiltinFunctions.Functions.Values.Concat(BuiltinFunctions.Methods.Values))
				{
					scope.SetVar(item.functionName, item, checkShadow: false, isStatic: true);
				}
				ModuleState moduleState = new ModuleState
				{
					globalScope = scope,
					currentExecutingNode = node
				};
				ModuleState oldModuleState = state.moduleState;
				state.moduleState = moduleState;
				foreach (double item2 in node.Execute(state, execution, depth))
				{
					yield return item2;
				}
				state.moduleState = oldModuleState;
				state.ModuleCache[name].fullyInitialized = true;
			}
			else if (execution.sim.leaderboardType == LeaderboardType.none && !state.ModuleCache[name].fullyInitialized)
			{
				Achievements.UnlockAchievement("CIRCULAR_IMPORT");
			}
			if (unpack)
			{
				if (unpackAll)
				{
					try
					{
						foreach (KeyValuePair<string, (IPyObject, bool)> element in state.ModuleCache[name].elements)
						{
							if (!element.Key.StartsWith('_'))
							{
								state.CurrentScope.ImportVar(element.Key, element.Value.Item1, element.Value.Item2);
							}
						}
					}
					catch (InvalidOperationException)
					{
					}
					continue;
				}
				foreach (string item3 in varsToUnpack)
				{
					(IPyObject, bool) tuple = state.ModuleCache[name].Export(item3, boxedParams.wordStart, boxedParams.wordEnd);
					state.CurrentScope.ImportVar(item3, tuple.Item1, tuple.Item2);
				}
			}
			else
			{
				state.CurrentScope.ImportVar(name, state.ModuleCache[name], isStatic);
			}
		}
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		if (moduleNames.Count != 1 || moduleNames[0] != "__builtins__")
		{
			state.currentDependencies.Add(("import", boxedParams.wordStart, boxedParams.wordEnd));
		}
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new ImportNode(boxedParams, moduleNames, unpack, unpackAll, varsToUnpack, isStatic)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class ListNode : Node
{
	public override string NodeName => "list";

	public ListNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public ListNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		Blink(state, execution);
		PyList pyList = (PyList)(state.ReturnValue = new PyList(((InternalPySequence)state.ReturnValue).elements.ToList()));
		state.IsExpressionStatic = false;
		if (CheckIncrementOpCount(state, execution, Math.Max(1, pyList.Count)))
		{
			yield return 0.0;
		}
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("lists", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new ListNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class LiteralNode : Node
{
	public IPyObject value;

	public override string NodeName => "literal";

	public LiteralNode(IPyObject value, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.value = value;
	}

	public LiteralNode(IPyObject value, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.value = value;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		Blink(state, execution);
		state.ReturnValue = value;
		state.IsExpressionStatic = false;
		yield break;
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var obj))
		{
			return (Node)obj;
		}
		copies[this] = new LiteralNode(value, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public abstract class Node
{
	public List<Node> slots = new List<Node>();

	public BoxedNodeParams boxedParams;

	public const int TICKS_PER_OP = 1;

	public virtual string NodeName => "";

	public bool blink => boxedParams.wordEnd > boxedParams.wordStart;

	public Node(CodeWindow codeWindow, int startIndex, int endIndex)
	{
		boxedParams = new BoxedNodeParams();
		boxedParams.codeWindow = codeWindow;
		boxedParams.wordStart = startIndex;
		boxedParams.wordEnd = endIndex;
	}

	public Node(BoxedNodeParams boxedParams)
	{
		this.boxedParams = boxedParams;
	}

	public abstract IEnumerable<double> Execute(ProgramState state, Execution execution, int depth);

	protected void ErrorsAndBreakpoints(ProgramState state, Execution execution, int depth)
	{
		if (depth > 1100)
		{
			if (execution.sim.leaderboardType == LeaderboardType.none)
			{
				Achievements.UnlockAchievement("STACK_OVERFLOW");
			}
			throw new ExecuteException("error_max_stack_size_reached");
		}
		if (boxedParams.executionId != execution.Id)
		{
			boxedParams.executionId = execution.Id;
			if (OptionHolder.GetString("allow locked features") != "enabled")
			{
				CheckDependencies(state, execution);
			}
		}
		if (boxedParams.isBreakpoint && !execution.sim.stepByStepMode && execution.sim.mainSim != null)
		{
			Blink(state, execution);
			state.hitBreakpoint = true;
		}
		if (execution.sim.stepByStepMode && execution.MainState == state && !IsOnSameLine(state.CurrentExecutingNode))
		{
			Blink(state, execution);
			state.hitStoppingPoint = true;
		}
		state.CurrentExecutingNode = this;
	}

	public bool CheckIncrementOpCount(ProgramState state, Execution execution, double ops)
	{
		state.OpCount += ops;
		if (!(state.OpCount >= state.TargetOpCount) && !state.hitBreakpoint && !state.hitStoppingPoint)
		{
			return state.currentSideEffect != SideEffect.None;
		}
		return true;
	}

	public void Blink(ProgramState state, Execution execution)
	{
		if (state == execution.MainState && execution.sim.mainSim != null)
		{
			execution.sim.mainSim.BlinkEffect(this);
		}
	}

	public virtual void CheckForNonsensicalCode()
	{
		foreach (Node slot in slots)
		{
			slot?.CheckForNonsensicalCode();
		}
	}

	public virtual void CheckDependencies(ProgramState state, Execution execution)
	{
	}

	public void InsertBreakpointsRec(HashSet<int> breakpointCharPositions)
	{
		boxedParams.isBreakpoint = false;
		foreach (int item in breakpointCharPositions.ToList())
		{
			if (item <= boxedParams.wordStart)
			{
				boxedParams.isBreakpoint = true;
				breakpointCharPositions.Remove(item);
			}
		}
		foreach (Node slot in slots)
		{
			slot?.InsertBreakpointsRec(breakpointCharPositions);
		}
	}

	public abstract Node DeepCopy(Dictionary<object, object> copies);

	public override string ToString()
	{
		string text = NodeName;
		if (slots.Count > 0)
		{
			text += " (";
			foreach (Node slot in slots)
			{
				text += slot;
				text += ", ";
			}
			text += ")";
		}
		return text;
	}

	private bool IsOnSameLine(Node other)
	{
		CodeWindow codeWindow = boxedParams.codeWindow;
		if (other == null || codeWindow != other.boxedParams.codeWindow)
		{
			return false;
		}
		int lineNumber = codeWindow.CodeInput.textComponent.textInfo.characterInfo[boxedParams.wordStart].lineNumber;
		int lineNumber2 = codeWindow.CodeInput.textComponent.textInfo.characterInfo[other.boxedParams.wordStart].lineNumber;
		return lineNumber == lineNumber2;
	}
}
public class BoxedNodeParams
{
	public bool isBreakpoint;

	public int executionId = -1;

	public int wordStart = -1;

	public int wordEnd = -1;

	public CodeWindow codeWindow;
}
public class NoOpNode : Node
{
	public override string NodeName => "noop";

	public NoOpNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		yield break;
	}
}
public class PassNode : Node
{
	public override string NodeName => "pass";

	public PassNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public PassNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		Blink(state, execution);
		if (CheckIncrementOpCount(state, execution, 1.0))
		{
			yield return 0.0;
		}
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		return new PassNode(boxedParams);
	}
}
public class ReturnNode : Node
{
	public override string NodeName => "return";

	public ReturnNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public ReturnNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		if (slots.Count > 0)
		{
			foreach (double item in slots[0].Execute(state, execution, depth + 1))
			{
				yield return item;
			}
		}
		else
		{
			state.ReturnValue = new PyNone();
		}
		Blink(state, execution);
		if (CheckIncrementOpCount(state, execution, 0.0))
		{
			yield return 0.0;
		}
		state.CurrentExecutingNode = this;
		throw new ReturnStatement(boxedParams.wordStart, boxedParams.wordEnd);
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new ReturnNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class SequenceNode : Node
{
	private InternalPySequence internalPySequence = new InternalPySequence(new List<IPyObject>());

	public override string NodeName => "seq";

	public SequenceNode(CodeWindow func)
		: base(func, 0, 0)
	{
	}

	public SequenceNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		InternalPySequence pySequence;
		if (internalPySequence == null)
		{
			pySequence = new InternalPySequence(new List<IPyObject>());
		}
		else
		{
			pySequence = internalPySequence;
			pySequence.elements.Clear();
			internalPySequence = null;
		}
		foreach (Node slot in slots)
		{
			foreach (double item in slot.Execute(state, execution, depth + 1))
			{
				yield return item;
			}
			pySequence.elements.Add(state.ReturnValue);
		}
		state.ReturnValue = pySequence;
		if (internalPySequence == null)
		{
			internalPySequence = pySequence;
		}
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new SequenceNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class SetNode : Node
{
	public override string NodeName => "set";

	public SetNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public SetNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		List<IPyObject> elements = ((InternalPySequence)state.ReturnValue).elements;
		HashSet<IPyObject> hashSet = new HashSet<IPyObject>();
		for (int i = 0; i < elements.Count; i++)
		{
			IPyObject pyObject = elements[i];
			if (pyObject is PyList || pyObject is PyDict || pyObject is PySet || pyObject is PyModule)
			{
				state.CurrentExecutingNode = this;
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_key", elements[i]));
			}
			hashSet.Add(elements[i]);
		}
		state.ReturnValue = new PySet(hashSet);
		state.IsExpressionStatic = false;
		Blink(state, execution);
		if (CheckIncrementOpCount(state, execution, Math.Max(1, state.ReturnValue.Size())))
		{
			yield return 0.0;
		}
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("sets", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new SetNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class TupleNode : Node
{
	public override string NodeName => "tuple";

	public TupleNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public TupleNode(BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		List<IPyObject> elements = ((InternalPySequence)state.ReturnValue).elements.ToList();
		state.ReturnValue = new PyTuple(elements);
		state.IsExpressionStatic = false;
		if (CheckIncrementOpCount(state, execution, 1.0))
		{
			yield return 0.0;
		}
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new TupleNode(boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class UnaryExprNode : Node
{
	private string op;

	public override string NodeName => "unary";

	public UnaryExprNode(string op, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.op = op;
	}

	public UnaryExprNode(string op, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.op = op;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		foreach (double item in slots[0].Execute(state, execution, depth + 1))
		{
			yield return item;
		}
		IPyObject returnValue = state.ReturnValue;
		state.CurrentExecutingNode = this;
		if (returnValue is PyFunction && op != "not")
		{
			PyFunction pyFunction = (PyFunction)returnValue;
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_function_in_operator", pyFunction.functionName, op));
		}
		switch (op)
		{
		case "+":
			if (!(returnValue is PyNumber))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_unary_operator", op, returnValue));
			}
			state.ReturnValue = returnValue;
			break;
		case "-":
			if (!(returnValue is PyNumber))
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_unary_operator", op, returnValue));
			}
			state.ReturnValue = new PyNumber(0.0 - (double)(PyNumber)returnValue);
			break;
		case "not":
			state.ReturnValue = new PyBool(!Scope.IsTrueValue(returnValue));
			break;
		}
		Blink(state, execution);
	}

	public override void CheckDependencies(ProgramState state, Execution execution)
	{
		state.currentDependencies.Add(("operators", boxedParams.wordStart, boxedParams.wordEnd));
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var value))
		{
			return (Node)value;
		}
		copies[this] = new UnaryExprNode(op, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class ValueNode : Node
{
	public string value;

	public override string NodeName => "value";

	public ValueNode(string value, CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
		this.value = value;
	}

	public ValueNode(string value, BoxedNodeParams boxedParams)
		: base(boxedParams)
	{
		this.value = value;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		Blink(state, execution);
		(state.ReturnValue, state.IsExpressionStatic) = state.CurrentScope.Evaluate(value, boxedParams.codeWindow.fileName);
		yield break;
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.TryGetValue(this, out var obj))
		{
			return (Node)obj;
		}
		copies[this] = new ValueNode(value, boxedParams)
		{
			slots = slots.Select((Node s) => s.DeepCopy(copies)).ToList()
		};
		return (Node)copies[this];
	}
}
public class Parser
{
	private static List<(List<TokenType> types, Func<TokenStream, CodeWindow, int, bool, TokenType, bool, Node> evaluationFunc)> operators = new List<(List<TokenType>, Func<TokenStream, CodeWindow, int, bool, TokenType, bool, Node>)>
	{
		(new List<TokenType> { TokenType.OR }, BinaryExpression),
		(new List<TokenType> { TokenType.AND }, BinaryExpression),
		(new List<TokenType> { TokenType.NOT }, UnaryExpression),
		(new List<TokenType>
		{
			TokenType.COMPARE,
			TokenType.IN
		}, BinaryExpression),
		(new List<TokenType> { TokenType.ADD }, BinaryExpression),
		(new List<TokenType> { TokenType.MULT }, BinaryExpression),
		(new List<TokenType> { TokenType.ADD }, UnaryExpression),
		(new List<TokenType> { TokenType.EXP }, BinaryExpression),
		(new List<TokenType>
		{
			TokenType.BRACKET_OPEN,
			TokenType.SQUARE_BRACKET_OPEN,
			TokenType.DOT
		}, IndexDotOrCallExpression)
	};

	public static Program Parse(TokenStream stream, CodeWindow f)
	{
		HashSet<string> allVars = new HashSet<string>();
		HashSet<string> importedModules = new HashSet<string>();
		HashSet<string> hashSet = new HashSet<string>();
		Node syntaxTree = Block(stream, f, -1, hashSet, hashSet, allVars, importedModules, global: true, isStatic: true);
		if (stream.Current != null)
		{
			throw new ParseException("error_code_after_block", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
		}
		return new Program(syntaxTree, hashSet, allVars, importedModules);
	}

	private static DefNode Function(TokenStream stream, CodeWindow f, int indentation, HashSet<string> allVars, HashSet<string> importedModules, bool global = false, bool isStatic = false)
	{
		Token token = stream.Consume(TokenType.DEF);
		Token token2 = stream.Consume(TokenType.IDENTIFIER);
		OptionalGenericTypeAnnotation(stream);
		stream.Consume(TokenType.BRACKET_OPEN);
		LineBreaks(stream);
		HashSet<string> hashSet = new HashSet<string>();
		List<string> list = new List<string>();
		List<Node> list2 = new List<Node>();
		bool flag = false;
		while (true)
		{
			Token current = stream.Current;
			if (current != null && current.type == TokenType.BRACKET_CLOSE)
			{
				break;
			}
			string value = stream.Consume(TokenType.IDENTIFIER).value;
			list.Add(value);
			hashSet.Add(value);
			allVars.Add(value);
			OptionalVariableTypeAnnotation(stream);
			LineBreaks(stream);
			Token current2 = stream.Current;
			if (current2 != null && current2.type == TokenType.ASSIGN)
			{
				stream.Consume(TokenType.ASSIGN);
				LineBreaks(stream);
				list2.Add(Expression(stream, f, 0, canLineBreak: true));
				flag = true;
			}
			else if (flag)
			{
				throw new ParseException("error_missing_default_parameter", token.startIndex, stream.CurrentStringEndIndex);
			}
			Token current3 = stream.Current;
			if (current3 == null || current3.type != TokenType.COMMA)
			{
				break;
			}
			stream.Consume(TokenType.COMMA);
			LineBreaks(stream);
		}
		stream.Consume(TokenType.BRACKET_CLOSE);
		OptionalReturnTypeAnnotation(stream);
		Token token3 = ConsumeColon(stream);
		FunctionNode functionNode = new FunctionNode(list, token2.value, global, f, token.startIndex, token3.startIndex + token3.value.Length);
		functionNode.boxedParams.codeWindow = f;
		functionNode.slots.Add(Block(stream, f, indentation, hashSet, new HashSet<string>(), allVars, importedModules, global: false, isStatic: true));
		functionNode.Vars = hashSet;
		foreach (Node item in list2)
		{
			functionNode.slots.Add(item);
		}
		return new DefNode(token2.value, isStatic, f, token.startIndex, token.startIndex + token.value.Length)
		{
			slots = { (Node)functionNode }
		};
	}

	private static Node Block(TokenStream stream, CodeWindow f, int prevIndentation, HashSet<string> vars, HashSet<string> globalVars, HashSet<string> allVars, HashSet<string> importedModules, bool global = false, bool isStatic = false)
	{
		if (global && stream.Current == null)
		{
			return new SequenceNode(f);
		}
		Token current = stream.Current;
		if (current == null || current.type != TokenType.NEW_LINE)
		{
			throw new ParseException("error_no_statements", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
		}
		int startIndex = stream.CurrentStringStartIndex + 1;
		int currentStringEndIndex = stream.CurrentStringEndIndex;
		int indentation = GetIndentation(stream);
		if (indentation <= prevIndentation)
		{
			throw new ParseException("error_not_enough_indentation", startIndex, currentStringEndIndex);
		}
		List<Node> list = new List<Node>();
		int num;
		for (num = indentation; num == indentation; num = GetIndentation(stream))
		{
			stream.Consume(TokenType.NEW_LINE);
			list.Add(Statement(stream, f, indentation, vars, globalVars, allVars, importedModules, global, isStatic));
			Token current2 = stream.Current;
			if (current2 == null || current2.type != TokenType.NEW_LINE)
			{
				break;
			}
		}
		startIndex = stream.CurrentStringStartIndex + 1;
		currentStringEndIndex = stream.CurrentStringEndIndex;
		if (num > indentation)
		{
			throw new ParseException("error_too_much_indentation", startIndex, currentStringEndIndex);
		}
		if (!global && list.Count == 0)
		{
			throw new ParseException("error_no_statements", startIndex, currentStringEndIndex);
		}
		return new SequenceNode(f)
		{
			slots = list
		};
	}

	private static Node Statement(TokenStream stream, CodeWindow f, int indentation, HashSet<string> vars, HashSet<string> globalVars, HashSet<string> allVars, HashSet<string> importedModules, bool global = false, bool isStatic = false)
	{
		Token current = stream.Current;
		if (current != null && current.type == TokenType.DEF)
		{
			DefNode defNode = Function(stream, f, indentation, allVars, importedModules, global, isStatic);
			if (!globalVars.Contains(defNode.funcName))
			{
				vars.Add(defNode.funcName);
			}
			allVars.Add(defNode.funcName);
			return defNode;
		}
		Token current2 = stream.Current;
		if (current2 != null && current2.type == TokenType.PASS)
		{
			Token token = stream.Consume(TokenType.PASS);
			return new PassNode(f, token.startIndex, token.startIndex + token.value.Length);
		}
		Token current3 = stream.Current;
		if (current3 != null && current3.type == TokenType.BREAK)
		{
			Token token2 = stream.Consume(TokenType.BREAK);
			return new BreakNode(f, token2.startIndex, token2.startIndex + token2.value.Length);
		}
		Token current4 = stream.Current;
		if (current4 != null && current4.type == TokenType.CONTINUE)
		{
			Token token3 = stream.Consume(TokenType.CONTINUE);
			return new ContinueNode(f, token3.startIndex, token3.startIndex + token3.value.Length);
		}
		Token current5 = stream.Current;
		if (current5 != null && current5.type == TokenType.RETURN)
		{
			Token token4 = stream.Consume(TokenType.RETURN);
			Node node = new ReturnNode(f, token4.startIndex, token4.startIndex + token4.value.Length);
			if (stream.Current != null)
			{
				Token current6 = stream.Current;
				if (current6 == null || current6.type != TokenType.NEW_LINE)
				{
					node.slots.Add(TupleOrExpression(stream, f));
				}
			}
			return node;
		}
		Token current7 = stream.Current;
		if (current7 != null && current7.type == TokenType.GLOBAL)
		{
			stream.Consume(TokenType.GLOBAL);
			Token token5 = stream.Consume(TokenType.IDENTIFIER);
			OptionalVariableTypeAnnotation(stream);
			if (vars.Contains(token5.value))
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_assign_before_global", token5.value), token5.startIndex, token5.startIndex + token5.value.Length);
			}
			globalVars.Add(token5.value);
			return new NoOpNode(f, token5.startIndex, token5.startIndex + token5.value.Length);
		}
		Token current8 = stream.Current;
		if (current8 != null && current8.type == TokenType.IMPORT)
		{
			Token token6 = stream.Consume(TokenType.IMPORT);
			List<string> list = SequenceOfIdentifiers(stream, "error_invalid_import");
			foreach (string item in list)
			{
				if (!globalVars.Contains(item))
				{
					vars.Add(item);
				}
				allVars.Add(item);
			}
			return new ImportNode(f, token6.startIndex, stream.CurrentStringStartIndex - 1, list, unpack: false, unpackAll: false, null, isStatic);
		}
		Token current10 = stream.Current;
		if (current10 != null && current10.type == TokenType.FROM)
		{
			Token token7 = stream.Consume(TokenType.FROM);
			Token token8 = stream.Consume(TokenType.IDENTIFIER, "error_invalid_import");
			stream.Consume(TokenType.IMPORT, "error_invalid_import");
			if (stream.Current?.value == "*")
			{
				if (!global)
				{
					throw new ParseException("error_wildcard_imports_not_allowed_in_function", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
				}
				stream.Consume(TokenType.MULT);
				importedModules.Add(token8.value);
				return new ImportNode(f, token7.startIndex, stream.CurrentStringStartIndex, new List<string> { token8.value }, unpack: true, unpackAll: true, null, isStatic);
			}
			List<string> list2 = SequenceOfIdentifiers(stream);
			foreach (string item2 in list2)
			{
				if (!globalVars.Contains(item2))
				{
					vars.Add(item2);
				}
				allVars.Add(item2);
			}
			return new ImportNode(f, token7.startIndex, stream.CurrentStringStartIndex, new List<string> { token8.value }, unpack: true, unpackAll: false, list2, isStatic);
		}
		Token current12 = stream.Current;
		if (current12 == null || current12.type != TokenType.WHILE)
		{
			Token current13 = stream.Current;
			if (current13 == null || current13.type != TokenType.FOR)
			{
				Token current14 = stream.Current;
				if (current14 == null || current14.type != TokenType.IF)
				{
					Node node2 = TupleOrExpression(stream, f, canLineBreak: false, TokenType.ASSIGN, null, isLeftmostExpression: true);
					Token current15 = stream.Current;
					if (current15 != null && current15.type == TokenType.ASSIGN)
					{
						return Assignment(stream, f, node2, vars, globalVars, allVars);
					}
					if (!(node2 is FunctionNode) && !(node2 is CallNode))
					{
						if (node2 is ValueNode)
						{
							string value = ((ValueNode)node2).value;
							if (BuiltinFunctions.Functions.ContainsKey(value) || BuiltinFunctions.Methods.ContainsKey(value))
							{
								throw new ParseException(CodeUtilities.LocalizeAndFormat("error_not_a_statement2", value + "()"), node2.boxedParams.wordStart, node2.boxedParams.wordEnd);
							}
						}
						throw new ParseException("error_not_a_statement", node2.boxedParams.wordStart, node2.boxedParams.wordEnd);
					}
					return node2;
				}
			}
		}
		return FlowControll(stream, f, indentation, vars, globalVars, allVars, importedModules);
	}

	private static List<string> SequenceOfIdentifiers(TokenStream stream, string error = null)
	{
		List<string> list = new List<string>();
		Token current = stream.Current;
		if (current != null && current.type == TokenType.BRACKET_OPEN)
		{
			stream.Consume(TokenType.BRACKET_OPEN);
			LineBreaks(stream);
			list.Add(stream.Consume(TokenType.IDENTIFIER, error).value);
			LineBreaks(stream);
			while (true)
			{
				Token current2 = stream.Current;
				if (current2 != null && current2.type == TokenType.COMMA)
				{
					stream.Consume(TokenType.COMMA);
					LineBreaks(stream);
					Token current3 = stream.Current;
					if (current3 != null && current3.type == TokenType.BRACKET_CLOSE)
					{
						stream.Consume(TokenType.BRACKET_CLOSE);
						break;
					}
					list.Add(stream.Consume(TokenType.IDENTIFIER, error).value);
					LineBreaks(stream);
					continue;
				}
				stream.Consume(TokenType.BRACKET_CLOSE, error);
				break;
			}
		}
		else
		{
			list.Add(stream.Consume(TokenType.IDENTIFIER, error).value);
			while (true)
			{
				Token current4 = stream.Current;
				if (current4 == null || current4.type != TokenType.COMMA)
				{
					break;
				}
				stream.Consume(TokenType.COMMA);
				list.Add(stream.Consume(TokenType.IDENTIFIER, error).value);
			}
			if (error != null && stream.Current != null)
			{
				Token current5 = stream.Current;
				if (current5 == null || current5.type != TokenType.NEW_LINE)
				{
					throw new ParseException(error, stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
				}
			}
		}
		return list;
	}

	private static Node Assignment(TokenStream stream, CodeWindow f, Node lhs, HashSet<string> vars, HashSet<string> globalVars, HashSet<string> allVars)
	{
		Token token = stream.Consume(TokenType.ASSIGN);
		Node item = TupleOrExpression(stream, f);
		CheckAssignmentLhsRec(lhs, f, vars, globalVars, allVars);
		return new AssignmentNode(token.value, f, token.startIndex, token.startIndex + token.value.Length)
		{
			slots = { lhs, item }
		};
	}

	private static void CheckAssignmentLhsRec(Node lhs, CodeWindow f, HashSet<string> vars, HashSet<string> globalVars, HashSet<string> allVars)
	{
		if (lhs is ValueNode)
		{
			ValueNode valueNode = (ValueNode)lhs;
			string value = valueNode.value;
			if (Farm.allKeyWords.Contains(value) || Scope.IsConstant(value))
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_reserved_keyword", value), valueNode.boxedParams.wordStart, valueNode.boxedParams.wordEnd);
			}
			if (double.TryParse(value, NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture, out var _) || value.StartsWith('"') || value.StartsWith('\''))
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_invalid_name", value), valueNode.boxedParams.wordStart, valueNode.boxedParams.wordEnd);
			}
			if (!globalVars.Contains(value))
			{
				vars.Add(value);
			}
			allVars.Add(value);
			return;
		}
		if (lhs is TupleNode || lhs is ListNode)
		{
			foreach (Node slot in lhs.slots[0].slots)
			{
				CheckAssignmentLhsRec(slot, f, vars, globalVars, allVars);
			}
			return;
		}
		if (lhs is BracketNode)
		{
			CheckAssignmentLhsRec(lhs.slots[0], f, vars, globalVars, allVars);
		}
		else if (!(lhs is BinaryExprNode binaryExprNode) || (!(binaryExprNode.op == ".") && (!(binaryExprNode.op == "[]") || binaryExprNode.slots[1].slots.Count != 1)))
		{
			throw new ParseException("error_invalid_assign_expr", lhs.boxedParams.wordStart, lhs.boxedParams.wordEnd);
		}
	}

	private static Node FlowControll(TokenStream stream, CodeWindow f, int indentation, HashSet<string> vars, HashSet<string> globalVars, HashSet<string> allVars, HashSet<string> importedModules, bool isElif = false)
	{
		bool flag = false;
		Token current = stream.Current;
		Node node;
		if (current != null && current.type == TokenType.WHILE)
		{
			Token token = stream.Consume(TokenType.WHILE);
			node = new BranchNode(f, token.startIndex, token.startIndex + token.value.Length, looping: true);
		}
		else
		{
			Token current2 = stream.Current;
			if (current2 != null && current2.type == TokenType.FOR)
			{
				Token token2 = stream.Consume(TokenType.FOR);
				Node node2 = TupleOrExpression(stream, f, canLineBreak: false, TokenType.IN);
				CheckAssignmentLhsRec(node2, f, vars, globalVars, allVars);
				ForNode forNode = new ForNode(node2, f, token2.startIndex, token2.startIndex + token2.value.Length);
				stream.Consume(TokenType.IN, "error_invalid_for_syntax");
				node = forNode;
			}
			else
			{
				Token token3 = stream.Consume(isElif ? TokenType.ELIF : TokenType.IF);
				node = new BranchNode(f, token3.startIndex, token3.startIndex + token3.value.Length);
				flag = true;
			}
		}
		Node item = TupleOrExpression(stream, f);
		Token current3 = stream.Current;
		if (current3 != null && current3.type == TokenType.ASSIGN)
		{
			throw new ParseException("error_unexpected_assign", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
		}
		ConsumeColon(stream);
		Node item2 = Block(stream, f, indentation, vars, globalVars, allVars, importedModules);
		node.slots.Add(item);
		node.slots.Add(item2);
		node.boxedParams.codeWindow = f;
		if (flag)
		{
			Token lookAhead = stream.LookAhead;
			if (lookAhead != null && lookAhead.type == TokenType.ELSE && GetIndentation(stream) == indentation)
			{
				stream.Consume(TokenType.NEW_LINE, "error_new_line_expected");
				stream.Consume(TokenType.ELSE);
				ConsumeColon(stream);
				node.slots.Add(Block(stream, f, indentation, vars, globalVars, allVars, importedModules));
				goto IL_021f;
			}
		}
		if (flag)
		{
			Token lookAhead2 = stream.LookAhead;
			if (lookAhead2 != null && lookAhead2.type == TokenType.ELIF && GetIndentation(stream) == indentation)
			{
				stream.Consume(TokenType.NEW_LINE, "error_new_line_expected");
				node.slots.Add(FlowControll(stream, f, indentation, vars, globalVars, allVars, importedModules, isElif: true));
			}
		}
		goto IL_021f;
		IL_021f:
		return node;
	}

	private static Node Sequence(TokenStream stream, CodeWindow f, TokenType endToken, out bool keyValuePairs, bool allowKeyValuePairs = false, bool lineBreaks = true)
	{
		keyValuePairs = true;
		Node node = new SequenceNode(f);
		if (lineBreaks)
		{
			LineBreaks(stream);
		}
		Token current = stream.Current;
		if (current == null || current.type != endToken)
		{
			Token current2 = stream.Current;
			if ((current2 == null || current2.type != TokenType.NEW_LINE || lineBreaks) && (stream.Current != null || lineBreaks))
			{
				while (true)
				{
					Node item = Expression(stream, f, 0, lineBreaks, endToken);
					if (lineBreaks)
					{
						LineBreaks(stream);
					}
					Token current3 = stream.Current;
					if (current3 != null && current3.type == TokenType.COLON)
					{
						if (!keyValuePairs || !allowKeyValuePairs)
						{
							throw new ParseException("error_invalid_expression", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
						}
						stream.Consume(TokenType.COLON, "error_wrong_dict_literal");
						if (lineBreaks)
						{
							LineBreaks(stream);
						}
						Node item2 = Expression(stream, f, 0, lineBreaks, endToken);
						node.slots.Add(item);
						node.slots.Add(item2);
					}
					else
					{
						if (keyValuePairs && node.slots.Count > 0)
						{
							throw new ParseException("error_invalid_expression", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
						}
						node.slots.Add(item);
						keyValuePairs = false;
					}
					if (lineBreaks)
					{
						LineBreaks(stream);
					}
					Token current4 = stream.Current;
					bool flag = current4 != null && current4.type == TokenType.COMMA;
					if (flag)
					{
						stream.Consume(TokenType.COMMA);
						if (lineBreaks)
						{
							LineBreaks(stream);
						}
					}
					Token current5 = stream.Current;
					int num;
					if (current5 == null || current5.type != endToken)
					{
						Token current6 = stream.Current;
						if (current6 == null || current6.type != TokenType.NEW_LINE || lineBreaks)
						{
							num = ((stream.Current == null && !lineBreaks) ? 1 : 0);
							goto IL_019c;
						}
					}
					num = 1;
					goto IL_019c;
					IL_019c:
					bool flag2 = (byte)num != 0;
					if (flag2)
					{
						break;
					}
					if (!flag && !flag2)
					{
						if (lineBreaks)
						{
							throw new ParseException("error_expected_close_token", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
						}
						throw new ParseException("error_invalid_expression", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
					}
				}
				return node;
			}
		}
		return node;
	}

	private static Node TupleOrExpression(TokenStream stream, CodeWindow f, bool canLineBreak = false, TokenType endOfTupleToken = TokenType.BRACKET_CLOSE, Node startExpr = null, bool isLeftmostExpression = false)
	{
		if (startExpr == null)
		{
			Token current = stream.Current;
			if (current != null && current.type == endOfTupleToken)
			{
				Node item = new SequenceNode(f);
				return new TupleNode(f, stream.CurrentStringStartIndex, stream.CurrentStringStartIndex)
				{
					slots = { item }
				};
			}
		}
		Node node = ((startExpr != null) ? startExpr : Expression(stream, f, 0, canLineBreak, endOfTupleToken, isLeftmostExpression));
		Token current2 = stream.Current;
		if (current2 != null && current2.type == TokenType.COMMA)
		{
			stream.Consume(TokenType.COMMA);
			bool keyValuePairs;
			Node node2 = Sequence(stream, f, endOfTupleToken, out keyValuePairs, allowKeyValuePairs: false, canLineBreak);
			node2.slots.Insert(0, node);
			return new TupleNode(f, stream.CurrentStringStartIndex, stream.CurrentStringStartIndex)
			{
				slots = { node2 }
			};
		}
		return node;
	}

	private static Node Expression(TokenStream stream, CodeWindow f, int opIndex = 0, bool canLineBreak = false, TokenType excludeToken = TokenType.NO_TOKEN, bool isLeftmost = false)
	{
		if (canLineBreak)
		{
			LineBreaks(stream);
		}
		if (opIndex < operators.Count && operators[opIndex].types.Contains(excludeToken))
		{
			opIndex++;
		}
		if (opIndex < operators.Count)
		{
			return operators[opIndex].evaluationFunc(stream, f, opIndex, canLineBreak, excludeToken, isLeftmost);
		}
		return AtomicExpression(stream, f, isLeftmost);
	}

	private static void LineBreaks(TokenStream stream)
	{
		while (true)
		{
			Token current = stream.Current;
			if (current != null && current.type == TokenType.NEW_LINE)
			{
				stream.Consume(TokenType.NEW_LINE);
				continue;
			}
			break;
		}
	}

	public static void OptionalVariableTypeAnnotation(TokenStream stream)
	{
		Token current = stream.Current;
		if (current == null || current.type != TokenType.COLON)
		{
			return;
		}
		Token lookAhead = stream.LookAhead;
		if (lookAhead == null || lookAhead.type != TokenType.STRING)
		{
			Token lookAhead2 = stream.LookAhead;
			if (lookAhead2 == null || lookAhead2.type != TokenType.IDENTIFIER)
			{
				return;
			}
		}
		stream.Consume(TokenType.COLON);
		TypeExpression(stream);
	}

	public static void OptionalReturnTypeAnnotation(TokenStream stream)
	{
		Token current = stream.Current;
		if (current != null && current.type == TokenType.ARROW)
		{
			stream.Consume(TokenType.ARROW);
			TypeExpression(stream);
		}
	}

	public static void OptionalGenericTypeAnnotation(TokenStream stream)
	{
		Token current = stream.Current;
		if (current != null && current.type == TokenType.SQUARE_BRACKET_OPEN)
		{
			TypeExpressionList(stream);
		}
	}

	public static void TypeExpression(TokenStream stream, bool identifierIsOptional = false)
	{
		Token current = stream.Current;
		if (current != null && current.type == TokenType.STRING)
		{
			stream.Consume(TokenType.STRING);
			return;
		}
		if (identifierIsOptional)
		{
			Token current2 = stream.Current;
			if (current2 != null && current2.type == TokenType.IDENTIFIER)
			{
				stream.Consume(TokenType.IDENTIFIER);
			}
		}
		else
		{
			stream.Consume(TokenType.IDENTIFIER);
		}
		Token current3 = stream.Current;
		if (current3 != null && current3.type == TokenType.SQUARE_BRACKET_OPEN)
		{
			TypeExpressionList(stream);
		}
		Token current4 = stream.Current;
		if (current4 != null && current4.type == TokenType.UNION)
		{
			stream.Consume(TokenType.UNION);
			TypeExpression(stream);
		}
	}

	public static void TypeExpressionList(TokenStream stream)
	{
		stream.Consume(TokenType.SQUARE_BRACKET_OPEN);
		Token current = stream.Current;
		if (current != null && current.type == TokenType.BRACKET_OPEN)
		{
			EmptyTuple(stream);
		}
		else
		{
			TypeExpression(stream, identifierIsOptional: true);
			while (true)
			{
				Token current2 = stream.Current;
				if (current2 == null || current2.type != TokenType.COMMA)
				{
					break;
				}
				stream.Consume(TokenType.COMMA);
				Token current3 = stream.Current;
				if (current3 != null && current3.type == TokenType.SQUARE_BRACKET_CLOSE)
				{
					break;
				}
				TypeExpression(stream, identifierIsOptional: true);
			}
		}
		stream.Consume(TokenType.SQUARE_BRACKET_CLOSE);
	}

	private static void EmptyTuple(TokenStream stream)
	{
		stream.Consume(TokenType.BRACKET_OPEN);
		stream.Consume(TokenType.BRACKET_CLOSE);
	}

	private static Node BracketExpression(TokenStream stream, CodeWindow f)
	{
		stream.Consume(TokenType.BRACKET_OPEN);
		Node node = TupleOrExpression(stream, f, canLineBreak: true);
		LineBreaks(stream);
		stream.Consume(TokenType.BRACKET_CLOSE);
		return new BracketNode(f, node.boxedParams.wordStart, node.boxedParams.wordEnd)
		{
			slots = { node }
		};
	}

	private static Node BinaryExpression(TokenStream stream, CodeWindow f, int opIndex, bool canLineBreak, TokenType excludeToken, bool isLeftmost = false)
	{
		if (canLineBreak)
		{
			LineBreaks(stream);
		}
		Node node = Expression(stream, f, opIndex + 1, canLineBreak, excludeToken, isLeftmost);
		if (canLineBreak)
		{
			LineBreaks(stream);
		}
		foreach (TokenType item in operators[opIndex].types)
		{
			Token current2 = stream.Current;
			if (current2 == null || current2.type != item)
			{
				continue;
			}
			if (item == TokenType.COMPARE || item == TokenType.IN)
			{
				List<Node> list = new List<Node> { node };
				List<string> list2 = new List<string>();
				while (true)
				{
					Token current3 = stream.Current;
					if (current3 == null || current3.type != TokenType.COMPARE)
					{
						Token current4 = stream.Current;
						if (current4 == null || current4.type != TokenType.IN)
						{
							break;
						}
					}
					Token token = stream.Consume();
					list.Add(BinaryExpression(stream, f, opIndex + 1, canLineBreak, excludeToken));
					list2.Add(token.value);
				}
				return new ComparisonNode(list2, f, node.boxedParams.wordStart, stream.CurrentStringEndIndex)
				{
					slots = list
				};
			}
			Token token2 = stream.Consume(item);
			Node node2 = BinaryExpression(stream, f, opIndex, canLineBreak, excludeToken);
			Node node3 = new BinaryExprNode(token2.value, token2.type, f, token2.startIndex, token2.startIndex + token2.value.Length);
			node3.slots.Add(node);
			if (!(node2 is BinaryExprNode) || !operators[opIndex].types.Contains(((BinaryExprNode)node2).opTokenType))
			{
				node3.slots.Add(node2);
				return node3;
			}
			Node node4 = node2;
			while (node4.slots[0] is BinaryExprNode && operators[opIndex].types.Contains(((BinaryExprNode)node4.slots[0]).opTokenType))
			{
				node4 = node4.slots[0];
			}
			node3.slots.Add(node4.slots[0]);
			node4.slots[0] = node3;
			return node2;
		}
		return node;
	}

	private static Node UnaryExpression(TokenStream stream, CodeWindow f, int opIndex, bool canLineBreak, TokenType excludeToken, bool isLeftmost = false)
	{
		if (canLineBreak)
		{
			LineBreaks(stream);
		}
		foreach (TokenType item2 in operators[opIndex].types)
		{
			Token current2 = stream.Current;
			if (current2 != null && current2.type == item2)
			{
				Token token = stream.Consume(item2);
				Node item = Expression(stream, f, opIndex, canLineBreak);
				return new UnaryExprNode(token.value, f, token.startIndex, token.startIndex + token.value.Length)
				{
					slots = { item }
				};
			}
		}
		return Expression(stream, f, opIndex + 1, canLineBreak, excludeToken, isLeftmost);
	}

	private static Node IndexDotOrCallExpression(TokenStream stream, CodeWindow f, int opIndex, bool canLineBreak, TokenType excludeToken, bool isLeftmost = false)
	{
		if (canLineBreak)
		{
			LineBreaks(stream);
		}
		Node node = Expression(stream, f, opIndex + 1, canLineBreak, excludeToken, isLeftmost);
		if (canLineBreak)
		{
			LineBreaks(stream);
		}
		while (true)
		{
			Token current = stream.Current;
			if (current == null || current.type != TokenType.SQUARE_BRACKET_OPEN)
			{
				Token current2 = stream.Current;
				if (current2 == null || current2.type != TokenType.BRACKET_OPEN)
				{
					Token current3 = stream.Current;
					if (current3 == null || current3.type != TokenType.DOT)
					{
						break;
					}
				}
			}
			Token current4 = stream.Current;
			if (current4 != null && current4.type == TokenType.SQUARE_BRACKET_OPEN)
			{
				Token token = stream.Consume(TokenType.SQUARE_BRACKET_OPEN);
				Node node2 = new SequenceNode(f);
				node2.slots.Add(SliceIndex(stream, f));
				Token current5 = stream.Current;
				if (current5 != null && current5.type == TokenType.COLON)
				{
					stream.Consume(TokenType.COLON);
					node2.slots.Add(SliceIndex(stream, f, couldBeLastSlice: true));
					Token current6 = stream.Current;
					if (current6 != null && current6.type == TokenType.COLON)
					{
						stream.Consume(TokenType.COLON);
						LineBreaks(stream);
						Token current7 = stream.Current;
						if (current7 == null || current7.type != TokenType.SQUARE_BRACKET_CLOSE)
						{
							node2.slots.Add(Expression(stream, f, 0, canLineBreak: true));
						}
					}
				}
				LineBreaks(stream);
				stream.Consume(TokenType.SQUARE_BRACKET_CLOSE);
				node = new BinaryExprNode("[]", TokenType.BRACKET_OPEN, f, token.startIndex, token.startIndex + token.value.Length)
				{
					slots = { node, node2 }
				};
				continue;
			}
			Token current8 = stream.Current;
			if (current8 != null && current8.type == TokenType.BRACKET_OPEN)
			{
				Token token2 = stream.Consume(TokenType.BRACKET_OPEN);
				bool keyValuePairs;
				Node item = Sequence(stream, f, TokenType.BRACKET_CLOSE, out keyValuePairs);
				stream.Consume(TokenType.BRACKET_CLOSE);
				node = new CallNode(f, token2.startIndex, token2.startIndex + token2.value.Length)
				{
					slots = { node, item }
				};
				continue;
			}
			Token current9 = stream.Current;
			if (current9 == null || current9.type != TokenType.DOT)
			{
				continue;
			}
			Token token3 = stream.Consume(TokenType.DOT);
			Token token4 = stream.Consume(TokenType.IDENTIFIER);
			if (node is LiteralNode { value: PyConstBag value })
			{
				try
				{
					node = new LiteralNode(value.Evaluate(token4.value, node.boxedParams.wordStart, node.boxedParams.wordEnd).val, f, node.boxedParams.wordStart, token4.startIndex + token4.value.Length);
				}
				catch (ExecuteException ex)
				{
					throw new ParseException(ex.Message, ex.startIndex, ex.endIndex);
				}
			}
			else
			{
				Node item2 = new ValueNode(token4.value, f, token4.startIndex, token4.startIndex + token4.value.Length);
				node = new BinaryExprNode(".", TokenType.DOT, f, token3.startIndex, token3.startIndex + token3.value.Length)
				{
					slots = { node, item2 }
				};
			}
		}
		return node;
	}

	private static Node SliceIndex(TokenStream stream, CodeWindow f, bool couldBeLastSlice = false)
	{
		LineBreaks(stream);
		Token current = stream.Current;
		Node node;
		if (current == null || current.type != TokenType.COLON)
		{
			Token current2 = stream.Current;
			if (!(current2 != null && current2.type == TokenType.SQUARE_BRACKET_CLOSE && couldBeLastSlice))
			{
				node = Expression(stream, f, 0, canLineBreak: true);
				Token current3 = stream.Current;
				if (current3 == null || current3.type != TokenType.COLON)
				{
					node = TupleOrExpression(stream, f, canLineBreak: true, TokenType.SQUARE_BRACKET_CLOSE, node);
				}
				goto IL_0089;
			}
		}
		node = new LiteralNode(new PyNone(), f, stream.CurrentStringStartIndex, stream.CurrentStringStartIndex);
		goto IL_0089;
		IL_0089:
		LineBreaks(stream);
		return node;
	}

	private static Node AtomicExpression(TokenStream stream, CodeWindow f, bool canBeTypeAnnotated)
	{
		Token current = stream.Current;
		if (current != null && current.type == TokenType.BRACKET_OPEN)
		{
			return BracketExpression(stream, f);
		}
		Token current2 = stream.Current;
		if (current2 != null && current2.type == TokenType.SQUARE_BRACKET_OPEN)
		{
			int currentStringStartIndex = stream.CurrentStringStartIndex;
			int currentStringEndIndex = stream.CurrentStringEndIndex;
			stream.Consume(TokenType.SQUARE_BRACKET_OPEN);
			bool keyValuePairs;
			Node item = Sequence(stream, f, TokenType.SQUARE_BRACKET_CLOSE, out keyValuePairs);
			stream.Consume(TokenType.SQUARE_BRACKET_CLOSE);
			return new ListNode(f, currentStringStartIndex, currentStringEndIndex)
			{
				slots = { item }
			};
		}
		Token current3 = stream.Current;
		if (current3 != null && current3.type == TokenType.CURL_BRACE_OPEN)
		{
			int currentStringStartIndex2 = stream.CurrentStringStartIndex;
			int currentStringEndIndex2 = stream.CurrentStringEndIndex;
			stream.Consume(TokenType.CURL_BRACE_OPEN);
			bool keyValuePairs2;
			Node item2 = Sequence(stream, f, TokenType.CURL_BRACE_CLOSE, out keyValuePairs2, allowKeyValuePairs: true);
			stream.Consume(TokenType.CURL_BRACE_CLOSE);
			if (keyValuePairs2)
			{
				return new DictNode(f, currentStringStartIndex2, currentStringEndIndex2)
				{
					slots = { item2 }
				};
			}
			return new SetNode(f, currentStringStartIndex2, currentStringEndIndex2)
			{
				slots = { item2 }
			};
		}
		Token current4 = stream.Current;
		if (current4 != null && current4.type == TokenType.NUM)
		{
			Token token = stream.Consume(TokenType.NUM);
			double num;
			try
			{
				num = double.Parse(token.value, NumberStyles.AllowDecimalPoint, CultureInfo.InvariantCulture);
			}
			catch (OverflowException)
			{
				num = double.PositiveInfinity;
			}
			catch (FormatException)
			{
				throw new ParseException("error_invalid_number_format", token.startIndex, token.startIndex + token.value.Length);
			}
			return new LiteralNode(new PyNumber(num), f, token.startIndex, token.startIndex + token.value.Length);
		}
		Token current5 = stream.Current;
		if (current5 != null && current5.type == TokenType.STRING)
		{
			Token token2 = stream.Consume(TokenType.STRING);
			return new LiteralNode(new PyString(token2.value.Substring(1, token2.value.Length - 2)), f, token2.startIndex, token2.startIndex + token2.value.Length);
		}
		Token current6 = stream.Current;
		if (current6 != null && current6.type == TokenType.IDENTIFIER)
		{
			Token token3 = stream.Consume(TokenType.IDENTIFIER);
			if (canBeTypeAnnotated)
			{
				OptionalVariableTypeAnnotation(stream);
			}
			IPyObject pyObject = Scope.EvaluateConstant(token3.value);
			if (pyObject != null)
			{
				return new LiteralNode(pyObject, f, token3.startIndex, token3.startIndex + token3.value.Length);
			}
			return new ValueNode(token3.value, f, token3.startIndex, token3.startIndex + token3.value.Length);
		}
		throw new ParseException("error_invalid_expression", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
	}

	private static void ProcessChainedComparisons(Node tree)
	{
		List<(Node, Node, int)> list = new List<(Node, Node, int)>();
		list.Add((tree, null, 0));
		while (list.Count > 0)
		{
			var (node, node2, _) = list[list.Count - 1];
			list.RemoveAt(list.Count - 1);
			if (node2 != null && node is BinaryExprNode { opTokenType: TokenType.COMPARE } binaryExprNode && binaryExprNode.slots[0] is BinaryExprNode binaryExprNode2)
			{
				_ = binaryExprNode2.opTokenType;
				_ = 26;
			}
		}
	}

	private static int GetIndentation(TokenStream stream)
	{
		Token current = stream.Current;
		if (current == null || current.type != TokenType.NEW_LINE)
		{
			throw new ParseException("error_new_line_expected", stream.CurrentStringStartIndex, stream.CurrentStringEndIndex);
		}
		while (true)
		{
			Token lookAhead = stream.LookAhead;
			if (lookAhead == null || lookAhead.type != TokenType.NEW_LINE)
			{
				break;
			}
			stream.Consume(TokenType.NEW_LINE);
		}
		string value = stream.Current.value;
		if (value.Contains('\t') && value.Contains(' '))
		{
			throw new ParseException("error_mixed_indentation", stream.CurrentStringStartIndex + 1, stream.CurrentStringEndIndex);
		}
		return value.Count((char c) => c == ' ') + value.Count((char c) => c == '\t') * 4;
	}

	private static Token ConsumeColon(TokenStream stream)
	{
		Token current = stream.Current;
		if (current != null && current.type == TokenType.NEW_LINE)
		{
			stream.Consume(TokenType.COLON, "error_missing_colon", moveErrorBack: true);
		}
		return stream.Consume(TokenType.COLON);
	}
}
public class Program
{
	public Node syntaxTree;

	public HashSet<string> globalVars;

	public HashSet<string> allVars;

	public HashSet<string> importedModules = new HashSet<string>();

	public Program(Node syntaxTree, HashSet<string> globalVars, HashSet<string> allVars, HashSet<string> importedModules)
	{
		this.syntaxTree = syntaxTree;
		this.globalVars = globalVars;
		this.allVars = allVars;
		this.importedModules = importedModules;
	}
}
public class ParseException : Exception
{
	public int startIndex;

	public int endIndex;

	public ParseException(string message, int startIndex, int endIndex)
		: base(message)
	{
		this.startIndex = startIndex;
		this.endIndex = endIndex;
	}
}
public class ProgramState
{
	public ModuleState moduleState;

	public int awaitedDroneId = -1;

	public SideEffect currentSideEffect;

	public IPyObject currentSideEffectArgument;

	public object currentSideEffectArgument2;

	public bool hitBreakpoint;

	public bool hitStoppingPoint;

	public ExecuteException currentExecuteException;

	public List<(string, int, int)> currentDependencies = new List<(string, int, int)>();

	public System.Random randomRandom;

	private IEnumerator<double>[] executionStack = new IEnumerator<double>[1101];

	private int executionStackIndex = -1;

	public Scope CurrentScope
	{
		get
		{
			if (moduleState.callStack.Count <= 0)
			{
				return moduleState.globalScope;
			}
			return moduleState.callStack.Peek();
		}
	}

	public IPyObject ReturnValue
	{
		get
		{
			return moduleState.returnValue;
		}
		set
		{
			moduleState.returnValue = value;
		}
	}

	public bool IsExpressionStatic
	{
		get
		{
			return moduleState.isExpressionStatic;
		}
		set
		{
			moduleState.isExpressionStatic = value;
		}
	}

	public Node CurrentExecutingNode
	{
		get
		{
			return moduleState.currentExecutingNode;
		}
		set
		{
			moduleState.currentExecutingNode = value;
		}
	}

	public Deque<(IPyObject data, int droneId)> AllMessagesQueue { get; } = new Deque<(IPyObject, int)>();

	public Deque<IPyObject>[] MessageQueues { get; } = new Deque<IPyObject>[36];

	public Dictionary<string, PyModule> ModuleCache { get; set; } = new Dictionary<string, PyModule>();

	public double OpCount { get; set; }

	public double StartOpCount { get; private set; }

	private double LastConsumedOpCount { get; set; }

	public int DroneId { get; set; } = -1;

	public PyDroneHandle DroneHandle { get; set; }

	public double TargetOpCount { get; set; }

	public ProgramState(double opCount, System.Random random, int droneId)
	{
		moduleState = new ModuleState();
		moduleState.globalScope = new Scope(null, null, null, new HashSet<string>());
		moduleState.globalScope.ImportVar("__name__", new PyString("__main__"));
		StartOpCount = opCount;
		LastConsumedOpCount = opCount;
		OpCount = opCount;
		DroneId = droneId;
		for (int i = 0; i < MessageQueues.Length; i++)
		{
			MessageQueues[i] = new Deque<IPyObject>();
		}
		randomRandom = new System.Random(random.Next());
	}

	public void PushScope(Scope scope)
	{
		moduleState.callStack.Push(scope);
	}

	public void PopScope()
	{
		moduleState.callStack.Pop();
	}

	public void PerformExecutionStep(double targetOpCount, out bool activeDroneExecutedStep)
	{
		activeDroneExecutedStep = false;
		TargetOpCount = targetOpCount;
		if (executionStackIndex < 0)
		{
			currentSideEffect = SideEffect.Terminated;
			return;
		}
		if (awaitedDroneId >= 0)
		{
			OpCount += 1.0;
			LastConsumedOpCount += 1.0;
			return;
		}
		try
		{
			int num = 0;
			while (true)
			{
				if (executionStackIndex >= 0 && !executionStack[executionStackIndex].MoveNext())
				{
					executionStack[executionStackIndex] = null;
					executionStackIndex--;
					continue;
				}
				num++;
				if (executionStackIndex < 0 || !(OpCount <= targetOpCount) || currentSideEffect != SideEffect.None || hitBreakpoint || hitStoppingPoint || num >= 1000)
				{
					break;
				}
			}
			if (hitStoppingPoint || hitBreakpoint)
			{
				hitStoppingPoint = false;
				activeDroneExecutedStep = true;
			}
		}
		catch (Exception ex)
		{
			if (ex is BreakStatement)
			{
				currentExecuteException = new ExecuteException("error_no_loop_to_break");
			}
			else if (ex is ContinueStatement)
			{
				currentExecuteException = new ExecuteException("error_no_loop_to_continue");
			}
			else if (ex is ReturnStatement)
			{
				currentExecuteException = new ExecuteException("error_no_function_to_return_from");
			}
			else if (ex is ExecuteException)
			{
				currentExecuteException = ex as ExecuteException;
			}
			else
			{
				UnityEngine.Debug.LogError($"Unexpected exception during execution: {ex}");
			}
			currentSideEffect = SideEffect.Error;
		}
	}

	public void AddAndConsumeOps(double ops)
	{
		OpCount += ops;
		LastConsumedOpCount += ops;
	}

	public double ConsumeOps()
	{
		double result = OpCount - LastConsumedOpCount;
		LastConsumedOpCount = OpCount;
		return result;
	}

	public void PushOntoExecutionStack(IEnumerable<double> exec)
	{
		if (executionStackIndex >= executionStack.Length - 1)
		{
			Achievements.UnlockAchievement("STACK_OVERFLOW");
			throw new ExecuteException("error_max_stack_size_reached");
		}
		executionStackIndex++;
		executionStack[executionStackIndex] = exec.GetEnumerator();
	}

	public bool EvaluateVarAlongCallstack(string varName, out IPyObject value)
	{
		try
		{
			foreach (Scope item in moduleState.callStack.Concat(new Scope[1] { moduleState.globalScope }))
			{
				if (item.HasVar(varName))
				{
					value = item.Evaluate(varName, "").val;
					return true;
				}
			}
		}
		catch (Exception)
		{
		}
		value = null;
		return false;
	}

	public string GetTrace()
	{
		StringBuilder stringBuilder = new StringBuilder();
		bool flag = true;
		int num = 0;
		foreach (Scope item in moduleState.callStack.Reverse())
		{
			if (flag)
			{
				flag = false;
			}
			else
			{
				stringBuilder.Append(" <- ");
			}
			stringBuilder.Append(item.functionNode.FuncName);
			num++;
			if (num >= 5)
			{
				stringBuilder.Append(" <- ...");
				break;
			}
		}
		stringBuilder.Append('\n');
		AppendLineWithIndicatorAtIndex(moduleState.currentExecutingNode.boxedParams.codeWindow.CodeInput.text, moduleState.currentExecutingNode.boxedParams.wordStart, moduleState.currentExecutingNode.boxedParams.wordEnd, stringBuilder);
		return stringBuilder.ToString();
	}

	public List<(FunctionNode func, Node callNode)> GetCallStack()
	{
		return moduleState.callStack.Select((Scope scope) => (functionNode: scope.functionNode, callNode: scope.callNode)).ToList();
	}

	public static void AppendLineWithIndicatorAtIndex(string text, int index1, int index2, StringBuilder output)
	{
		int num = text.LastIndexOf('\n', index1) + 1;
		int num2 = ((index1 < text.Length - 1) ? text.IndexOf('\n', index1 + 1) : (-1));
		if (num2 < 0)
		{
			num2 = text.Length;
		}
		string text2 = text.Substring(num, num2 - num);
		int num3 = text2.Length - text2.TrimStart(' ', '\t').Length;
		text2 = text2.TrimStart(' ', '\t');
		int num4 = Math.Min(index1, index2) - num - num3;
		int num5 = Math.Max(index1, index2) - num - num3;
		output.AppendLine(text2);
		for (int i = 0; i < num4; i++)
		{
			output.Append(' ');
		}
		for (int j = num4; j <= num5; j++)
		{
			output.Append('^');
		}
		for (int k = num5 + 1; k < text2.Length; k++)
		{
			output.Append(' ');
		}
	}
}
public class Scope
{
	public FunctionNode functionNode;

	public Node callNode;

	private Scope parentScope;

	private Dictionary<string, (IPyObject val, bool isStatic)> vars = new Dictionary<string, (IPyObject, bool)>();

	public Scope(FunctionNode functionNode, Node callNode, Scope parentScope, HashSet<string> variableNames)
	{
		this.functionNode = functionNode;
		this.parentScope = parentScope;
		this.callNode = callNode;
		foreach (string variableName in variableNames)
		{
			vars.Add(variableName, (new PyUnassigned(), false));
		}
	}

	public Scope(FunctionNode functionNode, Node callNode, Scope parentScope, Dictionary<string, (IPyObject val, bool isStatic)> vars)
	{
		this.functionNode = functionNode;
		this.parentScope = parentScope;
		this.callNode = callNode;
		this.vars = vars;
	}

	public void SetVar(string varName, IPyObject value, bool checkShadow = true, bool isStatic = false)
	{
		if (vars.ContainsKey(varName))
		{
			vars[varName] = (value, isStatic);
		}
		else if (parentScope != null)
		{
			parentScope.SetVar(varName, value, checkShadow, isStatic);
		}
		else
		{
			vars[varName] = (value, isStatic);
		}
	}

	public void ImportVar(string varName, IPyObject value, bool isStatic = false)
	{
		vars[varName] = (value, isStatic);
	}

	public bool HasVar(string varName)
	{
		if (vars.ContainsKey(varName))
		{
			return true;
		}
		if (parentScope != null)
		{
			return parentScope.HasVar(varName);
		}
		return false;
	}

	public Scope DeepCopy(Dictionary<object, object> copies)
	{
		if (copies.ContainsKey(this))
		{
			return (Scope)copies[this];
		}
		Scope scope = (Scope)(copies[this] = new Scope(functionNode, callNode, null, new HashSet<string>()));
		scope.parentScope = parentScope?.DeepCopy(copies);
		foreach (KeyValuePair<string, (IPyObject, bool)> var in vars)
		{
			scope.vars.Add(var.Key, (var.Value.Item1.DeepCopy(copies), var.Value.Item2));
		}
		return scope;
	}

	public (IPyObject val, bool isStatic) Evaluate(string s, string currentFileName)
	{
		if (vars.TryGetValue(s, out (IPyObject, bool) value))
		{
			if (value.Item1 is PyUnassigned)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_use_before_assign", s));
			}
			return value;
		}
		if (parentScope != null)
		{
			return parentScope.Evaluate(s, currentFileName);
		}
		foreach (KeyValuePair<string, CodeWindow> codeWindow in MainSim.Inst.workspace.codeWindows)
		{
			if (codeWindow.Value.parsedFunctions.ContainsKey(s))
			{
				if (codeWindow.Key == currentFileName)
				{
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_call_before_def", s, codeWindow.Key));
				}
				if (HasVar(codeWindow.Key) && Evaluate(codeWindow.Key, currentFileName).val is PyModule)
				{
					throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_missing_module_access", s, codeWindow.Key));
				}
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_missing_import", s, codeWindow.Key));
			}
		}
		throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_name_not_defined", s));
	}

	public static IPyObject EvaluateConstant(string s)
	{
		return s switch
		{
			"True" => new PyBool(b: true), 
			"False" => new PyBool(b: false), 
			"None" => new PyNone(), 
			"Items" => new PyConstBag((from i in ResourceManager.GetAllItems()
				where i.enabled
				select i).ToDictionary((Func<ItemSO, string>)((ItemSO i) => i.itemName), (Func<ItemSO, IPyObject>)((ItemSO i) => i)), "Items"), 
			"Entities" => new PyConstBag((from f in ResourceManager.GetAllFarmObjects()
				where !f.isGround
				select f).ToDictionary((Func<FarmObjectSO, string>)((FarmObjectSO i) => i.objectName), (Func<FarmObjectSO, IPyObject>)((FarmObjectSO i) => i)), "Entities"), 
			"Grounds" => new PyConstBag((from f in ResourceManager.GetAllFarmObjects()
				where f.isGround
				select f).ToDictionary((Func<FarmObjectSO, string>)((FarmObjectSO i) => i.objectName), (Func<FarmObjectSO, IPyObject>)((FarmObjectSO i) => i)), "Grounds"), 
			"Unlocks" => new PyConstBag((from u in ResourceManager.GetAllUnlocks()
				where u.enabled
				select u).ToDictionary((Func<UnlockSO, string>)((UnlockSO u) => u.unlockName), (Func<UnlockSO, IPyObject>)((UnlockSO i) => i)), "Unlocks"), 
			"Leaderboards" => new PyConstBag(ResourceManager.GetAllLeaderboards().ToDictionary((Func<LeaderboardSO, string>)((LeaderboardSO u) => u.leaderboardName), (Func<LeaderboardSO, IPyObject>)((LeaderboardSO i) => i)), "Leaderboards"), 
			"Hats" => new PyConstBag((from h in ResourceManager.GetAllHats()
				where !h.hidden
				select h).ToDictionary((Func<HatSO, string>)((HatSO i) => i.hatName), (Func<HatSO, IPyObject>)((HatSO i) => i)), "Hats")
			{
				hiddenElements = (from h in ResourceManager.GetAllHats()
					where h.hidden
					select h).ToDictionary((Func<HatSO, string>)((HatSO i) => i.hatName), (Func<HatSO, IPyObject>)((HatSO i) => i))
			}, 
			"North" => new PyGridDirection(GridDirection.North), 
			"East" => new PyGridDirection(GridDirection.East), 
			"South" => new PyGridDirection(GridDirection.South), 
			"West" => new PyGridDirection(GridDirection.West), 
			_ => null, 
		};
	}

	public static bool IsConstant(string s)
	{
		if (s == "None")
		{
			return true;
		}
		try
		{
			return EvaluateConstant(s) != null;
		}
		catch (ExecuteException)
		{
			return false;
		}
	}

	public static bool IsTrueValue(IPyObject o)
	{
		if (o is PyNone)
		{
			return false;
		}
		if (o is PyNumber)
		{
			return (double)(PyNumber)o != 0.0;
		}
		if (o is IEnumerable)
		{
			return ((IEnumerable)o).GetEnumerator().MoveNext();
		}
		if (o is PyFunction && OptionHolder.GetString("error forgot call") == "enabled")
		{
			PyFunction pyFunction = (PyFunction)o;
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_function_as_condition", pyFunction.functionName));
		}
		return true;
	}
}
public class Tokenizer
{
	private static readonly (string Text, bool needsWordBoundary, TokenType Type)[] constantTokens = new(string, bool, TokenType)[45]
	{
		("if", true, TokenType.IF),
		("else", true, TokenType.ELSE),
		("for", true, TokenType.FOR),
		("or", true, TokenType.OR),
		("and", true, TokenType.AND),
		("return", true, TokenType.RETURN),
		("def", true, TokenType.DEF),
		("while", true, TokenType.WHILE),
		("elif", true, TokenType.ELIF),
		("break", true, TokenType.BREAK),
		("continue", true, TokenType.CONTINUE),
		("pass", true, TokenType.PASS),
		("**", false, TokenType.EXP),
		("==", false, TokenType.COMPARE),
		("=", false, TokenType.ASSIGN),
		("!=", false, TokenType.COMPARE),
		("<=", false, TokenType.COMPARE),
		(">=", false, TokenType.COMPARE),
		("<", false, TokenType.COMPARE),
		(">", false, TokenType.COMPARE),
		("(", false, TokenType.BRACKET_OPEN),
		(")", false, TokenType.BRACKET_CLOSE),
		("+=", false, TokenType.ASSIGN),
		("+", false, TokenType.ADD),
		("-=", false, TokenType.ASSIGN),
		("->", false, TokenType.ARROW),
		("-", false, TokenType.ADD),
		("*=", false, TokenType.ASSIGN),
		("//=", false, TokenType.ASSIGN),
		("//", false, TokenType.MULT),
		("/=", false, TokenType.ASSIGN),
		("%=", false, TokenType.ASSIGN),
		("*", false, TokenType.MULT),
		("/", false, TokenType.MULT),
		("%", false, TokenType.MULT),
		("[", false, TokenType.SQUARE_BRACKET_OPEN),
		("]", false, TokenType.SQUARE_BRACKET_CLOSE),
		("{", false, TokenType.CURL_BRACE_OPEN),
		("}", false, TokenType.CURL_BRACE_CLOSE),
		(",", false, TokenType.COMMA),
		(":", false, TokenType.COLON),
		("|", false, TokenType.UNION),
		("global", true, TokenType.GLOBAL),
		("import", true, TokenType.IMPORT),
		("from", true, TokenType.FROM)
	};

	private static readonly List<(Regex, TokenType)> regexTokens = new List<(Regex, TokenType)>
	{
		(new Regex("\\G(\\d*\\.)?\\d+\\b"), TokenType.NUM),
		(new Regex("\\G(?:in|not\\s+in)\\b"), TokenType.IN),
		(new Regex("\\Gnot\\b"), TokenType.NOT),
		(new Regex("\\G[a-zA-Z_]\\w*"), TokenType.IDENTIFIER),
		(new Regex("\\G(['\"])(.*?)\\1"), TokenType.STRING),
		(new Regex("\\G\\n( |\\t)*"), TokenType.NEW_LINE),
		(new Regex("\\G[\\s-[\\n]]+"), TokenType.IGNORE),
		(new Regex("\\G#.*"), TokenType.IGNORE),
		(new Regex("\\G\\."), TokenType.DOT),
		(new Regex("\\G\\S+"), TokenType.UNKNOWN)
	};

	public static bool Tokenize(string code, out TokenStream stream)
	{
		stream = new TokenStream();
		stream.Add(new Token(TokenType.NEW_LINE, "\n", 0));
		bool flag = false;
		string text = code.Replace("\v", "\n");
		int num = 0;
		while (num < text.Length)
		{
			bool flag2 = false;
			(string, bool, TokenType)[] array = constantTokens;
			for (int i = 0; i < array.Length; i++)
			{
				var (text2, flag3, type) = array[i];
				if (num + text2.Length > text.Length || !text.AsSpan(num, text2.Length).SequenceEqual(text2))
				{
					continue;
				}
				if (flag3 && num + text2.Length < text.Length)
				{
					char c = text[num + text2.Length];
					if (char.IsLetterOrDigit(c) || c == '_')
					{
						continue;
					}
				}
				stream.Add(new Token(type, text2, num));
				num += text2.Length;
				flag2 = true;
				break;
			}
			if (flag2)
			{
				continue;
			}
			foreach (var regexToken in regexTokens)
			{
				Regex item = regexToken.Item1;
				TokenType item2 = regexToken.Item2;
				Match match = item.Match(text, num);
				if (match.Success)
				{
					if (item2 != TokenType.IGNORE)
					{
						stream.Add(new Token(item2, match.Value, num));
					}
					flag = flag || item2 == TokenType.UNKNOWN;
					num += match.Length;
					flag2 = true;
					break;
				}
			}
			if (!flag2)
			{
				throw new Exception("nothing matched, not even UNKNOWN. this should never happen");
			}
		}
		while (true)
		{
			Token last = stream.Last;
			if (last == null || last.type != TokenType.NEW_LINE)
			{
				break;
			}
			stream.RemoveLast();
		}
		return flag;
	}
}
public class TokenStream
{
	private LinkedList<Token> tokens = new LinkedList<Token>();

	private int lastStringIndex;

	public Token Current => tokens.First?.Value;

	public Token LookAhead => tokens.First?.Next?.Value;

	public Token LookAheadIgnoreNewlines
	{
		get
		{
			LinkedListNode<Token> linkedListNode = tokens.First;
			while (linkedListNode != null && linkedListNode.Value?.type == TokenType.NEW_LINE)
			{
				linkedListNode = linkedListNode.Next;
			}
			return linkedListNode?.Next?.Value;
		}
	}

	public Token Last => tokens.Last?.Value;

	public int CurrentStringEndIndex
	{
		get
		{
			if (Current == null)
			{
				return lastStringIndex;
			}
			return Current.startIndex + Current.value.Length;
		}
	}

	public int CurrentStringStartIndex
	{
		get
		{
			if (Current == null)
			{
				return lastStringIndex;
			}
			return Current.startIndex;
		}
	}

	public void Add(Token t)
	{
		tokens.AddLast(t);
		lastStringIndex = t.startIndex + t.value.Length;
	}

	public Token Consume(TokenType type = TokenType.NO_TOKEN, string error = null, bool moveErrorBack = false)
	{
		Token current = Current;
		if (current == null)
		{
			if (error == null)
			{
				throw new ParseException(string.Format(Localizer.Localize("error_unexpected_token"), type), lastStringIndex, lastStringIndex);
			}
			throw new ParseException(error, lastStringIndex, lastStringIndex);
		}
		if (type != TokenType.NO_TOKEN && current.type != type)
		{
			int num = ((current.type == TokenType.NEW_LINE) ? 1 : 0);
			if (error == null)
			{
				throw new ParseException(string.Format(Localizer.Localize("error_unexpected_token"), type), current.startIndex - (moveErrorBack ? 1 : 0) + num, current.startIndex + ((!moveErrorBack) ? current.value.Length : 0));
			}
			throw new ParseException(error, current.startIndex - (moveErrorBack ? 1 : 0) + num, current.startIndex + ((!moveErrorBack) ? current.value.Length : 0));
		}
		tokens.RemoveFirst();
		return current;
	}

	public void RemoveLast()
	{
		if (tokens.Last != null)
		{
			tokens.RemoveLast();
		}
		lastStringIndex = ((Last != null) ? (Last.startIndex + Last.value.Length) : 0);
	}

	public IEnumerator<Token> GetEnumerator()
	{
		return tokens.GetEnumerator();
	}

	public IEnumerable<Token> IterateReverse()
	{
		for (LinkedListNode<Token> node = tokens.Last; node != null; node = node.Previous)
		{
			yield return node.Value;
		}
	}

	public List<Token> ToList()
	{
		return tokens.ToList();
	}

	public override string ToString()
	{
		string text = "";
		using IEnumerator<Token> enumerator = GetEnumerator();
		while (enumerator.MoveNext())
		{
			Token current = enumerator.Current;
			text += $" {current.value} {current.type} |".Replace("\n", "\\n").Replace("\t", "\\t");
		}
		return text;
	}

	public Token GetLastNewLine(int pos)
	{
		LinkedListNode<Token> linkedListNode = TokenNodeAtPos(pos);
		for (linkedListNode = ((linkedListNode != null) ? linkedListNode.Previous : tokens.Last); linkedListNode != null; linkedListNode = linkedListNode.Previous)
		{
			if (linkedListNode.Value.type == TokenType.NEW_LINE)
			{
				return linkedListNode.Value;
			}
		}
		return null;
	}

	public Token GetTokenAtPos(int pos)
	{
		return TokenNodeAtPos(pos).Value;
	}

	private LinkedListNode<Token> TokenNodeAtPos(int pos)
	{
		LinkedListNode<Token> linkedListNode = tokens.First;
		while (linkedListNode != null && linkedListNode.Value.startIndex + linkedListNode.Value.value.Length <= pos)
		{
			linkedListNode = linkedListNode.Next;
		}
		return linkedListNode;
	}
}
public class Token
{
	public TokenType type;

	public string value;

	public int startIndex;

	public Token(TokenType type, string value, int startIndex)
	{
		this.type = type;
		this.value = value;
		this.startIndex = startIndex;
	}
}
public enum TokenType
{
	NO_TOKEN,
	IGNORE,
	NUM,
	IDENTIFIER,
	STRING,
	DEF,
	BRACKET_OPEN,
	BRACKET_CLOSE,
	SQUARE_BRACKET_OPEN,
	SQUARE_BRACKET_CLOSE,
	CURL_BRACE_OPEN,
	CURL_BRACE_CLOSE,
	COMMA,
	COLON,
	DOT,
	NEW_LINE,
	ASSIGN,
	IF,
	ELSE,
	ELIF,
	FOR,
	IN,
	WHILE,
	OR,
	AND,
	NOT,
	COMPARE,
	ADD,
	MULT,
	EXP,
	ARROW,
	UNION,
	PASS,
	RETURN,
	BREAK,
	CONTINUE,
	GLOBAL,
	IMPORT,
	FROM,
	UNKNOWN
}
public static class Saver
{
	private static FileSystemWatcher watcher;

	private static List<(string, string)> codeToUpdate = new List<(string, string)>();

	private static object codeToUpdateLock = new object();

	private const int version = 3;

	public static void Save(MainSim mainSim)
	{
		SaveProgress(mainSim);
		SaveCode(mainSim);
	}

	public static void SaveProgress(MainSim mainSim)
	{
		if (!(mainSim == null))
		{
			bool num = mainSim.MightBeSimulating();
			SaveGame saveGame = new SaveGame();
			if (num)
			{
				saveGame.items = new ItemBlock(mainSim.storedSim.farm.Items);
			}
			else
			{
				saveGame.items = mainSim.GetInventory();
			}
			saveGame.items.Serialize();
			Vector2 farmPos = ((RectTransform)mainSim.workspace.container.GetChild(0)).anchoredPosition;
			Dictionary<string, Window>.ValueCollection values = mainSim.workspace.openWindows.Values;
			saveGame.openFilePositions = values.Select((Window f) => new Pair<string, Vector2>(f.windowName, ((RectTransform)f.transform).anchoredPosition - farmPos)).ToList();
			saveGame.openFileSizes = values.Select((Window f) => new Pair<string, Vector2>(f.windowName, f.playerSetSize)).ToList();
			saveGame.openFileScrollPositions = (from w in values
				where w.TryGetComponent<CodeWindow>(out var _)
				select new Pair<string, float>(w.windowName, ((RectTransform)w.GetComponent<CodeWindow>().CodeInput.transform).anchoredPosition.y)).ToList();
			saveGame.dockedFiles = (from f in values
				where f.dockedParent != null
				select new Pair<string, string>(f.windowName, f.dockedParent.windowName)).ToList();
			saveGame.minimizedFiles = (from f in values
				where f.isMinimized
				select f.windowName).ToList();
			saveGame.openDocPages = (from w in values
				where w.GetComponent<DocsWindow>() != null
				select new Pair<string, string>(w.windowName, w.GetComponent<DocsWindow>().openDoc)).ToList();
			if (num)
			{
				saveGame.unlocks = mainSim.storedSim.farm.SerializeUnlocks();
			}
			else
			{
				saveGame.unlocks = mainSim.GetSerializedUnlocks();
			}
			saveGame.version = 3;
			string text = OptionHolder.GetString("activeSave", "Save0");
			try
			{
				string backupPath = CreateBackupPath(text);
				string pathOfSaveDirectory = GetPathOfSaveDirectory(text);
				WriteSaveGame(saveGame, pathOfSaveDirectory, backupPath);
			}
			catch (IOException ex)
			{
				UnityEngine.Debug.LogError(ex.Message);
				List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
				{
					new WarningPopup.ButtonData("ok", mainSim.warningPopup.Close)
				};
				mainSim.warningPopup.ShowPopup(CodeUtilities.LocalizeAndFormat("popup_warning_failed_write_save", text), buttonsToAdd);
			}
			mainSim.dirty = false;
		}
	}

	public static void SaveCode(MainSim mainSim)
	{
		string text = OptionHolder.GetString("activeSave", "Save0");
		try
		{
			string backupPath = CreateBackupPath(text);
			string pathOfSaveDirectory = GetPathOfSaveDirectory(text);
			WriteCodeFiles(mainSim.workspace, pathOfSaveDirectory, backupPath);
		}
		catch (IOException ex)
		{
			UnityEngine.Debug.LogError(ex.Message);
			List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
			{
				new WarningPopup.ButtonData("ok", mainSim.warningPopup.Close)
			};
			mainSim.warningPopup.ShowPopup(CodeUtilities.LocalizeAndFormat("popup_warning_failed_write_save", text), buttonsToAdd);
		}
	}

	private static void WriteSaveGame(SaveGame sg, string savePath, string backupPath)
	{
		string content = JsonUtility.ToJson(sg);
		FileInfo destinationFile = new FileInfo(savePath + "/save.json");
		WriteFilesSafely(new FileInfo(backupPath + "/save.json"), destinationFile, content);
	}

	private static void WriteCodeFiles(Workspace workspace, string savePath, string backupPath)
	{
		foreach (CodeWindow value in workspace.codeWindows.Values)
		{
			FileInfo destinationFile = new FileInfo($"{savePath}/{value.fileName}.py");
			WriteFilesSafely(new FileInfo($"{backupPath}/{value.fileName}.py"), destinationFile, value.CodeInput.text);
		}
		foreach (string item in from f in Directory.GetFiles(savePath)
			where Path.GetExtension(f) == ".py" && !workspace.openWindows.ContainsKey(Path.GetFileNameWithoutExtension(f)) && !f.EndsWith("__builtins__.py")
			select f)
		{
			try
			{
				File.Delete(item);
			}
			catch (Exception ex)
			{
				UnityEngine.Debug.LogError(ex.Message);
			}
		}
		FileInfo fileInfo = new FileInfo(savePath + "/__builtins__.py");
		if (!fileInfo.Exists)
		{
			string contents = Localizer.LoadBuiltins();
			try
			{
				File.WriteAllText(fileInfo.FullName, contents);
			}
			catch (Exception ex2)
			{
				UnityEngine.Debug.LogError(ex2.Message);
			}
		}
	}

	private static string CreateBackupPath(string fileName)
	{
		string text = Helper.persistentDataPath + "/Backup";
		Directory.CreateDirectory(text);
		List<(int, string)> list = Directory.GetDirectories(text, fileName + "*", SearchOption.TopDirectoryOnly).Select(delegate(string s)
		{
			DirectoryInfo directoryInfo = new DirectoryInfo(s);
			int num7 = fileName.Length + "_backup".Length;
			if (directoryInfo.Name.Length <= num7)
			{
				return (0, "");
			}
			int result;
			return int.TryParse(directoryInfo.Name.Substring(num7), out result) ? (result, s) : (0, "");
		}).ToList();
		list.Sort();
		while (true)
		{
			int num = -1;
			int num2 = int.MaxValue;
			int num3 = int.MaxValue;
			for (int num4 = 1; num4 < list.Count; num4++)
			{
				int num5 = list[num4].Item1 - list[num4 - 1].Item1;
				if (num3 <= num5 && num3 <= num2)
				{
					num = num4 - 2;
					break;
				}
				num3 = num2;
				num2 = num5;
			}
			if (num < 0)
			{
				break;
			}
			try
			{
				Directory.Delete(list[num].Item2, recursive: true);
			}
			catch (Exception)
			{
			}
			list.RemoveAt(num);
		}
		int num6 = ((list.Count > 0) ? (list.Last().Item1 + 1) : 0);
		return $"{text}/{fileName}_backup{num6}";
	}

	private static void WriteFilesSafely(FileInfo backupFile, FileInfo destinationFile, string content)
	{
		backupFile.Directory.Create();
		destinationFile.Directory.Create();
		try
		{
			File.WriteAllText(backupFile.FullName, content);
			File.Copy(backupFile.FullName, destinationFile.FullName, overwrite: true);
		}
		catch (Exception ex)
		{
			UnityEngine.Debug.LogError(ex.Message);
		}
	}

	public static void Load(MainSim mainSim)
	{
		SaveGame currentSaveGame = GetCurrentSaveGame();
		if (currentSaveGame != null)
		{
			currentSaveGame.items.Deserialize();
			mainSim.SetupSim(currentSaveGame.unlocks, new ItemBlock(currentSaveGame.items), null, null, currentSaveGame.version < 3);
			Vector2 anchoredPosition = ((RectTransform)mainSim.workspace.container.GetChild(0)).anchoredPosition;
			DirectoryInfo directoryInfo = new DirectoryInfo(GetPathOfSaveDirectory(OptionHolder.GetString("activeSave", "Save0")));
			directoryInfo.Create();
			IEnumerable<string> source = from f in Directory.GetFiles(directoryInfo.FullName)
				where Path.GetExtension(f) == ".py" && Path.GetFileName(f) != "__builtins__.py"
				select f;
			IEnumerable<string> first = source.Select((string f) => Path.GetFileNameWithoutExtension(f));
			IEnumerable<string> second = source.Select((string f) => File.ReadAllText(f).Replace("\r", ""));
			Dictionary<string, Vector2> dictionary = currentSaveGame.openFilePositions.ToDictionary((Pair<string, Vector2> x) => x.key, (Pair<string, Vector2> x) => x.value);
			Dictionary<string, Vector2> dictionary2 = currentSaveGame.openFileSizes.ToDictionary((Pair<string, Vector2> x) => x.key, (Pair<string, Vector2> x) => x.value);
			foreach (var item in first.Zip(second, (string file, string code) => (file: file, code: code)))
			{
				mainSim.workspace.OpenCodeWindow(item.file, item.code, dictionary.GetValueOrDefault(item.file) + anchoredPosition, dictionary2.GetValueOrDefault(item.file));
			}
			foreach (Pair<string, string> openDocPage in currentSaveGame.openDocPages)
			{
				mainSim.workspace.OpenDocsWindow(openDocPage.key, openDocPage.value, dictionary.GetValueOrDefault(openDocPage.key) + anchoredPosition, dictionary2.GetValueOrDefault(openDocPage.key));
			}
			foreach (Pair<string, float> openFileScrollPosition in currentSaveGame.openFileScrollPositions)
			{
				if (mainSim.workspace.openWindows.TryGetValue(openFileScrollPosition.key, out var value) && value.TryGetComponent<CodeWindow>(out var component))
				{
					((RectTransform)component.CodeInput.transform).anchoredPosition += new Vector2(0f, openFileScrollPosition.value);
				}
			}
			foreach (string minimizedFile in currentSaveGame.minimizedFiles)
			{
				if (mainSim.workspace.openWindows.ContainsKey(minimizedFile))
				{
					mainSim.workspace.openWindows[minimizedFile].SetMinmized(minimized: true);
				}
			}
			for (int num = 0; num < currentSaveGame.dockedFiles.Count; num++)
			{
				if (mainSim.workspace.openWindows.ContainsKey(currentSaveGame.dockedFiles[num].key) && mainSim.workspace.openWindows.ContainsKey(currentSaveGame.dockedFiles[num].value))
				{
					Window component2 = mainSim.workspace.openWindows[currentSaveGame.dockedFiles[num].value].GetComponent<Window>();
					mainSim.workspace.openWindows[currentSaveGame.dockedFiles[num].key].GetComponent<Window>()?.DockOnto(component2);
				}
			}
			if (currentSaveGame.version < 3)
			{
				mainSim.workspace.AddNewDocsWindow("docs/patchnotes.md");
				List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
				{
					new WarningPopup.ButtonData("ok", mainSim.warningPopup.Close)
				};
				mainSim.warningPopup.ShowPopup("popup_warning_old_save", buttonsToAdd);
			}
		}
		else
		{
			mainSim.SetupSim(Enumerable.Empty<string>(), ItemBlock.CreateEmpty());
			mainSim.workspace.OpenCodeWindow("main", "", new Vector2(300f, -150f));
			mainSim.workspace.AddNewDocsWindow("docs/getting_started.md", new Vector2(-300f, 100f));
		}
		mainSim.researchMenu.Setup();
		mainSim.inv.SetUp(mainSim.GetInventory);
		LeanTween.init(1600);
		mainSim.dirty = false;
		StartFileWatcher();
	}

	public static void StartFileWatcher()
	{
		string pathOfSaveDirectory = GetPathOfSaveDirectory(OptionHolder.GetString("activeSave", "Save0"));
		if (!Directory.Exists(pathOfSaveDirectory))
		{
			Directory.CreateDirectory(pathOfSaveDirectory);
		}
		if (watcher != null)
		{
			watcher.Dispose();
		}
		watcher = new FileSystemWatcher(pathOfSaveDirectory);
		watcher.NotifyFilter = watcher.NotifyFilter | NotifyFilters.LastWrite | NotifyFilters.FileName;
		watcher.EnableRaisingEvents = true;
		EnableDisableFileWatcher("file watcher");
		OptionHolder.OnOptionChanged -= EnableDisableFileWatcher;
		OptionHolder.OnOptionChanged += EnableDisableFileWatcher;
	}

	public static void StopFileWatcher()
	{
		if (watcher != null)
		{
			watcher.Dispose();
			watcher = null;
		}
	}

	private static void EnableDisableFileWatcher(string optionName)
	{
		if (optionName == "autosave")
		{
			if (OptionHolder.GetString("autosave") == "enabled" && OptionHolder.GetString("file watcher") == "enabled")
			{
				OptionHolder.SetOption("file watcher", "disabled");
			}
		}
		else
		{
			if (optionName != "file watcher")
			{
				return;
			}
			if (OptionHolder.GetString("file watcher") == "enabled")
			{
				if (OptionHolder.GetString("autosave") == "enabled")
				{
					OptionHolder.SetOption("autosave", "disabled");
				}
				watcher.Changed -= OnFileChanged;
				watcher.Changed += OnFileChanged;
			}
			else
			{
				watcher.Changed -= OnFileChanged;
			}
		}
	}

	private static void OnFileChanged(object sender, FileSystemEventArgs e)
	{
		if (!e.Name.EndsWith(".py"))
		{
			return;
		}
		string item = e.Name.Substring(0, e.Name.Length - 3);
		lock (codeToUpdateLock)
		{
			codeToUpdate.Add((item, File.ReadAllText(e.FullPath)));
		}
	}

	public static void ApplyCodeChanges(Workspace workspace)
	{
		if (codeToUpdate.Count <= 0)
		{
			return;
		}
		lock (codeToUpdateLock)
		{
			foreach (var item in codeToUpdate)
			{
				if (workspace.codeWindows.TryGetValue(item.Item1, out var value))
				{
					value.CodeInput.text = item.Item2;
				}
			}
			codeToUpdate.Clear();
		}
	}

	public static void UpdateFromOldSaveGame(OldSaveGame oldSaveGame)
	{
		string text = OptionHolder.GetString("activeSave", "Save0");
		SaveGame saveGame = new SaveGame();
		saveGame.unlocks = oldSaveGame.unlocks;
		saveGame.items = oldSaveGame.items;
		saveGame.openDocPages = new List<Pair<string, string>>();
		saveGame.minimizedFiles = oldSaveGame.minimized;
		saveGame.openFilePositions = new List<Pair<string, Vector2>>();
		saveGame.openFileSizes = new List<Pair<string, Vector2>>();
		saveGame.dockedFiles = new List<Pair<string, string>>();
		for (int i = 0; i < oldSaveGame.functionNames.Count; i++)
		{
			FileInfo fileInfo = new FileInfo(Helper.persistentDataPath + $"/Saves/{text}/{oldSaveGame.functionNames[i]}.py");
			fileInfo.Directory.Create();
			File.WriteAllText(fileInfo.FullName, oldSaveGame.functionCode[i]);
			saveGame.openFilePositions.Add(new Pair<string, Vector2>(oldSaveGame.functionNames[i], oldSaveGame.openFunctionPositions[i]));
			if (i < oldSaveGame.functionDocked.Count && oldSaveGame.functionDocked[i] != "")
			{
				saveGame.dockedFiles.Add(new Pair<string, string>(oldSaveGame.functionNames[i], oldSaveGame.functionDocked[i]));
			}
		}
		_ = Helper.persistentDataPath + "/Backup";
		WriteSaveGame(saveGame, GetPathOfSaveDirectory(text), CreateBackupPath(text));
	}

	private static SaveGame GetCurrentSaveGame()
	{
		string currentSaveGameJson = GetCurrentSaveGameJson();
		if (!string.IsNullOrEmpty(currentSaveGameJson))
		{
			SaveGame saveGame = JsonUtility.FromJson<SaveGame>(currentSaveGameJson);
			if (saveGame.openFilePositions.Count > 0)
			{
				return saveGame;
			}
			OldSaveGame oldSaveGame = JsonUtility.FromJson<OldSaveGame>(currentSaveGameJson);
			if (oldSaveGame.functionNames.Count > 0)
			{
				UpdateFromOldSaveGame(oldSaveGame);
				currentSaveGameJson = GetCurrentSaveGameJson();
				return JsonUtility.FromJson<SaveGame>(currentSaveGameJson);
			}
			if (saveGame.unlocks.Count > 0 || !saveGame.items.IsEmpty())
			{
				return saveGame;
			}
			return null;
		}
		return null;
	}

	private static string GetCurrentSaveGameJson()
	{
		string saveName = OptionHolder.GetString("activeSave", "Save0");
		FileInfo fileInfo = new FileInfo(GetPathOfSaveFile(saveName));
		if (!File.Exists(fileInfo.FullName))
		{
			CreateNewSaveGame(saveName);
		}
		return File.ReadAllText(fileInfo.FullName);
	}

	public static bool RenameSave(string saveName, string newSaveName)
	{
		if (string.IsNullOrEmpty(newSaveName) || newSaveName.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 || Directory.Exists(GetPathOfSaveDirectory(newSaveName)))
		{
			return false;
		}
		try
		{
			Directory.Move(GetPathOfSaveDirectory(saveName), GetPathOfSaveDirectory(newSaveName));
		}
		catch (Exception)
		{
			return false;
		}
		return true;
	}

	public static bool DeleteSave(string saveName)
	{
		try
		{
			Directory.Delete(GetPathOfSaveDirectory(saveName), recursive: true);
		}
		catch (Exception)
		{
			return false;
		}
		return true;
	}

	public static void CreateNewSaveGame(string saveName)
	{
		FileInfo fileInfo = new FileInfo(GetPathOfSaveFile(saveName));
		if (!fileInfo.Exists)
		{
			Directory.CreateDirectory(fileInfo.Directory.FullName);
		}
		File.Create(fileInfo.FullName).Dispose();
		new DirectoryInfo(GetPathOfSaveDirectory(saveName)).Create();
	}

	public static string GetPathOfSaveFile(string saveName)
	{
		string text = $"{Helper.persistentDataPath}/Saves/{saveName}/save.json";
		if (!File.Exists(text))
		{
			text = $"{Helper.persistentDataPath}/Saves/{saveName}.json";
		}
		return text;
	}

	public static string GetPathOfSaveDirectory(string saveName)
	{
		return $"{Helper.persistentDataPath}/Saves/{saveName}";
	}
}
[Serializable]
public class OldSaveGame
{
	public ItemBlock items;

	public List<string> functionNames;

	public List<string> functionCode;

	public List<string> functionDocked;

	public List<string> minimized;

	public List<Vector2> openFunctionPositions;

	public Vector2 docsPos;

	public string openDocsPage;

	public List<string> unlocks;

	public List<SFO> grounds;

	public List<SFO> entities;
}
[Serializable]
public class SaveGame
{
	public ItemBlock items;

	public List<Pair<string, string>> dockedFiles;

	public List<string> minimizedFiles;

	public List<Pair<string, Vector2>> openFilePositions;

	public List<Pair<string, float>> openFileScrollPositions;

	public List<Pair<string, Vector2>> openFileSizes;

	public List<Pair<string, string>> openDocPages;

	public List<string> unlocks;

	public int version;
}
[Serializable]
public struct SFO
{
	public Vector2Int pos;

	public string data;

	public SFO(Vector2Int pos, string data)
	{
		this.pos = pos;
		this.data = data;
	}
}
[Serializable]
public struct Pair<T1, T2>
{
	public T1 key;

	public T2 value;

	public Pair(T1 key, T2 value)
	{
		this.key = key;
		this.value = value;
	}
}
public class SteamScript : MonoBehaviour
{
	private CallResult<NumberOfCurrentPlayers_t> m_NumberOfCurrentPlayers;

	private void OnEnable()
	{
		if (SteamManager.Initialized)
		{
			m_NumberOfCurrentPlayers = CallResult<NumberOfCurrentPlayers_t>.Create(OnNumberOfCurrentPlayers);
		}
	}

	private void Update()
	{
		if (Input.GetKeyDown(KeyCode.Space))
		{
			SteamAPICall_t numberOfCurrentPlayers = SteamUserStats.GetNumberOfCurrentPlayers();
			m_NumberOfCurrentPlayers.Set(numberOfCurrentPlayers);
			UnityEngine.Debug.Log("Called GetNumberOfCurrentPlayers()");
		}
	}

	private void OnNumberOfCurrentPlayers(NumberOfCurrentPlayers_t pCallback, bool bIOFailure)
	{
		if (pCallback.m_bSuccess != 1 || bIOFailure)
		{
			UnityEngine.Debug.Log("There was an error retrieving the NumberOfCurrentPlayers.");
		}
		else
		{
			UnityEngine.Debug.Log("The number of players playing your game: " + pCallback.m_cPlayers);
		}
	}
}
public class SteamStatsLoop : MonoBehaviour
{
	private float statsTime;

	private float richTextTime;

	private void Update()
	{
		if (Time.time - statsTime > 1f)
		{
			statsTime = Time.time;
			if (SteamManager.Initialized)
			{
				SteamUserStats.StoreStats();
			}
		}
		if (Time.time - richTextTime > 60f && Achievements.RichPresenceDisplay != null)
		{
			richTextTime = Time.time;
			if (SteamManager.Initialized)
			{
				SteamFriends.SetRichPresence("steam_display", Achievements.RichPresenceDisplay);
				Achievements.RichPresenceDisplay = null;
				SteamFriends.SetRichPresence("quantity", Achievements.RichPresenceQuantity);
				Achievements.RichPresenceQuantity = null;
			}
		}
	}
}
public class BlinkManager : MonoBehaviour
{
	[SerializeField]
	private float blinkTime;

	[SerializeField]
	private float strength;

	[SerializeField]
	private float fullLineAlpha;

	[SerializeField]
	private float vmargin;

	[SerializeField]
	private float hmargin;

	[SerializeField]
	private float horizontalOffset;

	[SerializeField]
	private float height;

	[SerializeField]
	private CameraController cameraController;

	[SerializeField]
	private Canvas canvas;

	private object blinkLock = new object();

	private Dictionary<Node, float> rects = new Dictionary<Node, float>();

	private Node currentNode;

	private Texture2D texture;

	private float prevTime;

	private HashSet<FunctionNode> visitedFunctions = new HashSet<FunctionNode>();

	private void Awake()
	{
		texture = new Texture2D(1, 1);
		texture.SetPixel(0, 0, Color.white);
		texture.Apply();
	}

	private void OnGUI()
	{
		float num = Time.time - prevTime;
		prevTime = Time.time;
		if (MainSim.Inst.researchMenu.IsOpen || OptionHolder.GetString("code highlights", "enabled") == "disabled")
		{
			return;
		}
		bool stepByStepMode = MainSim.Inst.StepByStepMode;
		RectTransform container = MainSim.Inst.workspace.container;
		RectTransform topWindowRect = null;
		CodeWindow component2;
		if (container.childCount > 0 && container.GetChild(container.childCount - 1).TryGetComponent<DocsWindow>(out var component))
		{
			topWindowRect = component.GetComponent<RectTransform>();
		}
		else if (container.childCount > 0 && container.GetChild(container.childCount - 1).TryGetComponent<CodeWindow>(out component2))
		{
			topWindowRect = component2.GetComponent<RectTransform>();
		}
		ColorTheme theme = ThemeManager.Inst.Theme;
		lock (blinkLock)
		{
			foreach (var (node2, num3) in rects.ToList())
			{
				if (node2.blink && !node2.boxedParams.codeWindow.GetComponent<Window>().isMinimized)
				{
					float alpha = Mathf.Pow(num3 / blinkTime * strength, 2f);
					GUI.color = theme.code.ExecOverlayColor.MultiplyAlpha(alpha);
					Rect worldWordRect = GetWorldWordRect(node2.boxedParams.wordStart, node2.boxedParams.wordEnd, node2.boxedParams.codeWindow, topWindowRect);
					if (worldWordRect.height > 0f && worldWordRect.width > 0f)
					{
						GUI.DrawTexture(worldWordRect, texture, ScaleMode.StretchToFill);
					}
				}
				if (num3 <= num)
				{
					rects.Remove(node2);
				}
				else
				{
					rects[node2] = num3 - num;
				}
			}
			if (stepByStepMode && currentNode != null && !currentNode.boxedParams.codeWindow.GetComponent<Window>().isMinimized)
			{
				GUI.color = theme.code.ExecOverlayColor.MultiplyAlpha(fullLineAlpha);
				Rect worldLineRect = GetWorldLineRect(currentNode.boxedParams.wordStart, currentNode.boxedParams.codeWindow, topWindowRect);
				if (worldLineRect.height > 0f && worldLineRect.width > 0f)
				{
					GUI.DrawTexture(worldLineRect, texture, ScaleMode.StretchToFill);
				}
			}
		}
		List<(FunctionNode, Node)> callStack = MainSim.Inst.GetCallStack();
		if (callStack == null)
		{
			return;
		}
		for (int i = 0; i < callStack.Count; i++)
		{
			FunctionNode item = ((i == callStack.Count - 1) ? null : callStack[i + 1].Item1);
			Node item2 = callStack[i].Item2;
			if (item2 == null || visitedFunctions.Contains(item))
			{
				continue;
			}
			visitedFunctions.Add(item);
			if (!item2.boxedParams.codeWindow.GetComponent<Window>().isMinimized)
			{
				GUI.color = theme.code.ExecOverlayColor.MultiplyAlpha(fullLineAlpha);
				Rect worldLineRect2 = GetWorldLineRect(item2.boxedParams.wordStart, item2.boxedParams.codeWindow, topWindowRect);
				if (worldLineRect2.height > 0f && worldLineRect2.width > 0f)
				{
					GUI.DrawTexture(worldLineRect2, texture, ScaleMode.StretchToFill);
				}
			}
		}
		visitedFunctions.Clear();
	}

	public void EnqueueBlink(Node n)
	{
		lock (blinkLock)
		{
			if (rects.Count < 1000)
			{
				rects[n] = blinkTime;
				currentNode = n;
			}
		}
	}

	private Rect GetWorldWordRect(int start, int end, CodeWindow codeWindow, RectTransform topWindowRect)
	{
		TMP_CharacterInfo[] characterInfo = codeWindow.CodeInput.textComponent.textInfo.characterInfo;
		Vector3 startLocal = (characterInfo[start].bottomLeft + characterInfo[start].bottomRight) * 0.5f;
		Vector3 endLocal = (characterInfo[end - 1].bottomLeft + characterInfo[end - 1].bottomRight) * 0.5f;
		return GetWorldRect(startLocal, endLocal, height, codeWindow, topWindowRect);
	}

	private Rect GetWorldLineRect(int stringIndex, CodeWindow codeWindow, RectTransform topWindowRect)
	{
		TMP_CharacterInfo[] characterInfo = codeWindow.CodeInput.textComponent.textInfo.characterInfo;
		int lineNumber = characterInfo[stringIndex].lineNumber;
		TMP_LineInfo tMP_LineInfo = codeWindow.CodeInput.textComponent.textInfo.lineInfo[lineNumber];
		Vector3 bottomLeft = characterInfo[tMP_LineInfo.firstCharacterIndex].bottomLeft;
		Vector3 bottomRight = characterInfo[tMP_LineInfo.lastCharacterIndex].bottomRight;
		return GetWorldRect(bottomLeft, bottomRight, height, codeWindow, topWindowRect);
	}

	private Rect GetWorldRect(Vector3 startLocal, Vector3 endLocal, float height, CodeWindow codeWindow, RectTransform topWindowRect)
	{
		RectTransform component = codeWindow.CodeInput.GetComponent<RectTransform>();
		Vector3 vector = GetCodeOffset(component);
		Vector2 vector2 = startLocal * canvas.scaleFactor * cameraController.zoom + component.position + vector;
		Vector2 vector3 = endLocal * canvas.scaleFactor * cameraController.zoom + component.position + vector;
		Vector2 vector4 = vector2 - new Vector2(hmargin, vmargin) * canvas.scaleFactor * cameraController.zoom;
		Vector2 vector5 = vector3 + new Vector2(hmargin, height + vmargin) * canvas.scaleFactor * cameraController.zoom;
		vector4.x += horizontalOffset * canvas.scaleFactor * cameraController.zoom;
		vector5.x += horizontalOffset * canvas.scaleFactor * cameraController.zoom;
		vector4.y = (float)Screen.height - vector4.y;
		vector5.y = (float)Screen.height - vector5.y;
		Rect screenRect = GetScreenRect(codeWindow.scrollViewRect);
		Rect rect = new Rect(vector4, vector5 - vector4);
		rect.height = Mathf.Abs(rect.height);
		rect.y -= rect.height;
		Rect rect2 = Rect.MinMaxRect(Mathf.Max(screenRect.xMin, rect.xMin), Mathf.Max(screenRect.yMin, rect.yMin), Mathf.Min(screenRect.xMax, rect.xMax), Mathf.Min(screenRect.yMax, rect.yMax));
		if (topWindowRect != null && codeWindow != topWindowRect.GetComponent<CodeWindow>())
		{
			Rect screenRect2 = GetScreenRect(topWindowRect);
			MaskOutRect(ref rect2, screenRect2);
		}
		RectTransform component2 = MainSim.Inst.workspace.tooltip.Container.GetComponent<RectTransform>();
		if (component2.localScale != Vector3.zero)
		{
			Rect screenRect3 = GetScreenRect(component2);
			MaskOutRect(ref rect2, screenRect3);
		}
		return rect2;
	}

	private void MaskOutRect(ref Rect rect, Rect mask)
	{
		if (rect.yMin < mask.yMax && rect.yMax > mask.yMin)
		{
			if (rect.xMin < mask.xMin)
			{
				rect.xMax = Mathf.Clamp(mask.xMin, rect.xMin, rect.xMax);
			}
			else
			{
				rect.xMin = Mathf.Clamp(mask.xMax, rect.xMin, rect.xMax);
			}
		}
	}

	private static Rect GetScreenRect(RectTransform rectTransform)
	{
		Vector3[] array = new Vector3[4];
		rectTransform.GetWorldCorners(array);
		array[3].y = (float)Screen.height - array[3].y;
		array[1].y = (float)Screen.height - array[1].y;
		return new Rect(array[1], array[3] - array[1]);
	}

	public static Vector2 GetCodeOffset(RectTransform inputFieldRect)
	{
		Vector3[] array = new Vector3[4];
		inputFieldRect.GetWorldCorners(array);
		return (array[3] - array[0]) * 0.5f + (array[0] - array[1]) * 0.5f;
	}
}
public class BreakPointPanel : MonoBehaviour, IPointerDownHandler, IEventSystemHandler
{
	[SerializeField]
	private CodeWindow function;

	[SerializeField]
	private float topMargin;

	[SerializeField]
	private float bottomMargin;

	[SerializeField]
	private RawImage borderLine;

	[SerializeField]
	private GameObject breakpointPrefab;

	private List<int> breakpointLines = new List<int>();

	private Dictionary<int, GameObject> breakpoints = new Dictionary<int, GameObject>();

	private int prevLineCount;

	private volatile Node syntaxTree;

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void Start()
	{
		function.CodeInput.onValueChanged.AddListener(UpdatePanel);
		UpdatePanel(function.CodeInput.text);
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		borderLine.color = theme.code.BreakpointLineColor;
		foreach (GameObject value in breakpoints.Values)
		{
			if (value.TryGetComponent<Image>(out var component))
			{
				component.color = theme.code.BreakpointColor;
			}
		}
	}

	private void UpdatePanel(string value)
	{
		if (breakpointLines.Count == 0)
		{
			return;
		}
		if (value.Count((char c) => c == '\n') + 1 != prevLineCount)
		{
			foreach (int breakpointLine in breakpointLines)
			{
				UnityEngine.Object.Destroy(breakpoints[breakpointLine]);
			}
			breakpointLines.Clear();
			breakpoints.Clear();
		}
		_ = prevLineCount;
	}

	public void OnPointerDown(PointerEventData eventData)
	{
		if (!MainSim.Inst.IsUnlocked("debug"))
		{
			return;
		}
		int num = function.CodeInput.text.Count((char c) => c == '\n') + 1;
		RectTransform rect = (RectTransform)base.transform;
		float preferredHeight = function.CodeInput.textComponent.preferredHeight;
		float num2 = preferredHeight / (float)num;
		RectTransformUtility.ScreenPointToLocalPointInRectangle(rect, eventData.position, eventData.pressEventCamera, out var localPoint);
		int num3 = Mathf.FloorToInt((0f - localPoint.y - topMargin) / preferredHeight * (float)num);
		if (num3 < 0 || num3 >= num)
		{
			return;
		}
		if (breakpointLines.Contains(num3))
		{
			breakpointLines.Remove(num3);
			UnityEngine.Object.Destroy(breakpoints[num3]);
			breakpoints.Remove(num3);
		}
		else
		{
			GameObject gameObject = UnityEngine.Object.Instantiate(breakpointPrefab, base.transform);
			RectTransform obj = (RectTransform)gameObject.transform;
			float y = (0f - num2) * (float)num3 - 0.5f * num2 - topMargin;
			obj.anchoredPosition += new Vector2(0f, y);
			if (gameObject.TryGetComponent<Image>(out var component))
			{
				component.color = ThemeManager.Inst.Theme.code.BreakpointColor;
			}
			breakpointLines.Add(num3);
			breakpointLines.Sort();
			breakpoints[num3] = gameObject;
		}
		UpdateBreakpoints(syntaxTree);
	}

	public void UpdateBreakpoints(Node syntaxTree)
	{
		this.syntaxTree = syntaxTree;
		TMP_LineInfo[] lineInfos = function.CodeInput.textComponent.textInfo.lineInfo;
		syntaxTree?.InsertBreakpointsRec(breakpointLines.Select((int i) => lineInfos[i].firstCharacterIndex).ToHashSet());
	}
}
public class CodeCompleter : MonoBehaviour
{
	[SerializeField]
	private RectTransform container;

	[SerializeField]
	private CodeOption optionPrefab;

	[SerializeField]
	private Canvas editorCanvas;

	private List<CodeOption> options = new List<CodeOption>();

	private List<string> optionStrings;

	private int selected;

	private string compareString;

	public int startStringIndex;

	private CodeWindow func;

	public bool IsOpen => base.gameObject.activeInHierarchy;

	public string Selection => options[selected].text.text;

	public bool IsMatch
	{
		get
		{
			int num = 0;
			string selection = Selection;
			foreach (char c in selection)
			{
				if (num >= compareString.Length)
				{
					return true;
				}
				if (char.ToLower(c) == char.ToLower(compareString[num]))
				{
					num++;
				}
			}
			return false;
		}
	}

	public int TypedLength => compareString.Length;

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		if (TryGetComponent<Image>(out var component))
		{
			component.color = theme.code.CompleteBackgroundColor;
		}
	}

	private void Update()
	{
		if (Input.GetKeyDown(KeyCode.DownArrow))
		{
			if (options.Count > selected + 1)
			{
				SelectOption(selected + 1);
			}
		}
		else if (Input.GetKeyDown(KeyCode.UpArrow))
		{
			if (selected > 0)
			{
				SelectOption(selected - 1);
			}
		}
		else if (Input.GetKeyDown(KeyCode.LeftArrow) || Input.GetKeyDown(KeyCode.RightArrow))
		{
			Close();
		}
	}

	public void SelectOption(int index)
	{
		if (options.Count != 0)
		{
			options[selected].Unhighlight();
			selected = index;
			options[index].Highlight();
			float y = ((RectTransform)options[selected].transform).anchoredPosition.y;
			float num = GetComponent<RectTransform>().sizeDelta.y / 2f;
			float y2 = container.sizeDelta.y;
			container.anchoredPosition = new Vector2(0f, Mathf.Clamp(0f - y - num, 0f, y2 - 2f * num));
		}
	}

	public void Commit()
	{
		func.CompleteWord(removeExtraChar: false);
		func.CodeInput.Select();
		Close();
	}

	public void UpdateString(char addition)
	{
		compareString += addition;
		UpdateOptions();
	}

	public void Backspace()
	{
		if (compareString.Length > 0)
		{
			compareString = compareString.Remove(compareString.Length - 1);
			UpdateOptions();
		}
	}

	public void Scroll(float scroll)
	{
		container.anchoredPosition += new Vector2(0f, (0f - scroll) * 100f);
	}

	public void Open(Vector3 pos, List<string> optionStrings, string compareString, int startStringIndex, CodeWindow func)
	{
		if (optionStrings.Count != 0)
		{
			base.gameObject.SetActive(value: true);
			RectTransform rectTransform = (RectTransform)base.transform;
			rectTransform.position = pos;
			rectTransform.anchoredPosition += new Vector2(rectTransform.rect.size.x, 0f - rectTransform.rect.size.y) / 2f;
			this.compareString = compareString;
			this.optionStrings = optionStrings;
			this.startStringIndex = startStringIndex;
			this.func = func;
			func.CodeInput.blockArrowKeys = true;
			UpdateOptions();
		}
	}

	public void Close()
	{
		base.gameObject.SetActive(value: false);
		func.CodeInput.blockArrowKeys = false;
	}

	public TooltipInfo GetCompletionTooltip(int optionIndex)
	{
		return TooltipUtils.GetWordTooltip(optionStrings[optionIndex], func);
	}

	private void UpdateOptions()
	{
		optionStrings = optionStrings.OrderByDescending((string s) => CompareScore(s)).ToList();
		int num = 0;
		foreach (CodeOption option in options)
		{
			if (num < optionStrings.Count)
			{
				option.text.text = optionStrings[num];
				option.Unhighlight();
				option.gameObject.SetActive(value: true);
			}
			else
			{
				option.gameObject.SetActive(value: false);
			}
			num++;
		}
		for (; num < optionStrings.Count; num++)
		{
			options.Add(UnityEngine.Object.Instantiate(optionPrefab, container));
			options[options.Count - 1].SetUp(options.Count - 1, this);
			options[options.Count - 1].text.text = optionStrings[num];
		}
		SelectOption(0);
	}

	private float CompareScore(string s)
	{
		int num = 0;
		int num2 = 0;
		float num3 = 0f;
		foreach (char c in s)
		{
			if (num >= compareString.Length)
			{
				break;
			}
			if (c == compareString[num])
			{
				num++;
				num3 += (float)(1 / (1 << num2));
			}
			else if (char.ToLower(c) == char.ToLower(compareString[num]))
			{
				num++;
				num3 += 0.5f / (float)(1 << num2);
			}
			else
			{
				num2++;
			}
		}
		if (num == s.Length)
		{
			num3 += 1f;
		}
		return num3;
	}
}
public class CodeOption : MonoBehaviour, IPointerClickHandler, IEventSystemHandler, ITooltipHandler
{
	private int index;

	private CodeCompleter completer;

	public TextMeshProUGUI text;

	[SerializeField]
	private Image highlightImage;

	[SerializeField]
	private Transform tooltipPosition;

	public void SetUp(int index, CodeCompleter completer)
	{
		this.index = index;
		this.completer = completer;
		Unhighlight();
	}

	public void OnPointerClick(PointerEventData eventData)
	{
		completer.SelectOption(index);
		completer.Commit();
	}

	public void Highlight()
	{
		ColorTheme theme = ThemeManager.Inst.Theme;
		highlightImage.color = theme.code.CompleteSelectedBackgroundColor;
		text.color = theme.code.CompleteSelectedTextColor;
	}

	public void Unhighlight()
	{
		ColorTheme theme = ThemeManager.Inst.Theme;
		highlightImage.color = Color.clear;
		text.color = theme.code.CompleteTextColor;
	}

	public TooltipInfo GetTooltipInfo(Action updateTooltipCallback)
	{
		TooltipInfo completionTooltip = completer.GetCompletionTooltip(index);
		if (completionTooltip != null)
		{
			completionTooltip.delay = 0.2f;
			completionTooltip.fixedPosition = tooltipPosition.position;
			completionTooltip.anchor = TooltipInfo.Anchor.BottomRight;
		}
		return completionTooltip;
	}

	public void TooltipGone()
	{
	}
}
public class CodeWindow : MonoBehaviour, ITooltipHandler
{
	[SerializeField]
	private float minWidth;

	[SerializeField]
	private float scrollingStartSize;

	[SerializeField]
	private Vector2 extraSize;

	private const float colorFadeDuration = 0.2f;

	private float fadeStartTime = -1f;

	private bool isFading;

	[SerializeField]
	private Image windowBackground;

	[SerializeField]
	private ScrollRect scrollView;

	public RectTransform scrollViewRect;

	[SerializeField]
	private CodeInputField codeInput;

	[SerializeField]
	private BreakPointPanel breakpointPanel;

	[SerializeField]
	private TextMeshProUGUI codeText;

	[SerializeField]
	private TMP_InputField fileNameText;

	[SerializeField]
	private ColoredButton executeButton;

	[SerializeField]
	private ColoredButton stepByStepButton;

	[SerializeField]
	private Image executeImg;

	[SerializeField]
	private Image stepByStepImg;

	[SerializeField]
	private Sprite executeSprite;

	[SerializeField]
	private Sprite stopSprite;

	[SerializeField]
	private Sprite stepByStepSprite;

	[SerializeField]
	private Sprite pauseSprite;

	[SerializeField]
	private ErrorMessage errorMessage;

	[SerializeField]
	private Color errorColor;

	public Workspace workspace;

	public bool isExecuting;

	public TokenStream tokens;

	public string fileName;

	private volatile string errorString;

	private volatile int errorStartIndex;

	private volatile int errorEndIndex;

	public ConcurrentDictionary<string, FunctionNode> parsedFunctions = new ConcurrentDictionary<string, FunctionNode>();

	public HashSet<string> tokenizedIdentifiers = new HashSet<string>();

	private volatile Program cachedProgram;

	private volatile bool dirty = true;

	private volatile ParseException parseException;

	private object parseLock = new object();

	private string undoState = "";

	private float undoChangeTime;

	private bool undoPreventNextChange;

	private int prevSelectionStart;

	private int prevSelectionEnd;

	private string prevText;

	private Action tooltipUpdateCallback;

	private int hoverWordStart;

	private int hoverWordEnd;

	private int updateSizeInXFrames;

	public CodeInputField CodeInput => codeInput;

	public CodeWindow DockedParent => GetComponent<Window>().dockedParent?.GetComponent<CodeWindow>();

	public CodeWindow DockedChild => GetComponent<Window>().DockedChild?.GetComponent<CodeWindow>();

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void Update()
	{
		if (!errorMessage.IsShowing() && errorString != null)
		{
			ShowError();
		}
		if (updateSizeInXFrames > 0)
		{
			if (updateSizeInXFrames == 1)
			{
				UpdateSize();
			}
			updateSizeInXFrames--;
		}
		UpdateFade();
		UpdateCodeTooltips();
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		windowBackground.color = theme.ui.WindowFrameColor;
		theme.ui.text.ApplyTo(fileNameText);
		theme.code.text.ApplyTo(codeInput);
		codeInput.textComponent.color = new Color(1f, 1f, 1f, 0f);
		codeText.color = theme.code.text.TextColor;
		if (codeInput.TryGetComponent<Image>(out var component))
		{
			component.color = theme.code.BackgroundColor;
		}
		if (breakpointPanel.TryGetComponent<Image>(out var component2))
		{
			component2.color = theme.code.BackgroundColor;
		}
		if (scrollView.verticalScrollbar.handleRect.TryGetComponent<Image>(out var component3))
		{
			component3.color = theme.ui.ScrollbarColor;
		}
		codeText.text = CodeUtilities.SyntaxColor2(codeInput.text, ThemeManager.Inst.Theme);
	}

	private void UpdateCodeTooltips()
	{
		if (tooltipUpdateCallback == null)
		{
			return;
		}
		int num;
		int i = (num = TMP_TextUtilities.FindIntersectingCharacter(codeInput.textComponent, new Vector3(Input.mousePosition.x, Input.mousePosition.y), workspace.uiCam, visibleOnly: true));
		while (num > 0 && (Helper.IsValidNameChar(codeInput.text[num - 1]) || codeInput.text[num - 1] == '.'))
		{
			num--;
		}
		for (; i + 1 < codeInput.text.Length && (Helper.IsValidNameChar(codeInput.text[i + 1]) || codeInput.text[i + 1] == '.'); i++)
		{
		}
		if (num != hoverWordStart || i != hoverWordEnd)
		{
			hoverWordStart = num;
			hoverWordEnd = i;
			TimerManager.StopTimer(CallTooltipUpdate);
			if (hoverWordStart < 0 || hoverWordEnd >= codeInput.text.Length)
			{
				CallTooltipUpdate();
			}
			else
			{
				TimerManager.StartTimer(CallTooltipUpdate, 0.4);
			}
		}
	}

	private void CallTooltipUpdate()
	{
		if (tooltipUpdateCallback != null)
		{
			tooltipUpdateCallback();
		}
	}

	public void PressExecuteOrStop()
	{
		workspace.activeWindow = GetComponent<Window>();
		if (MainSim.Inst.StepByStepMode)
		{
			MainSim.Inst.StepByStepMode = false;
			return;
		}
		if (!MainSim.Inst.IsExecuting())
		{
			Node node = Parse();
			if (node != null && node != null)
			{
				MainSim.Inst.StartMainExecution(this, node);
				return;
			}
		}
		MainSim.Inst.StopMainExecution();
	}

	public void PressStepByStepButton()
	{
		workspace.activeWindow = GetComponent<Window>();
		if (MainSim.Inst.StepByStepMode)
		{
			MainSim.Inst.NextExecutionStep();
			return;
		}
		if (!MainSim.Inst.IsExecuting())
		{
			PressExecuteOrStop();
		}
		MainSim.Inst.StepByStepMode = true;
	}

	public void StartStepByStepMode()
	{
		stepByStepImg.sprite = stepByStepSprite;
		executeImg.sprite = executeSprite;
	}

	public void StartExecutionMode(bool closeErrors = true)
	{
		executeButton.IsRunning = true;
		stepByStepButton.IsRunning = true;
		isExecuting = true;
		executeImg.sprite = stopSprite;
		stepByStepImg.sprite = pauseSprite;
		if (closeErrors)
		{
			CloseError();
		}
	}

	public void StopExecutionMode()
	{
		if (isExecuting)
		{
			executeButton.IsRunning = false;
			stepByStepButton.IsRunning = false;
			isExecuting = false;
			executeImg.sprite = executeSprite;
			stepByStepImg.sprite = stepByStepSprite;
		}
	}

	public void SetExecutionColor()
	{
		if (!(OptionHolder.GetString("code highlights", "enabled") == "disabled"))
		{
			fadeStartTime = Time.time;
			isFading = true;
		}
	}

	private void UpdateFade()
	{
		if (isFading)
		{
			ColorTheme theme = ThemeManager.Inst.Theme;
			float num = Time.time - fadeStartTime;
			if (num >= 0.2f)
			{
				windowBackground.color = theme.ui.WindowFrameColor;
				isFading = false;
			}
			else
			{
				windowBackground.color = Color.Lerp(theme.code.WindowFrameExecColor, theme.ui.WindowFrameColor, num / 0.2f);
			}
		}
	}

	public void Load(string code)
	{
		codeInput.onTextInserted.AddListener(OnCodeInserted);
		codeInput.onTextMeshUpdated.AddListener(OnCodeChanged);
		codeInput.onEndEdit.AddListener(OnCodeCommit);
		codeInput.onCarretMoved.AddListener(OnCarretMoved);
		codeInput.onBackSpace.AddListener(OnBackspace);
		codeInput.onSelect.AddListener(OnFocus);
		codeInput.onTextSelection.AddListener(OnTextSelection);
		codeInput.uiCam = workspace.uiCam;
		codeInput.codeCompleter = (RectTransform)workspace.codeCompleter.transform;
		codeInput.text = code;
		fileNameText.text = fileName;
		undoState = codeInput.text;
		undoChangeTime = Time.time;
	}

	public void PromptDelete()
	{
		if (isExecuting)
		{
			return;
		}
		string text = string.Format(Localizer.Localize("popup_warning_delete_files"), fileName);
		List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
		{
			new WarningPopup.ButtonData("delete", delegate
			{
				MainSim.Inst.warningPopup.Close();
				if (!isExecuting)
				{
					GetComponent<Window>().Close();
				}
			}),
			new WarningPopup.ButtonData("cancel", MainSim.Inst.warningPopup.Close)
		};
		MainSim.Inst.warningPopup.ShowPopup(text, buttonsToAdd);
	}

	public void OnNameTextEdited()
	{
		Rename(fileNameText.text);
	}

	public void Rename(string newName)
	{
		if (workspace.IsValidFileName(newName))
		{
			GetComponent<Window>().Rename(newName);
			fileName = newName;
			fileNameText.text = newName;
		}
		else
		{
			fileNameText.text = fileName;
		}
	}

	public List<CodeWindow> GetDockedChildren()
	{
		if (DockedChild == null)
		{
			return new List<CodeWindow>();
		}
		List<CodeWindow> dockedChildren = DockedChild.GetDockedChildren();
		dockedChildren.Add(DockedChild);
		return dockedChildren;
	}

	public void SetMinimized()
	{
		_ = GetComponent<Window>().isMinimized;
		errorMessage.Close();
		updateSizeInXFrames = 2;
	}

	public bool IsPointerOverCodeInput()
	{
		if (RectTransformUtility.RectangleContainsScreenPoint((RectTransform)codeInput.textViewport.transform, Input.mousePosition, workspace.uiCam))
		{
			return RectTransformUtility.RectangleContainsScreenPoint(scrollViewRect, Input.mousePosition, workspace.uiCam);
		}
		return false;
	}

	public void OnCodeCommit(string s)
	{
		Parse();
	}

	private void OnCodeChanged()
	{
		UpdateTokens();
		UpdateSize();
		int stringPosition = Mathf.Clamp(codeInput.stringPosition - 1, 0, codeInput.text.Length);
		ScrollToStringPosition(stringPosition);
	}

	public void ScrollToStringPosition(int stringPosition)
	{
		TMP_TextInfo textInfo = codeInput.textComponent.textInfo;
		if (textInfo.characterCount != 0 && stringPosition < textInfo.characterCount)
		{
			float y = textInfo.characterInfo[stringPosition].bottomLeft.y;
			y -= ((RectTransform)codeText.transform).rect.height / 2f;
			y = 0f - y;
			RectTransform rectTransform = (RectTransform)codeInput.transform;
			float y2 = rectTransform.anchoredPosition.y;
			float height = scrollViewRect.rect.height;
			float lineHeight = textInfo.lineInfo[0].lineHeight;
			if (y < y2 + 30f)
			{
				rectTransform.anchoredPosition = new Vector2(0f, Mathf.Max(y - 30f, 0f));
			}
			else if (y > y2 + height - (70f + lineHeight))
			{
				rectTransform.anchoredPosition = new Vector2(0f, Mathf.Min(y - height + (70f + lineHeight), Mathf.Max(rectTransform.rect.height - height, 0f)));
			}
		}
	}

	public void Scroll(float scroll)
	{
		((RectTransform)codeInput.transform).anchoredPosition += new Vector2(0f, scroll * -500f);
	}

	private void UpdateSize()
	{
		Window component = GetComponent<Window>();
		Vector2 vector = codeInput.textComponent.GetRenderedValues(onlyVisibleCharacters: false) + extraSize;
		component.minSize.x = Mathf.Max(vector.x, minWidth, 0f);
		component.automaticSize.y = Mathf.Min(vector.y, scrollingStartSize);
		component.UpdateSize();
		UpdateCodeInputSize();
		if (errorMessage.IsShowing())
		{
			ShowError();
		}
	}

	public void UpdateCodeInputSize()
	{
		Window component = GetComponent<Window>();
		codeInput.GetComponent<LayoutElement>().minHeight = Mathf.Max(component.minSize.y, component.playerSetSize.y) - 70f;
	}

	private void OnCarretMoved()
	{
		bool flag = RectTransformUtility.RectangleContainsScreenPoint((RectTransform)workspace.codeCompleter.transform, Input.mousePosition, workspace.uiCam);
		if (workspace.codeCompleter.IsOpen && !flag)
		{
			workspace.codeCompleter.Close();
			codeInput.blockArrowKeys = false;
		}
	}

	private void OnTextSelection(string s, int start, int end)
	{
		prevSelectionEnd = Mathf.Max(start, end);
		prevSelectionStart = Mathf.Min(start, end);
	}

	private void OnFocus(string code)
	{
		CloseError();
		GetComponent<Window>().MoveToFront();
		workspace.activeWindow = GetComponent<Window>();
	}

	private void OnBackspace()
	{
		if (workspace.codeCompleter.IsOpen && codeInput.stringPosition > 0 && !char.IsLetterOrDigit(codeInput.text[codeInput.stringPosition - 1]))
		{
			workspace.codeCompleter.Close();
		}
		else if (workspace.codeCompleter.IsOpen)
		{
			workspace.codeCompleter.Backspace();
		}
	}

	private void OnCodeInserted(string inserted)
	{
		if (inserted.Contains('\r'))
		{
			codeInput.text = codeInput.text.Replace("\r", "");
		}
		if (isExecuting)
		{
			return;
		}
		workspace?.tooltip?.CloseTooltip();
		CodeCompleter codeCompleter = workspace.codeCompleter;
		if (inserted.Length == 1 && (Helper.IsValidNameChar(inserted[0]) || inserted[0] == '.'))
		{
			if (codeCompleter.IsOpen && inserted[0] != '.')
			{
				codeCompleter.UpdateString(inserted[0]);
			}
			else if (((char.IsLetter(inserted[0]) || inserted[0] == '_') && (codeInput.stringPosition <= 1 || !Helper.IsValidNameChar(codeInput.text[codeInput.stringPosition - 2]))) || inserted[0] == '.')
			{
				Vector3 bottomLeft = codeInput.textComponent.textInfo.characterInfo[codeInput.stringPosition - 1].bottomLeft;
				Vector3 vector = BlinkManager.GetCodeOffset(codeInput.GetComponent<RectTransform>());
				bottomLeft = codeInput.transform.TransformPoint(bottomLeft) + vector;
				if (inserted[0] == '.')
				{
					codeCompleter.Open(bottomLeft, GetSubWordList(GetWordBefore(codeInput.stringPosition - 2)), "", codeInput.stringPosition, this);
				}
				else if (codeInput.stringPosition >= 2 && codeInput.text[codeInput.stringPosition - 2] == '.')
				{
					codeCompleter.Open(bottomLeft, GetSubWordList(GetWordBefore(codeInput.stringPosition - 3)), inserted, codeInput.stringPosition - 1, this);
				}
				else if (IsImportStatement(codeInput.text, codeInput.stringPosition - 1))
				{
					codeCompleter.Open(bottomLeft, workspace.codeWindows.Values.Select((CodeWindow cw) => cw.fileName).ToList(), inserted, codeInput.stringPosition - 1, this);
				}
				else
				{
					codeCompleter.Open(bottomLeft, GetWordList(), inserted, codeInput.stringPosition - 1, this);
				}
			}
		}
		else if (codeCompleter.IsOpen && inserted.Length == 1 && (inserted[0] == '\t' || inserted[0] == '\n'))
		{
			if (codeCompleter.IsMatch || inserted[0] == '\t')
			{
				CompleteWord(removeExtraChar: true);
			}
			codeCompleter.Close();
		}
		else if (workspace.codeCompleter.IsOpen)
		{
			codeCompleter.Close();
		}
		if (prevText.Length > 0 && (OptionHolder.GetKeyCombination("indent selection").IsKeyPressed(pressedRightThisFrame: true) || OptionHolder.GetKeyCombination("unindent selection").IsKeyPressed(pressedRightThisFrame: true)))
		{
			List<int> list = new List<int>();
			bool flag = prevText.Length > codeInput.text.Length;
			if (flag)
			{
				int num = prevSelectionEnd - 1;
				while (num >= 0 && (num >= prevSelectionStart || prevText[num] != '\n'))
				{
					if (prevText[num] == '\n')
					{
						list.Add(num);
					}
					num--;
				}
				list.Add(num);
			}
			else
			{
				int num2 = codeInput.stringPosition - 2;
				while (num2 >= 0 && prevText[num2] != '\n')
				{
					num2--;
				}
				list.Add(num2);
			}
			bool flag2 = OptionHolder.GetKeyCombination("unindent selection").IsKeyPressed(pressedRightThisFrame: true);
			if (list.Count > 1 || flag2)
			{
				StringBuilder stringBuilder = new StringBuilder(prevText);
				int num3 = 0;
				bool flag3 = false;
				foreach (int item in list)
				{
					if (flag2)
					{
						if (stringBuilder.Length > item + 1 && stringBuilder[item + 1] == '\t')
						{
							stringBuilder.Remove(item + 1, 1);
							num3++;
						}
						else if (stringBuilder.Length > item + 4 && stringBuilder[item + 1] == ' ' && stringBuilder[item + 2] == ' ' && stringBuilder[item + 3] == ' ' && stringBuilder[item + 4] == ' ')
						{
							stringBuilder.Remove(item + 1, 4);
							num3 += 4;
							flag3 = true;
						}
					}
					else
					{
						bool flag4 = OptionHolder.GetString("tabs to spaces") == "enabled";
						stringBuilder.Insert(item + 1, flag4 ? "    " : "\t");
						num3 += ((!flag4) ? 1 : 4);
					}
				}
				int stringPosition = codeInput.stringPosition;
				codeInput.text = stringBuilder.ToString();
				if (flag2)
				{
					if (flag)
					{
						codeInput.stringPosition = prevSelectionEnd - num3;
						codeInput.selectionStringFocusPosition = prevSelectionStart - ((!flag3) ? 1 : 4);
					}
					else
					{
						codeInput.stringPosition = stringPosition - (1 + num3);
					}
				}
				else
				{
					codeInput.stringPosition = prevSelectionEnd + num3;
					codeInput.selectionStringFocusPosition = prevSelectionStart + 1;
				}
				if (workspace.codeCompleter.IsOpen)
				{
					codeCompleter.Close();
				}
				UpdateTokens();
				return;
			}
		}
		if (inserted.Contains('\r'))
		{
			codeInput.text = codeInput.text.Replace("\r", "");
		}
		UpdateTokens();
		int num4 = codeInput.stringPosition - 1;
		if (num4 > 0 && codeInput.text[num4] == '\n')
		{
			Token lastNewLine = tokens.GetLastNewLine(num4);
			string text = ((lastNewLine != null) ? lastNewLine.value.Remove(0, 1) : "\t");
			if (num4 - 1 > 0 && codeInput.text[num4 - 1] == ':' && lastNewLine != null)
			{
				text += (text.StartsWith(' ') ? "    " : ((object)'\t'));
			}
			codeInput.text = codeInput.text.Insert(num4 + 1, text);
			codeInput.stringPosition += text.Length;
		}
	}

	public void OpenCodeCompleterAtCarret()
	{
		if (codeInput.text[codeInput.stringPosition - 1] == ' ')
		{
			codeInput.text = codeInput.text.Remove(codeInput.stringPosition - 1, 1);
			codeInput.stringPosition--;
		}
		CodeCompleter codeCompleter = workspace.codeCompleter;
		int num = Mathf.Max(0, codeInput.stringPosition - 1);
		if (codeInput.text[num] == '.')
		{
			Vector3 bottomLeft = codeInput.textComponent.textInfo.characterInfo[num].bottomLeft;
			Vector3 vector = BlinkManager.GetCodeOffset(codeInput.GetComponent<RectTransform>());
			bottomLeft = codeInput.transform.TransformPoint(bottomLeft) + vector;
			codeCompleter.Open(bottomLeft, GetSubWordList(GetWordBefore(num - 1)), "", num + 1, this);
			return;
		}
		int num2 = num;
		while (num2 > 0 && Helper.IsValidNameChar(codeInput.text[num2]) && Helper.IsValidNameChar(codeInput.text[num2 - 1]))
		{
			num2--;
		}
		Vector3 bottomLeft2 = codeInput.textComponent.textInfo.characterInfo[num2].bottomLeft;
		Vector3 vector2 = BlinkManager.GetCodeOffset(codeInput.GetComponent<RectTransform>());
		bottomLeft2 = codeInput.transform.TransformPoint(bottomLeft2) + vector2;
		if (num2 != num && num2 > 0 && codeInput.text[num2 - 1] == '.')
		{
			codeCompleter.Open(bottomLeft2, GetSubWordList(GetWordBefore(num2 - 2)), codeInput.text.Substring(num2, num - num2), num2, this);
		}
		else
		{
			codeCompleter.Open(bottomLeft2, GetWordList(), codeInput.text.Substring(num2, num - num2), num2, this);
		}
	}

	private bool IsImportStatement(string text, int stringIndex)
	{
		int num = stringIndex - 1;
		while (num >= 0 && char.IsWhiteSpace(text[num]))
		{
			num--;
		}
		if (num < 0)
		{
			return false;
		}
		int num2 = num;
		while (num >= 0 && char.IsLetterOrDigit(text[num]))
		{
			num--;
		}
		int num3 = num + 1;
		int num4 = num2 - num;
		bool num5 = num4 == 6 && text[num3] == 'i' && text[num3 + 1] == 'm' && text[num3 + 2] == 'p' && text[num3 + 3] == 'o' && text[num3 + 4] == 'r' && text[num3 + 5] == 't';
		bool flag = num4 == 4 && text[num3] == 'f' && text[num3 + 1] == 'r' && text[num3 + 2] == 'o' && text[num3 + 3] == 'm';
		if (num5)
		{
			num = num3 - 1;
			while (num >= 0 && char.IsWhiteSpace(text[num]))
			{
				num--;
			}
			while (num >= 0 && char.IsLetterOrDigit(text[num]))
			{
				num--;
			}
			while (num >= 0 && char.IsWhiteSpace(text[num]))
			{
				num--;
			}
			if (num < 0)
			{
				return true;
			}
			int num6 = num;
			while (num >= 0 && char.IsLetterOrDigit(text[num]))
			{
				num--;
			}
			int num7 = num + 1;
			if (num6 - num == 4 && text[num7] == 'f' && text[num7 + 1] == 'r' && text[num7 + 2] == 'o' && text[num7 + 3] == 'm')
			{
				return false;
			}
			return true;
		}
		if (flag)
		{
			return true;
		}
		return false;
	}

	public void CompleteWord(bool removeExtraChar)
	{
		CodeCompleter codeCompleter = workspace.codeCompleter;
		bool flag = codeInput.stringPosition == codeInput.text.Length;
		string text = codeInput.text;
		int startStringIndex = codeCompleter.startStringIndex;
		text = text.Remove(startStringIndex, codeCompleter.TypedLength + (removeExtraChar ? 1 : 0));
		text = text.Insert(startStringIndex, codeCompleter.Selection);
		codeInput.text = text;
		codeInput.stringPosition += codeCompleter.Selection.Length - ((removeExtraChar && !flag) ? 1 : 0) - codeCompleter.TypedLength;
	}

	public void UpdateSearch(string word, int selectedIndex = -1)
	{
		codeText.text = CodeUtilities.SyntaxColor2(codeInput.text, ThemeManager.Inst.Theme, word, selectedIndex);
	}

	private void ConvertSpacesToTabs()
	{
		int num = 0;
		bool flag = true;
		List<int> list = null;
		for (int i = 0; i < codeInput.text.Length; i++)
		{
			if (codeInput.text[i] == ' ' && flag)
			{
				num++;
				if (num == 4)
				{
					num = 0;
					codeInput.stringPosition -= 3;
					if (list == null)
					{
						list = new List<int>();
					}
					list.Add(i - 3);
				}
			}
			else if (codeInput.text[i] == '\n' || codeInput.text[i] == '\t')
			{
				num = 0;
				flag = true;
			}
			else
			{
				num = 0;
				flag = false;
			}
		}
		if (list == null)
		{
			return;
		}
		list.Reverse();
		StringBuilder stringBuilder = new StringBuilder(codeInput.text);
		foreach (int item in list)
		{
			stringBuilder.Remove(item, 4);
			stringBuilder.Insert(item, '\t');
		}
		codeInput.text = stringBuilder.ToString();
	}

	private bool UpdateTokens()
	{
		if (codeInput.text == prevText)
		{
			return false;
		}
		if (isExecuting)
		{
			MainSim.Inst.StopMainExecution();
		}
		if (OptionHolder.GetString("tabs to spaces") == "enabled" && codeInput.text.Contains('\t'))
		{
			int num = codeInput.text.Take(codeInput.stringPosition + 1).Count((char c) => c == '\t');
			codeInput.text = codeInput.text.Replace("\t", "    ");
			codeInput.stringPosition += num * 3;
		}
		else if (OptionHolder.GetString("tabs to spaces") == "disabled")
		{
			ConvertSpacesToTabs();
		}
		prevText = codeInput.text;
		dirty = true;
		codeText.text = CodeUtilities.SyntaxColor2(codeInput.text, ThemeManager.Inst.Theme);
		Tokenizer.Tokenize(codeInput.text, out tokens);
		updateTokenizedIdentifiers(tokens);
		if (undoPreventNextChange)
		{
			undoPreventNextChange = false;
		}
		else
		{
			if (Time.time - undoChangeTime > 0.5f)
			{
				workspace.undoHistory.AddChange(SetToCodeState, undoState, base.gameObject);
				undoState = codeInput.text;
			}
			undoChangeTime = Time.time;
		}
		return true;
		void updateTokenizedIdentifiers(TokenStream t)
		{
			tokenizedIdentifiers.Clear();
			foreach (Token item in t)
			{
				if (item.type == TokenType.IDENTIFIER)
				{
					tokenizedIdentifiers.Add(item.value);
				}
			}
		}
	}

	private object SetToCodeState(object state)
	{
		string text = codeInput.text;
		undoPreventNextChange = true;
		codeInput.text = (string)state;
		if (!codeInput.isFocused)
		{
			Parse();
		}
		undoState = codeInput.text;
		return text;
	}

	public Node Parse()
	{
		lock (parseLock)
		{
			UpdateTokens();
			if (!dirty)
			{
				if (parseException != null)
				{
					errorString = parseException.Message;
					errorStartIndex = parseException.startIndex;
					errorEndIndex = parseException.endIndex;
				}
				return cachedProgram?.syntaxTree;
			}
			MainSim.Inst.dirty = true;
			dirty = false;
			parsedFunctions.Clear();
			try
			{
				cachedProgram = Parser.Parse(tokens, this);
				cachedProgram.syntaxTree.CheckForNonsensicalCode();
				breakpointPanel.UpdateBreakpoints(cachedProgram.syntaxTree);
				parseException = null;
				return cachedProgram?.syntaxTree;
			}
			catch (ParseException ex)
			{
				errorString = ex.Message;
				errorStartIndex = ex.startIndex;
				errorEndIndex = ex.endIndex;
				parseException = ex;
				cachedProgram = null;
				return null;
			}
		}
	}

	public void SetErrorMessage(string message, int startIndex, int endIndex)
	{
		errorString = message;
		errorStartIndex = startIndex;
		errorEndIndex = endIndex;
	}

	private void ShowError()
	{
		if (!(EventSystem.current.currentSelectedGameObject == codeInput.gameObject))
		{
			Vector3 vector;
			Vector3 right;
			if (GetComponent<Window>().isMinimized)
			{
				errorMessage.transform.SetParent(base.transform);
				Rect rect = ((RectTransform)base.transform).rect;
				vector = base.transform.TransformPoint(new Vector3((rect.xMin + rect.xMax) / 2f, rect.yMin + 10f, 0f));
				right = vector;
				workspace.MoveCameraTo(GetComponent<Window>());
			}
			else
			{
				errorMessage.transform.SetParent(codeInput.transform);
				TMP_CharacterInfo[] characterInfo = codeInput.textComponent.textInfo.characterInfo;
				Vector3 vector2 = BlinkManager.GetCodeOffset(codeInput.GetComponent<RectTransform>());
				ScrollToStringPosition(errorStartIndex);
				vector = codeInput.transform.TransformPoint(characterInfo[errorStartIndex].bottomLeft) + vector2;
				right = codeInput.transform.TransformPoint(characterInfo[errorEndIndex].bottomRight) + vector2;
				workspace.MoveCameraTo(GetComponent<Window>(), alwaysMoveWindow: false, errorStartIndex, codeInput);
			}
			errorMessage.ShowError(errorString, vector, right);
		}
	}

	private void CloseError()
	{
		errorString = null;
		errorMessage.Close();
	}

	private List<string> GetWordList()
	{
		HashSet<string> hashSet = BuiltinFunctions.Functions.Keys.Where((string x) => MainSim.Inst.IsUnlocked(x) && x != "tap").ToHashSet();
		hashSet.UnionWith(MainSim.Inst.GetUnlockedKeywords());
		hashSet.UnionWith(tokenizedIdentifiers);
		if (cachedProgram != null)
		{
			hashSet.UnionWith(cachedProgram.allVars);
			foreach (string importedModule in cachedProgram.importedModules)
			{
				foreach (CodeWindow value in workspace.codeWindows.Values)
				{
					if (value.fileName == importedModule && value.cachedProgram != null)
					{
						hashSet.UnionWith(value.cachedProgram.allVars);
					}
				}
			}
		}
		List<string> list = hashSet.ToList();
		list.Add("__name__");
		list.Sort();
		return list;
	}

	private List<string> GetSubWordList(string domain)
	{
		IEnumerable<string> enumerable = domain switch
		{
			"Entities" => from f in ResourceManager.GetAllFarmObjects()
				where !f.isGround
				select f.objectName into s
				where MainSim.Inst.IsUnlocked(s)
				select s, 
			"Grounds" => from f in ResourceManager.GetAllFarmObjects()
				where f.isGround
				select f.objectName into s
				where MainSim.Inst.IsUnlocked(s)
				select s, 
			"Items" => from i in ResourceManager.GetAllItems()
				where MainSim.Inst.IsUnlocked(i.itemName) && i.enabled
				select i.itemName, 
			"Unlocks" => from u in ResourceManager.GetAllUnlocks()
				where u.enabled
				select u.unlockName, 
			"Leaderboards" => from l in ResourceManager.GetAllLeaderboards()
				select l.leaderboardName, 
			"Hats" => from h in ResourceManager.GetAllHats()
				where MainSim.Inst.IsUnlocked(h.hatName) && !h.hidden
				select h.hatName, 
			_ => null, 
		};
		if (enumerable == null)
		{
			bool flag = false;
			HashSet<string> hashSet = new HashSet<string>();
			foreach (CodeWindow value in workspace.codeWindows.Values)
			{
				if (value.fileName == domain && value.cachedProgram != null)
				{
					hashSet.UnionWith(value.cachedProgram.allVars);
					flag = true;
				}
			}
			if (!flag)
			{
				hashSet.UnionWith(BuiltinFunctions.Methods.Keys.Where((string s) => MainSim.Inst.IsUnlocked(s)).ToHashSet());
			}
			return hashSet.ToList();
		}
		if (enumerable != null)
		{
			return enumerable.Select(CodeUtilities.ToUpperSnake).ToList();
		}
		return new List<string>();
	}

	private string GetWordBefore(int stringPos)
	{
		int num = stringPos;
		while (num >= 0 && codeInput.text.Length > num && Helper.IsValidNameChar(codeInput.text[num]))
		{
			num--;
		}
		return codeInput.text.Substring(num + 1, stringPos - num);
	}

	public TooltipInfo GetTooltipInfo(Action updateTooltipCallback)
	{
		tooltipUpdateCallback = updateTooltipCallback;
		if (hoverWordStart < 0 || hoverWordEnd >= CodeInput.text.Length)
		{
			return null;
		}
		string word = ((codeInput.text == "") ? "" : codeInput.text.Substring(hoverWordStart, hoverWordEnd - hoverWordStart + 1));
		TooltipInfo tooltipInfo = TooltipUtils.GetWordTooltip(word, this);
		if (MainSim.Inst.EvaluateName(word, out var value))
		{
			string text = CodeUtilities.ToNiceString(value);
			tooltipInfo = new TooltipInfo("`" + text + "`");
		}
		if (tooltipInfo != null)
		{
			Vector3 bottomLeft = codeInput.textComponent.textInfo.characterInfo[hoverWordStart].bottomLeft;
			Vector3 vector = BlinkManager.GetCodeOffset(codeInput.GetComponent<RectTransform>());
			Vector3 fixedPosition = codeInput.transform.TransformPoint(bottomLeft) + vector;
			tooltipInfo.fixedPosition = fixedPosition;
			tooltipInfo.anchor = TooltipInfo.Anchor.BottomRight;
			tooltipInfo.delay = 0.3f;
		}
		return tooltipInfo;
	}

	public void TooltipGone()
	{
		tooltipUpdateCallback = null;
	}
}
public class ContainerScaler : MonoBehaviour
{
	[SerializeField]
	private RectTransform contentRect;

	[SerializeField]
	private Canvas canvas;

	[SerializeField]
	private CameraController cameraController;

	private Vector2 rectSize;

	public void UpdateMarginSize()
	{
		Vector2 vector = new Vector2(Screen.width, Screen.height) / canvas.scaleFactor / cameraController.zoom;
		GetComponent<RectTransform>().sizeDelta = rectSize + vector * 1.4f;
	}

	public void UpdateSize()
	{
		RectTransform component = base.transform.parent.GetComponent<RectTransform>();
		List<RectTransform> list = new List<RectTransform>();
		int childCount = base.transform.childCount;
		for (int i = 0; i < childCount; i++)
		{
			RectTransform rectTransform = (RectTransform)base.transform.GetChild(0);
			list.Add(rectTransform);
			rectTransform.transform.SetParent(component, worldPositionStays: true);
		}
		Vector2 vector = Vector2.zero;
		Vector2 vector2 = Vector2.zero;
		if (list.Count > 0)
		{
			vector = list[0].rect.min + list[0].anchoredPosition;
			vector2 = list[0].rect.max + list[0].anchoredPosition;
			foreach (RectTransform item in list)
			{
				vector = Vector2.Min(vector, item.rect.min + item.anchoredPosition);
				Window window = item.GetComponent<Window>();
				while (window?.DockedChild != null)
				{
					window = window.DockedChild;
					vector.y += ((RectTransform)window.transform).rect.y;
				}
				vector2 = Vector2.Max(vector2, item.rect.max + item.anchoredPosition);
			}
		}
		Vector2 vector3 = new Vector2(Screen.width, Screen.height) / canvas.scaleFactor;
		Rect rect = new Rect
		{
			min = vector,
			max = vector2
		};
		RectTransform component2 = GetComponent<RectTransform>();
		component2.sizeDelta = rect.size + vector3 * 1.4f;
		rectSize = rect.size;
		component2.anchoredPosition = rect.center;
		foreach (RectTransform item2 in list)
		{
			item2.SetParent(base.transform, worldPositionStays: true);
		}
	}
}
public class DLCBanner : MonoBehaviour
{
	public uint dlcAppId;

	public string dlcUrl;

	public bool hideAfterShow;

	private const string DlcBannerOptionName = "show dlc banner";

	private const string OptionDisabledValue = "disabled";

	public void ShowDLC()
	{
		if (!TryShowOverlay())
		{
			Application.OpenURL(dlcUrl);
		}
		if (hideAfterShow)
		{
			HideBanner();
		}
	}

	public void Close()
	{
		HideBanner();
	}

	private void Start()
	{
		if (OptionHolder.GetString("show dlc banner") == "disabled")
		{
			base.gameObject.SetActive(value: false);
		}
	}

	private bool TryShowOverlay()
	{
		if (!SteamManager.Initialized)
		{
			return false;
		}
		if (!SteamUtils.IsOverlayEnabled())
		{
			return false;
		}
		SteamFriends.ActivateGameOverlayToStore(new AppId_t(dlcAppId), EOverlayToStoreFlag.k_EOverlayToStoreFlag_None);
		return true;
	}

	private void HideBanner()
	{
		base.gameObject.SetActive(value: false);
		OptionHolder.SetOption("show dlc banner", "disabled");
	}
}
public class DocsWindow : MonoBehaviour
{
	[SerializeField]
	private ScrollRect scrollView;

	[SerializeField]
	private RectTransform container;

	[SerializeField]
	private MarkdownText markdownPrefab;

	public string openDoc;

	public string fullOpenDoc;

	public MarkdownText OpenMarkdownText { get; private set; }

	public void LoadDoc(string doc)
	{
		if (container.childCount > 0)
		{
			Transform child = container.GetChild(0);
			container.DetachChildren();
			UnityEngine.Object.Destroy(child.gameObject);
		}
		StringBuilder stringBuilder = new StringBuilder();
		if (doc.StartsWith("functions/"))
		{
			string text = doc.Substring("functions/".Length);
			stringBuilder.Append(Localizer.Localize("code_tooltip_" + text));
			AddUnlockedIn(stringBuilder, text);
		}
		else if (doc.StartsWith("unlocks/"))
		{
			string unlockName = doc.Substring("unlocks/".Length);
			stringBuilder.Append(TooltipUtils.UnlockTooltip(unlockName).text);
		}
		else if (doc.StartsWith("items/"))
		{
			string text2 = doc.Substring("items/".Length);
			stringBuilder.Append(TooltipUtils.ItemTooltip(text2).text);
			AddUnlockedIn(stringBuilder, text2);
		}
		else if (doc.StartsWith("objects/"))
		{
			string text3 = doc.Substring("objects/".Length);
			stringBuilder.Append(TooltipUtils.FarmObjectTooltip(text3).text);
			AddUnlockedIn(stringBuilder, text3);
		}
		else
		{
			stringBuilder.Append(Localizer.LoadDoc(doc));
		}
		container.anchoredPosition = new Vector2(0f, 0f);
		MarkdownText markdownText = UnityEngine.Object.Instantiate(markdownPrefab, container);
		fullOpenDoc = stringBuilder.ToString();
		markdownText.Setup(fullOpenDoc, LinkCalled);
		openDoc = doc;
		OpenMarkdownText = markdownText;
		MainSim.Inst.workspace.searchBox.RefreshSearchResults();
	}

	private void AddUnlockedIn(StringBuilder sb, string word)
	{
		string keywordDocsPage = TooltipUtils.GetKeywordDocsPage(word);
		if (!(keywordDocsPage == ""))
		{
			string text = keywordDocsPage.Split('/').Last();
			text = text.Substring(0, text.Length - 3);
			string value = string.Format(Localizer.Localize("unlocked_in"), CodeUtilities.ToUpperSnake(text), keywordDocsPage);
			sb.Append('\n');
			sb.Append('\n');
			sb.Append(value);
		}
	}

	private void LinkCalled(string link)
	{
		if (link.StartsWith("persistent_data_path/"))
		{
			Process.Start(Path.Combine(Helper.persistentDataPath, link.Substring("persistent_data_path/".Length)));
		}
		else if (link.StartsWith("https"))
		{
			Process.Start(link);
		}
		else
		{
			LoadDoc(link);
		}
	}

	public void GotoHome()
	{
		LoadDoc("docs/home.md");
	}

	public void Scroll(float scroll)
	{
		container.anchoredPosition += new Vector2(0f, scroll * -500f);
	}

	private void Awake()
	{
		OptionHolder.OnOptionChanged += OnSettingChanged;
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDestroy()
	{
		OptionHolder.OnOptionChanged -= OnSettingChanged;
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnSettingChanged(string setting)
	{
		if (setting == "language")
		{
			LoadDoc(openDoc);
		}
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		if (TryGetComponent<Image>(out var component))
		{
			component.color = theme.ui.WindowFrameColor;
		}
		if (scrollView.TryGetComponent<Image>(out var component2))
		{
			component2.color = theme.docs.BackgroundColor;
		}
		if (scrollView.verticalScrollbar.handleRect.TryGetComponent<Image>(out var component3))
		{
			component3.color = theme.ui.ScrollbarColor;
		}
		LoadDoc(openDoc);
	}
}
public class DropdownTooltips : MonoBehaviour, ITooltipHandler
{
	[SerializeField]
	private TMP_Dropdown dropdown;

	[NonSerialized]
	public List<string> descriptions = new List<string>();

	[NonSerialized]
	public List<ItemBlock> costs;

	private int index;

	public void OnItemHovered(GameObject item)
	{
		index = item.transform.GetSiblingIndex() - 1;
	}

	public TooltipInfo GetTooltipInfo(Action updateTooltipCallback)
	{
		return null;
	}

	public void TooltipGone()
	{
	}
}
public class ErrorMessage : MonoBehaviour
{
	[SerializeField]
	private float codeBoxMargin;

	[SerializeField]
	private float errorBoxHeight;

	[SerializeField]
	private Image background;

	[SerializeField]
	private Image messageBorder;

	[SerializeField]
	private RectTransform codeBorder;

	[SerializeField]
	private TextMeshProUGUI errorText;

	[SerializeField]
	private TextMeshProUGUI errorTitle;

	private string error;

	private Vector3 left;

	private Vector3 right;

	private bool updateOnEnable;

	public bool IsShowing()
	{
		return base.gameObject.activeInHierarchy;
	}

	public void ShowError(string error, Vector3 left, Vector3 right)
	{
		this.error = error;
		this.left = left;
		this.right = right;
		if (base.gameObject.activeInHierarchy)
		{
			UpdateErrorMessage();
			return;
		}
		updateOnEnable = true;
		base.gameObject.SetActive(value: true);
	}

	private void OnEnable()
	{
		if (updateOnEnable)
		{
			updateOnEnable = false;
			UpdateErrorMessage();
		}
	}

	private void UpdateErrorMessage()
	{
		RectTransform rectTransform = (RectTransform)base.transform;
		rectTransform.position = (left + right) / 2f;
		codeBorder.sizeDelta = new Vector2((rectTransform.InverseTransformPoint(right) - rectTransform.InverseTransformPoint(left)).x + codeBoxMargin, codeBorder.sizeDelta.y);
		errorText.text = Localizer.Localize(error);
		rectTransform.sizeDelta = new Vector2(rectTransform.sizeDelta.x, errorText.preferredHeight + errorBoxHeight);
		ColorTheme theme = ThemeManager.Inst.Theme;
		background.color = theme.code.ErrorBackgroundColor;
		messageBorder.color = theme.code.ErrorBorderColor;
		errorText.color = theme.code.ErrorMessageColor;
		errorTitle.color = theme.code.ErrorTitleColor;
		if (codeBorder.TryGetComponent<Image>(out var component))
		{
			component.color = theme.code.ErrorBorderColor;
		}
	}

	public void Close()
	{
		base.gameObject.SetActive(value: false);
	}
}
[RequireComponent(typeof(ColoredButton))]
public class FlashingButton : MonoBehaviour
{
	private ColoredButton coloredButton;

	[SerializeField]
	private float brightness = 0.2f;

	[SerializeField]
	private float flashSpeed = 1f;

	private void Awake()
	{
		coloredButton = GetComponent<ColoredButton>();
		coloredButton.OnClick.AddListener(OnButtonPressed);
	}

	private void Update()
	{
		if (MainSim.Inst.IsUnlocked("loops"))
		{
			base.enabled = false;
		}
		else if (MainSim.Inst.GetNumItem(StringIds.GetItemId("hay")) >= 1.0)
		{
			coloredButton.UpdateColor(1.2f + brightness * (Mathf.Sin(Time.time * flashSpeed) + 1f));
		}
	}

	private void OnButtonPressed()
	{
		base.enabled = false;
	}
}
public class HatPopup : MonoBehaviour
{
	private static HatPopup _instance;

	[SerializeField]
	private MarkdownText text;

	[SerializeField]
	private RectTransform scaleObject;

	[SerializeField]
	private RectTransform greenOverlayBox;

	[SerializeField]
	private float animationDuration = 0.3f;

	[SerializeField]
	private float displayDuration = 4f;

	private volatile HatSO hatSO;

	private bool isPopupActive;

	public static HatPopup Inst => _instance;

	private void Awake()
	{
		if (_instance != null && _instance != this)
		{
			UnityEngine.Object.Destroy(base.gameObject);
		}
		else
		{
			_instance = this;
		}
	}

	private void Start()
	{
		scaleObject.localScale = new Vector3(0f, 1f, 1f);
		greenOverlayBox.localScale = new Vector3(0f, 1f, 1f);
	}

	private void Update()
	{
		HatSO hatSO = this.hatSO;
		if (hatSO != null && !isPopupActive)
		{
			this.hatSO = null;
			text.UpdateText(CodeUtilities.LocalizeAndFormat("new_hat_unlocked", hatSO));
			StartCoroutine(ShowPopupAnimation());
		}
	}

	public void ShowPopup(HatSO hat)
	{
		hatSO = hat;
	}

	private IEnumerator ShowPopupAnimation()
	{
		isPopupActive = true;
		yield return StartCoroutine(GreenOverlayEffect());
		yield return new WaitForSeconds(displayDuration);
		yield return StartCoroutine(TweenScaleX(scaleObject, 1f, 0f, animationDuration));
		isPopupActive = false;
	}

	private IEnumerator GreenOverlayEffect()
	{
		Vector2 originalPivot = greenOverlayBox.pivot;
		Vector2 originalAnchoredPosition = greenOverlayBox.anchoredPosition;
		SetPivotAndAdjustPosition(greenOverlayBox, new Vector2(0f, 0.5f));
		yield return StartCoroutine(TweenScaleX(greenOverlayBox, 0f, 1f, animationDuration));
		scaleObject.localScale = Vector3.one;
		SetPivotAndAdjustPosition(greenOverlayBox, new Vector2(1f, 0.5f));
		yield return StartCoroutine(TweenScaleX(greenOverlayBox, 1f, 0f, animationDuration));
		greenOverlayBox.pivot = originalPivot;
		greenOverlayBox.anchoredPosition = originalAnchoredPosition;
	}

	private void SetPivotAndAdjustPosition(RectTransform rectTransform, Vector2 newPivot)
	{
		Vector2 pivot = rectTransform.pivot;
		Vector2 vector = new Vector2((newPivot.x - pivot.x) * rectTransform.rect.width, (newPivot.y - pivot.y) * rectTransform.rect.height);
		rectTransform.pivot = newPivot;
		rectTransform.anchoredPosition += vector;
	}

	private IEnumerator TweenScaleX(RectTransform target, float fromScaleX, float toScaleX, float duration)
	{
		float elapsedTime = 0f;
		Vector3 startScale = target.localScale;
		while (elapsedTime < duration)
		{
			elapsedTime += Time.deltaTime;
			float num = elapsedTime / duration;
			num = num * num * (3f - 2f * num);
			float x = Mathf.Lerp(fromScaleX, toScaleX, num);
			target.localScale = new Vector3(x, startScale.y, startScale.z);
			yield return null;
		}
		target.localScale = new Vector3(toScaleX, startScale.y, startScale.z);
	}

	private IEnumerator TweenScale(RectTransform target, Vector3 fromScale, Vector3 toScale, float duration)
	{
		float elapsedTime = 0f;
		while (elapsedTime < duration)
		{
			elapsedTime += Time.deltaTime;
			float num = elapsedTime / duration;
			num = num * num * (3f - 2f * num);
			target.localScale = Vector3.Lerp(fromScale, toScale, num);
			yield return null;
		}
		target.localScale = toScale;
	}
}
public class Inventory : MonoBehaviour
{
	[SerializeField]
	private ItemUI itemUIPrefab;

	[SerializeField]
	private Transform container;

	private Dictionary<int, ItemUI> itemUIs = new Dictionary<int, ItemUI>();

	private Func<ItemBlock> getItemBlock;

	private void Update()
	{
		ItemBlock itemBlock = getItemBlock();
		if (itemBlock == null)
		{
			return;
		}
		foreach (int item in itemBlock.ItemIds().Union(itemUIs.Keys))
		{
			UpdateItem(item, itemBlock.GetNumber(item));
		}
	}

	public void SetUp(Func<ItemBlock> getItemBlock)
	{
		foreach (ItemUI value in itemUIs.Values)
		{
			UnityEngine.Object.Destroy(value.gameObject);
		}
		itemUIs.Clear();
		this.getItemBlock = getItemBlock;
		ItemBlock itemBlock = getItemBlock();
		if (itemBlock == null)
		{
			return;
		}
		foreach (int item in itemBlock.ItemIds())
		{
			AddItem(item, itemBlock.GetNumber(item));
		}
	}

	private void AddItem(int itemId, double n)
	{
		ItemUI itemUI = UnityEngine.Object.Instantiate(itemUIPrefab, container);
		itemUI.Setup(itemId, n);
		itemUIs[itemId] = itemUI;
	}

	private void UpdateItem(int itemId, double n)
	{
		if (itemUIs.ContainsKey(itemId))
		{
			itemUIs[itemId].UpdateCount(n);
		}
		else
		{
			AddItem(itemId, n);
		}
	}
}
public class ItemUI : MonoBehaviour, ITooltipHandler
{
	[SerializeField]
	private float animDuration = 0.1f;

	[SerializeField]
	private float animHeightOffset = 5f;

	[SerializeField]
	private float textWidthPerChar = 12f;

	[SerializeField]
	private float imageScaleDuration = 0.05f;

	[SerializeField]
	private float imageDescaleDurationFactor = 2f;

	[SerializeField]
	private float imageScalePickup = 1.1f;

	[SerializeField]
	private float imageScaleImpact = 1.3f;

	[SerializeField]
	private float impactRatioThreshold = 0.3f;

	[SerializeField]
	private float imagePickupOffset = 5f;

	[SerializeField]
	private Image image;

	[SerializeField]
	private TextMeshProUGUI countText;

	[SerializeField]
	private Transform tooltipPos;

	private ItemSO item;

	private double amount;

	private double newAmount;

	private Action updateTooltipCallback;

	private float updateAnimStartTime = -1f;

	private bool isAnimating;

	private Vector3[] startPositions;

	private Vector3[] endPositions;

	private Vector3[] currentPositions;

	private List<int> animatedCharacters = new List<int>();

	private float imageScalingStartTime = -1f;

	private float imageTargetScale = 1f;

	private float imageStartPosY;

	public void Setup(int itemId, double c)
	{
		item = ResourceManager.GetItem(itemId);
		amount = c;
		countText.text = Helper.NrToText(amount);
		RectTransform component = countText.GetComponent<RectTransform>();
		component.sizeDelta = new Vector2((float)countText.text.Length * textWidthPerChar, component.sizeDelta.y);
		image.sprite = Resources.Load<Sprite>("ItemTextures/" + item.itemName);
		imageStartPosY = image.transform.localPosition.y;
	}

	public void UpdateCount(double c)
	{
		double num = newAmount;
		newAmount = c;
		if (!(newAmount <= num) && !(Time.time - imageScalingStartTime < imageScaleDuration * 3f) && !(OptionHolder.GetString("increment number effect") != "enabled"))
		{
			double num2 = Math.Abs(newAmount - num);
			imageTargetScale = (((num2 + 1.0) / (newAmount + 1.0) > (double)impactRatioThreshold) ? imageScaleImpact : imageScalePickup);
			if (image.transform.localScale.x > imageTargetScale)
			{
				imageTargetScale = image.transform.localScale.x;
			}
			imageScalingStartTime = Time.time;
			float num3 = (image.transform.localScale.x - 1f) / (imageTargetScale - 1f);
			imageScalingStartTime -= num3 * imageScaleDuration;
		}
	}

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		ThemeManager.Inst.Theme.docs.text.ApplyTo(countText);
	}

	private void Update()
	{
		if (newAmount != amount && !isAnimating)
		{
			bool increase = newAmount > amount;
			amount = newAmount;
			string text = Helper.NrToText(amount);
			if (updateTooltipCallback != null)
			{
				updateTooltipCallback();
			}
			if (text != countText.text && OptionHolder.GetString("increment number effect") == "enabled")
			{
				StartAnimation(text, increase);
			}
			else if (text != countText.text)
			{
				RectTransform component = countText.GetComponent<RectTransform>();
				component.sizeDelta = new Vector2((float)text.Length * textWidthPerChar, component.sizeDelta.y);
				countText.text = text;
			}
		}
		UpdateAnimation();
		UpdateImageScale();
	}

	private void StartAnimation(string newText, bool increase)
	{
		if (string.IsNullOrEmpty(newText))
		{
			countText.text = newText;
			updateAnimStartTime = -1f;
			return;
		}
		animatedCharacters.Clear();
		StringBuilder stringBuilder = new StringBuilder(newText);
		int num = Mathf.Min(newText.Length, countText.text.Length);
		for (int i = 0; i < num; i++)
		{
			if (newText[i] != countText.text[i] && char.IsDigit(newText[i]))
			{
				animatedCharacters.Add(i);
				stringBuilder.Append(countText.text[i]);
			}
		}
		RectTransform component = countText.GetComponent<RectTransform>();
		component.sizeDelta = new Vector2((float)newText.Length * textWidthPerChar, component.sizeDelta.y);
		countText.text = stringBuilder.ToString();
		countText.ForceMeshUpdate();
		TMP_TextInfo textInfo = countText.textInfo;
		int materialReferenceIndex = textInfo.characterInfo[0].materialReferenceIndex;
		Vector3[] vertices = textInfo.meshInfo[materialReferenceIndex].vertices;
		updateAnimStartTime = Time.time;
		isAnimating = true;
		startPositions = new Vector3[vertices.Length];
		endPositions = new Vector3[vertices.Length];
		currentPositions = new Vector3[vertices.Length];
		float num2 = textInfo.characterInfo[0].topLeft.y + animHeightOffset;
		float num3 = textInfo.characterInfo[0].bottomLeft.y - animHeightOffset;
		for (int j = 0; j < textInfo.characterCount; j++)
		{
			if (!textInfo.characterInfo[j].isVisible)
			{
				continue;
			}
			int vertexIndex = textInfo.characterInfo[j].vertexIndex;
			if (j < newText.Length)
			{
				for (int k = 0; k < 4; k++)
				{
					startPositions[vertexIndex + k] = vertices[vertexIndex + k];
					endPositions[vertexIndex + k] = vertices[vertexIndex + k];
				}
				continue;
			}
			int num4 = animatedCharacters[j - newText.Length];
			int vertexIndex2 = textInfo.characterInfo[num4].vertexIndex;
			for (int l = 0; l < 4; l++)
			{
				startPositions[vertexIndex + l] = vertices[vertexIndex2 + l];
				endPositions[vertexIndex + l] = vertices[vertexIndex2 + l];
				endPositions[vertexIndex + l].y = (increase ? num2 : num3);
				startPositions[vertexIndex2 + l].y = (increase ? num3 : num2);
			}
		}
	}

	private void UpdateAnimation()
	{
		if (!isAnimating)
		{
			return;
		}
		if (Time.time - updateAnimStartTime > animDuration)
		{
			isAnimating = false;
			countText.text = Helper.NrToText(amount);
			return;
		}
		float t = (Time.time - updateAnimStartTime) / animDuration;
		for (int i = 0; i < startPositions.Length; i++)
		{
			currentPositions[i] = Vector3.Lerp(startPositions[i], endPositions[i], t);
		}
		TMP_MeshInfo tMP_MeshInfo = countText.textInfo.meshInfo[0];
		tMP_MeshInfo.mesh.vertices = currentPositions;
		countText.UpdateGeometry(tMP_MeshInfo.mesh, 0);
	}

	private void UpdateImageScale()
	{
		float num = (Time.time - imageScalingStartTime) / imageScaleDuration;
		if (num >= 1f)
		{
			num = (1f + imageDescaleDurationFactor - num) / imageDescaleDurationFactor;
		}
		if (!(num < 0f))
		{
			float num2 = Mathf.Lerp(1f, imageTargetScale, num);
			image.transform.localScale = new Vector3(1f / num2, num2, 1f);
			float y = Mathf.Lerp(imageStartPosY, imageStartPosY + imagePickupOffset, num);
			image.transform.localPosition = new Vector3(image.transform.localPosition.x, y, image.transform.localPosition.z);
		}
	}

	public TooltipInfo GetTooltipInfo(Action updateTooltipCallback)
	{
		this.updateTooltipCallback = updateTooltipCallback;
		TooltipInfo tooltipInfo = TooltipUtils.ItemTooltip(item.name);
		if (tooltipInfo != null)
		{
			tooltipInfo.fixedPosition = ((tooltipPos != null) ? tooltipPos.position : default(Vector3));
			tooltipInfo.anchor = TooltipInfo.Anchor.BottomRight;
			tooltipInfo.delay = 0f;
		}
		return tooltipInfo;
	}

	public void TooltipGone()
	{
		updateTooltipCallback = null;
	}
}
public class Leaderboard : MonoBehaviour
{
	[SerializeField]
	private LeaderboardEntry leaderboardEntryPrefab;

	[SerializeField]
	private Transform container;

	[SerializeField]
	private TextMeshProUGUI highScoreText;

	[SerializeField]
	private TextMeshProUGUI rankText;

	private List<LeaderboardEntry> leaderboardEntries = new List<LeaderboardEntry>();

	public void FillLeaderboard(string leaderboardName, int score = 0)
	{
		SteamLeaderboard.LoadLeaderboard(leaderboardName, score, OnPlayerLoaded, OnEntriesLoaded);
		highScoreText.text = "-";
		rankText.text = "-";
		container.gameObject.SetActive(value: false);
	}

	private void OnPlayerLoaded(LeaderboardEntryData[] data)
	{
		if (data.Length != 0)
		{
			if (highScoreText != null)
			{
				highScoreText.text = LeaderboardManager.StringFromTimeSpan(TimeSpan.FromMilliseconds(data[0].score));
			}
			if (rankText != null)
			{
				rankText.text = "#" + data[0].rank;
			}
			if (data[0].rank == 1)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("gold_trophy_hat"));
			}
			else if (data[0].rank == 2)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("silver_trophy_hat"));
			}
			else if (data[0].rank == 3)
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("wood_trophy_hat"));
			}
		}
	}

	private void OnEntriesLoaded(LeaderboardEntryData[] data)
	{
		container.gameObject.SetActive(value: true);
		for (int i = 0; i < data.Length; i++)
		{
			if (leaderboardEntries.Count - 1 < i)
			{
				leaderboardEntries.Add(UnityEngine.Object.Instantiate(leaderboardEntryPrefab, container));
			}
			leaderboardEntries[i].Setup(data[i].rank, data[i].playerName, LeaderboardManager.StringFromTimeSpan(TimeSpan.FromMilliseconds(data[i].score)));
		}
		while (leaderboardEntries.Count > data.Length)
		{
			UnityEngine.Object.Destroy(leaderboardEntries[leaderboardEntries.Count - 1].gameObject);
			leaderboardEntries.RemoveAt(leaderboardEntries.Count - 1);
		}
	}
}
public class LeaderboardEntry : MonoBehaviour
{
	[SerializeField]
	private TextMeshProUGUI rankText;

	[SerializeField]
	private TextMeshProUGUI playerNameText;

	[SerializeField]
	private TextMeshProUGUI timeText;

	public void Setup(int rank, string playerName, string timeText)
	{
		rankText.text = "#" + rank;
		playerNameText.text = playerName;
		this.timeText.text = timeText;
	}
}
public class LeaderboardManager : MonoBehaviour
{
	private const double MAX_SPEEDUP = 256.0;

	[SerializeField]
	private GameObject overlay;

	[SerializeField]
	private TextMeshProUGUI timeText;

	[SerializeField]
	private GameObject leftButton;

	[SerializeField]
	private GameObject rightButton;

	[SerializeField]
	private GameObject leaderboardScreen;

	[SerializeField]
	private Leaderboard leaderboard;

	[SerializeField]
	private TextMeshProUGUI finishTimeText;

	[SerializeField]
	private GameObject runCancelled;

	[SerializeField]
	private TextMeshProUGUI leaderboardTitle;

	[SerializeField]
	private TextMeshProUGUI averageText;

	public bool IsRunning => overlay.activeInHierarchy;

	public bool IsLeaderBoardScreenOpen => leaderboardScreen.activeInHierarchy;

	private void Update()
	{
		if (IsRunning)
		{
			timeText.text = StringFromTimeSpan(MainSim.Inst.GetCurrentTime().ToTimeSpan());
			if (MainSim.Inst.numLeaderboardRuns > 0)
			{
				int numLeaderboardRuns = MainSim.Inst.numLeaderboardRuns;
				TimeSpan timeSpan = MainSim.Inst.totalLeaderboardTime.ToTimeSpan();
				double num = timeSpan / TimeSpan.FromHours(2.0) * 100.0;
				averageText.text = string.Format(Localizer.Localize("average_text"), numLeaderboardRuns, StringFromTimeSpan(timeSpan / numLeaderboardRuns), num);
			}
			else
			{
				averageText.text = string.Format(Localizer.Localize("average_text2"), 0, "");
			}
		}
	}

	public void StartLeaderboardRun(bool showAverageText)
	{
		overlay.SetActive(value: true);
		averageText.gameObject.SetActive(showAverageText);
	}

	public void RemoveOverlay()
	{
		overlay.SetActive(value: false);
	}

	public void StopLeaderboardRun(bool finished, string leaderboardName, string steamLeaderboardName, TimeSpan timeSpan)
	{
		overlay.SetActive(value: false);
		MainSim.Inst.workspace.gameObject.SetActive(value: false);
		leaderboardScreen.SetActive(value: true);
		leaderboardTitle.text = CodeUtilities.ToUpperSnake(leaderboardName);
		finishTimeText.text = StringFromTimeSpan(timeSpan);
		int score = (int)timeSpan.TotalMilliseconds;
		if (!finished || timeSpan.TotalMilliseconds > 2147483647.0)
		{
			runCancelled.SetActive(value: true);
			score = 0;
		}
		else
		{
			runCancelled.SetActive(value: false);
		}
		leaderboard.FillLeaderboard(steamLeaderboardName, score);
		if (finished)
		{
			Achievements.UnlockAchievement("COMPETITIVE_FARMING");
			if (leaderboardName == "fastest_reset")
			{
				Achievements.UnlockAchievement("FULL_AUTOMATION");
			}
		}
	}

	public void SpeedUp()
	{
		if (MainSim.Inst.TimeFactor <= 128.0)
		{
			MainSim.Inst.TimeFactor *= 2.0;
		}
	}

	public void SlowDown()
	{
		if (MainSim.Inst.TimeFactor >= 2.0)
		{
			MainSim.Inst.TimeFactor /= 2.0;
		}
		rightButton.SetActive(MainSim.Inst.TimeFactor <= 128.0);
		leftButton.SetActive(MainSim.Inst.TimeFactor >= 2.0);
	}

	public void OkPressed()
	{
		MainSim.Inst.workspace.gameObject.SetActive(value: true);
		leaderboardScreen.SetActive(value: false);
		MainSim.Inst.RestoreMainSim();
	}

	public static string StringFromTimeSpan(TimeSpan t)
	{
		return string.Format("{0}{1}", ((int)t.TotalHours > 0) ? ((int)t.TotalHours + ":") : "", t.ToString("mm\\:ss\\.fff"));
	}
}
public class MarkdownText : MonoBehaviour, IPointerMoveHandler, IEventSystemHandler, IPointerExitHandler
{
	private enum SectionType
	{
		Text,
		Image,
		Custom
	}

	private struct TextSection
	{
		public SectionType type;

		public string text;

		public bool isSpoiler;

		public string spoilerText;

		public TextSection(SectionType type, string text, bool isSpoiler, string spoilerText = null)
		{
			this.type = type;
			this.text = text;
			this.isSpoiler = isSpoiler;
			this.spoilerText = spoilerText;
		}
	}

	private struct HoverInfo
	{
		public CodeInputField inputField;

		public string linkID;

		public int startIndex;
	}

	[SerializeField]
	private SpoilerWarning spoilerWarning;

	[SerializeField]
	private CodeInputField textPrefab;

	[SerializeField]
	private Image imgPrefab;

	[SerializeField]
	private OutputText outputPrefab;

	[SerializeField]
	private Inventory invPrefab;

	private List<CodeInputField> textFields = new List<CodeInputField>();

	private Action<string> clickLinkCallback;

	private HoverInfo hoverInfo;

	private string ChangeColorBeforeIndex(string text, string color, int index)
	{
		int num = index;
		while (num > 0 && text[num] != '#')
		{
			num--;
		}
		return text.Remove(num, 9).Insert(num, color);
	}

	public void OnPointerMove(PointerEventData eventData)
	{
		HoverInfo hoverInfo = default(HoverInfo);
		foreach (CodeInputField textField in textFields)
		{
			int num = TMP_TextUtilities.FindIntersectingLink(textField.textComponent, Input.mousePosition, MainSim.Inst.workspace.uiCam);
			if (num >= 0)
			{
				TMP_LinkInfo tMP_LinkInfo = textField.textComponent.textInfo.linkInfo[num];
				hoverInfo.startIndex = tMP_LinkInfo.linkIdFirstCharacterIndex;
				hoverInfo.inputField = textField;
				hoverInfo.linkID = tMP_LinkInfo.GetLinkID();
				break;
			}
		}
		if (hoverInfo.startIndex != this.hoverInfo.startIndex)
		{
			ColorTheme theme = ThemeManager.Inst.Theme;
			if (this.hoverInfo.linkID != null)
			{
				this.hoverInfo.inputField.text = ChangeColorBeforeIndex(this.hoverInfo.inputField.text, theme.docs.link, this.hoverInfo.startIndex);
			}
			this.hoverInfo = hoverInfo;
			if (this.hoverInfo.linkID != null)
			{
				this.hoverInfo.inputField.text = ChangeColorBeforeIndex(this.hoverInfo.inputField.text, theme.docs.link_hover, this.hoverInfo.startIndex);
			}
		}
	}

	public void OnPointerExit(PointerEventData eventData)
	{
		hoverInfo = default(HoverInfo);
	}

	public void Update()
	{
		if (!string.IsNullOrEmpty(hoverInfo.linkID) && Input.GetKeyDown(KeyCode.Mouse0))
		{
			clickLinkCallback(hoverInfo.linkID);
		}
	}

	public int UpdateSearch(string searchTerm, int occurenceIndex)
	{
		int count = 0;
		foreach (CodeInputField textField in textFields)
		{
			if (string.IsNullOrEmpty(searchTerm))
			{
				textField.text = CodeUtilities.RemoveMarks(textField.text);
			}
			else
			{
				textField.text = CodeUtilities.MarkSearch(CodeUtilities.RemoveMarks(textField.text), searchTerm, occurenceIndex, ref count);
			}
		}
		return count;
	}

	public void Setup(string text, Action<string> clickLinkCallback)
	{
		this.clickLinkCallback = clickLinkCallback;
		ColorTheme theme = ThemeManager.Inst.Theme;
		List<Func<TextSection, IEnumerable<TextSection>>> obj = new List<Func<TextSection, IEnumerable<TextSection>>>
		{
			InsertCustomTexts,
			(TextSection section) => Enumerable.Repeat(new TextSection(section.type, CodeUtilities.ApplyCodeTags(section.text), section.isSpoiler), 1),
			ApplyHeadings,
			ApplyLinks,
			ApplyUnlocks,
			ApplySpoilers,
			ApplyImages,
			InsertCustomSections
		};
		IEnumerable<TextSection> enumerable = Enumerable.Repeat(new TextSection(SectionType.Text, text, isSpoiler: false), 1);
		foreach (Func<TextSection, IEnumerable<TextSection>> stage in obj)
		{
			enumerable = enumerable.SelectMany((TextSection section) => (section.type != SectionType.Text) ? Enumerable.Repeat(section, 1) : stage(section));
		}
		foreach (TextSection item in enumerable)
		{
			if (string.IsNullOrEmpty(item.text))
			{
				continue;
			}
			switch (item.type)
			{
			case SectionType.Text:
			{
				CodeInputField codeInputField = UnityEngine.Object.Instantiate(textPrefab, base.transform);
				theme.docs.text.ApplyTo(codeInputField);
				codeInputField.text = item.text;
				if (item.isSpoiler)
				{
					UnityEngine.Object.Instantiate(spoilerWarning, codeInputField.transform).SetText(item.spoilerText);
				}
				textFields.Add(codeInputField);
				break;
			}
			case SectionType.Image:
			{
				Image image = UnityEngine.Object.Instantiate(imgPrefab, base.transform);
				int num = item.text.Length;
				while (char.IsDigit(item.text[num - 1]))
				{
					num--;
				}
				string text2 = item.text.Substring(0, num);
				if (int.TryParse(item.text.Substring(num), out var result))
				{
					image.GetComponent<LayoutElement>().preferredHeight = result;
					image.sprite = ResourceManager.GetSprite(text2);
				}
				break;
			}
			case SectionType.Custom:
				if (item.text == "output")
				{
					OutputText outputText = UnityEngine.Object.Instantiate(outputPrefab, base.transform);
					theme.docs.text.ApplyTo(outputText.Text);
				}
				else
				{
					if (!item.text.StartsWith("itemblock"))
					{
						break;
					}
					string[] array = item.text.Split(' ');
					Func<ItemBlock> up;
					if (array[1] == "stats_sum")
					{
						up = delegate
						{
							if (!MainSim.Inst.MightBeSimulating())
							{
								Achievements.UpdateSum(MainSim.Inst.GetCurrentTime());
							}
							return Achievements.GetSum();
						};
					}
					else if (array[1] == "stats_best")
					{
						up = Achievements.GetBest;
					}
					else if (!(array[1] == "cost"))
					{
						up = ((!(array[1] == "tooltip")) ? ((Func<ItemBlock>)(() => (ItemBlock)null)) : ((Func<ItemBlock>)(() => MainSim.Inst.workspace.tooltip.Info?.itemBlock)));
					}
					else if (array[2] == "object")
					{
						FarmObjectSO fo = ResourceManager.GetFarmObject(array[3]);
						ItemBlock cost = fo.cost;
						int upgradeCount = Mathf.Max(0, MainSim.Inst.NumUnlocked(fo.yieldUpgradeName) - 1);
						up = () => cost * ((!(fo.yieldUpgradeName != "")) ? 1 : Mathf.Max(1, 1 << upgradeCount));
					}
					else if (array[2] == "unlock")
					{
						UnlockSO unlockSO = ResourceManager.GetUnlock(array[3]);
						up = ((unlockSO != null) ? ((Func<ItemBlock>)(() => MainSim.Inst.GetUnlockCost(unlockSO))) : ((Func<ItemBlock>)(() => (ItemBlock)null)));
					}
					else
					{
						up = () => (ItemBlock)null;
					}
					UnityEngine.Object.Instantiate(invPrefab, base.transform).SetUp(up);
				}
				break;
			}
		}
	}

	public void UpdateText(string text)
	{
		for (int num = base.transform.childCount - 1; num >= 0; num--)
		{
			UnityEngine.Object.Destroy(base.transform.GetChild(num).gameObject);
		}
		textFields.Clear();
		Setup(text, clickLinkCallback);
	}

	private IEnumerable<TextSection> ApplyHeadings(TextSection section)
	{
		Regex regex = new Regex("(?<=^|\\r\\n|\\n)#+ .*");
		StringBuilder stringBuilder = new StringBuilder(section.text);
		foreach (Match item in regex.Matches(section.text).Reverse())
		{
			Capture capture = item.Captures.First();
			stringBuilder.Remove(capture.Index, capture.Length);
			int num = capture.Value.IndexOf('#');
			int num2 = 40;
			while (capture.Value[num + 1] == '#')
			{
				num++;
				num2 -= 8;
			}
			string arg = capture.Value.Substring(num + 2);
			string value = $"<line-height=50%><size={num2}px>{arg}</size>\n</line-height>";
			stringBuilder.Insert(capture.Index, value);
		}
		section.text = stringBuilder.ToString();
		return Enumerable.Repeat(section, 1);
	}

	private IEnumerable<TextSection> ApplyLinks(TextSection section)
	{
		ColorTheme theme = ThemeManager.Inst.Theme;
		Regex regex = new Regex("(?<!!)\\[.*?\\]\\(.*?\\)");
		StringBuilder stringBuilder = new StringBuilder(section.text);
		foreach (Match item in regex.Matches(section.text).Reverse())
		{
			Capture capture = item.Captures.First();
			int num = capture.Value.IndexOf(']');
			string arg = capture.Value.Substring(1, num - 1);
			string arg2 = capture.Value.Substring(num + 2, capture.Value.Length - (num + 2) - 1);
			stringBuilder.Remove(capture.Index, capture.Length);
			string value = $"<font=\"FiraCode-Regular SDF\"><color={theme.docs.link}><u><link=\"{arg2}\">{arg}</link></u></color></font>";
			stringBuilder.Insert(capture.Index, value);
		}
		section.text = stringBuilder.ToString();
		return Enumerable.Repeat(section, 1);
	}

	private IEnumerable<TextSection> ApplyUnlocks(TextSection section)
	{
		IEnumerable<string> enumerable = from m in new Regex("<unlock=.*?>").Matches(section.text)
			select m.Captures.First().Value.Substring(8, m.Captures.First().Value.Length - 9);
		string[] array = new Regex("</?unlock=?.*?>").Split(section.text);
		StringBuilder stringBuilder = new StringBuilder();
		bool flag = false;
		IEnumerator<string> enumerator = enumerable.GetEnumerator();
		string[] array2 = array;
		foreach (string value in array2)
		{
			if (flag)
			{
				enumerator.MoveNext();
				if (MainSim.Inst.IsUnlocked(enumerator.Current))
				{
					stringBuilder.Append(value);
				}
			}
			else
			{
				stringBuilder.Append(value);
			}
			flag = !flag;
		}
		section.text = stringBuilder.ToString();
		return Enumerable.Repeat(section, 1);
	}

	private IEnumerable<TextSection> ApplySpoilers(TextSection section)
	{
		IEnumerable<string> enumerable = from m in new Regex("<spoiler=.*?>").Matches(section.text)
			select m.Captures.First().Value.Substring(9, m.Captures.First().Value.Length - 10);
		string[] array = new Regex("</?spoiler=?.*?>").Split(section.text);
		List<TextSection> list = new List<TextSection>();
		bool flag = false;
		IEnumerator<string> enumerator = enumerable.GetEnumerator();
		string[] array2 = array;
		foreach (string text in array2)
		{
			if (flag)
			{
				enumerator.MoveNext();
				list.Add(new TextSection(SectionType.Text, text, isSpoiler: true, enumerator.Current));
			}
			else
			{
				list.Add(new TextSection(SectionType.Text, text, isSpoiler: false));
			}
			flag = !flag;
		}
		return list;
	}

	private IEnumerable<TextSection> ApplyImages(TextSection section)
	{
		Regex regex = new Regex("!\\[.*?\\]\\(.*?\\)");
		List<TextSection> list = (from s in regex.Split(section.text)
			select new TextSection(SectionType.Text, s, section.isSpoiler, section.spoilerText)).ToList();
		int num = 1;
		foreach (Match item2 in regex.Matches(section.text))
		{
			Capture capture = item2.Captures.First();
			int num2 = capture.Value.IndexOf(']');
			string text = capture.Value.Substring(num2 + 2, capture.Value.Length - (num2 + 2) - 1);
			TextSection item = new TextSection(SectionType.Image, text, section.isSpoiler, section.spoilerText);
			list.Insert(num, item);
			num += 2;
		}
		return list;
	}

	private IEnumerable<TextSection> InsertCustomTexts(TextSection section)
	{
		Regex regex = new Regex("{{.*}}");
		StringBuilder stringBuilder = new StringBuilder(section.text);
		foreach (Match item in regex.Matches(section.text).Reverse())
		{
			Capture capture = item.Captures.First();
			string text = capture.Value.Substring(2, capture.Value.Length - 4);
			stringBuilder.Remove(capture.Index, capture.Length);
			string value = capture.Value;
			switch (text)
			{
			case "unlocksTOC":
				value = GenerateUnlockTOC();
				break;
			case "builtinsTOC":
				value = GenerateBuiltinsTOC();
				break;
			case "itemsTOC":
				value = GenerateItemsTOC();
				break;
			case "entitiesTOC":
				value = GenerateEntitiesTOC();
				break;
			case "groundsTOC":
				value = GenerateGroundsTOC();
				break;
			default:
				if (text.StartsWith("@"))
				{
					value = Localizer.Localize(text.Substring(1));
				}
				break;
			}
			stringBuilder.Insert(capture.Index, value);
		}
		section.text = stringBuilder.ToString();
		return Enumerable.Repeat(section, 1);
	}

	private IEnumerable<TextSection> InsertCustomSections(TextSection section)
	{
		Regex regex = new Regex("{{.*}}");
		List<TextSection> list = (from s in regex.Split(section.text)
			select new TextSection(SectionType.Text, s, section.isSpoiler, section.spoilerText)).ToList();
		int num = 1;
		foreach (Match item2 in regex.Matches(section.text))
		{
			Capture capture = item2.Captures.First();
			string text = capture.Value.Substring(2, capture.Value.Length - 4);
			TextSection item = new TextSection(SectionType.Custom, text, section.isSpoiler, section.spoilerText);
			list.Insert(num, item);
			num += 2;
		}
		return list;
	}

	private string GenerateUnlockTOC()
	{
		IOrderedEnumerable<(string, string, string)> orderedEnumerable = from s in (from unlock in ResourceManager.GetAllUnlocks()
				where unlock.enabled
				select unlock).Select(delegate(UnlockSO unlock)
			{
				string text = unlock.docs;
				if (string.IsNullOrEmpty(text))
				{
					text = "unlocks/" + unlock.unlockName;
				}
				return (unlock.name, unlock.name, docLink: text);
			}).Append(("for", "expand_2", "docs/unlocks/expand_2.md"))
			orderby s.Item2
			select s;
		StringBuilder stringBuilder = new StringBuilder();
		foreach (var item in orderedEnumerable)
		{
			string value = $"<unlock={item.Item1}>[{Localizer.Localize(item.Item2)}]({item.Item3})      </unlock>";
			stringBuilder.Append(value);
		}
		return stringBuilder.ToString();
	}

	private string GenerateBuiltinsTOC()
	{
		StringBuilder stringBuilder = new StringBuilder();
		foreach (string item in BuiltinFunctions.Functions.Keys.OrderBy((string s) => s))
		{
			string value = string.Format("<unlock={0}>[{0}](functions/{0})      </unlock>", item);
			stringBuilder.Append(value);
		}
		return stringBuilder.ToString();
	}

	private string GenerateItemsTOC()
	{
		StringBuilder stringBuilder = new StringBuilder();
		foreach (ItemSO item in from i in ResourceManager.GetAllItems()
			where i.enabled
			select i)
		{
			string value = $"<unlock={item.itemName}>[{CodeUtilities.ToUpperSnake(item.itemName)}](items/{item.itemName})      </unlock>";
			stringBuilder.Append(value);
		}
		return stringBuilder.ToString();
	}

	private string GenerateEntitiesTOC()
	{
		StringBuilder stringBuilder = new StringBuilder();
		foreach (FarmObjectSO item in from f in ResourceManager.GetAllFarmObjects()
			where !f.isGround
			select f)
		{
			string value = $"<unlock={item.objectName}>[{CodeUtilities.ToUpperSnake(item.objectName)}](objects/{item.objectName})      </unlock>";
			stringBuilder.Append(value);
		}
		return stringBuilder.ToString();
	}

	private string GenerateGroundsTOC()
	{
		StringBuilder stringBuilder = new StringBuilder();
		foreach (FarmObjectSO item in from f in ResourceManager.GetAllFarmObjects()
			where f.isGround
			select f)
		{
			string value = $"<unlock={item.objectName}>[{CodeUtilities.ToUpperSnake(item.objectName)}](objects/{item.objectName})      </unlock>";
			stringBuilder.Append(value);
		}
		return stringBuilder.ToString();
	}
}
public class Menu : MonoBehaviour
{
	[SerializeField]
	private GameObject menu;

	[SerializeField]
	private GameObject[] uiCanvases;

	[SerializeField]
	private GameObject titlePage;

	[SerializeField]
	private SaveChooser saveChooser;

	[SerializeField]
	private OptionMenu options;

	[SerializeField]
	private ColoredButton saveButton;

	private void Start()
	{
		ResourceManager.LoadAll();
		Achievements.LoadStats();
		string text = OptionHolder.GetString("activeSave", "Save0");
		LoadSave(text);
		try
		{
			Saver.Load(MainSim.Inst);
		}
		catch (IOException message)
		{
			UnityEngine.Debug.LogError(message);
			List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
			{
				new WarningPopup.ButtonData("ok", MainSim.Inst.warningPopup.Close)
			};
			MainSim.Inst.warningPopup.ShowPopup(CodeUtilities.LocalizeAndFormat("popup_warning_failed_read_save", text), buttonsToAdd);
		}
		catch (ArgumentException message2)
		{
			UnityEngine.Debug.LogError(message2);
			List<WarningPopup.ButtonData> buttonsToAdd2 = new List<WarningPopup.ButtonData>
			{
				new WarningPopup.ButtonData("ok", delegate
				{
					MainSim.Inst.warningPopup.Close();
					MainSim.Inst.workspace.AddNewDocsWindow("docs/backup.md");
					Play();
				})
			};
			MainSim.Inst.warningPopup.ShowPopup(CodeUtilities.LocalizeAndFormat("popup_warning_corrupted_save", text), buttonsToAdd2);
		}
		Open();
		RestartAutosave("autosave");
		RestartAutosave("autosave progress");
		OptionHolder.OnOptionChanged -= RestartAutosave;
		OptionHolder.OnOptionChanged += RestartAutosave;
	}

	private void RestartAutosave(string optionName)
	{
		if (optionName == "autosave")
		{
			TimerManager.StopTimer(AutosaveCode);
			if (OptionHolder.GetString("autosave") == "enabled")
			{
				TimerManager.StartTimer(AutosaveCode, 30.0, loop: true);
			}
		}
		else if (optionName == "autosave progress")
		{
			TimerManager.StopTimer(AutosaveProgress);
			if (OptionHolder.GetString("autosave progress") == "enabled")
			{
				TimerManager.StartTimer(AutosaveProgress, 30.0, loop: true);
			}
		}
	}

	private void AutosaveProgress()
	{
		Saver.SaveProgress(MainSim.Inst);
	}

	private void AutosaveCode()
	{
		Saver.SaveCode(MainSim.Inst);
	}

	public void LoadSave(string saveName)
	{
		if (OptionHolder.GetString("activeSave", "Save0") != saveName)
		{
			OptionHolder.SetOption("activeSave", saveName);
		}
	}

	public void Play()
	{
		MainSim.Inst.workspace.gameObject.SetActive(value: true);
		GameObject[] array = uiCanvases;
		for (int i = 0; i < array.Length; i++)
		{
			array[i].SetActive(value: true);
		}
		menu.gameObject.SetActive(value: false);
		FMODSoundManager.CloseMenu();
	}

	public void ChooseSave()
	{
		titlePage.gameObject.SetActive(value: false);
		saveChooser.gameObject.SetActive(value: true);
		saveChooser.Setup();
	}

	public void PressSaveButton()
	{
		TimerManager.StartTimer(ReleaseSaveButton, 1.0);
		saveButton.Interactable = false;
		saveButton.Text = Localizer.Localize("saved");
		Saver.Save(MainSim.Inst);
	}

	private void ReleaseSaveButton()
	{
		saveButton.Interactable = true;
		saveButton.Text = Localizer.Localize("save");
	}

	public void Open()
	{
		MainSim.Inst.workspace.gameObject.SetActive(value: false);
		GameObject[] array = uiCanvases;
		for (int i = 0; i < array.Length; i++)
		{
			array[i].gameObject.SetActive(value: false);
		}
		menu.gameObject.SetActive(value: true);
		titlePage.gameObject.SetActive(value: true);
		saveChooser.gameObject.SetActive(value: false);
		options.gameObject.SetActive(value: false);
	}

	public void Options()
	{
		titlePage.gameObject.SetActive(value: false);
		options.gameObject.SetActive(value: true);
		options.Setup();
	}

	public void Quit()
	{
		if (MainSim.Inst.dirty)
		{
			List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
			{
				new WarningPopup.ButtonData("save", delegate
				{
					Saver.Save(MainSim.Inst);
					Application.Quit();
				}),
				new WarningPopup.ButtonData("don't save", Application.Quit)
			};
			MainSim.Inst.warningPopup.ShowPopup("popup_warning_exit_game", buttonsToAdd);
		}
		else
		{
			Application.Quit();
		}
	}

	public void JoinDiscord()
	{
		Application.OpenURL("https://discord.com/invite/kj33cJkeJn");
	}
}
public class OptionMenu : MonoBehaviour
{
	[SerializeField]
	private ColoredButton coloredButtonPrefab;

	[SerializeField]
	private Image background;

	[SerializeField]
	private RectTransform optionContainer;

	[SerializeField]
	private RectTransform tabsContainer;

	private IEnumerable<OptionSO> allOptions;

	private Dictionary<string, ColoredButton> categoryButtons;

	private string currentCategory;

	private Dictionary<string, OptionUI> optionUIs = new Dictionary<string, OptionUI>();

	public void Setup()
	{
		if (categoryButtons != null)
		{
			return;
		}
		allOptions = from o in ResourceManager.GetAllOptions()
			orderby o.importance descending
			select o;
		if (allOptions.Count() == 0)
		{
			return;
		}
		IEnumerable<string> enumerable = allOptions.Select((OptionSO o) => o.category).Distinct();
		currentCategory = enumerable.First();
		categoryButtons = new Dictionary<string, ColoredButton>();
		foreach (string category in enumerable)
		{
			ColoredButton coloredButton = UnityEngine.Object.Instantiate(coloredButtonPrefab, tabsContainer);
			coloredButton.Text = category;
			coloredButton.GetComponent<Button>().onClick.AddListener(delegate
			{
				ChangeCategory(category);
			});
			categoryButtons[category] = coloredButton;
		}
		ChangeCategory(currentCategory);
		OptionHolder.OnOptionChanged += OnOptionChanged;
	}

	private void ChangeCategory(string newCategory)
	{
		categoryButtons[currentCategory].Interactable = true;
		currentCategory = newCategory;
		categoryButtons[newCategory].Interactable = false;
		for (int num = optionContainer.childCount - 1; num >= 0; num--)
		{
			UnityEngine.Object.Destroy(optionContainer.GetChild(num).gameObject);
		}
		optionUIs.Clear();
		foreach (OptionSO item in allOptions.Where((OptionSO o) => o.category == currentCategory))
		{
			OptionUI optionUI = UnityEngine.Object.Instantiate(item.optionUI, optionContainer);
			optionUI.Setup(item);
			optionUIs[item.name] = optionUI;
		}
	}

	private void OnOptionChanged(string optionName)
	{
		if (optionUIs.TryGetValue(optionName, out var value))
		{
			value.UpdateValue();
		}
	}

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		background.color = theme.ui.OptionsMenuColor;
	}
}
public class SaveChooser : MonoBehaviour
{
	[SerializeField]
	private SaveOption saveOptionPrefab;

	[SerializeField]
	private Image background;

	[SerializeField]
	private Transform content;

	[SerializeField]
	private Menu menu;

	private Dictionary<string, SaveOption> openOptions = new Dictionary<string, SaveOption>();

	public void Setup()
	{
		foreach (SaveOption value in openOptions.Values)
		{
			UnityEngine.Object.Destroy(value.gameObject);
		}
		foreach (string item in from d in Directory.GetDirectories(Helper.persistentDataPath + "/Saves")
			select new DirectoryInfo(d).Name)
		{
			AddOption(item);
		}
	}

	private void AddOption(string saveName)
	{
		SaveOption saveOption = UnityEngine.Object.Instantiate(saveOptionPrefab, content);
		openOptions[saveName] = saveOption;
		saveOption.Setup(saveName, this);
	}

	public void DeleteSave(string saveName)
	{
		if (!openOptions.ContainsKey(saveName))
		{
			throw new Exception("tried to delete save that doesn't exist");
		}
		string text = string.Format(Localizer.Localize("popup_warning_delete_save"), saveName);
		List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
		{
			new WarningPopup.ButtonData("delete", delegate
			{
				if (Saver.DeleteSave(saveName))
				{
					UnityEngine.Object.Destroy(openOptions[saveName].gameObject);
					openOptions.Remove(saveName);
				}
				MainSim.Inst.warningPopup.Close();
			}),
			new WarningPopup.ButtonData("cancel", MainSim.Inst.warningPopup.Close)
		};
		MainSim.Inst.warningPopup.ShowPopup(text, buttonsToAdd);
	}

	public void LoadSave(string saveName)
	{
		if (MainSim.Inst.dirty)
		{
			List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
			{
				new WarningPopup.ButtonData("save", delegate
				{
					Saver.StopFileWatcher();
					Saver.Save(MainSim.Inst);
					menu.LoadSave(saveName);
					SceneManager.LoadScene(0);
				}),
				new WarningPopup.ButtonData("don't save", delegate
				{
					Saver.StopFileWatcher();
					menu.LoadSave(saveName);
					SceneManager.LoadScene(0);
				})
			};
			MainSim.Inst.warningPopup.ShowPopup("popup_warning_load_game", buttonsToAdd);
		}
		else
		{
			Saver.StopFileWatcher();
			menu.LoadSave(saveName);
			SceneManager.LoadScene(0);
		}
	}

	public bool RenameSave(string saveName, string newSaveName)
	{
		if (!Saver.RenameSave(saveName, newSaveName))
		{
			return false;
		}
		openOptions[newSaveName] = openOptions[saveName];
		openOptions.Remove(saveName);
		if (OptionHolder.GetString("activeSave", "Save0") == saveName)
		{
			menu.LoadSave(newSaveName);
		}
		return true;
	}

	public void CreateNewSave()
	{
		string text = GenerateUnusedSaveName();
		Saver.CreateNewSaveGame(text);
		AddOption(text);
		openOptions[text].Edit();
	}

	public void OpenFolder()
	{
		Process.Start(Helper.persistentDataPath);
	}

	public static string GenerateUnusedSaveName()
	{
		int num = 0;
		string text;
		do
		{
			text = $"Save{num}";
			num++;
		}
		while (File.Exists(Saver.GetPathOfSaveFile(text)));
		return text;
	}

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		background.color = theme.ui.OptionsMenuColor;
	}
}
public class SaveOption : MonoBehaviour
{
	private const int MAX_NAME_SIZE = 20;

	[SerializeField]
	private TextMeshProUGUI nameText;

	[SerializeField]
	private TMP_InputField nameEditInput;

	private string fileName;

	private SaveChooser saveChooser;

	public void Setup(string fileName, SaveChooser saveChooser)
	{
		this.fileName = fileName;
		this.saveChooser = saveChooser;
		nameText.text = fileName;
	}

	public void Load()
	{
		saveChooser.LoadSave(fileName);
	}

	public void Delete()
	{
		saveChooser.DeleteSave(fileName);
	}

	public void Edit()
	{
		nameEditInput.gameObject.SetActive(value: true);
		nameText.gameObject.SetActive(value: false);
		nameEditInput.text = fileName;
		nameEditInput.Select();
	}

	public void EditFinished()
	{
		string text = nameEditInput.text;
		if (saveChooser.RenameSave(fileName, text))
		{
			fileName = text;
			nameText.text = text;
		}
		nameEditInput.gameObject.SetActive(value: false);
		nameText.gameObject.SetActive(value: true);
	}

	public void NameChanged()
	{
		string text = nameEditInput.text;
		if (text.Length > 20)
		{
			nameEditInput.text = text.Substring(0, 20);
		}
	}

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	protected virtual void OnThemeChanged(ColorTheme theme)
	{
		if (TryGetComponent<Image>(out var component))
		{
			component.color = theme.ui.OptionBackgroundColor;
		}
		nameText.color = theme.ui.OptionTextColor;
		theme.ui.text.ApplyTo(nameEditInput);
	}
}
[RequireComponent(typeof(CodeInputField))]
public class OutputText : MonoBehaviour
{
	private bool dirty;

	private CodeInputField txt;

	public CodeInputField Text
	{
		get
		{
			if (txt == null)
			{
				TryGetComponent<CodeInputField>(out txt);
			}
			return txt;
		}
	}

	private void Update()
	{
		if (dirty)
		{
			txt.text = Logger.GetOutputString();
			dirty = false;
		}
	}

	private void Start()
	{
		dirty = true;
		Logger.OnOutputChanged += OutputChanged;
	}

	private void OnDestroy()
	{
		Logger.OnOutputChanged -= OutputChanged;
	}

	private void OutputChanged()
	{
		dirty = true;
	}
}
public class ResearchMenu : MonoBehaviour
{
	private class UnlockLayout
	{
		public int xOffset;

		public List<UnlockLayout> children;

		public UnlockBox box;

		public bool CollidesWith(UnlockLayout sibling)
		{
			HashSet<Vector2Int> hashSet = new HashSet<Vector2Int>();
			FillTakenSet(hashSet);
			HashSet<Vector2Int> hashSet2 = new HashSet<Vector2Int>();
			sibling.FillTakenSet(hashSet2);
			hashSet.IntersectWith(hashSet2);
			return hashSet.Count > 0;
		}

		private void FillTakenSet(HashSet<Vector2Int> taken, Vector2Int totalOffset = default(Vector2Int))
		{
			taken.Add(totalOffset + new Vector2Int(xOffset, 0));
			taken.Add(totalOffset + new Vector2Int(xOffset + 1, 0));
			foreach (UnlockLayout child in children)
			{
				child.FillTakenSet(taken, totalOffset + new Vector2Int(xOffset, -1));
			}
		}

		public int GetWidth()
		{
			return GetMaxXOffset() - GetMinXOffset();
		}

		private int GetMaxXOffset()
		{
			if (children.Count == 0)
			{
				return xOffset;
			}
			return children.Max((UnlockLayout x) => x.GetMaxXOffset()) + xOffset;
		}

		private int GetMinXOffset()
		{
			if (children.Count == 0)
			{
				return xOffset;
			}
			return children.Min((UnlockLayout x) => x.GetMinXOffset()) + xOffset;
		}

		public void SetUIPositions(float horizontalSpacing, float verticalSpacing, Vector2 startPosition, ref Rect boundary)
		{
			Vector2 vector = startPosition + new Vector2((float)xOffset * horizontalSpacing, 0f);
			((RectTransform)box.transform).anchoredPosition = vector;
			foreach (UnlockLayout child in children)
			{
				child.SetUIPositions(horizontalSpacing, verticalSpacing, startPosition + new Vector2((float)xOffset * horizontalSpacing, 0f - verticalSpacing), ref boundary);
			}
			boundary.min = Vector2.Min(boundary.min, vector);
			boundary.max = Vector2.Max(boundary.max, vector);
		}
	}

	[SerializeField]
	private RectTransform container;

	[SerializeField]
	private Image background;

	[SerializeField]
	private ColoredButton openCloseButton;

	[SerializeField]
	private GameObject plusButton;

	[SerializeField]
	private GameObject infoButton;

	[SerializeField]
	private GameObject farmIcon;

	[SerializeField]
	private GameObject unlockIcon;

	[SerializeField]
	private ScrollRect scrollRect;

	[SerializeField]
	private UnlockBox researchPrefab;

	[SerializeField]
	private RectTransform linePrefab;

	[SerializeField]
	private float horizontalSpacing;

	[SerializeField]
	private float verticalSpacing;

	[SerializeField]
	private float paddingVertical;

	[SerializeField]
	private float paddingHorizontal;

	[SerializeField]
	private float zoomSpeed = 1.1f;

	[SerializeField]
	private float maxZoomScale = 2f;

	[SerializeField]
	private float minZoomScale = 0.1f;

	private Dictionary<string, UnlockBox> allBoxes = new Dictionary<string, UnlockBox>();

	private List<UnlockBox> rootUnlocks = new List<UnlockBox>();

	public HashSet<string> openedUnlockDocs = new HashSet<string>();

	public bool IsOpen => base.transform.GetChild(0).gameObject.activeInHierarchy;

	private void Start()
	{
		SetViewportOptions("viewport sliding");
		OptionHolder.OnOptionChanged += SetViewportOptions;
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDestroy()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		background.color = theme.unlocks.BackgroundColor;
	}

	private void Update()
	{
		ItemBlock inventory = MainSim.Inst.GetInventory();
		Dictionary<string, int> unlocks = MainSim.Inst.GetUnlocks();
		bool flag = true;
		foreach (UnlockBox rootUnlock in rootUnlocks)
		{
			rootUnlock.SetupRec(unlockable: true, openedUnlockDocs, inventory, unlocks, out var allUnlocked);
			flag = flag && allUnlocked;
		}
		if (!MainSim.Inst.leaderboardManager.IsRunning && flag && !MainSim.Inst.MightBeSimulating())
		{
			Achievements.UnlockAchievement("UNLOCK_EVERYTHING");
		}
	}

	private void SetViewportOptions(string option)
	{
		if (option == "viewport sliding")
		{
			scrollRect.inertia = OptionHolder.GetString("viewport sliding") == "enabled";
		}
	}

	public void Setup()
	{
		for (int num = container.childCount - 1; num >= 0; num--)
		{
			UnityEngine.Object.Destroy(container.GetChild(num).gameObject);
		}
		allBoxes.Clear();
		rootUnlocks.Clear();
		foreach (UnlockSO allUnlock in ResourceManager.GetAllUnlocks())
		{
			if (allUnlock.enabled)
			{
				UnlockBox unlockBox = UnityEngine.Object.Instantiate(researchPrefab, container);
				unlockBox.unlockSO = allUnlock;
				if (string.IsNullOrEmpty(allUnlock.parentUnlock))
				{
					rootUnlocks.Add(unlockBox);
				}
				allBoxes[allUnlock.unlockName] = unlockBox;
			}
		}
		foreach (UnlockBox value in allBoxes.Values)
		{
			if (!string.IsNullOrEmpty(value.unlockSO.parentUnlock) && allBoxes.ContainsKey(value.unlockSO.parentUnlock))
			{
				allBoxes[value.unlockSO.parentUnlock].children.Add(value);
			}
		}
		UnlockLayout layout = GetLayout(rootUnlocks[0]);
		Rect boundary = default(Rect);
		layout.SetUIPositions(horizontalSpacing, verticalSpacing, new Vector2(0f, 0f - paddingVertical), ref boundary);
		container.sizeDelta = boundary.size + new Vector2(paddingHorizontal * 2f, paddingVertical * 2f);
		foreach (UnlockBox value2 in allBoxes.Values)
		{
			if (value2.children.Count == 0)
			{
				continue;
			}
			Vector2 anchoredPosition = ((RectTransform)value2.transform).anchoredPosition;
			RectTransform rectTransform = (RectTransform)value2.children[0].transform;
			float num2 = anchoredPosition.y - rectTransform.anchoredPosition.y;
			Vector2 end = anchoredPosition + Vector2.down * num2 * 0.82f;
			value2.lines.Add(DrawLine(anchoredPosition, end));
			float num3 = anchoredPosition.x;
			float num4 = anchoredPosition.x;
			foreach (UnlockBox child in value2.children)
			{
				RectTransform rectTransform2 = (RectTransform)child.transform;
				value2.lines.Add(DrawLine(rectTransform2.anchoredPosition + Vector2.up * num2 * 0.18f, rectTransform2.anchoredPosition));
				num3 = Mathf.Max(num3, rectTransform2.anchoredPosition.x);
				num4 = Mathf.Min(num4, rectTransform2.anchoredPosition.x);
			}
			value2.lines.Add(DrawLine(new Vector2(num4, end.y), new Vector2(num3, end.y)));
		}
	}

	private UnlockLayout GetLayout(UnlockBox unlock)
	{
		UnlockLayout unlockLayout = new UnlockLayout();
		unlockLayout.children = (from u in unlock.children
			orderby u.unlockSO.order
			select GetLayout(u)).ToList();
		unlockLayout.box = unlock;
		int num = 0;
		for (int num2 = 0; num2 < unlockLayout.children.Count; num2++)
		{
			unlockLayout.children[num2].xOffset = num;
			for (int num3 = 0; num3 < num2; num3++)
			{
				while (num2 > 0 && unlockLayout.children[num2].CollidesWith(unlockLayout.children[num3]))
				{
					num++;
					unlockLayout.children[num2].xOffset = num;
				}
			}
			num += 2;
		}
		int num4 = (num - 1) / 2;
		foreach (UnlockLayout child in unlockLayout.children)
		{
			child.xOffset -= num4;
		}
		return unlockLayout;
	}

	private int GetSubtreeDepth(UnlockBox unlock)
	{
		if (unlock.children.Count == 0)
		{
			return 0;
		}
		return ((IEnumerable<UnlockBox>)unlock.children).Max((Func<UnlockBox, int>)GetSubtreeDepth) + 1;
	}

	public Image DrawLine(Vector2 start, Vector2 end)
	{
		RectTransform rectTransform = UnityEngine.Object.Instantiate(linePrefab, container);
		rectTransform.localPosition = Vector3.zero;
		Vector2 vector = end - start;
		rectTransform.sizeDelta *= new Vector2(1f, vector.magnitude);
		rectTransform.anchoredPosition = start;
		float z = 57.29578f * Mathf.Atan2(vector.y, vector.x) + 90f;
		rectTransform.Rotate(new Vector3(0f, 0f, z));
		rectTransform.SetAsFirstSibling();
		return rectTransform.GetComponent<Image>();
	}

	public void OpenCloseMenu()
	{
		bool flag = !IsOpen;
		MainSim.Inst.workspace.gameObject.SetActive(!flag);
		base.transform.GetChild(0).gameObject.SetActive(flag);
		farmIcon.SetActive(flag);
		unlockIcon.SetActive(!flag);
		plusButton.SetActive(!flag);
		infoButton.SetActive(!flag);
	}

	public void DisableMenu()
	{
		openCloseButton.gameObject.SetActive(value: false);
		if (IsOpen)
		{
			OpenCloseMenu();
		}
	}

	public void Scroll(float zoom)
	{
		if (zoom > 0f)
		{
			base.transform.localScale = Vector2.one * Mathf.Clamp(base.transform.localScale.x * zoomSpeed, minZoomScale, maxZoomScale);
		}
		else if (zoom < 0f)
		{
			base.transform.localScale = Vector2.one * Mathf.Clamp(base.transform.localScale.x / zoomSpeed, minZoomScale, maxZoomScale);
		}
	}
}
public class SearchBox : MonoBehaviour
{
	private struct SearchResult
	{
		public CodeWindow codeWindow;

		public DocsWindow docsWindow;

		public int stringIndex;

		public SearchResult(CodeWindow codeWindow, int stringIndex)
		{
			this.codeWindow = codeWindow;
			this.stringIndex = stringIndex;
			docsWindow = null;
		}

		public SearchResult(DocsWindow docsWindow, int stringIndex)
		{
			this.docsWindow = docsWindow;
			this.stringIndex = stringIndex;
			codeWindow = null;
		}
	}

	private enum MoveWindowMode
	{
		Always,
		OnlyIfOffScreen,
		Never
	}

	[SerializeField]
	private CodeInputField inputField;

	[SerializeField]
	private Button nextButton;

	[SerializeField]
	private Button previousButton;

	[SerializeField]
	private ColoredButton closeButton;

	[SerializeField]
	private TextMeshProUGUI searchIndexText;

	private List<SearchResult> searchResults = new List<SearchResult>();

	private int currentSearchIndex;

	private string currentSearchString = "";

	private Window currentWindow;

	private bool wasWindowMinimized;

	private void Start()
	{
		inputField.onValueChanged.AddListener(delegate(string s)
		{
			UpdateSearchResults(s);
		});
		nextButton.onClick.AddListener(OnNextButtonClicked);
		previousButton.onClick.AddListener(OnPreviousButtonClicked);
		closeButton.OnClick.AddListener(CloseSearchBox);
	}

	private void UpdateSearchResults(string searchString, MoveWindowMode moveWindowMode = MoveWindowMode.OnlyIfOffScreen)
	{
		int num = searchString.IndexOf('\n');
		num = ((num == -1) ? 29 : Mathf.Min(num, 29));
		if (searchString.Length > num)
		{
			searchString = searchString.Substring(0, num);
			inputField.text = searchString;
		}
		inputField.Select();
		searchResults.Clear();
		if (string.IsNullOrEmpty(searchString))
		{
			foreach (Window value in MainSim.Inst.workspace.openWindows.Values)
			{
				DocsWindow component2;
				if (value.TryGetComponent<CodeWindow>(out var component))
				{
					component.UpdateSearch("");
				}
				else if (value.TryGetComponent<DocsWindow>(out component2))
				{
					component2.OpenMarkdownText.UpdateSearch("", -1);
				}
			}
			currentSearchString = "";
			searchIndexText.text = "0 / 0";
			LeaveCurrentSearchResult();
			return;
		}
		foreach (Window value2 in MainSim.Inst.workspace.openWindows.Values)
		{
			DocsWindow component4;
			if (value2.TryGetComponent<CodeWindow>(out var component3))
			{
				string text = component3.CodeInput.text;
				for (int num2 = text.IndexOf(searchString, 0, StringComparison.OrdinalIgnoreCase); num2 != -1; num2 = text.IndexOf(searchString, num2 + searchString.Length, StringComparison.OrdinalIgnoreCase))
				{
					searchResults.Add(new SearchResult(component3, num2));
				}
				component3.UpdateSearch(searchString);
			}
			else if (value2.TryGetComponent<DocsWindow>(out component4))
			{
				int num3 = component4.OpenMarkdownText.UpdateSearch(searchString, -1);
				for (int i = 0; i < num3; i++)
				{
					searchResults.Add(new SearchResult(component4, i));
				}
			}
		}
		currentSearchString = searchString;
		GoToSearchResult(0, moveWindowMode);
	}

	public void StartSearch(string searchTerm = "")
	{
		base.gameObject.SetActive(value: true);
		inputField.Select();
		inputField.text = searchTerm;
		UpdateSearchResults(searchTerm);
	}

	public void RefreshSearchResults()
	{
		UpdateSearchResults(currentSearchString, MoveWindowMode.Never);
	}

	public void CloseSearchBox()
	{
		UpdateSearchResults("");
		base.gameObject.SetActive(value: false);
	}

	private void OnNextButtonClicked()
	{
		if (searchResults.Count != 0)
		{
			currentSearchIndex = (currentSearchIndex + 1) % searchResults.Count;
			GoToSearchResult(currentSearchIndex, MoveWindowMode.Always);
		}
	}

	private void OnPreviousButtonClicked()
	{
		if (searchResults.Count != 0)
		{
			currentSearchIndex = (currentSearchIndex - 1 + searchResults.Count) % searchResults.Count;
			GoToSearchResult(currentSearchIndex, MoveWindowMode.Always);
		}
	}

	private void GoToSearchResult(int searchIndex, MoveWindowMode moveWindowMode = MoveWindowMode.OnlyIfOffScreen)
	{
		LeaveCurrentSearchResult();
		if (searchResults.Count == 0)
		{
			currentSearchIndex = 0;
			searchIndexText.text = "0 / 0";
			return;
		}
		searchIndexText.text = $"{searchIndex + 1} / {searchResults.Count}";
		currentSearchIndex = searchIndex;
		if (searchIndex >= searchResults.Count || searchIndex < 0)
		{
			currentSearchIndex = 0;
		}
		CodeWindow codeWindow = searchResults[currentSearchIndex].codeWindow;
		if (codeWindow != null)
		{
			currentWindow = codeWindow.GetComponent<Window>();
			if (currentWindow.isMinimized)
			{
				currentWindow.SetMinmized(minimized: false);
				wasWindowMinimized = true;
			}
			if (moveWindowMode != MoveWindowMode.Never)
			{
				MainSim.Inst.workspace.MoveCameraTo(currentWindow, moveWindowMode == MoveWindowMode.Always, searchResults[currentSearchIndex].stringIndex, codeWindow.CodeInput);
			}
			int stringIndex = searchResults[currentSearchIndex].stringIndex;
			codeWindow.ScrollToStringPosition(stringIndex);
			codeWindow.UpdateSearch(currentSearchString, stringIndex);
			codeWindow.GetComponent<Window>().MoveToFront();
		}
		DocsWindow docsWindow = searchResults[currentSearchIndex].docsWindow;
		if (docsWindow != null)
		{
			currentWindow = docsWindow.GetComponent<Window>();
			if (currentWindow.isMinimized)
			{
				currentWindow.SetMinmized(minimized: false);
				wasWindowMinimized = true;
			}
			if (moveWindowMode != MoveWindowMode.Never)
			{
				MainSim.Inst.workspace.MoveCameraTo(currentWindow, moveWindowMode == MoveWindowMode.Always);
			}
			int stringIndex2 = searchResults[currentSearchIndex].stringIndex;
			docsWindow.OpenMarkdownText.UpdateSearch(currentSearchString, stringIndex2);
			docsWindow.GetComponent<Window>().MoveToFront();
		}
	}

	private void LeaveCurrentSearchResult()
	{
		if (currentWindow != null && wasWindowMinimized)
		{
			currentWindow.SetMinmized(minimized: true);
		}
		if (currentWindow != null && currentWindow.TryGetComponent<CodeWindow>(out var component))
		{
			component.UpdateSearch(currentSearchString);
		}
		currentWindow = null;
		wasWindowMinimized = false;
	}

	public void SetValue(string value)
	{
		inputField.text = value;
	}
}
public class SpoilerWarning : MonoBehaviour
{
	[SerializeField]
	private TextMeshProUGUI text;

	[SerializeField]
	private Image background;

	public void SetText(string text)
	{
		this.text.text = text;
		ColorTheme theme = ThemeManager.Inst.Theme;
		background.color = theme.docs.SpoilerColor;
		this.text.color = theme.docs.SpoilerTextColor;
	}

	public void OnClicked()
	{
		UnityEngine.Object.Destroy(base.gameObject);
	}
}
public class CustomStandaloneInputModule : StandaloneInputModule
{
	public PointerEventData GetPointerData()
	{
		if (m_PointerData.ContainsKey(-1))
		{
			return m_PointerData[-1];
		}
		return null;
	}
}
public class Tooltip : MonoBehaviour
{
	private const float tweenTime = 0f;

	[SerializeField]
	private Canvas canvas;

	[SerializeField]
	private GameObject container;

	[SerializeField]
	private CustomStandaloneInputModule inputModule;

	[SerializeField]
	private Image background;

	[SerializeField]
	private MarkdownText text;

	[SerializeField]
	private TextMeshProUGUI docsNotice;

	private Vector2 offset = new Vector2(-20f, -20f);

	private TooltipInfo info;

	private GameObject tooltipGameObject;

	public GameObject Container => container;

	public TooltipInfo Info => info;

	private void Update()
	{
		GameObject gameObject = inputModule.GetPointerData()?.pointerCurrentRaycast.gameObject;
		if (gameObject != tooltipGameObject)
		{
			if (tooltipGameObject != null)
			{
				tooltipGameObject.GetComponent<TooltipAccessor>()?.TooltipGone();
			}
			tooltipGameObject = gameObject;
			UpdateTooltip();
		}
		if (info != null)
		{
			UpdatePosition();
			if (!string.IsNullOrEmpty(info.docs) && Input.GetKeyDown(KeyCode.Mouse1))
			{
				MainSim.Inst.workspace.OpenAndGoTo(info.docs);
			}
		}
	}

	private void Start()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
		text.Setup("", delegate
		{
		});
	}

	private void OnDestroy()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		background.color = theme.ui.TooltipColor;
	}

	private void UpdateTooltip()
	{
		container.transform.localScale = Vector3.zero;
		TooltipAccessor tooltipAccessor = tooltipGameObject?.GetComponent<TooltipAccessor>();
		if (tooltipAccessor != null)
		{
			info = tooltipAccessor.GetTooltipInfo(UpdateTooltip);
			if (info != null)
			{
				ScheduleTooltip();
			}
		}
		else
		{
			info = null;
		}
	}

	private void ScheduleTooltip()
	{
		GameObject go = tooltipGameObject;
		if (info.delay <= 0f)
		{
			SetTooltip(go);
			return;
		}
		TimerManager.StartTimer(delegate
		{
			SetTooltip(go);
		}, info.delay);
	}

	private void SetTooltip(GameObject tooltipObject)
	{
		if (!(tooltipObject != tooltipGameObject) && info != null)
		{
			if (string.IsNullOrEmpty(info.text))
			{
				container.transform.localScale = Vector3.zero;
				return;
			}
			text.UpdateText(info.text);
			container.transform.localScale = Vector3.one;
			UpdatePosition();
			docsNotice.gameObject.SetActive(!string.IsNullOrEmpty(info.docs));
		}
	}

	public bool CanShowTooltipImmediate()
	{
		if (!(tooltipGameObject == null))
		{
			return tooltipGameObject == MainSim.Inst.workspace.container.gameObject;
		}
		return true;
	}

	public void SetTooltipImmediate(TooltipInfo info)
	{
		if (CanShowTooltipImmediate())
		{
			this.info = info;
			tooltipGameObject = null;
			SetTooltip(null);
		}
	}

	public void CloseTooltip()
	{
		if (!string.IsNullOrEmpty(info?.text) && container.transform.localScale != Vector3.zero)
		{
			container.transform.localScale = Vector3.zero;
		}
	}

	private void UpdatePosition()
	{
		RectTransform rectTransform = (RectTransform)base.transform;
		Vector2 vector = offset;
		if (Input.mousePosition.x * 2f > (float)Screen.width)
		{
			TooltipInfo tooltipInfo = info;
			if (tooltipInfo == null || tooltipInfo.anchor != TooltipInfo.Anchor.BottomRight)
			{
				TooltipInfo tooltipInfo2 = info;
				if (tooltipInfo2 == null || tooltipInfo2.anchor != TooltipInfo.Anchor.TopRight)
				{
					goto IL_008d;
				}
			}
		}
		TooltipInfo tooltipInfo3 = info;
		Vector2 pivot = default(Vector2);
		if (tooltipInfo3 == null || tooltipInfo3.anchor != TooltipInfo.Anchor.BottomLeft)
		{
			TooltipInfo tooltipInfo4 = info;
			if (tooltipInfo4 == null || tooltipInfo4.anchor != TooltipInfo.Anchor.TopLeft)
			{
				pivot.x = 0f;
				vector *= new Vector2(-1f, 1f);
				goto IL_00bd;
			}
		}
		goto IL_008d;
		IL_00bd:
		if (Input.mousePosition.y * 2f > (float)Screen.height)
		{
			TooltipInfo tooltipInfo5 = info;
			if (tooltipInfo5 == null || tooltipInfo5.anchor != TooltipInfo.Anchor.TopLeft)
			{
				TooltipInfo tooltipInfo6 = info;
				if (tooltipInfo6 == null || tooltipInfo6.anchor != TooltipInfo.Anchor.TopRight)
				{
					goto IL_0137;
				}
			}
		}
		TooltipInfo tooltipInfo7 = info;
		if (tooltipInfo7 == null || tooltipInfo7.anchor != TooltipInfo.Anchor.BottomLeft)
		{
			TooltipInfo tooltipInfo8 = info;
			if (tooltipInfo8 == null || tooltipInfo8.anchor != TooltipInfo.Anchor.BottomRight)
			{
				pivot.y = 0f;
				vector *= new Vector2(1f, -1f);
				goto IL_0167;
			}
		}
		goto IL_0137;
		IL_0137:
		pivot.y = 1f;
		goto IL_0167;
		IL_008d:
		pivot.x = 1f;
		goto IL_00bd;
		IL_0167:
		rectTransform.pivot = pivot;
		rectTransform.anchoredPosition = ((Vector2)Input.mousePosition + vector) / canvas.scaleFactor;
		if (info != null && info.fixedPosition != Vector3.zero)
		{
			rectTransform.position = info.fixedPosition;
		}
	}
}
public class TooltipAccessor : MonoBehaviour
{
	[Header("Assign an object that inherits ITooltipHandler here.")]
	public GameObject tooltipHandler;

	public TooltipInfo GetTooltipInfo(Action updateTooltipCallback)
	{
		return tooltipHandler.GetComponent<ITooltipHandler>().GetTooltipInfo(updateTooltipCallback);
	}

	public void TooltipGone()
	{
		tooltipHandler.GetComponent<ITooltipHandler>().TooltipGone();
	}
}
public class TooltipPositioner : MonoBehaviour
{
	private Vector2 offset = new Vector2(-20f, -20f);

	private void Start()
	{
		UpdatePosition();
	}

	private void Update()
	{
		UpdatePosition();
	}

	public void UpdatePosition()
	{
		RectTransform obj = (RectTransform)base.transform;
		Vector2 vector = offset;
		Vector2 pivot = default(Vector2);
		if (Input.mousePosition.x * 2f > (float)Screen.width)
		{
			pivot.x = 1f;
		}
		else
		{
			pivot.x = 0f;
			vector *= new Vector2(-1f, 1f);
		}
		if (Input.mousePosition.y * 2f > (float)Screen.height)
		{
			pivot.y = 1f;
		}
		else
		{
			pivot.y = 0f;
			vector *= new Vector2(1f, -1f);
		}
		obj.pivot = pivot;
		obj.anchoredPosition = (Vector2)Input.mousePosition + vector;
	}
}
public static class TooltipUtils
{
	private static Dictionary<string, string> keywordDocs;

	public static TooltipInfo ItemTooltip(string itemName)
	{
		int itemId = StringIds.GetItemId(itemName.ToLower());
		if (itemId < 0)
		{
			return null;
		}
		ItemSO item = ResourceManager.GetItem(itemId);
		if (item == null)
		{
			return null;
		}
		double numItem = MainSim.Inst.GetNumItem(itemId);
		string text = "";
		string text2 = "\n\n" + string.Format(Localizer.Localize("item_tooltip_template_amount"), "`" + numItem.ToString("0.##", CultureInfo.InvariantCulture) + "`");
		return new TooltipInfo($"## {CodeUtilities.ToUpperSnake(item.itemName)}\n{Localizer.Localize(item.description)}{text2}{text}", 0f, default(Vector3), TooltipInfo.Anchor.Auto, item.docs);
	}

	public static TooltipInfo FarmObjectTooltip(string objectName)
	{
		FarmObjectSO farmObject = ResourceManager.GetFarmObject(objectName);
		if (farmObject == null || !MainSim.Inst.IsUnlocked(objectName))
		{
			return null;
		}
		string text = ((farmObject.cost == null || farmObject.cost.IsEmpty()) ? "" : ("\n\n" + string.Format(Localizer.Localize("object_tooltip_template_cost"), farmObject.objectName)));
		string text2 = "";
		return new TooltipInfo($"## {CodeUtilities.ToUpperSnake(farmObject.objectName)}\n{Localizer.Localize(farmObject.GetDescription())}{text2}{text}", 0f, default(Vector3), TooltipInfo.Anchor.Auto, farmObject.docs);
	}

	public static TooltipInfo UnlockTooltip(string unlockName)
	{
		UnlockSO unlock = ResourceManager.GetUnlock(unlockName);
		if (unlock == null)
		{
			return null;
		}
		string docs = (MainSim.Inst.IsUnlocked(unlock.unlockName) ? unlock.docs : "");
		int num = MainSim.Inst.NumUnlocked(unlock.unlockName);
		string text;
		if (num > unlock.maxUnlockLevel)
		{
			text = "Upgrade level is above the maximum. Stats and Achievements are disabled while this is the case. Click to reset to the max level.";
		}
		else if (unlock.IsMultiUnlock && num > 0)
		{
			text = Localizer.Localize(unlock.multiUnlockDescr);
			int num2 = num;
			bool flag = num2 >= unlock.maxUnlockLevel;
			switch (unlock.multiUnlockDescrMode)
			{
			case MultiUnlockDescrMode.AdditivePercent:
				text = string.Format(flag ? "{0}\n{1}%" : "{0}\n{1}% => {2}%", text, Mathf.Pow(unlock.additivePercentFactor, num2 - 1) * (100f + unlock.additivePercentStart), Mathf.Pow(unlock.additivePercentFactor, num2) * (100f + unlock.additivePercentStart));
				break;
			case MultiUnlockDescrMode.GridSize:
			{
				string format = (flag ? "{0}\n{1}x{2}" : "{0}\n{1}x{2} => {3}x{3}");
				Vector2Int worldSize = MainSim.Inst.GetWorldSize();
				int num3 = Helper.WorldSizeScale(num2 + 1);
				text = string.Format(format, text, worldSize.x, worldSize.y, num3);
				break;
			}
			case MultiUnlockDescrMode.Per10Seconds:
			{
				string format2 = (flag ? "{0}\n{1}/s" : "{0}\n{1}/s => {2}/s");
				float num4 = (float)(1 << Mathf.Max(0, num2 - 1)) * 0.1f;
				text = string.Format(format2, text, num4, num4 * 2f);
				break;
			}
			case MultiUnlockDescrMode.Megafarm:
				text = string.Format(flag ? "{0}\n{1}" : "{0}\n{1} => {2}", text, Helper.NumDrones(num2), Helper.NumDrones(num2 + 1));
				break;
			}
		}
		else
		{
			text = Localizer.Localize(unlock.description);
		}
		string arg = "";
		ItemBlock unlockCost = MainSim.Inst.GetUnlockCost(unlock);
		if (unlockCost != null && !unlockCost.IsEmpty())
		{
			arg = "\n\n" + string.Format(Localizer.Localize("unlock_tooltip_template_cost"), unlock.unlockName);
		}
		text = $"## {Localizer.Localize(unlock.unlockName)}\n{text}{arg}";
		return new TooltipInfo(text, 0f, Vector3.zero, TooltipInfo.Anchor.Auto, docs);
	}

	public static TooltipInfo HatTooltip(string hatName)
	{
		if (ResourceManager.GetHat(hatName) == null)
		{
			return null;
		}
		return new TooltipInfo(Localizer.Localize("hat_descr_" + hatName.ToLower()));
	}

	public static TooltipInfo LeaderboardTooltip(string lbName)
	{
		if (ResourceManager.GetLeaderboard(lbName) == null)
		{
			return null;
		}
		return new TooltipInfo(Localizer.Localize("lb_descr_" + lbName.ToLower()));
	}

	public static string GetKeywordDocsPage(string keyword)
	{
		if (keywordDocs == null)
		{
			keywordDocs = new Dictionary<string, string>();
			foreach (UnlockSO allUnlock in ResourceManager.GetAllUnlocks())
			{
				foreach (string unlock in allUnlock.unlocks)
				{
					if (Localizer.LoadDoc("docs/scripting/" + unlock) != "")
					{
						keywordDocs[unlock] = "docs/scripting/" + unlock;
					}
					else
					{
						keywordDocs[unlock] = allUnlock.docs;
					}
				}
			}
		}
		return keywordDocs.GetValueOrDefault(keyword, "");
	}

	public static TooltipInfo KeywordTooltip(string word)
	{
		if (!MainSim.Inst.IsUnlocked(word))
		{
			return null;
		}
		string text = "code_tooltip_" + word;
		string text2 = Localizer.Localize(text);
		if (text2 == text)
		{
			return null;
		}
		string text3 = $"## `{word}`\n{text2}";
		string docs = ((!BuiltinFunctions.Functions.ContainsKey(word) && !BuiltinFunctions.Methods.ContainsKey(word)) ? GetKeywordDocsPage(word) : ("functions/" + word));
		return new TooltipInfo(text3, 0f, default(Vector3), TooltipInfo.Anchor.Auto, docs);
	}

	public static TooltipInfo GetWordTooltip(string word, CodeWindow context)
	{
		if (word.Contains('.'))
		{
			string[] source = word.Split('.');
			word = source.Last().ToLower();
			switch (source.First())
			{
			case "Entities":
				return FarmObjectTooltip(word);
			case "Grounds":
				return FarmObjectTooltip(word);
			case "Items":
				return ItemTooltip(word);
			case "Unlocks":
				return UnlockTooltip(word);
			case "Hats":
				return HatTooltip(word);
			case "Leaderboards":
				return LeaderboardTooltip(word);
			}
		}
		TooltipInfo tooltipInfo = KeywordTooltip(word);
		if (tooltipInfo != null)
		{
			return tooltipInfo;
		}
		tooltipInfo = ItemTooltip(word);
		if (tooltipInfo != null)
		{
			return tooltipInfo;
		}
		tooltipInfo = FarmObjectTooltip(word);
		if (tooltipInfo != null)
		{
			return tooltipInfo;
		}
		tooltipInfo = UnlockTooltip(word);
		if (tooltipInfo != null)
		{
			return tooltipInfo;
		}
		FunctionNode functionNode = null;
		foreach (CodeWindow value in context.workspace.codeWindows.Values)
		{
			if (value.parsedFunctions.ContainsKey(word))
			{
				functionNode = value.parsedFunctions.GetValueOrDefault(word);
			}
		}
		if (functionNode != null)
		{
			return new TooltipInfo(CodeUtilities.ApplyCodeTags("`" + functionNode.GetSignature() + "`"));
		}
		return null;
	}
}
public class UnlockBox : MonoBehaviour, ITooltipHandler, IPointerEnterHandler, IEventSystemHandler
{
	public enum UnlockState
	{
		None,
		Unlocked,
		Locked,
		Unlockable,
		Upgradable,
		TooHigh
	}

	[SerializeField]
	private float animDuration = 0.1f;

	[SerializeField]
	private float anumScale = 1.5f;

	[SerializeField]
	private AnimationCurve animCurve;

	[NonSerialized]
	public UnlockSO unlockSO;

	public List<UnlockBox> children = new List<UnlockBox>();

	private Action updateTooltipCallback;

	[SerializeField]
	private Image background;

	[SerializeField]
	private ColoredButton button;

	[SerializeField]
	private TextMeshProUGUI codeText;

	[SerializeField]
	private Image image;

	[SerializeField]
	private RectTransform semiUnlockedRing;

	[SerializeField]
	private GameObject multiUnlockedPanel;

	[SerializeField]
	private TextMeshProUGUI multiUnlockText;

	[SerializeField]
	private float defaultHeight = 150f;

	[SerializeField]
	private float multiUnlockHeight = 225f;

	[NonSerialized]
	public List<Image> lines = new List<Image>();

	private ItemBlock currentCost;

	private UnlockState unlockState;

	private int prevNumUnlocked;

	public void SetupRec(bool unlockable, HashSet<string> openedUnlockDocs, ItemBlock inventory, Dictionary<string, int> unlocks, out bool allUnlocked)
	{
		int valueOrDefault = unlocks.GetValueOrDefault(unlockSO.unlockName, 0);
		UnlockState unlockState = ((valueOrDefault < unlockSO.maxUnlockLevel) ? ((!unlockable) ? UnlockState.Locked : ((valueOrDefault > 0) ? UnlockState.Upgradable : UnlockState.Unlockable)) : ((!unlockSO.IsMultiUnlock || valueOrDefault <= unlockSO.maxUnlockLevel) ? UnlockState.Unlocked : UnlockState.TooHigh));
		ColorTheme theme = ThemeManager.Inst.Theme;
		if (unlockState != this.unlockState || prevNumUnlocked != valueOrDefault)
		{
			this.unlockState = unlockState;
			currentCost = MainSim.Inst.GetUnlockCost(unlockSO);
			if (valueOrDefault == 1 && !openedUnlockDocs.Contains(unlockSO.docs) && !string.IsNullOrEmpty(unlockSO.docs) && !MainSim.Inst.MightBeSimulating())
			{
				MainSim.Inst.workspace.OpenAndGoTo(unlockSO.docs);
				openedUnlockDocs.Add(unlockSO.docs);
			}
			else if (valueOrDefault == 2 && unlockSO.unlockName == "expand" && !openedUnlockDocs.Contains("docs/unlocks/expand_2.md") && !MainSim.Inst.MightBeSimulating())
			{
				MainSim.Inst.workspace.OpenAndGoTo("docs/unlocks/expand_2.md");
				openedUnlockDocs.Add("docs/unlocks/expand_2.md");
			}
			if (unlockSO.mesh != null)
			{
				image.gameObject.SetActive(value: true);
				image.sprite = Resources.Load<Sprite>("UnlockTextures/" + unlockSO.unlockName);
				image.color = (unlockable ? Color.white : new Color(1f, 1f, 1f, 0.1f));
			}
			else
			{
				codeText.text = CodeUtilities.SyntaxColor2(unlockSO.displayCode, theme);
				Color32 textColor = theme.code.text.TextColor;
				if (!unlockable)
				{
					textColor.a = 26;
				}
				codeText.color = textColor;
			}
			semiUnlockedRing.gameObject.SetActive(valueOrDefault > 0 && unlockSO.IsMultiUnlock);
			semiUnlockedRing.sizeDelta = new Vector2(semiUnlockedRing.sizeDelta.x, multiUnlockHeight * ((float)valueOrDefault / (float)unlockSO.maxUnlockLevel));
			multiUnlockedPanel.SetActive(unlockSO.IsMultiUnlock);
			Color color = theme.unlocks.UnlockCountTextColor;
			if (!unlockable)
			{
				color.a = 0.1f;
			}
			multiUnlockText.color = color;
			multiUnlockText.text = $"{valueOrDefault} / {unlockSO.maxUnlockLevel}";
			RectTransform component = GetComponent<RectTransform>();
			component.sizeDelta = new Vector2(component.sizeDelta.x, unlockSO.IsMultiUnlock ? multiUnlockHeight : defaultHeight);
			foreach (Image line in lines)
			{
				line.color = ((valueOrDefault > 0) ? theme.unlocks.LineUnlockedColor : theme.unlocks.LineLockedColor);
			}
			button.Interactable = this.unlockState == UnlockState.Unlockable || this.unlockState == UnlockState.Upgradable;
			if (this.unlockState == UnlockState.TooHigh)
			{
				Achievements.enabled = false;
				button.Text = "TOO HIGH";
				button.Interactable = true;
			}
			if (updateTooltipCallback != null)
			{
				updateTooltipCallback();
			}
			prevNumUnlocked = valueOrDefault;
		}
		if (this.unlockState == UnlockState.Unlockable || this.unlockState == UnlockState.Upgradable)
		{
			if (inventory.Contains(currentCost))
			{
				button.OverrideColors = theme.unlocks.unlockable.ToColorBlock();
			}
			else
			{
				button.OverrideColors = theme.unlocks.unaffordable.ToColorBlock();
			}
		}
		else
		{
			ColorBlock value = theme.unlocks.unlockable.ToColorBlock();
			if (this.unlockState == UnlockState.Unlocked)
			{
				value.disabledColor = theme.unlocks.AlreadyUnlockedColor;
			}
			else
			{
				value.disabledColor = theme.unlocks.NotUnlockableColor;
			}
			button.OverrideColors = value;
		}
		background.color = theme.unlocks.BoxBackgroundColor;
		if (semiUnlockedRing.TryGetComponent<Image>(out var component2))
		{
			component2.color = theme.unlocks.AlreadyUnlockedColor;
		}
		if (multiUnlockedPanel.TryGetComponent<Image>(out var component3))
		{
			component3.color = theme.unlocks.UnlockCountBackgroundColor;
		}
		SetupChildren(unlockable && valueOrDefault > 0, openedUnlockDocs, inventory, unlocks, out allUnlocked);
		if (valueOrDefault < unlockSO.maxUnlockLevel)
		{
			allUnlocked = false;
		}
	}

	private void SetupChildren(bool unlockable, HashSet<string> openedUnlockDocs, ItemBlock inventory, Dictionary<string, int> unlocks, out bool allUnlocked)
	{
		allUnlocked = true;
		foreach (UnlockBox child in children)
		{
			child.SetupRec(unlockable, openedUnlockDocs, inventory, unlocks, out var allUnlocked2);
			allUnlocked &= allUnlocked2;
		}
	}

	public void ButtonClicked()
	{
		if (NumUnlocked() > unlockSO.maxUnlockLevel)
		{
			Achievements.enabled = true;
			MainSim.Inst.ResetUnlocksToMax();
		}
		else if (MainSim.Inst.UnlockOrUpgrade(unlockSO))
		{
			FMODSoundManager.PlaySound(SoundEffectType.Unlock, Vector3.zero);
			if (!string.IsNullOrEmpty(unlockSO.unlockedHat))
			{
				MainSim.Inst.UnlockHat(ResourceManager.GetHat(unlockSO.unlockedHat));
			}
		}
	}

	public TooltipInfo GetTooltipInfo(Action updateTooltipCallback)
	{
		this.updateTooltipCallback = updateTooltipCallback;
		return TooltipUtils.UnlockTooltip(unlockSO.unlockName);
	}

	public void TooltipGone()
	{
		updateTooltipCallback = null;
	}

	private int NumUnlocked()
	{
		return MainSim.Inst.NumUnlocked(unlockSO.unlockName);
	}

	public void OnPointerEnter(PointerEventData eventData)
	{
		if (!LeanTween.isTweening(base.gameObject))
		{
			LeanTween.scale(base.gameObject, new Vector3(anumScale, anumScale, 1f), animDuration).setEase(animCurve);
		}
	}

	private void OnEnable()
	{
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDisable()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		unlockState = UnlockState.None;
		prevNumUnlocked = 0;
	}
}
public class WarningIcon : MonoBehaviour
{
	private RectTransform rectTransform;

	private bool popUp;

	private bool dismiss;

	private void Awake()
	{
		rectTransform = GetComponent<RectTransform>();
		rectTransform.localScale = Vector3.zero;
	}

	private void Update()
	{
		if (popUp)
		{
			LeanTween.cancel(rectTransform);
			LeanTween.scale(rectTransform, Vector3.one, 0.3f).setEase(LeanTweenType.easeOutBack);
			popUp = false;
		}
		if (dismiss)
		{
			LeanTween.cancel(rectTransform);
			LeanTween.scale(rectTransform, Vector3.zero, 0.3f).setEase(LeanTweenType.easeInBack);
			dismiss = false;
		}
	}

	public void PopUp()
	{
		popUp = true;
		dismiss = false;
	}

	public void Dismiss()
	{
		dismiss = true;
		popUp = false;
	}

	public void Pressed()
	{
		Dismiss();
		MainSim.Inst.workspace.OpenAndGoTo("docs/output.md");
	}
}
public class Window : MonoBehaviour, IDragHandler, IEventSystemHandler, IBeginDragHandler, IEndDragHandler, IPointerDownHandler
{
	[SerializeField]
	private bool dockable;

	public RectTransform dockPosition;

	public Workspace workspace;

	public string windowName;

	public bool isMinimized;

	public Vector2 minimizedSize;

	public Vector2 playerSetSize;

	public Vector2 automaticSize;

	public Vector2 minSize;

	public float resizeMargin = 10f;

	public List<GameObject> disableOnMinimize;

	public UnityEvent<bool> OnMinimizeChanged;

	private bool horitontalResize;

	private bool verticalResize;

	private Vector2 pointerDownPosition;

	public Window dockedParent { get; private set; }

	public Window DockedChild
	{
		get
		{
			if (dockPosition == null || dockPosition.childCount == 0)
			{
				return null;
			}
			return dockPosition.GetChild(0)?.GetComponent<Window>();
		}
	}

	public Window LeastDockedChild
	{
		get
		{
			Window window = this;
			while (window.DockedChild != null)
			{
				window = window.DockedChild;
			}
			return window;
		}
	}

	public Window HighestDockedParent
	{
		get
		{
			Window window = this;
			while (window.dockedParent != null)
			{
				window = window.dockedParent;
			}
			return window;
		}
	}

	public float DockingOffset
	{
		get
		{
			Window window = HighestDockedParent;
			float num = 0f;
			while (window != this)
			{
				num += ((RectTransform)window.transform).rect.height;
				window = window.DockedChild;
			}
			return num;
		}
	}

	public void SetMinmized(bool minimized)
	{
		isMinimized = minimized;
		workspace.UpdateContainerSize();
		OnMinimizeChanged?.Invoke(minimized);
		foreach (GameObject item in disableOnMinimize)
		{
			item.SetActive(!minimized);
		}
		UpdateSize();
		MoveToFront();
	}

	public void Close()
	{
		if (DockedChild != null)
		{
			DockedChild.GetComponent<Window>().Undock();
		}
		workspace.openWindows.Remove(windowName);
		workspace.codeWindows.Remove(windowName, out var _);
		UnityEngine.Object.Destroy(base.gameObject);
	}

	public void UpdateSize()
	{
		if (isMinimized)
		{
			((RectTransform)base.transform).sizeDelta = minimizedSize;
			return;
		}
		Vector2 sizeDelta = Vector2.Max(playerSetSize, minSize);
		if (playerSetSize.y < minSize.y)
		{
			sizeDelta.y = MathF.Max(automaticSize.y, minSize.y);
		}
		((RectTransform)base.transform).sizeDelta = sizeDelta;
		if (TryGetComponent<CodeWindow>(out var component))
		{
			component.UpdateCodeInputSize();
		}
	}

	public void ToggleMinimize()
	{
		SetMinmized(!isMinimized);
	}

	public void OnDrag(PointerEventData eventData)
	{
		if (eventData.button == PointerEventData.InputButton.Left)
		{
			RectTransform rectTransform = (RectTransform)base.transform;
			if (horitontalResize)
			{
				playerSetSize.x += eventData.delta.x / workspace.editorCanvas.scaleFactor / workspace.cameraController.zoom;
				playerSetSize.x = MathF.Max(playerSetSize.x, minSize.x);
				UpdateSize();
			}
			if (verticalResize)
			{
				playerSetSize.y -= eventData.delta.y / workspace.editorCanvas.scaleFactor / workspace.cameraController.zoom;
				playerSetSize.y = MathF.Max(playerSetSize.y, minSize.y);
				UpdateSize();
			}
			if (!horitontalResize && !verticalResize)
			{
				rectTransform.anchoredPosition += eventData.delta / workspace.editorCanvas.scaleFactor / workspace.cameraController.zoom;
			}
		}
	}

	public void OnBeginDrag(PointerEventData eventData)
	{
		if (eventData.button == PointerEventData.InputButton.Left)
		{
			IsPointerOnResizeArea(pointerDownPosition, out horitontalResize, out verticalResize);
			if (horitontalResize || verticalResize)
			{
				playerSetSize = ((RectTransform)base.transform).sizeDelta;
			}
			if (dockable && !verticalResize && !horitontalResize)
			{
				Undock();
				GetComponent<CanvasGroup>().blocksRaycasts = false;
			}
		}
	}

	public void OnEndDrag(PointerEventData eventData)
	{
		if (eventData.button != PointerEventData.InputButton.Left)
		{
			return;
		}
		workspace.UpdateContainerSize();
		if (dockable && !verticalResize && !horitontalResize)
		{
			Window window = eventData.pointerCurrentRaycast.gameObject?.GetComponent<Window>();
			if (window == null)
			{
				window = eventData.pointerCurrentRaycast.gameObject?.GetComponentInParent<Window>();
			}
			DockOnto(window);
			GetComponent<CanvasGroup>().blocksRaycasts = true;
		}
		if (playerSetSize.x <= minSize.x)
		{
			playerSetSize.x = 0f;
		}
		if (playerSetSize.y <= minSize.y)
		{
			playerSetSize.y = 0f;
		}
		UpdateSize();
		horitontalResize = false;
		verticalResize = false;
	}

	public void OnPointerDown(PointerEventData eventData)
	{
		if (eventData.button == PointerEventData.InputButton.Left)
		{
			MoveToFront();
			pointerDownPosition = eventData.position;
		}
	}

	public void IsPointerOnResizeArea(Vector2 screenPoint, out bool horizontal, out bool vertical)
	{
		RectTransform rectTransform = (RectTransform)base.transform;
		RectTransformUtility.ScreenPointToLocalPointInRectangle(rectTransform, screenPoint, workspace.uiCam, out var localPoint);
		localPoint.y = 0f - localPoint.y;
		horizontal = rectTransform.rect.width - localPoint.x < resizeMargin && !isMinimized;
		vertical = rectTransform.rect.height - localPoint.y < resizeMargin && !isMinimized;
	}

	public void MoveToFront()
	{
		HighestDockedParent.transform.SetAsLastSibling();
	}

	public void DockOnto(Window other)
	{
		if (!(other == null) && other.dockable && dockable)
		{
			other.DockedChild?.DockOnto(LeastDockedChild);
			base.transform.SetParent(other.dockPosition, worldPositionStays: false);
			((RectTransform)base.transform).anchoredPosition = Vector2.zero;
			dockedParent = other;
		}
	}

	public void Undock()
	{
		if (dockedParent != null)
		{
			base.transform.SetParent(workspace.container);
			dockedParent = null;
		}
	}

	public void Rename(string newName)
	{
		workspace.openWindows.Remove(windowName);
		workspace.openWindows[newName] = this;
		if (TryGetComponent<CodeWindow>(out var component))
		{
			workspace.codeWindows.Remove(windowName, out var _);
			workspace.codeWindows[newName] = component;
		}
		windowName = newName;
	}
}
public class Workspace : MonoBehaviour
{
	public RectTransform container;

	public RectTransform zoomContainer;

	public Canvas editorCanvas;

	public CodeCompleter codeCompleter;

	public Camera uiCam;

	public CameraController cameraController;

	public SearchBox searchBox;

	public Tooltip tooltip;

	[SerializeField]
	private ScrollRect scrollRect;

	[SerializeField]
	private float zoomSpeed;

	[SerializeField]
	private float maxCanvasScaleFactor;

	[SerializeField]
	private float minCanvasScaleFactor;

	public bool slowMode;

	[SerializeField]
	private Vector2 spawnWindowOffset;

	[SerializeField]
	private Vector2 spawnDocsWindowOffset;

	[SerializeField]
	private CodeWindow codeWinPrefab;

	[SerializeField]
	private DocsWindow docWinPrefab;

	[SerializeField]
	private Texture2D textCursor;

	[SerializeField]
	private Texture2D horizontalResizeCursor;

	[SerializeField]
	private Texture2D verticalResizeCursor;

	[SerializeField]
	private Texture2D bidirectionalResizeCursor;

	public Window activeWindow;

	public UndoHistory undoHistory = new UndoHistory();

	public Dictionary<string, Window> openWindows = new Dictionary<string, Window>();

	public volatile ConcurrentDictionary<string, CodeWindow> codeWindows = new ConcurrentDictionary<string, CodeWindow>();

	private int docId;

	private bool containerDirty;

	private Window transitionTarget;

	private int transitionTargetCharIndex;

	private CodeInputField transitionTargetInputField;

	private float transitionStartTime;

	private float transitionEndTime;

	private Vector2 transitionStartPosition;

	public void Scroll(float scroll)
	{
		IOrderedEnumerable<Window> source = from w in openWindows.Values
			where RectTransformUtility.RectangleContainsScreenPoint(w.GetComponent<RectTransform>(), Input.mousePosition, uiCam)
			orderby w.HighestDockedParent.transform.GetSiblingIndex() descending
			select w;
		CodeWindow component2;
		if (source.Any() && source.First().TryGetComponent<DocsWindow>(out var component))
		{
			component.Scroll(scroll);
		}
		else if (source.Any() && source.First().TryGetComponent<CodeWindow>(out component2))
		{
			component2.Scroll(scroll);
		}
		else
		{
			Zoom(scroll);
		}
	}

	public void Zoom(float zoom)
	{
		if (zoom > 0f)
		{
			cameraController.zoom = Mathf.Clamp(cameraController.zoom * zoomSpeed, minCanvasScaleFactor, maxCanvasScaleFactor);
			zoomContainer.localScale = Vector3.one * cameraController.zoom;
			container.GetComponent<ContainerScaler>().UpdateMarginSize();
		}
		else if (zoom < 0f)
		{
			cameraController.zoom = Mathf.Clamp(cameraController.zoom / zoomSpeed, minCanvasScaleFactor, maxCanvasScaleFactor);
			zoomContainer.localScale = Vector3.one * cameraController.zoom;
			container.GetComponent<ContainerScaler>().UpdateMarginSize();
		}
	}

	private void Update()
	{
		if (containerDirty)
		{
			UpdateContainerSizeInternal();
		}
		LerpCameraToTarget();
		IOrderedEnumerable<Window> source = from w in openWindows.Values
			where RectTransformUtility.RectangleContainsScreenPoint(w.GetComponent<RectTransform>(), Input.mousePosition, uiCam)
			orderby w.transform.GetSiblingIndex() descending
			select w;
		if (source.Any() && source.First().TryGetComponent<Window>(out var component))
		{
			component.IsPointerOnResizeArea(Input.mousePosition, out var horizontal, out var vertical);
			float x = textCursor.width / 2;
			float y = textCursor.height / 2;
			CodeWindow component2;
			if (horizontal && vertical)
			{
				Cursor.SetCursor(bidirectionalResizeCursor, new Vector2(x, y), CursorMode.Auto);
			}
			else if (horizontal)
			{
				Cursor.SetCursor(horizontalResizeCursor, new Vector2(x, y), CursorMode.Auto);
			}
			else if (vertical)
			{
				Cursor.SetCursor(verticalResizeCursor, new Vector2(x, y), CursorMode.Auto);
			}
			else if (source.First().TryGetComponent<CodeWindow>(out component2) && component2.IsPointerOverCodeInput())
			{
				Cursor.SetCursor(textCursor, new Vector2(x, y), CursorMode.Auto);
			}
			else
			{
				Cursor.SetCursor(null, Vector2.zero, CursorMode.Auto);
			}
		}
		else
		{
			Cursor.SetCursor(null, Vector2.zero, CursorMode.Auto);
		}
	}

	private void Start()
	{
		SetViewportOptions("viewport sliding");
		OptionHolder.OnOptionChanged += SetViewportOptions;
	}

	private void SetViewportOptions(string option)
	{
		if (option == "viewport sliding")
		{
			scrollRect.inertia = OptionHolder.GetString("viewport sliding") == "enabled";
		}
	}

	public void UpdateContainerSize()
	{
		containerDirty = true;
	}

	private void UpdateContainerSizeInternal()
	{
		container.GetComponent<ContainerScaler>().UpdateSize();
		containerDirty = false;
	}

	public void OpenCodeWindow(string fileName, string code, Vector2 offset, Vector2 size = default(Vector2))
	{
		if (!openWindows.ContainsKey(fileName))
		{
			CodeWindow codeWindow = UnityEngine.Object.Instantiate(codeWinPrefab, container);
			codeWindow.workspace = this;
			Window component = codeWindow.GetComponent<Window>();
			RegisterWindow(component, fileName, offset, size);
			codeWindow.fileName = fileName;
			if (!string.IsNullOrEmpty(code))
			{
				codeWindow.Load(code);
			}
			else
			{
				codeWindow.Load("");
			}
			codeWindow.Parse();
		}
	}

	public void OpenDocsWindow(string windowName, string docsPage, Vector2 offset, Vector2 size = default(Vector2))
	{
		DocsWindow docsWindow = UnityEngine.Object.Instantiate(docWinPrefab, container);
		Window component = docsWindow.GetComponent<Window>();
		docId++;
		RegisterWindow(component, windowName, offset, size);
		docsWindow.LoadDoc(docsPage);
	}

	public void OpenAndGoTo(string doc)
	{
		AddNewDocsWindow(doc);
		if (MainSim.Inst.researchMenu.IsOpen)
		{
			MainSim.Inst.researchMenu.OpenCloseMenu();
		}
	}

	private void RegisterWindow(Window win, string name, Vector2 offset, Vector2 size = default(Vector2))
	{
		win.workspace = this;
		openWindows[name] = win;
		if (win.TryGetComponent<CodeWindow>(out var component))
		{
			codeWindows[name] = component;
		}
		win.windowName = name;
		win.GetComponent<RectTransform>().anchoredPosition = offset;
		if (size != default(Vector2))
		{
			win.playerSetSize = size;
			win.UpdateSize();
		}
		containerDirty = true;
	}

	public void MoveCameraTo(Window target, bool alwaysMoveWindow = false, int charIndex = -1, CodeInputField inputField = null)
	{
		RectTransform component = target.GetComponent<RectTransform>();
		if (!alwaysMoveWindow)
		{
			if (inputField != null)
			{
				Vector3 bottomRight = inputField.textComponent.textInfo.characterInfo[charIndex].bottomRight;
				Vector3 vector = inputField.textComponent.rectTransform.TransformPoint(bottomRight);
				if (vector.x >= 0f && vector.x < (float)Screen.width && vector.y >= 0f && vector.y < (float)Screen.height)
				{
					return;
				}
			}
			else
			{
				Rect rect = new Rect(Vector2.zero, ((RectTransform)base.transform).rect.size);
				Vector2 size = rect.size;
				Vector2 anchoredPosition = target.HighestDockedParent.GetComponent<RectTransform>().anchoredPosition;
				Vector2 vector2 = new Vector2(0f, target.DockingOffset);
				Vector2 position = anchoredPosition - vector2 + container.anchoredPosition + size / 2f;
				Rect rect2 = new Rect(position, component.rect.size);
				rect2.position -= new Vector2(0f, component.rect.size.y);
				if (rect2.Intersection(rect).Area() > rect2.Area() * 0.5f)
				{
					return;
				}
			}
		}
		float num = 0.2f;
		transitionStartPosition = container.anchoredPosition;
		transitionStartTime = Time.time;
		transitionEndTime = transitionStartTime + num;
		transitionTarget = target;
		transitionTargetCharIndex = charIndex;
		transitionTargetInputField = inputField;
	}

	private void LerpCameraToTarget()
	{
		if (transitionEndTime >= Time.time && transitionTarget != null)
		{
			RectTransform component = transitionTarget.GetComponent<RectTransform>();
			Vector2 anchoredPosition = transitionTarget.HighestDockedParent.GetComponent<RectTransform>().anchoredPosition;
			Vector2 vector = new Vector2(0f, transitionTarget.DockingOffset);
			Vector2 b = -anchoredPosition + vector;
			if (transitionTargetInputField != null)
			{
				Vector3 bottomRight = transitionTargetInputField.textComponent.textInfo.characterInfo[transitionTargetCharIndex].bottomRight;
				Vector3 position = transitionTargetInputField.textComponent.rectTransform.TransformPoint(bottomRight);
				Vector3 vector2 = component.InverseTransformPoint(position);
				b -= (Vector2)vector2;
			}
			else
			{
				b += new Vector2(0f - component.rect.width, component.rect.height) / 2f;
			}
			float t = (Time.time - transitionStartTime) / (transitionEndTime - transitionStartTime);
			container.anchoredPosition = Vector2.Lerp(transitionStartPosition, b, t);
		}
		else
		{
			transitionTarget = null;
		}
	}

	public string GenerateFileName(string prefix)
	{
		int num = 0;
		string text;
		do
		{
			text = prefix + num;
			num++;
		}
		while (!IsValidFileName(text));
		return text;
	}

	public bool IsValidFileName(string fileName)
	{
		if (string.IsNullOrEmpty(fileName) || openWindows.Keys.Select((string f) => f.ToLower()).Contains(fileName.ToLower()))
		{
			return false;
		}
		if (fileName == "__builtins__")
		{
			return false;
		}
		char[] invalidFileNameChars = Path.GetInvalidFileNameChars();
		foreach (char value in invalidFileNameChars)
		{
			if (fileName.Contains(value))
			{
				return false;
			}
		}
		return true;
	}

	public void AddNewWindow()
	{
		OpenCodeWindow(GenerateFileName("f"), "", -container.anchoredPosition + spawnWindowOffset);
		if (codeWindows.Count >= 20)
		{
			Achievements.UnlockAchievement("CHAOS");
		}
	}

	public void AddNewDocsWindow(string doc = "docs/home.md", Vector2 offset = default(Vector2))
	{
		OpenDocsWindow(GenerateFileName("docs"), doc, -container.anchoredPosition + spawnDocsWindowOffset + offset);
	}

	public void CallAddNewDocsWindow()
	{
		AddNewDocsWindow();
	}

	public void Undo()
	{
		if (activeWindow != null)
		{
			undoHistory.Undo(activeWindow.gameObject);
		}
	}

	public void Redo()
	{
		if (activeWindow != null)
		{
			undoHistory.Redo(activeWindow.gameObject);
		}
	}
}
[CompilerGenerated]
[EditorBrowsable(EditorBrowsableState.Never)]
[GeneratedCode("Unity.MonoScriptGenerator.MonoScriptInfoGenerator", null)]
internal class UnitySourceGeneratedAssemblyMonoScriptTypes_v1
{
	private struct MonoScriptData
	{
		public byte[] FilePathsData;

		public byte[] TypesData;

		public int TotalTypes;

		public int TotalFiles;

		public bool IsEditorOnly;
	}

	[MethodImpl(MethodImplOptions.AggressiveInlining)]
	private static MonoScriptData Get()
	{
		return new MonoScriptData
		{
			FilePathsData = new byte[5507]
			{
				0, 0, 0, 2, 0, 0, 0, 36, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 65,
				99, 104, 105, 101, 118, 101, 109, 101, 110, 116,
				115, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 36, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 104, 101, 97, 116, 67, 111,
				110, 115, 111, 108, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 49, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 67, 111, 110,
				116, 101, 110, 116, 92, 70, 97, 114, 109, 79,
				98, 106, 101, 99, 116, 83, 92, 65, 112, 112,
				108, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 53, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 67, 111, 110, 116, 101, 110,
				116, 92, 70, 97, 114, 109, 79, 98, 106, 101,
				99, 116, 83, 92, 66, 117, 115, 104, 80, 108,
				97, 110, 116, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 50, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 67, 111, 110, 116, 101,
				110, 116, 92, 70, 97, 114, 109, 79, 98, 106,
				101, 99, 116, 83, 92, 67, 97, 99, 116, 117,
				115, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 55, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 111, 110, 116, 101, 110, 116,
				92, 70, 97, 114, 109, 79, 98, 106, 101, 99,
				116, 83, 92, 68, 101, 97, 100, 80, 117, 109,
				112, 107, 105, 110, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 52, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 67, 111, 110, 116,
				101, 110, 116, 92, 70, 97, 114, 109, 79, 98,
				106, 101, 99, 116, 83, 92, 68, 105, 110, 111,
				115, 97, 117, 114, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 54, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 67, 111, 110, 116,
				101, 110, 116, 92, 70, 97, 114, 109, 79, 98,
				106, 101, 99, 116, 83, 92, 70, 97, 114, 109,
				79, 98, 106, 101, 99, 116, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 56, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 70, 97, 114, 109,
				79, 98, 106, 101, 99, 116, 83, 92, 70, 97,
				114, 109, 79, 98, 106, 101, 99, 116, 83, 79,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				50, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 71, 114, 111, 117, 110, 100, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 52, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 70, 97,
				114, 109, 79, 98, 106, 101, 99, 116, 83, 92,
				71, 114, 111, 119, 97, 98, 108, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 54, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 70, 97,
				114, 109, 79, 98, 106, 101, 99, 116, 83, 92,
				72, 101, 100, 103, 101, 80, 108, 97, 110, 116,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				51, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 80, 117, 109, 112, 107, 105, 110, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 61,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 67, 111, 110, 116, 101, 110, 116, 92, 70,
				97, 114, 109, 79, 98, 106, 101, 99, 116, 83,
				92, 80, 117, 109, 112, 107, 105, 110, 67, 111,
				110, 116, 114, 111, 108, 108, 101, 114, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 48, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 70, 97,
				114, 109, 79, 98, 106, 101, 99, 116, 83, 92,
				83, 111, 105, 108, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 53, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 67, 111, 110, 116,
				101, 110, 116, 92, 70, 97, 114, 109, 79, 98,
				106, 101, 99, 116, 83, 92, 83, 117, 110, 102,
				108, 111, 119, 101, 114, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 52, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 67, 111, 110,
				116, 101, 110, 116, 92, 70, 97, 114, 109, 79,
				98, 106, 101, 99, 116, 83, 92, 84, 114, 101,
				97, 115, 117, 114, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 53, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 67, 111, 110,
				116, 101, 110, 116, 92, 70, 97, 114, 109, 79,
				98, 106, 101, 99, 116, 83, 92, 84, 114, 101,
				101, 80, 108, 97, 110, 116, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 48, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 72, 97, 116, 115,
				92, 68, 105, 110, 111, 115, 97, 117, 114, 72,
				97, 116, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 40, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 67, 111, 110, 116, 101, 110,
				116, 92, 72, 97, 116, 115, 92, 72, 97, 116,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				42, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				72, 97, 116, 115, 92, 72, 97, 116, 83, 79,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				45, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				76, 101, 97, 100, 101, 114, 98, 111, 97, 114,
				100, 83, 79, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 47, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 67, 111, 110, 116, 101,
				110, 116, 92, 82, 101, 115, 111, 117, 114, 99,
				101, 77, 97, 110, 97, 103, 101, 114, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 39, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 84, 114,
				97, 100, 101, 83, 79, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 40, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 67, 111, 110,
				116, 101, 110, 116, 92, 85, 110, 108, 111, 99,
				107, 83, 79, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 34, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 70, 97, 114, 109, 92,
				68, 114, 111, 110, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 36, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 70, 97, 114,
				109, 92, 68, 114, 111, 110, 101, 83, 79, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 33,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 70, 97, 114, 109, 92, 70, 97, 114, 109,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				41, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 70, 97, 114, 109, 92, 70, 97, 114,
				109, 82, 101, 110, 100, 101, 114, 101, 114, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 40,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 70, 97, 114, 109, 92, 71, 114, 105, 100,
				77, 97, 110, 97, 103, 101, 114, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 39, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 70,
				97, 114, 109, 92, 73, 116, 101, 109, 69, 102,
				102, 101, 99, 116, 46, 99, 115, 0, 0, 0,
				2, 0, 0, 0, 36, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 70, 97, 114, 109,
				92, 77, 97, 105, 110, 83, 105, 109, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 38, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				70, 97, 114, 109, 92, 80, 105, 103, 103, 121,
				66, 97, 110, 107, 46, 99, 115, 0, 0, 0,
				2, 0, 0, 0, 39, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 70, 97, 114, 109,
				92, 83, 105, 109, 117, 108, 97, 116, 105, 111,
				110, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 33, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 73, 110, 112, 117, 116, 66, 111,
				115, 115, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 49, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 80, 114, 111, 103, 76, 97,
				110, 103, 92, 66, 117, 105, 108, 116, 105, 110,
				70, 117, 110, 99, 116, 105, 111, 110, 115, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 42,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				69, 120, 101, 99, 117, 116, 105, 111, 110, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 39,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				76, 111, 103, 103, 101, 114, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 44, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 80, 114,
				111, 103, 76, 97, 110, 103, 92, 77, 111, 100,
				117, 108, 101, 83, 116, 97, 116, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 53, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 65, 115, 115, 105, 103,
				110, 109, 101, 110, 116, 78, 111, 100, 101, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 53,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				78, 111, 100, 101, 115, 92, 66, 105, 110, 97,
				114, 121, 69, 120, 112, 114, 78, 111, 100, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				50, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 80, 114, 111, 103, 76, 97, 110, 103,
				92, 78, 111, 100, 101, 115, 92, 66, 114, 97,
				99, 107, 101, 116, 78, 111, 100, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 49, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 66, 114, 97, 110, 99,
				104, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 48, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 66, 114, 101, 97, 107, 78, 111, 100,
				101, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 47, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 78, 111, 100, 101, 115, 92, 67, 97,
				108, 108, 78, 111, 100, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 53, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 80, 114,
				111, 103, 76, 97, 110, 103, 92, 78, 111, 100,
				101, 115, 92, 67, 111, 109, 112, 97, 114, 105,
				115, 111, 110, 78, 111, 100, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 51, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 80,
				114, 111, 103, 76, 97, 110, 103, 92, 78, 111,
				100, 101, 115, 92, 67, 111, 110, 116, 105, 110,
				117, 101, 78, 111, 100, 101, 46, 99, 115, 0,
				0, 0, 2, 0, 0, 0, 46, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 80, 114,
				111, 103, 76, 97, 110, 103, 92, 78, 111, 100,
				101, 115, 92, 68, 101, 102, 78, 111, 100, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				47, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 80, 114, 111, 103, 76, 97, 110, 103,
				92, 78, 111, 100, 101, 115, 92, 68, 105, 99,
				116, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 46, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 70, 111, 114, 78, 111, 100, 101, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 51,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				78, 111, 100, 101, 115, 92, 70, 117, 110, 99,
				116, 105, 111, 110, 78, 111, 100, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 49, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 73, 109, 112, 111, 114,
				116, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 47, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 76, 105, 115, 116, 78, 111, 100, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				50, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 80, 114, 111, 103, 76, 97, 110, 103,
				92, 78, 111, 100, 101, 115, 92, 76, 105, 116,
				101, 114, 97, 108, 78, 111, 100, 101, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 43, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 78, 111, 100, 101, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 47,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				78, 111, 100, 101, 115, 92, 78, 111, 79, 112,
				78, 111, 100, 101, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 47, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 80, 114, 111, 103,
				76, 97, 110, 103, 92, 78, 111, 100, 101, 115,
				92, 80, 97, 115, 115, 78, 111, 100, 101, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 49,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				78, 111, 100, 101, 115, 92, 82, 101, 116, 117,
				114, 110, 78, 111, 100, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 51, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 80, 114,
				111, 103, 76, 97, 110, 103, 92, 78, 111, 100,
				101, 115, 92, 83, 101, 113, 117, 101, 110, 99,
				101, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 46, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 83, 101, 116, 78, 111, 100, 101, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 48,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				78, 111, 100, 101, 115, 92, 84, 117, 112, 108,
				101, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 52, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 85, 110, 97, 114, 121, 69, 120, 112,
				114, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 48, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 86, 97, 108, 117, 101, 78, 111, 100,
				101, 46, 99, 115, 0, 0, 0, 3, 0, 0,
				0, 39, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 80, 97, 114, 115, 101, 114, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 45, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 80,
				114, 111, 103, 114, 97, 109, 83, 116, 97, 116,
				101, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 38, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 83, 99, 111, 112, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 42, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 80,
				114, 111, 103, 76, 97, 110, 103, 92, 84, 111,
				107, 101, 110, 105, 122, 101, 114, 46, 99, 115,
				0, 0, 0, 2, 0, 0, 0, 44, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 80,
				114, 111, 103, 76, 97, 110, 103, 92, 84, 111,
				107, 101, 110, 83, 116, 114, 101, 97, 109, 46,
				99, 115, 0, 0, 0, 5, 0, 0, 0, 29,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 83, 97, 118, 101, 114, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 35, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 83, 116,
				101, 97, 109, 83, 99, 114, 105, 112, 116, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 38,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 83, 116, 101, 97, 109, 83, 116, 97, 116,
				115, 76, 111, 111, 112, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 39, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				66, 108, 105, 110, 107, 77, 97, 110, 97, 103,
				101, 114, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 42, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 66, 114, 101,
				97, 107, 80, 111, 105, 110, 116, 80, 97, 110,
				101, 108, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 40, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 67, 111, 100,
				101, 67, 111, 109, 112, 108, 101, 116, 101, 114,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				37, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 67, 111, 100, 101, 79,
				112, 116, 105, 111, 110, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 37, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				67, 111, 100, 101, 87, 105, 110, 100, 111, 119,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				42, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 67, 111, 110, 116, 97,
				105, 110, 101, 114, 83, 99, 97, 108, 101, 114,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				36, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 68, 76, 67, 66, 97,
				110, 110, 101, 114, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 37, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 68,
				111, 99, 115, 87, 105, 110, 100, 111, 119, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 43,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 68, 114, 111, 112, 100, 111,
				119, 110, 84, 111, 111, 108, 116, 105, 112, 115,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				39, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 69, 114, 114, 111, 114,
				77, 101, 115, 115, 97, 103, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 41, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 85,
				73, 92, 70, 108, 97, 115, 104, 105, 110, 103,
				66, 117, 116, 116, 111, 110, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 35, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 85, 73,
				92, 72, 97, 116, 80, 111, 112, 117, 112, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 36,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 73, 110, 118, 101, 110, 116,
				111, 114, 121, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 33, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 73, 116,
				101, 109, 85, 73, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 38, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 76,
				101, 97, 100, 101, 114, 98, 111, 97, 114, 100,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				43, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 76, 101, 97, 100, 101,
				114, 98, 111, 97, 114, 100, 69, 110, 116, 114,
				121, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 45, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 76, 101, 97, 100,
				101, 114, 98, 111, 97, 114, 100, 77, 97, 110,
				97, 103, 101, 114, 46, 99, 115, 0, 0, 0,
				3, 0, 0, 0, 39, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 77,
				97, 114, 107, 100, 111, 119, 110, 84, 101, 120,
				116, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 36, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 77, 101, 110, 117,
				92, 77, 101, 110, 117, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 42, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				77, 101, 110, 117, 92, 79, 112, 116, 105, 111,
				110, 77, 101, 110, 117, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 43, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				77, 101, 110, 117, 92, 83, 97, 118, 101, 67,
				104, 111, 111, 115, 101, 114, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 42, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 85, 73,
				92, 77, 101, 110, 117, 92, 83, 97, 118, 101,
				79, 112, 116, 105, 111, 110, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 37, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 85, 73,
				92, 79, 117, 116, 112, 117, 116, 84, 101, 120,
				116, 46, 99, 115, 0, 0, 0, 2, 0, 0,
				0, 39, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 82, 101, 115, 101,
				97, 114, 99, 104, 77, 101, 110, 117, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 36, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				85, 73, 92, 83, 101, 97, 114, 99, 104, 66,
				111, 120, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 41, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 83, 112, 111,
				105, 108, 101, 114, 87, 97, 114, 110, 105, 110,
				103, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 63, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 116, 111, 111, 108,
				116, 105, 112, 115, 92, 67, 117, 115, 116, 111,
				109, 83, 116, 97, 110, 100, 97, 108, 111, 110,
				101, 73, 110, 112, 117, 116, 77, 111, 100, 117,
				108, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 43, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 116, 111, 111,
				108, 116, 105, 112, 115, 92, 84, 111, 111, 108,
				116, 105, 112, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 51, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 116, 111,
				111, 108, 116, 105, 112, 115, 92, 84, 111, 111,
				108, 116, 105, 112, 65, 99, 99, 101, 115, 115,
				111, 114, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 53, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 116, 111, 111,
				108, 116, 105, 112, 115, 92, 84, 111, 111, 108,
				116, 105, 112, 80, 111, 115, 105, 116, 105, 111,
				110, 101, 114, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 48, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 116, 111,
				111, 108, 116, 105, 112, 115, 92, 84, 111, 111,
				108, 116, 105, 112, 85, 116, 105, 108, 115, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 36,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 85, 110, 108, 111, 99, 107,
				66, 111, 120, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 38, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 87, 97,
				114, 110, 105, 110, 103, 73, 99, 111, 110, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 33,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 87, 105, 110, 100, 111, 119,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				36, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 87, 111, 114, 107, 115,
				112, 97, 99, 101, 46, 99, 115
			},
			TypesData = new byte[2059]
			{
				0, 0, 0, 0, 13, 124, 65, 99, 104, 105,
				101, 118, 101, 109, 101, 110, 116, 115, 0, 0,
				0, 0, 25, 65, 99, 104, 105, 101, 118, 101,
				109, 101, 110, 116, 115, 124, 73, 116, 101, 109,
				65, 100, 100, 105, 116, 105, 111, 110, 0, 0,
				0, 0, 13, 124, 67, 104, 101, 97, 116, 67,
				111, 110, 115, 111, 108, 101, 0, 0, 0, 0,
				6, 124, 65, 112, 112, 108, 101, 0, 0, 0,
				0, 10, 124, 66, 117, 115, 104, 80, 108, 97,
				110, 116, 0, 0, 0, 0, 7, 124, 67, 97,
				99, 116, 117, 115, 0, 0, 0, 0, 12, 124,
				68, 101, 97, 100, 80, 117, 109, 112, 107, 105,
				110, 0, 0, 0, 0, 9, 124, 68, 105, 110,
				111, 115, 97, 117, 114, 0, 0, 0, 0, 11,
				124, 70, 97, 114, 109, 79, 98, 106, 101, 99,
				116, 0, 0, 0, 0, 13, 124, 70, 97, 114,
				109, 79, 98, 106, 101, 99, 116, 83, 79, 0,
				0, 0, 0, 7, 124, 71, 114, 111, 117, 110,
				100, 0, 0, 0, 0, 9, 124, 71, 114, 111,
				119, 97, 98, 108, 101, 0, 0, 0, 0, 11,
				124, 72, 101, 100, 103, 101, 80, 108, 97, 110,
				116, 0, 0, 0, 0, 8, 124, 80, 117, 109,
				112, 107, 105, 110, 0, 0, 0, 0, 18, 124,
				80, 117, 109, 112, 107, 105, 110, 67, 111, 110,
				116, 114, 111, 108, 108, 101, 114, 0, 0, 0,
				0, 5, 124, 83, 111, 105, 108, 0, 0, 0,
				0, 10, 124, 83, 117, 110, 102, 108, 111, 119,
				101, 114, 0, 0, 0, 0, 9, 124, 84, 114,
				101, 97, 115, 117, 114, 101, 0, 0, 0, 0,
				10, 124, 84, 114, 101, 101, 80, 108, 97, 110,
				116, 0, 0, 0, 0, 12, 124, 68, 105, 110,
				111, 115, 97, 117, 114, 72, 97, 116, 0, 0,
				0, 0, 4, 124, 72, 97, 116, 0, 0, 0,
				0, 6, 124, 72, 97, 116, 83, 79, 0, 0,
				0, 0, 14, 124, 76, 101, 97, 100, 101, 114,
				98, 111, 97, 114, 100, 83, 79, 0, 0, 0,
				0, 16, 124, 82, 101, 115, 111, 117, 114, 99,
				101, 77, 97, 110, 97, 103, 101, 114, 0, 0,
				0, 0, 8, 124, 84, 114, 97, 100, 101, 83,
				79, 0, 0, 0, 0, 9, 124, 85, 110, 108,
				111, 99, 107, 83, 79, 0, 0, 0, 0, 6,
				124, 68, 114, 111, 110, 101, 0, 0, 0, 0,
				8, 124, 68, 114, 111, 110, 101, 83, 79, 0,
				0, 0, 0, 5, 124, 70, 97, 114, 109, 0,
				0, 0, 0, 13, 124, 70, 97, 114, 109, 82,
				101, 110, 100, 101, 114, 101, 114, 0, 0, 0,
				0, 12, 124, 71, 114, 105, 100, 77, 97, 110,
				97, 103, 101, 114, 0, 0, 0, 0, 11, 124,
				73, 116, 101, 109, 69, 102, 102, 101, 99, 116,
				0, 0, 0, 0, 8, 124, 77, 97, 105, 110,
				83, 105, 109, 0, 0, 0, 0, 28, 77, 97,
				105, 110, 83, 105, 109, 124, 76, 101, 97, 100,
				101, 114, 98, 111, 97, 114, 100, 83, 116, 97,
				114, 116, 65, 114, 103, 115, 0, 0, 0, 0,
				10, 124, 80, 105, 103, 103, 121, 66, 97, 110,
				107, 0, 0, 0, 0, 22, 80, 105, 103, 103,
				121, 66, 97, 110, 107, 124, 65, 99, 116, 105,
				118, 101, 69, 102, 102, 101, 99, 116, 0, 0,
				0, 0, 11, 124, 83, 105, 109, 117, 108, 97,
				116, 105, 111, 110, 0, 0, 0, 0, 16, 83,
				105, 109, 117, 108, 97, 116, 105, 111, 110, 124,
				84, 105, 109, 101, 114, 0, 0, 0, 0, 10,
				124, 73, 110, 112, 117, 116, 66, 111, 115, 115,
				0, 0, 0, 0, 17, 124, 66, 117, 105, 108,
				116, 105, 110, 70, 117, 110, 99, 116, 105, 111,
				110, 115, 0, 0, 0, 0, 10, 124, 69, 120,
				101, 99, 117, 116, 105, 111, 110, 0, 0, 0,
				0, 7, 124, 76, 111, 103, 103, 101, 114, 0,
				0, 0, 0, 12, 124, 77, 111, 100, 117, 108,
				101, 83, 116, 97, 116, 101, 0, 0, 0, 0,
				15, 124, 65, 115, 115, 105, 103, 110, 109, 101,
				110, 116, 78, 111, 100, 101, 0, 0, 0, 0,
				15, 124, 66, 105, 110, 97, 114, 121, 69, 120,
				112, 114, 78, 111, 100, 101, 0, 0, 0, 0,
				12, 124, 66, 114, 97, 99, 107, 101, 116, 78,
				111, 100, 101, 0, 0, 0, 0, 11, 124, 66,
				114, 97, 110, 99, 104, 78, 111, 100, 101, 0,
				0, 0, 0, 10, 124, 66, 114, 101, 97, 107,
				78, 111, 100, 101, 0, 0, 0, 0, 9, 124,
				67, 97, 108, 108, 78, 111, 100, 101, 0, 0,
				0, 0, 15, 124, 67, 111, 109, 112, 97, 114,
				105, 115, 111, 110, 78, 111, 100, 101, 0, 0,
				0, 0, 13, 124, 67, 111, 110, 116, 105, 110,
				117, 101, 78, 111, 100, 101, 0, 0, 0, 0,
				8, 124, 68, 101, 102, 78, 111, 100, 101, 0,
				0, 0, 0, 11, 124, 80, 121, 70, 117, 110,
				99, 116, 105, 111, 110, 0, 0, 0, 0, 9,
				124, 68, 105, 99, 116, 78, 111, 100, 101, 0,
				0, 0, 0, 8, 124, 70, 111, 114, 78, 111,
				100, 101, 0, 0, 0, 0, 13, 124, 70, 117,
				110, 99, 116, 105, 111, 110, 78, 111, 100, 101,
				0, 0, 0, 0, 11, 124, 73, 109, 112, 111,
				114, 116, 78, 111, 100, 101, 0, 0, 0, 0,
				9, 124, 76, 105, 115, 116, 78, 111, 100, 101,
				0, 0, 0, 0, 12, 124, 76, 105, 116, 101,
				114, 97, 108, 78, 111, 100, 101, 0, 0, 0,
				0, 5, 124, 78, 111, 100, 101, 0, 0, 0,
				0, 16, 124, 66, 111, 120, 101, 100, 78, 111,
				100, 101, 80, 97, 114, 97, 109, 115, 0, 0,
				0, 0, 9, 124, 78, 111, 79, 112, 78, 111,
				100, 101, 0, 0, 0, 0, 9, 124, 80, 97,
				115, 115, 78, 111, 100, 101, 0, 0, 0, 0,
				11, 124, 82, 101, 116, 117, 114, 110, 78, 111,
				100, 101, 0, 0, 0, 0, 13, 124, 83, 101,
				113, 117, 101, 110, 99, 101, 78, 111, 100, 101,
				0, 0, 0, 0, 8, 124, 83, 101, 116, 78,
				111, 100, 101, 0, 0, 0, 0, 10, 124, 84,
				117, 112, 108, 101, 78, 111, 100, 101, 0, 0,
				0, 0, 14, 124, 85, 110, 97, 114, 121, 69,
				120, 112, 114, 78, 111, 100, 101, 0, 0, 0,
				0, 10, 124, 86, 97, 108, 117, 101, 78, 111,
				100, 101, 0, 0, 0, 0, 7, 124, 80, 97,
				114, 115, 101, 114, 0, 0, 0, 0, 8, 124,
				80, 114, 111, 103, 114, 97, 109, 0, 0, 0,
				0, 15, 124, 80, 97, 114, 115, 101, 69, 120,
				99, 101, 112, 116, 105, 111, 110, 0, 0, 0,
				0, 13, 124, 80, 114, 111, 103, 114, 97, 109,
				83, 116, 97, 116, 101, 0, 0, 0, 0, 6,
				124, 83, 99, 111, 112, 101, 0, 0, 0, 0,
				10, 124, 84, 111, 107, 101, 110, 105, 122, 101,
				114, 0, 0, 0, 0, 12, 124, 84, 111, 107,
				101, 110, 83, 116, 114, 101, 97, 109, 0, 0,
				0, 0, 6, 124, 84, 111, 107, 101, 110, 0,
				0, 0, 0, 6, 124, 83, 97, 118, 101, 114,
				0, 0, 0, 0, 12, 124, 79, 108, 100, 83,
				97, 118, 101, 71, 97, 109, 101, 0, 0, 0,
				0, 9, 124, 83, 97, 118, 101, 71, 97, 109,
				101, 0, 0, 0, 0, 4, 124, 83, 70, 79,
				0, 0, 0, 0, 5, 124, 80, 97, 105, 114,
				0, 0, 0, 0, 12, 124, 83, 116, 101, 97,
				109, 83, 99, 114, 105, 112, 116, 0, 0, 0,
				0, 15, 124, 83, 116, 101, 97, 109, 83, 116,
				97, 116, 115, 76, 111, 111, 112, 0, 0, 0,
				0, 13, 124, 66, 108, 105, 110, 107, 77, 97,
				110, 97, 103, 101, 114, 0, 0, 0, 0, 16,
				124, 66, 114, 101, 97, 107, 80, 111, 105, 110,
				116, 80, 97, 110, 101, 108, 0, 0, 0, 0,
				14, 124, 67, 111, 100, 101, 67, 111, 109, 112,
				108, 101, 116, 101, 114, 0, 0, 0, 0, 11,
				124, 67, 111, 100, 101, 79, 112, 116, 105, 111,
				110, 0, 0, 0, 0, 11, 124, 67, 111, 100,
				101, 87, 105, 110, 100, 111, 119, 0, 0, 0,
				0, 16, 124, 67, 111, 110, 116, 97, 105, 110,
				101, 114, 83, 99, 97, 108, 101, 114, 0, 0,
				0, 0, 10, 124, 68, 76, 67, 66, 97, 110,
				110, 101, 114, 0, 0, 0, 0, 11, 124, 68,
				111, 99, 115, 87, 105, 110, 100, 111, 119, 0,
				0, 0, 0, 17, 124, 68, 114, 111, 112, 100,
				111, 119, 110, 84, 111, 111, 108, 116, 105, 112,
				115, 0, 0, 0, 0, 13, 124, 69, 114, 114,
				111, 114, 77, 101, 115, 115, 97, 103, 101, 0,
				0, 0, 0, 15, 124, 70, 108, 97, 115, 104,
				105, 110, 103, 66, 117, 116, 116, 111, 110, 0,
				0, 0, 0, 9, 124, 72, 97, 116, 80, 111,
				112, 117, 112, 0, 0, 0, 0, 10, 124, 73,
				110, 118, 101, 110, 116, 111, 114, 121, 0, 0,
				0, 0, 7, 124, 73, 116, 101, 109, 85, 73,
				0, 0, 0, 0, 12, 124, 76, 101, 97, 100,
				101, 114, 98, 111, 97, 114, 100, 0, 0, 0,
				0, 17, 124, 76, 101, 97, 100, 101, 114, 98,
				111, 97, 114, 100, 69, 110, 116, 114, 121, 0,
				0, 0, 0, 19, 124, 76, 101, 97, 100, 101,
				114, 98, 111, 97, 114, 100, 77, 97, 110, 97,
				103, 101, 114, 0, 0, 0, 0, 13, 124, 77,
				97, 114, 107, 100, 111, 119, 110, 84, 101, 120,
				116, 0, 0, 0, 0, 24, 77, 97, 114, 107,
				100, 111, 119, 110, 84, 101, 120, 116, 124, 84,
				101, 120, 116, 83, 101, 99, 116, 105, 111, 110,
				0, 0, 0, 0, 22, 77, 97, 114, 107, 100,
				111, 119, 110, 84, 101, 120, 116, 124, 72, 111,
				118, 101, 114, 73, 110, 102, 111, 0, 0, 0,
				0, 5, 124, 77, 101, 110, 117, 0, 0, 0,
				0, 11, 124, 79, 112, 116, 105, 111, 110, 77,
				101, 110, 117, 0, 0, 0, 0, 12, 124, 83,
				97, 118, 101, 67, 104, 111, 111, 115, 101, 114,
				0, 0, 0, 0, 11, 124, 83, 97, 118, 101,
				79, 112, 116, 105, 111, 110, 0, 0, 0, 0,
				11, 124, 79, 117, 116, 112, 117, 116, 84, 101,
				120, 116, 0, 0, 0, 0, 13, 124, 82, 101,
				115, 101, 97, 114, 99, 104, 77, 101, 110, 117,
				0, 0, 0, 0, 25, 82, 101, 115, 101, 97,
				114, 99, 104, 77, 101, 110, 117, 124, 85, 110,
				108, 111, 99, 107, 76, 97, 121, 111, 117, 116,
				0, 0, 0, 0, 10, 124, 83, 101, 97, 114,
				99, 104, 66, 111, 120, 0, 0, 0, 0, 22,
				83, 101, 97, 114, 99, 104, 66, 111, 120, 124,
				83, 101, 97, 114, 99, 104, 82, 101, 115, 117,
				108, 116, 0, 0, 0, 0, 15, 124, 83, 112,
				111, 105, 108, 101, 114, 87, 97, 114, 110, 105,
				110, 103, 0, 0, 0, 0, 28, 124, 67, 117,
				115, 116, 111, 109, 83, 116, 97, 110, 100, 97,
				108, 111, 110, 101, 73, 110, 112, 117, 116, 77,
				111, 100, 117, 108, 101, 0, 0, 0, 0, 8,
				124, 84, 111, 111, 108, 116, 105, 112, 0, 0,
				0, 0, 16, 124, 84, 111, 111, 108, 116, 105,
				112, 65, 99, 99, 101, 115, 115, 111, 114, 0,
				0, 0, 0, 18, 124, 84, 111, 111, 108, 116,
				105, 112, 80, 111, 115, 105, 116, 105, 111, 110,
				101, 114, 0, 0, 0, 0, 13, 124, 84, 111,
				111, 108, 116, 105, 112, 85, 116, 105, 108, 115,
				0, 0, 0, 0, 10, 124, 85, 110, 108, 111,
				99, 107, 66, 111, 120, 0, 0, 0, 0, 12,
				124, 87, 97, 114, 110, 105, 110, 103, 73, 99,
				111, 110, 0, 0, 0, 0, 7, 124, 87, 105,
				110, 100, 111, 119, 0, 0, 0, 0, 10, 124,
				87, 111, 114, 107, 115, 112, 97, 99, 101
			},
			TotalFiles = 106,
			TotalTypes = 123,
			IsEditorOnly = false
		};
	}
}
