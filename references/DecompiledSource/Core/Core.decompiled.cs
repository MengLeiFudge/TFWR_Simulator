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
using Core.Content.FarmObjectS;
using Core.Content.WorldGen;
using Core.Platform;
using Microsoft.CodeAnalysis;
using Platforms;
using Platforms.Handler;
using Steamworks;
using TMPro;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Events;
using UnityEngine.Networking;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using UnityEngine.Serialization;
using UnityEngine.UI;
using UnityEngine.Video;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: AssemblyVersion("0.0.0.0")]
namespace Microsoft.CodeAnalysis
{
	[CompilerGenerated]
	[Microsoft.CodeAnalysis.Embedded]
	internal sealed class EmbeddedAttribute : Attribute
	{
	}
}
namespace System.Runtime.CompilerServices
{
	[CompilerGenerated]
	[Microsoft.CodeAnalysis.Embedded]
	[AttributeUsage(AttributeTargets.Class | AttributeTargets.Property | AttributeTargets.Field | AttributeTargets.Event | AttributeTargets.Parameter | AttributeTargets.ReturnValue | AttributeTargets.GenericParameter, AllowMultiple = false, Inherited = false)]
	internal sealed class NullableAttribute : Attribute
	{
		public readonly byte[] NullableFlags;

		public NullableAttribute(byte P_0)
		{
			NullableFlags = new byte[1] { P_0 };
		}

		public NullableAttribute(byte[] P_0)
		{
			NullableFlags = P_0;
		}
	}
	[CompilerGenerated]
	[Microsoft.CodeAnalysis.Embedded]
	[AttributeUsage(AttributeTargets.Class | AttributeTargets.Struct | AttributeTargets.Method | AttributeTargets.Interface | AttributeTargets.Delegate, AllowMultiple = false, Inherited = false)]
	internal sealed class NullableContextAttribute : Attribute
	{
		public readonly byte Flag;

		public NullableContextAttribute(byte P_0)
		{
			Flag = P_0;
		}
	}
}
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

	private static readonly string[] achievementHatNames = new string[22]
	{
		"golden_carrot_hat", "golden_cactus_hat", "golden_gold_hat", "golden_tree_hat", "golden_pumpkin_hat", "golden_sunflower_hat", "carrot_hat", "cactus_hat", "gold_hat", "tree_hat",
		"pumpkin_hat", "sunflower_hat", "bucket", "coal_hat", "rice_hat", "quartz_hat", "bamboo_hat", "dynamite_hat", "mushroom_hat", "traffic_cone",
		"traffic_cone_stack", "wizard_hat"
	};

	private static int richPresenceItemId = -1;

	private static object lockObject = new object();

	public static volatile bool enabled = true;

	public static string RichPresenceDisplay { get; set; } = null;

	public static string RichPresenceQuantity { get; set; } = null;

	public static IEnumerable<string> GetUnlockedHatNames(Func<string, bool> isUnlocked)
	{
		return achievementHatNames.Where(isUnlocked);
	}

	public static void LoadStats()
	{
		lock (lockObject)
		{
			PlatformHandler platformHandler = PlatformManager.PlatformHandler;
			window.Clear();
			best = ItemBlock.CreateEmpty();
			sum = ItemBlock.CreateEmpty();
			total_stats = ItemBlock.CreateEmpty();
			if (!SteamManager.Initialized || !best.IsEmpty())
			{
				return;
			}
			platformHandler.RequestCurrentStats();
			platformHandler.GetStat("version", out var statValue);
			if (statValue != 3)
			{
				platformHandler.ResetAllStats();
				platformHandler.SetStat("version", 3);
				platformHandler.StoreStats();
			}
			ItemSO[] array = Resources.LoadAll<ItemSO>("Items/");
			foreach (ItemSO itemSO in array)
			{
				if (itemSO.trackStats)
				{
					platformHandler.GetStat(itemSO.itemName, out var statValue2);
					best.AddItem(itemSO.itemId, statValue2);
					UnlockGoldenHats(itemSO.itemName, statValue2);
				}
				if (itemSO.trackTotalStats)
				{
					platformHandler.GetStat("total_" + itemSO.itemName, out var statValue3);
					total_stats.AddItem(itemSO.itemId, statValue3);
					UnlockFarmHats(itemSO.itemId);
				}
			}
			platformHandler.SetRichPresence("steam_display", "#default_status");
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

	public static void CollectItem(int itemId, double number, Duration currentTime, Duration collectionDuration, bool trackRate, bool trackTotal)
	{
		if (!enabled)
		{
			return;
		}
		lock (lockObject)
		{
			string itemName = StringIds.GetItemName(itemId);
			double n = number;
			if (trackRate)
			{
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
					PlatformManager.PlatformHandler.SetStat(itemName, (int)number3);
					UnlockGoldenHats(itemName, number3);
				}
				UpdateRichPresence(itemId);
			}
			if (trackTotal)
			{
				total_stats.AddItem(itemId, n);
				PlatformManager.PlatformHandler.SetStat("total_" + itemName, (int)total_stats.GetNumber(itemId));
				UnlockFarmHats(itemId);
			}
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
			case "coal":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("coal_hat"));
				break;
			case "iron":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("bucket"));
				break;
			case "rice":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("rice_hat"));
				break;
			case "quartz":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("quartz_hat"));
				break;
			case "bamboo":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("bamboo_hat"));
				break;
			case "dynamite":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("dynamite_hat"));
				break;
			case "mushroom":
				MainSim.Inst.UnlockHat(ResourceManager.GetHat("mushroom_hat"));
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
				PlatformManager.PlatformHandler.GetStat(statName, out var statValue);
				statValue += increment;
				PlatformManager.PlatformHandler.SetStat(statName, statValue);
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
					PlatformManager.PlatformHandler.UnlockAchievement(achievement);
					PlatformManager.PlatformHandler.StoreStats();
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
public class CameraController : MonoBehaviour
{
	[SerializeField]
	private RectTransform contentRect;

	[SerializeField]
	private RectTransform windowRect;

	[SerializeField]
	private Canvas canvas;

	[SerializeField]
	private Transform sceneScaler;

	public float zoom = 1f;

	private Vector3 startPos;

	private float minXAngle;

	private Camera cam;

	public static CameraController Inst { get; private set; }

	public Vector2 CameraToScrollPos(Vector3 cameraPos)
	{
		DesignConstants.CameraDesignConstants cameraController = DesignConstants.Inst.cameraController;
		Vector3 vector = new Vector3(startPos.x * canvas.scaleFactor * zoom, startPos.y, startPos.z);
		Vector3 vector2 = cameraPos - vector;
		vector2.x /= cameraController.xFactor;
		vector2.y /= cameraController.yFactor;
		return (Vector2)(vector2 / zoom / canvas.scaleFactor * Screen.height) - windowRect.anchoredPosition;
	}

	private void Start()
	{
		Inst = this;
		TryGetComponent<Camera>(out cam);
		startPos = base.transform.position;
		minXAngle = base.transform.eulerAngles.x;
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnDestroy()
	{
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		if (cam != null)
		{
			cam.backgroundColor = theme.ui.BackgroundColor;
		}
	}

	private void Update()
	{
		DesignConstants.CameraDesignConstants cameraController = DesignConstants.Inst.cameraController;
		Vector3 vector = (contentRect.anchoredPosition + windowRect.anchoredPosition) / Screen.height * canvas.scaleFactor * zoom;
		vector.x *= cameraController.xFactor;
		vector.y *= cameraController.yFactor;
		base.transform.position = vector + new Vector3(startPos.x * canvas.scaleFactor * zoom, startPos.y, startPos.z);
		sceneScaler.localScale = Vector3.one * cameraController.islandScale * canvas.scaleFactor * zoom / ((float)Screen.height / 1080f);
		RenderPackage obj = MainSim.Inst?.GetRenderPackage();
		float num = ((float?)(obj?.maxDepth - obj?.minDepth)) ?? 0f;
		float num2 = Mathf.LerpAngle(minXAngle, cameraController.maxXAngle, num / (float)cameraController.holeDepthForMaxXAngle);
		float num3 = Mathf.Max(1f, cameraController.maxCamTiltSpeedup * Mathf.Abs(Mathf.DeltaAngle(num2, base.transform.eulerAngles.x) / Mathf.DeltaAngle(cameraController.maxXAngle, minXAngle)));
		float x = Mathf.MoveTowardsAngle(base.transform.eulerAngles.x, num2, Time.deltaTime * cameraController.angularTiltSpeed * num3);
		base.transform.eulerAngles = new Vector3(x, base.transform.eulerAngles.y, base.transform.eulerAngles.z);
		FMODSoundManager.zoomLevelField(zoom);
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
			GridManager grid = sim.farm.grid;
			if (grid.CellAt(nextPos).entity is Dinosaur)
			{
				int num = 0;
				Vector2Int? vector2Int = null;
				GridManager.Cell[] cells = grid.cells;
				for (int i = 0; i < cells.Length; i++)
				{
					GridManager.Cell cell = cells[i];
					if (cell.entity is Dinosaur)
					{
						num++;
					}
					else if (cell.entity == null)
					{
						if (vector2Int.HasValue)
						{
							return PyTuple.From(nextPos);
						}
						vector2Int = cell.pos;
					}
				}
				int num2 = grid.WorldSize.x * grid.WorldSize.y - 2;
				if (num == num2 && vector2Int.HasValue)
				{
					return PyTuple.From(vector2Int.Value);
				}
			}
			return PyTuple.From(nextPos);
		}
		return new PyNone();
	}

	public void SetNextTarget(Vector2Int nextTarget)
	{
		if (base.pos == nextTarget)
		{
			throw new InvalidOperationException();
		}
		nextPos = nextTarget;
		hasNextPos = true;
	}
}
public class BushPlant : Growable
{
	public void GenerateHedgeMaze(int desired_size)
	{
		_ = sim.farm.grid.WorldSize;
		int z = pos3.z;
		int num = 1;
		Vector2Int vector2Int = base.pos;
		Vector2Int vector2Int2 = -Vector2Int.one;
		bool[] array = new bool[4];
		while (num < desired_size)
		{
			Vector2Int vector2Int3 = vector2Int;
			Vector2Int vector2Int4 = vector2Int;
			if (vector2Int2.x > 0)
			{
				vector2Int3.y += ((vector2Int2.y > 0) ? num : (-1));
				vector2Int4.x += num;
				if (vector2Int2.y < 0)
				{
					vector2Int4.y += num - 1;
				}
			}
			else
			{
				vector2Int3.x += num - 1;
				vector2Int3.y += ((vector2Int2.y > 0) ? num : (-1));
				vector2Int4.x--;
				if (vector2Int2.y < 0)
				{
					vector2Int4.y += num - 1;
				}
			}
			if (sim.farm.grid.IsWithinBounds(vector2Int3) && sim.farm.grid.IsWithinBounds(vector2Int4))
			{
				int num2 = (int)Mathf.Sign(vector2Int4.x - vector2Int3.x);
				int num3 = vector2Int3.x;
				while (num3 != vector2Int4.x)
				{
					Vector2Int vector2Int5 = new Vector2Int(num3, vector2Int3.y);
					if (sim.farm.grid.CellAt(vector2Int5).depth == z)
					{
						num3 += num2;
						continue;
					}
					goto IL_025b;
				}
				num2 = (int)Mathf.Sign(vector2Int4.y - vector2Int3.y);
				int num4 = vector2Int3.y;
				while (num4 != vector2Int4.y)
				{
					Vector2Int vector2Int6 = new Vector2Int(vector2Int4.x, num4);
					if (sim.farm.grid.CellAt(vector2Int6).depth == z)
					{
						num4 += num2;
						continue;
					}
					goto IL_025b;
				}
				if (sim.farm.grid.CellAt(vector2Int4).depth == z)
				{
					num++;
					if (vector2Int2.x < 0)
					{
						vector2Int.x--;
					}
					if (vector2Int2.y < 0)
					{
						vector2Int.y--;
					}
					vector2Int2 = -vector2Int2;
					continue;
				}
			}
			goto IL_025b;
			IL_025b:
			array[((vector2Int2.x > 0) ? 1 : 0) + ((vector2Int2.y > 0) ? 2 : 0)] = true;
			int num5 = 0;
			while (num5 < 3)
			{
				vector2Int2 = new Vector2Int(-vector2Int2.y, vector2Int2.x);
				if (array[((vector2Int2.x > 0) ? 1 : 0) + ((vector2Int2.y > 0) ? 2 : 0)])
				{
					num5++;
					continue;
				}
				goto IL_02c6;
			}
			break;
			IL_02c6:;
		}
		bool[][] array2 = new bool[num * num][];
		int num6 = sim.randomMaze.Next(num * num);
		array2[num6] = new bool[4] { true, true, true, true };
		List<int> list = new List<int> { num6 };
		bool flag = false;
		List<int> list2 = new List<int>();
		while (list.Count > 0)
		{
			int num7 = list[list.Count - 1];
			int num8 = num7 % num;
			int num9 = num7 / num;
			foreach (GridDirection item in ((GridDirection[])Enum.GetValues(typeof(GridDirection))).OrderBy((GridDirection k) => sim.randomMaze.Next()))
			{
				Vector2Int directionVector = item.GetDirectionVector();
				int num10 = num8 + directionVector.x;
				int num11 = num9 + directionVector.y;
				if (num10 >= 0 && num11 >= 0 && num10 < num && num11 < num && array2[num10 + num * num11] == null)
				{
					list.Add(num10 + num * num11);
					array2[num10 + num * num11] = new bool[4] { true, true, true, true };
					array2[num10 + num * num11][(int)item.Reverse()] = false;
					array2[num7][(int)item] = false;
					flag = false;
					break;
				}
			}
			if (list[list.Count - 1] == num7)
			{
				list.RemoveAt(list.Count - 1);
				if (!flag)
				{
					list2.Add(num7);
					flag = true;
				}
			}
		}
		int num12 = list2[sim.randomMaze.Next(list2.Count - 1)];
		for (int num13 = 0; num13 < num; num13++)
		{
			for (int num14 = 0; num14 < num; num14++)
			{
				bool flag2 = num12 == num13 + num * num14;
				sim.farm.grid.SetGround(new Vector2Int(num13, num14) + vector2Int, "grassland");
				HedgePlant hedgePlant = (HedgePlant)sim.farm.grid.SetEntity(new Vector2Int(num13, num14) + vector2Int, flag2 ? "treasure" : "hedge");
				hedgePlant.walls = array2[num13 + num * num14];
				hedgePlant.lowLeftCorner = vector2Int;
				hedgePlant.mazeSize = num;
				if (flag2)
				{
					((Treasure)hedgePlant).ChooseNextPosition();
				}
			}
		}
		sim.UnlockAchievement("SPAWN_MAZE");
	}
}
public class Cactus : Growable
{
	private int number;

	private bool isPopped;

	private Duration plantTime;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		collectionDuration = sim.CurrentTime - plantTime;
		if (!Harvestable)
		{
			HarvestEffects();
			sim.farm.grid.RemoveEntity(base.pos);
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
		sim.farm.grid.CellAt(base.pos).cactusNumber = -1;
		CheckWrongOrderAchievement();
	}

	public override void OnSwapped()
	{
		base.OnSwapped();
		CheckWrongOrderAchievement();
	}

	private void CheckWrongOrderAchievement()
	{
		if (!sim.RecordsAchievements)
		{
			return;
		}
		Vector2Int worldSize = sim.farm.grid.WorldSize;
		for (int i = 0; i < worldSize.y; i++)
		{
			for (int j = 0; j < worldSize.x; j++)
			{
				ref GridManager.Cell reference = ref sim.farm.grid.CellAt(j, i);
				if (!(reference.entity is Cactus { Harvestable: not false } cactus))
				{
					return;
				}
				if (j + 1 < worldSize.x)
				{
					ref GridManager.Cell reference2 = ref sim.farm.grid.CellAt(j + 1, i);
					if (!(reference2.entity is Cactus two) || reference.depth != reference2.depth || !AreSorted(cactus, two, reverse: true))
					{
						return;
					}
				}
				if (i + 1 < worldSize.y)
				{
					ref GridManager.Cell reference3 = ref sim.farm.grid.CellAt(j, i + 1);
					if (!(reference3.entity is Cactus two2) || reference.depth != reference3.depth || !AreSorted(cactus, two2, reverse: true))
					{
						return;
					}
				}
			}
		}
		sim.UnlockAchievement("WRONG_ORDER");
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
		Cactus[] neighbors = sim.farm.grid.GetNeighbors<Cactus>(base.pos);
		if (!neighbors.All((Cactus c) => c == null || pos3.z != c.pos3.z || c.IsSorted()))
		{
			return;
		}
		Cactus[] array = neighbors;
		foreach (Cactus cactus in array)
		{
			if (cactus != null && pos3.z == cactus.pos3.z)
			{
				cactus.Pop(popped, ref numWeird);
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
		List<Vector2Int> list = new List<Vector2Int> { base.pos };
		while (list.Count > 0)
		{
			Vector2Int item = list[list.Count - 1];
			list.RemoveAt(list.Count - 1);
			if (hashSet.Contains(item))
			{
				continue;
			}
			Cactus entity = sim.farm.grid.GetEntity<Cactus>(item);
			if (entity != null && pos3.z == entity.pos3.z && entity.IsSorted())
			{
				hashSet.Add(item);
				if (entity.weird)
				{
					numWeird++;
				}
				list.AddRange(GridManager.Neighboring4Positions(item));
			}
		}
		count = hashSet.Count;
	}

	private bool IsSorted(bool reverse = false)
	{
		if (!Harvestable)
		{
			return false;
		}
		GridManager grid = sim.farm.grid;
		if (!AreSorted(this, grid.GetEntity<Cactus>(base.pos.x, base.pos.y + 1), reverse))
		{
			return false;
		}
		if (!AreSorted(this, grid.GetEntity<Cactus>(base.pos.x + 1, base.pos.y), reverse))
		{
			return false;
		}
		if (!AreSorted(grid.GetEntity<Cactus>(base.pos.x, base.pos.y - 1), this, reverse))
		{
			return false;
		}
		if (!AreSorted(grid.GetEntity<Cactus>(base.pos.x - 1, base.pos.y), this, reverse))
		{
			return false;
		}
		return true;
	}

	private static bool AreSorted(Cactus one, Cactus two, bool reverse)
	{
		if (one == null || two == null)
		{
			return true;
		}
		if (one.pos3.z != two.pos3.z)
		{
			return true;
		}
		if (!one.Harvestable || !two.Harvestable)
		{
			return false;
		}
		int num = one.number - two.number;
		if (num != 0 && num > 0 != reverse)
		{
			return false;
		}
		return true;
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
			yield return (objectSO.gooMeshes[gooIndex], Matrix4x4.Translate(sim.farm.grid.CellToLocal(base.pos)));
		}
	}

	public override void OnRestart()
	{
		base.OnRestart();
		if (sim.farm.grid.CellAt(base.pos).cactusNumber == -1)
		{
			sim.farm.grid.CellAt(base.pos).cactusNumber = sim.randomCactus.Next(10);
		}
		number = sim.farm.grid.CellAt(base.pos).cactusNumber;
		isPopped = false;
		plantTime = sim.CurrentTime;
	}
}
public class DeadPumpkin : Entity
{
	public override bool Harvestable => false;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		sim.farm.grid.RemoveEntity(base.pos);
		return base.Harvest(out collectionDuration);
	}
}
public class Dinosaur : Entity
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
		Vector3 vector = sim.farm.grid.CellToLocal(base.pos + base.Orientation.Reverse().GetDirectionVector()) - localPosition;
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
		Vector3 vector = sim.farm.grid.CellToLocal(base.pos + base.Orientation.GetDirectionVector()) - localPosition;
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
		ref GroundData.Ground reference = ref sim.farm.grid.GroundAt(base.pos);
		if (reference.groundSo.objectName == "grassland")
		{
			reference.groundSo = ResourceManager.GetGround("soil");
			sim.farm.grid.groundData.MarkPositionChanged(base.pos);
		}
	}

	public override void OnFree()
	{
		base.OnFree();
		if (isInSnake && drone.hat.hatSO.hatName == "dinosaur_hat")
		{
			drone.ChangeHat(Hat.CreateDefaultHat(sim, drone), null);
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
public class Dynamite : Growable
{
	public const string Name = "dynamite";

	public const float BaseExplosionEnergy = 1000f;

	public const float ExplosionUpgradeBase = 1.3f;

	protected override double YieldFactor => 1.0;

	public override void OnDig(Drone drone, ItemBlock drops, ref double ops)
	{
		base.OnDig(drone, drops, ref ops);
		ops = Math.Min(sim.actionOps, ops);
		drops.Clear();
		GridManager grid = sim.farm.grid;
		Explode(grid, new Vector3Int(z: grid.CellAt(base.pos.x, base.pos.y).depth, x: base.pos.x, y: base.pos.y), GetExplosionEnergy(sim.farm));
	}

	protected override void OnFullyGrown()
	{
		base.OnFullyGrown();
		GridManager grid = sim.farm.grid;
		ref GridManager.Cell reference = ref grid.CellAt(base.pos.x, base.pos.y);
		GroundData.Ground ground = grid.GroundAt(base.pos.x, base.pos.y, reference.depth);
		if (ground.groundSo.objectName == "soot" && ground.groundSo.GetController(sim.farm.grid) is SweeperController sweeperController)
		{
			sweeperController.ClearAndScorePuzzle(new Vector3Int(base.pos.x, base.pos.y, reference.depth - 1), explode: true);
		}
	}

	public static float GetExplosionEnergy(Farm farm)
	{
		int num = Math.Max(farm.NumUnlocked("dynamite") - 1, 0);
		float num2 = Mathf.Pow(1.3f, num);
		return 1000f * num2;
	}

	public static void Explode(GridManager grid, Vector3Int pos, float explosionEnergy, float explosionSpread = 0.2f, bool collectDrops = false, float crumblePushAngle = 0f)
	{
		ISimRunner simRunner = grid.farm.sim.simRunner;
		if (simRunner != null)
		{
			simRunner.PlayEffect(VFXType.explosion, GridManager.CellToLocal(pos), changeColor: false, default(Color), null, 0f, crumblePushAngle);
		}
		grid.farm.sim.simRunner?.PlaySound(SoundEffectType.Explosion, (Vector2Int)pos);
		ItemBlock explosionDrops = (collectDrops ? ItemBlock.CreateEmpty() : null);
		Action<Vector3Int, GroundSO> onGroundCleared = (collectDrops ? ((Action<Vector3Int, GroundSO>)delegate(Vector3Int clearedPos, GroundSO groundSo)
		{
			if (clearedPos != pos)
			{
				explosionDrops.Add(groundSo.GetDrops(grid.farm, out var _));
			}
		}) : null);
		List<(Vector2Int, int)> list = (collectDrops ? new List<(Vector2Int, int)>() : null);
		Dictionary<Vector3Int, float> dictionary = new Dictionary<Vector3Int, float>();
		Queue<Vector3Int> queue = new Queue<Vector3Int>();
		queue.Enqueue(pos);
		dictionary[pos] = explosionEnergy;
		Vector3Int result;
		while (queue.TryDequeue(out result))
		{
			ref GroundData.Ground reference = ref grid.GroundAt(result);
			dictionary.TryGetValue(result, out var value);
			dictionary[result] = float.NaN;
			value -= (float)reference.hardness;
			GroundData.Chunk chunk = grid.ChunkAt(result.z);
			if (value >= 0f && chunk.IsBlockPresent(result.x, result.y, result.z, grid.WorldSize))
			{
				if (result != pos)
				{
					ref GridManager.Cell reference2 = ref grid.CellAt(result.x, result.y);
					if ((reference2.entity is Dynamite && reference2.depth == result.z) || grid.sweeperController.IsMine(reference.groundSo) || reference.groundSo.objectName == "soot")
					{
						if (reference.groundSo.objectName != "soot")
						{
							grid.farm.sim.simRunner?.PlayEffect(VFXType.explosion, GridManager.CellToLocal(result));
							grid.farm.sim.simRunner?.PlaySound(SoundEffectType.Explosion, (Vector2Int)result);
						}
						value = explosionEnergy;
					}
				}
				if (collectDrops)
				{
					list.Add(((Vector2Int)result, result.z));
				}
				else
				{
					grid.ClearGroundWithCaveins((Vector2Int)result, result.z);
				}
			}
			float num = value * explosionSpread;
			if (num <= 0f)
			{
				continue;
			}
			foreach (Vector3Int item in GridManager.Neighboring3DPositions(result))
			{
				if (grid.IsWithinBounds((Vector2Int)item) && item.z >= 0)
				{
					if (!dictionary.TryGetValue(item, out var value2))
					{
						value2 = 0f;
						queue.Enqueue(item);
					}
					if (!float.IsNaN(value2))
					{
						dictionary[item] = value2 + num;
					}
				}
			}
		}
		if (!collectDrops)
		{
			return;
		}
		foreach (var (vector2Int, upToDepth) in list)
		{
			grid.ClearGround(vector2Int, upToDepth, crumbleEffect: true, onGroundCleared);
		}
		foreach (var (aroundPos, upToDepth2) in list)
		{
			grid.ClearGroundWithCaveins(aroundPos, upToDepth2);
		}
		grid.farm.CollectItems(explosionDrops, GridManager.CellToLocal(pos));
	}
}
[CreateAssetMenu(fileName = "Entity", menuName = "ScriptableObjects/Entity", order = 1)]
public class EntitySO : ScriptableObject, IPyObject
{
	[Header("Entity")]
	public string className;

	public string objectName;

	public string description;

	public string docs;

	public Color color;

	public List<Mesh> meshes;

	public List<Mesh> gooMeshes;

	public bool canBeSwapped;

	public List<string> placeableOn;

	public SoundEffectType harvestSound;

	public bool showUnclamped;

	public EDlcType dlc;

	[Header("Growable")]
	public bool verticalGrowth;

	public float meanGrowTime;

	public float growTimeDeviationPercent;

	public bool canHaveCompanion;

	public bool randomRotation = true;

	public bool canBePlanted = true;

	public bool canBeOverplanted;

	public bool canBeWeird = true;

	[Header("Drops")]
	public string dropItem;

	[NonSerialized]
	public int dropItemId;

	public double dropAmount = 1.0;

	public string yieldUpgradeName;

	public ItemBlock cost;

	public bool CanBePlacedOn(string ground)
	{
		if (!canBePlanted)
		{
			return false;
		}
		if (placeableOn == null || placeableOn.Count == 0)
		{
			return false;
		}
		bool num = placeableOn[0] == "all";
		bool flag = placeableOn.Contains(ground);
		return num != flag;
	}

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
			List<string> values = placeableOn.ConvertAll((string ground) => "`Grounds." + CodeUtilities.ToUpperSnake(ground) + "`");
			return string.Format(Localizer.Localize("plant_tooltip_template"), Localizer.Localize(description), num, num2, string.Join(" or ", values));
		}
		return Localizer.Localize(description);
	}

	public override string ToString()
	{
		return "Entities." + CodeUtilities.ToUpperSnake(objectName);
	}

	public bool IsBamboo()
	{
		return dropItemId == StringIds.BambooItemId;
	}
}
public class Entity
{
	public EntitySO objectSO;

	public Vector3Int pos3;

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

	public Vector2Int pos => (Vector2Int)pos3;

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
		Vector3 localPosition = LocalPosition;
		Vector3 s = scaleEnd;
		if (scaleEndTime > sim.CurrentTime)
		{
			s = Vector3.Lerp(t: 1f - (float)((scaleEndTime - sim.CurrentTime) / scaleDuration), a: scaleStart, b: scaleEnd);
		}
		Quaternion q = ((!(rotationEndTime > sim.CurrentTime)) ? rotationEnd : Quaternion.Slerp(t: 1f - (float)((rotationEndTime - sim.CurrentTime) / rotationDuration), a: rotationStart, b: rotationEnd));
		if (s.x == 0f || s.y == 0f || s.z == 0f)
		{
			s = Vector3.zero;
		}
		return Matrix4x4.TRS(localPosition, q, s);
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

	public virtual void OnDig(Drone drone, ItemBlock drops, ref double ops)
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
		Entity[] neighbors = sim.farm.grid.GetNeighbors(pos);
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
		if (sim.simRunner != null && sim.simRunner.TimeFactor == 1.0)
		{
			Vector3 localPosition = LocalPosition;
			sim.simRunner.PlayEffect(VFXType.dust, localPosition);
			sim.simRunner.PlayEffect(VFXType.hit, localPosition, changeColor: true, objectSO.color);
			if (addStars)
			{
				sim.simRunner.PlayEffect(VFXType.stars, localPosition);
			}
		}
	}
}
public abstract class GridController
{
	protected GridManager gm;

	public string Name { get; }

	public GridController(string name, GridManager gridManager)
	{
		Name = name;
		gm = gridManager;
	}

	public virtual void ClearGrid()
	{
	}

	public virtual void OnChunksAddedOrRemoved(int startDepth, int endDepth)
	{
	}

	public virtual IPyObject Measure(Drone drone, Vector3Int pos)
	{
		return null;
	}

	public virtual ItemBlock GetHoveredTooltip(StringBuilder builder, Vector3Int hoveredBlock, in GroundData.Ground ground)
	{
		return null;
	}

	public virtual int OnMove(Vector2Int oldPos, Vector2Int newPos, ProgramState programState)
	{
		return -1;
	}

	public virtual void OnDig(Drone drone, Vector2Int dugPosition, ref double ops)
	{
	}

	public virtual void OnAfterDig(Drone drone, Vector2Int dugPosition)
	{
	}

	public virtual bool OnAfterPush(Drone drone, Vector3Int from, Vector3Int to)
	{
		return false;
	}

	public virtual void OnDroneRemoved(int droneId)
	{
	}

	public virtual void OnDroneChangedId(int oldDroneId, int newDroneId)
	{
	}
}
[CreateAssetMenu(fileName = "Ground", menuName = "ScriptableObjects/Ground", order = 1)]
public class GroundSO : ScriptableObject, IPyObject
{
	[Serializable]
	public class GroundDecoration
	{
		public Mesh mesh;

		public Mesh[] wetMeshes;

		public float probability;

		public bool top;

		public bool sides;

		public bool randomRotation = true;

		public float fixedRotation = 90f;

		[NonSerialized]
		public FarmRenderer.FaceDirection? face;

		public bool MatchesFace(FarmRenderer.FaceDirection direction)
		{
			if (face.HasValue)
			{
				return face.Value == direction;
			}
			return true;
		}

		public Mesh MeshForWaterVolume(double waterVolume)
		{
			int num = WaterVariantIndex(waterVolume);
			if (num != 0)
			{
				return wetMeshes[num - 1];
			}
			return mesh;
		}

		public int WaterVariantIndex(double waterVolume)
		{
			if (wetMeshes == null || wetMeshes.Length == 0)
			{
				return 0;
			}
			double num = Math.Clamp(waterVolume + 0.1, 0.0, 1.0);
			int num2 = wetMeshes.Length + 1;
			return Math.Min((int)(num * (double)num2), num2 - 1);
		}
	}

	public string objectName;

	public string description;

	public string docs;

	public EDlcType dlc;

	public string controller;

	public bool allowedToPlaceManually;

	[Header("Ground Properties")]
	public int maxHardness;

	public int stability;

	public bool autodestroyWhenDugBeside = true;

	public bool isTillable;

	public bool isPushable;

	public float yieldMultiplierForGrowables = 1f;

	[Header("Drops")]
	public string dropItem;

	[NonSerialized]
	public int dropItemId;

	public double dropAmount = 1.0;

	public string yieldUpgradeName;

	[Header("Appearance")]
	public bool matchSurroundingGroundColor;

	public bool isWhitelistedToSpreadGroundColor;

	public bool moreVisibleCavein;

	public Gradient colorGradient;

	public SoundEffectType digSound;

	public GroundDecoration[] decorations;

	public IPyObject DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}

	public bool PyEquals(IPyObject obj, ref int steps)
	{
		CodeUtilities.AssertMaxComparisonDepth(ref steps);
		if (!(obj is GroundSO groundSO))
		{
			return false;
		}
		return string.Equals(objectName, groundSO.objectName);
	}

	public int PyGetHashCode()
	{
		return objectName?.GetHashCode() ?? 0;
	}

	public string GetDescription()
	{
		return Localizer.Localize(description);
	}

	public override string ToString()
	{
		return "Grounds." + CodeUtilities.ToUpperSnake(objectName);
	}

	public GridController GetController(GridManager gridManager)
	{
		if (!string.IsNullOrEmpty(controller))
		{
			return gridManager.GetController(controller);
		}
		return null;
	}

	public ItemBlock GetDrops(Farm farm, out Duration collectionDuration)
	{
		collectionDuration = Duration.FromSeconds(0.0);
		double num = dropAmount;
		if (yieldUpgradeName != "")
		{
			num = ((!(yieldUpgradeName == "ore_boost")) ? (num * (double)Math.Max(1 << farm.NumUnlocked(yieldUpgradeName) - 1, 1)) : (num * (double)Math.Max(1 << farm.NumUnlocked(yieldUpgradeName), 1)));
		}
		return new ItemBlock(dropItemId, num);
	}

	public Mesh SampleDecoration(int x, int y, int depth, FarmRenderer.FaceDirection side, out float rotation, double waterVolume = 0.0)
	{
		rotation = 90f;
		if (decorations == null || decorations.Length == 0)
		{
			return null;
		}
		for (int i = 0; i < decorations.Length; i++)
		{
			if (decorations[i].probability <= 0f || (side == FarmRenderer.FaceDirection.Top && !decorations[i].top) || (side != FarmRenderer.FaceDirection.Top && !decorations[i].sides) || !decorations[i].MatchesFace(side))
			{
				continue;
			}
			UnityEngine.Random.InitState(HashCode.Combine(x, y, depth, side, i));
			if (UnityEngine.Random.value < decorations[i].probability)
			{
				if (decorations[i].randomRotation)
				{
					rotation = UnityEngine.Random.Range(0, 4) * 90;
				}
				else
				{
					rotation = decorations[i].fixedRotation;
				}
				return decorations[i].MeshForWaterVolume(waterVolume);
			}
		}
		return null;
	}

	public bool CrossesWaterDecorationThreshold(double oldWaterVolume, double newWaterVolume)
	{
		if (decorations == null)
		{
			return false;
		}
		GroundDecoration[] array = decorations;
		foreach (GroundDecoration groundDecoration in array)
		{
			if (groundDecoration.top && groundDecoration.WaterVariantIndex(oldWaterVolume) != groundDecoration.WaterVariantIndex(newWaterVolume))
			{
				return true;
			}
		}
		return false;
	}
}
public class Growable : Entity
{
	private bool isGrown;

	private Duration growTime;

	private double prevGrowTimeFactor = 1.0;

	private Duration growStart;

	private double grownPercent;

	private float randomFactor;

	public bool canBePlanted = true;

	public List<string> growsOn;

	private EntitySO companionType;

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

	protected virtual float InitialGrowthScale => 0.1f;

	protected virtual double GrowTimeFactor
	{
		get
		{
			double num = 1.0;
			num += sim.farm.grid.CellAt(base.pos).waterVolume * 4.0;
			return 1.0 / num;
		}
	}

	protected override double YieldFactor => base.YieldFactor * (double)((!HasCompanion()) ? 1 : (5 << sim.farm.NumUnlocked("polyculture"))) * (double)GetGroundYieldMultiplier();

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		foreach (var mesh in base.GetMeshes())
		{
			yield return mesh;
		}
		if (weird)
		{
			yield return (objectSO.gooMeshes[gooIndex], Matrix4x4.Translate(sim.farm.grid.CellToLocal(base.pos)));
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

	public void Instagrow()
	{
		if (!isGrown)
		{
			StopGrowing();
			grownPercent = 1.0;
			Grow();
			scaleEndTime = sim.CurrentTime;
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
		float num = Mathf.Lerp(InitialGrowthScale, 1f, (float)grownPercent);
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
			if (growTime.nanoseconds > 0)
			{
				grownPercent += (sim.CurrentTime - growStart) / growTime;
			}
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

	protected virtual ItemBlock GetHarvestYield()
	{
		return GetYield();
	}

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		base.Harvest(out collectionDuration);
		ItemBlock result = (Harvestable ? GetHarvestYield() : ItemBlock.CreateEmpty());
		sim.farm.grid.RemoveEntity(base.pos);
		HarvestEffects(HasCompanion());
		return result;
	}

	public void Fertilize(int number)
	{
		weird = true;
		if (isGrown)
		{
			OnAfterFertilize();
			return;
		}
		StopGrowing();
		grownPercent = Math.Min(grownPercent + Duration.FromSeconds(2 * number) / GetGrowTime(), 1.0);
		TryScheduleGrow();
		OnAfterFertilize();
	}

	public void ToggleWeird()
	{
		weird = !weird;
		gooIndex = sim.randomVarious.Next(objectSO.gooMeshes.Count - 1);
		bool flag = !weird;
		Entity[] neighbors = sim.farm.grid.GetNeighbors(base.pos);
		for (int i = 0; i < neighbors.Length; i++)
		{
			if (neighbors[i] is Growable growable && growable.objectSO.canBeWeird)
			{
				growable.weird = !growable.weird;
				growable.gooIndex = sim.randomVarious.Next(growable.objectSO.gooMeshes.Count - 1);
				flag = flag || !growable.weird;
			}
		}
		if (flag)
		{
			sim.UnlockAchievement("HEALER");
		}
	}

	private float GetGroundYieldMultiplier()
	{
		return sim.farm.grid.GroundAt(base.pos).groundSo.yieldMultiplierForGrowables;
	}

	protected bool HasCompanion()
	{
		if (!objectSO.canHaveCompanion || sim.farm.grid.CellAt(companionPos).entity == null)
		{
			return false;
		}
		if (sim.farm.grid.CellAt(companionPos).entity.objectSO.objectName == companionType.objectName)
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
		return PyTuple.From(companionType, PyTuple.From(companionPos));
	}

	private void ChooseCompanion()
	{
		int num = 3;
		do
		{
			companionPos = new Vector2Int(sim.randomPoly.Next(-num, num + 1), sim.randomPoly.Next(-num, num + 1));
		}
		while ((sim.farm.grid.Wrap(base.pos + companionPos) == base.pos || Mathf.Abs(companionPos.x) + Mathf.Abs(companionPos.y) > num) && sim.farm.grid.WorldSize.y != 1);
		companionPos = sim.farm.grid.Wrap(base.pos + companionPos);
		do
		{
			companionType = sim.randomPoly.Next(4) switch
			{
				2 => ResourceManager.GetEntity("carrot"), 
				1 => ResourceManager.GetEntity("bush"), 
				0 => ResourceManager.GetEntity("grass"), 
				_ => ResourceManager.GetEntity("tree"), 
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
		RestartGrowth();
	}

	public void RestartGrowth()
	{
		isGrown = false;
		growStart = sim.CurrentTime;
		grownPercent = 0.0;
		randomFactor = (float)sim.randomVarious.NextDouble() * objectSO.growTimeDeviationPercent * 2f + 1f - objectSO.growTimeDeviationPercent;
		growTime = GetGrowTime();
		TryScheduleGrow();
	}

	public virtual void OnAfterFertilize()
	{
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
public class HedgePlant : Entity
{
	public bool[] walls;

	public int mazeSize;

	public Vector2Int lowLeftCorner;

	public bool removed;

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		for (int i = 0; i < 4; i++)
		{
			if (walls[i] && (i < 2 || base.pos.x == lowLeftCorner.x || base.pos.y == lowLeftCorner.y))
			{
				Quaternion q = Quaternion.AngleAxis(90 * i, Vector3.forward);
				yield return (objectSO.meshes[0], Matrix4x4.TRS(base.LocalPosition, q, Vector3.one));
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
				Vector2Int vector2Int = new Vector2Int(i, j) + lowLeftCorner;
				if (sim.farm.grid.CellAt(vector2Int).entity is HedgePlant { removed: false } hedgePlant)
				{
					hedgePlant.removed = true;
					sim.farm.grid.RemoveEntity(vector2Int);
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
		removed = true;
	}

	public override IPyObject Measure()
	{
		for (int i = lowLeftCorner.x; i < lowLeftCorner.x + mazeSize; i++)
		{
			for (int j = lowLeftCorner.y; j < lowLeftCorner.y + mazeSize; j++)
			{
				Vector2Int position = new Vector2Int(i, j);
				if (sim.farm.grid.GetEntity<Treasure>(position) != null)
				{
					return PyTuple.From(position);
				}
			}
		}
		return PyNone.Instance;
	}
}
public class MushroomController : GridController
{
	private class Stratum
	{
		public int minDepth;

		public int maxDepth;

		public int stratumIndex;

		public int totalMushrooms;

		public int matchedMushrooms;
	}

	public new const string Name = "Mushroom";

	public const string GroundMushroomName = "mushroom";

	public const string StackRewardItemName = "mushroom";

	public const string YieldUpgradeName = "mushrooms";

	public const int MaxMushroomTypes = 6;

	public const int MaxActiveStrata = 10;

	private Dictionary<int, Stratum> strata = new Dictionary<int, Stratum>();

	private MushroomGroundSO mushroomGround;

	private MushroomGroundSO[][] strataGroundVariants;

	private int nextStrataIndex;

	private int stackRewardItemId;

	public MushroomGroundSO[] GetNextStrataGrounds(int minDepth, int maxDepth)
	{
		int num = nextStrataIndex;
		nextStrataIndex = (nextStrataIndex + 1) % 10;
		if (strata.ContainsKey(num))
		{
			UnityEngine.Debug.LogWarning($"MushroomController: Overwriting stratum with index {num}");
		}
		strata[num] = new Stratum
		{
			minDepth = minDepth,
			maxDepth = maxDepth,
			stratumIndex = num,
			totalMushrooms = -1
		};
		return strataGroundVariants[num];
	}

	public int GetMushroomTypeForGround(GroundSO ground)
	{
		if (!(ground is MushroomGroundSO mushroomGroundSO))
		{
			return -1;
		}
		return mushroomGroundSO.mushroomType;
	}

	public double GetYieldForMushroom()
	{
		int num = Math.Max(1 << gm.farm.NumUnlocked("mushrooms") - 1, 1);
		return 1 * num;
	}

	public MushroomController(GridManager gm)
		: base("Mushroom", gm)
	{
		stackRewardItemId = StringIds.GetItemId("mushroom");
		mushroomGround = (MushroomGroundSO)ResourceManager.GetGround("mushroom");
		MushroomGroundSO[] array = new MushroomGroundSO[6];
		GradientColorKey[] array2 = new GradientColorKey[2]
		{
			new GradientColorKey(Color.black, 0f),
			new GradientColorKey(Color.black, 1f)
		};
		GradientAlphaKey[] alphaKeys = new GradientAlphaKey[2]
		{
			new GradientAlphaKey(1f, 0f),
			new GradientAlphaKey(1f, 1f)
		};
		Color[] mushroomColors = DesignConstants.Inst.colors.mushroomColors;
		for (int i = 0; i < 6; i++)
		{
			Color color = mushroomColors[i % mushroomColors.Length];
			array2[0].color = color;
			array2[1].color = color;
			MushroomGroundSO mushroomGroundSO = UnityEngine.Object.Instantiate(mushroomGround);
			mushroomGroundSO.mushroomStratumIndex = 0;
			mushroomGroundSO.mushroomType = i;
			mushroomGroundSO.colorGradient.SetKeys(array2, alphaKeys);
			mushroomGroundSO.decorations = new GroundSO.GroundDecoration[1] { mushroomGround.decorations[i % mushroomGround.decorations.Length] };
			array[i] = mushroomGroundSO;
		}
		strataGroundVariants = new MushroomGroundSO[10][];
		for (int j = 0; j < 10; j++)
		{
			MushroomGroundSO[] array3;
			if (j == 0)
			{
				array3 = array;
			}
			else
			{
				array3 = new MushroomGroundSO[6];
				for (int k = 0; k < 6; k++)
				{
					MushroomGroundSO mushroomGroundSO2 = UnityEngine.Object.Instantiate(array[k]);
					mushroomGroundSO2.mushroomStratumIndex = j;
					mushroomGroundSO2.mushroomType = k;
					array3[k] = mushroomGroundSO2;
				}
			}
			strataGroundVariants[j] = array3;
		}
	}

	public override void ClearGrid()
	{
		base.ClearGrid();
		strata.Clear();
	}

	public override void OnChunksAddedOrRemoved(int startDepth, int endDepth)
	{
		base.OnChunksAddedOrRemoved(startDepth, endDepth);
		for (int i = 0; i < 10; i++)
		{
			if (!strata.TryGetValue(i, out var value))
			{
				continue;
			}
			if (value.maxDepth <= startDepth || endDepth < value.minDepth)
			{
				strata.Remove(i);
			}
			else
			{
				if (value.totalMushrooms >= 0)
				{
					continue;
				}
				value.totalMushrooms = 0;
				Vector2Int worldSize = gm.WorldSize;
				for (int j = value.minDepth; j < value.maxDepth; j++)
				{
					for (int k = 0; k < worldSize.y; k++)
					{
						for (int l = 0; l < worldSize.x; l++)
						{
							if (gm.GroundAt(l, k, j).groundSo is MushroomGroundSO)
							{
								value.totalMushrooms++;
							}
						}
					}
				}
			}
		}
	}

	public override IPyObject Measure(Drone drone, Vector3Int pos)
	{
		ref GroundData.Ground reference = ref gm.GroundAt(pos);
		if (reference.groundSo.objectName != "mushroom")
		{
			return PyNone.Instance;
		}
		int mushroomTypeForGround = GetMushroomTypeForGround(reference.groundSo);
		if (mushroomTypeForGround < 0)
		{
			UnityEngine.Debug.LogError("MushroomController: Ground not a mushroom ground (" + reference.groundSo?.GetType().Name + ")");
			return PyNone.Instance;
		}
		return new PyNumber(mushroomTypeForGround);
	}

	public override ItemBlock GetHoveredTooltip(StringBuilder builder, Vector3Int hoveredBlock, in GroundData.Ground ground)
	{
		builder.Append(Localizer.Localize("runtime_mushroom_tooltip")).Append("\n");
		return new ItemBlock(stackRewardItemId, GetYieldForMushroom());
	}

	public override bool OnAfterPush(Drone drone, Vector3Int from, Vector3Int to)
	{
		ref GroundData.Ground reference = ref gm.GroundAt(to);
		if (reference.groundSo.objectName != "mushroom")
		{
			UnityEngine.Debug.LogError("MushroomController: Unexpected ground type at push destination (" + reference.groundSo.objectName + ")");
			return false;
		}
		ref GroundData.Ground reference2 = ref gm.GroundAt(to + GridManager.down);
		if (reference2.groundSo.objectName != "mushroom")
		{
			return false;
		}
		MushroomGroundSO mushroomGroundSO = reference.groundSo as MushroomGroundSO;
		MushroomGroundSO mushroomGroundSO2 = reference2.groundSo as MushroomGroundSO;
		if (mushroomGroundSO == null || mushroomGroundSO2 == null)
		{
			return false;
		}
		if (mushroomGroundSO.mushroomType != mushroomGroundSO2.mushroomType)
		{
			return false;
		}
		int lifetimeCount = ((from.z == to.z) ? 1 : 2);
		gm.farm.sim.simRunner.SlideAndPopBlockEffect((Vector2Int)from, (Vector2Int)to, to.z, lifetimeCount);
		gm.farm.sim.simRunner.SlideAndPopBlockEffect((Vector2Int)to, (Vector2Int)to, to.z + 1, lifetimeCount);
		gm.farm.sim.simRunner.PlaySound(SoundEffectType.DigMushroom, (Vector2Int)to);
		gm.ClearGround((Vector2Int)to, to.z + 2, crumbleEffect: false);
		gm.farm.CollectItem(stackRewardItemId, GetYieldForMushroom(), GridManager.CellToLocal(to));
		Stratum value;
		if (mushroomGroundSO.mushroomStratumIndex != mushroomGroundSO2.mushroomStratumIndex)
		{
			gm.farm.sim.UnlockAchievement("MUSHROOM_STARTUM_SKIP");
		}
		else if (!strata.TryGetValue(mushroomGroundSO.mushroomStratumIndex, out value))
		{
			UnityEngine.Debug.LogError($"MushroomController: Could not get startum for index {mushroomGroundSO.mushroomStratumIndex}");
		}
		else
		{
			value.matchedMushrooms += 2;
			float num = 100f * (float)value.matchedMushrooms / (float)value.totalMushrooms;
			if (num > 95f)
			{
				gm.farm.sim.UnlockAchievement("MUSHROOM_STRATUM_OPTIMAL");
			}
			UnityEngine.Debug.Log($"MushroomController: Matched {value.matchedMushrooms} of {value.totalMushrooms} blocks ({num:00.#}%)");
		}
		return true;
	}
}
public class MushroomGroundSO : GroundSO
{
	[NonSerialized]
	public int mushroomType;

	[NonSerialized]
	public int mushroomStratumIndex;
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
			sim.farm.grid.SetEntity(base.pos, "dead_pumpkin");
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
		if (size.x == 32)
		{
			sim.UnlockAchievement("GIANT_PUMPKIN");
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
public class PumpkinController : GridController
{
	public new const string Name = "Pumpkin";

	private const int greenOffset = 5;

	private Dictionary<Vector2Int, Pumpkin> pumpkins = new Dictionary<Vector2Int, Pumpkin>();

	private Dictionary<Pumpkin, RectInt> groups = new Dictionary<Pumpkin, RectInt>();

	public PumpkinController(GridManager gm)
		: base("Pumpkin", gm)
	{
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
			Pumpkin pumpkin = gm.CellAt(item).entity as Pumpkin;
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
			if (gm.CellAt(item).entity is Pumpkin { weird: not false })
			{
				numWeird++;
			}
		}
		return size + Vector2Int.one;
	}

	private void MergeWithOthers(Vector2Int pos)
	{
		int y = gm.farm.grid.WorldSize.y;
		Vector2Int[] array = new Vector2Int[y * y];
		for (int i = 0; i < array.Length; i++)
		{
			if (!pumpkins.TryGetValue(new Vector2Int(i % y, i / y), out var value))
			{
				array[i] = Vector2Int.zero;
			}
			else
			{
				array[i] = new Vector2Int(1, value.pos3.z);
			}
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
				if (num2 + 1 < y && num3 + 1 < y)
				{
					Vector2Int vector2Int = array[j];
					Vector2Int vector2Int2 = array[num2 + 1 + y * num3];
					Vector2Int vector2Int3 = array[num2 + y * (num3 + 1)];
					Vector2Int vector2Int4 = array[num2 + 1 + y * (num3 + 1)];
					if (vector2Int.x == num - 1 && vector2Int2.x == num - 1 && vector2Int2.y == vector2Int.y && vector2Int3.x == num - 1 && vector2Int3.y == vector2Int.y && vector2Int4.x == num - 1 && vector2Int4.y == vector2Int.y)
					{
						array[j].x = num;
						flag = true;
					}
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

	private RectInt LargestSquare(Vector2Int[] dp, int n, int squareSize, Vector2Int pos)
	{
		while (squareSize > 1)
		{
			for (int i = 0; i < dp.Length; i++)
			{
				RectInt rectInt = new RectInt(new Vector2Int(i % n, i / n), new Vector2Int(squareSize - 1, squareSize - 1));
				if (dp[i].x >= squareSize && IsInRect(rectInt, pos) && !HasOverlaps(rectInt))
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
public class PyramidController : GridController
{
	public enum RestoredPyramidType
	{
		Undefined,
		Sand,
		Color
	}

	public class Pyramid
	{
		public Vector3Int startingCorner;

		public int baseWidth;

		public int height;

		public Pyramid(int baseWidth, Vector3Int startingCorner)
		{
			this.baseWidth = baseWidth;
			this.startingCorner = startingCorner;
			height = baseWidth / 2 + 1;
		}
	}

	public readonly GroundSO pyramidGround;

	public readonly GroundSO colorRedGround;

	public readonly GroundSO colorGreenGround;

	public readonly GroundSO colorBlueGround;

	public new const string Name = "Pyramid";

	private List<Pyramid> pyramids = new List<Pyramid>();

	public PyramidController(GridManager gm)
		: base("Pyramid", gm)
	{
		pyramidGround = ResourceManager.GetGround("sand");
		colorRedGround = ResourceManager.GetGround("block_red");
		colorGreenGround = ResourceManager.GetGround("block_green");
		colorBlueGround = ResourceManager.GetGround("block_blue");
	}

	public bool IsPyramidGround(GroundSO ground)
	{
		if (!(ground == pyramidGround) && !(ground == colorRedGround) && !(ground == colorGreenGround))
		{
			return ground == colorBlueGround;
		}
		return true;
	}

	public void AddPyramid(int baseWidth, Vector3Int startingCorner)
	{
		pyramids.Add(new Pyramid(baseWidth, startingCorner));
	}

	public void ClearOldPyramids(GridManager gridManager)
	{
		int minDepth = int.MaxValue;
		GridManager.Cell[] cells = gridManager.cells;
		for (int i = 0; i < cells.Length; i++)
		{
			GridManager.Cell cell = cells[i];
			minDepth = Math.Min(cell.depth, minDepth);
		}
		pyramids = pyramids.Where((Pyramid p) => p.startingCorner.z + 1 >= minDepth).ToList();
	}

	public override void ClearGrid()
	{
		pyramids.Clear();
	}

	private void ClearPyramid(Pyramid pyramid, RestoredPyramidType pyramidType)
	{
		pyramids.Remove(pyramid);
		Vector2Int vector2Int = new Vector2Int(pyramid.startingCorner.x + pyramid.baseWidth / 2, pyramid.startingCorner.y + pyramid.baseWidth / 2);
		float pyramidRevealDelayPerBlock = DesignConstants.Inst.vfx.pyramidRevealDelayPerBlock;
		float pyramidPopEffectVelocityHorizontal = DesignConstants.Inst.vfx.pyramidPopEffectVelocityHorizontal;
		float pyramidPopEffectVelocityZ = DesignConstants.Inst.vfx.pyramidPopEffectVelocityZ;
		for (int i = pyramid.startingCorner.x; i < pyramid.startingCorner.x + pyramid.baseWidth; i++)
		{
			for (int j = pyramid.startingCorner.y; j < pyramid.startingCorner.y + pyramid.baseWidth; j++)
			{
				gm.ClearGround(new Vector2Int(i, j), pyramid.startingCorner.z + 1, crumbleEffect: false);
				int num = i - pyramid.startingCorner.x;
				int num2 = j - pyramid.startingCorner.y;
				int num3 = Mathf.Min(num, num2, pyramid.baseWidth - num - 1, pyramid.baseWidth - num2 - 1);
				Vector2 vector = new Vector2(i - vector2Int.x, j - vector2Int.y);
				Vector3 normalized = new Vector3(0f - vector.x, vector.y, 0f).normalized;
				gm.farm.sim.simRunner.DelayedPopBlockEffect(new Vector3Int(i, j, pyramid.startingCorner.z - num3), vector.magnitude * pyramidRevealDelayPerBlock, normalized * pyramidPopEffectVelocityHorizontal + new Vector3(0f, 0f, 1f) * pyramidPopEffectVelocityZ);
			}
		}
		gm.farm.sim.simRunner?.PlaySound(SoundEffectType.PyramidCompleted, vector2Int);
		double num4 = pyramid.baseWidth;
		float num5 = Mathf.Max(1 << gm.farm.NumUnlocked("pyramid") - 1, 1);
		Sunflower obj = (Sunflower)gm.SetEntity(vector2Int, "sunflower");
		obj.pyramidYieldOverride = num4 * num4 * (double)num5 * 0.25;
		obj.pyramidSizeMultiplier = pyramid.height - 1;
		obj.Instagrow();
		if (pyramid.baseWidth >= 29)
		{
			gm.farm.sim.UnlockAchievement("RESTORE_MAX_PYRAMID");
		}
		if (pyramidType == RestoredPyramidType.Color)
		{
			gm.farm.sim.UnlockAchievement("RESTORE_COLOR_PYRAMID");
		}
	}

	private bool IsPyramidComplete(Pyramid pyramid, out RestoredPyramidType pyramidType)
	{
		pyramidType = RestoredPyramidType.Undefined;
		for (int i = 0; i < pyramid.baseWidth; i++)
		{
			for (int j = 0; j < pyramid.baseWidth; j++)
			{
				int x = j + pyramid.startingCorner.x;
				int y = i + pyramid.startingCorner.y;
				int num = pyramid.startingCorner.z - PyramidFeature.PyramidHeight(j, i, pyramid.baseWidth);
				for (int num2 = pyramid.startingCorner.z; num2 > num; num2--)
				{
					if (!gm.ChunkAt(num2).IsBlockPresent(x, y, num2, gm.WorldSize))
					{
						return false;
					}
					GroundSO groundSo = gm.GroundAt(x, y, num2).groundSo;
					if (groundSo == colorRedGround || groundSo == colorGreenGround || groundSo == colorBlueGround)
					{
						if (pyramidType == RestoredPyramidType.Undefined)
						{
							pyramidType = RestoredPyramidType.Color;
						}
						else if (pyramidType != RestoredPyramidType.Color)
						{
							return false;
						}
					}
					else
					{
						if (!(groundSo == pyramidGround))
						{
							return false;
						}
						if (pyramidType == RestoredPyramidType.Undefined)
						{
							pyramidType = RestoredPyramidType.Sand;
						}
						else if (pyramidType != RestoredPyramidType.Sand)
						{
							return false;
						}
					}
				}
				if (gm.ChunkAt(num).IsBlockPresent(x, y, num, gm.WorldSize))
				{
					return false;
				}
			}
		}
		return true;
	}

	public bool ClearPyramidIfComplete(Pyramid pyramid)
	{
		if (IsPyramidComplete(pyramid, out var pyramidType))
		{
			ClearPyramid(pyramid, pyramidType);
			return true;
		}
		return false;
	}

	public Pyramid GetPyramidAtPos(Vector3Int pos)
	{
		return pyramids.FirstOrDefault((Pyramid p) => pos.x >= p.startingCorner.x && pos.y >= p.startingCorner.y && pos.x < p.startingCorner.x + p.baseWidth && pos.y < p.startingCorner.y + p.baseWidth && pos.z <= p.startingCorner.z && pos.z > p.startingCorner.z - PyramidFeature.PyramidHeight(pos.x - p.startingCorner.x, pos.y - p.startingCorner.y, p.baseWidth));
	}

	public bool IsInPyramid(Vector3Int pos)
	{
		return pyramids.Any((Pyramid p) => pos.x >= p.startingCorner.x && pos.y >= p.startingCorner.y && pos.x < p.startingCorner.x + p.baseWidth && pos.y < p.startingCorner.y + p.baseWidth && pos.z <= p.startingCorner.z && pos.z > p.startingCorner.z + 1 - Mathf.Min(Mathf.Min(pos.x - p.startingCorner.x, pos.y - p.startingCorner.y), Mathf.Min(p.startingCorner.x + p.baseWidth - pos.x, p.startingCorner.y + p.baseWidth - pos.y)));
	}
}
public class Sunflower : Growable
{
	private int number;

	private bool getBoost;

	public double? pyramidYieldOverride;

	public float pyramidSizeMultiplier = 1f;

	protected override double YieldFactor
	{
		get
		{
			double? num = pyramidYieldOverride;
			if (num.HasValue)
			{
				return num.GetValueOrDefault();
			}
			if (getBoost)
			{
				return 8.0 * base.YieldFactor;
			}
			return base.YieldFactor;
		}
	}

	public bool WasSpawnedFromPyramid()
	{
		return pyramidYieldOverride.HasValue;
	}

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		IEnumerable<Entity> source = from c in sim.farm.grid.cells
			select c.entity into f
			where f is Sunflower
			select f;
		getBoost = number == source.Max((Entity s) => ((Sunflower)s).number) && source.Count() >= 10;
		bool hadIncorrectSunflowerHarvest = sim.farm.grid.hadIncorrectSunflowerHarvest;
		sim.farm.grid.hadIncorrectSunflowerHarvest = !getBoost;
		if (hadIncorrectSunflowerHarvest)
		{
			getBoost = false;
		}
		if (getBoost)
		{
			sim.simRunner.PlayEffect(VFXType.stars, base.LocalPosition);
		}
		if (WasSpawnedFromPyramid())
		{
			sim.IncrementAchievementStat("total_pyramid", 1);
		}
		return base.Harvest(out collectionDuration);
	}

	public override ItemBlock GetYield()
	{
		IEnumerable<Entity> source = from c in sim.farm.grid.cells
			select c.entity into f
			where f is Sunflower
			select f;
		getBoost = number == source.Max((Entity s) => ((Sunflower)s).number) && source.Count() >= 10;
		return base.GetYield();
	}

	protected override ItemBlock GetHarvestYield()
	{
		return base.GetYield();
	}

	public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
	{
		Matrix4x4 transform = GetTransform();
		if (WasSpawnedFromPyramid())
		{
			transform *= Matrix4x4.Scale(Vector3.one * pyramidSizeMultiplier * 0.8f);
			List<Mesh> meshes = objectSO.meshes;
			yield return (meshes[meshes.Count - 1], transform);
		}
		else
		{
			yield return (objectSO.meshes[number - 7], transform);
		}
		if (weird)
		{
			yield return (objectSO.gooMeshes[gooIndex], Matrix4x4.Translate(sim.farm.grid.CellToLocal(base.pos)));
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
public class SweeperController : GridController
{
	private class StratumData
	{
		public int[] neighborMap;

		public int mineCount;

		public int revealedDuds;
	}

	public new const string Name = "Sweeper";

	public const string SpawnEntityName = "dynamite";

	public const string GroundOreName = "dynamite";

	public const string GroundCounterName = "soot";

	public const string UpgradeName = "dynamite";

	private GroundSO oreMine;

	private GroundSO oreDud;

	private GroundSO[] counterGrounds;

	private Dictionary<int, StratumData> strata = new Dictionary<int, StratumData>();

	public double DynamitePerDudBlock => 1.0;

	public (int depth, float ratio) MineRatioMin => (depth: 20, ratio: 0.1f);

	public (int depth, float ratio) MineRatioMax => (depth: 600, ratio: 0.17f);

	public bool IsMine(GroundSO ground)
	{
		if (ground == null)
		{
			return false;
		}
		if (ground.objectName != "dynamite")
		{
			return false;
		}
		return ground != oreDud;
	}

	public float GetMineRatio(int depth)
	{
		if (gm.farm.sim.leaderboardType == LeaderboardType.farm_resources)
		{
			return (MineRatioMin.ratio + MineRatioMax.ratio) / 2f;
		}
		float num = Mathf.Clamp01(((float)depth - (float)MineRatioMin.depth) / (float)(MineRatioMax.depth - MineRatioMin.depth));
		return MineRatioMin.ratio + (MineRatioMax.ratio - MineRatioMin.ratio) * num;
	}

	public double GetYieldFactor()
	{
		return Math.Max(1 << gm.farm.NumUnlocked("dynamite") - 1, 1);
	}

	public SweeperController(GridManager gm)
		: base("Sweeper", gm)
	{
		oreMine = ResourceManager.GetGround("dynamite");
		oreDud = UnityEngine.Object.Instantiate(oreMine);
		oreDud.dropItemId = oreMine.dropItemId;
		counterGrounds = new GroundSO[10];
		GroundSO ground = ResourceManager.GetGround("soot");
		for (int i = 0; i < 10; i++)
		{
			GroundSO groundSO = UnityEngine.Object.Instantiate(ground);
			groundSO.dropItemId = ground.dropItemId;
			groundSO.decorations = new GroundSO.GroundDecoration[1] { ground.decorations[i] };
			counterGrounds[i] = groundSO;
		}
	}

	public override IPyObject Measure(Drone drone, Vector3Int pos)
	{
		if (gm.ChunkAt(pos.z).GroundAt(pos, gm.WorldSize).groundSo?.objectName != "soot")
		{
			return null;
		}
		if (!strata.TryGetValue(pos.z - 1, out var value))
		{
			return null;
		}
		return new PyNumber(GetMineCount(value.neighborMap, pos.x, pos.y, gm.WorldSize.x));
	}

	public override void OnDig(Drone drone, Vector2Int dugPosition, ref double ops)
	{
		Vector3Int vector3Int = (Vector3Int)dugPosition;
		ref GridManager.Cell reference = ref gm.CellAt(vector3Int.x, vector3Int.y);
		vector3Int.z = reference.depth;
		ref GroundData.Ground reference2 = ref gm.GroundAt(vector3Int);
		if (reference2.groundSo.objectName == "soot")
		{
			if (strata.ContainsKey(vector3Int.z - 1))
			{
				ClearAndScorePuzzle(vector3Int + GridManager.up, explode: true);
			}
		}
		else
		{
			if (reference2.groundSo.objectName != "dynamite")
			{
				return;
			}
			Vector2Int worldSize = gm.WorldSize;
			if (!strata.TryGetValue(reference.depth, out var value))
			{
				StratumData stratumData = (strata[reference.depth] = GeneratePuzzle(vector3Int));
				value = stratumData;
			}
			if (IsMine(reference2.groundSo))
			{
				gm.farm.sim.simRunner?.PlaySound(SoundEffectType.DigIntoSweeperMine, dugPosition);
				return;
			}
			GroundData.Chunk chunk = gm.ChunkAt(vector3Int.z);
			chunk.SetBlockPresent(vector3Int.x, vector3Int.y, vector3Int.z, gm.WorldSize, isPresent: false);
			if (GetAndApplyMineCount(value.neighborMap, vector3Int, worldSize.x) == 0)
			{
				HashSet<Vector3Int> hashSet = new HashSet<Vector3Int> { vector3Int };
				Queue<Vector3Int> queue = new Queue<Vector3Int>();
				foreach (Vector2Int item2 in GridManager.Neighboring8Positions((Vector2Int)vector3Int))
				{
					if (gm.IsWithinBounds(item2))
					{
						queue.Enqueue(new Vector3Int(item2.x, item2.y, vector3Int.z));
					}
				}
				Vector3Int result;
				while (queue.TryDequeue(out result))
				{
					if (!hashSet.Add(result) || !chunk.IsBlockPresent(result.x, result.y, result.z, worldSize))
					{
						continue;
					}
					ref GroundData.Ground reference3 = ref chunk.GroundAt(result, worldSize);
					if (reference3.groundSo.objectName != "dynamite")
					{
						continue;
					}
					gm.ClearGroundWithCaveins((Vector2Int)result, result.z);
					if (IsMine(reference3.groundSo) || GetMineCount(value.neighborMap, result.x, result.y, worldSize.x) > 0)
					{
						continue;
					}
					foreach (Vector2Int item3 in GridManager.Neighboring8Positions((Vector2Int)result))
					{
						Vector3Int item = new Vector3Int(item3.x, item3.y, result.z);
						if (!hashSet.Contains(item) && gm.IsWithinBounds(item3))
						{
							queue.Enqueue(item);
						}
					}
				}
			}
			value.revealedDuds++;
			gm.farm.sim.simRunner?.PlaySound(SoundEffectType.CorrectSweeperReveal, dugPosition);
			double n = Math.Ceiling(DynamitePerDudBlock * GetYieldFactor());
			gm.farm.CollectItem(StringIds.GetItemId("dynamite"), n, GridManager.CellToLocal(vector3Int));
			int num = worldSize.x * worldSize.y - value.mineCount;
			if (value.revealedDuds >= num)
			{
				ClearAndScorePuzzle(vector3Int, explode: false);
			}
		}
	}

	public override void OnAfterDig(Drone drone, Vector2Int dugPosition)
	{
		int depth = gm.CellAt(dugPosition).depth;
		if (IsMine(gm.GroundAt(dugPosition, depth - 1).groundSo))
		{
			gm.SetEntity(dugPosition, "dynamite");
		}
	}

	public void ClearAndScorePuzzle(Vector3Int pos, bool explode)
	{
		if (!strata.TryGetValue(pos.z, out var _))
		{
			UnityEngine.Debug.LogError($"SweeperController.ClearAndScorePuzzle: No puzzle registered for depth {pos.z}");
			return;
		}
		GroundData.Chunk chunk = gm.ChunkAt(pos.z);
		Vector2Int worldSize = gm.WorldSize;
		int num = 0;
		for (int i = 0; i < worldSize.x; i++)
		{
			for (int j = 0; j < worldSize.y; j++)
			{
				Vector2Int pos2 = new Vector2Int(i, j);
				if (!chunk.IsBlockPresent(i, j, pos.z, worldSize) || !IsMine(chunk.GroundAt(new Vector3Int(i, j, pos.z), worldSize).groundSo))
				{
					continue;
				}
				bool flag = false;
				foreach (Vector2Int item in GridManager.Neighboring8Positions(pos2))
				{
					if (gm.IsWithinBounds(item) && chunk.IsBlockPresent(item.x, item.y, pos.z, worldSize) && !IsMine(chunk.GroundAt(new Vector3Int(item.x, item.y, pos.z), worldSize).groundSo) && !(item == (Vector2Int)pos))
					{
						flag = true;
						break;
					}
				}
				if (!flag)
				{
					num++;
				}
			}
		}
		double num2 = Math.Ceiling((double)num * (double)num * GetYieldFactor());
		gm.farm.CollectItem(StringIds.GetItemId("dynamite"), num2, GridManager.CellToLocal(pos));
		if (explode)
		{
			UnityEngine.Debug.Log($"Sweeper: Failed! ({num} mines uncovered, gained {num2} dynamite)");
			Dynamite.Explode(gm, pos, 1000f);
		}
		else
		{
			UnityEngine.Debug.Log($"Sweeper: Solved! ({num} mines uncovered, gained {num2} dynamite)");
			for (int k = 0; k < worldSize.x; k++)
			{
				for (int l = 0; l < worldSize.y; l++)
				{
					pos = new Vector3Int(k, l, pos.z);
					gm.ClearGroundWithCaveins((Vector2Int)pos, pos.z + 1);
					ref GroundData.Ground reference = ref gm.GroundAt(pos.x, pos.y, pos.z + 1);
					if (reference.groundSo.objectName == "soot")
					{
						reference.groundSo = counterGrounds[0];
						gm.groundData.MarkPositionChanged(pos);
					}
				}
			}
			gm.farm.sim.UnlockAchievement("DYNAMITE_OPTIMAL");
			if (worldSize.x == 32 && worldSize.y == 32 && pos.z >= MineRatioMax.depth)
			{
				gm.farm.sim.UnlockAchievement("DYNAMITE_MAX_OPTIMAL");
			}
		}
		strata.Remove(pos.z);
	}

	public override void ClearGrid()
	{
		strata.Clear();
	}

	public override void OnChunksAddedOrRemoved(int startDepth, int endDepth)
	{
		if (strata.Count == 0)
		{
			return;
		}
		int[] array = strata.Keys.ToArray();
		foreach (int num in array)
		{
			if (num < startDepth || num > endDepth)
			{
				strata.Remove(num);
			}
		}
	}

	private GroundSO GetCounterGround(int count)
	{
		if (count < 0 || count > 9)
		{
			throw new ArgumentException("count");
		}
		return counterGrounds[count];
	}

	private StratumData GeneratePuzzle(Vector3Int digPos)
	{
		System.Random randomWorldGen = gm.farm.sim.randomWorldGen;
		Vector2Int worldSize = gm.WorldSize;
		float mineRatio = GetMineRatio(digPos.z);
		int num = Mathf.Max(Mathf.RoundToInt((float)(worldSize.x * worldSize.y) * mineRatio), 1);
		HashSet<Vector2Int> hashSet = new HashSet<Vector2Int>();
		for (int i = 0; i < num; i++)
		{
			for (int j = 0; j < 100; j++)
			{
				Vector2Int item = new Vector2Int(randomWorldGen.Next(0, worldSize.x), randomWorldGen.Next(0, worldSize.y));
				if ((Mathf.Abs(digPos.x - item.x) > 1 || Mathf.Abs(digPos.y - item.y) > 1) && hashSet.Add(item))
				{
					break;
				}
			}
		}
		int[] array = new int[worldSize.x * worldSize.y];
		for (int k = 0; k < worldSize.x; k++)
		{
			for (int l = 0; l < worldSize.y; l++)
			{
				Vector3Int vector3Int = new Vector3Int(k, l, digPos.z);
				bool flag = hashSet.Contains((Vector2Int)vector3Int);
				gm.GroundAt(vector3Int).groundSo = (flag ? oreMine : oreDud);
				if (!flag)
				{
					continue;
				}
				foreach (Vector2Int item2 in GridManager.Neighboring8Positions((Vector2Int)vector3Int))
				{
					if (gm.IsWithinBounds(item2))
					{
						GetMineCount(array, item2.x, item2.y, worldSize.x)++;
					}
				}
			}
		}
		return new StratumData
		{
			neighborMap = array,
			mineCount = num,
			revealedDuds = 0
		};
	}

	private ref int GetMineCount(int[] map, int x, int y, int sizex)
	{
		return ref map[x + y * sizex];
	}

	private int GetAndApplyMineCount(int[] map, Vector3Int pos, int sizex)
	{
		Vector2Int worldSize = gm.WorldSize;
		GroundData.Chunk chunk = gm.ChunkAt(pos.z);
		ref GroundData.Ground reference = ref chunk.GroundAt(pos + GridManager.down, worldSize);
		if (reference.groundSo.objectName != "soot")
		{
			UnityEngine.Debug.LogError($"SweeperController: Unexpected ground at {pos + GridManager.down} '{reference.groundSo.objectName}'");
			return 0;
		}
		bool flag = false;
		foreach (Vector2Int item in GridManager.Neighboring8Positions((Vector2Int)pos))
		{
			if (!gm.IsWithinBounds(item))
			{
				continue;
			}
			bool flag2 = chunk.GroundAt(item.x, item.y, pos.z, worldSize).groundSo.objectName == "dynamite" && chunk.IsBlockPresent(item.x, item.y, pos.z, worldSize);
			flag = flag || flag2;
			if (flag2 || GetMineCount(map, item.x, item.y, sizex) != 0)
			{
				continue;
			}
			ref GroundData.Ground reference2 = ref chunk.GroundAt(item.x, item.y, pos.z + 1, worldSize);
			if (reference2.groundSo.objectName != "soot")
			{
				UnityEngine.Debug.LogError($"SweeperController: Unexpected ground at {new Vector3Int(item.x, item.y, pos.z + 1)} '{reference.groundSo.objectName}'");
				continue;
			}
			GroundSO groundSO = (HasUnrevealedNeighbor(new Vector3Int(item.x, item.y, pos.z)) ? GetCounterGround(1) : GetCounterGround(0));
			if (reference2.groundSo != groundSO)
			{
				reference2.groundSo = groundSO;
				gm.groundData.MarkPositionChanged(item);
			}
		}
		int mineCount = GetMineCount(map, pos.x, pos.y, sizex);
		if (mineCount == 0)
		{
			reference.groundSo = (flag ? GetCounterGround(1) : GetCounterGround(0));
		}
		else
		{
			reference.groundSo = GetCounterGround(mineCount + 1);
			gm.groundData.MarkPositionChanged(pos);
		}
		return mineCount;
	}

	private bool HasUnrevealedNeighbor(Vector3Int pos)
	{
		Vector2Int worldSize = gm.WorldSize;
		GroundData.Chunk chunk = gm.ChunkAt(pos.z);
		ref GroundData.Ground reference = ref chunk.GroundAt(pos + GridManager.down, worldSize);
		if (reference.groundSo.objectName != "soot")
		{
			UnityEngine.Debug.LogError($"SweeperController: Unexpected ground at {pos + GridManager.down} '{reference.groundSo.objectName}'");
			return false;
		}
		foreach (Vector2Int item in GridManager.Neighboring8Positions((Vector2Int)pos))
		{
			if (gm.IsWithinBounds(item) && chunk.GroundAt(item.x, item.y, pos.z, worldSize).groundSo.objectName == "dynamite" && chunk.IsBlockPresent(item.x, item.y, pos.z, worldSize))
			{
				return true;
			}
		}
		return false;
	}
}
public class Treasure : HedgePlant
{
	private const int MAX_TREASURE_FACTOR = 301;

	private int treasureFactor = 1;

	private Vector2Int nextPos;

	private Duration startTime;

	private bool repositioning;

	public override bool Harvestable => !repositioning;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		if (repositioning)
		{
			collectionDuration = Duration.FromSeconds(0.0);
			return ItemBlock.CreateEmpty();
		}
		base.Harvest(out collectionDuration);
		if (mazeSize == sim.farm.grid.WorldSize.x)
		{
			sim.UnlockAchievement("TREASURE_HUNTER");
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
		sim.simRunner?.PlaySound(SoundEffectType.HarvestTreasureChest, base.pos);
		Vector3 localPosition = base.LocalPosition;
		sim.simRunner?.PlayEffect(VFXType.hit, localPosition, changeColor: true, objectSO.color);
		sim.simRunner?.PlayEffect(VFXType.dust, localPosition);
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
		if (!sim.farm.grid.IsWithinBounds(base.pos) || sim.farm.grid.CellAt(base.pos).entity != this || !sim.farm.grid.IsWithinBounds(nextPos))
		{
			return;
		}
		HedgePlant hedgePlant = sim.farm.grid.CellAt(nextPos).entity as HedgePlant;
		if (!IsInSameMaze(hedgePlant))
		{
			return;
		}
		hedgePlant.removed = true;
		Treasure obj = (Treasure)sim.farm.grid.SetEntity(nextPos, "treasure");
		obj.walls = hedgePlant.walls;
		obj.treasureFactor = treasureFactor + 1;
		obj.startTime = startTime;
		obj.mazeSize = mazeSize;
		obj.lowLeftCorner = lowLeftCorner;
		obj.ChooseNextPosition();
		if (obj.treasureFactor >= 300)
		{
			sim.UnlockAchievement("RECYCLING");
		}
		removed = true;
		HedgePlant obj2 = (HedgePlant)sim.farm.grid.SetEntity(base.pos, "hedge");
		obj2.walls = walls;
		obj2.mazeSize = mazeSize;
		obj2.lowLeftCorner = lowLeftCorner;
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
					Vector2Int vector2Int2 = vector2Int + item.GetDirectionVector();
					if (!(sim.randomMaze.NextDouble() > 0.002) && vector2Int2.x >= lowLeftCorner.x && vector2Int2.y >= lowLeftCorner.y && vector2Int2.x < lowLeftCorner.x + mazeSize && vector2Int2.y < lowLeftCorner.y + mazeSize)
					{
						HedgePlant hedgePlant2 = sim.farm.grid.CellAt(vector2Int).entity as HedgePlant;
						HedgePlant hedgePlant3 = sim.farm.grid.CellAt(vector2Int2).entity as HedgePlant;
						if (IsInSameMaze(hedgePlant2) && IsInSameMaze(hedgePlant3))
						{
							hedgePlant2.walls[(int)item] = false;
							hedgePlant3.walls[(int)item.Reverse()] = false;
						}
					}
				}
			}
		}
	}

	private bool IsInSameMaze(HedgePlant hedge)
	{
		if (hedge != null && !hedge.removed && hedge.mazeSize == mazeSize)
		{
			return hedge.lowLeftCorner == lowLeftCorner;
		}
		return false;
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
		return PyTuple.From(base.pos);
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
			while (nextPos == base.pos);
		}
	}
}
public class TreasureMapController : GridController
{
	private class PathData
	{
		public int droneId;

		public List<Vector3Int> path;

		public int droneFurthestIndex;

		public int pathMinIndex;

		public HashSet<Vector3Int> visitedBlocks;

		public bool visitedBlockMultipleTimes;
	}

	private struct GenerationContext
	{
		public GridManager gm;

		public System.Random random;

		public Vector2Int size;

		public List<Vector3Int> path;

		public List<Vector3Int> steps;

		public Vector3Int lastPosition
		{
			get
			{
				if (steps.Count <= 0)
				{
					List<Vector3Int> list = path;
					return list[list.Count - 1];
				}
				List<Vector3Int> list2 = steps;
				return list2[list2.Count - 1];
			}
		}

		public GenerationContext(GridManager gridManager)
		{
			gm = gridManager;
			random = gm.farm.sim.randomWorldGen;
			size = gm.WorldSize;
			path = new List<Vector3Int>();
			steps = new List<Vector3Int>();
		}
	}

	private delegate void PathGenerator(in GenerationContext ctx);

	public new const string Name = "TreasureMap";

	public const string GroundStratumName = "basalt";

	public const string GroundMapName = "treasure_map";

	public const string GroundPathName = "treasure_path";

	public const string GroundGoalName = "treasure_goal";

	public const string EntityTreasureName = "underground_treasure";

	public const string TrasureMapUnlock = "treasure_map";

	public const int BaseTreasureDepth = 4;

	public const int DepthPerUnlockLevel = 1;

	public const bool RevealPathOnDig = true;

	private const double PathCheckInterval = 0.02;

	private GroundSO groundPath;

	private GroundSO groundGoal;

	private GroundSO groundCleared;

	private GroundSO groundBroken;

	private List<PathData> activePaths;

	private int currentPathDepth;

	public int CurrentPathDepth => currentPathDepth;

	public static int GetPathDepth(Farm farm)
	{
		return 4 + farm.NumUnlocked("treasure_map");
	}

	public TreasureMapController(GridManager gm)
		: base("TreasureMap", gm)
	{
		groundPath = ResourceManager.GetGround("treasure_path");
		groundGoal = ResourceManager.GetGround("treasure_goal");
		groundCleared = UnityEngine.Object.Instantiate(groundPath);
		groundCleared.decorations = new GroundSO.GroundDecoration[0];
		groundBroken = UnityEngine.Object.Instantiate(groundPath);
		groundBroken.decorations[0] = groundBroken.decorations[1];
	}

	public override void ClearGrid()
	{
		activePaths?.Clear();
		currentPathDepth = GetPathDepth(gm.farm);
	}

	public override void OnChunksAddedOrRemoved(int startDepth, int endDepth)
	{
		if (activePaths == null || activePaths.Count == 0)
		{
			return;
		}
		for (int num = activePaths.Count - 1; num >= 0; num--)
		{
			PathData pathData = activePaths[num];
			int z = pathData.path[0].z;
			List<Vector3Int> path = pathData.path;
			if (path[path.Count - 1].z < startDepth || z > endDepth)
			{
				activePaths.RemoveAt(num);
			}
		}
	}

	public override IPyObject Measure(Drone drone, Vector3Int pos)
	{
		ref GroundData.Ground reference = ref gm.GroundAt(pos);
		if (reference.groundSo.objectName == "basalt")
		{
			Vector2Int worldSize = gm.WorldSize;
			for (int i = 0; i < worldSize.x; i++)
			{
				for (int j = 0; j < worldSize.y; j++)
				{
					if (gm.GroundAt(i, j, pos.z + 1).groundSo.objectName == "treasure_map")
					{
						return PyTuple.From(new Vector2Int(i, j));
					}
				}
			}
			UnityEngine.Debug.LogError(string.Format("Treasure Map: Could not find map ground ({0}) below strata at depth {1}", "treasure_map", pos.z));
			return PyNone.Instance;
		}
		if (reference.groundSo.objectName != "treasure_map")
		{
			return PyNone.Instance;
		}
		PathData pathData = activePaths?.Find((PathData d) => d.path[0] == pos);
		if (pathData == null)
		{
			pathData = new PathData
			{
				droneId = -1,
				path = GeneratePath(pos, currentPathDepth),
				pathMinIndex = 1,
				visitedBlocks = new HashSet<Vector3Int>()
			};
			if (activePaths == null)
			{
				activePaths = new List<PathData>();
			}
			activePaths.Add(pathData);
			ScheduleCheckPaths();
		}
		StringBuilder stringBuilder = new StringBuilder();
		Vector3Int vector3Int = new Vector3Int(-1, -1, -1);
		foreach (Vector3Int item in pathData.path)
		{
			if (vector3Int.z >= 0)
			{
				Vector3Int vector3Int2 = item - vector3Int;
				if (Math.Abs(vector3Int2.x) + Math.Abs(vector3Int2.y) + Math.Abs(vector3Int2.z) != 1)
				{
					throw new Exception($"Treasure map path step is not a cardinal direction: {vector3Int} -> {item} ({vector3Int2})");
				}
				if (vector3Int2.x < 0)
				{
					stringBuilder.Append('W');
				}
				else if (vector3Int2.x > 0)
				{
					stringBuilder.Append('E');
				}
				else if (vector3Int2.y < 0)
				{
					stringBuilder.Append('S');
				}
				else if (vector3Int2.y > 0)
				{
					stringBuilder.Append('N');
				}
				else
				{
					if (vector3Int2.z <= 0)
					{
						throw new Exception($"Invalid treasure map path direction: {vector3Int} -> {item} ({vector3Int2})");
					}
					stringBuilder.Append('D');
				}
			}
			vector3Int = item;
		}
		return new PyString(stringBuilder.ToString());
	}

	public override int OnMove(Vector2Int oldPos, Vector2Int newPos, ProgramState programState)
	{
		Vector3Int pos = (Vector3Int)newPos;
		pos.z = gm.CellAt(newPos).depth;
		CheckDronePosition(programState.DroneId, pos);
		return -1;
	}

	public override void OnAfterDig(Drone drone, Vector2Int dugPosition)
	{
		Vector3Int vector3Int = (Vector3Int)dugPosition;
		vector3Int.z = gm.CellAt(dugPosition).depth;
		Vector3Int mapPos = vector3Int + GridManager.up;
		if (gm.GroundAt(mapPos).groundSo.objectName == "treasure_map")
		{
			PathData pathData = activePaths?.Find((PathData d) => d.path[0] == mapPos);
			if (pathData == null)
			{
				UnityEngine.Debug.LogError($"Treasure Map: Dug into map ground but could not find path (@{mapPos})");
				return;
			}
			if (pathData.droneId >= 0)
			{
				UnityEngine.Debug.LogError($"Treasure Map: Dug into map ground but path already assigned (to drone #{pathData.droneId}, dug by drone #{drone.DroneId})");
				return;
			}
			pathData.droneId = drone.DroneId;
		}
		CheckDronePosition(drone.DroneId, vector3Int, revealPath: true);
	}

	public override void OnDroneRemoved(int droneId)
	{
		if (activePaths != null)
		{
			int num = activePaths.FindIndex((PathData d) => d.droneId == droneId);
			if (num >= 0)
			{
				ClearPathAtIndex(num, breakPath: true);
			}
		}
	}

	public override void OnDroneChangedId(int oldDroneId, int newDroneId)
	{
		if (activePaths == null)
		{
			return;
		}
		if (activePaths.FindIndex((PathData d) => d.droneId == newDroneId) >= 0)
		{
			UnityEngine.Debug.LogError($"Treasure Map: Cannot change drone ID form {oldDroneId} to {newDroneId}, ID {newDroneId} already exists");
			return;
		}
		int num = activePaths.FindIndex((PathData d) => d.droneId == oldDroneId);
		if (num >= 0)
		{
			activePaths[num].droneId = newDroneId;
		}
	}

	private List<Vector3Int> GeneratePath(Vector3Int startPos, int depth)
	{
		GenerationContext ctx = new GenerationContext(gm);
		float t = Mathf.Clamp01(((float)ctx.size.x - 4f) / 28f);
		int num = Mathf.CeilToInt(Mathf.Lerp(5f, 25f, t));
		int num2 = Mathf.CeilToInt(Mathf.Lerp(10f, 5f, t));
		ctx.path.Add(startPos);
		for (int i = 1; i < depth; i++)
		{
			if (!TryGenerateAndAdd(in ctx, GenerateStepDown))
			{
				int num3 = 0;
				while (true)
				{
					if (num3 < 10)
					{
						if (TryGenerateAndAdd(in ctx, GenerateCombined(GenerateToRandomTarget, GenerateStepDown)))
						{
							break;
						}
						num3++;
						continue;
					}
					UnityEngine.Debug.LogError("Treasure Map: Failed to generate step down");
					return null;
				}
			}
			int num4 = ctx.random.Next(1, num + 1);
			for (int j = 0; j < num4; j++)
			{
				int num5 = 0;
				while (true)
				{
					if (num5 < 10)
					{
						double num6 = ctx.random.NextDouble();
						PathGenerator pathGenerator = ((num6 < 0.5) ? new PathGenerator(GenerateToRandomTarget) : ((!(num6 < 0.8)) ? GenerateRepeatCopy(GenerateLoop, 1, num2) : GenerateRepeatCopy(GenerateBackAndForth, 1, num2 / 2)));
						PathGenerator generator = pathGenerator;
						if (TryGenerateAndAdd(in ctx, generator))
						{
							break;
						}
						num5++;
						continue;
					}
					UnityEngine.Debug.LogError("Treasure Map: Failed to generate path feature");
					return null;
				}
			}
		}
		TryGenerateAndAdd(in ctx, GenerateStepDown);
		int k = 1;
		for (int count = ctx.path.Count; k < count; k++)
		{
			Vector3Int pos = ctx.path[k];
			gm.GroundAt(ctx.path[k]).groundSo = ((k == count - 1) ? groundGoal : groundPath);
			gm.groundData.MarkPositionChanged(pos);
		}
		return ctx.path;
	}

	private void ScheduleCheckPaths()
	{
		gm.farm.sim.StartTimer(CheckPaths, Duration.FromSeconds(0.02));
	}

	private void CheckPaths()
	{
		if (activePaths == null || activePaths.Count == 0)
		{
			return;
		}
		for (int num = activePaths.Count - 1; num >= 0; num--)
		{
			PathData data = activePaths[num];
			if (!CheckPathIsValid(data))
			{
				ClearPathAtIndex(num, breakPath: true);
			}
		}
		if (activePaths.Count > 0)
		{
			ScheduleCheckPaths();
		}
	}

	private bool CheckPathIsValid(PathData data)
	{
		int num = data.pathMinIndex;
		int i = data.pathMinIndex;
		for (int count = data.path.Count; i < count; i++)
		{
			Vector3Int pos = data.path[i];
			if (!CheckPathPositionIsValid(pos))
			{
				if (i >= data.droneFurthestIndex)
				{
					return false;
				}
				num = i;
			}
		}
		if (num > data.pathMinIndex)
		{
			for (int j = data.pathMinIndex; j < num; j++)
			{
				ClearBlock(data.path[j], breakPath: false);
			}
			data.pathMinIndex = num;
		}
		return true;
	}

	private bool CheckPathPositionIsValid(Vector3Int pos)
	{
		GroundData.Chunk chunk = gm.ChunkAt(pos.z);
		if (!chunk.IsBlockPresent(pos.x, pos.y, pos.z, gm.WorldSize))
		{
			return false;
		}
		ref GroundData.Ground reference = ref chunk.GroundAt(pos.x, pos.y, pos.z, gm.WorldSize);
		if (reference.groundSo == null)
		{
			return false;
		}
		string objectName = reference.groundSo.objectName;
		if (objectName != "treasure_path" && objectName != "treasure_goal")
		{
			return false;
		}
		return true;
	}

	private void CheckDronePosition(int droneId, Vector3Int pos, bool revealPath = false)
	{
		if (activePaths == null || activePaths.Count == 0)
		{
			return;
		}
		int num = activePaths.FindIndex((PathData p) => p.droneId == droneId);
		if (num < 0)
		{
			return;
		}
		PathData pathData = activePaths[num];
		int num2 = pathData.path.FindLastIndex((Vector3Int p) => p == pos);
		if (num2 < 0)
		{
			UnityEngine.Debug.Log("Treasure Map: Drone not on a path position");
			ClearPathAtIndex(num, breakPath: true);
			return;
		}
		ref GroundData.Ground reference = ref gm.GroundAt(pos);
		string objectName = reference.groundSo.objectName;
		if (objectName != "treasure_path" && objectName != "treasure_goal")
		{
			UnityEngine.Debug.Log("Treasure Map: Drone on path position but ground changed (" + objectName + ")");
			ClearPathAtIndex(num, breakPath: true);
			return;
		}
		if (num2 == pathData.path.Count - 1 && objectName == "treasure_goal")
		{
			UnityEngine.Debug.Log("FOUND TREASURE!");
			ClearPathAtIndex(num, breakPath: false);
			((UndergroundTreasure)gm.SetEntity((Vector2Int)pos, "underground_treasure")).treasurePathLength = pathData.path.Count;
			if (!pathData.visitedBlockMultipleTimes)
			{
				gm.farm.sim.UnlockAchievement("TREASURE_OPTIMAL");
			}
			return;
		}
		pathData.droneFurthestIndex = num2;
		if (revealPath)
		{
			int num3 = pathData.pathMinIndex;
			for (int count = pathData.path.Count; num3 < count; num3++)
			{
				Vector3Int vector3Int = pathData.path[num3];
				if (vector3Int.z == pos.z)
				{
					gm.GroundAt(vector3Int);
					if (!(reference.groundSo.objectName != "treasure_path") && !(reference.groundSo == groundBroken))
					{
						gm.ClearGroundWithCaveins((Vector2Int)vector3Int, vector3Int.z);
					}
				}
			}
		}
		if (revealPath)
		{
			pathData.visitedBlocks.Clear();
		}
		if (!pathData.visitedBlocks.Add(pos))
		{
			pathData.visitedBlockMultipleTimes = true;
		}
	}

	private void ClearPathAtIndex(int index, bool breakPath)
	{
		foreach (Vector3Int item in activePaths[index].path)
		{
			ClearBlock(item, breakPath);
		}
		activePaths.RemoveAt(index);
	}

	private void ClearBlock(Vector3Int pos, bool breakPath)
	{
		ref GroundData.Ground reference = ref gm.GroundAt(pos);
		string objectName = reference.groundSo.objectName;
		if (!(objectName != "treasure_path") || !(objectName != "treasure_goal"))
		{
			reference.groundSo = (breakPath ? groundBroken : groundCleared);
			gm.groundData.MarkPositionChanged(pos);
		}
	}

	private static PathGenerator GenerateCombined(PathGenerator one, PathGenerator two)
	{
		return delegate(in GenerationContext ctx)
		{
			one(in ctx);
			two(in ctx);
		};
	}

	private static PathGenerator GenerateRepeated(PathGenerator generator, int minRepetitions, int maxRepetitions)
	{
		return delegate(in GenerationContext ctx)
		{
			int num = ctx.random.Next(minRepetitions, maxRepetitions + 1);
			for (int i = 0; i < num; i++)
			{
				generator(in ctx);
			}
		};
	}

	private static PathGenerator GenerateRepeatCopy(PathGenerator generator, int minRepetitions, int maxRepetitions)
	{
		return delegate(in GenerationContext ctx)
		{
			int num = ctx.random.Next(minRepetitions, maxRepetitions + 1);
			if (num > 0)
			{
				int count = ctx.steps.Count;
				generator(in ctx);
				int count2 = ctx.steps.Count;
				if (count != count2)
				{
					List<Vector3Int> list = null;
					for (int i = 1; i < num; i++)
					{
						if (list == null)
						{
							list = ctx.steps.GetRange(count, count2 - count);
						}
						ctx.steps.AddRange(list);
					}
				}
			}
		};
	}

	private static void GenerateStepDown(in GenerationContext ctx)
	{
		ctx.steps.Add(ctx.lastPosition + GridManager.down);
	}

	private static void GenerateToTarget(in GenerationContext ctx, Vector3Int target, int firstAxis = -1)
	{
		Vector3Int lastPosition = ctx.lastPosition;
		Vector2Int vector2Int = new Vector2Int(Math.Sign(target.x - lastPosition.x), Math.Sign(target.y - lastPosition.y));
		int num = ((firstAxis == 0 || firstAxis == 1) ? firstAxis : ctx.random.Next(0, 2));
		while (lastPosition[num] != target[num])
		{
			lastPosition[num] += vector2Int[num];
			ctx.steps.Add(lastPosition);
		}
		num = ((num != 1) ? 1 : 0);
		while (lastPosition[num] != target[num])
		{
			lastPosition[num] += vector2Int[num];
			ctx.steps.Add(lastPosition);
		}
	}

	private static void GenerateToRandomTarget(in GenerationContext ctx)
	{
		Vector3Int target = new Vector3Int(ctx.random.Next(0, ctx.size.x), ctx.random.Next(0, ctx.size.y), ctx.lastPosition.z);
		GenerateToTarget(in ctx, target);
	}

	private static void GenerateBackAndForth(in GenerationContext ctx)
	{
		Vector3Int lastPosition = ctx.lastPosition;
		int index = ctx.random.Next(0, 2);
		int num = ctx.random.Next(1, ctx.size[index] / 2 + 1);
		int value = ((lastPosition[index] < num) ? 1 : ((lastPosition[index] + num < ctx.size[index]) ? ((ctx.random.Next(0, 2) != 0) ? 1 : (-1)) : (-1)));
		Vector3Int zero = Vector3Int.zero;
		zero[index] = value;
		for (int i = 0; i < num; i++)
		{
			lastPosition += zero;
			ctx.steps.Add(lastPosition);
		}
		for (int j = 0; j < num; j++)
		{
			lastPosition -= zero;
			ctx.steps.Add(lastPosition);
		}
	}

	private static void GenerateLoop(in GenerationContext ctx)
	{
		Vector3Int lastPosition = ctx.lastPosition;
		Vector3Int pos = new Vector3Int(lastPosition.x + ctx.random.Next(2, ctx.size.x / 2) * RandomSign(ctx.random), lastPosition.y + ctx.random.Next(2, ctx.size.y / 2) * RandomSign(ctx.random), lastPosition.z);
		pos = ctx.gm.Wrap(pos);
		int firstAxis = ctx.random.Next(0, 2);
		GenerateToTarget(in ctx, pos, firstAxis);
		GenerateToTarget(in ctx, lastPosition, firstAxis);
	}

	private static bool CheckSteps(in GenerationContext ctx)
	{
		foreach (Vector3Int step in ctx.steps)
		{
			if (!CanStepThroughPosition(in ctx, step))
			{
				return false;
			}
		}
		return true;
	}

	private static bool CanStepThroughPosition(in GenerationContext ctx, Vector3Int pos)
	{
		GroundData.Chunk chunk = ctx.gm.ChunkAt(pos.z);
		if (!chunk.IsBlockPresent(pos.x, pos.y, pos.z, ctx.size))
		{
			return false;
		}
		ref GroundData.Ground reference = ref chunk.GroundAt(pos.x, pos.y, pos.z, ctx.size);
		if (reference.groundSo == null)
		{
			return false;
		}
		if (!string.IsNullOrEmpty(reference.groundSo.controller))
		{
			return false;
		}
		string objectName = reference.groundSo.objectName;
		if (objectName == "treasure_path" || objectName == "treasure_goal")
		{
			return false;
		}
		return true;
	}

	private static bool TryGenerateAndAdd(in GenerationContext ctx, PathGenerator generator)
	{
		ctx.steps.Clear();
		generator(in ctx);
		if (!CheckSteps(in ctx))
		{
			return false;
		}
		ctx.path.AddRange(ctx.steps);
		return true;
	}

	private static int RandomSign(System.Random random)
	{
		if (random.Next(0, 2) != 0)
		{
			return 1;
		}
		return -1;
	}
}
public class TreePlant : Growable
{
	protected override double GrowTimeFactor
	{
		get
		{
			Entity[] neighbors = sim.farm.grid.GetNeighbors(base.pos);
			double num = 1.0;
			Entity[] array = neighbors;
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

	public override void OnFree()
	{
		base.OnFree();
		UpdateNeighbors();
	}
}
public class UndergroundTreasure : Entity
{
	public int treasurePathLength;

	public override ItemBlock Harvest(out Duration collectionDuration)
	{
		base.Harvest(out collectionDuration);
		sim.farm.grid.RemoveEntity(base.pos);
		double n = objectSO.dropAmount * (double)treasurePathLength * YieldFactor;
		sim.IncrementAchievementStat("total_treasure_map", 1);
		return new ItemBlock(objectSO.dropItemId, n);
	}

	public override ItemBlock GetYield()
	{
		double n = objectSO.dropAmount * (double)treasurePathLength * YieldFactor;
		return new ItemBlock(objectSO.dropItemId, n);
	}

	public override void OnRestart()
	{
	}
}
public class DinosaurHat : Hat
{
	private LinkedList<Dinosaur> tail = new LinkedList<Dinosaur>();

	private Apple target;

	private List<Vector2Int> freeCells = new List<Vector2Int>();

	private HashSet<Vector2Int> snakeSurface;

	private int surfaceDepth;

	private int ops = 400;

	private Duration equipTime;

	public ItemBlock GetAppleCost()
	{
		int num = Mathf.Max(0, base.sim.farm.NumUnlocked("dinosaurs") - 1);
		return ResourceManager.GetEntity("apple").cost * Mathf.Max(1, 1 << num);
	}

	public override void OnEquip(Drone drone, ProgramState programState)
	{
		base.OnEquip(drone, programState);
		equipTime = base.sim.CurrentTime;
		base.sim.UnlockAchievement("EQUIP_DINO_HAT");
		if (base.sim.farm.drones.Count((Drone d) => d?.hat.hatSO.hatName == "dinosaur_hat") > 1)
		{
			drone.hat = Hat.CreateDefaultHat(base.sim, drone);
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_dino_hat_already_used"));
		}
		if (base.sim.farm.grid.CellAt(drone.pos).entity == null || drone.EntityUnderDrone().objectSO.canBeOverplanted)
		{
			ItemBlock appleCost = GetAppleCost();
			snakeSurface = FindFreeCells(freeCells);
			surfaceDepth = base.sim.farm.grid.CellAt(drone.pos).depth;
			if (base.sim.farm.Items.Contains(appleCost) && TryChooseTarget(freeCells, out var targetPos, drone.pos))
			{
				base.sim.farm.Items.Remove(appleCost);
				target = (Apple)base.sim.farm.grid.SetEntity(drone.pos, "apple");
				target.SetNextTarget(targetPos);
			}
			else
			{
				base.sim.simRunner.Logger.LogWarning(CodeUtilities.LocalizeAndFormat("warning_missing_seed", ResourceManager.GetEntity("apple")), programState);
			}
		}
	}

	public override void OnUnequip()
	{
		base.OnUnequip();
		if (tail.Count > 0)
		{
			base.sim.simRunner?.PlaySound(SoundEffectType.DinosaurDie, base.drone.pos);
			base.sim.farm.CollectItem(StringIds.BoneItemId, BoneCount(), tail.First.Value.LocalPosition, base.sim.CurrentTime - equipTime);
		}
		foreach (Dinosaur item in tail)
		{
			item.HarvestEffects();
			item.isInSnake = false;
			base.sim.farm.grid.RemoveEntity(item.pos);
		}
		RemoveApple();
		tail.Clear();
	}

	private void RemoveApple()
	{
		if (target != null && base.sim.farm.grid.CellAt(target.pos).entity == target)
		{
			base.sim.farm.grid.RemoveEntity(target.pos);
		}
		target = null;
	}

	public double BoneCount()
	{
		int num = base.sim.farm.grid.cells.Count((GridManager.Cell cell) => cell.entity is Dinosaur);
		int num2 = Mathf.Max(0, base.sim.farm.NumUnlocked("dinosaurs") - 1);
		return Math.Floor(Math.Pow(num, 2.0)) * (double)(1 << num2);
	}

	public override bool CanMoveTo(GridDirection direction)
	{
		Vector2Int pos = base.drone.pos + direction.GetDirectionVector();
		ref GridManager.Cell reference = ref base.sim.farm.grid.CellAt(base.drone.pos);
		ref GridManager.Cell reference2 = ref base.sim.farm.grid.CellAt(pos);
		if (reference.depth != reference2.depth)
		{
			return false;
		}
		return true;
	}

	public override int OnMove(Vector2Int oldPos, Vector2Int newPos, ProgramState programState)
	{
		base.OnMove(oldPos, newPos, programState);
		bool flag = false;
		HashSet<Vector2Int> hashSet = FindFreeCells(freeCells);
		if (target != null && (base.sim.farm.grid.CellAt(base.drone.pos).depth != surfaceDepth || !snakeSurface.SetEquals(hashSet)))
		{
			RemoveApple();
		}
		int num = base.sim.farm.grid.WorldSize.x * base.sim.farm.grid.WorldSize.y - 2;
		Apple apple = target;
		if (apple != null && apple.pos == oldPos && base.sim.farm.grid.CellAt(oldPos).entity == target)
		{
			ItemBlock appleCost = GetAppleCost();
			bool flag2 = base.sim.farm.Items.Contains(appleCost);
			flag = true;
			if ((base.sim.farm.grid.CellAt(target.nextPos).entity?.objectSO.canBeOverplanted ?? true) && flag2 && TryChooseTarget(freeCells, out var targetPos, target.nextPos))
			{
				base.sim.farm.Items.Remove(appleCost);
				base.sim.simRunner?.PlaySound(SoundEffectType.DinosaurEatApple, newPos);
				base.sim.simRunner?.PlayEffect(VFXType.hit, target.LocalPosition, changeColor: true, target.objectSO.color);
				target = (Apple)base.sim.farm.grid.SetEntity(target.nextPos, "apple");
				target.SetNextTarget(targetPos);
				ops -= (int)Math.Floor((double)ops * 0.03);
			}
			else
			{
				if (!flag2)
				{
					base.sim.simRunner.Logger.LogWarning(CodeUtilities.LocalizeAndFormat("warning_missing_seed", ResourceManager.GetEntity("apple")), programState);
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
			if (tail.Count == num)
			{
				base.sim.UnlockAchievement("LONG_DINOSAUR");
			}
			else if (tail.Count >= 1000)
			{
				base.sim.UnlockAchievement("SIZE_MATTERS");
			}
			if (freeCells.Count > 0 && tail.Count > 1 && base.sim.farm.grid.CellAt(newPos).entity != target)
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
		Apple apple2 = target;
		if (apple2 != null && apple2.nextPos == oldPos && TryChooseTarget(freeCells, out var targetPos2))
		{
			target.SetNextTarget(targetPos2);
		}
		return ops;
	}

	private HashSet<Vector2Int> FindFreeCells(List<Vector2Int> freeCells)
	{
		if (freeCells == null)
		{
			freeCells = new List<Vector2Int>();
		}
		freeCells.Clear();
		GridManager grid = base.sim.farm.grid;
		int depth = grid.CellAtOrDefault(base.drone.pos).depth;
		HashSet<Vector2Int> hashSet = new HashSet<Vector2Int> { base.drone.pos };
		List<Vector2Int> list = new List<Vector2Int>();
		list.AddRange(GridManager.Neighboring4Positions(base.drone.pos));
		int num = 0;
		while (list.Count > 0)
		{
			Vector2Int vector2Int = list[list.Count - 1];
			list.RemoveAt(list.Count - 1);
			if (!grid.IsWithinBounds(vector2Int))
			{
				continue;
			}
			ref GridManager.Cell reference = ref grid.CellAt(vector2Int);
			if (reference.depth == depth && hashSet.Add(vector2Int))
			{
				list.AddRange(GridManager.Neighboring4Positions(vector2Int));
				Entity entity = reference.entity;
				if (entity is Dinosaur || entity is Apple)
				{
					num++;
				}
				else
				{
					freeCells.Add(vector2Int);
				}
			}
		}
		return hashSet;
	}

	private bool TryChooseTarget(List<Vector2Int> freeCells, out Vector2Int targetPos, Vector2Int? currentTargetPos = null)
	{
		targetPos = default(Vector2Int);
		if (base.sim.farm.grid.WorldSize.y <= 1)
		{
			return false;
		}
		if (freeCells.Count == 0 || (freeCells.Count == 1 && freeCells[0] == currentTargetPos))
		{
			return false;
		}
		do
		{
			targetPos = freeCells[base.sim.randomSnake.Next(freeCells.Count)];
		}
		while (targetPos == currentTargetPos);
		return true;
	}
}
public class DynamiteHat : Hat
{
	public override void OnEquip(Drone drone, ProgramState programState)
	{
		if (base.sim.farm.drones.Count((Drone d) => d?.hat.hatSO.hatName == base.hatSO.hatName) > 1)
		{
			drone.hat = Hat.CreateDefaultHat(base.sim, drone);
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_explosive_drill_already_used"));
		}
	}

	public override void OnDig(Drone drone, Vector2Int dugPosition, ref double ops)
	{
		if (base.sim.farm.Items.Remove(StringIds.GetItemId("dynamite"), 1.0))
		{
			GridManager.Cell cell = base.sim.farm.grid.CellAt(dugPosition);
			Vector3Int pos = (Vector3Int)dugPosition;
			pos.z = cell.depth;
			Dynamite.Explode(base.sim.farm.grid, pos, Dynamite.GetExplosionEnergy(base.sim.farm), 0.2f, collectDrops: true, DesignConstants.Inst.vfx.explosiveDrillCrumblePushAngle);
			ops = Math.Min(base.sim.actionOps, ops);
			base.sim.UnlockAchievement("EXPLOSIVE_DRILL");
		}
	}
}
public class Hat
{
	private static Dictionary<string, Type> hatTypes;

	public HatSO hatSO { get; private set; }

	public Simulation sim { get; private set; }

	public Drone drone { get; private set; }

	public bool DefaultHat { get; private set; }

	public virtual bool CanMoveTo(GridDirection direction)
	{
		return true;
	}

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

	public virtual void OnDig(Drone drone, Vector2Int dugPosition, ref double ops)
	{
	}

	public static Hat CreateHat(HatSO hatType, Simulation sim, Drone drone, bool isDefault)
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
		obj.DefaultHat = isDefault;
		return obj;
	}

	public static Hat CreateDefaultHat(Simulation sim, Drone drone)
	{
		return CreateHat(ResourceManager.GetHat("straw_hat"), sim, drone, isDefault: true);
	}
}
[CreateAssetMenu(fileName = "Hat", menuName = "ScriptableObjects/Hat", order = 3)]
public class HatSO : ScriptableObject, IPyObject
{
	public string className;

	public string hatName;

	public Mesh hatMesh;

	[Tooltip("Optional material override for each submesh. Leave empty to render the entire hat with the default hat material.")]
	public Material[] subMeshMaterials;

	public bool isGolden;

	public bool preventWrapping;

	public bool preventHover;

	public bool rotateDroneToMove;

	public float droneFlyHeight;

	public bool hidden;

	public EDlcType dlc;

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

	public EDlcType dlc;

	public bool fullyGenerateUnderground;

	[Tooltip("If non-empty, ground feature generation will be limited to these features + non-specific features (`GroundFeature.associatedUnlockForGroundLoop` == null).")]
	public List<string> whitelistedGroundFeatureUnlocks;

	[Tooltip("If non-null, the generation will 'pretend' that non-specific features (hardness, stone layer, ...) are at these chunks. Length must equal whitelistedGroundFeatureUnlocks.")]
	public List<int> pretendedFeatureChunks;

	public List<int> pretendedChunkDepths;

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
	private static Dictionary<string, EntitySO> entitites;

	private static Dictionary<string, GroundSO> grounds;

	private static DroneSO drone;

	private static Dictionary<string, HatSO> hats;

	private static Dictionary<string, LeaderboardSO> leaderboards;

	private static Dictionary<string, UnlockSO> unlocks;

	private static Dictionary<string, UnlockSO> unlockedIn;

	private static ItemSO[] items;

	private static List<GroundFeature> groundFeaturesSorted;

	private static Dictionary<string, GroundFeature> groundFeaturesByName;

	private static Dictionary<string, EDlcType> dlcKeys;

	private static readonly string[] contentLinkPrefixes = new string[6] { "functions/", "unlocks/", "items/", "objects/", "grounds/", "docs/unlocks/" };

	public static void LoadAll()
	{
		if (entitites != null || grounds != null || drone != null || hats != null || leaderboards != null || unlocks != null || items != null || groundFeaturesSorted != null)
		{
			return;
		}
		dlcKeys = new Dictionary<string, EDlcType>();
		items = (from x in Resources.LoadAll<ItemSO>("Items/")
			orderby x.priority
			select x).ToArray();
		for (int num = 0; num < items.Length; num++)
		{
			ItemSO itemSO = items[num];
			itemSO.itemId = num;
			TrackDlcKey(itemSO.dlc, itemSO.itemName);
		}
		StringIds.SetItemIds(items.Select((ItemSO x) => x.itemName));
		entitites = new Dictionary<string, EntitySO>();
		EntitySO[] array = Resources.LoadAll<EntitySO>("FarmObjects/");
		foreach (EntitySO entitySO in array)
		{
			entitySO.cost.Deserialize();
			entitySO.dropItemId = StringIds.GetItemId(entitySO.dropItem);
			TrackDlcKey(entitySO.dlc, entitySO.objectName);
			entitites[entitySO.objectName] = entitySO;
		}
		grounds = new Dictionary<string, GroundSO>();
		GroundSO[] array2 = Resources.LoadAll<GroundSO>("Grounds/");
		foreach (GroundSO groundSO in array2)
		{
			grounds[groundSO.objectName] = groundSO;
			TrackDlcKey(groundSO.dlc, groundSO.objectName);
			groundSO.dropItemId = StringIds.GetItemId(groundSO.dropItem);
		}
		drone = Resources.Load<DroneSO>("FarmObjects/drone");
		hats = new Dictionary<string, HatSO>();
		HatSO[] array3 = Resources.LoadAll<HatSO>("Hats/");
		foreach (HatSO hatSO in array3)
		{
			TrackDlcKey(hatSO.dlc, hatSO.hatName);
			hats[hatSO.hatName] = hatSO;
		}
		leaderboards = new Dictionary<string, LeaderboardSO>();
		LeaderboardSO[] array4 = Resources.LoadAll<LeaderboardSO>("Leaderboards/");
		foreach (LeaderboardSO leaderboardSO in array4)
		{
			leaderboardSO.startItems.Deserialize();
			leaderboardSO.goalItems.Deserialize();
			TrackDlcKey(leaderboardSO.dlc, leaderboardSO.leaderboardName);
			leaderboards[leaderboardSO.leaderboardName] = leaderboardSO;
		}
		unlocks = new Dictionary<string, UnlockSO>();
		UnlockSO[] array5 = Resources.LoadAll<UnlockSO>("Unlocks/");
		foreach (UnlockSO unlockSO in array5)
		{
			foreach (ItemBlock item in unlockSO.multiUnlockCost)
			{
				item.Deserialize();
			}
			unlockSO.unlockCost.Deserialize();
			TrackDlcKey(unlockSO.dlc, unlockSO.unlockName);
			TrackDlcKey(unlockSO.dlc, unlockSO.docs);
			if (unlockSO.unlocks != null)
			{
				foreach (string unlock in unlockSO.unlocks)
				{
					TrackDlcKey(unlockSO.dlc, unlock);
				}
			}
			unlocks[unlockSO.unlockName] = unlockSO;
		}
		groundFeaturesSorted = new List<GroundFeature>();
		groundFeaturesByName = new Dictionary<string, GroundFeature>();
		GroundFeature[] array6 = Resources.LoadAll<GroundFeature>("GroundFeatures/");
		foreach (GroundFeature groundFeature in array6)
		{
			groundFeature.OnLoaded();
			groundFeaturesSorted.Add(groundFeature);
			groundFeaturesByName[groundFeature.name] = groundFeature;
		}
		groundFeaturesSorted.Sort(GroundFeature.PriorityComparer);
		static void TrackDlcKey(EDlcType dlc, string key)
		{
			if (!string.IsNullOrEmpty(key))
			{
				if (dlcKeys.TryGetValue(key, out var value))
				{
					if (value == EDlcType.None || value == dlc)
					{
						return;
					}
					if (dlc == EDlcType.None)
					{
						dlcKeys[key] = EDlcType.None;
						return;
					}
					UnityEngine.Debug.LogWarning($"Duplicate DLC association for '{key}': {value} and {dlc}");
				}
				dlcKeys[key] = dlc;
			}
		}
	}

	public static EntitySO GetEntity(string name)
	{
		return entitites.GetValueOrDefault(name);
	}

	public static GroundSO GetGround(string name)
	{
		return grounds.GetValueOrDefault(name);
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

	public static GroundFeature GetGroundFeature(string name)
	{
		return groundFeaturesByName[name];
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

	public static IEnumerable<EntitySO> GetAllEntitites()
	{
		return entitites.Values;
	}

	public static IEnumerable<GroundSO> GetAllGrounds()
	{
		return grounds.Values;
	}

	public static IEnumerable<UnlockSO> GetAllUnlocks()
	{
		return unlocks.Values;
	}

	public static UnlockSO GetUnlockOf(string name)
	{
		if (unlockedIn == null)
		{
			unlockedIn = new Dictionary<string, UnlockSO>();
			Deque<UnlockSO> deque = new Deque<UnlockSO>();
			Dictionary<string, List<UnlockSO>> dictionary = new Dictionary<string, List<UnlockSO>>();
			foreach (UnlockSO allUnlock in GetAllUnlocks())
			{
				if (!PlatformManager.IsDlcInstalled(allUnlock.dlc))
				{
					continue;
				}
				if (string.IsNullOrEmpty(allUnlock.parentUnlock))
				{
					deque.Add(allUnlock);
					continue;
				}
				if (!dictionary.ContainsKey(allUnlock.parentUnlock))
				{
					dictionary[allUnlock.parentUnlock] = new List<UnlockSO>();
				}
				dictionary[allUnlock.parentUnlock].Add(allUnlock);
			}
			while (deque.Count > 0)
			{
				UnlockSO unlockSO = deque.PopFront();
				CacheIfFirst(unlockSO.unlockName, unlockSO);
				foreach (string unlock in unlockSO.unlocks)
				{
					CacheIfFirst(unlock, unlockSO);
					if (unlock.Length > 1 && char.IsDigit(unlock[0]))
					{
						CacheIfFirst(unlock.Substring(1), unlockSO);
					}
				}
				if (!dictionary.TryGetValue(unlockSO.unlockName, out var value))
				{
					continue;
				}
				foreach (UnlockSO item in value)
				{
					deque.Add(item);
				}
			}
		}
		return unlockedIn.GetValueOrDefault(name);
		static void CacheIfFirst(string unlockedName, UnlockSO value2)
		{
			if (!unlockedIn.ContainsKey(unlockedName))
			{
				unlockedIn[unlockedName] = value2;
			}
		}
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

	public static IReadOnlyList<GroundFeature> GetAllGroundFeatures()
	{
		return groundFeaturesSorted;
	}

	public static EDlcType GetDlcForKey(string key)
	{
		if (!dlcKeys.TryGetValue(key, out var value))
		{
			return EDlcType.None;
		}
		return value;
	}

	public static EDlcType GetDlcForLink(string link)
	{
		if (dlcKeys.TryGetValue(link, out var value))
		{
			return value;
		}
		string[] array = contentLinkPrefixes;
		foreach (string text in array)
		{
			if (link.StartsWith(text, StringComparison.Ordinal))
			{
				string text2 = link.Substring(text.Length);
				if (text2.EndsWith(".md", StringComparison.Ordinal))
				{
					text2 = text2.Substring(0, text2.Length - 3);
				}
				return GetDlcForKey(text2);
			}
		}
		return EDlcType.None;
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

	public string gainResource;

	public Vector3 iconRotation;

	public string displayCode;

	public List<string> unlocks;

	public string parentUnlock;

	public AdditionalUnlockRequirement additionalUnlockRequirement;

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

	public EDlcType dlc;

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
	Per10Seconds,
	Additive
}
[Serializable]
public class AdditionalUnlockRequirement
{
	public string unlockName;

	public int level;
}
[CreateAssetMenu(fileName = "BlockFeature", menuName = "ScriptableObjects/Block", order = 20)]
public class BlockFeature : GroundFeature
{
	[Header("Block")]
	public float probability;

	public Vector3Int sizeMin;

	public Vector3Int sizeMax;

	[Space]
	public GroundSO ground;

	public override float GetProbability(in Context ctx)
	{
		return probability;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		Vector3Int vector3Int = new Vector3Int(ctx.random.Next(sizeMin.x, sizeMax.x + 1), ctx.random.Next(sizeMin.y, sizeMax.y + 1), ctx.random.Next(sizeMin.z, sizeMax.z + 1));
		Vector3Int vector3Int2 = new Vector3Int(ctx.random.Next(0, worldSize.x - vector3Int.x), ctx.random.Next(0, worldSize.y - vector3Int.y), ctx.random.Next(ctx.chunk.startingDepth, ctx.chunk.startingDepth + 16 - vector3Int.z));
		BoundingBoxInt boundingBoxInt = new BoundingBoxInt(vector3Int2, vector3Int2 + vector3Int);
		if (ctx.OtherFeatureOverlaps(boundingBoxInt))
		{
			return null;
		}
		for (int i = boundingBoxInt.min.x; i < boundingBoxInt.max.x; i++)
		{
			for (int j = boundingBoxInt.min.y; j < boundingBoxInt.max.y; j++)
			{
				for (int k = boundingBoxInt.min.z; k < boundingBoxInt.max.z; k++)
				{
					ctx.chunk.GroundAt(i, j, k, worldSize) = new GroundData.Ground(ground);
				}
			}
		}
		return new BoundingBoxInt[1] { boundingBoxInt };
	}
}
[CreateAssetMenu(fileName = "ClayFeature", menuName = "ScriptableObjects/Clay", order = 20)]
public class ClayFeature : GroundFeature
{
	public enum GenerationAlgorithm
	{
		Hill,
		Slope,
		Noise
	}

	public GenerationAlgorithm algorithm = GenerationAlgorithm.Noise;

	public OpenSimplexNoise noise;

	public int startOffset = 1;

	public int randomStartOffsetMin = 2;

	public int randomStartOffsetMax = 3;

	public GroundSO ground;

	[Header("Hill Algorithm Config")]
	public int seedPieceLongSideMin = 3;

	public int seedPieceLongSideMax = 6;

	public int seedPieceShortSide = 2;

	public int addTerracePieceCounterMin = 7;

	public int addTerracePieceCounterMax = 9;

	public int randomlyAddedTerracePieceMinLength = 2;

	public int randomlyAddedTerracePieceMaxLength = 5;

	[Header("Slope Algorithm Config")]
	public float terracePieceChance = 0.3f;

	public bool randomizeTerraceWidths = true;

	[Header("Noise Algorithm Config")]
	public float noiseSamplingScale = 0.1f;

	public float noiseHeightMultiplier = 0.5f;

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		return algorithm switch
		{
			GenerationAlgorithm.Hill => GenerateWithHillShape(ctx), 
			GenerationAlgorithm.Slope => GenerateSlope(in ctx), 
			GenerationAlgorithm.Noise => GenerateWithNoise(ctx), 
			_ => throw new ArgumentOutOfRangeException(), 
		};
	}

	private IEnumerable<BoundingBoxInt> GenerateSlope(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		int num = startOffset + ctx.random.Next(randomStartOffsetMin, randomStartOffsetMax) + ctx.chunk.startingDepth;
		float num2 = Math.Max((float)worldSize.x / (float)(16 - num), 1f);
		(Vector2Int, Vector2Int, Vector2Int)[] array = new(Vector2Int, Vector2Int, Vector2Int)[4]
		{
			(new Vector2Int(0, 0), new Vector2Int(1, 0), new Vector2Int(0, 1)),
			(new Vector2Int(0, 0), new Vector2Int(0, 1), new Vector2Int(1, 0)),
			(new Vector2Int(worldSize.x - 1, 0), new Vector2Int(-1, 0), new Vector2Int(0, 1)),
			(new Vector2Int(0, worldSize.y - 1), new Vector2Int(0, -1), new Vector2Int(1, 0))
		};
		(Vector2Int, Vector2Int, Vector2Int) tuple = array[ctx.random.Next(array.Length)];
		Vector2Int item = tuple.Item1;
		Vector2Int item2 = tuple.Item2;
		Vector2Int item3 = tuple.Item3;
		int num3 = num;
		float num4 = num2;
		for (int i = 0; i < worldSize.x; i++)
		{
			num4 -= 1f;
			if (num4 < 0f)
			{
				num4 = num2;
				if (randomizeTerraceWidths)
				{
					num4 += (float)ctx.random.NextDouble() * 2f - 1f;
				}
				num3 = Math.Min(num3 + 1, 14);
			}
			for (int j = 0; j < worldSize.x; j++)
			{
				Vector2Int vector2Int = item + item2 * i + item3 * j;
				if (num3 >= 16)
				{
					break;
				}
				ctx.chunk.GroundAt(vector2Int.x, vector2Int.y, num3, worldSize) = new GroundData.Ground(ground);
				if (num3 + 1 >= 16)
				{
					break;
				}
				ctx.chunk.GroundAt(vector2Int.x, vector2Int.y, num3 + 1, worldSize) = new GroundData.Ground(ground);
			}
		}
		BoundingBoxInt boundingBoxInt = new BoundingBoxInt(new Vector3Int(0, 0, num), new Vector3Int(worldSize.x, worldSize.y, num3));
		return new BoundingBoxInt[1] { boundingBoxInt };
	}

	private IEnumerable<BoundingBoxInt> GenerateWithHillShape(Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		int num = startOffset + ctx.random.Next(randomStartOffsetMin, randomStartOffsetMax) + ctx.chunk.startingDepth;
		int num2 = ctx.random.Next(seedPieceLongSideMin, seedPieceLongSideMax);
		int num3 = seedPieceShortSide;
		bool num4 = ctx.random.NextDouble() > 0.5;
		if (!num4)
		{
			new Vector2Int(1, 0);
		}
		else
		{
			new Vector2Int(0, 1);
		}
		if (num4)
		{
			int num5 = num2;
			int num6 = num3;
			num3 = num5;
			num2 = num6;
		}
		Vector2Int vector2Int = new Vector2Int(ctx.random.Next(ctx.sim.farm.grid.WorldSize.x - num2), ctx.random.Next(ctx.sim.farm.grid.WorldSize.y - num3));
		Vector2 seedPieceCenter = new Vector2((float)vector2Int.x + (float)num2 / 2f, (float)vector2Int.y + (float)num3 / 2f);
		HashSet<Vector2Int> hashSet = new HashSet<Vector2Int>();
		List<Vector2Int> list = new List<Vector2Int>();
		int num7 = num;
		for (int i = vector2Int.x; i < vector2Int.x + num2 + ctx.random.Next(-1, 1); i++)
		{
			for (int j = vector2Int.y; j < vector2Int.y + num3 + ctx.random.Next(-1, 1); j++)
			{
				ctx.chunk.GroundAt(i, j, num7, worldSize) = new GroundData.Ground(ground);
				ctx.chunk.GroundAt(i, j, num7 + 1, worldSize) = new GroundData.Ground(ground);
				hashSet.Add(new Vector2Int(i, j));
				foreach (Vector2Int item in GridManager.Neighboring8Positions(new Vector2Int(i, j)))
				{
					if (ctx.sim.farm.grid.IsWithinBounds(item))
					{
						list.Add(item);
					}
				}
			}
		}
		int num8 = ctx.random.Next(addTerracePieceCounterMin, addTerracePieceCounterMax);
		while (list.Count > 0)
		{
			num7++;
			num7 = Math.Min(num7, 14);
			List<Vector2Int> list2 = new List<Vector2Int>();
			for (int k = 0; k < list.Count; k++)
			{
				Vector2Int vector2Int2 = list[k];
				if (hashSet.Contains(vector2Int2))
				{
					continue;
				}
				num8--;
				if (num8 <= 0)
				{
					num8 = ctx.random.Next(addTerracePieceCounterMin, addTerracePieceCounterMax);
					int size = ctx.random.Next(randomlyAddedTerracePieceMinLength, randomlyAddedTerracePieceMaxLength);
					foreach (Vector2Int item2 in addTerracePiece(k, list, seedPieceCenter, size))
					{
						if (!ctx.sim.farm.grid.IsWithinBounds(item2))
						{
							continue;
						}
						ctx.chunk.GroundAt(item2.x, item2.y, num7, worldSize) = new GroundData.Ground(ground);
						ctx.chunk.GroundAt(item2.x, item2.y, num7 + 1, worldSize) = new GroundData.Ground(ground);
						hashSet.Add(item2);
						foreach (Vector2Int item3 in GridManager.Neighboring8Positions(item2))
						{
							if (ctx.sim.farm.grid.IsWithinBounds(item3))
							{
								list2.Add(item3);
							}
						}
					}
				}
				ctx.chunk.GroundAt(vector2Int2.x, vector2Int2.y, num7, worldSize) = new GroundData.Ground(ground);
				ctx.chunk.GroundAt(vector2Int2.x, vector2Int2.y, num7 + 1, worldSize) = new GroundData.Ground(ground);
				hashSet.Add(vector2Int2);
				foreach (Vector2Int item4 in GridManager.Neighboring8Positions(vector2Int2))
				{
					if (ctx.sim.farm.grid.IsWithinBounds(item4))
					{
						list2.Add(item4);
					}
				}
			}
			list = list2;
		}
		BoundingBoxInt boundingBoxInt = new BoundingBoxInt(new Vector3Int(0, 0, num), new Vector3Int(worldSize.x, worldSize.y, num7));
		return new BoundingBoxInt[1] { boundingBoxInt };
		static IEnumerable<Vector2Int> addTerracePiece(int posIndex, List<Vector2Int> terracePositions, Vector2 vector2, int num9)
		{
			Vector2Int vector2Int3 = terracePositions[posIndex];
			Vector2 vector = vector2Int3 - vector2;
			Vector2Int vector2Int4 = ((!(Mathf.Abs(vector.x) > Mathf.Abs(vector.y))) ? new Vector2Int(0, (vector.y > 0f) ? 1 : (-1)) : new Vector2Int((vector.x > 0f) ? 1 : (-1), 0));
			Vector2Int vector2Int5 = vector2Int3 + vector2Int4;
			int l = 0;
			Vector2Int currentPos = vector2Int5;
			yield return currentPos;
			for (; l < num9 && posIndex + l + 1 < terracePositions.Count; l++)
			{
				currentPos += terracePositions[posIndex + l + 1] - terracePositions[posIndex + l];
				yield return currentPos;
			}
		}
	}

	private IEnumerable<BoundingBoxInt> GenerateWithNoise(Context ctx)
	{
		GroundSO rock = ResourceManager.GetGround("rock");
		GroundSO dirt = ResourceManager.GetGround("dirt");
		noise = new OpenSimplexNoise(ctx.random.Next());
		int num = startOffset + ctx.random.Next(randomStartOffsetMin, randomStartOffsetMax) + ctx.chunk.startingDepth;
		float num2 = 16 - num + ctx.chunk.startingDepth - 1;
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		BoundingBoxInt boundingBoxInt = new BoundingBoxInt(new Vector3Int(0, 0, num), new Vector3Int(worldSize.x, worldSize.y, 16));
		if (ctx.OtherFeatureOverlaps(boundingBoxInt))
		{
			return null;
		}
		for (int i = 0; i < worldSize.x; i++)
		{
			for (int j = 0; j < worldSize.y; j++)
			{
				int num3 = num + (int)((noise.Evaluate((float)i * noiseSamplingScale, (float)j * noiseSamplingScale) + 1.0) * 0.5 * (double)num2 * (double)noiseHeightMultiplier);
				fillWithDirtUpwards(i, j, num3 - 1);
				ctx.chunk.GroundAt(i, j, num3, worldSize) = new GroundData.Ground(ground);
				ctx.chunk.GroundAt(i, j, num3 + 1, worldSize) = new GroundData.Ground(ground);
				fillWithStoneDownwards(i, j, num3 + 2);
			}
		}
		return new BoundingBoxInt[1] { boundingBoxInt };
		void fillWithDirtUpwards(int x, int y, int z)
		{
			for (int num4 = z; num4 >= ctx.chunk.startingDepth; num4--)
			{
				ctx.chunk.GroundAt(x, y, num4, worldSize) = new GroundData.Ground(dirt, 1, 1);
			}
		}
		void fillWithStoneDownwards(int x, int y, int z)
		{
			for (int k = z; k < ctx.chunk.startingDepth + 16; k++)
			{
				ctx.chunk.GroundAt(x, y, k, worldSize) = new GroundData.Ground(rock);
			}
		}
	}
}
[CreateAssetMenu(fileName = "CoalFeature", menuName = "ScriptableObjects/Coal", order = 20)]
public class CoalFeature : GroundFeature
{
	public GroundSO coal;

	[FormerlySerializedAs("depthStart")]
	public int loopRelativeDepthStart = 2;

	[FormerlySerializedAs("depthEnd")]
	public int loopRelativeDepthEnd = 16;

	public float veinCornerSkipChance = 0.2f;

	public List<int> sheetCountPerUnlock = new List<int>();

	private static int CalculateVeinSize(int worldSize)
	{
		return (int)((float)(worldSize * worldSize) * 0.8f);
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		GridManager gridManager = ctx.sim.farm.grid;
		Vector2Int worldSize = gridManager.WorldSize;
		List<BoundingBoxInt> list = new List<BoundingBoxInt>();
		int count = sheetCountPerUnlock[ctx.sim.farm.NumUnlocked("coal")];
		int num = Math.Max(loopRelativeDepthStart + ctx.loopStartDepth, ctx.chunk.startingDepth);
		int num2 = Math.Min(loopRelativeDepthEnd + ctx.loopStartDepth, ctx.chunk.startingDepth + 16);
		System.Random rnd = ctx.random;
		foreach (int item3 in (from _ in Enumerable.Range(num, num2 - num)
			orderby rnd.Next()
			select _).Take(count))
		{
			BoundingBoxInt item = generateVein(in ctx, item3);
			list.Add(item);
		}
		return list;
		BoundingBoxInt generateVein(in Context reference, int depth)
		{
			Vector2Int item2 = new Vector2Int(reference.random.Next(worldSize.x), reference.random.Next(worldSize.y));
			BoundingBoxInt result = new BoundingBoxInt(new Vector3Int(item2.x, item2.y, depth));
			int num3 = CalculateVeinSize(reference.sim.farm.grid.WorldSize.x);
			Deque<Vector2Int> deque = new Deque<Vector2Int> { item2 };
			HashSet<Vector2Int> hashSet = new HashSet<Vector2Int>();
			int num4 = 0;
			while (deque.Count > 0 && num4 < num3)
			{
				Vector2Int vector2Int = deque.Dequeue();
				hashSet.Add(vector2Int);
				reference.chunk.GroundAt(vector2Int.x, vector2Int.y, depth, worldSize) = new GroundData.Ground(coal);
				result.Encapsulate(new Vector3Int(vector2Int.x, vector2Int.y, depth));
				foreach (Vector2Int item4 in GridManager.Neighboring4Positions(vector2Int))
				{
					if (gridManager.IsWithinBounds(item4) && !hashSet.Contains(item4))
					{
						deque.Enqueue(item4);
					}
				}
				foreach (Vector2Int item5 in GridManager.NeighboringDiagonals(vector2Int))
				{
					if (gridManager.IsWithinBounds(item5) && !(reference.random.NextDouble() <= (double)veinCornerSkipChance) && !hashSet.Contains(item5))
					{
						deque.Enqueue(item5);
					}
				}
				num4++;
			}
			return result;
		}
	}
}
public class DummyGrasslandFeature : GroundFeature
{
	protected override void OnEnable()
	{
		base.name = "DummyGrasslandFeature";
		priority = 100000;
		base.OnEnable();
	}

	public override float GetProbability(in Context ctx)
	{
		if (ctx.chunk.startingDepth == 0)
		{
			return 1f;
		}
		return 0f;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		return new BoundingBoxInt[1] { BoundingBoxInt.FromMinAndSize(Vector3Int.zero, new Vector3Int(worldSize.x, worldSize.y, 1)) };
	}
}
[CreateAssetMenu(fileName = "Full Size", menuName = "ScriptableObjects/Full Size", order = 20)]
public class FullSizeFeature : GroundFeature
{
	[Header("Full Size")]
	public float probability;

	public int heightMin;

	public int heightMax;

	[Space]
	public GroundSO ground;

	public override float GetProbability(in Context ctx)
	{
		return probability;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		Vector3Int vector3Int = new Vector3Int(worldSize.x, worldSize.y, ctx.random.Next(heightMin, heightMax + 1));
		Vector3Int vector3Int2 = new Vector3Int(0, 0, ctx.chunk.startingDepth);
		BoundingBoxInt boundingBoxInt = new BoundingBoxInt(vector3Int2, vector3Int2 + vector3Int);
		if (ctx.OtherFeatureOverlaps(boundingBoxInt))
		{
			return null;
		}
		for (int i = boundingBoxInt.min.x; i < boundingBoxInt.max.x; i++)
		{
			for (int j = boundingBoxInt.min.y; j < boundingBoxInt.max.y; j++)
			{
				for (int k = boundingBoxInt.min.z; k < boundingBoxInt.max.z; k++)
				{
					ctx.chunk.GroundAt(i, j, k, worldSize) = new GroundData.Ground(ground);
				}
			}
		}
		return new BoundingBoxInt[1] { boundingBoxInt };
	}
}
public abstract class GroundFeature : ScriptableObject
{
	public struct Context
	{
		public Simulation sim;

		public GroundData.Chunk chunk;

		public System.Random random;

		public List<GeneratedFeature> features;

		public int loopStartIndex;

		public int loopStartDepth;

		public int? pretendedChunkDepth;

		public bool OtherFeatureContains(Vector3Int point, Func<GroundFeature, bool> featurePredicate = null)
		{
			if (features != null)
			{
				foreach (GeneratedFeature feature in features)
				{
					if ((featurePredicate == null || featurePredicate(feature.feature)) && feature.Contains(point))
					{
						return true;
					}
				}
			}
			return false;
		}

		public bool OtherFeatureOverlaps(BoundingBoxInt testBounds, Func<GroundFeature, bool> featurePredicate = null)
		{
			if (features != null)
			{
				foreach (GeneratedFeature feature in features)
				{
					if ((featurePredicate == null || featurePredicate(feature.feature)) && feature.Overlaps(testBounds))
					{
						return true;
					}
				}
			}
			return false;
		}

		public bool OtherFeatureOverlaps(BoundingBoxInt[] testBounds, Func<GroundFeature, bool> featurePredicate = null)
		{
			if (features != null)
			{
				foreach (GeneratedFeature feature in features)
				{
					if (featurePredicate != null && !featurePredicate(feature.feature))
					{
						continue;
					}
					foreach (BoundingBoxInt testBounds2 in testBounds)
					{
						if (feature.Overlaps(testBounds2))
						{
							return true;
						}
					}
				}
			}
			return false;
		}

		public bool SweepBounds(ref BoundingBoxInt bounds, Vector3Int? maxShift = null, Func<GroundFeature, bool> featurePredicate = null)
		{
			if (!OtherFeatureOverlaps(bounds, featurePredicate))
			{
				return true;
			}
			BoundingBoxInt boundingBoxInt = bounds;
			Vector3Int vector3Int = (Vector3Int)sim.farm.grid.WorldSize;
			vector3Int.z = 16;
			_ = bounds.size;
			Vector3Int vector3Int2 = vector3Int - bounds.size;
			if (maxShift.HasValue)
			{
				Vector3Int valueOrDefault = maxShift.GetValueOrDefault();
				vector3Int2.x = Mathf.Min(valueOrDefault.x, vector3Int2.x);
				vector3Int2.y = Mathf.Min(valueOrDefault.y, vector3Int2.y);
				vector3Int2.z = Mathf.Min(valueOrDefault.z, vector3Int2.z);
			}
			Vector3Int zero = Vector3Int.zero;
			while (true)
			{
				if (zero.x < vector3Int2.x)
				{
					bounds.Shift(GridManager.east);
					zero.x++;
					if (bounds.max.x > vector3Int.x)
					{
						bounds.Shift(GridManager.west * bounds.min.x);
					}
				}
				else if (zero.y < vector3Int2.y)
				{
					bounds.min.x = boundingBoxInt.min.x;
					bounds.max.x = boundingBoxInt.max.x;
					bounds.Shift(GridManager.north);
					zero.y++;
					if (bounds.max.y > vector3Int.y)
					{
						bounds.Shift(GridManager.south * bounds.min.y);
					}
				}
				else
				{
					if (zero.z >= vector3Int2.z)
					{
						break;
					}
					bounds.min.y = boundingBoxInt.min.y;
					bounds.max.y = boundingBoxInt.max.y;
					bounds.Shift(GridManager.down);
					zero.z++;
					if (bounds.max.z > vector3Int.z)
					{
						bounds.Shift(GridManager.up * (chunk.startingDepth - bounds.min.z));
					}
				}
				if (!OtherFeatureOverlaps(bounds, featurePredicate))
				{
					return true;
				}
			}
			bounds = boundingBoxInt;
			return false;
		}

		public bool TryPlaceRandomly(out BoundingBoxInt bounds, Vector3Int size, BoundingBoxInt? space = null, int attempts = 100, Func<GroundFeature, bool> featurePredicate = null)
		{
			bounds = default(BoundingBoxInt);
			BoundingBoxInt boundingBoxInt;
			if (space.HasValue)
			{
				BoundingBoxInt valueOrDefault = space.GetValueOrDefault();
				boundingBoxInt = valueOrDefault;
			}
			else
			{
				Vector2Int worldSize = sim.farm.grid.WorldSize;
				boundingBoxInt = new BoundingBoxInt(new Vector3Int(0, 0, chunk.startingDepth), new Vector3Int(worldSize.x, worldSize.y, chunk.startingDepth + 16));
			}
			Vector3Int size2 = boundingBoxInt.size;
			if (size2.x < size.x || size2.y < size.y || size2.z < size.z)
			{
				UnityEngine.Debug.LogError($"PlaceRandomly: Given space is too small to fit bounds! ({size} < {size2})");
				return false;
			}
			if (size2 == size)
			{
				return OtherFeatureOverlaps(bounds, featurePredicate);
			}
			Vector3Int vector3Int = size2 - size;
			int num = 0;
			do
			{
				Vector3Int vector3Int2 = new Vector3Int(random.Next(0, vector3Int.x + 1), random.Next(0, vector3Int.y + 1), random.Next(0, vector3Int.z + 1));
				BoundingBoxInt boundingBoxInt2 = BoundingBoxInt.FromMinAndSize(boundingBoxInt.min + vector3Int2, size);
				if (!OtherFeatureOverlaps(boundingBoxInt2, featurePredicate))
				{
					bounds = boundingBoxInt2;
					return true;
				}
			}
			while (++num < attempts);
			return false;
		}
	}

	public struct GeneratedFeature
	{
		public GroundFeature feature;

		public IEnumerable<BoundingBoxInt> bounds;

		public bool Contains(Vector3Int point)
		{
			if (bounds != null)
			{
				foreach (BoundingBoxInt bound in bounds)
				{
					if (bound.Contains(point))
					{
						return true;
					}
				}
			}
			return false;
		}

		public bool Overlaps(BoundingBoxInt testBounds)
		{
			if (bounds != null)
			{
				foreach (BoundingBoxInt bound in bounds)
				{
					if (bound.Overlaps(testBounds))
					{
						return true;
					}
				}
			}
			return false;
		}
	}

	public bool enabled = true;

	public bool onlyIncludeFirstChunkInGroundLoop;

	public List<int> chunkIndexWhitelist = new List<int>();

	public List<int> chunkIndexBlacklist = new List<int>();

	public int priority;

	public string associatedUnlockForGroundLoop = "";

	public string associatedUnlockForJumpCommand = "";

	public string Name { get; protected set; }

	public virtual float GetProbability(in Context ctx)
	{
		return 1f;
	}

	public virtual void OnLoaded()
	{
	}

	public abstract IEnumerable<BoundingBoxInt> Generate(in Context ctx);

	public virtual bool DoesPermitLaterFeature(in Context ctx, GroundFeature feature)
	{
		return true;
	}

	public static int PriorityComparer(GroundFeature one, GroundFeature two)
	{
		if (one == null && two == null)
		{
			return 0;
		}
		if (one == null)
		{
			return -1;
		}
		if (two == null)
		{
			return 1;
		}
		int num = two.priority.CompareTo(one.priority);
		if (num != 0)
		{
			return num;
		}
		return string.CompareOrdinal(two.Name, one.Name);
	}

	protected virtual void OnEnable()
	{
		Name = base.name;
	}
}
[CreateAssetMenu(fileName = "Mushroom", menuName = "ScriptableObjects/Mushroom", order = 20)]
public class MushroomFeature : GroundFeature
{
	public class Array2D<T>
	{
		public T[] array;

		public Vector2Int size;

		public T this[int x, int y]
		{
			get
			{
				AssertBounds(x, y);
				return array[y * size.x + x];
			}
			set
			{
				AssertBounds(x, y);
				array[y * size.x + x] = value;
			}
		}

		public T this[Vector2Int pos]
		{
			get
			{
				return this[pos.x, pos.y];
			}
			set
			{
				this[pos.x, pos.y] = value;
			}
		}

		public Array2D(Vector2Int size)
		{
			this.size = size;
			array = new T[size.x * size.y];
		}

		public bool TryGet(int x, int y, out T element)
		{
			if (!IsWithinBounds(x, y))
			{
				element = default(T);
				return false;
			}
			element = array[y * size.x + x];
			return true;
		}

		public bool TryGet(Vector2Int pos, out T element)
		{
			return TryGet(pos.x, pos.y, out element);
		}

		public void AssertBounds(int x, int y)
		{
			if (IsWithinBounds(x, y))
			{
				return;
			}
			throw new ArgumentException($"Arguments out of bounds (x: 0 <= {x} < {size.x}, y: 0 <= {y} < {size.y})");
		}

		public bool IsWithinBounds(int x, int y)
		{
			if (x >= 0 && x < size.x && y >= 0)
			{
				return y < size.y;
			}
			return false;
		}
	}

	[Header("Mushroom")]
	public float probability;

	[Space]
	public int heightMin;

	public int heightMax;

	[Space]
	public int typesMin;

	public int typesMax;

	public override float GetProbability(in Context ctx)
	{
		return probability;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		Vector3Int size = new Vector3Int(worldSize.x, worldSize.y, ctx.random.Next(heightMin, heightMax + 1));
		if (!ctx.TryPlaceRandomly(out var bounds, size, null, 100, (GroundFeature f) => !(f is OreVeinFeature) && !(f is HardPatchesFeature) && !(f is QuartzVeinFeature) && !(f is PetrifiedPumpkinsFeature)))
		{
			return null;
		}
		MushroomController mushroomController = ctx.sim.farm.grid.mushroomController;
		int value = Mathf.RoundToInt(typesMin + (typesMax - typesMin));
		value = Math.Clamp(value, 2, 6);
		Array2D<int> array2D = new Array2D<int>(worldSize);
		Array2D<int> array2D2 = new Array2D<int>(worldSize);
		Array.Fill(array2D.array, -1);
		MushroomGroundSO[] nextStrataGrounds = mushroomController.GetNextStrataGrounds(bounds.min.z, bounds.max.z);
		for (int num = bounds.min.z; num < bounds.max.z; num++)
		{
			for (int num2 = bounds.min.x; num2 < bounds.max.x; num2++)
			{
				for (int num3 = bounds.min.y; num3 < bounds.max.y; num3++)
				{
					int num4 = array2D[num2, num3];
					int num5;
					do
					{
						num5 = ctx.random.Next(0, value);
					}
					while (num5 == num4);
					array2D2[num2, num3] = num5;
					MushroomGroundSO fromGroundSo = nextStrataGrounds[num5];
					ctx.chunk.GroundAt(num2, num3, num, worldSize) = new GroundData.Ground(fromGroundSo);
				}
			}
			Array2D<int> array2D3 = array2D;
			array2D = array2D2;
			array2D2 = array2D3;
		}
		return new BoundingBoxInt[1] { bounds };
	}
}
[CreateAssetMenu(fileName = "ChunkFeature", menuName = "ScriptableObjects/Ore Vein", order = 20)]
public class OreVeinFeature : GroundFeature
{
	[Header("Ore Vein")]
	public int randomAdditionalVeinSizeMin;

	public int randomAdditionalVeinSizeMax = 2;

	public int veinSize = 7;

	public float veinProbability = 0.3f;

	[Space]
	public GroundSO oreGround;

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		GridManager grid = ctx.sim.farm.grid;
		Vector2Int worldSize = grid.WorldSize;
		int num = Mathf.CeilToInt(Mathf.Pow(veinSize * 2, 1f / 3f) * 1.5f) + 1;
		int num2 = num * num * num;
		List<Vector3Int> list = new List<Vector3Int>();
		ctx.chunk.oreCache["iron"] = list;
		List<BoundingBoxInt> list2 = new List<BoundingBoxInt>();
		bool flag = true;
		for (int i = 0; i < worldSize.x; i += num)
		{
			for (int j = 0; j < worldSize.y; j += num)
			{
				for (int k = ctx.chunk.startingDepth; k < ctx.chunk.startingDepth + 16; k += num)
				{
					if (ctx.random.NextDouble() >= (double)veinProbability)
					{
						continue;
					}
					int num3 = Mathf.Min(i + num, worldSize.x);
					int num4 = Mathf.Min(j + num, worldSize.y);
					int num5 = Mathf.Min(k + num, ctx.chunk.startingDepth + 16);
					Vector3Int item = new Vector3Int(ctx.random.Next(i, num3), ctx.random.Next(j, num4), ctx.random.Next(k, num5));
					float num6 = (float)((num3 - i) * (num4 - j) * (num5 - k)) / (float)num2;
					if (!flag && ctx.random.NextDouble() >= (double)num6)
					{
						continue;
					}
					int num7 = veinSize * Mathf.Max(1, 1 << ctx.sim.farm.NumUnlocked("ore_boost")) + ctx.random.Next(randomAdditionalVeinSizeMin, randomAdditionalVeinSizeMax);
					BoundingBoxInt reverseMaxBounds = BoundingBoxInt.ReverseMaxBounds;
					Queue<Vector3Int> queue = new Queue<Vector3Int>();
					HashSet<Vector3Int> hashSet = new HashSet<Vector3Int>();
					queue.Enqueue(item);
					int num8 = 0;
					while (num8 < num7 && queue.Count > 0)
					{
						Vector3Int pos = queue.Dequeue();
						if (pos.z < ctx.chunk.startingDepth || pos.z >= ctx.chunk.startingDepth + 16 || (!DesignConstants.Inst.caveIn.allowWrappingDigAndMeasure && !grid.IsWithinBounds(pos)))
						{
							continue;
						}
						Vector2Int vector2Int = grid.Wrap(new Vector2Int(pos.x, pos.y));
						Vector3Int vector3Int = new Vector3Int(vector2Int.x, vector2Int.y, pos.z);
						if (!hashSet.Add(vector3Int) || ctx.OtherFeatureContains(vector3Int))
						{
							continue;
						}
						num8++;
						ctx.chunk.GroundAt(vector3Int, worldSize) = new GroundData.Ground(oreGround);
						list.Add(vector3Int);
						reverseMaxBounds.Encapsulate(vector3Int);
						System.Random random = ctx.random;
						foreach (Vector3Int item3 in from _ in GridManager.Neighboring3DPositions(pos)
							orderby random.Next()
							select _)
						{
							Vector3Int item2 = new Vector3Int(item3.x, item3.y, item3.z);
							queue.Enqueue(item2);
						}
					}
					if (num8 > 0)
					{
						list2.Add(reverseMaxBounds);
						flag = false;
					}
				}
			}
		}
		return list2;
	}
}
[CreateAssetMenu(fileName = "PyramidFeature", menuName = "ScriptableObjects/Pyramid", order = 20)]
public class PyramidFeature : GroundFeature
{
	public const int pyramidBaseMin = 5;

	public const int erosionAmountMin = 3;

	public const int erosionAmountMax = 6;

	public GroundSO ground;

	public GroundSO pyramidFoundationGround;

	public float probability = 0.7f;

	public override float GetProbability(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		if (worldSize.x <= 5 && worldSize.y <= 5)
		{
			return 0f;
		}
		return probability;
	}

	public static int PyramidHeight(int x, int y, int pyramidSize)
	{
		return 1 + Math.Min(Math.Min(x, y), Math.Min(pyramidSize - 1 - x, pyramidSize - 1 - y));
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		int num = ((worldSize.x % 2 == 1) ? worldSize.x : (worldSize.x - 1));
		while (num >= 5 && num > 2)
		{
			int num2 = Math.Max((num - 5) / 2, 0);
			int num3 = 5 + ctx.random.Next(num2 + 1) * 2;
			int num4 = num3 / 2 + 1;
			Vector3Int size = new Vector3Int(num3, num3, num4 + 1);
			if (size.z > 16 || !ctx.TryPlaceRandomly(out var bounds, size, null, 20, (GroundFeature f) => f is TreasureMapFeature || f is SweeperStratumFeature || f is MushroomFeature))
			{
				num = num / 2 + 1;
				continue;
			}
			Vector2Int vector2Int = new Vector2Int(bounds.min.x, bounds.min.y);
			int num5 = bounds.max.z - 1;
			int num6 = num5 - 1;
			int z = num5 - num4;
			ctx.sim.farm.grid.pyramidController.AddPyramid(num3, new Vector3Int(vector2Int.x, vector2Int.y, num6));
			HashSet<Vector2Int> hashSet = new HashSet<Vector2Int>();
			int num7 = ctx.random.Next(3, 7);
			for (int num8 = 0; num8 < num7; num8++)
			{
				Vector2Int item;
				do
				{
					item = new Vector2Int(ctx.random.Next(num3), ctx.random.Next(num3));
				}
				while (hashSet.Contains(item));
				hashSet.Add(item);
			}
			for (int num9 = 0; num9 < num3; num9++)
			{
				for (int num10 = 0; num10 < num3; num10++)
				{
					ctx.chunk.GroundAt(vector2Int.x + num9, vector2Int.y + num10, num5, worldSize) = new GroundData.Ground(pyramidFoundationGround);
					int num11 = PyramidHeight(num9, num10, num3);
					int num12 = num6;
					if (!hashSet.Contains(new Vector2Int(num9, num10)))
					{
						while (num12 > num6 - num11)
						{
							ctx.chunk.GroundAt(vector2Int.x + num9, vector2Int.y + num10, num12, worldSize) = new GroundData.Ground(ground);
							num12--;
						}
					}
					int num13 = ctx.random.Next(1, 3);
					while (num12 > num6 - num11 - num13 && num12 >= ctx.chunk.startingDepth)
					{
						ctx.chunk.GroundAt(vector2Int.x + num9, vector2Int.y + num10, num12, worldSize) = new GroundData.Ground(ResourceManager.GetGround("dirt"), 1, 1);
						num12--;
					}
				}
			}
			BoundingBoxInt boundingBoxInt = new BoundingBoxInt(new Vector3Int(vector2Int.x, vector2Int.y, z), new Vector3Int(vector2Int.x + num3, vector2Int.y + num3, bounds.max.z));
			return new BoundingBoxInt[1] { boundingBoxInt };
		}
		return new List<BoundingBoxInt>();
	}
}
[CreateAssetMenu(fileName = "ChunkFeature", menuName = "ScriptableObjects/Quartz", order = 20)]
public class QuartzVeinFeature : GroundFeature
{
	public float veinRollsPer4x4WorldSize = 0.0625f;

	public float veinChance = 1f;

	public int randomAdditionalVeinSizeMin;

	public int randomAdditionalVeinSizeMax = 2;

	public float changeNeedleXYChance = 0.7f;

	public int veinSize = 4;

	[Space]
	public GroundSO oreGround;

	public override float GetProbability(in Context ctx)
	{
		return ctx.sim.farm.IsUnlocked("quartz") ? 1 : 0;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		List<Vector3Int> list = new List<Vector3Int>();
		ctx.chunk.oreCache["quartz"] = list;
		float num = veinRollsPer4x4WorldSize * (float)worldSize.x * (float)worldSize.y;
		int num2 = (int)num;
		if (ctx.random.NextDouble() < (double)(num - (float)num2))
		{
			num2++;
		}
		List<BoundingBoxInt> list2 = new List<BoundingBoxInt>();
		for (int i = 0; i < num2; i++)
		{
			if (ctx.random.NextDouble() > (double)veinChance)
			{
				continue;
			}
			BoundingBoxInt reverseMaxBounds = BoundingBoxInt.ReverseMaxBounds;
			int num3 = veinSize * Mathf.Max(1, 1 << ctx.sim.farm.NumUnlocked("ore_boost")) + ctx.random.Next(randomAdditionalVeinSizeMin, randomAdditionalVeinSizeMax);
			int num4 = ((ctx.random.NextDouble() < (double)changeNeedleXYChance) ? ctx.random.Next(2, num3) : int.MaxValue);
			int num5 = ctx.random.Next(worldSize.x);
			int num6 = ctx.random.Next(worldSize.y);
			int num7 = ctx.random.Next(ctx.chunk.startingDepth, ctx.chunk.startingDepth + 16 - num3);
			for (int j = 0; j < num3; j++)
			{
				if (j == num4)
				{
					num5 = Math.Clamp(num5 + ctx.random.Next(-1, 2), 0, worldSize.x - 1);
					num6 = Math.Clamp(num6 + ctx.random.Next(-1, 2), 0, worldSize.y - 1);
				}
				Vector3Int vector3Int = new Vector3Int(num5, num6, num7 + j);
				if (!ctx.OtherFeatureContains(vector3Int, (GroundFeature f) => !(f is PetrifiedPumpkinsFeature) && !(f is OreVeinFeature) && !(f is HardPatchesFeature)))
				{
					ctx.chunk.GroundAt(vector3Int, worldSize) = new GroundData.Ground(oreGround);
					list.Add(vector3Int);
					reverseMaxBounds.Encapsulate(vector3Int);
				}
			}
			list2.Add(reverseMaxBounds);
		}
		return list2;
	}
}
[CreateAssetMenu(fileName = "SpecialSoilsFeature", menuName = "ScriptableObjects/SpecialSoils", order = 20)]
public class SpecialSoilsFeature : GroundFeature
{
	public OpenSimplexNoise noise;

	public int startOffset;

	public int randomStartOffsetMin;

	public int randomStartOffsetMax = 10;

	public GroundSO ground;

	public float probability = 0.3f;

	public float noiseSamplingScale = 0.1f;

	public float hillRange = 4f;

	public override float GetProbability(in Context ctx)
	{
		return probability;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		return GenerateWithNoise(ctx);
	}

	private IEnumerable<BoundingBoxInt> GenerateWithNoise(Context ctx)
	{
		noise = new OpenSimplexNoise(ctx.random.Next());
		int num = startOffset + ctx.random.Next(randomStartOffsetMin, randomStartOffsetMax) + ctx.chunk.startingDepth;
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		BoundingBoxInt reverseMaxBounds = BoundingBoxInt.ReverseMaxBounds;
		if (ctx.OtherFeatureOverlaps(reverseMaxBounds))
		{
			return null;
		}
		for (int i = 0; i < worldSize.x; i++)
		{
			for (int j = 0; j < worldSize.y; j++)
			{
				int num2 = num + (int)((noise.Evaluate((float)i * noiseSamplingScale, (float)j * noiseSamplingScale) + 1.0) * 0.5 * (double)hillRange);
				ctx.chunk.GroundAt(i, j, num2, worldSize) = new GroundData.Ground(ground);
				ctx.chunk.GroundAt(i, j, num2 + 1, worldSize) = new GroundData.Ground(ground);
				reverseMaxBounds.Encapsulate(new Vector3Int(i, j, num2));
				reverseMaxBounds.Encapsulate(new Vector3Int(i, j, num2 + 1));
			}
		}
		return new BoundingBoxInt[1] { reverseMaxBounds };
	}
}
[CreateAssetMenu(fileName = "Sweeper Stratum", menuName = "ScriptableObjects/Sweeper Stratum", order = 20)]
public class SweeperStratumFeature : GroundFeature
{
	[Header("Sweeper Stratum")]
	public float probability;

	[Space]
	public GroundSO topGround;

	public GroundSO bottomGround;

	public override float GetProbability(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		if (worldSize.x <= 3 && worldSize.y <= 3)
		{
			return 0f;
		}
		return probability;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		Vector3Int size = new Vector3Int(worldSize.x, worldSize.y, 2);
		if (!ctx.TryPlaceRandomly(out var bounds, size, null, 100, (GroundFeature f) => !(f is OreVeinFeature) && !(f is HardPatchesFeature) && !(f is QuartzVeinFeature) && !(f is PetrifiedPumpkinsFeature)))
		{
			return null;
		}
		for (int num = bounds.min.x; num < bounds.max.x; num++)
		{
			for (int num2 = bounds.min.y; num2 < bounds.max.y; num2++)
			{
				ctx.chunk.GroundAt(num, num2, bounds.min.z, worldSize) = new GroundData.Ground(topGround);
				ctx.chunk.GroundAt(num, num2, bounds.max.z - 1, worldSize) = new GroundData.Ground(bottomGround);
			}
		}
		return new BoundingBoxInt[1] { bounds };
	}
}
[CreateAssetMenu(fileName = "TreasureMap", menuName = "ScriptableObjects/Treasure Map", order = 20)]
public class TreasureMapFeature : GroundFeature
{
	[Header("Treasure Map")]
	public float probability;

	[Space]
	public GroundSO strataGround;

	public GroundSO mapGround;

	public override float GetProbability(in Context ctx)
	{
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		if (worldSize.x <= 3 && worldSize.y <= 3)
		{
			return 0f;
		}
		return probability;
	}

	public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
	{
		int num = Math.Min(ctx.sim.farm.grid.treasureMapController.CurrentPathDepth, 16);
		Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
		Vector3Int size = new Vector3Int(worldSize.x, worldSize.y, 2 + num);
		if (!ctx.TryPlaceRandomly(out var bounds, size, null, 100, (GroundFeature f) => !(f is HardPatchesFeature) && !(f is PetrifiedPumpkinsFeature)))
		{
			UnityEngine.Debug.Log("found no fit for treasure map");
			return null;
		}
		for (int num2 = bounds.min.x; num2 < bounds.max.x; num2++)
		{
			for (int num3 = bounds.min.y; num3 < bounds.max.y; num3++)
			{
				ctx.chunk.GroundAt(num2, num3, bounds.min.z, worldSize) = new GroundData.Ground(strataGround);
			}
		}
		Vector2Int vector2Int = Vector2Int.Min(new Vector2Int(2, 2), worldSize / 4);
		Vector3Int vector3Int = new Vector3Int(ctx.random.Next(vector2Int.x, worldSize.x - vector2Int.x), ctx.random.Next(vector2Int.y, worldSize.y - vector2Int.y), bounds.min.z + 1);
		ctx.chunk.GroundAt(vector3Int, worldSize) = new GroundData.Ground(mapGround);
		return new BoundingBoxInt[2]
		{
			bounds,
			new BoundingBoxInt(vector3Int)
		};
	}
}
public class VFXManager : MonoBehaviour
{
	private const float EffectMaxRenderHeight = 100000f;

	private const float LowSmokeExplosionInterval = 0.5f;

	private const float CrumbleSpawnRateSmoothingTime = 3f;

	private const float CrumbleSpawnRateSettlingTime = 3f;

	private const float CrumbleSpawnRateIdleResetTime = 3f;

	[SerializeField]
	private Transform piggyMesh;

	private ISimRunner simRunner;

	private FarmRenderer farmRenderer;

	private Camera farmCamera;

	private RenderPackage prevRenderPackage;

	private Queue<float> effectStartTimes = new Queue<float>();

	private float lastExplosionTime = float.NegativeInfinity;

	private Dictionary<VFXType, List<GameObject>> effectPool = new Dictionary<VFXType, List<GameObject>>();

	private Dictionary<Mesh, List<MovingMeshEffect>> movingMeshEffects = new Dictionary<Mesh, List<MovingMeshEffect>>();

	private List<CrumbleEffect> crumbleEffects = new List<CrumbleEffect>();

	private Dictionary<Mesh, List<Matrix4x4>> crumbleDecorationBatches = new Dictionary<Mesh, List<Matrix4x4>>();

	private List<Mesh> activeCrumbleDecorationMeshes = new List<Mesh>();

	private Matrix4x4[] reusableTransformBuffer = new Matrix4x4[1023];

	private Vector4[] reusableColorBuffer = new Vector4[1023];

	private MaterialPropertyBlock crumbleMaterialProperties;

	private MaterialPropertyBlock movingMeshMaterialProperties;

	private MaterialPropertyBlock fogMaterialProperties;

	private Mesh crumbleMesh;

	private float estimatedCrumbleCandidateRate;

	private float estimatedCrumbleExpirationRate;

	private float crumbleCandidateRateHistoryTime;

	private float lastCrumbleCandidateBatchTime = float.NegativeInfinity;

	private void Awake()
	{
		simRunner = GetComponentInParent<ISimRunner>();
		if (simRunner == null)
		{
			UnityEngine.Debug.LogError("VFXManager requires a component that implements ISimRunner.");
		}
		farmRenderer = GetComponentInParent<FarmRenderer>();
		if ((object)farmRenderer == null)
		{
			UnityEngine.Debug.LogError("VFXManager requires a FarmRenderer in its parent hierarchy.");
		}
		else
		{
			farmCamera = farmRenderer.GetComponentInChildren<Camera>();
		}
		crumbleMaterialProperties = new MaterialPropertyBlock();
		movingMeshMaterialProperties = new MaterialPropertyBlock();
		fogMaterialProperties = new MaterialPropertyBlock();
		crumbleMesh = CreateCubeMesh();
	}

	private void Update()
	{
		RenderPackage renderPackage = simRunner?.GetRenderPackage();
		if (renderPackage != null && (object)renderPackage != prevRenderPackage)
		{
			int crumbleEffectExpectedCountLimit = DesignConstants.Inst.vfx.crumbleEffectExpectedCountLimit;
			Transform sceneScaler = simRunner.SceneScaler;
			Vector3 position = new Vector3(sceneScaler.position.x, sceneScaler.position.y, DesignConstants.Inst.farmRenderer.maxFarmRenderHeight);
			float num = 0f - sceneScaler.InverseTransformPoint(position).z - 0.5f;
			Vector3Int vector3Int = new Vector3Int(int.MaxValue, int.MaxValue, int.MaxValue);
			foreach (VFXCall vfxCall in renderPackage.vfxCalls)
			{
				if (vfxCall.effect == VFXType.block_break && vfxCall.lifetime > 0f)
				{
					vector3Int = LocalToVoxelBlock(vfxCall.localPos);
				}
			}
			int num2 = 0;
			Vector3 zero = Vector3.zero;
			int num3 = 0;
			foreach (CrumblingBlockCall crumblingBlock in renderPackage.crumblingBlocks)
			{
				Vector3Int pos = crumblingBlock.pos;
				if ((float)pos.z >= num && vector3Int != crumblingBlock.pos)
				{
					num3++;
				}
			}
			float batchSpawnChance = CalculateCrumbleSpawnChance(crumbleEffectExpectedCountLimit, crumbleEffects.Count, num3);
			float num4 = CalculateCrumbleSpawnChanceForBatch(batchSpawnChance, crumbleEffectExpectedCountLimit, crumbleEffects.Count, num3);
			foreach (CrumblingBlockCall crumblingBlock2 in renderPackage.crumblingBlocks)
			{
				Vector3Int pos = crumblingBlock2.pos;
				if (!((float)pos.z < num) && !(vector3Int == crumblingBlock2.pos) && !(num4 <= 0f) && (!(num4 < 1f) || !(UnityEngine.Random.value >= num4)))
				{
					AddCrumbleEffect(renderPackage, crumblingBlock2.pos);
					num2++;
					zero += GridManager.CellToLocal(crumblingBlock2.pos + new Vector3(0f, 0f, 0.5f));
				}
			}
			PlayAvalancheStartSound(num2, zero);
			foreach (SlidingBlockCall slidingBlock in renderPackage.slidingBlocks)
			{
				AddSlidingBlockEffect(renderPackage, slidingBlock, slidingBlock.overrideDuration ? Mathf.Max(0f, slidingBlock.duration) : DesignConstants.Inst.vfx.blockSlideEffectDuration);
			}
			foreach (VFXCall vfxCall2 in renderPackage.vfxCalls)
			{
				if (vfxCall2.effect == VFXType.moving_mesh_piggy)
				{
					if (!movingMeshEffects.ContainsKey(vfxCall2.mesh))
					{
						movingMeshEffects[vfxCall2.mesh] = new List<MovingMeshEffect>();
					}
					movingMeshEffects[vfxCall2.mesh].Add(new MovingMeshEffect
					{
						localPosition = vfxCall2.localPos,
						rotation = Quaternion.identity,
						scale = 1f,
						renderLayer = simRunner.RenderLayer,
						zVelocity = DesignConstants.Inst.vfx.collectEffectStartZVelocity
					});
				}
				else if (vfxCall2.effect == VFXType.block_break)
				{
					AddBlockBreakEffect(renderPackage, vfxCall2);
				}
				else if (vfxCall2.effect == VFXType.falling_bamboo)
				{
					AddFallingBambooEffect(renderPackage, vfxCall2);
				}
				else
				{
					Play(vfxCall2.effect, vfxCall2.localPos, vfxCall2.changeColor, vfxCall2.color, vfxCall2.text, simRunner.RenderLayer);
					if (vfxCall2.effect == VFXType.explosion)
					{
						PushCrumbleEffectsFromExplosion(vfxCall2.localPos, vfxCall2.crumblePushAngle);
					}
				}
			}
			prevRenderPackage = renderPackage;
		}
		DrawMovingMeshEffects();
		DrawCrumbleEffects();
		DrawCrumbleDecorationEffects();
		UpdateMovingMeshEffects();
		UpdateCrumbleEffects();
	}

	public static float CalculateCrumbleSpawnChance(int effectCountLimit, int activeEffectCount, int candidateCount)
	{
		if (effectCountLimit <= 0 || candidateCount <= 0)
		{
			return 0f;
		}
		return Mathf.Clamp01((float)Mathf.Max(0, effectCountLimit - activeEffectCount) / (float)candidateCount);
	}

	public static float CalculateRateControlledCrumbleSpawnChance(float batchSpawnChance, float candidateRate, float expirationRate, int effectCountLimit, int activeEffectCount, float settlingTime, float historyConfidence)
	{
		if (candidateRate <= 0f || settlingTime <= 0f)
		{
			return batchSpawnChance;
		}
		float num = (float)(effectCountLimit - activeEffectCount) / settlingTime;
		float b = Mathf.Clamp01(Mathf.Max(0f, expirationRate + num) / candidateRate);
		return Mathf.Lerp(batchSpawnChance, b, Mathf.Clamp01(historyConfidence));
	}

	private float CalculateCrumbleSpawnChanceForBatch(float batchSpawnChance, int effectCountLimit, int activeEffectCount, int candidateCount)
	{
		if (candidateCount <= 0)
		{
			return 0f;
		}
		float unscaledTime = Time.unscaledTime;
		float num = unscaledTime - lastCrumbleCandidateBatchTime;
		lastCrumbleCandidateBatchTime = unscaledTime;
		if (!float.IsFinite(num) || num > 3f)
		{
			estimatedCrumbleCandidateRate = 0f;
			estimatedCrumbleExpirationRate = 0f;
			crumbleCandidateRateHistoryTime = 0f;
			return batchSpawnChance;
		}
		if (num <= 0f)
		{
			return batchSpawnChance;
		}
		float num2 = (float)candidateCount / num;
		float t = 1f - Mathf.Exp((0f - num) / 3f);
		estimatedCrumbleCandidateRate = ((crumbleCandidateRateHistoryTime > 0f) ? Mathf.Lerp(estimatedCrumbleCandidateRate, num2, t) : num2);
		crumbleCandidateRateHistoryTime = Mathf.Min(3f, crumbleCandidateRateHistoryTime + num);
		return CalculateRateControlledCrumbleSpawnChance(batchSpawnChance, estimatedCrumbleCandidateRate, estimatedCrumbleExpirationRate, effectCountLimit, activeEffectCount, 3f, crumbleCandidateRateHistoryTime / 3f);
	}

	private void UpdateCrumbleExpirationRate(int expiredEffectCount)
	{
		float unscaledDeltaTime = Time.unscaledDeltaTime;
		if (!(unscaledDeltaTime <= 0f))
		{
			float b = (float)expiredEffectCount / unscaledDeltaTime;
			float t = 1f - Mathf.Exp((0f - unscaledDeltaTime) / 3f);
			estimatedCrumbleExpirationRate = Mathf.Lerp(estimatedCrumbleExpirationRate, b, t);
		}
	}

	private void PlayAvalancheStartSound(int blockCount, Vector3 blockPositionSum)
	{
		if (blockCount != 0 && simRunner is MainSim)
		{
			Vector3 localPosition = blockPositionSum / blockCount;
			FMODSoundManager.PlaySound(SoundEffectType.AvalancheStart, SoundManager.ZoomAdjustedPosition(localPosition), "BlockCount", blockCount);
		}
	}

	public float Play(VFXType effect, Vector3 localPos, bool changeColor = false, Color color = default(Color), string text = null, int renderLayer = 0)
	{
		GameObject effectObject = GetEffectObject(effect);
		effectObject.SetLayerRecursively(renderLayer);
		if (effectObject == null)
		{
			return 0f;
		}
		effectObject.transform.localPosition = localPos;
		IVisualEffect component = effectObject.GetComponent<IVisualEffect>();
		if (changeColor)
		{
			component.SetColor(color);
		}
		float result = 0f;
		if (text != null)
		{
			result = component.SetText(text);
		}
		component.Play();
		return result;
	}

	private GameObject GetEffectObject(VFXType effect)
	{
		float result;
		while (effectStartTimes.TryPeek(out result) && Time.time - result > 1f)
		{
			effectStartTimes.Dequeue();
		}
		float num = OptionHolder.GetFloat("vfx limit", 50f);
		float num2 = (float)effectStartTimes.Count / num;
		float num3 = num2 * num2;
		if (UnityEngine.Random.Range(0f, 1f) < num3 && effect != VFXType.print_sign)
		{
			return null;
		}
		effectStartTimes.Enqueue(Time.time);
		if (effect == VFXType.explosion)
		{
			if (Time.time - lastExplosionTime < 0.5f)
			{
				effect = VFXType.explosion_low_smoke;
			}
			lastExplosionTime = Time.time;
		}
		if (!effectPool.ContainsKey(effect))
		{
			effectPool[effect] = new List<GameObject>();
		}
		foreach (GameObject item in effectPool[effect])
		{
			if (!item.GetComponent<IVisualEffect>().IsPlaying())
			{
				return item;
			}
		}
		GameObject gameObject = UnityEngine.Object.Instantiate(GetPrefab(effect), base.transform).gameObject;
		effectPool[effect].Add(gameObject);
		return gameObject;
	}

	private GameObject GetPrefab(VFXType effect)
	{
		DesignConstants.VFXDesignConstants vfx = DesignConstants.Inst.vfx;
		return effect switch
		{
			VFXType.dust => vfx.dustPrefab, 
			VFXType.light_dust => vfx.lightDustPrefab, 
			VFXType.hit => vfx.hitPrefab, 
			VFXType.coins => vfx.coinsPrefab, 
			VFXType.water => vfx.waterPrefab, 
			VFXType.hearts => vfx.heartsPrefab, 
			VFXType.stars => vfx.starsPrefab, 
			VFXType.explosion => vfx.explosionPrefab, 
			VFXType.explosion_low_smoke => vfx.explosionLowSmokePrefab, 
			VFXType.text_popup => vfx.textPopupPrefab, 
			VFXType.print_sign => vfx.printSignPrefab, 
			_ => null, 
		};
	}

	private void UpdateMovingMeshEffects()
	{
		DesignConstants.VFXDesignConstants vfx = DesignConstants.Inst.vfx;
		DesignConstants.PiggyBankDesignConstants piggyBank = DesignConstants.Inst.piggyBank;
		foreach (KeyValuePair<Mesh, List<MovingMeshEffect>> movingMeshEffect6 in movingMeshEffects)
		{
			_ = movingMeshEffect6.Key;
			List<MovingMeshEffect> value = movingMeshEffect6.Value;
			for (int num = value.Count - 1; num >= 0; num--)
			{
				MovingMeshEffect value2 = value[num];
				Vector3 vector = piggyMesh.localPosition - value[num].localPosition;
				if (vector.magnitude < value2.speed * Time.deltaTime)
				{
					Transform parent = base.transform.parent;
					if (simRunner is MainSim)
					{
						FMODSoundManager.PlaySound(SoundEffectType.PickUpItem, piggyMesh.position / parent.localScale.x);
					}
					LeanTween.cancel(piggyMesh.gameObject);
					piggyMesh.localScale = Vector3.one;
					LeanTween.scale(piggyMesh.gameObject, Vector3.one * 1.2f, 0.1f).setLoopPingPong(1);
					Vector3 localPos = piggyMesh.localPosition + new Vector3(0f, 0f, piggyBank.coinEffectHeight);
					int renderLayer = value[num].renderLayer;
					Play(VFXType.coins, localPos, changeColor: false, default(Color), null, renderLayer);
					renderLayer = num;
					List<MovingMeshEffect> list = value;
					int index = value.Count - 1;
					MovingMeshEffect movingMeshEffect = value[value.Count - 1];
					MovingMeshEffect movingMeshEffect2 = value[num];
					MovingMeshEffect movingMeshEffect3 = (value[renderLayer] = movingMeshEffect);
					movingMeshEffect3 = (list[index] = movingMeshEffect2);
					value.RemoveAt(value.Count - 1);
				}
				else
				{
					value2.localPosition += (value2.speed * vector.normalized + Vector3.forward * value2.zVelocity) * Time.deltaTime;
					value2.scale = Mathf.Max(value2.scale - vfx.collectEffectShrinkSpeed * Time.deltaTime, 0.2f);
					value2.speed = Mathf.Min(value2.speed + vfx.collectEffectAcceleration * Time.deltaTime, vfx.collectEffectMaxSpeed);
					value2.zVelocity = Mathf.Max(value2.zVelocity - vfx.collectEffectGravity * Time.deltaTime, 0f);
					value[num] = value2;
				}
			}
		}
	}

	private void AddCrumbleEffect(RenderPackage renderPackage, Vector3Int blockPos)
	{
		if (FarmRenderer.TryGetBlockColor(renderPackage.groundData, blockPos, out var color))
		{
			GroundSO groundSo = renderPackage.groundData.GroundAt(blockPos).groundSo;
			CrumbleEffect effect = new CrumbleEffect
			{
				kind = (((object)groundSo != null && groundSo.moreVisibleCavein) ? CrumbleEffectKind.SpecialCrumble : CrumbleEffectKind.Crumble),
				localPosition = GridManager.CellToLocal(blockPos + new Vector3(0f, 0f, 0.5f)),
				rotation = Quaternion.identity,
				scale = 1f,
				lifetime = DesignConstants.Inst.vfx.crumbleEffectLifetime,
				velocity = CreateCrumbleVelocity(renderPackage, blockPos, popEffect: false),
				angularVelocity = new Vector3(UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f)),
				color = color,
				renderLayer = simRunner.RenderLayer
			};
			AddCrumbleDecorations(ref effect, renderPackage.groundData, groundSo, blockPos);
			crumbleEffects.Add(effect);
		}
	}

	private void AddBlockBreakEffect(RenderPackage renderPackage, VFXCall vfxCall)
	{
		if (vfxCall.lifetime <= 0f)
		{
			return;
		}
		Vector3Int vector3Int = LocalToVoxelBlock(vfxCall.localPos);
		if (FarmRenderer.TryGetBlockColor(renderPackage.groundData, vector3Int, out var color))
		{
			Vector3 vector = new Vector3(UnityEngine.Random.Range(-1f, 1f), UnityEngine.Random.Range(-1f, 1f), UnityEngine.Random.Range(-0.25f, 0.25f));
			if (vector.sqrMagnitude <= 0.0001f)
			{
				vector = Vector3.right;
			}
			CrumbleEffect effect = new CrumbleEffect
			{
				kind = CrumbleEffectKind.BlockBreak,
				localPosition = vfxCall.localPos,
				rotation = Quaternion.identity,
				scale = 1f,
				lifetime = vfxCall.lifetime,
				breakRotationAxis = vector.normalized,
				color = color,
				renderLayer = simRunner.RenderLayer
			};
			GroundSO groundSo = renderPackage.groundData.GroundAt(vector3Int).groundSo;
			AddCrumbleDecorations(ref effect, renderPackage.groundData, groundSo, vector3Int);
			crumbleEffects.Add(effect);
		}
	}

	private void AddFallingBambooEffect(RenderPackage renderPackage, VFXCall vfxCall)
	{
		Vector3Int blockPos = LocalToVoxelBlock(vfxCall.localPos);
		CrumbleEffect item = new CrumbleEffect
		{
			kind = CrumbleEffectKind.InvisibleBlock,
			localPosition = vfxCall.localPos,
			rotation = Quaternion.identity,
			scale = 1f,
			lifetime = DesignConstants.Inst.vfx.crumbleEffectLifetime,
			velocity = CreateCrumbleVelocity(renderPackage, blockPos, popEffect: false),
			angularVelocity = new Vector3(UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f)),
			renderLayer = simRunner.RenderLayer,
			topDecoration = new CrumbleDecoration
			{
				mesh = DesignConstants.Inst.vfx.bambooDecoration,
				localTransform = Matrix4x4.identity
			}
		};
		crumbleEffects.Add(item);
	}

	private bool AddSlidingBlockEffect(RenderPackage renderPackage, SlidingBlockCall call, float duration)
	{
		if (!CanAddSlidingBlockEffect(renderPackage, call, duration))
		{
			return false;
		}
		Vector3Int vector3Int = new Vector3Int(call.targetPos.x, call.targetPos.y, call.targetDepth);
		if (!FarmRenderer.TryGetBlockColor(renderPackage.groundData, vector3Int, out var color))
		{
			return false;
		}
		Vector3 vector = BlockCenterLocalPosition(vector3Int);
		Vector3 vector2 = (call.startAtTarget ? vector : BlockAboveColumnLocalPosition(renderPackage, call.sourcePos));
		bool flag = (vector - vector2).sqrMagnitude <= 0.0001f;
		GroundSO groundSo = renderPackage.groundData.GroundAt(vector3Int).groundSo;
		CrumbleEffect effect = new CrumbleEffect
		{
			kind = (call.popEffect ? CrumbleEffectKind.SlideAndPop : CrumbleEffectKind.SlidingBlock),
			localPosition = vector2,
			velocity = ((duration > 0f) ? ((vector - vector2) / duration) : Vector3.zero),
			rotation = Quaternion.identity,
			scale = 1f,
			elapsedTime = (flag ? (duration * (float)(1 - Mathf.Max(1, call.lifetimeCount))) : 0f),
			lifetime = duration,
			overridePopVelocity = call.overridePopVelocity,
			popVelocity = call.popVelocity,
			color = color,
			renderLayer = simRunner.RenderLayer
		};
		AddCrumbleDecorations(ref effect, renderPackage.groundData, groundSo, vector3Int);
		if (!call.popEffect)
		{
			farmRenderer.SuppressBlock(call.targetPos);
		}
		crumbleEffects.Add(effect);
		return true;
	}

	private bool CanAddSlidingBlockEffect(RenderPackage renderPackage, SlidingBlockCall call, float duration)
	{
		if (farmRenderer == null || renderPackage?.groundData == null || duration < 0f || (duration <= 0f && (!call.popEffect || !call.overrideDuration)) || (!call.popEffect && call.sourcePos == call.targetPos))
		{
			return false;
		}
		Vector2Int sizexy = renderPackage.groundData.sizexy;
		if (IsWithinGrid(call.sourcePos, sizexy))
		{
			return IsWithinGrid(call.targetPos, sizexy);
		}
		return false;
	}

	private void DrawMovingMeshEffects()
	{
		Transform parent = base.transform.parent;
		ConfigureFogProperties(movingMeshMaterialProperties, 100000f);
		RenderParams renderParams = new RenderParams(DesignConstants.Inst.farmRenderer.paletteMaterial);
		renderParams.matProps = movingMeshMaterialProperties;
		RenderParams rparams = renderParams;
		foreach (KeyValuePair<Mesh, List<MovingMeshEffect>> movingMeshEffect in movingMeshEffects)
		{
			Mesh key = movingMeshEffect.Key;
			List<MovingMeshEffect> value = movingMeshEffect.Value;
			int num = 0;
			while (num < value.Count)
			{
				int renderLayer = value[num].renderLayer;
				int num2 = 0;
				do
				{
					Matrix4x4 matrix4x = Matrix4x4.TRS(value[num].localPosition, value[num].rotation, Vector3.one * value[num].scale);
					reusableTransformBuffer[num2] = parent.localToWorldMatrix * matrix4x;
					num2++;
					num++;
				}
				while (num < value.Count && num2 < 1023 && value[num].renderLayer == renderLayer);
				rparams.layer = renderLayer;
				Graphics.RenderMeshInstanced(in rparams, key, 0, reusableTransformBuffer, num2);
			}
		}
	}

	private void AddCrumbleDecorations(ref CrumbleEffect effect, GroundData groundData, GroundSO groundSo, Vector3Int blockPos)
	{
		if (groundData == null || groundSo == null || groundSo.decorations == null || groundSo.decorations.Length == 0)
		{
			return;
		}
		UnityEngine.Random.State state = UnityEngine.Random.state;
		try
		{
			if (!IsSolidVoxel(groundData, blockPos + Vector3Int.back))
			{
				effect.topDecoration = CreateCrumbleDecoration(groundSo, blockPos, FarmRenderer.FaceDirection.Top);
			}
			if (!IsSolidVoxel(groundData, blockPos + Vector3Int.up))
			{
				effect.northDecoration = CreateCrumbleDecoration(groundSo, blockPos, FarmRenderer.FaceDirection.North);
			}
			if (!IsSolidVoxel(groundData, blockPos + Vector3Int.right))
			{
				effect.eastDecoration = CreateCrumbleDecoration(groundSo, blockPos, FarmRenderer.FaceDirection.East);
			}
			if (!IsSolidVoxel(groundData, blockPos + Vector3Int.down))
			{
				effect.southDecoration = CreateCrumbleDecoration(groundSo, blockPos, FarmRenderer.FaceDirection.South);
			}
			if (!IsSolidVoxel(groundData, blockPos + Vector3Int.left))
			{
				effect.westDecoration = CreateCrumbleDecoration(groundSo, blockPos, FarmRenderer.FaceDirection.West);
			}
		}
		finally
		{
			UnityEngine.Random.state = state;
		}
	}

	private CrumbleDecoration CreateCrumbleDecoration(GroundSO groundSo, Vector3Int blockPos, FarmRenderer.FaceDirection faceDirection)
	{
		float rotation;
		Mesh mesh = groundSo.SampleDecoration(blockPos.x, blockPos.y, blockPos.z, faceDirection, out rotation);
		if (mesh == null)
		{
			return default(CrumbleDecoration);
		}
		Quaternion decorationRotation = FarmRenderer.GetDecorationRotation(faceDirection, rotation);
		return new CrumbleDecoration
		{
			mesh = mesh,
			localTransform = Matrix4x4.Rotate(decorationRotation)
		};
	}

	private Vector2 CalculateDownhillDirection(RenderPackage renderPackage, Vector3Int blockPos)
	{
		if (renderPackage?.groundData == null)
		{
			return Vector2.zero;
		}
		Vector2Int sizexy = renderPackage.groundData.sizexy;
		int[] cellDepths = renderPackage.cellDepths;
		if (cellDepths == null || cellDepths.Length != sizexy.x * sizexy.y)
		{
			return Vector2.zero;
		}
		int num = cellDepths[blockPos.y * sizexy.x + blockPos.x];
		Vector2 zero = Vector2.zero;
		for (int i = -1; i <= 1; i++)
		{
			for (int j = -1; j <= 1; j++)
			{
				if (j != 0 || i != 0)
				{
					int num2 = blockPos.x + j;
					int num3 = blockPos.y + i;
					if (num2 < 0 || num2 >= sizexy.x || num3 < 0 || num3 >= sizexy.y)
					{
						zero += new Vector2(j, i).normalized;
						continue;
					}
					int num4 = cellDepths[num3 * sizexy.x + num2];
					zero += new Vector2(j, i).normalized * Mathf.Sign(num4 - num);
				}
			}
		}
		return zero.normalized;
	}

	private Vector3 CreateCrumbleVelocity(RenderPackage renderPackage, Vector3Int blockPos, bool popEffect)
	{
		Vector2 vector = CalculateDownhillDirection(renderPackage, blockPos);
		if (vector == Vector2.zero)
		{
			float f = UnityEngine.Random.Range(0f, 360f) * (MathF.PI / 180f);
			vector = new Vector2(Mathf.Cos(f), Mathf.Sin(f));
		}
		float minInclusive = Mathf.Max(0f, Mathf.Min(DesignConstants.Inst.vfx.crumbleEffectStartSpeedMin, DesignConstants.Inst.vfx.crumbleEffectStartSpeedMax));
		float maxInclusive = Mathf.Max(0f, Mathf.Max(DesignConstants.Inst.vfx.crumbleEffectStartSpeedMin, DesignConstants.Inst.vfx.crumbleEffectStartSpeedMax));
		Vector3 vector2 = new Vector3(0f - vector.x, vector.y, 0f) * UnityEngine.Random.Range(minInclusive, maxInclusive);
		float num = Mathf.Abs(DesignConstants.Inst.vfx.crumbleEffectStartDirectionRandomAngle);
		vector2 = Quaternion.AngleAxis(UnityEngine.Random.Range(0f - num, num), Vector3.forward) * vector2;
		if (popEffect)
		{
			vector2 += Vector3.forward * DesignConstants.Inst.vfx.popEffectZVelocity;
		}
		return vector2;
	}

	private void PushCrumbleEffectsFromExplosion(Vector3 explosionLocalPos, float pushAngle)
	{
		float explosionCrumblePushHorizontal = DesignConstants.Inst.vfx.explosionCrumblePushHorizontal;
		float explosionCrumblePushVertical = DesignConstants.Inst.vfx.explosionCrumblePushVertical;
		float explosionCrumblePushRange = DesignConstants.Inst.vfx.explosionCrumblePushRange;
		if (explosionCrumblePushRange <= 0f)
		{
			return;
		}
		float maxLength = Mathf.Max(0f, DesignConstants.Inst.vfx.explosionCrumbleMaxSpeed);
		for (int i = 0; i < crumbleEffects.Count; i++)
		{
			CrumbleEffect value = crumbleEffects[i];
			if ((value.kind != CrumbleEffectKind.Crumble && value.kind != CrumbleEffectKind.SpecialCrumble && value.kind != CrumbleEffectKind.InvisibleBlock) || value.wasPushedByExplosion)
			{
				continue;
			}
			Vector3 vector = value.localPosition - explosionLocalPos;
			float magnitude = vector.magnitude;
			if (!(magnitude >= explosionCrumblePushRange))
			{
				vector.z = 0f;
				if (vector.sqrMagnitude <= 0.0001f)
				{
					float f = UnityEngine.Random.Range(0f, 360f) * (MathF.PI / 180f);
					vector = new Vector3(Mathf.Cos(f), Mathf.Sin(f), 0f);
				}
				float num = Mathf.Clamp01((explosionCrumblePushRange - magnitude) / explosionCrumblePushRange);
				Vector3 vector2 = Quaternion.AngleAxis(pushAngle, Vector3.forward) * vector.normalized;
				value.velocity = Vector3.ClampMagnitude(value.velocity + (vector2 * explosionCrumblePushHorizontal + Vector3.forward * explosionCrumblePushVertical) * num * num, maxLength);
				value.wasPushedByExplosion = true;
				crumbleEffects[i] = value;
			}
		}
	}

	private void UpdateCrumbleEffects()
	{
		int count = crumbleEffects.Count;
		DesignConstants.VFXDesignConstants vfx = DesignConstants.Inst.vfx;
		GroundData groundData = prevRenderPackage?.groundData;
		for (int num = crumbleEffects.Count - 1; num >= 0; num--)
		{
			CrumbleEffect effect = crumbleEffects[num];
			if (effect.kind == CrumbleEffectKind.SlidingBlock || effect.kind == CrumbleEffectKind.SlideAndPop)
			{
				if (effect.elapsedTime >= effect.lifetime)
				{
					if (!HasHorizontalVelocity(effect.velocity) || Mathf.Approximately(effect.velocity.z, 0f))
					{
						if (effect.kind == CrumbleEffectKind.SlideAndPop)
						{
							TurnSlideAndPopIntoPop(ref effect);
							crumbleEffects[num] = effect;
							continue;
						}
						farmRenderer?.ReleaseBlockSuppression(GridManager.LocalToCell(effect.localPosition));
						List<CrumbleEffect> list = crumbleEffects;
						int index = num;
						List<CrumbleEffect> list2 = crumbleEffects;
						int index2 = crumbleEffects.Count - 1;
						CrumbleEffect crumbleEffect = crumbleEffects[crumbleEffects.Count - 1];
						CrumbleEffect crumbleEffect2 = crumbleEffects[num];
						CrumbleEffect crumbleEffect3 = (list[index] = crumbleEffect);
						crumbleEffect3 = (list2[index2] = crumbleEffect2);
						crumbleEffects.RemoveAt(crumbleEffects.Count - 1);
						continue;
					}
					effect.velocity = Vector3.forward * effect.velocity.z;
					effect.elapsedTime = 0f;
				}
				UpdateSlidingBlockEffect(ref effect);
				crumbleEffects[num] = effect;
				continue;
			}
			if (effect.kind == CrumbleEffectKind.BlockBreak)
			{
				UpdateBlockBreakEffect(ref effect, vfx);
				if (effect.elapsedTime >= effect.lifetime)
				{
					List<CrumbleEffect> list3 = crumbleEffects;
					int index2 = num;
					List<CrumbleEffect> list2 = crumbleEffects;
					int index = crumbleEffects.Count - 1;
					CrumbleEffect crumbleEffect2 = crumbleEffects[crumbleEffects.Count - 1];
					CrumbleEffect crumbleEffect = crumbleEffects[num];
					CrumbleEffect crumbleEffect3 = (list3[index2] = crumbleEffect2);
					crumbleEffect3 = (list2[index] = crumbleEffect);
					crumbleEffects.RemoveAt(crumbleEffects.Count - 1);
				}
				else
				{
					crumbleEffects[num] = effect;
				}
				continue;
			}
			effect.elapsedTime += Time.deltaTime * vfx.crumbleEffectMoveSpeedLifetimeSpeedMultiplier.Evaluate(effect.velocity.magnitude) * GetCrumbleLifetimeSpeedMultiplierNearMainDrone(effect.localPosition, effect.velocity, prevRenderPackage, vfx.crumbleEffectDroneProximityLifetimeRadiusByWorldSize.Evaluate(groundData.sizexy.x), vfx.crumbleEffectDroneProximityLifetimeSpeedMultiplier, effect.kind == CrumbleEffectKind.SpecialCrumble || effect.kind == CrumbleEffectKind.InvisibleBlock);
			if (effect.elapsedTime >= effect.lifetime)
			{
				List<CrumbleEffect> list4 = crumbleEffects;
				int index = num;
				List<CrumbleEffect> list2 = crumbleEffects;
				int index2 = crumbleEffects.Count - 1;
				CrumbleEffect crumbleEffect = crumbleEffects[crumbleEffects.Count - 1];
				CrumbleEffect crumbleEffect2 = crumbleEffects[num];
				CrumbleEffect crumbleEffect3 = (list4[index] = crumbleEffect);
				crumbleEffect3 = (list2[index2] = crumbleEffect2);
				crumbleEffects.RemoveAt(crumbleEffects.Count - 1);
				continue;
			}
			float time = effect.elapsedTime / effect.lifetime;
			float friction = vfx.crumbleEffectCollisionFriction * vfx.crumbleEffectCollisionFrictionOverLifetime.Evaluate(time);
			effect.velocity += Vector3.back * vfx.crumbleEffectGravity * Time.deltaTime;
			effect.localPosition += effect.velocity * Time.deltaTime;
			ResolveCrumbleVoxelCollision(ref effect, groundData, vfx.crumbleEffectCollisionRestitution, friction, vfx.crumbleEffectMaxAngularSpeed);
			effect.rotation = (Quaternion.Euler(effect.angularVelocity * Time.deltaTime) * effect.rotation).normalized;
			time = effect.elapsedTime / effect.lifetime;
			if (effect.kind == CrumbleEffectKind.SpecialCrumble)
			{
				effect.scale = vfx.crumbleEffectSpecialSizeOverLifetime.Evaluate(time);
			}
			else
			{
				effect.scale = vfx.crumbleEffectSizeOverLifetime.Evaluate(time);
			}
			crumbleEffects[num] = effect;
		}
		UpdateCrumbleExpirationRate(count - crumbleEffects.Count);
	}

	private void UpdateSlidingBlockEffect(ref CrumbleEffect effect)
	{
		float num = Mathf.Min(Time.deltaTime * Mathf.Max(0f, (float)(simRunner?.TimeFactor ?? 1.0)), effect.lifetime - effect.elapsedTime);
		Vector3 vector = (HasHorizontalVelocity(effect.velocity) ? new Vector3(effect.velocity.x, effect.velocity.y, 0f) : effect.velocity);
		effect.localPosition += vector * num;
		effect.elapsedTime += num;
	}

	private static bool HasHorizontalVelocity(Vector3 velocity)
	{
		if (Mathf.Approximately(velocity.x, 0f))
		{
			return !Mathf.Approximately(velocity.y, 0f);
		}
		return true;
	}

	private void TurnSlideAndPopIntoPop(ref CrumbleEffect effect)
	{
		Vector3Int blockPos = LocalToVoxelBlock(effect.localPosition);
		effect.kind = CrumbleEffectKind.SpecialCrumble;
		effect.velocity = (effect.overridePopVelocity ? effect.popVelocity : CreateCrumbleVelocity(prevRenderPackage, blockPos, popEffect: true));
		effect.angularVelocity = new Vector3(UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f));
		effect.elapsedTime = 0f;
		effect.lifetime = DesignConstants.Inst.vfx.crumbleEffectLifetime;
		effect.rotation = Quaternion.identity;
		effect.scale = 1f;
	}

	private void UpdateBlockBreakEffect(ref CrumbleEffect effect, DesignConstants.VFXDesignConstants vfxDesign)
	{
		effect.elapsedTime += Time.deltaTime * Mathf.Max(0f, (float)(simRunner?.TimeFactor ?? 1.0));
		float num = ((effect.lifetime > 0f) ? Mathf.Clamp01(effect.elapsedTime / effect.lifetime) : 1f);
		float angle = Mathf.Sin(effect.elapsedTime * Mathf.Max(0f, vfxDesign.blockBreakEffectWigglesPerSecond) * MathF.PI * 2f) * Mathf.Max(0f, vfxDesign.blockBreakEffectRotationAngle) * num;
		effect.rotation = Quaternion.AngleAxis(angle, effect.breakRotationAxis);
		effect.scale = vfxDesign.blockBreakEffectSizeOverLifetime.Evaluate(num);
	}

	private void TurnBlockBreakIntoCrumble(ref CrumbleEffect effect)
	{
		Vector3Int blockPos = LocalToVoxelBlock(effect.localPosition);
		Vector2 vector = CalculateDownhillDirection(prevRenderPackage, blockPos);
		if (vector == Vector2.zero)
		{
			float f = UnityEngine.Random.Range(0f, 360f) * (MathF.PI / 180f);
			vector = new Vector2(Mathf.Cos(f), Mathf.Sin(f));
		}
		float minInclusive = Mathf.Max(0f, Mathf.Min(DesignConstants.Inst.vfx.crumbleEffectStartSpeedMin, DesignConstants.Inst.vfx.crumbleEffectStartSpeedMax));
		float maxInclusive = Mathf.Max(0f, Mathf.Max(DesignConstants.Inst.vfx.crumbleEffectStartSpeedMin, DesignConstants.Inst.vfx.crumbleEffectStartSpeedMax));
		Vector3 vector2 = new Vector3(0f - vector.x, vector.y, 0f) * UnityEngine.Random.Range(minInclusive, maxInclusive);
		float num = Mathf.Abs(DesignConstants.Inst.vfx.crumbleEffectStartDirectionRandomAngle);
		effect.kind = CrumbleEffectKind.Crumble;
		effect.rotation = Quaternion.identity;
		effect.scale = 1f;
		effect.velocity = Quaternion.AngleAxis(UnityEngine.Random.Range(0f - num, num), Vector3.forward) * vector2;
		effect.angularVelocity = new Vector3(UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f), UnityEngine.Random.Range(-90f, 90f));
		effect.elapsedTime = 0f;
		effect.lifetime = DesignConstants.Inst.vfx.crumbleEffectLifetime;
		effect.breakRotationAxis = default(Vector3);
	}

	private float GetCrumbleLifetimeSpeedMultiplierNearMainDrone(Vector3 localPosition, Vector3 velocity, RenderPackage renderPackage, float radius, float maxMultiplier, bool isSpecial)
	{
		if (velocity.z > 0.1f || isSpecial)
		{
			return 1f;
		}
		if (renderPackage == null || radius <= 0f)
		{
			return 1f;
		}
		float cameraProjectedDistanceToMainDrone = GetCameraProjectedDistanceToMainDrone(localPosition, renderPackage);
		float t = 1f - Mathf.Clamp01(cameraProjectedDistanceToMainDrone / radius);
		return Mathf.Lerp(1f, Mathf.Max(1f, maxMultiplier), t);
	}

	private float GetCameraProjectedDistanceToMainDrone(Vector3 localPosition, RenderPackage renderPackage)
	{
		Transform transform = simRunner?.SceneScaler;
		if ((object)farmCamera == null || (object)transform == null)
		{
			return float.PositiveInfinity;
		}
		Vector3 mainDroneLocalPosition = renderPackage.mainDroneLocalPosition;
		Vector3 vector = transform.TransformPoint(localPosition);
		Vector3 vector2 = transform.TransformPoint(mainDroneLocalPosition);
		Vector3 position = farmCamera.transform.position;
		Vector3 forward = farmCamera.transform.forward;
		Vector3 vector3 = vector - position;
		Vector3 lhs = vector2 - position;
		float num = Vector3.Dot(vector3, forward);
		float num2 = Vector3.Dot(lhs, forward);
		if (num <= 0f || num >= num2)
		{
			return float.PositiveInfinity;
		}
		Vector3 position2 = position + vector3 * (num2 / num);
		return Vector3.Distance(transform.InverseTransformPoint(position2), mainDroneLocalPosition);
	}

	private void ResolveCrumbleVoxelCollision(ref CrumbleEffect effect, GroundData groundData, float restitution, float friction, float maxAngularSpeed)
	{
		if (groundData == null || effect.scale <= 0f)
		{
			return;
		}
		float num = effect.scale * 0.5f;
		if (!TryGetSphereVoxelCollision(effect.localPosition, num, groundData, out var deepestPenetration, out var contactNormal))
		{
			return;
		}
		effect.localPosition += contactNormal * (deepestPenetration + 0.001f);
		float num2 = Vector3.Dot(effect.velocity, contactNormal);
		if (num2 >= 0f)
		{
			effect.angularVelocity = Vector3.ClampMagnitude(effect.angularVelocity, maxAngularSpeed);
			return;
		}
		float num3 = 0f - num2;
		DesignConstants.VFXDesignConstants vfx = DesignConstants.Inst.vfx;
		if (simRunner is MainSim && crumbleEffects.Count > vfx.crumbleEffectCollisionSoundBlockCountThreshold && num3 > vfx.crumbleEffectCollisionSoundForceThreshold)
		{
			FMODSoundManager.PlaySound(SoundEffectType.AvalancheCollision, SoundManager.ZoomAdjustedPosition(effect.localPosition), "Force", num3);
		}
		Vector3 vector = Vector3.ProjectOnPlane(effect.velocity, contactNormal);
		float num4 = Mathf.Clamp01(friction);
		if (effect.velocity.z > 0f)
		{
			num4 = 0f;
		}
		effect.velocity = vector * (1f - num4) - contactNormal * num2 * Mathf.Clamp01(restitution);
		if (vector.sqrMagnitude > 0.0001f)
		{
			Vector3 b = Vector3.Cross(contactNormal, vector) / num * 57.29578f;
			effect.angularVelocity = Vector3.Lerp(effect.angularVelocity, b, num4);
		}
		effect.angularVelocity = Vector3.ClampMagnitude(effect.angularVelocity, maxAngularSpeed);
	}

	private bool TryGetSphereVoxelCollision(Vector3 center, float radius, GroundData groundData, out float deepestPenetration, out Vector3 contactNormal)
	{
		deepestPenetration = 0f;
		contactNormal = default(Vector3);
		Vector3Int vector3Int = LocalToVoxelBlock(center);
		int num = Mathf.CeilToInt(radius + 0.5f);
		for (int i = vector3Int.x - num; i <= vector3Int.x + num; i++)
		{
			for (int j = vector3Int.y - num; j <= vector3Int.y + num; j++)
			{
				for (int k = vector3Int.z - num; k <= vector3Int.z + num; k++)
				{
					Vector3Int vector3Int2 = new Vector3Int(i, j, k);
					if (!IsSolidVoxel(groundData, vector3Int2))
					{
						continue;
					}
					Vector3 vector = GridManager.CellToLocal(vector3Int2 + new Vector3(0f, 0f, 0.5f));
					Vector3 vector2 = center - vector;
					Vector3 vector3 = vector + new Vector3(Mathf.Clamp(vector2.x, -0.5f, 0.5f), Mathf.Clamp(vector2.y, -0.5f, 0.5f), Mathf.Clamp(vector2.z, -0.5f, 0.5f));
					Vector3 vector4 = center - vector3;
					float magnitude = vector4.magnitude;
					float num2;
					Vector3 vector5;
					if (magnitude > 0.0001f)
					{
						num2 = radius - magnitude;
						vector5 = vector4 / magnitude;
					}
					else
					{
						Vector3 vector6 = new Vector3(0.5f - Mathf.Abs(vector2.x), 0.5f - Mathf.Abs(vector2.y), 0.5f - Mathf.Abs(vector2.z));
						if (vector6.x <= vector6.y && vector6.x <= vector6.z)
						{
							num2 = radius + vector6.x;
							vector5 = ((vector2.x >= 0f) ? Vector3.right : Vector3.left);
						}
						else if (vector6.y <= vector6.z)
						{
							num2 = radius + vector6.y;
							vector5 = ((vector2.y >= 0f) ? Vector3.up : Vector3.down);
						}
						else
						{
							num2 = radius + vector6.z;
							vector5 = ((vector2.z >= 0f) ? Vector3.forward : Vector3.back);
						}
					}
					if (num2 > deepestPenetration)
					{
						deepestPenetration = num2;
						contactNormal = vector5;
					}
				}
			}
		}
		return deepestPenetration > 0f;
	}

	private Vector3Int LocalToVoxelBlock(Vector3 localPos)
	{
		return new Vector3Int(Mathf.RoundToInt(0f - localPos.x), Mathf.RoundToInt(localPos.y), Mathf.FloorToInt(0f - localPos.z));
	}

	private static Vector3 BlockAboveColumnLocalPosition(RenderPackage renderPackage, Vector2Int blockPos)
	{
		int depth = renderPackage.cellDepths[blockPos.x + renderPackage.groundData.sizexy.x * blockPos.y];
		return GridManager.CellToLocal(blockPos, depth) + Vector3.forward * 0.5f;
	}

	private static Vector3 BlockCenterLocalPosition(Vector3Int blockPos)
	{
		return GridManager.CellToLocal(blockPos + new Vector3(0f, 0f, 0.5f));
	}

	private static bool IsWithinGrid(Vector2Int blockPos, Vector2Int gridSize)
	{
		if (blockPos.x >= 0 && blockPos.x < gridSize.x && blockPos.y >= 0)
		{
			return blockPos.y < gridSize.y;
		}
		return false;
	}

	private bool IsSolidVoxel(GroundData groundData, Vector3Int blockPos)
	{
		GroundData.Chunk chunk = groundData.ChunkAt(blockPos.z);
		if (chunk != null && blockPos.x >= 0 && blockPos.x < groundData.sizexy.x && blockPos.y >= 0 && blockPos.y < groundData.sizexy.y && blockPos.z >= chunk.startingDepth && blockPos.z < chunk.startingDepth + 16)
		{
			return chunk.IsBlockPresent(blockPos.x, blockPos.y, blockPos.z, groundData.sizexy);
		}
		return false;
	}

	private void DrawCrumbleEffects()
	{
		Transform parent = base.transform.parent;
		ConfigureFogProperties(crumbleMaterialProperties, 100000f);
		RenderParams renderParams = new RenderParams(DesignConstants.Inst.farmRenderer.crumbleMaterial);
		renderParams.matProps = crumbleMaterialProperties;
		RenderParams rparams = renderParams;
		int i = 0;
		while (i < crumbleEffects.Count)
		{
			for (; i < crumbleEffects.Count && crumbleEffects[i].kind == CrumbleEffectKind.InvisibleBlock; i++)
			{
			}
			if (i >= crumbleEffects.Count)
			{
				break;
			}
			int renderLayer = crumbleEffects[i].renderLayer;
			int num = 0;
			do
			{
				CrumbleEffect crumbleEffect = crumbleEffects[i];
				if (crumbleEffect.kind != CrumbleEffectKind.InvisibleBlock)
				{
					Matrix4x4 matrix4x = Matrix4x4.TRS(crumbleEffect.localPosition, crumbleEffect.rotation, Vector3.one * crumbleEffect.scale);
					reusableTransformBuffer[num] = parent.localToWorldMatrix * matrix4x;
					reusableColorBuffer[num] = crumbleEffect.color;
					num++;
				}
				i++;
			}
			while (i < crumbleEffects.Count && num < 1023 && crumbleEffects[i].renderLayer == renderLayer);
			if (num != 0)
			{
				crumbleMaterialProperties.SetVectorArray("_Color", reusableColorBuffer);
				rparams.layer = renderLayer;
				Graphics.RenderMeshInstanced(in rparams, crumbleMesh, 0, reusableTransformBuffer, num);
			}
		}
	}

	private void DrawCrumbleDecorationEffects()
	{
		foreach (Mesh activeCrumbleDecorationMesh in activeCrumbleDecorationMeshes)
		{
			crumbleDecorationBatches[activeCrumbleDecorationMesh].Clear();
		}
		activeCrumbleDecorationMeshes.Clear();
		Matrix4x4 localToWorldMatrix = base.transform.parent.localToWorldMatrix;
		for (int i = 0; i < crumbleEffects.Count; i++)
		{
			CrumbleEffect crumbleEffect = crumbleEffects[i];
			Matrix4x4 matrix4x = Matrix4x4.TRS(crumbleEffect.localPosition, crumbleEffect.rotation, Vector3.one * crumbleEffect.scale);
			Matrix4x4 worldTransform = localToWorldMatrix * matrix4x;
			AddCrumbleDecorationTransform(crumbleEffect.topDecoration, worldTransform);
			AddCrumbleDecorationTransform(crumbleEffect.northDecoration, worldTransform);
			AddCrumbleDecorationTransform(crumbleEffect.eastDecoration, worldTransform);
			AddCrumbleDecorationTransform(crumbleEffect.southDecoration, worldTransform);
			AddCrumbleDecorationTransform(crumbleEffect.westDecoration, worldTransform);
		}
		ConfigureFogProperties(fogMaterialProperties, 100000f);
		RenderParams renderParams = new RenderParams(DesignConstants.Inst.farmRenderer.paletteMaterial);
		renderParams.matProps = fogMaterialProperties;
		renderParams.layer = simRunner.RenderLayer;
		RenderParams rparams = renderParams;
		foreach (Mesh activeCrumbleDecorationMesh2 in activeCrumbleDecorationMeshes)
		{
			List<Matrix4x4> list = crumbleDecorationBatches[activeCrumbleDecorationMesh2];
			for (int j = 0; j < list.Count; j += 1023)
			{
				int instanceCount = Mathf.Min(1023, list.Count - j);
				Graphics.RenderMeshInstanced(in rparams, activeCrumbleDecorationMesh2, 0, list, instanceCount, j);
			}
		}
	}

	private void AddCrumbleDecorationTransform(CrumbleDecoration decoration, Matrix4x4 worldTransform)
	{
		if (!(decoration.mesh == null))
		{
			if (!crumbleDecorationBatches.TryGetValue(decoration.mesh, out var value))
			{
				value = new List<Matrix4x4>();
				crumbleDecorationBatches.Add(decoration.mesh, value);
			}
			if (value.Count == 0)
			{
				activeCrumbleDecorationMeshes.Add(decoration.mesh);
			}
			value.Add(worldTransform * decoration.localTransform);
		}
	}

	private void ConfigureFogProperties(MaterialPropertyBlock properties, float? maxZOverride = null)
	{
		RenderPackage renderPackage = prevRenderPackage;
		if (renderPackage?.groundData != null && !(simRunner?.SceneScaler == null))
		{
			Transform sceneScaler = simRunner.SceneScaler;
			DesignConstants.FarmRendererDesignConstants farmRendererDesignConstants = DesignConstants.Inst.farmRenderer;
			bool num = simRunner.InstalledDlcs.HasFlag(EDlcMask.Minig);
			float num2 = (num ? farmRendererDesignConstants.EffectiveFogHeight(renderPackage.groundData.sizexy) : (-0.5f));
			float num3 = ((sceneScaler.localScale.z != 0f) ? (sceneScaler.localPosition.z / sceneScaler.localScale.z) : 0f);
			float z = sceneScaler.localToWorldMatrix.MultiplyPoint(new Vector3(0f, 0f, num2 - num3)).z;
			float num4 = (num ? farmRendererDesignConstants.EffectiveFogFade(renderPackage.groundData.sizexy) : 2f);
			properties.SetFloat("_MinZ", z);
			properties.SetFloat("_MinFadeDistance", num4 * sceneScaler.localScale.z);
			properties.SetColor("_MinFogColor", farmRendererDesignConstants.FogColor);
			properties.SetFloat("_MaxZ", maxZOverride ?? farmRendererDesignConstants.maxFarmRenderHeight);
			properties.SetFloat("_FadeDistance", farmRendererDesignConstants.maxRenderFadeDistance);
		}
	}

	private static Mesh CreateCubeMesh()
	{
		Vector3[] vertices = new Vector3[24]
		{
			new Vector3(-0.5f, -0.5f, 0.5f),
			new Vector3(0.5f, -0.5f, 0.5f),
			new Vector3(0.5f, 0.5f, 0.5f),
			new Vector3(-0.5f, 0.5f, 0.5f),
			new Vector3(0.5f, -0.5f, -0.5f),
			new Vector3(-0.5f, -0.5f, -0.5f),
			new Vector3(-0.5f, 0.5f, -0.5f),
			new Vector3(0.5f, 0.5f, -0.5f),
			new Vector3(-0.5f, -0.5f, -0.5f),
			new Vector3(-0.5f, -0.5f, 0.5f),
			new Vector3(-0.5f, 0.5f, 0.5f),
			new Vector3(-0.5f, 0.5f, -0.5f),
			new Vector3(0.5f, -0.5f, 0.5f),
			new Vector3(0.5f, -0.5f, -0.5f),
			new Vector3(0.5f, 0.5f, -0.5f),
			new Vector3(0.5f, 0.5f, 0.5f),
			new Vector3(-0.5f, 0.5f, 0.5f),
			new Vector3(0.5f, 0.5f, 0.5f),
			new Vector3(0.5f, 0.5f, -0.5f),
			new Vector3(-0.5f, 0.5f, -0.5f),
			new Vector3(-0.5f, -0.5f, -0.5f),
			new Vector3(0.5f, -0.5f, -0.5f),
			new Vector3(0.5f, -0.5f, 0.5f),
			new Vector3(-0.5f, -0.5f, 0.5f)
		};
		Vector3[] normals = new Vector3[24]
		{
			Vector3.forward,
			Vector3.forward,
			Vector3.forward,
			Vector3.forward,
			Vector3.back,
			Vector3.back,
			Vector3.back,
			Vector3.back,
			Vector3.left,
			Vector3.left,
			Vector3.left,
			Vector3.left,
			Vector3.right,
			Vector3.right,
			Vector3.right,
			Vector3.right,
			Vector3.up,
			Vector3.up,
			Vector3.up,
			Vector3.up,
			Vector3.down,
			Vector3.down,
			Vector3.down,
			Vector3.down
		};
		int[] triangles = new int[36]
		{
			0, 1, 2, 0, 2, 3, 4, 5, 6, 4,
			6, 7, 8, 9, 10, 8, 10, 11, 12, 13,
			14, 12, 14, 15, 16, 17, 18, 16, 18, 19,
			20, 21, 22, 20, 22, 23
		};
		Mesh mesh = new Mesh();
		mesh.name = "Crumble Cube";
		mesh.vertices = vertices;
		mesh.normals = normals;
		mesh.triangles = triangles;
		mesh.RecalculateBounds();
		return mesh;
	}

	private void OnDisable()
	{
		CancelSlidingBlockEffects();
	}

	private void CancelSlidingBlockEffects()
	{
		for (int num = crumbleEffects.Count - 1; num >= 0; num--)
		{
			CrumbleEffect crumbleEffect = crumbleEffects[num];
			if (crumbleEffect.kind == CrumbleEffectKind.SlidingBlock || crumbleEffect.kind == CrumbleEffectKind.SlideAndPop)
			{
				if (crumbleEffect.kind == CrumbleEffectKind.SlidingBlock)
				{
					float num2 = Mathf.Max(0f, crumbleEffect.lifetime - crumbleEffect.elapsedTime);
					Vector3 localPos = ((!HasHorizontalVelocity(crumbleEffect.velocity)) ? (crumbleEffect.localPosition + crumbleEffect.velocity * num2) : (crumbleEffect.localPosition + new Vector3(crumbleEffect.velocity.x, crumbleEffect.velocity.y, 0f) * num2 + Vector3.forward * crumbleEffect.velocity.z * crumbleEffect.lifetime));
					farmRenderer?.ReleaseBlockSuppression(GridManager.LocalToCell(localPos));
				}
				crumbleEffects.RemoveAt(num);
			}
		}
	}

	private void OnDestroy()
	{
		CancelSlidingBlockEffects();
		UnityEngine.Object.Destroy(crumbleMesh);
	}
}
internal struct MovingMeshEffect
{
	public Vector3 localPosition;

	public float scale;

	public Quaternion rotation;

	public float speed;

	public float zVelocity;

	public int renderLayer;
}
internal struct CrumbleEffect
{
	public CrumbleEffectKind kind;

	public bool wasPushedByExplosion;

	public Vector3 localPosition;

	public float scale;

	public Quaternion rotation;

	public Vector3 velocity;

	public bool overridePopVelocity;

	public Vector3 popVelocity;

	public Vector3 angularVelocity;

	public float elapsedTime;

	public float lifetime;

	public Vector3 breakRotationAxis;

	public Color color;

	public int renderLayer;

	public CrumbleDecoration topDecoration;

	public CrumbleDecoration northDecoration;

	public CrumbleDecoration eastDecoration;

	public CrumbleDecoration southDecoration;

	public CrumbleDecoration westDecoration;
}
internal enum CrumbleEffectKind
{
	Crumble,
	SpecialCrumble,
	InvisibleBlock,
	BlockBreak,
	SlidingBlock,
	SlideAndPop
}
internal struct CrumbleDecoration
{
	public Mesh mesh;

	public Matrix4x4 localTransform;
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

	public int depth;

	private Simulation sim;

	private DroneSO droneSO;

	public Hat hat;

	private DroneState droneState;

	private Duration animDuration;

	private Duration actionStartTime;

	private Duration diggingEndTime;

	private Vector3 startPosition;

	private Vector3 endPosition;

	private Vector3 whackingBlockDirection;

	private Quaternion startRotation = Quaternion.identity;

	private Quaternion endRotation = Quaternion.identity;

	private float printWidth;

	private const int maxFleightHeight = 18;

	private float prevRealTime = -1f;

	private Vector3 prevSpeedMeasurement = Vector3.zero;

	public int fleightHeight { get; private set; } = 1;

	public int DroneId { get; set; }

	public Drone(Simulation sim, Vector2Int pos, int droneId)
	{
		this.sim = sim;
		droneSO = ResourceManager.GetDrone();
		this.pos = pos;
		depth = sim.farm.grid.CellAtOrDefault(pos).depth;
		endPosition = sim.farm.grid.CellToLocal(pos);
		droneState = DroneState.idle;
		DroneId = droneId;
		hat = Hat.CreateDefaultHat(sim, this);
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
		float num = 1.1f;
		if (animDuration.nanoseconds > 0)
		{
			num = (float)((sim.CurrentTime - actionStartTime) / animDuration);
		}
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
			z = hat.hatSO.droneFlyHeight + endPosition.z;
			q = endRotation;
			break;
		case DroneState.moving:
			x = ExtendedLerp(startPosition.x, endPosition.x, num);
			y = ExtendedLerp(startPosition.y, endPosition.y, num);
			z = hat.hatSO.droneFlyHeight + ExtendedLerp(startPosition.z, endPosition.z, num);
			q = Quaternion.Slerp(startRotation, endRotation, num);
			break;
		case DroneState.action:
			x = endPosition.x;
			y = endPosition.y;
			z = ExtendedLerp(hat.hatSO.droneFlyHeight, hat.hatSO.droneFlyHeight - 0.4f, droneSO.actionZCurve.Evaluate(num)) + endPosition.z;
			q = endRotation;
			break;
		case DroneState.flipping:
			x = endPosition.x;
			y = endPosition.y;
			z = ExtendedLerp(hat.hatSO.droneFlyHeight, hat.hatSO.droneFlyHeight + 1f, droneSO.flipZCuve.Evaluate(num)) + endPosition.z;
			q = Quaternion.AngleAxis(ExtendedLerp(0f, 360f, EaseOutCubic(num)), Vector3.right);
			break;
		case DroneState.printing:
			x = ExtendedLerp(endPosition.x, endPosition.x + printWidth, droneSO.printXCurve.Evaluate(num));
			y = endPosition.y;
			z = ExtendedLerp(hat.hatSO.droneFlyHeight, hat.hatSO.droneFlyHeight + 1f, droneSO.printZCurve.Evaluate(num)) + endPosition.z;
			q = Quaternion.AngleAxis(ExtendedLerp(0f, 360f, droneSO.printRotationCurve.Evaluate(num)), Vector3.down);
			break;
		case DroneState.petting:
			x = ExtendedLerp(endPosition.x, startPosition.x, droneSO.petMoveXYCurve.Evaluate(num));
			y = ExtendedLerp(endPosition.y, startPosition.y, droneSO.petMoveXYCurve.Evaluate(num));
			z = ExtendedLerp(hat.hatSO.droneFlyHeight + endPosition.z, startPosition.z, droneSO.petMoveZCurve.Evaluate(num));
			q = endRotation;
			break;
		default:
			throw new Exception("this case shouldn't be reachable");
		}
		return Matrix4x4.TRS(new Vector3(x, y, z), q, Vector3.one);
	}

	public float GetDiggingTimeRemaining()
	{
		return (float)GetDiggingDurationRemaining().Seconds;
	}

	public Duration GetDiggingDurationRemaining()
	{
		if (!(diggingEndTime > sim.CurrentTime))
		{
			return new Duration(0L);
		}
		return diggingEndTime - sim.CurrentTime;
	}

	public void ChangeHat(HatSO hatSO, ProgramState programState, bool isDefault = false)
	{
		if (!hatSO.hidden && !sim.farm.IsUnlocked(hatSO.hatName))
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_missing_x_unlock", hatSO));
		}
		ChangeHat(Hat.CreateHat(hatSO, sim, this, isDefault), programState);
	}

	public void ChangeHat(Hat newHat, ProgramState programState)
	{
		Hat obj = hat;
		hat = newHat;
		obj?.OnUnequip();
		hat.OnEquip(this, programState);
		if (!hat.hatSO.rotateDroneToMove)
		{
			startRotation = (endRotation = Quaternion.identity);
		}
		if (!hat.DefaultHat)
		{
			sim.UnlockAchievement("EQUIP_A_NEW_HAT");
		}
		if ((from d in sim.farm.drones
			where d != null
			select d.hat.hatSO).Distinct().Count() >= 5)
		{
			sim.UnlockAchievement("FASHION_SHOW");
		}
	}

	public void DoAFlip()
	{
		if (!hat.hatSO.rotateDroneToMove)
		{
			droneState = DroneState.flipping;
			actionStartTime = sim.CurrentTime;
			animDuration = Duration.FromSeconds(1.0);
			sim.IncrementAchievementStat("flips", 1);
		}
	}

	public void PetThePiggy()
	{
		if (!hat.hatSO.rotateDroneToMove)
		{
			droneState = DroneState.petting;
			actionStartTime = sim.CurrentTime;
			animDuration = Duration.FromSeconds(1.0);
			endPosition = sim.farm.grid.CellToLocal(pos);
			startPosition = sim.simRunner.PiggyBankPosition;
			endRotation = Quaternion.identity;
			startRotation = Quaternion.identity;
			sim.simRunner?.PlayEffect(VFXType.hearts, startPosition);
			sim.UnlockAchievement("PET_THE_PIGGY");
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
		if (sim.simRunner != null)
		{
			sim.simRunner?.PlayEffect(VFXType.print_sign, GetTransform().GetPosition(), changeColor: false, default(Color), s);
			printWidth = droneSO.extraPrintWidth + (float)Mathf.Min(droneSO.charactersAtMaxPrintWidth, s.Length) * droneSO.characterPrintWidth;
		}
	}

	public bool Hover(int h, out double ops)
	{
		if (h < 0 || h > 18 || !((!(hat?.hatSO?.preventHover)) ?? true))
		{
			ops = sim.operationOps;
			return false;
		}
		if (sim.farm.grid.CellAt(pos).entity is Bamboo bamboo && h < bamboo.Height)
		{
			ops = sim.operationOps;
			return false;
		}
		ops = sim.actionOps;
		bool flag = h > fleightHeight;
		fleightHeight = h;
		Bamboo bamboo2 = sim.farm.grid.CellAt(pos).entity as Bamboo;
		if (bamboo2 != null && flag)
		{
			bamboo2.OnDroneLeft(DroneId);
		}
		UpdatePosition(ops);
		return true;
	}

	public bool Move(GridDirection direction, ProgramState programState, out double ops)
	{
		ops = sim.operationOps;
		Vector2Int newPos = pos + direction.GetDirectionVector();
		Vector2Int vector2Int = sim.farm.grid.Wrap(newPos);
		if (!CanMove(direction))
		{
			return false;
		}
		ops = hat.OnMove(pos, newPos, programState);
		GridController controller = sim.farm.grid.GroundAt(pos).groundSo.GetController(sim.farm.grid);
		if (controller != null)
		{
			ops = Math.Max(ops, controller.OnMove(pos, vector2Int, programState));
		}
		GridController controller2 = sim.farm.grid.GroundAt(vector2Int).groundSo.GetController(sim.farm.grid);
		if (controller2 != null && controller2 != controller)
		{
			ops = Math.Max(ops, controller2.OnMove(pos, vector2Int, programState));
		}
		if (ops <= 0.0)
		{
			ops = sim.actionOps;
		}
		if (hat.hatSO.rotateDroneToMove)
		{
			startRotation = endRotation;
			endRotation = direction.GetQuaternion();
		}
		GridManager.Cell cell = sim.farm.grid.CellAt(pos);
		float num = Vector2Int.Distance(pos, vector2Int);
		pos = vector2Int;
		if (sim.farm.grid.CellAt(pos).entity is Bamboo bamboo)
		{
			bamboo.OnDroneEntered(fleightHeight);
		}
		if (num > 8f)
		{
			UpdatePosition(0.0);
		}
		else
		{
			UpdatePosition(ops);
		}
		if (cell.entity is Bamboo bamboo2)
		{
			bamboo2.OnDroneLeft(DroneId);
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
		if (!hat.CanMoveTo(direction))
		{
			return false;
		}
		Entity entity = sim.farm.grid.CellAt(vector2Int2).entity;
		Entity entity2 = sim.farm.grid.CellAt(pos).entity;
		if ((entity != null && !entity.CanDroneMoveToFrom(direction.Reverse())) || (entity2 != null && !entity2.CanDroneMoveAwayTo(direction)))
		{
			return false;
		}
		return true;
	}

	public void Dig(Vector2Int dugPosition, out double ops)
	{
		ops = sim.operationOps;
		GridManager.Cell cell = sim.farm.grid.CellAt(dugPosition);
		ref GroundData.Ground reference = ref sim.farm.grid.GroundAt(dugPosition, cell.depth);
		GroundSO groundSo = reference.groundSo;
		if (groundSo == null)
		{
			return;
		}
		Duration collectionDuration;
		ItemBlock drops = groundSo.GetDrops(sim.farm, out collectionDuration);
		ops = Math.Ceiling((double)reference.hardness / sim.OpDuration.Seconds / sim.DiggingSpeedFactor);
		if (cell.entity != null)
		{
			cell.entity.OnDig(this, drops, ref ops);
		}
		groundSo.GetController(sim.farm.grid)?.OnDig(this, dugPosition, ref ops);
		diggingEndTime = sim.CurrentTime + sim.GetActionTime(ops);
		ResetFlightHeight(updatePosition: false);
		UpdatePosition(ops);
		if (hat.DefaultHat && hat.hatSO.hatName == "straw_hat")
		{
			ChangeHat(ResourceManager.GetHat("mining_hat"), null, isDefault: true);
		}
		else if (!hat.DefaultHat && hat.hatSO.hatName != "mining_hat")
		{
			sim.UnlockAchievement("MINING_HELMET_UNSAFE");
		}
		hat?.OnDig(this, dugPosition, ref ops);
		sim.farm.CollectItems(drops, GetTransform().GetPosition(), collectionDuration);
		if (groundSo.objectName == "petrified_pumpkin")
		{
			double number = drops.GetNumber(StringIds.PumpkinItemId);
			if (number > 0.0)
			{
				sim.IncrementAchievementStat("total_petrified_pumpkin", (int)number);
			}
		}
		ActionTween();
		sim.simRunner?.PlaySound(groundSo.digSound, dugPosition);
	}

	public void PlaceBlock(GroundSO block)
	{
		GridManager.Cell cell = sim.farm.grid.CellAt(pos);
		Vector3Int vector3Int = new Vector3Int(pos.x, pos.y, cell.depth - 1);
		sim.farm.grid.RemoveEntity((Vector2Int)vector3Int, regrowGrass: false);
		sim.farm.grid.SetGround(vector3Int, block);
		GroundSO sand = ResourceManager.GetGround("sand");
		GroundSO limestone = ResourceManager.GetGround("limestone");
		if (block == sand && !isSandSupported(vector3Int))
		{
			sim.farm.grid.ClearGround(new Vector2Int(pos.x, pos.y), cell.depth);
		}
		else if (sim.farm.grid.pyramidController.IsPyramidGround(block))
		{
			PyramidController.Pyramid pyramidAtPos = sim.farm.grid.pyramidController.GetPyramidAtPos(vector3Int);
			if (pyramidAtPos != null)
			{
				sim.farm.grid.pyramidController.ClearPyramidIfComplete(pyramidAtPos);
			}
		}
		ResetFlightHeight(updatePosition: false);
		sim.simRunner?.PlaySound(SoundEffectType.PlaceBlock, pos);
		UpdatePosition(sim.actionOps);
		ActionTween();
		sim.IncrementAchievementStat("total_placed_blocks", 1);
		if (block.objectName == "block_red" || block.objectName == "block_green" || block.objectName == "block_blue")
		{
			sim.IncrementAchievementStat("total_placed_color_blocks", 1);
		}
		if (vector3Int.z <= -150)
		{
			sim.UnlockAchievement("REACH_HEIGHT");
		}
		bool isSandSupported(Vector3Int sandPos)
		{
			sim.farm.grid.TryGetExistingGroundAt(new Vector3Int(sandPos.x, sandPos.y, sandPos.z + 1), out var ground);
			if (ground.groundSo == limestone)
			{
				return true;
			}
			if (ground.groundSo != sand)
			{
				return false;
			}
			foreach (Vector2Int item in GridManager.Neighboring8Positions(new Vector2Int(pos.x, pos.y)))
			{
				sim.farm.grid.TryGetExistingGroundAt(new Vector3Int(item.x, item.y, sandPos.z + 1), out var ground2);
				if (!(ground2.groundSo == sand) && !(ground2.groundSo == limestone))
				{
					return false;
				}
			}
			return true;
		}
	}

	public bool CanPush(GridDirection dir)
	{
		int num = sim.farm.grid.CellAt(pos).depth;
		if (!sim.farm.grid.GroundAt(pos, num).groundSo.isPushable)
		{
			return false;
		}
		Vector2Int vector2Int = sim.farm.grid.Wrap(pos + dir.GetDirectionVector());
		if (sim.farm.grid.CellAt(vector2Int).depth - 1 < num)
		{
			return false;
		}
		return true;
	}

	public bool Push(GridDirection dir, out double ops)
	{
		ops = sim.operationOps;
		int num = sim.farm.grid.CellAt(pos).depth;
		ref GroundData.Ground reference = ref sim.farm.grid.GroundAt(pos, num);
		if (!reference.groundSo.isPushable)
		{
			return false;
		}
		Vector2Int targetPos = sim.farm.grid.Wrap(pos + dir.GetDirectionVector());
		int num2 = sim.farm.grid.CellAt(targetPos).depth - 1;
		if (num2 < num)
		{
			if (reference.groundSo.objectName == "mushroom")
			{
				sim.UnlockAchievement("PUSH_MUSHROOM_BLOCKED");
			}
			return false;
		}
		ref GroundData.Ground reference2 = ref sim.farm.grid.GroundAt(pos, num);
		sim.farm.grid.GroundAt(targetPos, num2) = reference2;
		sim.farm.grid.ChunkAt(num).SetBlockPresent(pos.x, pos.y, num, sim.farm.grid.WorldSize, isPresent: false);
		sim.farm.grid.ChunkAt(num2).SetBlockPresent(targetPos.x, targetPos.y, num2, sim.farm.grid.WorldSize, isPresent: true);
		sim.farm.grid.CellAt(pos).depth++;
		sim.farm.grid.CellAt(targetPos).depth--;
		sim.farm.grid.RemoveEntity(pos, regrowGrass: false);
		sim.farm.grid.groundData.MarkPositionChanged(pos);
		sim.farm.grid.groundData.MarkPositionChanged(targetPos);
		GridController controller = reference2.groundSo.GetController(sim.farm.grid);
		if (controller == null || !controller.OnAfterPush(this, new Vector3Int(pos.x, pos.y, num), new Vector3Int(targetPos.x, targetPos.y, num2)))
		{
			sim.simRunner.SlideBlockEffect(pos, targetPos);
		}
		ResetFlightHeight();
		ops = sim.actionOps;
		return true;
	}

	public bool Swap(GridDirection dir, ProgramState state)
	{
		if (sim.farm.grid.Swap(pos, dir))
		{
			sim.simRunner?.PlaySound(SoundEffectType.SwapPlants, pos);
			ActionTween();
			return true;
		}
		Vector2Int vector2Int = pos + dir.GetDirectionVector();
		if (!sim.farm.grid.IsWithinBounds(vector2Int))
		{
			sim.simRunner.Logger.LogWarning(Localizer.Localize("warning_failed_swap_wrap"), state);
		}
		else
		{
			sim.simRunner.Logger.LogWarning(string.Format(Localizer.Localize("warning_failed_swap_unswappable"), EntityUnderDrone()), state);
		}
		ResetFlightHeight();
		return false;
	}

	public bool Harvest()
	{
		Entity entity = EntityUnderDrone();
		if (entity == null)
		{
			return false;
		}
		sim.farm.CollectItems(entity.Harvest(out var collectionDuration), GetTransform().GetPosition(), collectionDuration);
		if (fleightHeight != 1)
		{
			fleightHeight = 1;
			UpdatePosition(sim.actionOps);
		}
		else
		{
			fleightHeight = 1;
			ActionTween();
		}
		sim.simRunner?.PlaySound(entity.objectSO.harvestSound, pos);
		return true;
	}

	public bool CanHarvest()
	{
		return EntityUnderDrone()?.Harvestable ?? false;
	}

	public bool IsOver(string objName)
	{
		string text = EntityUnderDrone()?.objectSO.objectName ?? "";
		string objectName = GroundUnderDrone().objectName;
		if (!(objName == text))
		{
			return objName == objectName;
		}
		return true;
	}

	public void ChangeGround(string ground)
	{
		GroundData.Ground ground2 = sim.farm.grid.GroundAt(pos);
		GroundSO groundSo = ground2.groundSo;
		if (!groundSo.isTillable)
		{
			if (groundSo.objectName == "rock")
			{
				sim.UnlockAchievement("TILL_ROCK");
			}
			return;
		}
		if (!(EntityUnderDrone() is HedgePlant))
		{
			sim.farm.grid.RemoveEntity(pos, regrowGrass: false);
		}
		if (IsOver(ground))
		{
			sim.farm.grid.SetGround(pos, "grassland", ground2.hardness);
			if (!(EntityUnderDrone() is HedgePlant))
			{
				sim.farm.grid.SetEntity(pos, "grass");
			}
		}
		else
		{
			sim.farm.grid.SetGround(pos, ground, ground2.hardness);
		}
		ResetFlightHeight();
		ActionTween();
		sim.simRunner?.PlaySound(SoundEffectType.Till, pos);
	}

	public bool Plant(EntitySO growable, ProgramState state)
	{
		if (sim.farm.grid.CellAt(pos).entity != null && !EntityUnderDrone().objectSO.canBeOverplanted)
		{
			return false;
		}
		if (growable.IsBamboo() && sim.farm.drones.Any((Drone d) => d != null && d.DroneId != DroneId && d.fleightHeight == 0 && d.pos == pos))
		{
			sim.simRunner.Logger.LogWarning(string.Format(Localizer.Localize("warning_no_space_to_plant"), growable), state);
			return false;
		}
		if (!growable.CanBePlacedOn(sim.farm.grid.GroundAt(pos).groundSo.objectName))
		{
			sim.simRunner.Logger.LogWarning(string.Format(Localizer.Localize("warning_cant_plant_on_ground"), growable, sim.farm.grid.GroundAt(pos).groundSo.objectName), state);
			return false;
		}
		sim.farm.AssertUnlocked(growable.objectName);
		int num = Mathf.Max(0, sim.farm.NumUnlocked(growable.yieldUpgradeName) - 1);
		if (!sim.farm.Items.Remove(growable.cost * Mathf.Max(1, 1 << num)))
		{
			sim.simRunner.Logger.LogWarning(string.Format(Localizer.Localize("warning_missing_seed"), growable), state);
			return false;
		}
		sim.farm.grid.SetEntity(pos, growable.objectName).OnPlanted(this);
		ResetFlightHeight();
		if (sim.simRunner != null)
		{
			ActionTween();
			sim.simRunner?.PlaySound((growable.objectName == "dynamite") ? SoundEffectType.PlaceDynamite : SoundEffectType.Plant, pos);
			switch (growable.objectName)
			{
			case "bush":
				sim.UnlockAchievement("PLANT_BUSH");
				break;
			case "carrot":
				sim.UnlockAchievement("PLANT_CARROTS");
				break;
			case "tree":
				sim.UnlockAchievement("PLANT_TREE");
				break;
			case "pumpkin":
				sim.UnlockAchievement("PLANT_PUMPKIN");
				break;
			case "sunflower":
				sim.UnlockAchievement("PLANT_SUNFLOWER");
				break;
			case "cactus":
				sim.UnlockAchievement("PLANT_CACTUS");
				break;
			case "bamboo":
				sim.UnlockAchievement("PLANT_BAMBOO");
				break;
			}
			if (growable.objectName == "rice")
			{
				Vector2Int worldSize = sim.farm.grid.WorldSize;
				bool flag = true;
				for (int num2 = 0; num2 < worldSize.y; num2++)
				{
					int num3 = 0;
					while (num3 < worldSize.x)
					{
						if (sim.farm.grid.CellAt(num3, num2).entity is Rice)
						{
							num3++;
							continue;
						}
						goto IL_03c7;
					}
					continue;
					IL_03c7:
					flag = false;
					break;
				}
				if (flag)
				{
					sim.UnlockAchievement("RICE_TERRACE");
				}
			}
		}
		return true;
	}

	public bool Water(int number)
	{
		sim.farm.grid.SetWaterVolume(pos, sim.farm.grid.CellAt(pos).waterVolume + 0.25 * (double)number);
		if (sim.farm.grid.cells.All((GridManager.Cell c) => c.waterVolume >= 0.5))
		{
			sim.UnlockAchievement("MUD_FARM");
		}
		ResetFlightHeight();
		if (sim.simRunner != null && sim.simRunner.TimeFactor == 1.0)
		{
			sim.simRunner.PlayEffect(VFXType.water, GetTransform().GetPosition());
			sim.simRunner?.PlaySound(SoundEffectType.UseWater, pos);
		}
		return true;
	}

	public double GetWater()
	{
		return sim.farm.grid.CellAt(pos).waterVolume;
	}

	public bool Fertilize(int number)
	{
		Growable growable = GrowableUnderDrone();
		if (growable == null || !growable.objectSO.canBeWeird)
		{
			return false;
		}
		growable.Fertilize(number);
		sim.simRunner?.PlaySound(SoundEffectType.UseFertilizer, pos);
		ResetFlightHeight();
		return true;
	}

	public IPyObject ProspectIron(ProgramState state)
	{
		int z = sim.farm.grid.CellAt(pos).depth;
		if (!sim.farm.Items.Remove(DesignConstants.Inst.balancingDesignConstants.prospectIronCost))
		{
			sim.simRunner.Logger.LogWarning(Localizer.Localize("warning_not_enough_coal"), state);
			return PyNone.Instance;
		}
		sim.IncrementAchievementStat("total_prospecting", 1);
		Vector3Int vector3Int = sim.farm.grid.FindClosestOreHamiltonDistance(new Vector3Int(pos.x, pos.y, z), ResourceManager.GetGround("iron"));
		if (vector3Int == new Vector3Int(-1, -1, -1))
		{
			return PyNone.Instance;
		}
		int num = int.MaxValue;
		IPyObject result = PyNone.Instance;
		(int, GridDirection)[] array = new(int, GridDirection)[4]
		{
			(pos.x - vector3Int.x, GridDirection.West),
			(vector3Int.x - pos.x, GridDirection.East),
			(pos.y - vector3Int.y, GridDirection.South),
			(vector3Int.y - pos.y, GridDirection.North)
		};
		for (int i = 0; i < array.Length; i++)
		{
			int item = array[i].Item1;
			if (item > 0 && item < num)
			{
				num = item;
				result = new PyGridDirection(array[i].Item2);
			}
		}
		return result;
	}

	public IPyObject ProspectQuartz(ProgramState state)
	{
		int z = sim.farm.grid.CellAt(pos).depth;
		if (!sim.farm.Items.Remove(DesignConstants.Inst.balancingDesignConstants.prospectQuartzCost))
		{
			sim.simRunner.Logger.LogWarning(Localizer.Localize("warning_not_enough_iron"), state);
			return PyNone.Instance;
		}
		sim.IncrementAchievementStat("total_prospecting", 1);
		Vector3Int vector3Int = sim.farm.grid.FindClosestOreEuclideanDistance(new Vector3Int(pos.x, pos.y, z), ResourceManager.GetGround("quartz"));
		if (!(vector3Int == new Vector3Int(-1, -1, -1)))
		{
			return new PyNumber((vector3Int - new Vector3Int(pos.x, pos.y, z)).magnitude);
		}
		return PyNone.Instance;
	}

	public void ResetPos()
	{
		fleightHeight = 1;
		if (pos != Vector2Int.zero)
		{
			Entity entity = sim.farm.grid.CellAt(pos).entity;
			pos = Vector2Int.zero;
			if (entity is Bamboo bamboo)
			{
				bamboo.OnDroneLeft(DroneId);
			}
			if (sim.farm.grid.CellAt(pos).entity is Bamboo bamboo2)
			{
				bamboo2.CutToHeight(1);
			}
		}
		UpdatePosition(sim.actionOps);
		ChangeHat(Hat.CreateDefaultHat(sim, this), null);
	}

	public Growable GrowableUnderDrone()
	{
		return EntityUnderDrone() as Growable;
	}

	public GroundSO GroundUnderDrone()
	{
		return sim.farm.grid.GroundAt(pos).groundSo;
	}

	public Entity EntityUnderDrone()
	{
		return sim.farm.grid.CellAt(pos).entity;
	}

	private void ResetFlightHeight(bool updatePosition = true)
	{
		int num = ((!(EntityUnderDrone() is Bamboo bamboo)) ? 1 : Mathf.Min(bamboo.Height, fleightHeight));
		if (fleightHeight != num)
		{
			fleightHeight = num;
			if (updatePosition)
			{
				UpdatePosition(sim.actionOps);
			}
		}
	}

	public void TryUpdateHeight(double ops = -1.0)
	{
		if (droneState != DroneState.idle)
		{
			return;
		}
		int num = sim.farm.grid.CellAtOrDefault(pos).depth;
		if (depth != num)
		{
			if (ops < 0.0)
			{
				ops = ((num > depth) ? (sim.actionOps * 7.0) : sim.actionOps);
			}
			UpdatePosition(ops);
		}
	}

	public void UpdateHeight(double ops = -1.0)
	{
		if (ops < 0.0)
		{
			ops = sim.actionOps;
		}
		UpdatePosition(ops);
	}

	private void UpdatePosition(double ops)
	{
		depth = sim.farm.grid.CellAtOrDefault(pos).depth;
		animDuration = sim.GetActionTime(ops);
		startPosition = endPosition;
		endPosition = sim.farm.grid.CellToLocalWithPlants(pos) + new Vector3(0f, 0f, fleightHeight - 1);
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
		animDuration = sim.GetActionTime(sim.actionOps);
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

	public AnimationCurve breakingBlockCurve;

	public float extraPrintWidth;

	public float characterPrintWidth;

	public int charactersAtMaxPrintWidth;
}
public class Farm
{
	private const double FILL_INTERVAL = 10.0;

	private const double USE_POWER_INTERVAL = 0.2;

	public const int MAX_PROSPECT_RANGE = 32;

	public GridManager grid;

	public List<Drone> drones = new List<Drone>();

	public int mainDroneId;

	public Simulation sim;

	public int droneGeneration;

	private readonly ItemBlock _items;

	public EDlcMask installedDlcs;

	public static List<string> startUnlocks = new List<string>
	{
		"grass", "soil", "harvest", "pass", "do_a_flip", "pet_the_piggy", "grassland", "hay", "straw_hat", "tap",
		"stats", "comments"
	};

	private Dictionary<string, int> unlocks = new Dictionary<string, int>();

	public static HashSet<string> allKeyWords = new HashSet<string>
	{
		"def", "while", "for", "if", "else", "elif", "and", "or", "not", "True",
		"False", "None", "Entities", "Grounds", "Items", "Unlocks", "Leaderboards", "Hats", "North", "South",
		"West", "East", "pass", "break", "continue", "return", "global", "import", "from"
	};

	public HashSet<string> unlockedKeyWords = new HashSet<string>();

	public ItemBlock Items => _items;

	public double UsedPower { get; set; }

	public int NumSpeedUpgrades { get; private set; }

	public int NumDiggingSpeedUpgrades { get; private set; }

	public Farm(Simulation sim, EDlcMask dlcs, IEnumerable<string> unlocks, ItemBlock itemBlock, bool resetUnlocks = false, Vector2Int worldSizeOverride = default(Vector2Int), int startingChunk = 0, bool fullyGenerateUnderground = true, List<string> whitelistedLeaderboardFeatures = null, List<int> pretendedFeatureChunks = null, List<int> pretendedChunkDepths = null)
	{
		bool resetUnlocks2 = resetUnlocks;
		base..ctor();
		Farm farm = this;
		this.sim = sim;
		sim.farm = this;
		grid = new GridManager(this, worldSizeOverride, startingChunk, fullyGenerateUnderground, whitelistedLeaderboardFeatures?.Select(ResourceManager.GetGroundFeature).ToList(), pretendedFeatureChunks, pretendedChunkDepths);
		drones.Add(new Drone(sim, Vector2Int.zero, 0));
		installedDlcs = dlcs;
		_items = itemBlock;
		foreach (string startUnlock in startUnlocks)
		{
			Unlock(startUnlock, 1);
		}
		string text = null;
		foreach (string unlock3 in unlocks)
		{
			if (Regex.IsMatch(unlock3, "expand(_[0-9]+)?"))
			{
				text = unlock3;
			}
			else
			{
				applyUnlock(unlock3);
			}
		}
		if (text == null)
		{
			grid.GenerateWorld();
		}
		else
		{
			applyUnlock(text);
		}
		sim.StartTimer(ReceiveWater, Duration.FromSeconds(20.0 / (double)(1 << NumUnlocked("watering"))));
		sim.StartTimer(ReceiveFertilizer, Duration.FromSeconds(20.0 / (double)(1 << NumUnlocked("fertilizer"))));
		sim.StartTimer(UsePower, Duration.FromSeconds(0.2));
		void applyUnlock(string s)
		{
			int num = s.LastIndexOf('_');
			string text2;
			if (num != -1 && int.TryParse(s.Substring(num + 1), out var result) && !s.StartsWith("debug"))
			{
				text2 = s.Substring(0, num);
				if (resetUnlocks2)
				{
					UnlockSO unlock = ResourceManager.GetUnlock(text2);
					if (unlock != null)
					{
						result = (int)Math.Clamp(Math.Log(result + 1, 2.0), 1.0, unlock.maxUnlockLevel);
					}
				}
				Unlock(text2, result);
			}
			else
			{
				text2 = s;
				result = 1;
			}
			if (ResourceManager.GetUnlock(text2) != null)
			{
				UnlockSO unlock2 = ResourceManager.GetUnlock(text2);
				Unlock(text2, result);
				UnlockAllIn(unlock2);
			}
			else
			{
				Unlock(text2, result);
			}
		}
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
		if (sim.simRunner == null)
		{
			return;
		}
		if (sim.RecordsAchievements)
		{
			for (int i = 0; i < items.items.Length; i++)
			{
				if (items.items[i] > 0.0)
				{
					ItemSO item = ResourceManager.GetItem(i);
					if (item != null && (item.trackStats || item.trackTotalStats))
					{
						sim.RecordCollectedItem(item.itemId, items.items[i], collectionDuration, item.trackStats, item.trackTotalStats);
					}
				}
			}
		}
		if (sim.simRunner.TimeFactor == 1.0)
		{
			sim.simRunner.CollectItemEffect(items.ItemIds().First(), localPos);
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

	public void InstallDlc(EDlcType dlc)
	{
		installedDlcs |= PlatformManager.DlcTypeToMask(dlc);
	}

	public void UninstallDlc(EDlcType dlc)
	{
		installedDlcs &= ~PlatformManager.DlcTypeToMask(dlc);
	}

	public bool IsDlcInstalled(EDlcType dlc)
	{
		return PlatformManager.IsDlcInstalled(dlc, installedDlcs);
	}

	public List<string> SerializeUnlocks()
	{
		List<string> list = new List<string>();
		foreach (KeyValuePair<string, int> unlock in unlocks)
		{
			UnlockSO unlockOf = ResourceManager.GetUnlockOf(unlock.Key);
			if (!(unlockOf != null) || !(unlock.Key != unlockOf.unlockName) || !unlocks.ContainsKey(unlockOf.unlockName))
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
		}
		return list;
	}

	public bool IsUnlocked(string s)
	{
		return NumUnlocked(s.ToLower()) > 0;
	}

	public void AssertUnlocked(string dependency, int wordStart = -1, int wordEnd = -1)
	{
		if (!IsUnlocked(dependency))
		{
			UnlockSO unlockSO = ResourceManager.GetUnlockOf(dependency) ?? ResourceManager.GetUnlockOf(dependency.ToLower());
			if (unlockSO != null && !IsDlcInstalled(ResourceManager.GetDlcForKey(unlockSO.unlockName)))
			{
				unlockSO = null;
			}
			if (unlockSO != null)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_missing_x_unlock", unlockSO), wordStart, wordEnd);
			}
			throw new ExecuteException(Localizer.Localize("error_missing_unlock"), wordStart, wordEnd);
		}
	}

	public bool UnlockOrUpgrade(UnlockSO unlockSO, bool requireParent = true)
	{
		if ((requireParent && !string.IsNullOrEmpty(unlockSO.parentUnlock) && !IsUnlocked(unlockSO.parentUnlock)) || NumUnlocked(unlockSO) >= unlockSO.maxUnlockLevel || (unlockSO.additionalUnlockRequirement != null && !string.IsNullOrEmpty(unlockSO.additionalUnlockRequirement.unlockName) && NumUnlocked(unlockSO.additionalUnlockRequirement.unlockName) < unlockSO.additionalUnlockRequirement.level) || (sim.singleDrone && (unlockSO.unlockName == "megafarm" || unlockSO.unlockName == "expand")))
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
		if (NumUnlocked(text) == level)
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
		switch (text)
		{
		case "expand":
			grid.GenerateExpandedWorld();
			sim.UnlockAchievement("EXPAND");
			if (level >= 9)
			{
				sim.UnlockAchievement("BIG_FARM");
			}
			break;
		case "speed":
		{
			double num = MaxSpeedFactor();
			NumSpeedUpgrades = level;
			if (sim.SpeedFactor == num)
			{
				sim.ChangeExecutionSpeed(MaxSpeedFactor());
			}
			break;
		}
		case "mining":
			NumDiggingSpeedUpgrades = level;
			sim.ChangeDiggingSpeed(GetDiggingSpeed());
			break;
		}
	}

	public void UnlockAllIn(UnlockSO unlockSO)
	{
		foreach (string unlock2 in unlockSO.unlocks)
		{
			if (unlock2 == unlockSO.unlockName || (char.IsDigit(unlock2[0]) && int.Parse(unlock2[0].ToString()) > NumUnlocked(unlockSO.unlockName)))
			{
				continue;
			}
			string text = (char.IsDigit(unlock2[0]) ? unlock2.Substring(1) : unlock2);
			bool num = IsUnlocked(text);
			Unlock(text, 1);
			if (!num)
			{
				UnlockSO unlock = ResourceManager.GetUnlock(text);
				if (unlock != null)
				{
					UnlockAllIn(unlock);
				}
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
		Dictionary<string, int> dictionary = new Dictionary<string, int>();
		foreach (KeyValuePair<string, int> unlock in unlocks)
		{
			if (IsDlcInstalled(ResourceManager.GetDlcForKey(unlock.Key)))
			{
				dictionary[unlock.Key] = unlock.Value;
			}
		}
		return dictionary;
	}

	public int NumUnlocked(UnlockSO unlockSO)
	{
		if (!IsDlcInstalled(unlockSO.dlc))
		{
			return 0;
		}
		return unlocks.GetValueOrDefault(unlockSO.unlockName, 0);
	}

	public int NumUnlocked(string unlock)
	{
		if (!IsDlcInstalled(ResourceManager.GetDlcForKey(unlock)))
		{
			return 0;
		}
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

	public double GetDiggingSpeed()
	{
		return Math.Pow(1.5, NumDiggingSpeedUpgrades);
	}

	private void UsePower()
	{
		if (sim.farm.Items.GetNumber(StringIds.PowerItemId) > 0.0)
		{
			if (!sim.farm.Items.Remove(StringIds.PowerItemId, UsedPower))
			{
				sim.farm.Items.SetNumber(StringIds.PowerItemId, 0.0);
			}
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
			Items.AddItem(StringIds.WaterItemId, sim.simRunner.HarvestFactor);
		}
		sim.StartTimer(ReceiveWater, Duration.FromSeconds(20.0 / (double)(1 << NumUnlocked("watering"))));
	}

	private void ReceiveFertilizer()
	{
		if (NumUnlocked("fertilizer") > 0)
		{
			Items.AddItem(StringIds.FertilizerItemId, sim.simRunner.HarvestFactor);
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
				OnRemoveDrone(num);
				drones.RemoveAt(num);
			}
		}
		int num2 = mainDroneId;
		mainDroneId = 0;
		drones[0].DroneId = 0;
		if (num2 == mainDroneId)
		{
			return;
		}
		foreach (GridController gridController in sim.farm.grid.GridControllers)
		{
			gridController.OnDroneChangedId(num2, mainDroneId);
		}
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
		OnRemoveDrone(droneId);
		drones[droneId] = null;
	}

	private void OnRemoveDrone(int droneId)
	{
		Drone drone = drones[droneId];
		if (drone != null)
		{
			drone.hat.OnUnequip();
			if (grid.CellAt(drone.pos).entity is Bamboo bamboo)
			{
				bamboo.OnDroneLeft(droneId);
			}
		}
		foreach (GridController gridController in sim.farm.grid.GridControllers)
		{
			gridController.OnDroneRemoved(droneId);
		}
	}
}
public class FarmRenderer : MonoBehaviour
{
	private struct FaceVisual
	{
		public Color firstColor;

		public Color secondColor;

		public Color thirdColor;

		public Color fourthColor;

		public bool flipQuad;

		public bool SameAs(FaceVisual other)
		{
			if (firstColor == other.firstColor && secondColor == other.secondColor && thirdColor == other.thirdColor && fourthColor == other.fourthColor)
			{
				return flipQuad == other.flipQuad;
			}
			return false;
		}
	}

	public enum FaceDirection
	{
		North,
		South,
		East,
		West,
		Top
	}

	private MaterialPropertyBlock fogMpb;

	private Dictionary<Mesh, List<Matrix4x4>> farmMeshes = new Dictionary<Mesh, List<Matrix4x4>>();

	private Dictionary<Mesh, List<Matrix4x4>> decorationMeshes = new Dictionary<Mesh, List<Matrix4x4>>();

	private Dictionary<Mesh, List<(Vector3Int blockPos, FaceDirection faceDirection)>> decorationKeys = new Dictionary<Mesh, List<(Vector3Int, FaceDirection)>>();

	private Dictionary<(Vector3Int, FaceDirection), (Mesh, int)> decorationIndices = new Dictionary<(Vector3Int, FaceDirection), (Mesh, int)>();

	private List<(Vector3Int blockPos, FaceDirection faceDirection)> decorationRemovalBuffer = new List<(Vector3Int, FaceDirection)>();

	private List<Matrix4x4> decorationRenderBuffer = new List<Matrix4x4>();

	private Dictionary<Mesh, List<Matrix4x4>> droneMeshes = new Dictionary<Mesh, List<Matrix4x4>>();

	private Dictionary<(Mesh mesh, Material material, int subMeshIndex), List<Matrix4x4>> customHatMeshes = new Dictionary<(Mesh, Material, int), List<Matrix4x4>>();

	private List<Matrix4x4> drillMeshes = new List<Matrix4x4>();

	private Dictionary<Mesh, List<Matrix4x4>> goldenHatMeshes = new Dictionary<Mesh, List<Matrix4x4>>();

	private List<Matrix4x4> propellerMeshes = new List<Matrix4x4>();

	private ISimRunner simRunner;

	private Mesh chunkMesh;

	private readonly List<Vector3> chunkMeshVertices = new List<Vector3>();

	private readonly List<Vector3> chunkMeshNormals = new List<Vector3>();

	private readonly List<int> chunkMeshTriangles = new List<int>();

	private readonly List<Color> chunkMeshColors = new List<Color>();

	private BitSet suppressedBlocks;

	private Vector2Int suppressionGridSize;

	private bool blockSuppressionDirty;

	private RenderPackage prevRenderPackage;

	[NonSerialized]
	public Matrix4x4 sceneTransform;

	private float renderHeightOffset;

	private float[] drillSizes = new float[32];

	private Camera farmCamera;

	private const float BaseShadowDistance = 13f;

	private const float BaseFogDepth = 1f;

	private float shadowDistance;

	private bool hasShadowDistance;

	private UniversalRenderPipelineAsset overriddenPipelineAsset;

	private float previousShadowDistance;

	private void Awake()
	{
		simRunner = GetComponent<ISimRunner>();
		if (simRunner == null)
		{
			UnityEngine.Debug.LogError("FarmRenderer requires a component that implements ISimRunner.");
		}
		fogMpb = new MaterialPropertyBlock();
		farmCamera = GetComponentInChildren<Camera>();
	}

	private void OnEnable()
	{
		RenderPipelineManager.beginCameraRendering += BeginCameraRendering;
		RenderPipelineManager.endCameraRendering += EndCameraRendering;
	}

	private void OnDisable()
	{
		RenderPipelineManager.beginCameraRendering -= BeginCameraRendering;
		RenderPipelineManager.endCameraRendering -= EndCameraRendering;
		RestoreShadowDistance();
	}

	private void Update()
	{
		RenderPackage renderPackage = simRunner.GetRenderPackage();
		if ((object)renderPackage == null)
		{
			return;
		}
		EnsureSuppressionGrid(renderPackage.groundData.sizexy);
		if ((object)renderPackage != prevRenderPackage)
		{
			foreach (SlidingBlockCall slidingBlock in renderPackage.slidingBlocks)
			{
				if (slidingBlock.sourcePos != slidingBlock.targetPos && DesignConstants.Inst.vfx.blockSlideEffectDuration > 0f && !slidingBlock.popEffect)
				{
					SuppressBlock(slidingBlock.targetPos);
				}
			}
		}
		Transform sceneScaler = simRunner.SceneScaler;
		DesignConstants.FarmRendererDesignConstants farmRenderer = DesignConstants.Inst.farmRenderer;
		float num = farmRenderer.FarmDepthOffset(renderPackage.groundData.sizexy, renderPackage.averageDepth, renderPackage.maxDepth);
		float num2 = Mathf.Pow(Mathf.Abs(num - renderHeightOffset), farmRenderer.cameraFollowSpeedPower) * farmRenderer.cameraFollowSpeedFactor;
		renderHeightOffset = Mathf.MoveTowards(renderHeightOffset, num, num2 * Time.deltaTime);
		float num3 = Mathf.Max(0f, farmRenderer.cameraFollowMaxDistance);
		renderHeightOffset = Mathf.Clamp(renderHeightOffset, num - num3, num + num3);
		sceneScaler.localPosition = new Vector3(sceneScaler.localPosition.x, sceneScaler.localPosition.y, renderHeightOffset * sceneScaler.localScale.z);
		sceneTransform = sceneScaler.localToWorldMatrix;
		bool num4 = simRunner.InstalledDlcs.HasFlag(EDlcMask.Minig);
		float num5 = (num4 ? farmRenderer.EffectiveFogHeight(renderPackage.groundData.sizexy) : (-0.5f));
		float z = sceneTransform.MultiplyPoint(new Vector3(0f, 0f, num5 - renderHeightOffset)).z;
		fogMpb.SetFloat("_MinZ", z);
		float num6 = (num4 ? farmRenderer.EffectiveFogFade(renderPackage.groundData.sizexy) : 2f);
		fogMpb.SetFloat("_MinFadeDistance", num6 * sceneScaler.localScale.z);
		fogMpb.SetColor("_MinFogColor", farmRenderer.FogColor);
		fogMpb.SetFloat("_MaxZ", farmRenderer.maxFarmRenderHeight);
		fogMpb.SetFloat("_FadeDistance", farmRenderer.maxRenderFadeDistance);
		UpdateShadowDistance(renderPackage, num5, num6, sceneScaler.localScale.z);
		foreach (Mesh key3 in farmMeshes.Keys)
		{
			farmMeshes[key3].Clear();
		}
		foreach (Mesh key4 in droneMeshes.Keys)
		{
			droneMeshes[key4].Clear();
		}
		foreach (Mesh key5 in goldenHatMeshes.Keys)
		{
			goldenHatMeshes[key5].Clear();
		}
		foreach (var key6 in customHatMeshes.Keys)
		{
			customHatMeshes[key6].Clear();
		}
		drillMeshes.Clear();
		propellerMeshes.Clear();
		if (!droneMeshes.ContainsKey(farmRenderer.droneMesh))
		{
			droneMeshes[farmRenderer.droneMesh] = new List<Matrix4x4>();
		}
		for (int i = 0; i < renderPackage.droneMeshes.Count; i++)
		{
			(HatSO hat, bool highlight, Matrix4x4 transform, float diggingTimeRemaining) tuple = renderPackage.droneMeshes[i];
			HatSO item = tuple.hat;
			bool item2 = tuple.highlight;
			Matrix4x4 item3 = tuple.transform;
			float item4 = tuple.diggingTimeRemaining;
			Matrix4x4 matrix4x = sceneTransform * item3;
			if (!IsMatrixValid(matrix4x))
			{
				continue;
			}
			Quaternion q = Quaternion.Euler(0f, 180f, 0f);
			droneMeshes[farmRenderer.droneMesh].Add(matrix4x);
			if (item4 > 0f)
			{
				drillSizes[i] = 1f;
			}
			else
			{
				drillSizes[i] -= farmRenderer.drillShrinkSpeed * Time.deltaTime;
			}
			if (drillSizes[i] > 0f)
			{
				float num7 = Mathf.Clamp(drillSizes[i], 0f, 1f);
				Matrix4x4 item5 = matrix4x * Matrix4x4.Scale(new Vector3(num7, num7, num7));
				drillMeshes.Add(item5);
			}
			Material[] subMeshMaterials = item.subMeshMaterials;
			if (subMeshMaterials != null && subMeshMaterials.Length > 0)
			{
				Material material = (item.isGolden ? farmRenderer.goldenHatMaterial : farmRenderer.unclampedPaletteMaterial);
				for (int j = 0; j < item.hatMesh.subMeshCount; j++)
				{
					Material material2 = ((j < item.subMeshMaterials.Length) ? item.subMeshMaterials[j] : null);
					if ((object)material2 == null)
					{
						material2 = material;
					}
					(Mesh, Material, int) key = (item.hatMesh, material2, j);
					if (!customHatMeshes.ContainsKey(key))
					{
						customHatMeshes[key] = new List<Matrix4x4>();
					}
					customHatMeshes[key].Add(matrix4x);
				}
			}
			else if (item.isGolden)
			{
				if (!goldenHatMeshes.ContainsKey(item.hatMesh))
				{
					goldenHatMeshes[item.hatMesh] = new List<Matrix4x4>();
				}
				goldenHatMeshes[item.hatMesh].Add(matrix4x);
			}
			else
			{
				if (!droneMeshes.ContainsKey(item.hatMesh))
				{
					droneMeshes[item.hatMesh] = new List<Matrix4x4>();
				}
				droneMeshes[item.hatMesh].Add(matrix4x);
			}
			if (item2)
			{
				droneMeshes[farmRenderer.droneHighlightArrowMesh] = new List<Matrix4x4> { matrix4x };
			}
			Matrix4x4 item6 = matrix4x * Matrix4x4.Translate(farmRenderer.propellerOffset1) * Matrix4x4.Rotate(q);
			propellerMeshes.Add(item6);
			Matrix4x4 item7 = matrix4x * Matrix4x4.Translate(farmRenderer.propellerOffset2);
			propellerMeshes.Add(item7);
			Matrix4x4 item8 = matrix4x * Matrix4x4.Translate(farmRenderer.propellerOffset3) * Matrix4x4.Rotate(q);
			propellerMeshes.Add(item8);
			Matrix4x4 item9 = matrix4x * Matrix4x4.Translate(farmRenderer.propellerOffset4);
			propellerMeshes.Add(item9);
		}
		foreach (var farmMesh in renderPackage.farmMeshes)
		{
			Mesh item10 = farmMesh.mesh;
			Matrix4x4 item11 = farmMesh.transform;
			Matrix4x4 item12 = sceneTransform * item11;
			if (!(item12.GetPosition().z > farmRenderer.maxFarmRenderHeight))
			{
				if (!farmMeshes.ContainsKey(item10))
				{
					farmMeshes[item10] = new List<Matrix4x4>();
				}
				farmMeshes[item10].Add(item12);
			}
		}
		UpdateDecorationMeshes(renderPackage, renderPackage.cellWaterVolumes);
		UpdateChunkMesh(renderPackage);
		blockSuppressionDirty = false;
		ShadowCastingMode shadowCastingMode = ShadowCastingMode.On;
		int renderLayer = simRunner.RenderLayer;
		RenderParams renderParams = new RenderParams(farmRenderer.paletteMaterial);
		renderParams.matProps = fogMpb;
		renderParams.shadowCastingMode = shadowCastingMode;
		renderParams.receiveShadows = true;
		renderParams.layer = renderLayer;
		RenderParams renderParams2 = renderParams;
		if (farmRenderer.renderFarm)
		{
			foreach (Mesh key7 in farmMeshes.Keys)
			{
				RenderInstanced(key7, farmMeshes[key7], in renderParams2);
			}
		}
		if (farmRenderer.renderDecorations)
		{
			foreach (Mesh key8 in decorationMeshes.Keys)
			{
				RenderDecorationsInstanced(key8, decorationMeshes[key8], sceneTransform, in renderParams2);
			}
		}
		if (farmRenderer.renderDrones)
		{
			renderParams = new RenderParams(farmRenderer.unclampedPaletteMaterial);
			renderParams.shadowCastingMode = shadowCastingMode;
			renderParams.receiveShadows = true;
			renderParams.layer = renderLayer;
			RenderParams renderParams3 = renderParams;
			renderParams = new RenderParams(farmRenderer.goldenHatMaterial);
			renderParams.shadowCastingMode = shadowCastingMode;
			renderParams.receiveShadows = true;
			renderParams.layer = renderLayer;
			RenderParams renderParams4 = renderParams;
			renderParams = new RenderParams(farmRenderer.propellerMaterial);
			renderParams.shadowCastingMode = shadowCastingMode;
			renderParams.receiveShadows = true;
			renderParams.layer = renderLayer;
			RenderParams renderParams5 = renderParams;
			renderParams = new RenderParams(farmRenderer.drillMaterial);
			renderParams.shadowCastingMode = shadowCastingMode;
			renderParams.receiveShadows = true;
			renderParams.layer = renderLayer;
			RenderParams renderParams6 = renderParams;
			foreach (Mesh key9 in droneMeshes.Keys)
			{
				RenderInstanced(key9, droneMeshes[key9], in renderParams3);
			}
			RenderInstanced(farmRenderer.drillMesh, drillMeshes, in renderParams6);
			foreach (Mesh key10 in goldenHatMeshes.Keys)
			{
				RenderInstanced(key10, goldenHatMeshes[key10], in renderParams4);
			}
			foreach (KeyValuePair<(Mesh, Material, int), List<Matrix4x4>> customHatMesh in customHatMeshes)
			{
				customHatMesh.Deconstruct(out var key2, out var value);
				(Mesh, Material, int) tuple2 = key2;
				List<Matrix4x4> instanceData = value;
				renderParams = new RenderParams(tuple2.Item2);
				renderParams.shadowCastingMode = shadowCastingMode;
				renderParams.receiveShadows = true;
				renderParams.layer = renderLayer;
				RenderParams renderParams7 = renderParams;
				RenderInstanced(tuple2.Item1, instanceData, in renderParams7, tuple2.Item3);
			}
			RenderInstanced(DesignConstants.Inst.farmRenderer.propellerMesh, propellerMeshes, in renderParams5);
		}
		if (farmRenderer.renderChunks && chunkMesh != null)
		{
			Graphics.DrawMesh(chunkMesh, sceneTransform, farmRenderer.vertexColorLitMaterial, renderLayer, null, 0, fogMpb);
		}
		if (farmRenderer.renderHover && simRunner is MainSim && MainSim.Inst.hoveredBlock != new Vector3Int(-1, -1, -1))
		{
			Graphics.DrawMesh(farmRenderer.hoverMesh, sceneTransform * Matrix4x4.Translate(new Vector3(-MainSim.Inst.hoveredBlock.x, MainSim.Inst.hoveredBlock.y, -MainSim.Inst.hoveredBlock.z)), farmRenderer.paletteMaterial, simRunner.RenderLayer, null, 0, fogMpb);
		}
		prevRenderPackage = renderPackage;
	}

	public void SuppressBlock(Vector2Int blockPos)
	{
		if (TryGetSuppressionIndex(blockPos, out var index) && !suppressedBlocks[index])
		{
			suppressedBlocks[index] = true;
			blockSuppressionDirty = true;
		}
	}

	public void ReleaseBlockSuppression(Vector2Int blockPos)
	{
		if (TryGetSuppressionIndex(blockPos, out var index) && suppressedBlocks[index])
		{
			suppressedBlocks[index] = false;
			blockSuppressionDirty = true;
		}
	}

	public bool IsBlockSuppressed(Vector2Int blockPos)
	{
		if (TryGetSuppressionIndex(blockPos, out var index))
		{
			return suppressedBlocks[index];
		}
		return false;
	}

	private void EnsureSuppressionGrid(Vector2Int gridSize)
	{
		int num = gridSize.x * gridSize.y;
		if (suppressedBlocks == null || !(suppressionGridSize == gridSize) || suppressedBlocks.Length != num)
		{
			suppressionGridSize = gridSize;
			suppressedBlocks = new BitSet(num);
			blockSuppressionDirty = true;
		}
	}

	private bool TryGetSuppressionIndex(Vector2Int blockPos, out int index)
	{
		if (suppressedBlocks == null)
		{
			RenderPackage renderPackage = simRunner?.GetRenderPackage();
			if (renderPackage?.groundData != null)
			{
				EnsureSuppressionGrid(renderPackage.groundData.sizexy);
			}
		}
		if (suppressedBlocks == null || blockPos.x < 0 || blockPos.x >= suppressionGridSize.x || blockPos.y < 0 || blockPos.y >= suppressionGridSize.y)
		{
			index = -1;
			return false;
		}
		index = blockPos.x + suppressionGridSize.x * blockPos.y;
		return true;
	}

	private void RenderInstanced(Mesh mesh, List<Matrix4x4> instanceData, in RenderParams renderParams, int subMeshIndex = 0)
	{
		for (int i = 0; i < instanceData.Count; i += 1023)
		{
			int instanceCount = Mathf.Min(1023, instanceData.Count - i);
			Graphics.RenderMeshInstanced(in renderParams, mesh, subMeshIndex, instanceData, instanceCount, i);
		}
	}

	private void RenderDecorationsInstanced(Mesh mesh, List<Matrix4x4> localTransforms, Matrix4x4 sceneTransform, in RenderParams renderParams)
	{
		decorationRenderBuffer.Clear();
		for (int i = 0; i < localTransforms.Count; i++)
		{
			decorationRenderBuffer.Add(sceneTransform * localTransforms[i]);
		}
		RenderInstanced(mesh, decorationRenderBuffer, in renderParams);
	}

	private bool FarmCoversMoreThanHalfScreen(RenderPackage renderPackage)
	{
		if ((object)farmCamera == null || renderPackage.groundData == null)
		{
			return false;
		}
		Vector2Int farmSize = renderPackage.groundData.sizexy;
		if (farmSize.x <= 0 || farmSize.y <= 0)
		{
			return false;
		}
		float minViewportX = float.PositiveInfinity;
		float maxViewportX = float.NegativeInfinity;
		float minViewportY = float.PositiveInfinity;
		float maxViewportY = float.NegativeInfinity;
		bool allCornersInFront = true;
		EncapsulateCorner(0, 0, 0.5f, -0.5f);
		EncapsulateCorner(farmSize.x - 1, 0, (float)(-farmSize.x) + 0.5f, -0.5f);
		EncapsulateCorner(0, farmSize.y - 1, 0.5f, (float)farmSize.y - 0.5f);
		EncapsulateCorner(farmSize.x - 1, farmSize.y - 1, (float)(-farmSize.x) + 0.5f, (float)farmSize.y - 0.5f);
		if (!allCornersInFront)
		{
			return true;
		}
		float num = Mathf.Clamp01(maxViewportX) - Mathf.Clamp01(minViewportX);
		float num2 = Mathf.Clamp01(maxViewportY) - Mathf.Clamp01(minViewportY);
		return num * num2 > 0.5f;
		void EncapsulateCorner(int cellX, int cellY, float x, float y)
		{
			int num3 = cellX + cellY * farmSize.x;
			float num4 = ((renderPackage.cellDepths != null && num3 < renderPackage.cellDepths.Length) ? ((float)renderPackage.cellDepths[num3]) : renderPackage.averageDepth);
			Vector3 position = sceneTransform.MultiplyPoint(new Vector3(x, y, 0f - num4));
			Vector3 vector = farmCamera.WorldToViewportPoint(position);
			if (vector.z <= 0f)
			{
				allCornersInFront = false;
			}
			else
			{
				minViewportX = Mathf.Min(minViewportX, vector.x);
				maxViewportX = Mathf.Max(maxViewportX, vector.x);
				minViewportY = Mathf.Min(minViewportY, vector.y);
				maxViewportY = Mathf.Max(maxViewportY, vector.y);
			}
		}
	}

	private void UpdateShadowDistance(RenderPackage renderPackage, float fogHeight, float fogFade, float sceneScale)
	{
		float num = fogFade - fogHeight;
		float num2 = (float)renderPackage.maxDepth - Mathf.Round(renderHeightOffset) + 2f;
		float num3 = (FarmCoversMoreThanHalfScreen(renderPackage) ? num2 : num);
		float num4 = Mathf.Max(0f, num3 - 1f) * Mathf.Abs(sceneScale);
		shadowDistance = 13f + num4;
		hasShadowDistance = true;
	}

	private void BeginCameraRendering(ScriptableRenderContext context, Camera camera)
	{
		if (!(camera != farmCamera) && hasShadowDistance && GraphicsSettings.currentRenderPipeline is UniversalRenderPipelineAsset universalRenderPipelineAsset)
		{
			overriddenPipelineAsset = universalRenderPipelineAsset;
			previousShadowDistance = universalRenderPipelineAsset.shadowDistance;
			universalRenderPipelineAsset.shadowDistance = shadowDistance;
		}
	}

	private void EndCameraRendering(ScriptableRenderContext context, Camera camera)
	{
		if (camera == farmCamera)
		{
			RestoreShadowDistance();
		}
	}

	private void RestoreShadowDistance()
	{
		if ((object)overriddenPipelineAsset != null)
		{
			overriddenPipelineAsset.shadowDistance = previousShadowDistance;
			overriddenPipelineAsset = null;
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

	private void UpdateDecorationMeshes(RenderPackage renderPackage, double[] cellWaterVolumes)
	{
		if (ShouldRebuildAllDecorations(renderPackage))
		{
			ClearDecorationMeshes();
			AddDecorationMeshes(renderPackage, cellWaterVolumes);
			return;
		}
		GroundData groundData = renderPackage.groundData;
		int x = groundData.sizexy.x;
		int y = groundData.sizexy.y;
		BitSet positionsDirty = groundData.positionsDirty;
		if (!positionsDirty.HasAnySet())
		{
			return;
		}
		BitSet bitSet = new BitSet(x * y);
		for (int i = 0; i < positionsDirty.Count; i++)
		{
			if (positionsDirty[i])
			{
				int num = i % x;
				int num2 = i / x;
				AddDirtyCell(bitSet, num, num2, x, y);
				AddDirtyCell(bitSet, num - 1, num2, x, y);
				AddDirtyCell(bitSet, num + 1, num2, x, y);
				AddDirtyCell(bitSet, num, num2 - 1, x, y);
				AddDirtyCell(bitSet, num, num2 + 1, x, y);
			}
		}
		RemoveDecorationMeshesForCells(bitSet, x);
		for (int j = 0; j < bitSet.Count; j++)
		{
			if (bitSet[j])
			{
				AddDecorationMeshesForCell(renderPackage, cellWaterVolumes, j % x, j / x);
			}
		}
	}

	private bool ShouldRebuildAllDecorations(RenderPackage renderPackage)
	{
		if ((object)prevRenderPackage != null && !blockSuppressionDirty && !renderPackage.rebuildMeshes && renderPackage.groundData != null && prevRenderPackage.groundData != null && !(renderPackage.groundData.sizexy != prevRenderPackage.groundData.sizexy) && renderPackage.groundData.positionsDirty != null && renderPackage.groundData.positionsDirty.Length == renderPackage.groundData.sizexy.x * renderPackage.groundData.sizexy.y && renderPackage.cellDepths != null && prevRenderPackage.cellDepths != null)
		{
			return renderPackage.cellDepths.Length != prevRenderPackage.cellDepths.Length;
		}
		return true;
	}

	private void AddDirtyCell(BitSet dirtyCells, int x, int y, int sizex, int sizey)
	{
		if (x >= 0 && x < sizex && y >= 0 && y < sizey)
		{
			dirtyCells.Set(x + y * sizex, value: true);
		}
	}

	private void ClearDecorationMeshes()
	{
		foreach (Mesh key in decorationMeshes.Keys)
		{
			decorationMeshes[key].Clear();
		}
		foreach (Mesh key2 in decorationKeys.Keys)
		{
			decorationKeys[key2].Clear();
		}
		decorationIndices.Clear();
	}

	private void RemoveDecorationMeshesForCells(BitSet dirtyCells, int sizex)
	{
		decorationRemovalBuffer.Clear();
		foreach (var key in decorationIndices.Keys)
		{
			Vector3Int item = key.Item1;
			FaceDirection item2 = key.Item2;
			int index = item.x + sizex * item.y;
			if (dirtyCells[index])
			{
				decorationRemovalBuffer.Add((item, item2));
			}
		}
		foreach (var (item3, item4) in decorationRemovalBuffer)
		{
			RemoveDecorationMesh((blockPos: item3, faceDirection: item4));
		}
	}

	private void RemoveDecorationMesh((Vector3Int blockPos, FaceDirection faceDirection) key)
	{
		if (decorationIndices.TryGetValue(key, out var value))
		{
			List<Matrix4x4> list = decorationMeshes[value.Item1];
			List<(Vector3Int, FaceDirection)> list2 = decorationKeys[value.Item1];
			int num = list.Count - 1;
			if (value.Item2 != num)
			{
				list[value.Item2] = list[num];
				list2[value.Item2] = list2[num];
				decorationIndices[list2[value.Item2]] = (value.Item1, value.Item2);
			}
			list.RemoveAt(num);
			list2.RemoveAt(num);
			decorationIndices.Remove(key);
		}
	}

	private void AddDecorationMeshes(RenderPackage renderPackage, double[] cellWaterVolumes)
	{
		GroundData groundData = renderPackage.groundData;
		int x = groundData.sizexy.x;
		int y = groundData.sizexy.y;
		for (int i = 0; i < x * y; i++)
		{
			int x2 = i % x;
			int y2 = i / x % y;
			AddDecorationMeshesForCell(renderPackage, cellWaterVolumes, x2, y2);
		}
	}

	private void AddDecorationMeshesForCell(RenderPackage renderPackage, double[] cellWaterVolumes, int x, int y)
	{
		GroundData groundData = renderPackage.groundData;
		int x2 = groundData.sizexy.x;
		int y2 = groundData.sizexy.y;
		int num = (groundData.startChunkIndex + groundData.chunks.Count) * 16;
		int num2 = x + y * x2;
		int renderDepth = GetRenderDepth(renderPackage, x, y, num);
		if (renderDepth >= num)
		{
			return;
		}
		double waterVolume = cellWaterVolumes[num2];
		AddDecorationMesh(groundData, x, y, renderDepth, x2, y2, FaceDirection.Top, waterVolume);
		int num3 = ((x > 0) ? GetRenderDepth(renderPackage, x - 1, y, num) : num) - renderDepth;
		if (num3 > 0)
		{
			for (int i = 0; i < num3; i++)
			{
				AddDecorationMesh(groundData, x, y, renderDepth + i, x2, y2, FaceDirection.West);
			}
		}
		int num4 = ((x < x2 - 1) ? GetRenderDepth(renderPackage, x + 1, y, num) : num) - renderDepth;
		if (num4 > 0)
		{
			for (int j = 0; j < num4; j++)
			{
				AddDecorationMesh(groundData, x, y, renderDepth + j, x2, y2, FaceDirection.East);
			}
		}
		int num5 = ((y > 0) ? GetRenderDepth(renderPackage, x, y - 1, num) : num) - renderDepth;
		if (num5 > 0)
		{
			for (int k = 0; k < num5; k++)
			{
				AddDecorationMesh(groundData, x, y, renderDepth + k, x2, y2, FaceDirection.South);
			}
		}
		int num6 = ((y < y2 - 1) ? GetRenderDepth(renderPackage, x, y + 1, num) : num) - renderDepth;
		if (num6 > 0)
		{
			for (int l = 0; l < num6; l++)
			{
				AddDecorationMesh(groundData, x, y, renderDepth + l, x2, y2, FaceDirection.North);
			}
		}
	}

	private void AddDecorationMesh(GroundData groundData, int x, int y, int depth, int sizex, int sizey, FaceDirection faceDirection, double waterVolume = 0.0)
	{
		Vector3Int vector3Int = new Vector3Int(x, y, depth);
		float rotation;
		Mesh mesh = groundData.GroundAt(x, y, depth).groundSo.SampleDecoration(vector3Int.x, vector3Int.y, vector3Int.z, faceDirection, out rotation, waterVolume);
		if (mesh != null)
		{
			if (!decorationMeshes.ContainsKey(mesh))
			{
				decorationMeshes[mesh] = new List<Matrix4x4>();
			}
			if (!decorationKeys.ContainsKey(mesh))
			{
				decorationKeys[mesh] = new List<(Vector3Int, FaceDirection)>();
			}
			Quaternion decorationRotation = GetDecorationRotation(faceDirection, rotation);
			decorationMeshes[mesh].Add(Matrix4x4.TRS(GridManager.CellToLocal(vector3Int) - new Vector3(0f, 0f, 0.5f), decorationRotation, Vector3.one));
			decorationKeys[mesh].Add((vector3Int, faceDirection));
			decorationIndices[(vector3Int, faceDirection)] = (mesh, decorationMeshes[mesh].Count - 1);
		}
	}

	public static Quaternion GetDecorationRotation(FaceDirection faceDirection, float extraRotation)
	{
		return faceDirection switch
		{
			FaceDirection.North => Quaternion.Euler(-90f, 0f, extraRotation + 180f), 
			FaceDirection.South => Quaternion.Euler(90f, 0f, extraRotation), 
			FaceDirection.East => Quaternion.Euler(0f, -90f, extraRotation - 90f), 
			FaceDirection.West => Quaternion.Euler(0f, 90f, extraRotation + 90f), 
			FaceDirection.Top => Quaternion.Euler(0f, 0f, extraRotation), 
			_ => Quaternion.identity, 
		};
	}

	private void UpdateChunkMesh(RenderPackage renderPackage)
	{
		if (ShouldRebuildChunkMesh(renderPackage))
		{
			if (chunkMesh != null)
			{
				UnityEngine.Object.Destroy(chunkMesh);
			}
			chunkMesh = GenerateChunkMesh(renderPackage);
		}
	}

	private bool ShouldRebuildChunkMesh(RenderPackage renderPackage)
	{
		if ((object)prevRenderPackage != null && !renderPackage.rebuildMeshes && !blockSuppressionDirty && prevRenderPackage.groundData != null && !renderPackage.groundData.positionsDirty.HasAnySet() && !(renderPackage.groundData.sizexy != prevRenderPackage.groundData.sizexy) && renderPackage.cellDepths != null && prevRenderPackage.cellDepths != null && renderPackage.cellDepths.Length == prevRenderPackage.cellDepths.Length)
		{
			return DidHeightMapChange(renderPackage.cellDepths, prevRenderPackage.cellDepths);
		}
		return true;
	}

	private bool DidHeightMapChange(int[] newDepths, int[] previousDepths)
	{
		for (int i = 0; i < newDepths.Length; i++)
		{
			if (newDepths[i] != previousDepths[i])
			{
				return true;
			}
		}
		return false;
	}

	private Mesh GenerateChunkMesh(RenderPackage renderPackage)
	{
		float minimumAmbientOcclusionBrightness = DesignConstants.Inst.farmRenderer.minimumAmbientOcclusionBrightness;
		GroundData groundData = renderPackage.groundData;
		Mesh mesh = new Mesh();
		chunkMeshVertices.Clear();
		chunkMeshNormals.Clear();
		chunkMeshTriangles.Clear();
		chunkMeshColors.Clear();
		if (groundData == null || renderPackage.cellDepths == null)
		{
			return mesh;
		}
		int sizex = groundData.sizexy.x;
		int sizey = groundData.sizexy.y;
		int maxChunkDepth = (groundData.startChunkIndex + groundData.chunks.Count) * 16;
		for (int i = 0; i < sizex * sizey; i++)
		{
			int num = i % sizex;
			int num2 = i / sizex % sizey;
			int renderDepth = GetRenderDepth(renderPackage, num, num2, maxChunkDepth);
			Vector3Int vector3Int = new Vector3Int(num, num2, renderDepth);
			if (IsBlockPresent(vector3Int))
			{
				AddFace(vector3Int, FaceDirection.Top, 1, GetFaceVisual(vector3Int, FaceDirection.Top));
			}
			int depthDifference = ((num > 0) ? GetRenderDepth(renderPackage, num - 1, num2, maxChunkDepth) : maxChunkDepth) - renderDepth;
			AddSideFaces(num, num2, renderDepth, depthDifference, FaceDirection.West);
			int depthDifference2 = ((num < sizex - 1) ? GetRenderDepth(renderPackage, num + 1, num2, maxChunkDepth) : maxChunkDepth) - renderDepth;
			AddSideFaces(num, num2, renderDepth, depthDifference2, FaceDirection.East);
			int depthDifference3 = ((num2 > 0) ? GetRenderDepth(renderPackage, num, num2 - 1, maxChunkDepth) : maxChunkDepth) - renderDepth;
			AddSideFaces(num, num2, renderDepth, depthDifference3, FaceDirection.South);
			int depthDifference4 = ((num2 < sizey - 1) ? GetRenderDepth(renderPackage, num, num2 + 1, maxChunkDepth) : maxChunkDepth) - renderDepth;
			AddSideFaces(num, num2, renderDepth, depthDifference4, FaceDirection.North);
		}
		mesh.indexFormat = IndexFormat.UInt32;
		mesh.SetVertices(chunkMeshVertices);
		mesh.SetNormals(chunkMeshNormals);
		mesh.SetTriangles(chunkMeshTriangles, 0);
		mesh.SetColors(chunkMeshColors);
		return mesh;
		void AddFace(Vector3Int blockPos, FaceDirection faceDirection, int depthLength, FaceVisual visual)
		{
			int count = chunkMeshVertices.Count;
			Vector3 item = Vector3.forward;
			switch (faceDirection)
			{
			case FaceDirection.North:
				item = Vector3.up;
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, 0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, 0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, 0.5f, depthLength)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, 0.5f, depthLength)));
				break;
			case FaceDirection.South:
				item = Vector3.down;
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, -0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, -0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, -0.5f, depthLength)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, -0.5f, depthLength)));
				break;
			case FaceDirection.East:
				item = Vector3.left;
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, -0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, 0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, 0.5f, depthLength)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, -0.5f, depthLength)));
				break;
			case FaceDirection.West:
				item = Vector3.right;
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, 0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, -0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, -0.5f, depthLength)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, 0.5f, depthLength)));
				break;
			case FaceDirection.Top:
				item = Vector3.forward;
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, 0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, 0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(0.5f, -0.5f, 0f)));
				chunkMeshVertices.Add(GridManager.CellToLocal(blockPos + new Vector3(-0.5f, -0.5f, 0f)));
				break;
			}
			chunkMeshNormals.Add(item);
			chunkMeshNormals.Add(item);
			chunkMeshNormals.Add(item);
			chunkMeshNormals.Add(item);
			chunkMeshColors.Add(visual.firstColor);
			chunkMeshColors.Add(visual.secondColor);
			chunkMeshColors.Add(visual.thirdColor);
			chunkMeshColors.Add(visual.fourthColor);
			if (visual.flipQuad)
			{
				chunkMeshTriangles.Add(count);
				chunkMeshTriangles.Add(count + 1);
				chunkMeshTriangles.Add(count + 3);
				chunkMeshTriangles.Add(count + 1);
				chunkMeshTriangles.Add(count + 2);
				chunkMeshTriangles.Add(count + 3);
			}
			else
			{
				chunkMeshTriangles.Add(count);
				chunkMeshTriangles.Add(count + 1);
				chunkMeshTriangles.Add(count + 2);
				chunkMeshTriangles.Add(count);
				chunkMeshTriangles.Add(count + 2);
				chunkMeshTriangles.Add(count + 3);
			}
		}
		void AddSideFaces(int x, int y, int startDepth, int num3, FaceDirection faceDirection)
		{
			bool hasActiveSpan;
			int faceSpanStartDepth;
			int faceSpanLength;
			FaceVisual spanVisual;
			if (num3 > 0)
			{
				hasActiveSpan = false;
				faceSpanStartDepth = startDepth;
				faceSpanLength = 0;
				spanVisual = default(FaceVisual);
				for (int j = 0; j < num3; j++)
				{
					Vector3Int vector3Int2 = new Vector3Int(x, y, startDepth + j);
					if (!IsBlockPresent(vector3Int2))
					{
						FlushFace();
					}
					else
					{
						FaceVisual faceVisual = GetFaceVisual(vector3Int2, faceDirection);
						if (!hasActiveSpan)
						{
							hasActiveSpan = true;
							faceSpanStartDepth = vector3Int2.z;
							faceSpanLength = 1;
							spanVisual = faceVisual;
						}
						else if (spanVisual.SameAs(faceVisual))
						{
							faceSpanLength++;
						}
						else
						{
							FlushFace();
							hasActiveSpan = true;
							faceSpanStartDepth = vector3Int2.z;
							faceSpanLength = 1;
							spanVisual = faceVisual;
						}
					}
				}
				FlushFace();
			}
			void FlushFace()
			{
				if (hasActiveSpan)
				{
					AddFace(new Vector3Int(x, y, faceSpanStartDepth), faceDirection, faceSpanLength, spanVisual);
					hasActiveSpan = false;
					faceSpanLength = 0;
				}
			}
		}
		int GetAmbientOcclusionColor(Color baseColor, Vector3Int blockPos, Vector3Int faceNormal, Vector3Int firstEdge, Vector3Int secondEdge, out Color vertexColor)
		{
			bool flag = IsBlockPresent(blockPos + faceNormal + firstEdge);
			bool flag2 = IsBlockPresent(blockPos + faceNormal + secondEdge);
			bool flag3 = IsBlockPresent(blockPos + faceNormal + firstEdge + secondEdge);
			int num3 = ((flag && flag2) ? 3 : ((flag ? 1 : 0) + (flag2 ? 1 : 0) + (flag3 ? 1 : 0)));
			float num4 = Mathf.Lerp(1f, minimumAmbientOcclusionBrightness, (float)num3 / 3f);
			vertexColor = new Color(baseColor.r * num4, baseColor.g * num4, baseColor.b * num4, baseColor.a);
			return num3;
		}
		FaceVisual GetFaceVisual(Vector3Int blockPos, FaceDirection faceDirection)
		{
			FaceVisual result = default(FaceVisual);
			if (!TryGetBlockColor(groundData, blockPos, out var color))
			{
				color = Color.gray;
			}
			Vector3Int faceNormal = Vector3Int.zero;
			Vector3Int vector3Int2 = Vector3Int.zero;
			Vector3Int vector3Int3 = Vector3Int.zero;
			switch (faceDirection)
			{
			case FaceDirection.North:
				faceNormal = Vector3Int.up;
				vector3Int2 = Vector3Int.right;
				vector3Int3 = Vector3Int.back;
				break;
			case FaceDirection.South:
				faceNormal = Vector3Int.down;
				vector3Int2 = Vector3Int.left;
				vector3Int3 = Vector3Int.back;
				break;
			case FaceDirection.East:
				faceNormal = Vector3Int.right;
				vector3Int2 = Vector3Int.down;
				vector3Int3 = Vector3Int.back;
				break;
			case FaceDirection.West:
				faceNormal = Vector3Int.left;
				vector3Int2 = Vector3Int.up;
				vector3Int3 = Vector3Int.back;
				break;
			case FaceDirection.Top:
				faceNormal = Vector3Int.back;
				vector3Int2 = Vector3Int.left;
				vector3Int3 = Vector3Int.up;
				break;
			}
			int a = GetAmbientOcclusionColor(color, blockPos, faceNormal, vector3Int2, vector3Int3, out result.firstColor);
			int a2 = GetAmbientOcclusionColor(color, blockPos, faceNormal, -vector3Int2, vector3Int3, out result.secondColor);
			int b = GetAmbientOcclusionColor(color, blockPos, faceNormal, -vector3Int2, -vector3Int3, out result.thirdColor);
			int b2 = GetAmbientOcclusionColor(color, blockPos, faceNormal, vector3Int2, -vector3Int3, out result.fourthColor);
			result.flipQuad = Mathf.Max(a, b) > Mathf.Max(a2, b2);
			return result;
		}
		bool IsBlockPresent(Vector3Int pos)
		{
			if (pos.x < 0 || pos.x >= sizex || pos.y < 0 || pos.y >= sizey || pos.z >= maxChunkDepth)
			{
				return false;
			}
			int num3 = renderPackage.cellDepths[pos.x + sizex * pos.y];
			if (pos.z >= num3)
			{
				if (pos.z == num3)
				{
					return !IsBlockSuppressed(new Vector2Int(pos.x, pos.y));
				}
				return true;
			}
			return false;
		}
	}

	private int GetRenderDepth(RenderPackage renderPackage, int x, int y, int maxChunkDepth)
	{
		int x2 = renderPackage.groundData.sizexy.x;
		int num = renderPackage.cellDepths[x + x2 * y];
		if (num < maxChunkDepth && IsBlockSuppressed(new Vector2Int(x, y)))
		{
			num++;
		}
		return num;
	}

	public static bool TryGetBlockColor(GroundData groundData, Vector3Int blockPos, out Color color)
	{
		color = default(Color);
		if (!TryGetGround(groundData, blockPos, out var ground) || (object)ground.groundSo == null)
		{
			return false;
		}
		if (!ground.groundSo.matchSurroundingGroundColor)
		{
			color = ground.GetColor();
			return true;
		}
		if (TryGetSurroundingGroundColor(groundData, blockPos, out color))
		{
			return true;
		}
		color = ground.GetColor();
		return true;
	}

	private static bool TryGetSurroundingGroundColor(GroundData groundData, Vector3Int origin, out Color color)
	{
		color = Color.gray;
		int num = Mathf.Max(groundData.sizexy.x, groundData.sizexy.y);
		for (int i = 1; i <= num; i++)
		{
			Color clear = Color.clear;
			int num2 = 0;
			foreach (Vector3Int item in SurroundingGroundColorOffsets())
			{
				if (TryGetNonAdaptiveGroundColor(groundData, origin + item * i, out var color2))
				{
					clear += color2;
					num2++;
				}
			}
			if (num2 > 0)
			{
				color = clear / num2;
				return true;
			}
		}
		return false;
	}

	private static bool TryGetNonAdaptiveGroundColor(GroundData groundData, Vector3Int pos, out Color color)
	{
		color = Color.gray;
		if (!TryGetGround(groundData, pos, out var ground) || (object)ground.groundSo == null || ground.groundSo.matchSurroundingGroundColor || !ground.groundSo.isWhitelistedToSpreadGroundColor)
		{
			return false;
		}
		color = ground.GetColor();
		return true;
	}

	private static bool TryGetGround(GroundData groundData, Vector3Int pos, out GroundData.Ground ground)
	{
		ground = default(GroundData.Ground);
		if (groundData == null || pos.x < 0 || pos.x >= groundData.sizexy.x || pos.y < 0 || pos.y >= groundData.sizexy.y)
		{
			return false;
		}
		GroundData.Chunk chunk = groundData.ChunkAt(pos.z);
		if ((object)chunk == null)
		{
			return false;
		}
		ground = chunk.GroundAt(pos, groundData.sizexy);
		return true;
	}

	private static IEnumerable<Vector3Int> SurroundingGroundColorOffsets()
	{
		yield return Vector3Int.up;
		yield return Vector3Int.right;
		yield return Vector3Int.down;
		yield return Vector3Int.left;
		yield return Vector3Int.up + Vector3Int.right;
		yield return Vector3Int.down + Vector3Int.right;
		yield return Vector3Int.down + Vector3Int.left;
		yield return Vector3Int.up + Vector3Int.left;
	}
}
public class GridManager
{
	public struct Cell
	{
		public Entity entity;

		public double waterVolume;

		public int cactusNumber;

		public Vector2Int pos;

		public int depth;
	}

	private const double MAX_WATER_VOLUME = 1.0;

	private const double WATER_DECAY_INTERVAL = 0.1;

	private const double WATER_DECAY_PROBABILITY = 0.1;

	private const double WATER_DECAY_FACTOR = 0.99;

	public const double MAX_HARDNESS = 10.0;

	public const int CHUNK_EXTENT = 16;

	public const int MAX_DEPTH = 200000000;

	public Farm farm;

	public PumpkinController pumpkinController;

	public SweeperController sweeperController;

	public TreasureMapController treasureMapController;

	public MushroomController mushroomController;

	public PyramidController pyramidController;

	private static Dictionary<string, Type> farmObjectTypes;

	private Vector2Int worldSizeOverride;

	private int startingChunkOverride;

	private readonly bool generateUnderground;

	private readonly List<GroundFeature> leaderboardFeatures;

	private readonly List<int> pretendedFeatureChunks;

	private readonly List<int> pretendedChunkDepths;

	private int groundSeed;

	private OpenSimplexNoise hardnessNoise;

	public OpenSimplexNoise bambooNoise;

	public GroundData groundData;

	private int sizeLimit;

	public bool hadIncorrectSunflowerHarvest;

	public Cell[] cells;

	private Cell defaultCell;

	public static readonly Vector3Int north = new Vector3Int(0, 1, 0);

	public static readonly Vector3Int east = new Vector3Int(1, 0, 0);

	public static readonly Vector3Int south = new Vector3Int(0, -1, 0);

	public static readonly Vector3Int west = new Vector3Int(-1, 0, 0);

	public static readonly Vector3Int down = new Vector3Int(0, 0, 1);

	public static readonly Vector3Int up = new Vector3Int(0, 0, -1);

	private static DummyGrasslandFeature grasslandFeature;

	public IEnumerable<GridController> GridControllers => new GridController[5] { pumpkinController, sweeperController, treasureMapController, mushroomController, pyramidController };

	public Vector2Int WorldSize { get; private set; }

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
				sizeLimit = value;
				GenerateWorld();
			}
			else if (sizeLimit > 0)
			{
				sizeLimit = 0;
				GenerateWorld();
			}
		}
	}

	public int maxUncoveredDepth { get; private set; }

	public Vector3 midPoint => (CellToLocal(WorldSize) + CellToLocal(Vector2Int.zero) + Vector3.left) / 2f;

	public GridController GetController(string name)
	{
		return name switch
		{
			"Pumpkin" => pumpkinController, 
			"Sweeper" => sweeperController, 
			"TreasureMap" => treasureMapController, 
			"Mushroom" => mushroomController, 
			"Pyramid" => pyramidController, 
			_ => throw new Exception("Unkown grid controller named '" + name + "'"), 
		};
	}

	private void CreateControllers()
	{
		pumpkinController = new PumpkinController(this);
		sweeperController = new SweeperController(this);
		treasureMapController = new TreasureMapController(this);
		mushroomController = new MushroomController(this);
		pyramidController = new PyramidController(this);
	}

	public void GenerateExpandedWorld()
	{
		sizeLimit = 0;
		GenerateWorld();
	}

	public float ComputeAverageDepth()
	{
		if (cells == null || cells.Length == 0)
		{
			return 0f;
		}
		long num = 0L;
		Cell[] array = cells;
		for (int i = 0; i < array.Length; i++)
		{
			Cell cell = array[i];
			num += cell.depth;
		}
		return (float)num / (float)cells.Length;
	}

	public (float averageDepth, int maxDepth) ComputeAverageAndMaxDepth()
	{
		if (cells == null || cells.Length == 0)
		{
			return default((float, int));
		}
		int num = int.MinValue;
		long num2 = 0L;
		Cell[] array = cells;
		for (int i = 0; i < array.Length; i++)
		{
			Cell cell = array[i];
			num2 += cell.depth;
			num = Math.Max(num, cell.depth);
		}
		return (averageDepth: (float)num2 / (float)cells.Length, maxDepth: num);
	}

	public ref Cell CellAt(int x, int y)
	{
		return ref cells[y * WorldSize.x + x];
	}

	public ref Cell CellAt(Vector2Int pos)
	{
		return ref CellAt(pos.x, pos.y);
	}

	public ref Cell CellAtOrDefault(int x, int y)
	{
		if (x < 0 || y < 0 || x >= WorldSize.x || y >= WorldSize.y)
		{
			return ref defaultCell;
		}
		return ref CellAt(x, y);
	}

	public ref Cell CellAtOrDefault(Vector2Int pos)
	{
		return ref CellAtOrDefault(pos.x, pos.y);
	}

	public GridManager(Farm farm, Vector2Int worldSizeOverride = default(Vector2Int), int startingChunkOverride = 0, bool generateUnderground = true, List<GroundFeature> leaderboardFeatures = null, List<int> pretendedFeatureChunks = null, List<int> pretendedChunkDepths = null)
	{
		this.farm = farm;
		farm.grid = this;
		this.worldSizeOverride = worldSizeOverride;
		this.startingChunkOverride = startingChunkOverride;
		this.generateUnderground = generateUnderground;
		this.leaderboardFeatures = leaderboardFeatures;
		this.pretendedFeatureChunks = pretendedFeatureChunks;
		this.pretendedChunkDepths = pretendedChunkDepths;
		CreateControllers();
		farm.sim.StartTimer(WaterDecay, Duration.FromSeconds(0.1));
	}

	private void UpdateWorldSize()
	{
		if (worldSizeOverride.x > 0 && worldSizeOverride.y > 0)
		{
			WorldSize = worldSizeOverride;
			return;
		}
		int num = Helper.WorldSizeScale(farm.NumUnlocked("expand"));
		if (sizeLimit > 0 && sizeLimit < num)
		{
			WorldSize = new Vector2Int(sizeLimit, sizeLimit);
		}
		else
		{
			WorldSize = ((num == 2) ? new Vector2Int(1, 3) : new Vector2Int(num, num));
		}
	}

	public void SetWaterVolume(Vector2Int pos, double volume)
	{
		ref Cell reference = ref CellAt(pos);
		double waterVolume = reference.waterVolume;
		reference.waterVolume = Math.Clamp(volume, 0.0, 1.0);
		if (reference.waterVolume != waterVolume)
		{
			GroundSO groundSo = GroundAt(pos).groundSo;
			if (groundSo != null && groundSo.objectName == "soil" && groundSo.CrossesWaterDecorationThreshold(waterVolume, reference.waterVolume))
			{
				groundData.MarkPositionChanged(pos);
			}
			if (reference.entity is Growable growable)
			{
				growable.UpdateFarmObject();
			}
		}
	}

	private void WaterDecay()
	{
		Span<Cell> span = cells.AsSpan();
		for (int i = 0; i < span.Length; i++)
		{
			ref Cell reference = ref span[i];
			if (farm.sim.randomVarious.NextDouble() < 0.1)
			{
				SetWaterVolume(reference.pos, reference.waterVolume * 0.99);
			}
		}
		farm.sim.StartTimer(WaterDecay, Duration.FromSeconds(0.1));
	}

	public void ClearGrid(bool spawnGrass = true, int upToChunk = 0, HashSet<GroundFeature> skippedProbabilityCheckFeatures = null)
	{
		int num = Math.Max(startingChunkOverride, upToChunk);
		List<int> list = pretendedChunkDepths;
		bool flag = list != null && list.Count > 0 && pretendedChunkDepths[0] != 0;
		bool flag2 = num == 0 && !flag;
		foreach (GridController gridController in GridControllers)
		{
			gridController?.ClearGrid();
		}
		groundSeed = Helper.JustSha256It(farm.sim.randomWorldGen);
		hardnessNoise = new OpenSimplexNoise(farm.sim.randomWorldGen.Next());
		bambooNoise = new OpenSimplexNoise(farm.sim.randomBamboo.Next());
		groundData = new GroundData(WorldSize);
		Span<Cell> span = cells.AsSpan();
		for (int i = 0; i < span.Length; i++)
		{
			ref Cell reference = ref span[i];
			reference.depth = num * 16;
			if (num != 0)
			{
				ChunkAt(num * 16, skippedProbabilityCheckFeatures);
			}
			else if (GroundAt(reference.pos).groundSo.objectName != "grassland" && flag2)
			{
				SetGround(reference.pos, "grassland");
			}
			if (flag2 && spawnGrass)
			{
				SetEntity(reference.pos, "grass");
			}
			else
			{
				RemoveEntity(reference.pos, regrowGrass: false);
			}
		}
		maxUncoveredDepth = num * 16;
	}

	public void GenerateWorld()
	{
		if (cells != null)
		{
			Span<Cell> span = cells.AsSpan();
			for (int i = 0; i < span.Length; i++)
			{
				Free(span[i].entity);
			}
		}
		Vector2Int worldSize = WorldSize;
		UpdateWorldSize();
		Cell[] array = cells;
		cells = new Cell[WorldSize.x * WorldSize.y];
		for (int j = 0; j < WorldSize.y; j++)
		{
			for (int k = 0; k < WorldSize.x; k++)
			{
				ref Cell reference = ref CellAt(k, j);
				if (array != null && k < worldSize.x && j < worldSize.y)
				{
					reference.waterVolume = array[j * worldSize.x + k].waterVolume;
					reference.cactusNumber = array[j * worldSize.x + k].cactusNumber;
				}
				reference.pos = new Vector2Int(k, j);
				reference.cactusNumber = -1;
			}
		}
		ClearGrid();
	}

	public bool Swap(Vector2Int pos, GridDirection dir)
	{
		ref Cell reference = ref CellAt(pos);
		Entity entity = reference.entity;
		Vector2Int pos2 = pos + dir.GetDirectionVector();
		if (!IsWithinBounds(pos2))
		{
			return false;
		}
		ref Cell reference2 = ref CellAt(pos2);
		Entity entity2 = reference2.entity;
		if (reference.depth != reference2.depth)
		{
			return false;
		}
		if ((entity != null && !entity.objectSO.canBeSwapped) || (entity2 != null && !entity2.objectSO.canBeSwapped))
		{
			return false;
		}
		if (farm.sim.simRunner != null && farm.sim.simRunner.TimeFactor == 1.0)
		{
			farm.sim.simRunner.PlayEffect(VFXType.light_dust, CellToLocal(pos));
			farm.sim.simRunner.PlayEffect(VFXType.light_dust, CellToLocal(pos2));
		}
		int cactusNumber = reference.cactusNumber;
		reference.cactusNumber = reference2.cactusNumber;
		reference2.cactusNumber = cactusNumber;
		if (entity != null)
		{
			reference2.entity = entity;
			entity.AnimateMove(CellToLocal(pos2), Duration.FromSeconds(0.1));
			entity.pos3 = new Vector3Int(pos2.x, pos2.y, reference2.depth);
			entity.UpdateFarmObject();
			entity.UpdateNeighbors();
			entity.OnSwapped();
		}
		else
		{
			reference2.entity = null;
		}
		if (entity2 != null)
		{
			reference.entity = entity2;
			entity2.AnimateMove(CellToLocal(pos), Duration.FromSeconds(0.1));
			entity2.pos3 = new Vector3Int(pos.x, pos.y, reference.depth);
			entity2.UpdateFarmObject();
			entity2.UpdateNeighbors();
			entity2.OnSwapped();
		}
		else
		{
			reference.entity = null;
		}
		return true;
	}

	public void ClearGround(Vector2Int pos, int upToDepth, bool crumbleEffect = true, Action<Vector3Int, GroundSO> onGroundCleared = null)
	{
		bool flag = OptionHolder.GetString("avalanche particles", "enabled") != "disabled";
		ClearGroundInternal(pos, upToDepth, crumbleEffect && flag, onGroundCleared);
	}

	private void ClearGroundInternal(Vector2Int pos, int upToDepth, bool crumbleEffect, Action<Vector3Int, GroundSO> onGroundCleared = null)
	{
		ref Cell reference = ref CellAt(pos);
		if (reference.depth >= upToDepth)
		{
			return;
		}
		for (int i = reference.depth; i < upToDepth; i++)
		{
			onGroundCleared?.Invoke(new Vector3Int(pos.x, pos.y, i), GroundAt(pos.x, pos.y, i).groundSo);
			if (crumbleEffect)
			{
				farm.sim.simRunner.CrumbleEffect(new Vector3Int(pos.x, pos.y, i));
			}
			SetBlockPresent(new Vector3Int(pos.x, pos.y, i), isPresent: false);
		}
		reference.depth = upToDepth;
		if (reference.depth > maxUncoveredDepth)
		{
			maxUncoveredDepth = reference.depth;
		}
		RemoveEntity(pos);
	}

	public float CaveInDistanceFunction(Vector2Int holePos, Vector2Int cavedInCellPos)
	{
		return DesignConstants.Inst.caveIn.caveInDistanceFunction switch
		{
			DesignConstants.DistanceFunction.Circle => Mathf.Sqrt(Mathf.Pow(holePos.x - cavedInCellPos.x, 2f) + Mathf.Pow(holePos.y - cavedInCellPos.y, 2f)), 
			DesignConstants.DistanceFunction.Square => Math.Max(Math.Abs(holePos.x - cavedInCellPos.x), Math.Abs(holePos.y - cavedInCellPos.y)), 
			_ => throw new ArgumentOutOfRangeException(), 
		};
	}

	public void ClearGroundWithCaveins(Vector2Int aroundPos, int upToDepth)
	{
		bool crumbleEffect = OptionHolder.GetString("avalanche particles", "enabled") != "disabled";
		ClearGroundInternal(aroundPos, upToDepth, crumbleEffect);
		Deque<Vector2Int> deque = new Deque<Vector2Int>();
		foreach (Vector2Int item in Neighboring4Positions(aroundPos))
		{
			if (IsWithinBounds(item))
			{
				if (!GroundAt(item).groundSo.autodestroyWhenDugBeside)
				{
					deque.Enqueue(item);
				}
				else
				{
					ClearGroundInternal(item, upToDepth - 1, crumbleEffect);
				}
			}
		}
		foreach (Vector2Int item2 in NeighboringDiagonals(aroundPos))
		{
			if (IsWithinBounds(item2))
			{
				deque.Enqueue(item2);
			}
		}
		foreach (Vector2Int item3 in GetRingAroundPosition(aroundPos, 2))
		{
			if (IsWithinBounds(item3) && item3.x != item3.y)
			{
				deque.Enqueue(item3);
			}
		}
		while (deque.Count > 0)
		{
			Vector2Int pos = deque.Dequeue();
			Vector2Int[] array = ((DesignConstants.Inst.caveIn.neighborsInStabilityPropagation == DesignConstants.ConsideredNeighborsKind.eight) ? Neighboring8Positions(pos) : Neighboring4Positions(pos)).ToArray();
			Cell cell = CellAt(pos);
			int num = 0;
			Vector2Int[] array2 = array;
			foreach (Vector2Int pos2 in array2)
			{
				if (IsWithinBounds(pos2))
				{
					int depth = CellAt(pos2).depth;
					if (depth > num)
					{
						num = depth;
					}
				}
			}
			for (int num2 = num - 1; num2 >= cell.depth; num2--)
			{
				if (GroundAt(pos, num2).stability < num - num2)
				{
					int num3 = num2 + 1;
					ClearGroundInternal(pos, num3, crumbleEffect);
					array2 = array;
					foreach (Vector2Int vector2Int in array2)
					{
						if (IsWithinBounds(vector2Int) && CellAt(vector2Int).depth < num3)
						{
							deque.Enqueue(vector2Int);
						}
					}
					break;
				}
			}
		}
	}

	public void RemoveTopsoil(Vector2Int pos, int amount)
	{
		ref Cell reference = ref CellAt(pos);
		GroundAt(pos.x, pos.y, reference.depth + amount) = GroundAt(pos.x, pos.y, reference.depth);
		SetBlockPresent(new Vector3Int(pos.x, pos.y, reference.depth + amount), isPresent: true);
		for (int i = 0; i < amount; i++)
		{
			SetBlockPresent(new Vector3Int(pos.x, pos.y, reference.depth + i), isPresent: false);
		}
		reference.depth += amount;
		if (reference.entity != null)
		{
			reference.entity.LocalPosition = CellToLocal(reference.pos, reference.depth);
		}
	}

	public void SetGround(Vector2Int pos, string newGround, int? overrideHardness = null)
	{
		SetGround(pos, CellAt(pos).depth, ResourceManager.GetGround(newGround), overrideHardness);
	}

	public void SetGround(Vector3Int pos, string newGround, int? overrideHardness = null)
	{
		SetGround((Vector2Int)pos, pos.z, ResourceManager.GetGround(newGround), overrideHardness);
	}

	public void SetGround(Vector3Int pos, GroundSO newGround, int? overrideHardness = null)
	{
		SetGround((Vector2Int)pos, pos.z, newGround, overrideHardness);
	}

	public void SetGround(Vector2Int pos, int depth, GroundSO newGround, int? overrideHardness = null)
	{
		ref Cell reference = ref CellAt(pos.x, pos.y);
		GroundData.Chunk chunk = ChunkAt(depth);
		bool num = !chunk.IsBlockPresent(pos.x, pos.y, depth, WorldSize);
		GroundData.Ground ground = new GroundData.Ground(newGround);
		if (overrideHardness.HasValue)
		{
			int valueOrDefault = overrideHardness.GetValueOrDefault();
			ground.hardness = valueOrDefault;
		}
		chunk.GroundAt(pos.x, pos.y, depth, WorldSize) = ground;
		SetBlockPresent(chunk, pos.x, pos.y, depth, isPresent: true);
		if (num)
		{
			reference.depth--;
		}
	}

	private void SetBlockPresent(Vector3Int pos, bool isPresent)
	{
		SetBlockPresent(ChunkAt(pos.z), pos.x, pos.y, pos.z, isPresent);
	}

	private void SetBlockPresent(GroundData.Chunk chunk, int x, int y, int depth, bool isPresent)
	{
		chunk.SetBlockPresent(x, y, depth, WorldSize, isPresent);
		groundData.MarkPositionChanged(x, y);
	}

	public TEntity GetEntity<TEntity>(Vector2Int pos) where TEntity : Entity
	{
		if (!IsWithinBounds(pos))
		{
			return null;
		}
		return CellAt(pos).entity as TEntity;
	}

	public TEntity GetEntity<TEntity>(int x, int y) where TEntity : Entity
	{
		return GetEntity<TEntity>(new Vector2Int(x, y));
	}

	public Entity SetEntity(Vector2Int pos, string newObject)
	{
		ref Cell reference = ref CellAt(pos);
		if (reference.entity != null)
		{
			Free(reference.entity);
		}
		Vector3Int pos2 = new Vector3Int(pos.x, pos.y, reference.depth);
		return SetEntity(pos2, newObject, isGround: false);
	}

	public void RemoveEntity(Vector2Int pos, bool regrowGrass = true)
	{
		if (CellAt(pos).entity != null)
		{
			Free(CellAt(pos).entity);
			if (regrowGrass && GroundAt(pos).groundSo.objectName == "grassland")
			{
				SetEntity(pos, "grass");
			}
		}
	}

	public static IEnumerable<Vector2Int> Neighboring4Positions(Vector2Int pos)
	{
		yield return pos + new Vector2Int(0, 1);
		yield return pos + new Vector2Int(1, 0);
		yield return pos + new Vector2Int(0, -1);
		yield return pos + new Vector2Int(-1, 0);
	}

	public static IEnumerable<Vector2Int> NeighboringDiagonals(Vector2Int pos)
	{
		yield return pos + new Vector2Int(1, 1);
		yield return pos + new Vector2Int(1, -1);
		yield return pos + new Vector2Int(-1, -1);
		yield return pos + new Vector2Int(-1, 1);
	}

	public static IEnumerable<Vector2Int> Neighboring8Positions(Vector2Int pos)
	{
		yield return pos + new Vector2Int(0, 1);
		yield return pos + new Vector2Int(1, 1);
		yield return pos + new Vector2Int(1, 0);
		yield return pos + new Vector2Int(1, -1);
		yield return pos + new Vector2Int(0, -1);
		yield return pos + new Vector2Int(-1, -1);
		yield return pos + new Vector2Int(-1, 0);
		yield return pos + new Vector2Int(-1, 1);
	}

	public static IEnumerable<Vector3Int> Neighboring3DPositions(Vector3Int pos)
	{
		yield return pos + new Vector3Int(0, 1, 0);
		yield return pos + new Vector3Int(1, 0, 0);
		yield return pos + new Vector3Int(0, -1, 0);
		yield return pos + new Vector3Int(-1, 0, 0);
		yield return pos + new Vector3Int(0, 0, 1);
		yield return pos + new Vector3Int(0, 0, -1);
	}

	public static IEnumerable<Vector2Int> GetRingAroundPosition(Vector2Int pos, int radius)
	{
		Vector2Int[] directions = new Vector2Int[4]
		{
			new Vector2Int(1, 0),
			new Vector2Int(0, 1),
			new Vector2Int(-1, 0),
			new Vector2Int(0, -1)
		};
		for (int d = 0; d < directions.Length; d++)
		{
			for (int i = 0; i < radius * 2; i++)
			{
				yield return pos - radius * directions[d] - radius * directions[(d + 1) % 4] + i * directions[d];
			}
		}
	}

	public Entity[] GetNeighbors(Vector2Int pos, Entity[] array = null)
	{
		return GetNeighbors<Entity>(pos);
	}

	public TEntity[] GetNeighbors<TEntity>(Vector2Int pos, TEntity[] array = null) where TEntity : Entity
	{
		if (array == null || array.Length < 4)
		{
			array = new TEntity[4];
		}
		array[0] = GetEntityOrNull<TEntity>(pos + new Vector2Int(0, 1));
		array[1] = GetEntityOrNull<TEntity>(pos + new Vector2Int(1, 0));
		array[2] = GetEntityOrNull<TEntity>(pos + new Vector2Int(0, -1));
		array[3] = GetEntityOrNull<TEntity>(pos + new Vector2Int(-1, 0));
		return array;
	}

	private TEntity GetEntityOrNull<TEntity>(Vector2Int pos) where TEntity : Entity
	{
		if (!IsWithinBounds(pos))
		{
			return null;
		}
		return CellAt(pos).entity as TEntity;
	}

	public Vector2Int Wrap(Vector2Int pos)
	{
		return new Vector2Int((pos.x + WorldSize.x) % WorldSize.x, (pos.y + WorldSize.y) % WorldSize.y);
	}

	public Vector3Int Wrap(Vector3Int pos)
	{
		return new Vector3Int((pos.x + WorldSize.x) % WorldSize.x, (pos.y + WorldSize.y) % WorldSize.y, 0);
	}

	public bool IsWithinBounds(Vector2Int pos)
	{
		if (pos.x >= 0 && pos.y >= 0 && pos.x < WorldSize.x)
		{
			return pos.y < WorldSize.y;
		}
		return false;
	}

	public bool IsWithinBounds(Vector3Int pos)
	{
		if (pos.x >= 0 && pos.y >= 0 && pos.x < WorldSize.x)
		{
			return pos.y < WorldSize.y;
		}
		return false;
	}

	public Vector3 CellToLocal(Vector2Int pos)
	{
		return new Vector3(-pos.x, pos.y, -CellAtOrDefault(pos).depth);
	}

	public Vector3 CellToLocalWithPlants(Vector2Int pos)
	{
		Cell cell = CellAtOrDefault(pos);
		if (cell.entity is Sunflower sunflower && sunflower.WasSpawnedFromPyramid())
		{
			return new Vector3(-pos.x, pos.y, -cell.depth + 1);
		}
		return new Vector3(-pos.x, pos.y, -cell.depth);
	}

	public static Vector3 CellToLocal(Vector2Int pos, int depth)
	{
		return new Vector3(-pos.x, pos.y, -depth);
	}

	public static Vector3 CellToLocal(Vector3Int pos)
	{
		return new Vector3(-pos.x, pos.y, -pos.z);
	}

	public static Vector3 CellToLocal(Vector3 pos)
	{
		return new Vector3(0f - pos.x, pos.y, 0f - pos.z);
	}

	public static Vector3 CellToLocal(int x, int y, int z)
	{
		return new Vector3(-x, y, -z);
	}

	public static Vector2Int LocalToCell(Vector3 localPos)
	{
		return new Vector2Int(Mathf.RoundToInt(0f - localPos.x), Mathf.RoundToInt(localPos.y));
	}

	public static Vector3Int LocalToBlock(Vector3 localPos)
	{
		return new Vector3Int(Mathf.RoundToInt(0f - localPos.x), Mathf.RoundToInt(localPos.y), Mathf.RoundToInt(0f - localPos.z));
	}

	private Entity CreateEntity(EntitySO objectSO)
	{
		if (farmObjectTypes == null)
		{
			farmObjectTypes = (from type in typeof(Entity).Assembly.GetTypes()
				where type.IsSubclassOf(typeof(Entity)) || type == typeof(Entity)
				select type).ToDictionary((Type t) => t.Name, (Type t) => t);
		}
		return (Entity)Activator.CreateInstance(farmObjectTypes[objectSO.className]);
	}

	private Entity SetEntity(Vector3Int pos, string objName, bool isGround)
	{
		EntitySO entity = ResourceManager.GetEntity(objName);
		Entity entity2 = CreateEntity(entity);
		entity2.objectSO = entity;
		entity2.pos3 = pos;
		entity2.LocalPosition = CellToLocal(pos);
		entity2.sim = farm.sim;
		CellAt(entity2.pos).entity = entity2;
		entity2.OnRestart();
		if (farm.sim.simRunner != null)
		{
			farm.sim.simRunner.SetDirty();
		}
		return entity2;
	}

	public void Free(Entity obj)
	{
		if (obj != null)
		{
			if (IsWithinBounds(obj.pos) && CellAt(obj.pos).entity == obj)
			{
				CellAt(obj.pos).entity = null;
			}
			obj.OnFree();
		}
	}

	private int GetChunkLoopSize(List<GroundFeature> features)
	{
		int num = 1;
		foreach (GroundFeature feature in features)
		{
			if (feature.associatedUnlockForGroundLoop != "" && farm.IsUnlocked(feature.associatedUnlockForGroundLoop))
			{
				int val = 0;
				if (feature.chunkIndexWhitelist.Count > 0)
				{
					val = (feature.onlyIncludeFirstChunkInGroundLoop ? (feature.chunkIndexWhitelist[0] + 1) : (feature.chunkIndexWhitelist.Max() + 1));
				}
				num = Math.Max(num, val);
			}
		}
		return num;
	}

	private List<GroundFeature> GetGroundFeatures()
	{
		List<GroundFeature> list = new List<GroundFeature>(ResourceManager.GetAllGroundFeatures());
		if (grasslandFeature == null)
		{
			grasslandFeature = ScriptableObject.CreateInstance<DummyGrasslandFeature>();
		}
		list.Insert(0, grasslandFeature);
		return list;
	}

	public void JumpToFeature(IEnumerable<GroundFeature> features, int jumpPadding = 3)
	{
		HashSet<GroundFeature> hashSet = new HashSet<GroundFeature>(features);
		int num = int.MaxValue;
		foreach (GroundFeature feature in features)
		{
			int firstChunkWhereFeatureSpawns = GetFirstChunkWhereFeatureSpawns(feature);
			num = Mathf.Min(num, firstChunkWhereFeatureSpawns);
		}
		int num2 = 0;
		int num3 = 0;
		int num4 = int.MaxValue;
		for (int i = 0; i < 6; i++)
		{
			ClearGrid(spawnGrass: true, num, hashSet);
			num2++;
			int num5 = groundData.startChunkIndex * 16;
			num4 = int.MaxValue;
			for (int j = 0; j < 3; j++)
			{
				GroundData.Chunk chunk = ChunkAt(num5, hashSet);
				num3++;
				GroundFeature.GeneratedFeature generatedFeature = chunk.features.Find((GroundFeature.GeneratedFeature g) => features.Contains(g.feature));
				if (generatedFeature.feature == null)
				{
					UnityEngine.Debug.Log(string.Format("JumpToFeature: Could not find features '{0}' in generated chunk @ {1}", string.Join(", ", features.Select((GroundFeature f) => f.Name)), chunk.startingDepth));
				}
				if (generatedFeature.bounds == null || !generatedFeature.bounds.Any())
				{
					UnityEngine.Debug.Log(string.Format("JumpToFeature: Feature '{0}' has no bounding volumes in chunk @ {1}", string.Join(", ", features.Select((GroundFeature f) => f.Name)), chunk.startingDepth));
					num5 += 16;
					continue;
				}
				foreach (BoundingBoxInt bound in generatedFeature.bounds)
				{
					num4 = Mathf.Min(bound.min.z, num4);
				}
				break;
			}
			if (num4 != int.MaxValue)
			{
				break;
			}
		}
		if (num4 == int.MaxValue)
		{
			UnityEngine.Debug.LogError(string.Format("JumpToFeature: Failed to jump to feature '{0}' (with {1} clear and {2} generated chunks)", string.Join(", ", features.Select((GroundFeature f) => f.Name)), num2, num3));
			return;
		}
		UnityEngine.Debug.Log(string.Format("JumpToFeature: Found '{0}' with {1} clear and {2} generated chunks.", string.Join(", ", features.Select((GroundFeature f) => f.Name)), num2, num3));
		int upToDepth = Mathf.Max(num4 - jumpPadding, groundData.startChunkIndex * 16);
		for (int num6 = 0; num6 < WorldSize.x; num6++)
		{
			for (int num7 = 0; num7 < WorldSize.y; num7++)
			{
				ClearGround(new Vector2Int(num6, num7), upToDepth, crumbleEffect: false);
			}
		}
	}

	private int GetFirstChunkWhereFeatureSpawns(GroundFeature feature)
	{
		List<GroundFeature> groundFeatures = GetGroundFeatures();
		int chunkLoopSize = GetChunkLoopSize(groundFeatures);
		int num = Math.Max(MathUtil.FloorDiv(maxUncoveredDepth, 16) + 1, 0);
		for (int i = 0; i < chunkLoopSize; i++)
		{
			int item = num % chunkLoopSize;
			bool num2 = feature.chunkIndexWhitelist.Count > 0 && !feature.chunkIndexWhitelist.Contains(item);
			bool flag = feature.chunkIndexBlacklist.Contains(item);
			if (!num2 && !flag)
			{
				return num;
			}
			num++;
		}
		throw new InvalidOperationException("Feature has not been properly configured and is always blacklisted/never whitelisted.");
	}

	private GroundData.Chunk GenerateChunk(int chunkIndex, HashSet<GroundFeature> droneJumpTargets = null)
	{
		if (!farm.IsDlcInstalled(EDlcType.Mining))
		{
			GroundData.Chunk obj = new GroundData.Chunk
			{
				startingDepth = chunkIndex * 16,
				tiles = new GroundData.Ground[WorldSize.x * WorldSize.y * 16],
				features = new List<GroundFeature.GeneratedFeature>()
			};
			Array.Fill(obj.tiles, new GroundData.Ground(ResourceManager.GetGround("dirt")));
			obj.InitializeBlockPresence(isPresent: true);
			return obj;
		}
		List<GroundFeature> features = GetGroundFeatures();
		List<GroundFeature> list = leaderboardFeatures;
		bool flag = list != null && list.Count > 0;
		int num = (flag ? leaderboardFeatures.Count : GetChunkLoopSize(features));
		while (chunkIndex >= num + groundData.currentGroundLoopStart)
		{
			groundData.currentGroundLoopStart += num;
		}
		int loopedChunkIndex = chunkIndex - groundData.currentGroundLoopStart;
		new Stopwatch().Start();
		GroundData.Chunk c = new GroundData.Chunk();
		c.startingDepth = chunkIndex * 16;
		c.tiles = new GroundData.Ground[WorldSize.x * WorldSize.y * 16];
		int chunkSeed = groundSeed + chunkIndex + 100;
		c.random = new System.Random(chunkSeed);
		GroundFeature.Context ctx = new GroundFeature.Context
		{
			sim = farm.sim,
			chunk = c,
			features = new List<GroundFeature.GeneratedFeature>(),
			loopStartIndex = groundData.currentGroundLoopStart,
			loopStartDepth = groundData.currentGroundLoopStart * 16
		};
		if (generateUnderground)
		{
			if (flag)
			{
				generateLeaderboardUnderground();
			}
			else
			{
				generateNormalUnderground();
			}
		}
		GroundSO ground = ResourceManager.GetGround("dirt");
		for (int i = 0; i < WorldSize.x; i++)
		{
			for (int j = 0; j < WorldSize.y; j++)
			{
				for (int k = c.startingDepth; k < c.startingDepth + 16; k++)
				{
					ref GroundData.Ground reference = ref c.GroundAt(i, j, k, WorldSize);
					if ((object)reference.groundSo == null)
					{
						reference = new GroundData.Ground(ground);
					}
				}
			}
		}
		c.features = ctx.features;
		c.InitializeBlockPresence(isPresent: true);
		pyramidController.ClearOldPyramids(this);
		return c;
		void generateLeaderboardUnderground()
		{
			GroundFeature groundFeature = leaderboardFeatures[loopedChunkIndex];
			for (int l = 0; l < features.Count; l++)
			{
				GroundFeature groundFeature2 = features[l];
				int item = pretendedFeatureChunks[loopedChunkIndex];
				bool flag2 = groundFeature2 == groundFeature;
				if (groundFeature2.enabled && (string.IsNullOrEmpty(groundFeature2.associatedUnlockForGroundLoop) || flag2))
				{
					bool num2 = !flag2 && groundFeature2.chunkIndexWhitelist.Count > 0 && !groundFeature2.chunkIndexWhitelist.Contains(item);
					bool flag3 = !flag2 && groundFeature2.chunkIndexBlacklist.Contains(item);
					if (!(num2 || flag3))
					{
						try
						{
							ctx.random = new System.Random(chunkSeed + (l + 1) * 1000);
							if (flag2)
							{
								List<int> list2 = pretendedChunkDepths;
								if (list2 != null && list2.Count > 0)
								{
									ctx.pretendedChunkDepth = pretendedChunkDepths[loopedChunkIndex];
								}
							}
							foreach (GroundFeature.GeneratedFeature feature in ctx.features)
							{
								if (feature.feature.DoesPermitLaterFeature(in ctx, groundFeature2))
								{
									continue;
								}
								goto end_IL_00a2;
							}
							float probability = groundFeature2.GetProbability(in ctx);
							if (flag2 || !((double)probability < c.random.NextDouble()))
							{
								IEnumerable<BoundingBoxInt> enumerable = groundFeature2.Generate(in ctx);
								if (enumerable != null)
								{
									ctx.features.Add(new GroundFeature.GeneratedFeature
									{
										feature = groundFeature2,
										bounds = enumerable
									});
								}
							}
							end_IL_00a2:;
						}
						catch (Exception exception)
						{
							UnityEngine.Debug.LogException(exception);
						}
					}
				}
			}
		}
		void generateNormalUnderground()
		{
			bool flag2 = droneJumpTargets?.Any((GroundFeature f) => f is PyramidFeature) ?? false;
			for (int num2 = 0; num2 < features.Count; num2++)
			{
				GroundFeature groundFeature = features[num2];
				if (groundFeature.enabled && (string.IsNullOrEmpty(groundFeature.associatedUnlockForGroundLoop) || farm.IsUnlocked(groundFeature.associatedUnlockForGroundLoop)))
				{
					bool num3 = groundFeature.chunkIndexWhitelist.Count > 0 && !groundFeature.chunkIndexWhitelist.Contains(loopedChunkIndex);
					bool flag3 = groundFeature.chunkIndexBlacklist.Contains(loopedChunkIndex);
					if (!(num3 || flag3) && (!flag2 || (!(groundFeature is MushroomFeature) && !(groundFeature is TreasureMapFeature))))
					{
						try
						{
							ctx.random = new System.Random(chunkSeed + (num2 + 1) * 1000);
							foreach (GroundFeature.GeneratedFeature feature2 in ctx.features)
							{
								if (feature2.feature.DoesPermitLaterFeature(in ctx, groundFeature))
								{
									continue;
								}
								goto end_IL_00f8;
							}
							float probability = groundFeature.GetProbability(in ctx);
							if ((droneJumpTargets?.Contains(groundFeature) ?? false) || !((double)probability < c.random.NextDouble()))
							{
								IEnumerable<BoundingBoxInt> enumerable = groundFeature.Generate(in ctx);
								if (enumerable != null)
								{
									ctx.features.Add(new GroundFeature.GeneratedFeature
									{
										feature = groundFeature,
										bounds = enumerable
									});
								}
							}
							end_IL_00f8:;
						}
						catch (Exception exception)
						{
							UnityEngine.Debug.LogException(exception);
						}
					}
				}
			}
		}
	}

	public GroundData.Chunk ChunkAt(int depth, HashSet<GroundFeature> droneJumpTargets = null)
	{
		(int, int) chunksRange = groundData.ChunksRange;
		int num = MathUtil.FloorDiv(depth, 16);
		if (num < groundData.startChunkIndex)
		{
			for (int num2 = groundData.startChunkIndex - 1; num2 >= num; num2--)
			{
				groundData.SetChunk(num2, GroundData.Chunk.CreateEmpty(num2, WorldSize), trimEmptyTopChunks: false);
			}
		}
		GroundData.Chunk chunk = groundData.ChunkAt(depth);
		if (chunk == null)
		{
			chunk = GenerateChunk(num, droneJumpTargets);
			groundData.SetChunk(num, chunk);
		}
		(int, int) tuple = chunksRange;
		(int, int) chunksRange2 = groundData.ChunksRange;
		if (tuple.Item1 != chunksRange2.Item1 || tuple.Item2 != chunksRange2.Item2)
		{
			int num3 = groundData.startChunkIndex * 16;
			int endDepth = num3 + groundData.chunks.Count * 16;
			foreach (GridController gridController in GridControllers)
			{
				gridController.OnChunksAddedOrRemoved(num3, endDepth);
			}
		}
		return chunk;
	}

	public bool TryGetExistingGroundAt(Vector3Int pos, out GroundData.Ground ground)
	{
		ground = default(GroundData.Ground);
		if (!IsWithinBounds(pos))
		{
			return false;
		}
		GroundData.Chunk chunk = groundData.ChunkAt(pos.z);
		if ((object)chunk == null || !chunk.IsBlockPresent(pos.x, pos.y, pos.z, WorldSize))
		{
			return false;
		}
		ground = chunk.GroundAt(pos, WorldSize);
		return true;
	}

	public void EnsureChunksThroughDepth(int depth)
	{
		int num = groundData.startChunkIndex + groundData.chunks.Count;
		int num2 = Mathf.Max(0, depth) / 16;
		for (int i = num; i <= num2; i++)
		{
			ChunkAt(i * 16);
		}
	}

	public ref GroundData.Ground GroundAt(int x, int y, int depth)
	{
		GroundData.Chunk chunk = ChunkAt(depth);
		if (chunk == null)
		{
			return ref GroundData.defaultGround;
		}
		return ref chunk.GroundAt(x, y, depth, WorldSize);
	}

	public ref GroundData.Ground GroundAt(int x, int y)
	{
		return ref GroundAt(x, y, CellAt(x, y).depth);
	}

	public ref GroundData.Ground GroundAt(Vector2Int pos)
	{
		return ref GroundAt(pos.x, pos.y, CellAt(pos).depth);
	}

	public ref GroundData.Ground GroundAt(Vector2Int pos, int depth)
	{
		return ref GroundAt(pos.x, pos.y, depth);
	}

	public ref GroundData.Ground GroundAt(Vector3Int pos)
	{
		return ref GroundAt(pos.x, pos.y, pos.z);
	}

	public Vector3Int FindClosestOreHamiltonDistance(Vector3Int pos, GroundSO oreToFind)
	{
		return FindClosestOre(pos, oreToFind, (Vector3Int v1, Vector3Int v2) => HeightmapBasedHamiltonDist(v1, v2));
	}

	private int HeightmapBasedHamiltonDist(Vector3Int from, Vector3Int to)
	{
		return Math.Abs(to.x - from.x) + Math.Abs(to.y - from.y) + to.z - CellAt(to.x, to.y).depth;
	}

	public Vector3Int FindClosestOreEuclideanDistance(Vector3Int pos, GroundSO oreToFind)
	{
		return FindClosestOre(pos, oreToFind, (Vector3Int v1, Vector3Int v2) => (v1 - v2).magnitude);
	}

	public Vector3Int FindClosestOre(Vector3Int pos, GroundSO oreToFind, Func<Vector3Int, Vector3Int, double> distanceFunction)
	{
		Vector3Int result = new Vector3Int(-1, -1, -1);
		double num = double.PositiveInfinity;
		int num2 = MathUtil.FloorDiv(pos.z, 16);
		int num3 = Math.Max(num2 - (int)Math.Ceiling(2.0), 0);
		int num4 = num2 + (int)Math.Ceiling(2.0);
		for (int i = num3; i <= num4; i++)
		{
			GroundData.Chunk chunk = ChunkAt(i * 16);
			if ((object)chunk == null || !chunk.oreCache.TryGetValue(oreToFind.objectName, out var value))
			{
				continue;
			}
			foreach (Vector3Int item in value)
			{
				if (item.z < chunk.startingDepth || item.z >= chunk.startingDepth + 16)
				{
					throw new InvalidOperationException();
				}
				if (chunk.IsBlockPresent(item.x, item.y, item.z, WorldSize) && !(GroundAt(item.x, item.y, item.z).groundSo != oreToFind))
				{
					double num5 = distanceFunction(pos, item);
					if (!(num5 > 32.0) && num5 < num)
					{
						num = num5;
						result = new Vector3Int(item.x, item.y, item.z);
					}
				}
			}
		}
		return result;
	}

	public bool Raycast(Ray ray, Matrix4x4 sceneScale, out Vector3Int blockPosition, out Vector3 localPosition, int maxDepth = 2147483637)
	{
		Matrix4x4 inverse = sceneScale.inverse;
		ray.origin = inverse.MultiplyPoint(ray.origin);
		ray.direction = inverse.MultiplyVector(ray.direction);
		ray.origin = new Vector3(0f - ray.origin.x, ray.origin.y, 0f - ray.origin.z);
		ray.origin += new Vector3(0.5f, 0.5f, 0f);
		ray.direction = new Vector3(0f - ray.direction.x, ray.direction.y, 0f - ray.direction.z);
		Vector3Int vector3Int = new Vector3Int(Mathf.FloorToInt(ray.origin.x), Mathf.FloorToInt(ray.origin.y), Mathf.FloorToInt(ray.origin.z));
		float num = 0f;
		Vector3 normalized = ray.direction.normalized;
		int num2 = ((normalized.x >= 0f) ? 1 : (-1));
		int num3 = ((normalized.y >= 0f) ? 1 : (-1));
		int num4 = ((normalized.z >= 0f) ? 1 : (-1));
		float num5 = ((normalized.x == 0f) ? float.PositiveInfinity : Mathf.Abs(1f / normalized.x));
		float num6 = ((normalized.y == 0f) ? float.PositiveInfinity : Mathf.Abs(1f / normalized.y));
		float num7 = ((normalized.z == 0f) ? float.PositiveInfinity : Mathf.Abs(1f / normalized.z));
		float num8 = ((normalized.x >= 0f) ? ((float)(vector3Int.x + 1) - ray.origin.x) : (ray.origin.x - (float)vector3Int.x)) * num5;
		float num9 = ((normalized.y >= 0f) ? ((float)(vector3Int.y + 1) - ray.origin.y) : (ray.origin.y - (float)vector3Int.y)) * num6;
		float num10 = ((normalized.z >= 0f) ? ((float)(vector3Int.z + 1) - ray.origin.z) : (ray.origin.z - (float)vector3Int.z)) * num7;
		for (int i = 0; i < 100; i++)
		{
			if (IsWithinBounds(vector3Int))
			{
				GroundData.Chunk chunk = groundData.ChunkAt(vector3Int.z);
				if ((object)chunk != null && chunk.IsBlockPresent(vector3Int.x, vector3Int.y, vector3Int.z, WorldSize))
				{
					blockPosition = vector3Int;
					localPosition = ray.origin - new Vector3(0.5f, 0.5f, 0f) + num * normalized;
					return true;
				}
			}
			float num11 = Mathf.Min(num8, num9, num10);
			if (num11 == num8)
			{
				vector3Int.x += num2;
				num = num8;
				num8 += num5;
				continue;
			}
			if (num11 == num9)
			{
				vector3Int.y += num3;
				num = num9;
				num9 += num6;
				continue;
			}
			vector3Int.z += num4;
			num = num10;
			num10 += num7;
			if (vector3Int.z >= maxDepth)
			{
				break;
			}
		}
		blockPosition = default(Vector3Int);
		localPosition = default(Vector3);
		return false;
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
				Entity entity = CellAt(j, i).entity;
				if (entity != null)
				{
					stringBuilder.Append(entity.objectSO.objectName.First());
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
public class GroundData
{
	public record Chunk
	{
		public int startingDepth;

		public System.Random random;

		public Ground[] tiles;

		public BitSet blockPresence;

		public List<GroundFeature.GeneratedFeature> features;

		public Dictionary<string, List<Vector3Int>> oreCache = new Dictionary<string, List<Vector3Int>>();

		public static Chunk CreateEmpty(int chunkIndex, Vector2Int sizexy)
		{
			Chunk chunk = new Chunk
			{
				startingDepth = chunkIndex * 16,
				tiles = new Ground[sizexy.x * sizexy.y * 16]
			};
			GroundSO ground = ResourceManager.GetGround("dirt");
			for (int i = 0; i < chunk.tiles.Length; i++)
			{
				chunk.tiles[i].groundSo = ground;
			}
			chunk.InitializeBlockPresence(isPresent: false);
			return chunk;
		}

		public Chunk(Chunk other)
		{
			oreCache = new Dictionary<string, List<Vector3Int>>();
			startingDepth = other.startingDepth;
			tiles = new Ground[other.tiles.Length];
			Array.Copy(other.tiles, tiles, other.tiles.Length);
			blockPresence = ((other.blockPresence == null) ? null : new BitSet(other.blockPresence));
			features = other.features;
		}

		public void CopyTo(Chunk other)
		{
			other.startingDepth = startingDepth;
			foreach (var (key, collection) in oreCache)
			{
				other.oreCache[key] = new List<Vector3Int>();
				other.oreCache[key].AddRange(collection);
			}
			if (other.tiles == null || other.tiles.Length != tiles.Length)
			{
				other.tiles = new Ground[tiles.Length];
			}
			Array.Copy(tiles, other.tiles, tiles.Length);
			if (blockPresence == null)
			{
				other.blockPresence = null;
			}
			else if (other.blockPresence == null || other.blockPresence.Length != blockPresence.Length)
			{
				other.blockPresence = new BitSet(blockPresence);
			}
			else
			{
				other.blockPresence.SetAll(value: false);
				other.blockPresence.Or(blockPresence);
			}
			other.features = features;
		}

		public void InitializeBlockPresence(bool isPresent)
		{
			blockPresence = new BitSet(tiles.Length, isPresent);
		}

		public bool IsBlockPresent(int index)
		{
			return blockPresence?[index] ?? ((object)tiles[index].groundSo != null);
		}

		public bool IsBlockPresent(int x, int y, int depth, Vector2Int sizexy)
		{
			return IsBlockPresent(TileIndex(x, y, depth, sizexy));
		}

		public void SetBlockPresent(int x, int y, int depth, Vector2Int sizexy, bool isPresent)
		{
			EnsureBlockPresence();
			blockPresence[TileIndex(x, y, depth, sizexy)] = isPresent;
		}

		public bool IsEmpty()
		{
			if (blockPresence == null)
			{
				return true;
			}
			return !blockPresence.HasAnySet();
		}

		private void EnsureBlockPresence()
		{
			if (blockPresence == null)
			{
				blockPresence = new BitSet(tiles.Length);
				for (int i = 0; i < tiles.Length; i++)
				{
					blockPresence[i] = (object)tiles[i].groundSo != null;
				}
			}
		}

		private int TileIndex(int x, int y, int depth, Vector2Int sizexy)
		{
			return x + sizexy.x * (y + sizexy.y * (depth - startingDepth));
		}

		public ref Ground GroundAt(Vector3Int pos, Vector2Int sizexy)
		{
			return ref GroundAt(pos.x, pos.y, pos.z, sizexy);
		}

		public ref Ground GroundAt(int x, int y, int depth, Vector2Int sizexy)
		{
			return ref tiles[TileIndex(x, y, depth, sizexy)];
		}

		public Chunk()
		{
		}
	}

	public struct Ground
	{
		public GroundSO groundSo;

		public int hardness;

		public int stability;

		public Ground(GroundSO fromGroundSo)
		{
			groundSo = fromGroundSo;
			hardness = fromGroundSo.maxHardness;
			stability = fromGroundSo.stability;
		}

		public Ground(GroundSO fromGroundSo, int overrideHardness, int overrideStability)
		{
			groundSo = fromGroundSo;
			hardness = overrideHardness;
			stability = overrideStability;
		}

		public Color GetColor()
		{
			return groundSo.colorGradient.Evaluate((float)hardness / 10f);
		}
	}

	public static Ground defaultGround;

	public Deque<Chunk> chunks = new Deque<Chunk>();

	public int startChunkIndex;

	public int longestObservedNumberOfChunks;

	public BitSet positionsDirty;

	public int currentGroundLoopStart;

	public readonly Vector2Int sizexy;

	public (int start, int count) ChunksRange => (start: startChunkIndex, count: chunks.Count);

	public GroundData(Vector2Int size)
	{
		sizexy = size;
		positionsDirty = new BitSet(size.x * size.y);
	}

	public GroundData(GroundData other)
	{
		for (int i = 0; i < other.chunks.Count; i++)
		{
			Chunk chunk = other.chunks[i];
			if (chunk != null)
			{
				chunks.Add(new Chunk(chunk));
			}
			else
			{
				chunks.Add(null);
			}
		}
		startChunkIndex = other.startChunkIndex;
		longestObservedNumberOfChunks = other.longestObservedNumberOfChunks;
		positionsDirty = new BitSet(other.positionsDirty);
		sizexy = other.sizexy;
	}

	public GroundData CopyWithReuse(GroundData other)
	{
		if (sizexy != other.sizexy)
		{
			return new GroundData(this);
		}
		GroundData groundData = new GroundData(sizexy);
		groundData.startChunkIndex = startChunkIndex;
		groundData.longestObservedNumberOfChunks = longestObservedNumberOfChunks;
		groundData.positionsDirty = other.positionsDirty;
		groundData.positionsDirty.SetAll(value: false);
		groundData.positionsDirty.Or(positionsDirty);
		for (int i = 0; i < chunks.Count; i++)
		{
			if (chunks[i] == null)
			{
				groundData.chunks.Add(null);
			}
			else if (i < other.chunks.Count && other.chunks[i] != null)
			{
				chunks[i].CopyTo(other.chunks[i]);
				groundData.chunks.Add(other.chunks[i]);
				other.chunks[i] = null;
			}
			else
			{
				groundData.chunks.Add(new Chunk(chunks[i]));
			}
		}
		return groundData;
	}

	public Chunk ChunkAt(int depth)
	{
		int num = MathUtil.FloorDiv(depth, 16);
		if (num < startChunkIndex || num >= startChunkIndex + chunks.Count)
		{
			return null;
		}
		return chunks[num - startChunkIndex];
	}

	public void SetChunk(int chunkIndex, Chunk chunk, bool trimEmptyTopChunks = true)
	{
		if (chunkIndex < startChunkIndex)
		{
			int num = startChunkIndex - chunkIndex;
			for (int i = 0; i < num; i++)
			{
				chunks.Insert(0, null);
			}
			startChunkIndex = chunkIndex;
		}
		else if (chunkIndex >= startChunkIndex + chunks.Count)
		{
			int num2 = chunkIndex - (startChunkIndex + chunks.Count) + 1;
			for (int j = 0; j < num2; j++)
			{
				chunks.Add(null);
			}
		}
		chunks[chunkIndex - startChunkIndex] = chunk;
		if (chunks.Count > longestObservedNumberOfChunks)
		{
			if (trimEmptyTopChunks)
			{
				TrimEmptyTopChunks();
			}
			longestObservedNumberOfChunks = Math.Max(longestObservedNumberOfChunks, chunks.Count);
		}
		positionsDirty.SetAll(value: true);
	}

	public void MarkPositionChanged(int x, int y)
	{
		if (x >= 0 && x < sizexy.x && y >= 0 && y < sizexy.y)
		{
			positionsDirty.Set(x + y * sizexy.x, value: true);
		}
	}

	public void MarkPositionChanged(Vector2Int pos)
	{
		MarkPositionChanged(pos.x, pos.y);
	}

	public void MarkPositionChanged(Vector3Int pos)
	{
		MarkPositionChanged(pos.x, pos.y);
	}

	private void TrimEmptyTopChunks()
	{
		while (chunks.Count > 0 && ((object)chunks[0] == null || chunks[0].IsEmpty()))
		{
			chunks.PopFront();
			startChunkIndex++;
		}
	}

	public ref Ground GroundAt(int x, int y, int depth)
	{
		Chunk chunk = ChunkAt(depth);
		if (chunk == null)
		{
			return ref defaultGround;
		}
		return ref chunk.GroundAt(x, y, depth, sizexy);
	}

	public ref Ground GroundAt(Vector2Int pos, int depth)
	{
		return ref GroundAt(pos.x, pos.y, depth);
	}

	public ref Ground GroundAt(Vector3Int pos)
	{
		return ref GroundAt(pos.x, pos.y, pos.z);
	}
}
public interface ISimRunner
{
	Transform SceneScaler { get; }

	Logger Logger { get; }

	int RenderLayer { get; }

	Vector3 PiggyBankPosition { get; }

	double TimeFactor { get; set; }

	bool StepByStepMode { get; set; }

	int HarvestFactor { get; }

	bool RecordsAchievements { get; }

	EDlcMask InstalledDlcs { get; }

	RenderPackage GetRenderPackage();

	void ScheduleLeaderboardStart(MainSim.LeaderboardStartArgs startArgs);

	void PlaySound(SoundEffectType sound, Vector2Int farmPos);

	void PlayEffect(VFXType effect, Vector3 localPos, bool changeColor = false, Color color = default(Color), string text = null, float lifetime = 0f, float crumblePushAngle = 0f);

	void CollectItemEffect(int item, Vector3 localPos);

	void CrumbleEffect(Vector3Int blockPos);

	void SlideBlockEffect(Vector2Int sourcePos, Vector2Int targetPos);

	void SlideAndPopBlockEffect(Vector2Int sourcePos, Vector2Int targetPos, int targetDepth, int lifetimeCount);

	void DelayedPopBlockEffect(Vector3Int blockPos, float delay, Vector3 popVelocity);

	void BlinkEffect(Node node);

	void SetDirty();
}
public class ItemEffect : MonoBehaviour
{
	[SerializeField]
	private MeshFilter meshFilter;

	public void Setup(Mesh mesh)
	{
		meshFilter.mesh = mesh;
	}
}
public class MainSim : MonoBehaviour, ISimRunner
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

		public readonly EDlcType dlcType;

		public int seed;

		public bool singleDrone;

		public bool fullyGenerateUnderground;

		public List<string> whitelistedGroundFeatureUnlocks;

		public List<int> pretendedFeatureChunks;

		public List<int> pretendedChunkDepths;

		public LeaderboardStartArgs(string fileName, IEnumerable<string> unlocks, ItemBlock items, List<KeyValuePair<string, IPyObject>> globals, string leaderboardName, string steamLeaderboardName, LeaderboardType leaderboardType, bool fullyGenerateUnderground, EDlcType dlcType, int seed = -1, bool singleDrone = false, List<string> whitelistedGroundFeatureUnlocks = null, List<int> pretendedFeatureChunks = null, List<int> pretendedChunkDepths = null)
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
			this.fullyGenerateUnderground = fullyGenerateUnderground;
			this.dlcType = dlcType;
			this.whitelistedGroundFeatureUnlocks = whitelistedGroundFeatureUnlocks;
			this.pretendedFeatureChunks = pretendedFeatureChunks;
			this.pretendedChunkDepths = pretendedChunkDepths;
		}
	}

	private static MainSim _instance;

	public const float MAX_SIM_TIME_PER_FRAME = 0.2f;

	private const long MIN_LEADERBOARD_TIME = 7200000000000L;

	public PiggyBank pb;

	[SerializeField]
	private Transform sceneScaler;

	public LeaderboardManager leaderboardManager;

	public Workspace workspace;

	public WarningPopup warningPopup;

	public WarningIcon warningIcon;

	public ResearchMenu researchMenu;

	public Menu menu;

	[NonSerialized]
	public Camera mainCamera;

	public Inventory inv;

	private Logger logger;

	private ConcurrentQueue<HatSO> hatsToUnlock = new ConcurrentQueue<HatSO>();

	public int harvestFactor = 1;

	[SerializeField]
	private double timeFactor = 1.0;

	[NonSerialized]
	public Vector3Int hoveredBlock = new Vector3Int(-1, -1, -1);

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

	private RenderPackage renderPackage = new RenderPackage();

	private RenderPackage nextRenderPackage = new RenderPackage();

	private RenderPackage spareRenderPackage = new RenderPackage();

	private bool rebuildMeshesOnNextRenderPackage;

	private bool prevStepByStepMode;

	public static MainSim Inst => _instance;

	public int RenderLayer => 0;

	public Vector3 PiggyBankPosition { get; private set; }

	public Transform SceneScaler => sceneScaler;

	public Logger Logger => logger;

	public int HarvestFactor => harvestFactor;

	public bool RecordsAchievements => true;

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

	public EDlcMask InstalledDlcs => sim?.farm.installedDlcs ?? PlatformManager.InstalledDlcs;

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
		logger = new Logger();
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
		try
		{
			while (!disposed)
			{
				sim.RunNextStep(goalTime, lockSimulation, sim.leaderboardType != LeaderboardType.none);
			}
		}
		catch (ThreadAbortException)
		{
		}
		catch (Exception exception)
		{
			UnityEngine.Debug.LogException(exception);
		}
	}

	private void OnDestroy()
	{
		disposed = true;
	}

	private void Update()
	{
		Saver.ApplyCodeChanges(workspace);
		if (!RaycastMouse(out var vector3Int))
		{
			vector3Int = new Vector3Int(-1, -1, -1);
		}
		lock (lockSimulation)
		{
			PiggyBankPosition = pb.Position;
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
				FMODSoundManager.UpdateDroneParams(sim.farm.drones.Where((Drone d) => d != null).Select(delegate(Drone d)
				{
					var (item, item2) = d.GetSpeedAndPos(Time.time);
					return (speed: item, position: item2, d.GetDiggingTimeRemaining() > 0f);
				}).ToArray());
				FMODSoundManager.SetGameSpeedParam((float)(Duration.FromSeconds(0.0025) / sim.OpDuration * (double)sim.farm.drones.Where((Drone d) => d != null).Count()));
			}
			Vector3 mousePosition = Input.mousePosition;
			if (Application.isFocused && mousePosition.x >= 0f && mousePosition.y >= 0f && mousePosition.x < (float)Screen.width && mousePosition.y < (float)Screen.height && !Input.GetMouseButton(0) && !Input.GetMouseButton(1) && vector3Int != new Vector3Int(-1, -1, -1) && workspace.tooltip.CanShowTooltipImmediate() && !menu.gameObject.activeInHierarchy && !researchMenu.IsOpen)
			{
				if (vector3Int != hoveredBlock)
				{
					hoveredBlock = vector3Int;
					FMODSoundManager.PlaySound(SoundEffectType.VoxelHoverChanged, default(Vector3));
					lastHoveredTime = Time.time;
					workspace.tooltip.SetTooltipImmediate(null);
				}
				else if ((double)Time.time - lastHoveredTime > 0.4000000059604645)
				{
					hoveredBlock = vector3Int;
					if (workspace.tooltip.SetTooltipImmediate(GetHoveredTooltip()))
					{
						FMODSoundManager.PlaySound(SoundEffectType.TooltipAppeared, default(Vector3));
					}
				}
			}
			else
			{
				hoveredBlock = new Vector3Int(-1, -1, -1);
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
			float averageDepth = sim.farm.grid.ComputeAverageDepth();
			sim.farm.grid.EnsureChunksThroughDepth(DesignConstants.Inst.farmRenderer.MaxVisibleDepth(sim.farm.grid.WorldSize, averageDepth, sim.farm.grid.maxUncoveredDepth, sim.farm.IsDlcInstalled(EDlcType.Mining)));
			UpdateRenderPackage(averageDepth);
			FMODSoundManager.SetIsAboveGroundParam(renderPackage.minDepth == 0);
			sim.farm.grid.groundData.positionsDirty.SetAll(value: false);
			Monitor.Pulse(lockSimulation);
		}
	}

	public void SetupSim(IEnumerable<string> unlocks, ItemBlock items, List<SFO> loadedGrounds = null, List<SFO> loadedEntities = null, bool resetUnlocks = false)
	{
		lock (lockSimulation)
		{
			sim = new Simulation(this, PlatformManager.InstalledDlcs, unlocks, items, "", "", LeaderboardType.none, fullyGenerateUnderground: true, -1, loadedGrounds, loadedEntities, resetUnlocks);
			rebuildMeshesOnNextRenderPackage = true;
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
				IEnumerable<string> enumerable = startArgs.unlocks.Concat(Achievements.GetUnlockedHatNames(storedSim.farm.IsUnlocked));
				if (startArgs.leaderboardType != LeaderboardType.simulation)
				{
					enumerable = enumerable.Where((string s) => s != "explosive_drill");
				}
				EDlcMask dlcs = (((startArgs.leaderboardType == LeaderboardType.simulation && string.IsNullOrEmpty(startArgs.leaderboardName)) || startArgs.dlcType != EDlcType.None) ? PlatformManager.InstalledDlcs : EDlcMask.None);
				IEnumerable<string> unlocks = enumerable;
				ItemBlock items = startArgs.items;
				string leaderboardName = startArgs.leaderboardName;
				string steamLeaderboardName = startArgs.steamLeaderboardName;
				LeaderboardType leaderboardType = startArgs.leaderboardType;
				bool fullyGenerateUnderground = startArgs.fullyGenerateUnderground;
				int seed = startArgs.seed;
				List<string> whitelistedGroundFeatureUnlocks = startArgs.whitelistedGroundFeatureUnlocks;
				List<int> pretendedFeatureChunks = startArgs.pretendedFeatureChunks;
				List<int> pretendedChunkDepths = startArgs.pretendedChunkDepths;
				sim = new Simulation(this, dlcs, unlocks, items, leaderboardName, steamLeaderboardName, leaderboardType, fullyGenerateUnderground, seed, null, null, resetUnlocks: false, 200.0, 1.0, default(Vector2Int), 0, whitelistedGroundFeatureUnlocks, pretendedFeatureChunks, pretendedChunkDepths)
				{
					singleDrone = startArgs.singleDrone
				};
				rebuildMeshesOnNextRenderPackage = true;
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
		if (!workspace.codeWindows.ContainsKey(startArgs.fileName))
		{
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_file_not_found", startArgs.fileName));
		}
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
				LeaderboardType.reset => (sim.leaderboardName == "fastest_reset") ? sim.farm.IsUnlocked("leaderboard") : sim.farm.IsUnlocked("underground_leaderboard"), 
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
			int seed = Mathf.Abs(sim.randomVarious.Next() + sim.randomSunflower.Next() + sim.randomSnake.Next() + sim.randomRandom.Next() + sim.randomPumpkin.Next() + sim.randomPoly.Next() + sim.randomMaze.Next() + sim.randomCactus.Next() + sim.randomWorldGen.Next());
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
			rebuildMeshesOnNextRenderPackage = true;
		}
	}

	public void StartMainExecution(CodeWindow cw, Node syntaxTree, bool stepByStep = false)
	{
		lock (lockSimulation)
		{
			if (IsExecuting())
			{
				return;
			}
			foreach (CodeWindow value in workspace.codeWindows.Values)
			{
				value.StopExecutionMode();
			}
			activeCodeWindow = cw;
			if (activeCodeWindow != null)
			{
				activeCodeWindow.SetExecutionColor();
				activeCodeWindow.StartExecutionMode(closeErrors: false);
				if (stepByStep)
				{
					activeCodeWindow.StartStepByStepMode();
				}
				Transform obj = activeCodeWindow.transform;
				obj.SetSiblingIndex(obj.parent.childCount - 1);
			}
			Execution execution = new Execution(sim, syntaxTree, executionId);
			executionId++;
			Logger.Clear();
			sim.stepByStepMode = stepByStep;
			sim.StartProgramExecution(execution);
		}
		sim.UnlockAchievement("RUN_YOUR_FIRST_CODE");
	}

	public void StopMainExecution()
	{
		lock (lockSimulation)
		{
			bool num = sim.IsExecuting() || (storedSim?.IsExecuting() ?? false);
			if (sim.leaderboardType != LeaderboardType.none && sim.leaderboardType != LeaderboardType.simulation)
			{
				leaderboardCancelled = true;
			}
			storedSim?.StopProgramExecution();
			sim.StopProgramExecution();
			if (num)
			{
				FMODSoundManager.PlaySound(SoundEffectType.StopCodeExecution, default(Vector3));
			}
		}
	}

	public void PlaySound(SoundEffectType sound, Vector2Int farmPos)
	{
		if (TimeFactor < 2.0 && !SoundManager.IsThrottled())
		{
			SoundManager.EnqueueSound(sound, sim.farm.grid.CellToLocal(farmPos));
		}
	}

	public void PlayEffect(VFXType effect, Vector3 localPos, bool changeColor = false, Color color = default(Color), string text = null, float lifetime = 0f, float crumblePushAngle = 0f)
	{
		if (TimeFactor < 2.0)
		{
			AddVFXCall(new VFXCall(effect, localPos, changeColor, color, null, text, lifetime, crumblePushAngle));
		}
	}

	public void CollectItemEffect(int item, Vector3 localPos)
	{
		if (TimeFactor < 2.0)
		{
			AddVFXCall(new VFXCall(VFXType.moving_mesh_piggy, localPos, changeColor: false, default(Color), ResourceManager.GetItem(item).mesh, null));
		}
	}

	public void CrumbleEffect(Vector3Int blockPos)
	{
		lock (lockSimulation)
		{
			if (TimeFactor < 2.0 && DesignConstants.Inst.vfx.crumbleEffectExpectedCountLimit > 0)
			{
				nextRenderPackage.crumblingBlocks.Add(new CrumblingBlockCall
				{
					pos = blockPos
				});
			}
		}
	}

	public void SlideBlockEffect(Vector2Int sourcePos, Vector2Int targetPos)
	{
		if (TimeFactor >= 2.0)
		{
			return;
		}
		lock (lockSimulation)
		{
			nextRenderPackage.slidingBlocks.Add(new SlidingBlockCall
			{
				sourcePos = sourcePos,
				targetPos = targetPos,
				targetDepth = sim.farm.grid.CellAt(targetPos).depth,
				lifetimeCount = 1
			});
		}
	}

	public void SlideAndPopBlockEffect(Vector2Int sourcePos, Vector2Int targetPos, int targetDepth, int lifetimeCount)
	{
		if (TimeFactor >= 2.0)
		{
			return;
		}
		lock (lockSimulation)
		{
			nextRenderPackage.slidingBlocks.Add(new SlidingBlockCall
			{
				sourcePos = sourcePos,
				targetPos = targetPos,
				targetDepth = targetDepth,
				lifetimeCount = Mathf.Max(1, lifetimeCount),
				popEffect = true
			});
		}
	}

	public void DelayedPopBlockEffect(Vector3Int blockPos, float delay, Vector3 popVelocity)
	{
		if (TimeFactor >= 2.0)
		{
			return;
		}
		lock (lockSimulation)
		{
			nextRenderPackage.slidingBlocks.Add(new SlidingBlockCall
			{
				sourcePos = (Vector2Int)blockPos,
				targetPos = (Vector2Int)blockPos,
				targetDepth = blockPos.z,
				lifetimeCount = 1,
				popEffect = true,
				startAtTarget = true,
				overrideDuration = true,
				duration = delay,
				overridePopVelocity = true,
				popVelocity = popVelocity
			});
		}
	}

	private void AddVFXCall(VFXCall vfxCall)
	{
		lock (lockSimulation)
		{
			nextRenderPackage.vfxCalls.Add(vfxCall);
		}
	}

	public void BlinkEffect(Node node)
	{
		BlinkManager.Inst.EnqueueBlink(node);
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

	public bool IsPaused()
	{
		lock (lockSimulation)
		{
			return sim.Paused;
		}
	}

	public List<string> GetSerializedUnlocks()
	{
		lock (lockSimulation)
		{
			return sim.farm.SerializeUnlocks();
		}
	}

	private void UpdateRenderPackage(float averageDepth)
	{
		lock (lockSimulation)
		{
			nextRenderPackage.droneMeshes.Clear();
			foreach (Drone item in sim.farm.drones.Where((Drone d) => d != null))
			{
				item.TryUpdateHeight();
				nextRenderPackage.droneMeshes.Add((item.hat.hatSO, IsExecuting() && sim.farm.mainDroneId == item.DroneId && (sim.Paused || StepByStepMode), item.GetTransform(), item.GetDiggingTimeRemaining()));
			}
			Drone drone = sim.farm.drones[sim.farm.mainDroneId];
			int depth = sim.farm.grid.CellAt(drone.pos).depth;
			nextRenderPackage.dronePos = new Vector3Int(drone.pos.x, drone.pos.y, depth);
			nextRenderPackage.mainDroneLocalPosition = drone.GetTransform().GetPosition();
			nextRenderPackage.farmMeshes.Clear();
			Span<GridManager.Cell> span = sim.farm.grid.cells.AsSpan();
			for (int num = 0; num < span.Length; num++)
			{
				ref GridManager.Cell reference = ref span[num];
				if (reference.entity == null)
				{
					continue;
				}
				foreach (var mesh in reference.entity.GetMeshes())
				{
					nextRenderPackage.farmMeshes.Add((mesh.Item1, mesh.Item2));
				}
			}
			if (nextRenderPackage.cellDepths == null || nextRenderPackage.cellDepths.Length != sim.farm.grid.cells.Length)
			{
				nextRenderPackage.cellDepths = new int[sim.farm.grid.cells.Length];
			}
			if (nextRenderPackage.cellWaterVolumes == null || nextRenderPackage.cellWaterVolumes.Length != sim.farm.grid.cells.Length)
			{
				nextRenderPackage.cellWaterVolumes = new double[sim.farm.grid.cells.Length];
			}
			for (int num2 = 0; num2 < sim.farm.grid.cells.Length; num2++)
			{
				nextRenderPackage.cellDepths[num2] = sim.farm.grid.cells[num2].depth;
				nextRenderPackage.cellWaterVolumes[num2] = sim.farm.grid.cells[num2].waterVolume;
			}
			if (nextRenderPackage.groundData == null)
			{
				nextRenderPackage.groundData = new GroundData(sim.farm.grid.groundData);
			}
			else
			{
				nextRenderPackage.groundData = sim.farm.grid.groundData.CopyWithReuse(nextRenderPackage.groundData);
			}
			nextRenderPackage.averageDepth = sim.farm.grid.ComputeAverageDepth();
			nextRenderPackage.rebuildMeshes = rebuildMeshesOnNextRenderPackage;
			nextRenderPackage.minDepth = int.MaxValue;
			nextRenderPackage.maxDepth = int.MinValue;
			for (int num3 = 0; num3 < nextRenderPackage.cellDepths.Length; num3++)
			{
				nextRenderPackage.minDepth = Math.Min(nextRenderPackage.minDepth, nextRenderPackage.cellDepths[num3]);
				nextRenderPackage.maxDepth = Math.Max(nextRenderPackage.maxDepth, nextRenderPackage.cellDepths[num3]);
			}
			RenderPackage renderPackage = nextRenderPackage;
			RenderPackage renderPackage2 = spareRenderPackage;
			RenderPackage renderPackage3 = this.renderPackage;
			this.renderPackage = renderPackage;
			nextRenderPackage = renderPackage2;
			spareRenderPackage = renderPackage3;
			rebuildMeshesOnNextRenderPackage = false;
			nextRenderPackage.vfxCalls.Clear();
			nextRenderPackage.crumblingBlocks.Clear();
			nextRenderPackage.slidingBlocks.Clear();
		}
	}

	public RenderPackage GetRenderPackage()
	{
		return renderPackage;
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

	public bool Raycast(Ray ray, out Vector3 blockPosition, out Vector3 hitPosition, int? maxDepth = null)
	{
		Matrix4x4 localToWorldMatrix = sceneScaler.localToWorldMatrix;
		lock (lockSimulation)
		{
			int maxDepth2 = maxDepth ?? (sim.farm.grid.maxUncoveredDepth + 1);
			if (!sim.farm.grid.Raycast(ray, localToWorldMatrix, out var blockPosition2, out var localPosition, maxDepth2))
			{
				blockPosition = default(Vector3);
				hitPosition = default(Vector3);
				return false;
			}
			blockPosition = localToWorldMatrix.MultiplyPoint(GridManager.CellToLocal(blockPosition2));
			hitPosition = localToWorldMatrix.MultiplyPoint(GridManager.CellToLocal(localPosition));
		}
		return true;
	}

	private bool RaycastMouse(out Vector3Int hoveredBlock)
	{
		lock (lockSimulation)
		{
			float averageDepth = sim.farm.grid.ComputeAverageDepth();
			int maxDepth = (InstalledDlcs.HasFlag(EDlcMask.Minig) ? DesignConstants.Inst.farmRenderer.MaxVisibleDepth(sim.farm.grid.WorldSize, averageDepth, sim.farm.grid.maxUncoveredDepth, miningDlc: true) : (sim.farm.grid.maxUncoveredDepth + 1));
			Ray ray = mainCamera.ScreenPointToRay(Input.mousePosition);
			Vector3 localPosition;
			return sim.farm.grid.Raycast(ray, sceneScaler.localToWorldMatrix, out hoveredBlock, out localPosition, maxDepth);
		}
	}

	private TooltipInfo GetHoveredTooltip()
	{
		if (!sim.farm.grid.IsWithinBounds(hoveredBlock))
		{
			hoveredBlock = new Vector3Int(-1, -1, -1);
			return null;
		}
		ItemBlock itemBlock = null;
		ItemBlock itemBlock2 = null;
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.Append("`x = ").Append(hoveredBlock.x).Append(", y = ")
			.Append(hoveredBlock.y)
			.Append(", z = ")
			.Append(-hoveredBlock.z)
			.Append("`")
			.Append("\n\n");
		GridManager.Cell cell = sim.farm.grid.CellAt(hoveredBlock.x, hoveredBlock.y);
		Entity entity = cell.entity;
		Duration collectionDuration;
		if (cell.depth == hoveredBlock.z && entity != null)
		{
			stringBuilder.Append("### `").Append(CodeUtilities.ToNiceString(entity.objectSO)).Append("`\n");
			stringBuilder.Append(Localizer.Localize(entity.objectSO.description)).Append("\n\n");
			if (entity is Growable growable && entity.objectSO.className != "Apple")
			{
				object[] array = new object[2];
				collectionDuration = growable.GrowTime;
				array[0] = new PyNumber(collectionDuration.Seconds);
				array[1] = new PyNumber(growable.GrownPercent * 100.0);
				stringBuilder.Append(CodeUtilities.LocalizeAndFormat("runtime_growable_tooltip", array)).Append("\n\n");
			}
			IPyObject pyObject = entity.Measure();
			if (pyObject != null && !(pyObject is PyNone) && IsUnlocked("measure"))
			{
				stringBuilder.Append("`measure(): " + CodeUtilities.ToNiceString(pyObject) + "`").Append("\n\n");
			}
			itemBlock = entity.GetYield();
			if (itemBlock != null && !itemBlock.IsEmpty())
			{
				stringBuilder.Append(Localizer.Localize("runtime_entity_tooltip")).Append("\n");
			}
		}
		if (sim.farm.grid.TryGetExistingGroundAt(hoveredBlock, out var ground))
		{
			stringBuilder.Append("### `").Append(CodeUtilities.ToNiceString(ground.groundSo)).Append("`\n");
			stringBuilder.Append(Localizer.Localize(ground.groundSo.description)).Append("\n\n");
			GridController controller = ground.groundSo.GetController(sim.farm.grid);
			if (controller != null && (hoveredBlock.z != cell.depth || entity == null))
			{
				IPyObject pyObject2 = controller.Measure(null, hoveredBlock);
				if (pyObject2 != null && !(pyObject2 is PyNone) && IsUnlocked("measure"))
				{
					stringBuilder.Append("`measure(): " + CodeUtilities.ToNiceString(pyObject2) + "`").Append("\n\n");
				}
			}
			bool flag = InstalledDlcs.HasFlag(EDlcMask.Minig);
			if (flag)
			{
				stringBuilder.Append(CodeUtilities.LocalizeAndFormat("runtime_ground_hardness_tooltip", new PyNumber(ground.hardness))).Append("\n").Append(CodeUtilities.LocalizeAndFormat("runtime_ground_stability_tooltip", new PyNumber(ground.stability)))
					.Append("\n");
			}
			stringBuilder.Append(CodeUtilities.LocalizeAndFormat("runtime_ground_water_tooltip", new PyNumber(cell.waterVolume))).Append("\n\n");
			itemBlock2 = (flag ? ground.groundSo.GetDrops(sim.farm, out collectionDuration) : null);
			if (itemBlock2 != null && !itemBlock2.IsEmpty())
			{
				stringBuilder.Append(Localizer.Localize("runtime_ground_tooltip")).Append("\n");
			}
			if (controller != null)
			{
				ItemBlock hoveredTooltip = controller.GetHoveredTooltip(stringBuilder, hoveredBlock, in ground);
				if (itemBlock2 == null)
				{
					itemBlock2 = hoveredTooltip;
				}
				else if (hoveredTooltip != null)
				{
					itemBlock2.Add(hoveredTooltip);
				}
			}
		}
		return new TooltipInfo(stringBuilder.ToString(), 0.2f)
		{
			itemBlock = itemBlock,
			groundItemBlock = itemBlock2
		};
	}

	public void SetDirty()
	{
		dirty = true;
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
	private Transform piggyMesh;

	[SerializeField]
	private Camera cam;

	private Stack<ItemEffect> itemPool = new Stack<ItemEffect>();

	private List<ActiveEffect> activeEffects = new List<ActiveEffect>();

	private ISimRunner simRunner;

	private Vector3 velLocal;

	private float heightOffset;

	private ConcurrentQueue<(Mesh, Vector3, int)> collectQueue = new ConcurrentQueue<(Mesh, Vector3, int)>();

	public Vector3 Position => piggyMesh.localPosition;

	private Transform SceneScaler => simRunner?.SceneScaler ?? base.transform.parent;

	private void Awake()
	{
		simRunner = GetComponentInParent<ISimRunner>();
		if (simRunner == null)
		{
			UnityEngine.Debug.LogError("PiggyBank requires a component in its parent hierarchy that implements ISimRunner.");
		}
		heightOffset = piggyMesh.localPosition.z;
	}

	private void Update()
	{
		RenderPackage renderPackage = simRunner?.GetRenderPackage();
		if ((object)renderPackage != null)
		{
			Ray ray = cam.ScreenPointToRay(Input.mousePosition);
			Vector3 position = (Vector3)(-(Vector2)ray.direction * ((ray.origin.z - piggyMesh.position.z) / ray.direction.z)) + ray.origin;
			position = SceneScaler.InverseTransformPoint(position);
			position.z = piggyMesh.localPosition.z;
			DesignConstants.PiggyBankDesignConstants piggyBank = DesignConstants.Inst.piggyBank;
			bool flag = (piggyMesh.localPosition - position).magnitude < piggyBank.maxDistance;
			Vector3 vector = (flag ? position : new Vector3(0f, 0f, 0f)) - piggyMesh.localPosition;
			vector.z = 0f;
			velLocal += vector * Time.deltaTime * (flag ? piggyBank.accelerationTowardsCursor : piggyBank.acceleration);
			velLocal += CalculateObstacleDodge(renderPackage, piggyBank) * Time.deltaTime;
			velLocal = velLocal.normalized * Mathf.Min(velLocal.magnitude, piggyBank.maxSpeed);
			piggyMesh.localPosition += velLocal * Time.deltaTime;
			float num = GridManager.CellToLocal(new Vector3(0f, 0f, renderPackage.averageDepth)).z + piggyBank.hoverHeight;
			float num2 = Mathf.Pow(Mathf.Abs(num - heightOffset), piggyBank.zFollowSpeedPower) * piggyBank.zFollowSpeedFactor;
			heightOffset += Mathf.Sign(num - heightOffset) * num2 * Time.deltaTime;
			piggyMesh.localPosition = new Vector3(piggyMesh.localPosition.x, piggyMesh.localPosition.y, heightOffset);
			Quaternion to = Quaternion.AngleAxis(Mathf.Atan2(velLocal.y, velLocal.x) * 57.29578f + 180f, Vector3.forward);
			piggyMesh.localRotation = Quaternion.RotateTowards(piggyMesh.localRotation, to, piggyBank.maxRotation * Time.deltaTime);
		}
	}

	private Vector3 CalculateObstacleDodge(RenderPackage renderPackage, DesignConstants.PiggyBankDesignConstants design)
	{
		if (renderPackage.cellDepths == null || renderPackage.groundData == null)
		{
			return Vector3.zero;
		}
		Vector2Int sizexy = renderPackage.groundData.sizexy;
		if (renderPackage.cellDepths.Length != sizexy.x * sizexy.y)
		{
			return Vector3.zero;
		}
		Vector2Int vector2Int = GridManager.LocalToCell(piggyMesh.localPosition + new Vector3(0.5f, 0.5f, 0.5f));
		Vector2 vector = piggyMesh.localPosition;
		Vector2 zero = Vector2.zero;
		float averageDepth = renderPackage.averageDepth;
		float num = Mathf.Max(0.01f, design.obstacleDodgeRadius);
		int num2 = Mathf.CeilToInt(num);
		for (int i = -num2; i <= num2; i++)
		{
			for (int j = -num2; j <= num2; j++)
			{
				Vector2Int vector2Int2 = vector2Int + new Vector2Int(i, j);
				if (vector2Int2.x < 0 || vector2Int2.y < 0 || vector2Int2.x >= sizexy.x || vector2Int2.y >= sizexy.y)
				{
					continue;
				}
				int num3 = renderPackage.cellDepths[vector2Int2.x + vector2Int2.y * sizexy.x];
				float num4 = averageDepth - (float)num3;
				if (num4 <= 0f)
				{
					continue;
				}
				Vector3 vector2 = GridManager.CellToLocal(new Vector3(vector2Int2.x, vector2Int2.y, averageDepth));
				Vector2 vector3 = vector - new Vector2(vector2.x, vector2.y);
				float magnitude = vector3.magnitude;
				if (!(magnitude > num))
				{
					if (magnitude < 0.001f)
					{
						vector3 = ((velLocal.sqrMagnitude > 0.001f) ? new Vector2(velLocal.x, velLocal.y).normalized : Vector2.right);
					}
					else
					{
						vector3 /= magnitude;
					}
					float num5 = 1f - Mathf.Clamp01(magnitude / num);
					zero += vector3 * num4 * num5;
				}
			}
		}
		return new Vector3(zero.x, zero.y, 0f) * design.obstacleDodgeAcceleration;
	}
}
public record RenderPackage
{
	public List<(Mesh mesh, Matrix4x4 transform)> farmMeshes = new List<(Mesh, Matrix4x4)>();

	public List<(HatSO hat, bool highlight, Matrix4x4 transform, float diggingTimeRemaining)> droneMeshes = new List<(HatSO, bool, Matrix4x4, float)>();

	public List<VFXCall> vfxCalls = new List<VFXCall>();

	public List<CrumblingBlockCall> crumblingBlocks = new List<CrumblingBlockCall>();

	public List<SlidingBlockCall> slidingBlocks = new List<SlidingBlockCall>();

	public int[] cellDepths;

	public double[] cellWaterVolumes;

	public Vector3Int dronePos;

	public Vector3 mainDroneLocalPosition;

	public GroundData groundData;

	public bool rebuildMeshes;

	public int minDepth;

	public int maxDepth;

	public float averageDepth;
}
public struct CrumblingBlockCall
{
	public Vector3Int pos;
}
public struct SlidingBlockCall
{
	public Vector2Int sourcePos;

	public Vector2Int targetPos;

	public int targetDepth;

	public int lifetimeCount;

	public bool popEffect;

	public bool startAtTarget;

	public bool overrideDuration;

	public float duration;

	public bool overridePopVelocity;

	public Vector3 popVelocity;
}
public class Simulation
{
	public class Timer
	{
		public Action func;

		public bool stopped;
	}

	public const double BASE_OP_DURATION = 0.0025;

	public readonly double actionOps;

	public readonly double operationOps;

	public Farm farm;

	private Execution execution;

	public ISimRunner simRunner;

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

	public System.Random randomWorldGen;

	public System.Random randomBamboo;

	public readonly string leaderboardName;

	public readonly string steamLeaderboardName;

	public readonly LeaderboardType leaderboardType;

	public bool singleDrone;

	public readonly bool fullyGenerateUnderground;

	public readonly bool plantingDisabledDueToLeaderboard;

	public double SpeedFactor { get; private set; } = 1.0;

	public Duration OpDuration { get; private set; } = Duration.FromSeconds(0.0025);

	public double DiggingSpeedFactor { get; private set; } = 1.0;

	public Duration CurrentTime { get; private set; }

	public bool Paused { get; set; }

	public bool RecordsAchievements => ShouldRecordAchievements(simRunner, leaderboardType);

	public Execution Execution => execution;

	public static bool ShouldRecordAchievements(ISimRunner simRunner, LeaderboardType leaderboardType)
	{
		if (simRunner != null && simRunner.RecordsAchievements)
		{
			return leaderboardType == LeaderboardType.none;
		}
		return false;
	}

	public void UnlockAchievement(string achievement)
	{
		if (RecordsAchievements)
		{
			Achievements.UnlockAchievement(achievement);
		}
	}

	public void IncrementAchievementStat(string statName, int increment)
	{
		if (RecordsAchievements)
		{
			Achievements.IncrementStat(statName, increment);
		}
	}

	public void RecordCollectedItem(int itemId, double number, Duration collectionDuration, bool trackRate, bool trackTotal)
	{
		if (RecordsAchievements)
		{
			Achievements.CollectItem(itemId, number, CurrentTime, collectionDuration, trackRate, trackTotal);
		}
	}

	public Simulation(ISimRunner simRunner, EDlcMask dlcs, IEnumerable<string> unlocks, ItemBlock items, string leaderboardName, string steamLeaderboardName, LeaderboardType leaderboardType, bool fullyGenerateUnderground, int seed = -1, List<SFO> loadedGrounds = null, List<SFO> loadedEntities = null, bool resetUnlocks = false, double actionOps = 200.0, double operationOps = 1.0, Vector2Int worldSizeOverride = default(Vector2Int), int startingChunk = 0, List<string> whitelistedGroundFeatureUnlocks = null, List<int> pretendedFeatureChunks = null, List<int> pretendedChunkDepths = null)
	{
		int seed2 = seed;
		base..ctor();
		Simulation simulation = this;
		this.actionOps = actionOps;
		this.operationOps = operationOps;
		this.simRunner = simRunner;
		this.leaderboardName = leaderboardName;
		this.steamLeaderboardName = steamLeaderboardName;
		this.leaderboardType = leaderboardType;
		this.fullyGenerateUnderground = fullyGenerateUnderground;
		plantingDisabledDueToLeaderboard = leaderboardType == LeaderboardType.farm_resources && fullyGenerateUnderground && !new string[2] { "rice", "rice_single" }.Contains(leaderboardName);
		CurrentTime = new Duration(0L);
		if (seed2 >= 0)
		{
			random = new System.Random(seed2);
		}
		else
		{
			random = new System.Random();
		}
		bool secureRandom = leaderboardType == LeaderboardType.reset || leaderboardType == LeaderboardType.farm_resources;
		randomVarious = NewCropRandom();
		randomMaze = NewCropRandom();
		randomSnake = NewCropRandom();
		randomCactus = NewCropRandom();
		randomSunflower = NewCropRandom();
		randomPumpkin = NewCropRandom();
		randomPoly = NewCropRandom();
		randomRandom = NewCropRandom();
		randomWorldGen = new System.Random(Helper.JustSha256It(random));
		randomBamboo = NewCropRandom();
		farm = new Farm(this, dlcs, unlocks, items, resetUnlocks, worldSizeOverride, startingChunk, fullyGenerateUnderground, whitelistedGroundFeatureUnlocks, pretendedFeatureChunks, pretendedChunkDepths);
		ChangeExecutionSpeed(farm.MaxSpeedFactor());
		ChangeDiggingSpeed(farm.GetDiggingSpeed());
		System.Random NewCropRandom()
		{
			if (!secureRandom)
			{
				return new System.Random(Helper.JustSha256It(random));
			}
			return new BufferedCryptoRandom(seed2);
		}
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
			if (farm.grid.SizeLimit > 0)
			{
				farm.grid.SizeLimit = 0;
				farm.drones[farm.mainDroneId].UpdateHeight(0.0);
			}
			farm.RemoveSpawnedDrones();
			stepByStepMode = false;
			Paused = false;
			simRunner.Logger.Close();
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

	public void ChangeDiggingSpeed(double speedFactor)
	{
		DiggingSpeedFactor = speedFactor;
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
public class UISim : MonoBehaviour, ISimRunner
{
	private static UISim _instance;

	public PiggyBank pb;

	[SerializeField]
	private Transform sceneScaler;

	private Logger logger;

	[SerializeField]
	private Camera UIFarmCamera;

	private Inventory activeInventory;

	[SerializeField]
	private double timeFactor = 1.0;

	private Simulation sim;

	private Duration goalTime;

	private object lockSimulation = new object();

	private volatile bool disposed;

	private RenderPackage renderPackage;

	private RenderPackage nextRenderPackage = new RenderPackage();

	private RenderPackage spareRenderPackage = new RenderPackage();

	private CodeExample codeExample;

	private bool mainExecutionStarted;

	private ProgramState mainProgramState;

	public static UISim Inst => _instance;

	public int RenderLayer => 7;

	public Vector3 PiggyBankPosition { get; private set; }

	public Transform SceneScaler => sceneScaler;

	public EDlcMask InstalledDlcs { get; private set; }

	public Logger Logger => logger;

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

	public bool StepByStepMode { get; set; }

	public int HarvestFactor => 1;

	public bool RecordsAchievements => false;

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
		logger = new Logger(writeToOutputFile: false);
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
			sim?.RunNextStep(goalTime, lockSimulation);
		}
	}

	private void OnDestroy()
	{
		disposed = true;
	}

	private void Update()
	{
		if (sim == null)
		{
			return;
		}
		lock (lockSimulation)
		{
			PiggyBankPosition = pb.Position;
			float num = Mathf.Min(Time.deltaTime, 0.2f);
			goalTime = sim.CurrentTime + Duration.FromSeconds((double)num * TimeFactor);
			if (sim.IsExecuting())
			{
				codeExample?.SetExecutionColor();
			}
			else if (codeExample != null && mainExecutionStarted)
			{
				if (codeExample.settings.print_last_result)
				{
					PrintLastResult();
				}
				codeExample.UnsetExecutionVisuals();
				codeExample = null;
				mainExecutionStarted = false;
				mainProgramState = null;
			}
			float averageDepth = sim.farm.grid.ComputeAverageDepth();
			sim.farm.grid.EnsureChunksThroughDepth(DesignConstants.Inst.farmRenderer.MaxVisibleDepth(sim.farm.grid.WorldSize, averageDepth, sim.farm.grid.maxUncoveredDepth, sim.farm.IsDlcInstalled(EDlcType.Mining)));
			UpdateRenderPackage(averageDepth);
			sim.farm.grid.groundData.positionsDirty.SetAll(value: false);
			Monitor.Pulse(lockSimulation);
		}
	}

	public void SetupSim(ItemBlock items, RenderTexture renderTexture, Inventory inventory, CodeExample codeExample, string setupCOde)
	{
		if (activeInventory != null)
		{
			activeInventory.Disconnect();
		}
		activeInventory = inventory;
		this.codeExample = codeExample;
		mainExecutionStarted = false;
		InstalledDlcs = (codeExample.settings.dlc_enabled ? PlatformManager.InstalledDlcs : EDlcMask.None);
		lock (lockSimulation)
		{
			HashSet<string> excludedUnlocks = new HashSet<string>(codeExample.settings.exclude_unlocks);
			IEnumerable<string> unlocks = (from unlock in ResourceManager.GetAllUnlocks()
				where !excludedUnlocks.Contains(unlock.name)
				select (!unlock.IsMultiUnlock || !string.IsNullOrEmpty(unlock.gainResource) || !(unlock.unlockName != "watering")) ? unlock.unlockName : $"{unlock.unlockName}_{unlock.maxUnlockLevel}").Concat(from hat in ResourceManager.GetAllHats()
				select hat.hatName);
			sim = new Simulation(this, InstalledDlcs, unlocks, items, "", "", LeaderboardType.none, fullyGenerateUnderground: true, codeExample.settings.seed, null, null, resetUnlocks: false, codeExample.settings.action_ticks, codeExample.settings.operation_ticks, codeExample.settings.world_size, codeExample.settings.starting_chunk);
			Tokenizer.Tokenize(setupCOde, out var stream);
			Node syntaxTree = Parser.Parse(stream, null).syntaxTree;
			Execution execution = new Execution(sim, syntaxTree, 0);
			sim.StartProgramExecution(execution);
			while (sim.IsExecuting())
			{
				sim.RunNextStep(sim.CurrentTime + Duration.FromSeconds(1000.0), lockSimulation, stopOnFinished: true);
			}
			sim.Paused = true;
		}
		if (codeExample.settings.show_image)
		{
			UIFarmCamera.gameObject.SetActive(value: true);
			UIFarmCamera.targetTexture = renderTexture;
		}
		else
		{
			UIFarmCamera.gameObject.SetActive(value: false);
		}
		UIFarmCamera.transform.position = codeExample.settings.camera_position;
		activeInventory.SetUp(GetInventory);
	}

	public void ScheduleLeaderboardStart(MainSim.LeaderboardStartArgs startArgs)
	{
	}

	public void StartMainExecution(Node syntaxTree)
	{
		if (sim == null)
		{
			return;
		}
		lock (lockSimulation)
		{
			Simulation simulation = sim;
			if (simulation != null && simulation.IsExecuting())
			{
				return;
			}
			Execution execution = new Execution(sim, syntaxTree, 0);
			mainProgramState = execution.MainState;
			sim.StartProgramExecution(execution);
			mainExecutionStarted = true;
			sim.ChangeExecutionSpeed(codeExample.settings.execution_speed);
			sim.ChangeDiggingSpeed(codeExample.settings.digging_speed);
		}
		Logger.Clear();
		codeExample.SetExecutionVisuals();
	}

	private void PrintLastResult()
	{
		IPyObject pyObject = mainProgramState?.ReturnValue;
		if (pyObject is InternalPySequence internalPySequence)
		{
			if (internalPySequence.elements.Count == 0)
			{
				return;
			}
			pyObject = internalPySequence.elements[internalPySequence.elements.Count - 1];
		}
		if (pyObject != null)
		{
			Logger.Log(CodeUtilities.ToNiceString(pyObject));
		}
	}

	public void StopMainExecution()
	{
		if (sim != null)
		{
			lock (lockSimulation)
			{
				sim.StopProgramExecution();
			}
			codeExample.UnsetExecutionVisuals();
			codeExample = null;
			mainExecutionStarted = false;
			mainProgramState = null;
		}
	}

	public void DisableRendering()
	{
		if (UIFarmCamera != null)
		{
			UIFarmCamera.gameObject.SetActive(value: false);
		}
		if (activeInventory != null)
		{
			activeInventory.Disconnect();
		}
		activeInventory = null;
		sim = null;
		codeExample = null;
		mainExecutionStarted = false;
		mainProgramState = null;
	}

	public bool IsExecuting()
	{
		if (sim == null)
		{
			return false;
		}
		lock (lockSimulation)
		{
			return sim.IsExecuting();
		}
	}

	public void PlaySound(SoundEffectType sound, Vector2Int farmPos)
	{
	}

	public void PlayEffect(VFXType effect, Vector3 localPos, bool changeColor = false, Color color = default(Color), string text = null, float lifetime = 0f, float crumblePushAngle = 0f)
	{
		if (TimeFactor < 2.0)
		{
			AddVFXCall(new VFXCall(effect, localPos, changeColor, color, null, text, lifetime, crumblePushAngle));
		}
	}

	public void CollectItemEffect(int item, Vector3 localPos)
	{
		if (TimeFactor < 2.0)
		{
			AddVFXCall(new VFXCall(VFXType.moving_mesh_piggy, localPos, changeColor: false, default(Color), ResourceManager.GetItem(item).mesh, null));
		}
	}

	public void CrumbleEffect(Vector3Int blockPos)
	{
		lock (lockSimulation)
		{
			nextRenderPackage.crumblingBlocks.Add(new CrumblingBlockCall
			{
				pos = blockPos
			});
		}
	}

	public void SlideBlockEffect(Vector2Int sourcePos, Vector2Int targetPos)
	{
		if (TimeFactor >= 2.0)
		{
			return;
		}
		lock (lockSimulation)
		{
			nextRenderPackage.slidingBlocks.Add(new SlidingBlockCall
			{
				sourcePos = sourcePos,
				targetPos = targetPos,
				targetDepth = sim.farm.grid.CellAt(targetPos).depth,
				lifetimeCount = 1
			});
		}
	}

	public void SlideAndPopBlockEffect(Vector2Int sourcePos, Vector2Int targetPos, int targetDepth, int lifetimeCount)
	{
		if (TimeFactor >= 2.0)
		{
			return;
		}
		lock (lockSimulation)
		{
			nextRenderPackage.slidingBlocks.Add(new SlidingBlockCall
			{
				sourcePos = sourcePos,
				targetPos = targetPos,
				targetDepth = targetDepth,
				lifetimeCount = Mathf.Max(1, lifetimeCount),
				popEffect = true
			});
		}
	}

	public void DelayedPopBlockEffect(Vector3Int blockPos, float delay, Vector3 popVelocity)
	{
		if (TimeFactor >= 2.0)
		{
			return;
		}
		lock (lockSimulation)
		{
			nextRenderPackage.slidingBlocks.Add(new SlidingBlockCall
			{
				sourcePos = (Vector2Int)blockPos,
				targetPos = (Vector2Int)blockPos,
				targetDepth = blockPos.z,
				lifetimeCount = 1,
				popEffect = true,
				startAtTarget = true,
				overrideDuration = true,
				duration = delay,
				overridePopVelocity = true,
				popVelocity = popVelocity
			});
		}
	}

	private void AddVFXCall(VFXCall vfxCall)
	{
		lock (lockSimulation)
		{
			nextRenderPackage.vfxCalls.Add(vfxCall);
		}
	}

	public void BlinkEffect(Node node)
	{
		if (!(codeExample == null) && codeExample.settings.show_code)
		{
			BlinkManager.Inst.EnqueueBlink(node);
		}
	}

	public RenderPackage GetRenderPackage()
	{
		return renderPackage;
	}

	private void UpdateRenderPackage(float averageDepth)
	{
		nextRenderPackage.droneMeshes.Clear();
		foreach (Drone item in sim.farm.drones.Where((Drone d) => d != null))
		{
			item.TryUpdateHeight();
			nextRenderPackage.droneMeshes.Add((item.hat.hatSO, IsExecuting() && sim.farm.mainDroneId == item.DroneId && (sim.Paused || StepByStepMode), item.GetTransform(), item.GetDiggingTimeRemaining()));
		}
		Drone drone = sim.farm.drones[sim.farm.mainDroneId];
		int depth = sim.farm.grid.CellAt(drone.pos).depth;
		nextRenderPackage.dronePos = new Vector3Int(drone.pos.x, drone.pos.y, depth);
		nextRenderPackage.mainDroneLocalPosition = drone.GetTransform().GetPosition();
		nextRenderPackage.farmMeshes.Clear();
		Span<GridManager.Cell> span = sim.farm.grid.cells.AsSpan();
		for (int num = 0; num < span.Length; num++)
		{
			ref GridManager.Cell reference = ref span[num];
			if (reference.entity == null)
			{
				continue;
			}
			foreach (var mesh in reference.entity.GetMeshes())
			{
				nextRenderPackage.farmMeshes.Add((mesh.Item1, mesh.Item2));
			}
		}
		if (nextRenderPackage.cellDepths == null || nextRenderPackage.cellDepths.Length != sim.farm.grid.cells.Length)
		{
			nextRenderPackage.cellDepths = new int[sim.farm.grid.cells.Length];
		}
		if (nextRenderPackage.cellWaterVolumes == null || nextRenderPackage.cellWaterVolumes.Length != sim.farm.grid.cells.Length)
		{
			nextRenderPackage.cellWaterVolumes = new double[sim.farm.grid.cells.Length];
		}
		for (int num2 = 0; num2 < sim.farm.grid.cells.Length; num2++)
		{
			nextRenderPackage.cellDepths[num2] = sim.farm.grid.cells[num2].depth;
			nextRenderPackage.cellWaterVolumes[num2] = sim.farm.grid.cells[num2].waterVolume;
		}
		if (nextRenderPackage.groundData == null)
		{
			nextRenderPackage.groundData = new GroundData(sim.farm.grid.groundData);
		}
		else
		{
			nextRenderPackage.groundData = sim.farm.grid.groundData.CopyWithReuse(nextRenderPackage.groundData);
		}
		nextRenderPackage.averageDepth = averageDepth;
		nextRenderPackage.minDepth = int.MaxValue;
		nextRenderPackage.maxDepth = int.MinValue;
		for (int num3 = 0; num3 < nextRenderPackage.cellDepths.Length; num3++)
		{
			nextRenderPackage.minDepth = Math.Min(nextRenderPackage.minDepth, nextRenderPackage.cellDepths[num3]);
			nextRenderPackage.maxDepth = Math.Max(nextRenderPackage.maxDepth, nextRenderPackage.cellDepths[num3]);
		}
		RenderPackage renderPackage = nextRenderPackage;
		RenderPackage renderPackage2 = spareRenderPackage;
		RenderPackage renderPackage3 = this.renderPackage ?? new RenderPackage();
		this.renderPackage = renderPackage;
		nextRenderPackage = renderPackage2;
		spareRenderPackage = renderPackage3;
		nextRenderPackage.vfxCalls.Clear();
		nextRenderPackage.crumblingBlocks.Clear();
		nextRenderPackage.slidingBlocks.Clear();
	}

	public void SetDirty()
	{
	}

	public ItemBlock GetInventory()
	{
		if (sim == null)
		{
			return null;
		}
		lock (lockSimulation)
		{
			return new ItemBlock(sim.farm.Items);
		}
	}
}
public class InputBoss : MonoBehaviour
{
	[SerializeField]
	private float wasdSpeed;

	[SerializeField]
	private GameObject[] UIsToHide;

	private bool imeCompositionActive;

	private bool wasImeCompositionActiveThisFrame;

	private void Update()
	{
		wasImeCompositionActiveThisFrame |= (imeCompositionActive = !string.IsNullOrEmpty(Input.compositionString));
		if (0f > Input.mousePosition.x || 0f > Input.mousePosition.y || (float)Screen.width < Input.mousePosition.x || (float)Screen.height < Input.mousePosition.y)
		{
			return;
		}
		float axisRaw = Input.GetAxisRaw("ScrollWheel");
		float f = OptionHolder.GetFloat("scroll sensitivity", 1f);
		f = Mathf.Pow(f, 3f);
		f = Mathf.Max(f, 0.01f);
		axisRaw *= f;
		if (axisRaw != 0f)
		{
			if (MainSim.Inst.menu.gameObject.activeInHierarchy)
			{
				MainSim.Inst.menu.titleWorkspace.Scroll(axisRaw);
			}
			else if (MainSim.Inst.researchMenu.IsOpen)
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
		if (OptionHolder.GetKeyCombination("menu").IsKeyPressed(pressedRightThisFrame: true) && !wasImeCompositionActiveThisFrame)
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
				MainSim.Inst.workspace.workspaceContainer.anchoredPosition += new Vector2(0f, (0f - wasdSpeed) * Time.deltaTime);
			}
			if (OptionHolder.GetKeyCombination("move left").IsKeyPressed(pressedRightThisFrame: false))
			{
				MainSim.Inst.workspace.workspaceContainer.anchoredPosition += new Vector2(wasdSpeed * Time.deltaTime, 0f);
			}
			if (OptionHolder.GetKeyCombination("move down").IsKeyPressed(pressedRightThisFrame: false))
			{
				MainSim.Inst.workspace.workspaceContainer.anchoredPosition += new Vector2(0f, wasdSpeed * Time.deltaTime);
			}
			if (OptionHolder.GetKeyCombination("move right").IsKeyPressed(pressedRightThisFrame: false))
			{
				MainSim.Inst.workspace.workspaceContainer.anchoredPosition += new Vector2((0f - wasdSpeed) * Time.deltaTime, 0f);
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

	private void LateUpdate()
	{
		wasImeCompositionActiveThisFrame = imeCompositionActive;
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
		new PyFunction("get_pos_z", GetPosZ),
		new PyFunction("get_world_size", GetWorldSize),
		new PyFunction("get_entity_type", GetEntityType),
		new PyFunction("get_ground_type", GetGroundType),
		new PyFunction("get_time", GetTime, null, isFree: true),
		new PyFunction("get_tick_count", GetTickCount, null, isFree: true),
		new PyFunction("use_item", UseItem),
		new PyFunction("place", Place),
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
		new PyFunction("tap", IncrementTapTapLootCounter),
		new PyFunction("dig", Dig),
		new PyFunction("get_hardness", GetHardness),
		new PyFunction("get_stability", GetStability),
		new PyFunction("prospect_iron", ProspectIron),
		new PyFunction("prospect_quartz", ProspectQuartz),
		new PyFunction("push", Push),
		new PyFunction("can_push", CanPush),
		new PyFunction("jump", Jump),
		new PyFunction("hover", Hover),
		new PyFunction("get_hover", GetHover)
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
		"spawn_drone", "send", "receive", "underground_senses"
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
		Dictionary<IPyObject, PyObjectBox> dictionary = PyDict.CreateDictionary(items.items.Length);
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
		string s = string.Join(' ', parameters.Select((IPyObject p) => CodeUtilities.ToNiceString(p)));
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Print;
		programState.currentSideEffectArgument = new PyString(s);
		return 0.0;
	}

	private static double QuickPrint(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		string logMessage = string.Join(' ', parameters.Select((IPyObject p) => CodeUtilities.ToNiceString(p)));
		sim.simRunner.Logger.Log(logMessage);
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
		return exec.sim.operationOps * (double)Mathf.Max(steps, 1);
	}

	private static double Abs(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyNumber) }, "abs");
		exec.States[droneId].ReturnValue = new PyNumber(Math.Abs((PyNumber)parameters[0]));
		return sim.operationOps;
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
		CorrectParams(parameters, new List<Type> { typeof(EntitySO) }, "plant");
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

	private static double Place(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(GroundSO) }, "place");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Place;
		programState.currentSideEffectArgument = parameters[0];
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
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.GetEntityType;
		if (parameters.Count == 0 || (parameters.Count == 1 && parameters[0] is PyNone))
		{
			programState.currentSideEffectArgument = null;
		}
		else
		{
			CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "get_entity_type");
			programState.currentSideEffectArgument = parameters[0];
		}
		return 0.0;
	}

	private static double GetGroundType(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.GetGroundType;
		if (parameters.Count == 0 || (parameters.Count == 1 && parameters[0] is PyNone))
		{
			programState.currentSideEffectArgument = null;
		}
		else
		{
			CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "get_ground_type");
			programState.currentSideEffectArgument = parameters[0];
		}
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
		return sim.operationOps;
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

	private static double GetPosZ(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.GetPosZ;
		if (parameters.Count == 0 || (parameters.Count == 1 && parameters[0] is PyNone))
		{
			programState.currentSideEffectArgument = null;
		}
		else
		{
			CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "get_pos_z");
			programState.currentSideEffectArgument = parameters[0];
		}
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
		return sim.operationOps;
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
		return sim.operationOps;
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
			CorrectParams(parameters, new List<Type> { typeof(EntitySO) }, "get_cost");
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
			CorrectParams(parameters, new List<Type> { typeof(EntitySO) }, "num_unlocked");
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
		List<string> list = (leaderboardSO.everythingUnlocked ? GetUnlockStrings(ResourceManager.GetAllUnlocks(), leaderboardSO.singleDrone) : resetUnlocks);
		ItemBlock itemBlock = new ItemBlock(leaderboardSO.startItems);
		MainSim.LeaderboardStartArgs currentSideEffectArgument2 = new MainSim.LeaderboardStartArgs(obj.str, list, itemBlock, new List<KeyValuePair<string, IPyObject>>(), leaderboardSO.leaderboardName, leaderboardSO.steamLeaderboardName, leaderboardSO.leaderboardType, leaderboardSO.fullyGenerateUnderground, leaderboardSO.dlc, -1, whitelistedGroundFeatureUnlocks: leaderboardSO.whitelistedGroundFeatureUnlocks, pretendedFeatureChunks: leaderboardSO.pretendedFeatureChunks, pretendedChunkDepths: leaderboardSO.pretendedChunkDepths, singleDrone: leaderboardSO.singleDrone);
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
		MainSim.LeaderboardStartArgs currentSideEffectArgument2 = new MainSim.LeaderboardStartArgs(obj.str, unlockStrings, itemBlock, globals, "", "", LeaderboardType.simulation, fullyGenerateUnderground: true, EDlcType.None, (int)(double)pyNumber);
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Simulate;
		programState.currentSideEffectArgument = currentSideEffectArgument;
		programState.currentSideEffectArgument2 = currentSideEffectArgument2;
		return 0.0;
	}

	private static double SimulateAsync(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		return sim.actionOps;
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
		return Math.Max(sim.operationOps, num2);
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
		return sim.operationOps;
	}

	private static double ListConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PyList(new List<IPyObject>());
			return sim.operationOps;
		}
		CorrectParams(parameters, new List<Type> { typeof(IEnumerable<IPyObject>) }, "list");
		if (parameters[0] is IPySequence && ((IPySequence)parameters[0]).Count > 100000)
		{
			throw new ExecuteException("error_sequence_too_large");
		}
		PyList pyList = new PyList(((IEnumerable<IPyObject>)parameters[0]).ToList());
		exec.States[droneId].ReturnValue = pyList;
		return sim.operationOps * (double)(1 + pyList.Count);
	}

	private static double SetConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PySet();
			return sim.operationOps;
		}
		CorrectParams(parameters, new List<Type> { typeof(IEnumerable<IPyObject>) }, "set");
		if (parameters[0] is IPySequence && ((IPySequence)parameters[0]).Count > 100000)
		{
			throw new ExecuteException("error_sequence_too_large");
		}
		PySet pySet = new PySet(PySet.CreateSet((IEnumerable<IPyObject>)parameters[0]));
		foreach (IPyObject item in pySet)
		{
			if (item is PyDict || item is PyList || item is PySet || item is PyModule)
			{
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_bad_key", item));
			}
		}
		exec.States[droneId].ReturnValue = pySet;
		return sim.operationOps * (double)(1 + pySet.Count);
	}

	private static double DictConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PyDict();
			return sim.operationOps;
		}
		CorrectParams(parameters, new List<Type> { typeof(PyDict) }, "dict");
		PyDict pyDict = ((PyDict)parameters[0]).ShallowCopy();
		exec.States[droneId].ReturnValue = pyDict;
		return sim.operationOps * (double)(1 + 2 * pyDict.Count);
	}

	private static double StringConstructor(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count == 0)
		{
			exec.States[droneId].ReturnValue = new PyString("");
			return sim.operationOps;
		}
		CorrectParams(parameters, new List<Type> { typeof(IPyObject) }, "str");
		PyString returnValue = new PyString(CodeUtilities.ToNiceString(parameters[0]));
		exec.States[droneId].ReturnValue = returnValue;
		return sim.operationOps;
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

	private static double Dig(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "dig");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Dig;
		if (parameters.Count > 0)
		{
			programState.currentSideEffectArgument = parameters[0];
		}
		return 0.0;
	}

	private static double GetHardness(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count > 0)
		{
			CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "get_hardness");
		}
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.GetHardness;
		if (parameters.Count > 0)
		{
			programState.currentSideEffectArgument = parameters[0];
		}
		return 0.0;
	}

	private static double GetStability(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		if (parameters.Count > 0)
		{
			CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "get_stability");
		}
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.GetStability;
		if (parameters.Count > 0)
		{
			programState.currentSideEffectArgument = parameters[0];
		}
		return 0.0;
	}

	private static double ProspectIron(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type>(), "prospect_iron");
		exec.States[droneId].currentSideEffect = SideEffect.ProspectIron;
		return 0.0;
	}

	private static double ProspectQuartz(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type>(), "prospect_quartz");
		exec.States[droneId].currentSideEffect = SideEffect.ProspectQuartz;
		return 0.0;
	}

	private static double Push(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "push");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Push;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double CanPush(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyGridDirection) }, "can_push");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.CanPush;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double Jump(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(UnlockSO) }, "jump");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Jump;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double Hover(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		CorrectParams(parameters, new List<Type> { typeof(PyNumber) }, "hover");
		ProgramState programState = exec.States[droneId];
		programState.currentSideEffect = SideEffect.Hover;
		programState.currentSideEffectArgument = parameters[0];
		return 0.0;
	}

	private static double GetHover(List<IPyObject> parameters, Simulation sim, Execution exec, int droneId)
	{
		NoParams(parameters, "get_hover");
		exec.States[droneId].currentSideEffect = SideEffect.GetHover;
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
		return sim.operationOps;
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
		return sim.operationOps * (double)parameters[1].Size();
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
				if (pyList[i].PyEquals(parameters[1], ref steps))
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
			return sim.operationOps * (double)steps;
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
			return sim.operationOps * (double)parameters[1].Size();
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
				throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index_out_of_bounds", num, pyList));
			}
			IPyObject returnValue = pyList[num];
			pyList.RemoveAt(num);
			exec.States[droneId].ReturnValue = returnValue;
			return sim.operationOps * (double)(pyList.Count - num + 1);
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
			return sim.operationOps * (double)parameters[1].Size();
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
			throw new ExecuteException(CodeUtilities.LocalizeAndFormat("error_index_out_of_bounds", num, pyList));
		}
		double result = sim.operationOps * (double)(pyList.Count - num + 1);
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

	private bool hasJumped;

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
		ProgramState programState = new ProgramState(opCount, sim.randomRandom, droneId, sim);
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

	private void RescheduleOngoingDigs(int executionSpeedDroneId)
	{
		for (int i = 0; i < States.Count; i++)
		{
			if (i != executionSpeedDroneId && States[i] != null && i < sim.farm.drones.Count && sim.farm.drones[i] != null)
			{
				Duration diggingDurationRemaining = sim.farm.drones[i].GetDiggingDurationRemaining();
				if (diggingDurationRemaining.nanoseconds > 0)
				{
					double num = diggingDurationRemaining / sim.OpDuration;
					States[i].RescheduleConsumedOpCount(GlobalOpCount + num);
				}
			}
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
							sim.simRunner.StepByStepMode = true;
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
				if (stopped)
				{
					break;
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
		double ops = 0.0;
		ProgramState programState = States[droneId];
		IPyObject currentSideEffectArgument = programState.currentSideEffectArgument;
		object currentSideEffectArgument2 = programState.currentSideEffectArgument2;
		SideEffect currentSideEffect = programState.currentSideEffect;
		bool flag = true;
		switch (currentSideEffect)
		{
		case SideEffect.Harvest:
		{
			bool flag7 = sim.farm.drones[droneId].Harvest();
			programState.ReturnValue = new PyBool(flag7);
			ops = (flag7 ? sim.actionOps : sim.operationOps);
			break;
		}
		case SideEffect.CanHarvest:
			programState.ReturnValue = new PyBool(sim.farm.drones[droneId].CanHarvest());
			ops = sim.operationOps;
			break;
		case SideEffect.Swap:
		{
			bool flag5 = sim.farm.drones[droneId].Swap((PyGridDirection)currentSideEffectArgument, programState);
			programState.ReturnValue = new PyBool(flag5);
			ops = (flag5 ? sim.actionOps : sim.operationOps);
			break;
		}
		case SideEffect.Plant:
		{
			EntitySO entitySO3 = (EntitySO)currentSideEffectArgument;
			if (sim.plantingDisabledDueToLeaderboard)
			{
				throw new ExecuteException(Localizer.Localize("error_plant_not_allowed"));
			}
			bool flag6 = entitySO3.canBePlanted && sim.farm.drones[droneId].Plant(entitySO3, programState);
			programState.ReturnValue = new PyBool(flag6);
			ops = (flag6 ? sim.actionOps : sim.operationOps);
			break;
		}
		case SideEffect.Move:
		{
			double ops2;
			bool b2 = sim.farm.drones[droneId].Move((PyGridDirection)currentSideEffectArgument, programState, out ops2);
			programState.ReturnValue = new PyBool(b2);
			ops = ops2;
			break;
		}
		case SideEffect.CanMove:
			programState.ReturnValue = new PyBool(sim.farm.drones[droneId].CanMove((PyGridDirection)currentSideEffectArgument));
			ops = sim.operationOps;
			break;
		case SideEffect.Till:
			sim.farm.drones[droneId].ChangeGround("soil");
			programState.ReturnValue = new PyNone();
			ops = sim.actionOps;
			break;
		case SideEffect.GetPosX:
			programState.ReturnValue = new PyNumber(sim.farm.drones[droneId].pos.x);
			ops = sim.operationOps;
			break;
		case SideEffect.GetPosY:
			programState.ReturnValue = new PyNumber(sim.farm.drones[droneId].pos.y);
			ops = sim.operationOps;
			break;
		case SideEffect.GetPosZ:
		{
			Drone drone3 = sim.farm.drones[droneId];
			Vector2Int pos6;
			if (currentSideEffectArgument == null || currentSideEffectArgument is PyNone)
			{
				pos6 = drone3.pos;
			}
			else
			{
				GridDirection dir3 = (PyGridDirection)currentSideEffectArgument;
				pos6 = sim.farm.grid.Wrap(drone3.pos + dir3.GetDirectionVector());
			}
			programState.ReturnValue = new PyNumber(-sim.farm.grid.CellAt(pos6).depth);
			ops = sim.operationOps;
			break;
		}
		case SideEffect.GetWorldSize:
			programState.ReturnValue = new PyNumber(sim.farm.grid.WorldSize.y);
			ops = sim.operationOps;
			break;
		case SideEffect.GetEntityType:
		{
			Vector2Int pos3;
			if (currentSideEffectArgument == null || currentSideEffectArgument is PyNone)
			{
				pos3 = sim.farm.drones[droneId].pos;
			}
			else
			{
				GridDirection dir2 = (PyGridDirection)currentSideEffectArgument;
				pos3 = sim.farm.grid.Wrap(sim.farm.drones[droneId].pos + dir2.GetDirectionVector());
			}
			Entity entity = sim.farm.grid.CellAt(pos3).entity;
			if (entity != null)
			{
				programState.ReturnValue = entity.objectSO;
			}
			else
			{
				programState.ReturnValue = new PyNone();
			}
			ops = sim.operationOps;
			break;
		}
		case SideEffect.GetGroundType:
		{
			Drone drone4 = sim.farm.drones[droneId];
			Vector2Int pos7;
			if (currentSideEffectArgument == null || currentSideEffectArgument is PyNone)
			{
				pos7 = drone4.pos;
			}
			else
			{
				GridDirection dir4 = (PyGridDirection)currentSideEffectArgument;
				pos7 = sim.farm.grid.Wrap(drone4.pos + dir4.GetDirectionVector());
			}
			programState.ReturnValue = sim.farm.grid.GroundAt(pos7).groundSo;
			ops = sim.operationOps;
			break;
		}
		case SideEffect.UseItem:
		{
			ItemSO itemSO = (ItemSO)currentSideEffectArgument;
			int num2 = (int)((PyNumber)currentSideEffectArgument2).num;
			if (!sim.farm.Items.Contains(itemSO.itemId, num2))
			{
				sim.simRunner.Logger.LogWarning(string.Format(Localizer.Localize("warning_no_item_to_use"), itemSO), States[droneId]);
				programState.ReturnValue = new PyBool(b: false);
				ops = sim.operationOps;
				break;
			}
			bool flag4 = false;
			bool useActionTicks = false;
			switch (itemSO.itemName)
			{
			case "water":
				flag4 = sim.farm.drones[droneId].Water(num2);
				useActionTicks = flag4;
				break;
			case "fertilizer":
				flag4 = sim.farm.drones[droneId].Fertilize(num2);
				useActionTicks = flag4;
				break;
			case "weird_substance":
			{
				Entity entity2 = sim.farm.drones[droneId].EntityUnderDrone();
				if (entity2 is BushPlant bushPlant && sim.farm.IsUnlocked("mazes"))
				{
					int num3 = 1 << sim.farm.NumUnlocked("mazes") - 1;
					if (num2 % num3 != 0)
					{
						sim.simRunner.Logger.LogWarning(Localizer.Localize("warning_weird_substance_not_divisible"), States[droneId]);
					}
					int num4 = num2 / num3;
					if (num4 < 1)
					{
						bushPlant.ToggleWeird();
						break;
					}
					bushPlant.GenerateHedgeMaze(num4);
					flag4 = true;
					useActionTicks = flag4;
				}
				else if (entity2 is Treasure treasure && sim.farm.IsUnlocked("mazes"))
				{
					int num5 = num2 / (1 << sim.farm.NumUnlocked("mazes") - 1);
					if (num5 >= 1)
					{
						flag4 = treasure.RepositionTreasure(num5, out useActionTicks);
					}
				}
				else if (entity2 is Growable growable2 && growable2.objectSO.canBeWeird)
				{
					growable2.ToggleWeird();
					flag4 = true;
					useActionTicks = flag4;
				}
				break;
			}
			case "dynamite":
			{
				num2 = 1;
				flag4 = true;
				useActionTicks = true;
				Vector2Int pos4 = sim.farm.drones[droneId].pos;
				Dynamite.Explode(pos: new Vector3Int(pos4.x, pos4.y, sim.farm.grid.CellAt(pos4).depth), grid: sim.farm.grid, explosionEnergy: Dynamite.GetExplosionEnergy(sim.farm));
				break;
			}
			}
			programState.ReturnValue = new PyBool(flag4);
			if (flag4)
			{
				sim.farm.Items.RemoveItem(itemSO.itemId, num2);
			}
			ops = (useActionTicks ? sim.actionOps : sim.operationOps);
			break;
		}
		case SideEffect.Place:
		{
			GroundSO groundSO = (GroundSO)currentSideEffectArgument;
			if (!groundSO.allowedToPlaceManually)
			{
				sim.simRunner.Logger.LogWarning(string.Format(Localizer.Localize("warning_cannot_place_ground"), groundSO), States[droneId]);
				programState.ReturnValue = new PyBool(b: false);
				ops = sim.operationOps;
				break;
			}
			if (!sim.farm.Items.Contains(StringIds.BlockItemId, 1.0))
			{
				sim.simRunner.Logger.LogWarning(string.Format(Localizer.Localize("warning_no_item_to_use"), ResourceManager.GetItem(StringIds.BlockItemId)), States[droneId]);
				programState.ReturnValue = new PyBool(b: false);
				ops = sim.operationOps;
				break;
			}
			DesignConstants inst = DesignConstants.Inst;
			GridManager grid = sim.farm.grid;
			(float, int) tuple = grid.ComputeAverageAndMaxDepth();
			int num = Mathf.RoundToInt(inst.farmRenderer.FarmDepthOffset(grid.WorldSize, tuple.Item1, tuple.Item2)) + inst.balancingDesignConstants.placeMinDepthBelowOffset;
			if (sim.farm.drones[droneId].depth <= num)
			{
				throw new ExecuteException(string.Format(Localizer.Localize("error_place_too_high"), -sim.farm.drones[droneId].depth));
			}
			sim.farm.drones[droneId].PlaceBlock((GroundSO)currentSideEffectArgument);
			sim.farm.Items.RemoveItem(StringIds.BlockItemId, 1.0);
			programState.ReturnValue = new PyBool(b: true);
			ops = sim.actionOps;
			break;
		}
		case SideEffect.GetWater:
			programState.ReturnValue = new PyNumber(sim.farm.drones[droneId].GetWater());
			ops = sim.operationOps;
			break;
		case SideEffect.ChangeHat:
		{
			HatSO hatSO = (HatSO)currentSideEffectArgument;
			Drone drone = sim.farm.drones[droneId];
			bool flag2 = drone.hat.hatSO.preventHover && drone.fleightHeight == 1;
			if (hatSO.preventHover && !flag2)
			{
				if (drone.Hover(1, out ops))
				{
					drone.ChangeHat(hatSO, programState);
				}
			}
			else
			{
				drone.ChangeHat(hatSO, programState);
				ops = sim.actionOps;
			}
			programState.ReturnValue = new PyNone();
			break;
		}
		case SideEffect.NumItems:
			programState.ReturnValue = new PyNumber(sim.farm.Items.GetNumber(((ItemSO)currentSideEffectArgument).itemId));
			ops = sim.operationOps;
			break;
		case SideEffect.GetCost:
			if (currentSideEffectArgument is UnlockSO unlockSO2)
			{
				int numUnlocked = ((!(currentSideEffectArgument2 is PyNumber pyNumber)) ? (-1) : ((int)(double)pyNumber));
				States[droneId].ReturnValue = BuiltinFunctions.ItemsToNewDict(sim.farm.GetUnlockCost(unlockSO2, numUnlocked));
			}
			else if (currentSideEffectArgument is EntitySO entitySO)
			{
				if (string.IsNullOrEmpty(entitySO.yieldUpgradeName))
				{
					States[droneId].ReturnValue = BuiltinFunctions.ItemsToNewDict(entitySO.cost);
				}
				else
				{
					int num6 = Mathf.Max(0, sim.farm.NumUnlocked(entitySO.yieldUpgradeName) - 1);
					States[droneId].ReturnValue = BuiltinFunctions.ItemsToNewDict(entitySO.cost * (1 << num6));
				}
			}
			ops = sim.operationOps;
			break;
		case SideEffect.Clear:
			sim.simRunner?.PlaySound(SoundEffectType.ClearCalled, sim.farm.drones[droneId].pos);
			sim.farm.RemoveSpawnedDrones();
			sim.farm.grid.ClearGrid();
			sim.farm.drones[0].ResetPos();
			MainState = States[droneId];
			States.RemoveAll((ProgramState s) => s != MainState);
			MainState.DroneId = 0;
			if (MainState.awaitedDroneId >= 0)
			{
				MainState.awaitedDroneId = -1;
				MainState.OpCount = GlobalOpCount;
				MainState.ReturnValue = PyNone.Instance;
			}
			ops = sim.actionOps;
			programState.ReturnValue = PyNone.Instance;
			break;
		case SideEffect.GetCompanion:
		{
			IPyObject returnValue = ((!(sim.farm.grid.CellAt(sim.farm.drones[droneId].pos).entity is Growable growable)) ? new PyNone() : growable.GetCompanion());
			programState.ReturnValue = returnValue;
			ops = sim.operationOps;
			break;
		}
		case SideEffect.Unlock:
		{
			bool flag3 = sim.farm.UnlockOrUpgrade((UnlockSO)currentSideEffectArgument, requireParent: false);
			programState.ReturnValue = new PyBool(flag3);
			ops = (flag3 ? sim.actionOps : sim.operationOps);
			break;
		}
		case SideEffect.NumUnlocked:
			if (currentSideEffectArgument is UnlockSO unlockSO3)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(unlockSO3));
			}
			else if (currentSideEffectArgument is ItemSO itemSO2)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(itemSO2.itemName));
			}
			else if (currentSideEffectArgument is EntitySO entitySO2)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(entitySO2.objectName));
			}
			else if (currentSideEffectArgument is HatSO hatSO2)
			{
				programState.ReturnValue = new PyNumber(sim.farm.NumUnlocked(hatSO2.hatName));
			}
			ops = sim.operationOps;
			break;
		case SideEffect.Measure:
		{
			Drone drone2 = sim.farm.drones[droneId];
			Vector2Int pos;
			if (currentSideEffectArgument == null || currentSideEffectArgument is PyNone)
			{
				pos = drone2.pos;
			}
			else
			{
				GridDirection dir = (PyGridDirection)currentSideEffectArgument;
				pos = sim.farm.grid.Wrap(drone2.pos + dir.GetDirectionVector());
			}
			IPyObject pyObject = null;
			GridManager.Cell cell = sim.farm.grid.CellAt(pos);
			if (cell.entity != null)
			{
				pyObject = cell.entity.Measure();
			}
			else
			{
				Vector3Int pos2 = new Vector3Int(pos.x, pos.y, cell.depth);
				GridController controller = sim.farm.grid.GroundAt(pos2).groundSo.GetController(sim.farm.grid);
				if (controller != null)
				{
					pyObject = controller.Measure(drone2, pos2);
				}
			}
			programState.ReturnValue = pyObject ?? new PyNone();
			ops = sim.operationOps;
			break;
		}
		case SideEffect.SetExecutionSpeed:
		{
			double num13 = (PyNumber)currentSideEffectArgument;
			if (double.IsNaN(num13) || num13 > sim.farm.MaxSpeedFactor() || num13 < 0.1)
			{
				sim.ChangeExecutionSpeed(sim.farm.MaxSpeedFactor());
			}
			else
			{
				sim.ChangeExecutionSpeed(num13);
			}
			RescheduleOngoingDigs(droneId);
			programState.ReturnValue = new PyNone();
			ops = sim.actionOps;
			break;
		}
		case SideEffect.SetWorldSize:
			if ((int)(double)(PyNumber)currentSideEffectArgument != sim.farm.grid.WorldSize.y)
			{
				foreach (Drone drone5 in sim.farm.drones)
				{
					drone5?.ResetPos();
				}
				sim.farm.grid.SizeLimit = (int)(double)(PyNumber)currentSideEffectArgument;
			}
			programState.ReturnValue = new PyNone();
			ops = sim.actionOps;
			break;
		case SideEffect.GetTime:
			programState.ReturnValue = new PyNumber(sim.CurrentTime.Seconds);
			ops = 0.0;
			break;
		case SideEffect.SpawnDrone:
		{
			int num7 = States.Where((ProgramState s) => s != null).Count();
			int num8 = Helper.NumDrones(sim.farm.NumUnlocked("megafarm"));
			if (num7 >= num8)
			{
				programState.ReturnValue = PyNone.Instance;
				ops = sim.operationOps;
				break;
			}
			PyList obj = (PyList)currentSideEffectArgument;
			PyFunction pyFunction = (PyFunction)obj[0];
			Dictionary<object, object> copies2 = new Dictionary<object, object>();
			pyFunction = (PyFunction)pyFunction.DeepCopy(copies2);
			int num9 = sim.farm.AddDrone(droneId);
			FunctionNode functionNode = (FunctionNode)pyFunction.syntaxTree;
			List<IPyObject> list2 = new List<IPyObject>();
			foreach (IPyObject item in obj.list.Skip(1))
			{
				list2.Add(item.DeepCopy(copies2));
			}
			functionNode.Arguments = list2;
			AddProgramState(num9, functionNode, GlobalOpCount + sim.actionOps);
			States[num9].PushScope(new Scope(functionNode, null, pyFunction.parentScope, functionNode.Vars));
			PyDroneHandle pyDroneHandle2 = new PyDroneHandle(num9, sim.farm.droneGeneration);
			States[num9].DroneHandle = pyDroneHandle2;
			States[num9].CurrentExecutingNode = programState.CurrentExecutingNode;
			programState.ReturnValue = pyDroneHandle2;
			ops = sim.actionOps;
			sim.UnlockAchievement("USE_MULTIPLE_DRONES");
			if (num7 + 1 == 32)
			{
				sim.UnlockAchievement("SWARM");
			}
			break;
		}
		case SideEffect.GetDroneId:
			programState.ReturnValue = new PyNumber(droneId);
			ops = sim.operationOps;
			break;
		case SideEffect.NumDrones:
			programState.ReturnValue = new PyNumber(States.Where((ProgramState s) => s != null).Count());
			ops = sim.operationOps;
			break;
		case SideEffect.MaxDrones:
			programState.ReturnValue = new PyNumber(Helper.NumDrones(sim.farm.NumUnlocked("megafarm")));
			ops = sim.operationOps;
			break;
		case SideEffect.Await:
		{
			PyDroneHandle pyDroneHandle = (PyDroneHandle)currentSideEffectArgument;
			if (pyDroneHandle.returnValue != null)
			{
				Dictionary<object, object> copies = new Dictionary<object, object>();
				programState.ReturnValue = pyDroneHandle.returnValue.DeepCopy(copies);
				ops = sim.operationOps;
			}
			else
			{
				programState.awaitedDroneId = pyDroneHandle.id;
				ops = sim.operationOps;
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
			ops = sim.operationOps;
			break;
		case SideEffect.Terminated:
		{
			for (int num12 = 0; num12 < States.Count; num12++)
			{
				if (States[num12] != null && States[num12].awaitedDroneId == droneId)
				{
					States[num12].awaitedDroneId = -1;
					States[num12].OpCount = GlobalOpCount;
					Dictionary<object, object> copies3 = new Dictionary<object, object>();
					States[num12].ReturnValue = States[droneId].ReturnValue.DeepCopy(copies3);
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
			sim.simRunner.Logger.LogError(Localizer.Localize(currentExecuteException.Message), States[droneId]);
			sim.Error();
			IsPerformingAStep = false;
			sim.farm.mainDroneId = droneId;
			MainState = States[droneId];
			sim.UnlockAchievement("CAUSE_A_RUNTIME_ERROR");
			break;
		}
		case SideEffect.DoAFlip:
			sim.farm.drones[droneId].DoAFlip();
			programState.ReturnValue = new PyNone();
			ops = Math.Floor(1.0 / sim.OpDuration.Seconds);
			flag = false;
			break;
		case SideEffect.PetThePiggy:
			sim.farm.drones[droneId].PetThePiggy();
			programState.ReturnValue = new PyNone();
			ops = Math.Floor(1.0 / sim.OpDuration.Seconds);
			flag = false;
			break;
		case SideEffect.Print:
		{
			string str = ((PyString)currentSideEffectArgument).str;
			sim.farm.drones[droneId].PrintToAir(str);
			sim.simRunner.Logger.Log(str);
			programState.ReturnValue = new PyNone();
			ops = Math.Floor(1.0 / sim.OpDuration.Seconds);
			flag = false;
			break;
		}
		case SideEffect.Simulate:
			if (sim.simRunner != null && sim.leaderboardType == LeaderboardType.none)
			{
				MainSim.LeaderboardStartArgs startArgs = (MainSim.LeaderboardStartArgs)currentSideEffectArgument2;
				sim.simRunner.ScheduleLeaderboardStart(startArgs);
				sim.simRunner.TimeFactor = (PyNumber)currentSideEffectArgument;
				sim.Paused = true;
			}
			else
			{
				sim.simRunner.Logger.LogWarning(Localizer.Localize("warning_recursive_simulation"), programState);
			}
			programState.ReturnValue = new PyNone();
			ops = sim.actionOps;
			break;
		case SideEffect.RunLeaderboard:
			if (sim.simRunner != null && sim.leaderboardType == LeaderboardType.none)
			{
				MainSim.LeaderboardStartArgs leaderboardStartArgs = (MainSim.LeaderboardStartArgs)currentSideEffectArgument2;
				switch (leaderboardStartArgs.dlcType)
				{
				case EDlcType.None:
					sim.farm.AssertUnlocked("leaderboard");
					break;
				case EDlcType.Mining:
					sim.farm.AssertUnlocked("underground_leaderboard");
					break;
				}
				sim.simRunner.ScheduleLeaderboardStart(leaderboardStartArgs);
				sim.simRunner.TimeFactor = (PyNumber)currentSideEffectArgument;
				sim.Paused = true;
			}
			else
			{
				sim.simRunner.Logger.LogWarning(Localizer.Localize("warning_recursive_simulation"), programState);
			}
			programState.ReturnValue = new PyNone();
			ops = sim.actionOps;
			break;
		case SideEffect.Dig:
		{
			if (sim.leaderboardType != LeaderboardType.none && !sim.fullyGenerateUnderground)
			{
				throw new ExecuteException(Localizer.Localize("error_dig_not_allowed"));
			}
			int num10 = sim.farm.grid.CellAt(sim.farm.drones[droneId].pos).depth;
			Vector2Int vector2Int3 = sim.farm.drones[droneId].pos;
			DesignConstants.CaveInDesignConstants caveIn = DesignConstants.Inst.caveIn;
			if (currentSideEffectArgument is PyGridDirection pyGridDirection5)
			{
				vector2Int3 = (caveIn.allowWrappingDigAndMeasure ? sim.farm.grid.Wrap(vector2Int3 + pyGridDirection5.dir.GetDirectionVector()) : (vector2Int3 + pyGridDirection5.dir.GetDirectionVector()));
			}
			else
			{
				num10++;
			}
			if (sim.farm.grid.IsWithinBounds(vector2Int3) && sim.farm.grid.CellAt(vector2Int3).depth < num10)
			{
				GroundData.Ground ground = sim.farm.grid.GroundAt(vector2Int3);
				ops = Math.Ceiling((double)ground.hardness / sim.OpDuration.Seconds / sim.DiggingSpeedFactor);
				programState.ReturnValue = new PyBool(b: true);
				if (ground.hardness < 10000000)
				{
					int maxUncoveredDepth = sim.farm.grid.maxUncoveredDepth;
					sim.farm.drones[droneId].Dig(vector2Int3, out ops);
					Vector3Int vector3Int = new Vector3Int(vector2Int3.x, vector2Int3.y, num10 - 1);
					float num11 = (float)sim.GetActionTime(ops).Seconds;
					ISimRunner simRunner = sim.simRunner;
					if (simRunner != null)
					{
						Vector3 localPos = GridManager.CellToLocal(vector3Int + new Vector3(0f, 0f, 0.5f));
						float lifetime = num11;
						simRunner.PlayEffect(VFXType.block_break, localPos, changeColor: false, default(Color), null, lifetime);
					}
					if (caveIn.doCaveins)
					{
						sim.farm.grid.ClearGroundWithCaveins(vector2Int3, num10);
					}
					else
					{
						sim.farm.grid.ClearGround(vector2Int3, num10);
					}
					ground.groundSo.GetController(sim.farm.grid)?.OnAfterDig(sim.farm.drones[droneId], vector2Int3);
					if (sim.farm.grid.maxUncoveredDepth > maxUncoveredDepth)
					{
						sim.IncrementAchievementStat("total_depth", sim.farm.grid.maxUncoveredDepth - maxUncoveredDepth);
					}
					if (sim.farm.grid.maxUncoveredDepth >= 10000)
					{
						sim.UnlockAchievement("REACH_DEPTH");
					}
					Vector3Int pos5 = vector3Int + GridManager.down;
					GroundData.Ground ground2 = sim.farm.grid.GroundAt(pos5);
					if (sim.farm.grid.pyramidController.IsPyramidGround(ground2.groundSo))
					{
						PyramidController.Pyramid pyramidAtPos = sim.farm.grid.pyramidController.GetPyramidAtPos(pos5);
						if (pyramidAtPos != null)
						{
							sim.farm.grid.pyramidController.ClearPyramidIfComplete(pyramidAtPos);
						}
					}
				}
			}
			else
			{
				ops = sim.operationOps;
				programState.ReturnValue = new PyBool(b: false);
			}
			flag = false;
			break;
		}
		case SideEffect.GetHardness:
		{
			Vector2Int vector2Int2 = sim.farm.drones[droneId].pos;
			if (currentSideEffectArgument is PyGridDirection pyGridDirection4)
			{
				vector2Int2 = (DesignConstants.Inst.caveIn.allowWrappingDigAndMeasure ? sim.farm.grid.Wrap(vector2Int2 + pyGridDirection4.dir.GetDirectionVector()) : (vector2Int2 + pyGridDirection4.dir.GetDirectionVector()));
			}
			if (!sim.farm.grid.IsWithinBounds(vector2Int2))
			{
				programState.ReturnValue = PyNone.Instance;
			}
			else
			{
				programState.ReturnValue = new PyNumber(sim.farm.grid.GroundAt(vector2Int2).hardness);
			}
			ops = sim.operationOps;
			break;
		}
		case SideEffect.GetStability:
		{
			Vector2Int vector2Int = sim.farm.drones[droneId].pos;
			if (currentSideEffectArgument is PyGridDirection pyGridDirection3)
			{
				vector2Int = (DesignConstants.Inst.caveIn.allowWrappingDigAndMeasure ? sim.farm.grid.Wrap(vector2Int + pyGridDirection3.dir.GetDirectionVector()) : (vector2Int + pyGridDirection3.dir.GetDirectionVector()));
			}
			if (!sim.farm.grid.IsWithinBounds(vector2Int))
			{
				programState.ReturnValue = PyNone.Instance;
			}
			else
			{
				programState.ReturnValue = new PyNumber(sim.farm.grid.GroundAt(vector2Int).stability);
			}
			ops = sim.operationOps;
			break;
		}
		case SideEffect.ProspectIron:
			programState.ReturnValue = sim.farm.drones[droneId].ProspectIron(programState);
			ops = sim.operationOps;
			break;
		case SideEffect.ProspectQuartz:
			programState.ReturnValue = sim.farm.drones[droneId].ProspectQuartz(programState);
			ops = sim.operationOps;
			break;
		case SideEffect.Push:
		{
			if (!(currentSideEffectArgument is PyGridDirection pyGridDirection2))
			{
				programState.ReturnValue = new PyBool(b: false);
				break;
			}
			bool b3 = sim.farm.drones[droneId].Push(pyGridDirection2.dir, out ops);
			programState.ReturnValue = new PyBool(b3);
			break;
		}
		case SideEffect.CanPush:
			if (!(currentSideEffectArgument is PyGridDirection pyGridDirection))
			{
				programState.ReturnValue = new PyBool(b: false);
				break;
			}
			programState.ReturnValue = new PyBool(sim.farm.drones[droneId].CanPush(pyGridDirection.dir));
			ops = sim.operationOps;
			break;
		case SideEffect.Jump:
		{
			if (sim.leaderboardType != LeaderboardType.none && sim.leaderboardType != LeaderboardType.simulation)
			{
				throw new ExecuteException(Localizer.Localize("error_jump_not_allowed"));
			}
			UnlockSO unlockSO = (UnlockSO)programState.currentSideEffectArgument;
			List<GroundFeature> list = new List<GroundFeature>();
			foreach (GroundFeature allGroundFeature in ResourceManager.GetAllGroundFeatures())
			{
				if (!string.IsNullOrEmpty(allGroundFeature.associatedUnlockForJumpCommand) && string.CompareOrdinal(allGroundFeature.associatedUnlockForJumpCommand, unlockSO.unlockName) == 0)
				{
					list.Add(allGroundFeature);
				}
			}
			if (list.Count == 0)
			{
				throw new ExecuteException(Localizer.Localize("error_non_jumpable_unlock"));
			}
			if (hasJumped)
			{
				throw new ExecuteException(Localizer.Localize("error_can_only_jump_once"));
			}
			sim.farm.grid.JumpToFeature(list);
			hasJumped = true;
			ops = sim.actionOps;
			programState.ReturnValue = new PyNone();
			break;
		}
		case SideEffect.Hover:
		{
			bool b = sim.farm.drones[droneId].Hover((int)(double)(PyNumber)currentSideEffectArgument, out ops);
			programState.ReturnValue = new PyBool(b);
			break;
		}
		case SideEffect.GetHover:
			programState.ReturnValue = new PyNumber(sim.farm.drones[droneId].fleightHeight);
			ops = sim.operationOps;
			break;
		}
		if (programState != null)
		{
			if (flag)
			{
				programState.OpCount += ops;
			}
			else
			{
				programState.AddAndConsumeOps(ops);
			}
		}
		return ops;
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
	GetPosZ,
	GetWorldSize,
	GetEntityType,
	GetGroundType,
	UseItem,
	Place,
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
	RunLeaderboard,
	Dig,
	GetHardness,
	GetStability,
	ProspectIron,
	ProspectQuartz,
	Push,
	CanPush,
	Jump,
	Hover,
	GetHover
}
public class Logger
{
	public delegate void PrintAction();

	public const int NUM_OUTPUT_LIMIT = 100;

	public const int MESSAGE_LENGTH_LIMIT = 1000;

	private HashSet<Node> warningNodes = new HashSet<Node>();

	private LinkedList<string> output = new LinkedList<string>();

	private string persistentDataPath = Helper.persistentDataPath;

	private object outputLock = new object();

	private bool writeToOutputFile;

	public event PrintAction OnOutputChanged;

	public Logger(bool writeToOutputFile = true)
	{
		this.writeToOutputFile = writeToOutputFile;
	}

	public void Log(string logMessage)
	{
		WriteLog(logMessage, addSeparator: false);
	}

	public void LogError(string errorMessage, ProgramState state)
	{
		WriteLog("Error: " + errorMessage + "\nIn: " + state.GetTrace(), addSeparator: true);
	}

	public void LogWarning(string warningMessage, ProgramState state)
	{
		if (!(OptionHolder.GetString("print warnings") == "disabled") && !warningNodes.Contains(state.CurrentExecutingNode))
		{
			WriteLog("Warning: " + warningMessage + "\nIn: " + state.GetTrace(), addSeparator: true);
			MainSim.Inst.warningIcon.PopUp();
			warningNodes.Add(state.CurrentExecutingNode);
		}
	}

	public void Close()
	{
	}

	public void Clear()
	{
		lock (outputLock)
		{
			output.Clear();
		}
		warningNodes.Clear();
		MainSim.Inst.warningIcon.Dismiss();
		if (writeToOutputFile)
		{
			try
			{
				string path = Path.Combine(persistentDataPath, "output.txt");
				Directory.CreateDirectory(persistentDataPath);
				using (new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.ReadWrite | FileShare.Delete))
				{
				}
			}
			catch (IOException message)
			{
				UnityEngine.Debug.LogError(message);
			}
		}
		this.OnOutputChanged?.Invoke();
	}

	public string GetOutputString()
	{
		lock (outputLock)
		{
			return string.Join("\n", output);
		}
	}

	private void WriteLog(string logMessage, bool addSeparator)
	{
		if (addSeparator)
		{
			logMessage += "\n--------------------------------------------------------------------";
		}
		if (writeToOutputFile)
		{
			try
			{
				string path = Path.Combine(persistentDataPath, "output.txt");
				Directory.CreateDirectory(persistentDataPath);
				using FileStream stream = new FileStream(path, FileMode.Append, FileAccess.Write, FileShare.ReadWrite | FileShare.Delete);
				using StreamWriter streamWriter = new StreamWriter(stream);
				streamWriter.WriteLine(CodeUtilities.RemoveSyntaxTags(logMessage));
			}
			catch (IOException message)
			{
				UnityEngine.Debug.LogError(message);
			}
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
			this.OnOutputChanged?.Invoke();
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
		string currentFileName = ((boxedParams.codeWindow != null) ? boxedParams.codeWindow.fileName : "");
		foreach (double item2 in Assign(state, execution, depth, slots[0], returnValue, op, currentFileName))
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
			if (lhs.CheckIncrementOpCount(state, execution, execution.sim.operationOps * execTime))
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
				if (lhs.CheckIncrementOpCount(state, execution, execution.sim.operationOps * (execTime2 + (double)num)))
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
				if (lhs.CheckIncrementOpCount(state, execution, execution.sim.operationOps * ((double)steps + execTime3)))
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
				int num = ((IEnumerable<IPyObject>)rhsValue).Count();
				((PyList)before).list.AddRange((IEnumerable<IPyObject>)rhsValue);
				pyObject = before;
				execTime = num;
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
			if (CheckIncrementOpCount(state, execution, execution.sim.operationOps))
			{
				yield return 0.0;
			}
			yield break;
		}
		if (op == "or" && Scope.IsTrueValue(lhs))
		{
			Blink(state, execution);
			state.ReturnValue = lhs;
			if (CheckIncrementOpCount(state, execution, execution.sim.operationOps))
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
			yield return state.IsExpressionStatic ? 0.0 : execution.sim.operationOps;
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
			state.ReturnValue = new PyBool(lhs.PyEquals(returnValue, ref steps));
			break;
		case "!=":
			state.ReturnValue = new PyBool(!lhs.PyEquals(returnValue, ref steps));
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
			if (returnValue is IPySequence pySequence2)
			{
				state.ReturnValue = new PyBool(pySequence2.PyContains(lhs, ref steps));
			}
			else if (returnValue is PyDict pyDict2)
			{
				int steps4 = -1;
				state.ReturnValue = new PyBool(lhs != null && pyDict2.PyContains(lhs, ref steps4));
				steps = lhs.Size();
			}
			else if (returnValue is PySet pySet2)
			{
				int steps5 = -1;
				state.ReturnValue = new PyBool(pySet2.PyContains(lhs, ref steps5));
				steps = lhs.Size();
			}
			break;
		case "not in":
			if (returnValue is IPySequence pySequence)
			{
				state.ReturnValue = new PyBool(!pySequence.PyContains(lhs, ref steps));
			}
			else if (returnValue is PyDict pyDict)
			{
				int steps2 = -1;
				state.ReturnValue = new PyBool(lhs == null || !pyDict.PyContains(lhs, ref steps2));
				steps = lhs.Size();
			}
			else if (returnValue is PySet pySet)
			{
				int steps3 = -1;
				state.ReturnValue = new PyBool(!pySet.PyContains(lhs, ref steps3));
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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps * (double)steps))
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

	public override bool handlesErrorsAndBreakpoints => false;

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
				execution.sim.UnlockAchievement("INFINITE_LOOP");
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
				if (CheckIncrementOpCount(state, execution, execution.sim.operationOps))
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
					goto IL_0215;
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
				IL_0215:
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
			if (literalNode.value is EntitySO)
			{
				throw new ParseException(CodeUtilities.LocalizeAndFormat("error_entity_condition", literalNode.value), literalNode.boxedParams.wordStart, literalNode.boxedParams.wordEnd);
			}
			if (literalNode.value is GroundSO)
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
		if (parameters.Any((IPyObject p) => p is PyFunction))
		{
			execution.sim.UnlockAchievement("HIGHER_ORDER_PROGRAMMING");
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
				flag2 = pyObject.PyEquals(pyObject2, ref steps);
				break;
			case "!=":
				flag2 = !pyObject.PyEquals(pyObject2, ref steps);
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
				if (pyObject2 is IPySequence pySequence2)
				{
					flag2 = pySequence2.PyContains(pyObject, ref steps);
				}
				else if (pyObject2 is PyDict pyDict2)
				{
					int steps4 = -1;
					flag2 = pyObject != null && pyDict2.PyContains(pyObject, ref steps4);
					steps += pyObject.Size();
				}
				else if (pyObject2 is PySet pySet2)
				{
					int steps5 = -1;
					flag2 = pySet2.PyContains(pyObject, ref steps5);
					steps += pyObject.Size();
				}
				break;
			case "not in":
				if (pyObject2 is IPySequence pySequence)
				{
					flag2 = !pySequence.PyContains(pyObject, ref steps);
				}
				else if (pyObject2 is PyDict pyDict)
				{
					int steps2 = -1;
					flag2 = pyObject == null || !pyDict.PyContains(pyObject, ref steps2);
					steps += pyObject.Size();
				}
				else if (pyObject2 is PySet pySet)
				{
					int steps3 = -1;
					flag2 = !pySet.PyContains(pyObject, ref steps3);
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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps * (double)steps))
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
			if (literalNode2.value is EntitySO)
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
		if (!(obj is ItemSO) && !(obj is EntitySO))
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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps))
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
		Dictionary<IPyObject, PyObjectBox> dictionary = PyDict.CreateDictionary();
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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps * (double)(1 + dictionary.Count)))
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
			if (CheckIncrementOpCount(state, execution, execution.sim.operationOps))
			{
				yield return 0.0;
			}
			while (enumerator2.MoveNext())
			{
				IPyObject current = enumerator2.Current;
				string currentFileName = ((boxedParams.codeWindow != null) ? boxedParams.codeWindow.fileName : "");
				foreach (double item2 in AssignmentNode.Assign(state, execution, depth, pattern, current, "=", currentFileName))
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
						goto IL_02ce;
					}
					catch (BreakStatement)
					{
						yield break;
					}
					catch (ContinueStatement)
					{
					}
					break;
					IL_02ce:
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
public class GlobalNode : Node
{
	public override string NodeName => "global";

	public GlobalNode(CodeWindow func, int startIndex, int endIndex)
		: base(func, startIndex, endIndex)
	{
	}

	public override Node DeepCopy(Dictionary<object, object> copies)
	{
		return this;
	}

	public override IEnumerable<double> Execute(ProgramState state, Execution execution, int depth)
	{
		ErrorsAndBreakpoints(state, execution, depth);
		yield return 0.0;
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
			else if (!state.ModuleCache[name].fullyInitialized)
			{
				execution.sim.UnlockAchievement("CIRCULAR_IMPORT");
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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps * (double)Math.Max(1, pyList.Count)))
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

	public virtual string NodeName => "";

	public bool blink => boxedParams.wordEnd > boxedParams.wordStart;

	public virtual bool handlesErrorsAndBreakpoints => true;

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
			execution.sim.UnlockAchievement("STACK_OVERFLOW");
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
		if (boxedParams.isBreakpoint && !execution.sim.stepByStepMode && execution.sim.simRunner != null)
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
		if (state == execution.MainState && execution.sim.simRunner != null)
		{
			execution.sim.simRunner.BlinkEffect(this);
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
		if (handlesErrorsAndBreakpoints)
		{
			foreach (int item in breakpointCharPositions.ToList())
			{
				if (item <= boxedParams.wordStart)
				{
					boxedParams.isBreakpoint = true;
					breakpointCharPositions.Remove(item);
				}
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
		string text = codeWindow.CodeInput.text;
		return GetLineStart(text, boxedParams.wordStart) == GetLineStart(text, other.boxedParams.wordStart);
	}

	private static int GetLineStart(string source, int position)
	{
		position = Math.Clamp(position, 0, source.Length);
		if (position != 0)
		{
			return source.LastIndexOf('\n', position - 1) + 1;
		}
		return 0;
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

	public override bool handlesErrorsAndBreakpoints => false;

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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps))
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

	public override bool handlesErrorsAndBreakpoints => false;

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
		HashSet<IPyObject> hashSet = PySet.CreateSet(elements.Count);
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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps * (double)Math.Max(1, state.ReturnValue.Size())))
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
		if (CheckIncrementOpCount(state, execution, execution.sim.operationOps))
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
		string currentFileName = ((boxedParams.codeWindow != null) ? boxedParams.codeWindow.fileName : "");
		(state.ReturnValue, state.IsExpressionStatic) = state.CurrentScope.Evaluate(value, currentFileName);
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
			return new GlobalNode(f, token5.startIndex, token5.startIndex + token5.value.Length);
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
					if (!(node2 is FunctionNode) && !(node2 is CallNode) && node2 is ValueNode)
					{
						string value = ((ValueNode)node2).value;
						if (BuiltinFunctions.Functions.ContainsKey(value) || BuiltinFunctions.Methods.ContainsKey(value))
						{
							throw new ParseException(CodeUtilities.LocalizeAndFormat("error_not_a_statement2", value + "()"), node2.boxedParams.wordStart, node2.boxedParams.wordEnd);
						}
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
	private readonly Simulation sim;

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

	public double StartOpCount { get; }

	private double LastConsumedOpCount { get; set; }

	public int DroneId { get; set; } = -1;

	public PyDroneHandle DroneHandle { get; set; }

	public double TargetOpCount { get; set; }

	public ProgramState(double opCount, System.Random random, int droneId, Simulation sim)
	{
		this.sim = sim;
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

	public void RescheduleConsumedOpCount(double newOpCount)
	{
		double num = newOpCount - OpCount;
		OpCount = newOpCount;
		LastConsumedOpCount += num;
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
			sim.UnlockAchievement("STACK_OVERFLOW");
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
			"Entities" => new PyConstBag(ResourceManager.GetAllEntitites().ToDictionary((Func<EntitySO, string>)((EntitySO i) => i.objectName), (Func<EntitySO, IPyObject>)((EntitySO i) => i)), "Entities"), 
			"Grounds" => new PyConstBag(ResourceManager.GetAllGrounds().ToDictionary((Func<GroundSO, string>)((GroundSO i) => i.objectName), (Func<GroundSO, IPyObject>)((GroundSO i) => i)), "Grounds"), 
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
	private readonly struct PendingCodeChange
	{
		public readonly string name;

		public readonly string path;

		public readonly DateTime lastEventTime;

		public PendingCodeChange(string name, string path, DateTime lastEventTime)
		{
			this.name = name;
			this.path = path;
			this.lastEventTime = lastEventTime;
		}
	}

	private static FileSystemWatcher watcher;

	private static readonly Dictionary<string, PendingCodeChange> pendingCodeChanges = new Dictionary<string, PendingCodeChange>(StringComparer.OrdinalIgnoreCase);

	private static readonly object pendingCodeChangesLock = new object();

	private static readonly TimeSpan fileChangeSettleTime = TimeSpan.FromMilliseconds(250.0);

	private static readonly char[] portableInvalidFileNameChars = "<>:\"/\\|?*".ToCharArray();

	private static readonly HashSet<string> windowsReservedFileNames = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
	{
		"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6",
		"COM7", "COM8", "COM9", "COM¹", "COM²", "COM³", "LPT1", "LPT2", "LPT3", "LPT4",
		"LPT5", "LPT6", "LPT7", "LPT8", "LPT9", "LPT¹", "LPT²", "LPT³"
	};

	private const int version = 3;

	public static bool Save(MainSim mainSim)
	{
		if (mainSim == null)
		{
			return false;
		}
		string text = OptionHolder.GetString("activeSave", "Save0");
		try
		{
			string json = JsonUtility.ToJson(CreateSaveGame(mainSim));
			string pathOfSaveDirectory = GetPathOfSaveDirectory(text);
			CreateBackupSnapshot(text);
			WriteSaveGame(json, pathOfSaveDirectory);
			WriteCodeFiles(mainSim.workspace, pathOfSaveDirectory);
			mainSim.dirty = false;
			return true;
		}
		catch (Exception exception)
		{
			ReportSaveFailure(mainSim, text, exception);
			return false;
		}
	}

	public static bool SaveProgress(MainSim mainSim)
	{
		if (mainSim == null)
		{
			return false;
		}
		string text = OptionHolder.GetString("activeSave", "Save0");
		try
		{
			string json = JsonUtility.ToJson(CreateSaveGame(mainSim));
			string pathOfSaveDirectory = GetPathOfSaveDirectory(text);
			CreateBackupSnapshot(text);
			WriteSaveGame(json, pathOfSaveDirectory);
			return true;
		}
		catch (Exception exception)
		{
			ReportSaveFailure(mainSim, text, exception);
			return false;
		}
	}

	private static SaveGame CreateSaveGame(MainSim mainSim)
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
		Vector2 farmPos = mainSim.workspace.farmPosition.anchoredPosition;
		IEnumerable<Window> openWindows = mainSim.workspace.OpenWindows;
		saveGame.openFilePositions = openWindows.Select((Window f) => new Pair<string, Vector2>(f.windowName, f.WindowRect.anchoredPosition - farmPos)).ToList();
		saveGame.openFileSizes = openWindows.Select((Window f) => new Pair<string, Vector2>(f.windowName, f.playerSetSize)).ToList();
		saveGame.openFileScrollPositions = (from w in openWindows
			where w.TryGetComponent<CodeWindow>(out var _)
			select new Pair<string, float>(w.windowName, ((RectTransform)w.GetComponent<CodeWindow>().CodeInput.transform).anchoredPosition.y)).ToList();
		saveGame.dockedFiles = (from f in openWindows
			where f.dockedParent != null
			select new Pair<string, string>(f.windowName, f.dockedParent.windowName)).ToList();
		saveGame.minimizedFiles = (from f in openWindows
			where f.isMinimized
			select f.windowName).ToList();
		saveGame.openDocPages = (from w in openWindows
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
		return saveGame;
	}

	public static bool SaveCode(MainSim mainSim)
	{
		if (mainSim == null)
		{
			return false;
		}
		string text = OptionHolder.GetString("activeSave", "Save0");
		try
		{
			string pathOfSaveDirectory = GetPathOfSaveDirectory(text);
			CreateBackupSnapshot(text);
			WriteCodeFiles(mainSim.workspace, pathOfSaveDirectory);
			return true;
		}
		catch (Exception exception)
		{
			ReportSaveFailure(mainSim, text, exception);
			return false;
		}
	}

	private static void ReportSaveFailure(MainSim mainSim, string fileName, Exception exception)
	{
		UnityEngine.Debug.LogException(exception);
		if (!(mainSim?.warningPopup == null))
		{
			List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
			{
				new WarningPopup.ButtonData("ok", mainSim.warningPopup.Close)
			};
			mainSim.warningPopup.ShowPopup(CodeUtilities.LocalizeAndFormat("popup_warning_failed_write_save", fileName), buttonsToAdd);
		}
	}

	private static void WriteSaveGame(string json, string savePath)
	{
		WriteTextAtomically(new FileInfo(savePath + "/save.json"), json);
	}

	private static void WriteCodeFiles(Workspace workspace, string savePath)
	{
		foreach (CodeWindow value in workspace.codeWindows.Values)
		{
			if (!IsValidCodeFileName(value.fileName))
			{
				if (!SanitizeCodeFileName(value.fileName, out var newFileName) || workspace.IsWindowOpen(newFileName, ignoreCase: true))
				{
					newFileName = workspace.GenerateFileName("f");
				}
				value.Rename(newFileName);
			}
			WriteTextAtomically(new FileInfo($"{savePath}/{value.fileName}.py"), value.CodeInput.text);
		}
		FileInfo fileInfo = new FileInfo(savePath + "/__builtins__.py");
		if (!fileInfo.Exists)
		{
			string content = Localizer.LoadBuiltins();
			WriteTextAtomically(fileInfo, content);
		}
		foreach (string item in from f in Directory.GetFiles(savePath)
			where Path.GetExtension(f) == ".py" && !workspace.codeWindows.ContainsKey(Path.GetFileNameWithoutExtension(f)) && !f.EndsWith("__builtins__.py")
			select f)
		{
			File.Delete(item);
		}
	}

	private static string CreateBackupPath(string fileName)
	{
		string text = Helper.persistentDataPath + "/Backup";
		Directory.CreateDirectory(text);
		string text2 = fileName + "_backup";
		List<(int, string)> list = new List<(int, string)>();
		string[] directories = Directory.GetDirectories(text, text2 + "*", SearchOption.TopDirectoryOnly);
		foreach (string text3 in directories)
		{
			if (int.TryParse(new DirectoryInfo(text3).Name.Substring(text2.Length), out var result))
			{
				list.Add((result, text3));
			}
		}
		list.Sort();
		while (true)
		{
			int num = -1;
			int num2 = int.MaxValue;
			int num3 = int.MaxValue;
			for (int j = 1; j < list.Count; j++)
			{
				int num4 = list[j].Item1 - list[j - 1].Item1;
				if (num3 <= num4 && num3 <= num2)
				{
					num = j - 2;
					break;
				}
				num3 = num2;
				num2 = num4;
			}
			if (num < 0)
			{
				break;
			}
			try
			{
				Directory.Delete(list[num].Item2, recursive: true);
			}
			catch (Exception ex)
			{
				UnityEngine.Debug.LogWarning("Could not prune save backup '" + list[num].Item2 + "': " + ex.Message);
				break;
			}
			list.RemoveAt(num);
		}
		int num5 = ((list.Count > 0) ? (list.Last().Item1 + 1) : 0);
		return $"{text}/{fileName}_backup{num5}";
	}

	private static void CreateBackupSnapshot(string fileName)
	{
		string pathOfSaveDirectory = GetPathOfSaveDirectory(fileName);
		string legacySaveFilePath = GetLegacySaveFilePath(fileName);
		if (!Directory.Exists(pathOfSaveDirectory) && !File.Exists(legacySaveFilePath))
		{
			return;
		}
		string text = CreateBackupPath(fileName);
		string text2 = Path.Combine(Directory.GetParent(text).FullName, $".{fileName}.{Guid.NewGuid():N}.tmp");
		try
		{
			Directory.CreateDirectory(text2);
			if (Directory.Exists(pathOfSaveDirectory))
			{
				CopyDirectory(pathOfSaveDirectory, text2);
			}
			string text3 = Path.Combine(text2, "save.json");
			if (!File.Exists(text3) && File.Exists(legacySaveFilePath))
			{
				File.Copy(legacySaveFilePath, text3);
			}
			Directory.Move(text2, text);
		}
		catch
		{
			if (Directory.Exists(text2))
			{
				try
				{
					Directory.Delete(text2, recursive: true);
				}
				catch (Exception ex)
				{
					UnityEngine.Debug.LogWarning(ex.Message);
				}
			}
			throw;
		}
	}

	private static void CopyDirectory(string sourcePath, string destinationPath)
	{
		Directory.CreateDirectory(destinationPath);
		string[] files = Directory.GetFiles(sourcePath);
		foreach (string text in files)
		{
			File.Copy(text, Path.Combine(destinationPath, Path.GetFileName(text)));
		}
		files = Directory.GetDirectories(sourcePath);
		foreach (string text2 in files)
		{
			CopyDirectory(text2, Path.Combine(destinationPath, Path.GetFileName(text2)));
		}
	}

	internal static void WriteTextAtomically(FileInfo destinationFile, string content)
	{
		destinationFile.Directory.Create();
		string text = Path.Combine(destinationFile.DirectoryName, $".{destinationFile.Name}.{Guid.NewGuid():N}.tmp");
		try
		{
			using (FileStream fileStream = new FileStream(text, FileMode.CreateNew, FileAccess.Write, FileShare.None, 4096, FileOptions.WriteThrough))
			{
				using StreamWriter streamWriter = new StreamWriter(fileStream, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
				streamWriter.Write(content);
				streamWriter.Flush();
				fileStream.Flush(flushToDisk: true);
			}
			if (File.Exists(destinationFile.FullName))
			{
				File.Replace(text, destinationFile.FullName, null);
			}
			else
			{
				File.Move(text, destinationFile.FullName);
			}
		}
		finally
		{
			if (File.Exists(text))
			{
				File.Delete(text);
			}
		}
	}

	public static void Load(MainSim mainSim)
	{
		SaveGame currentSaveGame = GetCurrentSaveGame();
		if (currentSaveGame != null)
		{
			currentSaveGame.Normalize();
			currentSaveGame.items.Deserialize();
			mainSim.SetupSim(currentSaveGame.unlocks, new ItemBlock(currentSaveGame.items), null, null, currentSaveGame.version < 3);
			Vector2 anchoredPosition = mainSim.workspace.farmPosition.anchoredPosition;
			DirectoryInfo directoryInfo = new DirectoryInfo(GetPathOfSaveDirectory(OptionHolder.GetString("activeSave", "Save0")));
			directoryInfo.Create();
			IEnumerable<string> source = from f in Directory.GetFiles(directoryInfo.FullName)
				where Path.GetExtension(f) == ".py" && Path.GetFileName(f) != "__builtins__.py"
				select f;
			IEnumerable<string> first = source.Select((string f) => Path.GetFileNameWithoutExtension(f));
			IEnumerable<string> second = source.Select((string f) => File.ReadAllText(f).Replace("\r", ""));
			Dictionary<string, Vector2> dictionary = PairsToDictionary(currentSaveGame.openFilePositions);
			Dictionary<string, Vector2> dictionary2 = PairsToDictionary(currentSaveGame.openFileSizes);
			foreach (var item in first.Zip(second, (string file, string code) => (file: file, code: code)))
			{
				mainSim.workspace.OpenCodeWindow(item.file, item.code, dictionary.GetValueOrDefault(item.file) + anchoredPosition, dictionary2.GetValueOrDefault(item.file));
			}
			foreach (Pair<string, string> openDocPage in currentSaveGame.openDocPages)
			{
				if (!string.IsNullOrEmpty(openDocPage.key) && !string.IsNullOrEmpty(openDocPage.value) && !mainSim.workspace.IsWindowOpen(openDocPage.key))
				{
					mainSim.workspace.OpenDocsWindow(openDocPage.key, openDocPage.value, dictionary.GetValueOrDefault(openDocPage.key) + anchoredPosition, dictionary2.GetValueOrDefault(openDocPage.key));
				}
			}
			foreach (Pair<string, float> openFileScrollPosition in currentSaveGame.openFileScrollPositions)
			{
				if (mainSim.workspace.TryGetOpenWindow(openFileScrollPosition.key, out var window) && window.TryGetComponent<CodeWindow>(out var component))
				{
					((RectTransform)component.CodeInput.transform).anchoredPosition += new Vector2(0f, openFileScrollPosition.value);
				}
			}
			foreach (string minimizedFile in currentSaveGame.minimizedFiles)
			{
				if (mainSim.workspace.TryGetOpenWindow(minimizedFile, out var window2))
				{
					window2.SetMinmized(minimized: true);
				}
			}
			for (int num = 0; num < currentSaveGame.dockedFiles.Count; num++)
			{
				if (mainSim.workspace.TryGetOpenWindow(currentSaveGame.dockedFiles[num].key, out var window3) && mainSim.workspace.TryGetOpenWindow(currentSaveGame.dockedFiles[num].value, out var window4))
				{
					window3.DockOnto(window4);
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

	private static Dictionary<string, TValue> PairsToDictionary<TValue>(IEnumerable<Pair<string, TValue>> pairs)
	{
		Dictionary<string, TValue> dictionary = new Dictionary<string, TValue>();
		foreach (Pair<string, TValue> pair in pairs)
		{
			if (!string.IsNullOrEmpty(pair.key))
			{
				dictionary[pair.key] = pair.value;
			}
		}
		return dictionary;
	}

	public static void SaveTitleSave(Menu menu)
	{
		TitleSave titleSave = new TitleSave();
		IEnumerable<Window> openWindows = menu.titleWorkspace.OpenWindows;
		titleSave.openTitlePages = (from w in openWindows
			select (window: w, title: w.GetComponent<TitleWindow>()) into w
			where w.title != null
			select new Pair<string, string>(w.window.windowName, w.title.openPage)).ToList();
		titleSave.openFilePositions = openWindows.Select((Window f) => new Pair<string, Vector2>(f.windowName, f.WindowRect.anchoredPosition)).ToList();
		titleSave.openFileSizes = openWindows.Select((Window f) => new Pair<string, Vector2>(f.windowName, f.playerSetSize)).ToList();
		titleSave.dockedFiles = (from f in openWindows
			where f.dockedParent != null
			select new Pair<string, string>(f.windowName, f.dockedParent.windowName)).ToList();
		titleSave.minimizedFiles = (from f in openWindows
			where f.isMinimized
			select f.windowName).ToList();
		titleSave.windowHistory = menu.titleWorkspace.windowHistory?.ToList();
		try
		{
			string contents = JsonUtility.ToJson(titleSave);
			FileInfo fileInfo = new FileInfo(Helper.persistentDataPath + "/Title.json");
			fileInfo.Directory.Create();
			File.WriteAllText(fileInfo.FullName, contents);
		}
		catch (IOException ex)
		{
			UnityEngine.Debug.LogError(ex.Message);
		}
	}

	public static void LoadTitleSave(Menu menu)
	{
		FileInfo fileInfo = new FileInfo(Helper.persistentDataPath + "/Title.json");
		if (!fileInfo.Exists)
		{
			return;
		}
		TitleSave titleSave = JsonUtility.FromJson<TitleSave>(File.ReadAllText(fileInfo.FullName));
		Dictionary<string, Vector2> dictionary = titleSave.openFilePositions.ToDictionary((Pair<string, Vector2> x) => x.key, (Pair<string, Vector2> x) => x.value);
		Dictionary<string, Vector2> dictionary2 = titleSave.openFileSizes.ToDictionary((Pair<string, Vector2> x) => x.key, (Pair<string, Vector2> x) => x.value);
		foreach (Pair<string, string> openTitlePage in titleSave.openTitlePages)
		{
			menu.titleWorkspace.OpenWindow(openTitlePage.key, openTitlePage.value, dictionary.GetValueOrDefault(openTitlePage.key), dictionary2.GetValueOrDefault(openTitlePage.key));
		}
		foreach (string minimizedFile in titleSave.minimizedFiles)
		{
			if (menu.titleWorkspace.TryGetOpenWindow(minimizedFile, out var window))
			{
				window.SetMinmized(minimized: true);
			}
		}
		for (int num = 0; num < titleSave.dockedFiles.Count; num++)
		{
			if (menu.titleWorkspace.TryGetOpenWindow(titleSave.dockedFiles[num].key, out var window2) && menu.titleWorkspace.TryGetOpenWindow(titleSave.dockedFiles[num].value, out var window3))
			{
				window2.DockOnto(window3);
			}
		}
		TitleWorkspace titleWorkspace = menu.titleWorkspace;
		if (titleWorkspace.windowHistory == null)
		{
			titleWorkspace.windowHistory = new HashSet<string>();
		}
		if (titleSave.windowHistory != null)
		{
			menu.titleWorkspace.windowHistory.UnionWith(titleSave.windowHistory);
		}
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
		OptionHolder.OnOptionChanged -= EnableDisableFileWatcher;
		if (watcher != null)
		{
			watcher.Dispose();
			watcher = null;
		}
		lock (pendingCodeChangesLock)
		{
			pendingCodeChanges.Clear();
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
			if (optionName != "file watcher" || watcher == null)
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
				watcher.Created -= OnFileChanged;
				watcher.Created += OnFileChanged;
				watcher.Renamed -= OnFileRenamed;
				watcher.Renamed += OnFileRenamed;
			}
			else
			{
				watcher.Changed -= OnFileChanged;
				watcher.Created -= OnFileChanged;
				watcher.Renamed -= OnFileRenamed;
			}
		}
	}

	private static void OnFileChanged(object sender, FileSystemEventArgs e)
	{
		if (string.IsNullOrEmpty(e.Name) || !e.Name.EndsWith(".py", StringComparison.OrdinalIgnoreCase))
		{
			return;
		}
		string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(e.Name);
		lock (pendingCodeChangesLock)
		{
			pendingCodeChanges[fileNameWithoutExtension] = new PendingCodeChange(fileNameWithoutExtension, e.FullPath, DateTime.UtcNow);
		}
	}

	private static void OnFileRenamed(object sender, RenamedEventArgs e)
	{
		OnFileChanged(sender, e);
	}

	public static void ApplyCodeChanges(Workspace workspace)
	{
		DateTime now = DateTime.UtcNow;
		List<PendingCodeChange> list;
		lock (pendingCodeChangesLock)
		{
			list = pendingCodeChanges.Values.Where((PendingCodeChange change) => now - change.lastEventTime >= fileChangeSettleTime).ToList();
			foreach (PendingCodeChange item in list)
			{
				pendingCodeChanges.Remove(item.name);
			}
		}
		foreach (PendingCodeChange item2 in list)
		{
			if (!TryReadStableCodeFile(item2.path, out var code))
			{
				RequeueCodeChange(item2);
				continue;
			}
			lock (pendingCodeChangesLock)
			{
				if (pendingCodeChanges.TryGetValue(item2.name, out var value) && value.lastEventTime > item2.lastEventTime)
				{
					continue;
				}
			}
			if (code != null && workspace.codeWindows.TryGetValue(item2.name, out var value2) && value2.CodeInput.text != code)
			{
				value2.ApplyExternalCode(code);
			}
		}
	}

	private static bool TryReadStableCodeFile(string path, out string code)
	{
		code = null;
		try
		{
			FileInfo fileInfo = new FileInfo(path);
			if (!fileInfo.Exists)
			{
				return true;
			}
			long length = fileInfo.Length;
			DateTime lastWriteTimeUtc = fileInfo.LastWriteTimeUtc;
			using (FileStream stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
			{
				using StreamReader streamReader = new StreamReader(stream, Encoding.UTF8, detectEncodingFromByteOrderMarks: true);
				code = streamReader.ReadToEnd();
			}
			FileInfo fileInfo2 = new FileInfo(path);
			return fileInfo2.Exists && fileInfo2.Length == length && fileInfo2.LastWriteTimeUtc == lastWriteTimeUtc;
		}
		catch (IOException)
		{
			return false;
		}
		catch (UnauthorizedAccessException)
		{
			return false;
		}
	}

	private static void RequeueCodeChange(PendingCodeChange change)
	{
		lock (pendingCodeChangesLock)
		{
			if (!pendingCodeChanges.TryGetValue(change.name, out var value) || value.lastEventTime <= change.lastEventTime)
			{
				pendingCodeChanges[change.name] = new PendingCodeChange(change.name, change.path, DateTime.UtcNow);
			}
		}
	}

	public static SaveGame UpdateFromOldSaveGame(OldSaveGame oldSaveGame)
	{
		string text = OptionHolder.GetString("activeSave", "Save0");
		oldSaveGame.Normalize();
		SaveGame saveGame = new SaveGame();
		saveGame.unlocks = oldSaveGame.unlocks.ToList();
		saveGame.items = oldSaveGame.items ?? new ItemBlock();
		saveGame.openDocPages = new List<Pair<string, string>>();
		saveGame.minimizedFiles = oldSaveGame.minimized.ToList();
		saveGame.openFilePositions = new List<Pair<string, Vector2>>();
		saveGame.openFileScrollPositions = new List<Pair<string, float>>();
		saveGame.openFileSizes = new List<Pair<string, Vector2>>();
		saveGame.dockedFiles = new List<Pair<string, string>>();
		saveGame.version = 3;
		if (!string.IsNullOrEmpty(oldSaveGame.openDocsPage))
		{
			int num = 0;
			string docsWindowName;
			do
			{
				docsWindowName = $"docs{num}";
				num++;
			}
			while (oldSaveGame.functionNames.Any((string name) => string.Equals(name, docsWindowName, StringComparison.OrdinalIgnoreCase)));
			saveGame.openDocPages.Add(new Pair<string, string>(docsWindowName, oldSaveGame.openDocsPage));
			saveGame.openFilePositions.Add(new Pair<string, Vector2>(docsWindowName, oldSaveGame.docsPos));
		}
		CreateBackupSnapshot(text);
		int num2 = Math.Min(oldSaveGame.functionNames.Count, oldSaveGame.functionCode.Count);
		for (int num3 = 0; num3 < num2; num3++)
		{
			string text2 = oldSaveGame.functionNames[num3];
			if (IsValidCodeFileName(text2))
			{
				WriteTextAtomically(new FileInfo(Helper.persistentDataPath + $"/Saves/{text}/{text2}.py"), oldSaveGame.functionCode[num3]);
				Vector2 value = ((num3 < oldSaveGame.openFunctionPositions.Count) ? oldSaveGame.openFunctionPositions[num3] : Vector2.zero);
				saveGame.openFilePositions.Add(new Pair<string, Vector2>(text2, value));
				saveGame.openFileScrollPositions.Add(new Pair<string, float>(text2, 0f));
				if (num3 < oldSaveGame.functionDocked.Count && oldSaveGame.functionDocked[num3] != "")
				{
					saveGame.dockedFiles.Add(new Pair<string, string>(text2, oldSaveGame.functionDocked[num3]));
				}
			}
		}
		WriteSaveGame(JsonUtility.ToJson(saveGame), GetPathOfSaveDirectory(text));
		return saveGame;
	}

	private static SaveGame GetCurrentSaveGame()
	{
		string currentSaveGameJson = GetCurrentSaveGameJson();
		if (!string.IsNullOrEmpty(currentSaveGameJson))
		{
			SaveGame saveGame = JsonUtility.FromJson<SaveGame>(currentSaveGameJson);
			if (IsCurrentSaveGame(saveGame))
			{
				saveGame.Normalize();
				return saveGame;
			}
			OldSaveGame oldSaveGame = JsonUtility.FromJson<OldSaveGame>(currentSaveGameJson);
			if (IsOldSaveGame(oldSaveGame))
			{
				return UpdateFromOldSaveGame(oldSaveGame);
			}
			if (saveGame != null && (saveGame.unlocks != null || saveGame.items != null))
			{
				saveGame.Normalize();
				return saveGame;
			}
			return null;
		}
		return null;
	}

	private static bool IsCurrentSaveGame(SaveGame saveGame)
	{
		if (saveGame != null)
		{
			if (saveGame.version <= 0 && !HasEntries(saveGame.dockedFiles) && !HasEntries(saveGame.minimizedFiles) && !HasEntries(saveGame.openFilePositions) && !HasEntries(saveGame.openFileScrollPositions) && !HasEntries(saveGame.openFileSizes))
			{
				return HasEntries(saveGame.openDocPages);
			}
			return true;
		}
		return false;
	}

	private static bool IsOldSaveGame(OldSaveGame saveGame)
	{
		if (saveGame != null)
		{
			if (!HasEntries(saveGame.functionNames) && !HasEntries(saveGame.functionCode) && !HasEntries(saveGame.functionDocked) && !HasEntries(saveGame.minimized) && !HasEntries(saveGame.openFunctionPositions))
			{
				return !string.IsNullOrEmpty(saveGame.openDocsPage);
			}
			return true;
		}
		return false;
	}

	private static bool HasEntries<T>(List<T> list)
	{
		if (list != null)
		{
			return list.Count > 0;
		}
		return false;
	}

	public static bool GetCurrentSaveGameExists()
	{
		return File.Exists(GetPathOfSaveFile(OptionHolder.GetString("activeSave", "Save0")));
	}

	private static string GetCurrentSaveGameJson()
	{
		string saveName = OptionHolder.GetString("activeSave", "Save0");
		string pathOfSaveFile = GetPathOfSaveFile(saveName);
		if (!File.Exists(pathOfSaveFile))
		{
			CreateNewSaveGame(saveName);
			pathOfSaveFile = GetPathOfSaveFile(saveName);
		}
		return File.ReadAllText(pathOfSaveFile);
	}

	public static bool RenameSave(string saveName, string newSaveName)
	{
		if (!IsValidSaveName(newSaveName) || Directory.Exists(GetPathOfSaveDirectory(newSaveName)))
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
		if (!IsValidSaveName(saveName))
		{
			throw new ArgumentException("The save name is not a valid portable folder name.", "saveName");
		}
		DirectoryInfo directoryInfo = new DirectoryInfo(GetPathOfSaveDirectory(saveName));
		directoryInfo.Create();
		FileInfo fileInfo = new FileInfo(Path.Combine(directoryInfo.FullName, "save.json"));
		if (!File.Exists(fileInfo.FullName))
		{
			WriteTextAtomically(fileInfo, "");
		}
	}

	public static bool IsValidSaveName(string saveName)
	{
		return IsValidPortableFileName(saveName);
	}

	public static bool IsValidPortableFileName(string fileName)
	{
		if (string.IsNullOrEmpty(fileName) || fileName.StartsWith(".", StringComparison.Ordinal) || fileName.EndsWith(".", StringComparison.Ordinal) || fileName.EndsWith(" ", StringComparison.Ordinal) || fileName.IndexOfAny(portableInvalidFileNameChars) >= 0)
		{
			return false;
		}
		for (int i = 0; i < fileName.Length; i++)
		{
			if (fileName[i] < ' ')
			{
				return false;
			}
		}
		string item = fileName.Split('.')[0];
		return !windowsReservedFileNames.Contains(item);
	}

	public static bool IsValidCodeFileName(string fileName)
	{
		if (IsValidPortableFileName(fileName))
		{
			return !string.Equals(fileName, "__builtins__", StringComparison.OrdinalIgnoreCase);
		}
		return false;
	}

	public static bool SanitizeCodeFileName(string fileName, out string newFileName)
	{
		newFileName = fileName;
		if (string.IsNullOrEmpty(fileName))
		{
			return false;
		}
		if (newFileName.StartsWith(".", StringComparison.Ordinal))
		{
			newFileName = newFileName.Substring(1);
		}
		if (newFileName.EndsWith(".", StringComparison.Ordinal))
		{
			newFileName = newFileName.Substring(0, newFileName.Length - 1);
		}
		if (fileName.EndsWith(" ", StringComparison.Ordinal))
		{
			newFileName = newFileName.Substring(0, newFileName.Length - 1);
		}
		char[] array = portableInvalidFileNameChars;
		foreach (char c in array)
		{
			newFileName = newFileName.Replace(c.ToString(), "");
		}
		for (int num = newFileName.Length - 1; num >= 0; num--)
		{
			if (newFileName[num] < ' ')
			{
				newFileName = newFileName.Remove(num, 1);
			}
		}
		return newFileName.Length > 0;
	}

	public static string GetPathOfSaveFile(string saveName)
	{
		string text = $"{Helper.persistentDataPath}/Saves/{saveName}/save.json";
		if (!File.Exists(text))
		{
			text = GetLegacySaveFilePath(saveName);
		}
		return text;
	}

	private static string GetLegacySaveFilePath(string saveName)
	{
		return $"{Helper.persistentDataPath}/Saves/{saveName}.json";
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

	public void Normalize()
	{
		if (functionNames == null)
		{
			functionNames = new List<string>();
		}
		if (functionCode == null)
		{
			functionCode = new List<string>();
		}
		if (functionDocked == null)
		{
			functionDocked = new List<string>();
		}
		if (minimized == null)
		{
			minimized = new List<string>();
		}
		if (openFunctionPositions == null)
		{
			openFunctionPositions = new List<Vector2>();
		}
		if (unlocks == null)
		{
			unlocks = new List<string>();
		}
		if (grounds == null)
		{
			grounds = new List<SFO>();
		}
		if (entities == null)
		{
			entities = new List<SFO>();
		}
	}
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

	public void Normalize()
	{
		if (items == null)
		{
			items = new ItemBlock();
		}
		if (dockedFiles == null)
		{
			dockedFiles = new List<Pair<string, string>>();
		}
		if (minimizedFiles == null)
		{
			minimizedFiles = new List<string>();
		}
		if (openFilePositions == null)
		{
			openFilePositions = new List<Pair<string, Vector2>>();
		}
		if (openFileScrollPositions == null)
		{
			openFileScrollPositions = new List<Pair<string, float>>();
		}
		if (openFileSizes == null)
		{
			openFileSizes = new List<Pair<string, Vector2>>();
		}
		if (openDocPages == null)
		{
			openDocPages = new List<Pair<string, string>>();
		}
		if (unlocks == null)
		{
			unlocks = new List<string>();
		}
	}
}
[Serializable]
public class TitleSave
{
	public List<Pair<string, string>> dockedFiles;

	public List<string> minimizedFiles;

	public List<Pair<string, Vector2>> openFilePositions;

	public List<Pair<string, float>> openFileScrollPositions;

	public List<Pair<string, Vector2>> openFileSizes;

	public List<Pair<string, string>> openTitlePages;

	public List<string> windowHistory;
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
				PlatformManager.PlatformHandler.StoreStats();
			}
		}
		if (Time.time - richTextTime > 60f && Achievements.RichPresenceDisplay != null)
		{
			richTextTime = Time.time;
			PlatformManager.PlatformHandler.SetRichPresence("steam_display", Achievements.RichPresenceDisplay);
			Achievements.RichPresenceDisplay = null;
			PlatformManager.PlatformHandler.SetRichPresence("quantity", Achievements.RichPresenceQuantity);
			Achievements.RichPresenceQuantity = null;
		}
	}
}
public class BlinkManager : MonoBehaviour
{
	private static BlinkManager _instance;

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
	private float horizontalOffsetDocs;

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

	public static BlinkManager Inst => _instance;

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
				if (node2.boxedParams.codeWindow == null)
				{
					rects.Remove(node2);
					continue;
				}
				if (node2.blink && !node2.boxedParams.codeWindow.IsMinimized())
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
			if (stepByStepMode && currentNode != null && !currentNode.boxedParams.codeWindow.IsMinimized())
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
			if (!item2.boxedParams.codeWindow.IsMinimized())
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
		if (codeWindow.CodeInput.textComponent.textInfo.characterCount == 0 || end <= start)
		{
			return default(Rect);
		}
		TMP_CharacterInfo characterAtSourceIndex = codeWindow.CodeInput.GetCharacterAtSourceIndex(start);
		TMP_CharacterInfo characterAtSourceIndex2 = codeWindow.CodeInput.GetCharacterAtSourceIndex(end - 1);
		Vector3 startLocal = (characterAtSourceIndex.bottomLeft + characterAtSourceIndex.bottomRight) * 0.5f;
		Vector3 endLocal = (characterAtSourceIndex2.bottomLeft + characterAtSourceIndex2.bottomRight) * 0.5f;
		return GetWorldRect(startLocal, endLocal, height, codeWindow, topWindowRect);
	}

	private Rect GetWorldLineRect(int stringIndex, CodeWindow codeWindow, RectTransform topWindowRect)
	{
		TMP_CharacterInfo[] characterInfo = codeWindow.CodeInput.textComponent.textInfo.characterInfo;
		if (codeWindow.CodeInput.textComponent.textInfo.characterCount == 0)
		{
			return default(Rect);
		}
		int lineNumber = codeWindow.CodeInput.GetCharacterAtSourceIndex(stringIndex).lineNumber;
		TMP_LineInfo tMP_LineInfo = codeWindow.CodeInput.textComponent.textInfo.lineInfo[lineNumber];
		Vector3 bottomLeft = characterInfo[tMP_LineInfo.firstCharacterIndex].bottomLeft;
		Vector3 bottomRight = characterInfo[tMP_LineInfo.lastCharacterIndex].bottomRight;
		return GetWorldRect(bottomLeft, bottomRight, height, codeWindow, topWindowRect);
	}

	private Rect GetWorldRect(Vector3 startLocal, Vector3 endLocal, float height, CodeWindow codeWindow, RectTransform topWindowRect)
	{
		Window component;
		bool flag = !codeWindow.TryGetComponent<Window>(out component);
		RectTransform component2 = codeWindow.CodeInput.GetComponent<RectTransform>();
		Vector3 vector = GetCodeOffset(component2);
		Vector2 vector2 = startLocal * canvas.scaleFactor * cameraController.zoom + component2.position + vector;
		Vector2 vector3 = endLocal * canvas.scaleFactor * cameraController.zoom + component2.position + vector;
		Vector2 vector4 = vector2 - new Vector2(hmargin, vmargin) * canvas.scaleFactor * cameraController.zoom;
		Vector2 vector5 = vector3 + new Vector2(hmargin, height + vmargin) * canvas.scaleFactor * cameraController.zoom;
		float num = (flag ? horizontalOffsetDocs : horizontalOffset);
		vector4.x += num * canvas.scaleFactor * cameraController.zoom;
		vector5.x += num * canvas.scaleFactor * cameraController.zoom;
		vector4.y = (float)Screen.height - vector4.y;
		vector5.y = (float)Screen.height - vector5.y;
		Rect rect = new Rect(vector4, vector5 - vector4);
		rect.height = Mathf.Abs(rect.height);
		rect.y -= rect.height;
		RectTransform rectTransform = ((!flag) ? codeWindow.scrollViewRect : codeWindow.GetComponentInParent<ScrollRect>()?.viewport);
		Rect rect2;
		if (rectTransform != null)
		{
			Rect screenRect = GetScreenRect(rectTransform);
			rect2 = Rect.MinMaxRect(Mathf.Max(screenRect.xMin, rect.xMin), Mathf.Max(screenRect.yMin, rect.yMin), Mathf.Min(screenRect.xMax, rect.xMax), Mathf.Min(screenRect.yMax, rect.yMax));
		}
		else
		{
			rect2 = rect;
		}
		if (topWindowRect != null && codeWindow != topWindowRect.GetComponent<CodeWindow>() && (!flag || !topWindowRect.TryGetComponent<DocsWindow>(out var component3) || codeWindow.GetComponentInParent<DocsWindow>() != component3))
		{
			Rect screenRect2 = GetScreenRect(topWindowRect);
			MaskOutRect(ref rect2, screenRect2);
		}
		RectTransform component4 = MainSim.Inst.workspace.tooltip.Container.GetComponent<RectTransform>();
		if (component4.localScale != Vector3.zero)
		{
			Rect screenRect3 = GetScreenRect(component4);
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
public class BreakPointPanel : MonoBehaviour, IPointerClickHandler, IEventSystemHandler, IPointerDownHandler, IBeginDragHandler, IDragHandler
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

	public void OnPointerClick(PointerEventData eventData)
	{
		if (!MainSim.Inst.IsUnlocked("debug"))
		{
			return;
		}
		TMP_Text textComponent = function.CodeInput.textComponent;
		TMP_LineInfo[] array = textComponent.textInfo?.lineInfo;
		if (array == null || array.Length == 0)
		{
			return;
		}
		RectTransformUtility.ScreenPointToLocalPointInRectangle(textComponent.rectTransform, eventData.position, eventData.pressEventCamera, out var localPoint);
		Rect rect = textComponent.rectTransform.rect;
		float preferredHeight = textComponent.preferredHeight;
		if (localPoint.y > rect.yMax || localPoint.y < rect.yMax - preferredHeight)
		{
			return;
		}
		int num = -1;
		float num2 = float.PositiveInfinity;
		TMP_LineInfo tMP_LineInfo = default(TMP_LineInfo);
		for (int i = 0; i < array.Length; i++)
		{
			if (array[i].characterCount != 0)
			{
				Extents lineExtents = array[i].lineExtents;
				float num3 = Mathf.Abs((lineExtents.max.y + lineExtents.min.y) / 2f - localPoint.y);
				if (num3 < num2)
				{
					num = i;
					num2 = num3;
					tMP_LineInfo = array[i];
				}
			}
		}
		if (num < 0)
		{
			return;
		}
		if (breakpointLines.Contains(num))
		{
			breakpointLines.Remove(num);
			UnityEngine.Object.Destroy(breakpoints[num]);
			breakpoints.Remove(num);
		}
		else
		{
			GameObject gameObject = UnityEngine.Object.Instantiate(breakpointPrefab, base.transform);
			RectTransform obj = (RectTransform)gameObject.transform;
			float y = (tMP_LineInfo.lineExtents.max.y + tMP_LineInfo.lineExtents.min.y) / 2f;
			Vector3 position = textComponent.rectTransform.TransformPoint(new Vector3(0f, y, 0f));
			obj.anchoredPosition = new Vector2(0f, base.transform.InverseTransformPoint(position).y);
			if (gameObject.TryGetComponent<Image>(out var component))
			{
				component.color = ThemeManager.Inst.Theme.code.BreakpointColor;
			}
			breakpointLines.Add(num);
			breakpointLines.Sort();
			breakpoints[num] = gameObject;
		}
		UpdateBreakpoints(syntaxTree);
	}

	public void UpdateBreakpoints(Node syntaxTree)
	{
		this.syntaxTree = syntaxTree;
		string text = function.CodeInput.text;
		List<int> starts = new List<int> { 0 };
		for (int i = 0; i < text.Length; i++)
		{
			if (text[i] == '\n')
			{
				starts.Add(i + 1);
			}
		}
		syntaxTree?.InsertBreakpointsRec((from index in breakpointLines
			where index >= 0 && index < starts.Count
			select starts[index]).ToHashSet());
	}

	public void OnPointerDown(PointerEventData eventData)
	{
	}

	public void OnBeginDrag(PointerEventData eventData)
	{
	}

	public void OnDrag(PointerEventData eventData)
	{
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

	public void SetTypedString(string value)
	{
		compareString = value;
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
		optionStrings = (from s in optionStrings
			orderby MatchPriority(s), s
			select s).ToList();
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

	private int MatchPriority(string s)
	{
		int num = s.IndexOf(compareString, StringComparison.OrdinalIgnoreCase);
		if (num != 0)
		{
			if (num <= 0)
			{
				return 2;
			}
			return 1;
		}
		return 0;
	}
}
public class CodeExample : MonoBehaviour
{
	private class PointerEnterHandler : MonoBehaviour, IPointerEnterHandler, IEventSystemHandler
	{
		public Action onPointerEnter;

		public void OnPointerEnter(PointerEventData eventData)
		{
			onPointerEnter?.Invoke();
		}
	}

	public class CodeExampleSettings
	{
		[Serializable]
		public class ItemEntry
		{
			public string item;

			public double n;
		}

		public Vector3 camera_position = Vector3.zero;

		public bool show_image = true;

		public Vector2Int image_size = new Vector2Int(500, 300);

		public bool show_code = true;

		public bool show_inventory = true;

		public bool show_output;

		public bool print_last_result;

		public bool collapsing = true;

		public bool autoplay;

		public List<ItemEntry> items = new List<ItemEntry>();

		public List<string> exclude_unlocks = new List<string>();

		public Vector2Int world_size = new Vector2Int(5, 5);

		public double execution_speed = 2.0;

		public double digging_speed = 1.5;

		public int action_ticks = 200;

		public int operation_ticks = 1;

		public int seed;

		public int starting_chunk;

		public bool dlc_enabled = true;
	}

	private const float AnimationDuration = 0.1f;

	private const string ExamplePlayPressedOption = "code example play pressed";

	private static CodeExample activeExample;

	private static bool loggedHeadlessImageFallback;

	[SerializeField]
	private CodeWindow codeWindow;

	[SerializeField]
	private RawImage rawImage;

	[SerializeField]
	private Inventory inventory;

	[SerializeField]
	private GameObject executeButton;

	[SerializeField]
	private GameObject outputTextObject;

	[SerializeField]
	private OutputText outputText;

	private RenderTexture renderTexture;

	public CodeExampleSettings settings;

	private string setupCode;

	private bool wasVisible;

	private bool skipUpdate;

	private bool isExpanding;

	private Window parentWindow;

	private ColoredButton flashingExecuteButton;

	private Quaternion executeButtonRestRotation;

	private float executeButtonShakeStartTime;

	private readonly Vector3[] _corners = new Vector3[4];

	public void Setup(string code, string setupCode, CodeExampleSettings settings)
	{
		this.settings = settings;
		this.setupCode = setupCode;
		codeWindow.workspace = MainSim.Inst.workspace;
		codeWindow.Load(code, readOnly: true);
		codeWindow.UpdateTokens();
		if (settings.show_image && SystemInfo.graphicsDeviceType == GraphicsDeviceType.Null)
		{
			settings.show_image = false;
			if (!loggedHeadlessImageFallback)
			{
				loggedHeadlessImageFallback = true;
				UnityEngine.Debug.Log("[CodeExample] Graphics device is null; embedded simulation image previews are disabled for this headless run.");
			}
		}
		rawImage.gameObject.SetActive(settings.show_image);
		if (settings.show_image)
		{
			renderTexture = new RenderTexture(settings.image_size.x, settings.image_size.y, 24, RenderTextureFormat.DefaultHDR);
			renderTexture.Create();
			rawImage.texture = renderTexture;
			if (rawImage.GetComponent<RectMask2D>() == null)
			{
				rawImage.gameObject.AddComponent<RectMask2D>();
			}
			LayoutElement component = rawImage.GetComponent<LayoutElement>();
			component.minWidth = settings.image_size.x;
			component.minHeight = settings.image_size.y;
			component.preferredWidth = settings.image_size.x;
			component.preferredHeight = settings.image_size.y;
			component.flexibleWidth = 0f;
			component.flexibleHeight = 0f;
		}
		inventory.gameObject.SetActive(settings.show_image && settings.show_inventory);
		if (settings.collapsing)
		{
			rawImage.gameObject.SetActive(value: false);
			rawImage.transform.localScale = new Vector3(1f, 0f, 1f);
		}
		if (settings.autoplay)
		{
			executeButton.SetActive(value: false);
		}
		else if (!settings.autoplay && OptionHolder.GetFloat("code example play pressed") == 0f)
		{
			flashingExecuteButton = executeButton.GetComponent<ColoredButton>();
			executeButtonRestRotation = executeButton.transform.localRotation;
			executeButtonShakeStartTime = Time.time;
			OptionHolder.OnOptionChanged += OnOptionChanged;
		}
		if (settings.show_output)
		{
			outputTextObject.SetActive(value: true);
		}
		else
		{
			outputTextObject.SetActive(value: false);
		}
		codeWindow.gameObject.SetActive(settings.show_code);
		LayoutGroup componentInParent = rawImage.GetComponentInParent<LayoutGroup>();
		RefreshParentLayout(componentInParent);
		parentWindow = GetComponentInParent<Window>();
		if (parentWindow != null)
		{
			parentWindow.OnFocused.AddListener(RestartExecution);
		}
		base.gameObject.AddComponent<PointerEnterHandler>().onPointerEnter = RestartExecution;
	}

	public void OnPressExecute()
	{
		if (OptionHolder.GetFloat("code example play pressed") == 0f)
		{
			OptionHolder.SetOption("code example play pressed", 1f);
		}
		if (!UISim.Inst.IsExecuting())
		{
			StartExecution();
			return;
		}
		if (codeWindow.isExecuting)
		{
			UISim.Inst.StopMainExecution();
			return;
		}
		UISim.Inst.StopMainExecution();
		StartExecution();
	}

	private void Update()
	{
		if (flashingExecuteButton != null)
		{
			flashingExecuteButton.UpdateColor(1.2f + 0.3f * (Mathf.Sin(Time.time * 2f) + 1f));
			float num = Mathf.Repeat(Time.time - executeButtonShakeStartTime, 3f);
			float z = 0f;
			if (num < 0.6f)
			{
				float num2 = num / 0.6f;
				z = 10f * Mathf.Sin(num2 * 6f * MathF.PI) * Mathf.Sin(num2 * MathF.PI);
			}
			executeButton.transform.localRotation = executeButtonRestRotation * Quaternion.Euler(0f, 0f, z);
		}
		if (!settings.autoplay || codeWindow.isExecuting || isExpanding)
		{
			return;
		}
		skipUpdate = !skipUpdate;
		if (skipUpdate)
		{
			return;
		}
		bool flag = IsVisibleInScrollView();
		if (flag && activeExample == null && (!wasVisible || !UISim.Inst.IsExecuting()))
		{
			if (UISim.Inst.IsExecuting())
			{
				UISim.Inst.StopMainExecution();
			}
			StartExecution();
		}
		wasVisible = flag;
	}

	private void OnOptionChanged(string optionName)
	{
		if (!(optionName != "code example play pressed"))
		{
			if (flashingExecuteButton != null)
			{
				flashingExecuteButton.UpdateColor();
				executeButton.transform.localRotation = executeButtonRestRotation;
			}
			flashingExecuteButton = null;
			OptionHolder.OnOptionChanged -= OnOptionChanged;
		}
	}

	private void OnDisable()
	{
		if (flashingExecuteButton != null)
		{
			executeButton.transform.localRotation = executeButtonRestRotation;
		}
	}

	private bool IsVisibleInScrollView()
	{
		ScrollRect componentInParent = GetComponentInParent<ScrollRect>();
		if (componentInParent == null)
		{
			return true;
		}
		RectTransform obj = ((componentInParent.viewport != null) ? componentInParent.viewport : (componentInParent.transform as RectTransform));
		RectTransform rectTransform = base.transform as RectTransform;
		obj.GetWorldCorners(_corners);
		Rect rect = new Rect(_corners[0].x, _corners[0].y, _corners[2].x - _corners[0].x, _corners[2].y - _corners[0].y);
		rectTransform.GetWorldCorners(_corners);
		Rect other = new Rect(_corners[0].x, _corners[0].y, _corners[2].x - _corners[0].x, _corners[2].y - _corners[0].y);
		return rect.Overlaps(other);
	}

	private void RestartExecution()
	{
		if (settings.autoplay)
		{
			if (UISim.Inst.IsExecuting())
			{
				UISim.Inst.StopMainExecution();
			}
			StartExecution();
		}
	}

	private void StartExecution()
	{
		if (isExpanding)
		{
			return;
		}
		if (activeExample != null && activeExample != this)
		{
			activeExample.Interrupt();
		}
		LeanTween.cancel(rawImage.gameObject);
		activeExample = this;
		if (settings.show_image)
		{
			rawImage.gameObject.SetActive(value: true);
		}
		bool flag = settings.collapsing && settings.show_image && rawImage.transform.localScale.y < 1f;
		if (flag)
		{
			isExpanding = true;
			LayoutGroup layoutGroup = rawImage.GetComponentInParent<LayoutGroup>();
			LeanTween.scaleY(rawImage.gameObject, 1f, 0.1f).setOnUpdate((Action<float>)delegate
			{
				RefreshParentLayout(layoutGroup);
			}).setOnComplete(StartMainExecution);
		}
		ItemBlock itemBlock = ItemBlock.CreateEmpty();
		foreach (CodeExampleSettings.ItemEntry item in settings.items)
		{
			itemBlock.AddItem(StringIds.GetItemId(item.item), item.n);
		}
		UISim.Inst.SetupSim(itemBlock, renderTexture, inventory, this, setupCode);
		if (!flag)
		{
			StartMainExecution();
		}
	}

	private void StartMainExecution()
	{
		isExpanding = false;
		UISim.Inst.StartMainExecution(codeWindow.Parse());
		if (settings.show_output)
		{
			outputText.CoupleToSim();
		}
	}

	public void SetExecutionVisuals()
	{
		codeWindow.StartExecutionMode();
		codeWindow.SetExecutionColor();
	}

	public void SetExecutionColor()
	{
		codeWindow.SetExecutionColor();
	}

	public void UnsetExecutionVisuals()
	{
		codeWindow.StopExecutionMode();
		if (settings.show_output)
		{
			outputText.DecoupleFromSim();
		}
	}

	private void Interrupt()
	{
		if (codeWindow.isExecuting && UISim.Inst.IsExecuting())
		{
			UISim.Inst.StopMainExecution();
		}
		else
		{
			UnsetExecutionVisuals();
		}
		isExpanding = false;
		if (settings.collapsing && settings.show_image)
		{
			LeanTween.cancel(rawImage.gameObject);
			LayoutGroup layoutGroup = rawImage.GetComponentInParent<LayoutGroup>();
			LeanTween.scaleY(rawImage.gameObject, 0f, 0.1f).setOnUpdate((Action<float>)delegate
			{
				RefreshParentLayout(layoutGroup);
			}).setOnComplete((Action)delegate
			{
				rawImage.gameObject.SetActive(value: false);
			});
		}
	}

	private void RefreshParentLayout(LayoutGroup layoutGroup)
	{
		if (!(layoutGroup == null))
		{
			RectTransform rectTransform = layoutGroup.transform as RectTransform;
			if (rectTransform != null)
			{
				LayoutRebuilder.ForceRebuildLayoutImmediate(rectTransform);
			}
		}
	}

	private void OnDestroy()
	{
		OptionHolder.OnOptionChanged -= OnOptionChanged;
		if (parentWindow != null)
		{
			parentWindow.OnFocused.RemoveListener(RestartExecution);
		}
		if (renderTexture != null)
		{
			renderTexture.Release();
		}
		if (codeWindow.isExecuting)
		{
			UISim.Inst.StopMainExecution();
		}
		if (activeExample == this)
		{
			UISim.Inst.DisableRendering();
		}
		if (rawImage != null)
		{
			LeanTween.cancel(rawImage.gameObject);
		}
		if (activeExample == this)
		{
			activeExample = null;
		}
		if (settings.show_output)
		{
			outputText.DecoupleFromSim();
		}
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

	private string searchWord = "";

	private int selectedSearchIndex = -1;

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

	private void LateUpdate()
	{
		if (errorMessage.IsShowing() && errorString != null)
		{
			UpdateErrorPosition(revealError: false);
		}
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		windowBackground.color = theme.ui.WindowFrameColor;
		if (fileNameText != null)
		{
			theme.ui.text.ApplyTo(fileNameText);
		}
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
		ScrollRect scrollRect = scrollView;
		if ((object)scrollRect != null && scrollRect.verticalScrollbar.handleRect.TryGetComponent<Image>(out var component3))
		{
			component3.color = theme.ui.ScrollbarColor;
		}
		codeText.text = CodeUtilities.SyntaxColor2(codeInput.TextWithComposition, ThemeManager.Inst.Theme, "", -1, codeInput.IMECompositionRange);
	}

	private void UpdateCodeTooltips()
	{
		if (tooltipUpdateCallback == null)
		{
			return;
		}
		int characterIndex = TMP_TextUtilities.FindIntersectingCharacter(codeInput.textComponent, new Vector3(Input.mousePosition.x, Input.mousePosition.y), workspace.uiCam, visibleOnly: true);
		characterIndex = codeInput.CharacterToSourceIndex(characterIndex);
		int num = characterIndex;
		int i = characterIndex;
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
		if (!isExecuting || !MainSim.Inst.IsExecuting())
		{
			StartExecution(stepByStep: false);
		}
		else if (MainSim.Inst.StepByStepMode)
		{
			MainSim.Inst.StepByStepMode = false;
		}
		else
		{
			MainSim.Inst.StopMainExecution();
		}
	}

	public void PressStepByStepButton()
	{
		workspace.activeWindow = GetComponent<Window>();
		if (!isExecuting || !MainSim.Inst.IsExecuting())
		{
			StartExecution(stepByStep: true);
		}
		else if (MainSim.Inst.StepByStepMode)
		{
			MainSim.Inst.NextExecutionStep();
		}
		else
		{
			MainSim.Inst.StepByStepMode = true;
		}
	}

	private void StartExecution(bool stepByStep)
	{
		MainSim.Inst.StopMainExecution();
		Node node = Parse();
		if (node != null)
		{
			MainSim.Inst.StartMainExecution(this, node, stepByStep);
		}
	}

	public void StartStepByStepMode()
	{
		stepByStepImg.sprite = stepByStepSprite;
		executeImg.sprite = executeSprite;
		executeButton?.SetTooltipDescription("button_tooltip_resume_execution");
		stepByStepButton?.SetTooltipDescription("button_tooltip_next_step");
	}

	public void StartExecutionMode(bool closeErrors = true)
	{
		if (executeButton != null)
		{
			executeButton.IsRunning = true;
			executeButton.SetTooltipDescription("button_tooltip_stop_execution");
		}
		if (stepByStepButton != null)
		{
			stepByStepButton.IsRunning = true;
			stepByStepButton.SetTooltipDescription("button_tooltip_pause_execution");
		}
		isExecuting = true;
		if (executeImg != null)
		{
			executeImg.sprite = stopSprite;
		}
		if (stepByStepImg != null)
		{
			stepByStepImg.sprite = pauseSprite;
		}
		if (closeErrors)
		{
			CloseError();
		}
	}

	public void StopExecutionMode()
	{
		if (isExecuting)
		{
			if (executeButton != null)
			{
				executeButton.IsRunning = false;
				executeButton.SetTooltipDescription("button_tooltip_execute");
			}
			if (stepByStepButton != null)
			{
				stepByStepButton.IsRunning = false;
				stepByStepButton.SetTooltipDescription("button_tooltip_step_by_step");
			}
			isExecuting = false;
			if (executeImg != null)
			{
				executeImg.sprite = executeSprite;
			}
			if (stepByStepImg != null)
			{
				stepByStepImg.sprite = stepByStepSprite;
			}
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

	public void Load(string code, bool readOnly = false)
	{
		if (!readOnly)
		{
			codeInput.onTextInserted.AddListener(OnCodeInserted);
			codeInput.onTextMeshUpdated.AddListener(OnCodeChanged);
			codeInput.onEndEdit.AddListener(OnCodeCommit);
			codeInput.onCarretMoved.AddListener(OnCarretMoved);
			codeInput.onBackSpace.AddListener(OnBackspace);
			codeInput.onAutocompleteRequested.AddListener(OpenCodeCompleterAtCarret);
			codeInput.onSelect.AddListener(OnFocus);
			codeInput.onTextSelection.AddListener(OnTextSelection);
		}
		codeInput.uiCam = workspace.uiCam;
		codeInput.codeCompleter = (RectTransform)workspace.codeCompleter.transform;
		codeInput.text = code;
		if (fileNameText != null)
		{
			fileNameText.text = fileName;
		}
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
			workspace.RenameWindow(GetComponent<Window>(), newName);
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
		errorMessage.Close();
		updateSizeInXFrames = 2;
	}

	public bool IsMinimized()
	{
		return GetComponent<Window>()?.isMinimized ?? false;
	}

	public bool IsPointerOverCodeInput()
	{
		if (RectTransformUtility.RectangleContainsScreenPoint((RectTransform)codeInput.textViewport.transform, Input.mousePosition, workspace.uiCam))
		{
			if (!(scrollViewRect == null))
			{
				return RectTransformUtility.RectangleContainsScreenPoint(scrollViewRect, Input.mousePosition, workspace.uiCam);
			}
			return true;
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
		if (scrollViewRect == null || scrollView == null)
		{
			return;
		}
		TMP_TextInfo textInfo = codeInput.textComponent.textInfo;
		if (textInfo.characterCount != 0)
		{
			float y = codeInput.GetCharacterAtSourceIndex(stringPosition).bottomLeft.y;
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

	public void ApplyExternalCode(string code)
	{
		if (!(codeInput.text == code))
		{
			codeInput.text = code;
			Parse();
			if (parseException == null)
			{
				CloseError();
			}
			else
			{
				ShowError();
			}
		}
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
			UpdateErrorPosition(revealError: false);
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
		CodeCompleter codeCompleter = workspace.codeCompleter;
		if (!codeCompleter.IsOpen)
		{
			return;
		}
		int stringPosition = codeInput.stringPosition;
		if (stringPosition <= codeCompleter.startStringIndex || stringPosition > codeInput.text.Length)
		{
			codeCompleter.Close();
			return;
		}
		string text = codeInput.text.Substring(codeCompleter.startStringIndex, stringPosition - codeCompleter.startStringIndex);
		if (text.All(Helper.IsValidNameChar))
		{
			codeCompleter.SetTypedString(text);
		}
		else
		{
			codeCompleter.Close();
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
			else if (OptionHolder.GetString("automatic autocomplete", "enabled") == "enabled")
			{
				int stringPosition = codeInput.stringPosition;
				if (stringPosition <= 1 || stringPosition >= codeInput.text.Length || !Helper.IsValidNameChar(codeInput.text[stringPosition - 2]) || !Helper.IsValidNameChar(codeInput.text[stringPosition]))
				{
					OpenCodeCompleterAtCarret();
				}
				else if (codeCompleter.IsOpen)
				{
					codeCompleter.Close();
				}
			}
			else if (codeCompleter.IsOpen)
			{
				codeCompleter.Close();
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
				int stringPosition2 = codeInput.stringPosition;
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
						codeInput.stringPosition = stringPosition2 - (1 + num3);
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
		InsertNewLineIndentation(inserted);
	}

	private void InsertNewLineIndentation(string inserted)
	{
		if (!inserted.EndsWith("\n", StringComparison.Ordinal))
		{
			return;
		}
		int num = codeInput.stringPosition - 1;
		if (num > 0 && num < codeInput.text.Length && codeInput.text[num] == '\n')
		{
			Token lastNewLine = tokens.GetLastNewLine(num);
			string text = ((lastNewLine != null) ? lastNewLine.value.Remove(0, 1) : "");
			if (num - 1 > 0 && codeInput.text[num - 1] == ':' && lastNewLine != null)
			{
				text += (text.StartsWith(' ') ? "    " : ((object)'\t'));
			}
			codeInput.text = codeInput.text.Insert(num + 1, text);
			codeInput.stringPosition += text.Length;
		}
	}

	public void OpenCodeCompleterAtCarret()
	{
		if (isExecuting || codeInput.readOnly || codeInput.IMECompositionRange.length > 0)
		{
			return;
		}
		int num = Mathf.Clamp(codeInput.stringPosition, 0, codeInput.text.Length);
		int num2 = num;
		while (num2 > 0 && Helper.IsValidNameChar(codeInput.text[num2 - 1]))
		{
			num2--;
		}
		string text = codeInput.text.Substring(num2, num - num2);
		if (text.Length <= 0 || char.IsLetter(text[0]) || text[0] == '_')
		{
			List<string> optionStrings = ((num2 > 0 && codeInput.text[num2 - 1] == '.') ? GetSubWordList(GetWordBefore(num2 - 2)) : ((!IsImportStatement(codeInput.text, num2)) ? GetWordList() : workspace.codeWindows.Values.Select((CodeWindow cw) => cw.fileName).ToList()));
			RectTransform component = codeInput.GetComponent<RectTransform>();
			Vector3 position = ((codeInput.text.Length == 0) ? Vector3.zero : ((num2 < codeInput.text.Length) ? codeInput.GetCharacterAtSourceIndex(num2).bottomLeft : codeInput.GetCharacterAtSourceIndex(num2 - 1).bottomRight));
			position = codeInput.transform.TransformPoint(position) + (Vector3)BlinkManager.GetCodeOffset(component);
			workspace.codeCompleter.Open(position, optionStrings, text, num2, this);
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
		int startStringIndex = codeCompleter.startStringIndex;
		int num = startStringIndex + codeCompleter.TypedLength + (removeExtraChar ? 1 : 0);
		codeInput.text = codeInput.text.Remove(startStringIndex, num - startStringIndex).Insert(startStringIndex, codeCompleter.Selection);
		codeInput.stringPosition = startStringIndex + codeCompleter.Selection.Length;
	}

	public void UpdateSearch(string word, int selectedIndex = -1)
	{
		searchWord = word;
		selectedSearchIndex = selectedIndex;
		codeText.text = CodeUtilities.SyntaxColor2(codeInput.TextWithComposition, ThemeManager.Inst.Theme, word, selectedIndex, codeInput.IMECompositionRange);
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

	public bool UpdateTokens()
	{
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
		UpdateSearch(searchWord, selectedSearchIndex);
		string text = codeInput.text;
		if (text == prevText)
		{
			return false;
		}
		if (isExecuting)
		{
			MainSim.Inst.StopMainExecution();
		}
		prevText = text;
		dirty = true;
		Tokenizer.Tokenize(text, out tokens);
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
			UpdateErrorPosition(revealError: true);
		}
	}

	private void UpdateErrorPosition(bool revealError)
	{
		if (errorString == null)
		{
			return;
		}
		Window component = GetComponent<Window>();
		Vector3 vector;
		Vector3 right;
		if ((object)component != null && component.isMinimized)
		{
			if (errorMessage.transform.parent != base.transform)
			{
				errorMessage.transform.SetParent(base.transform);
			}
			Rect rect = ((RectTransform)base.transform).rect;
			vector = base.transform.TransformPoint(new Vector3((rect.xMin + rect.xMax) / 2f, rect.yMin + 10f, 0f));
			right = vector;
			if (revealError && OptionHolder.GetString("focus errors", "enabled") == "enabled")
			{
				workspace.MoveCameraTo(component);
			}
		}
		else
		{
			if (errorMessage.transform.parent != codeInput.transform)
			{
				errorMessage.transform.SetParent(codeInput.transform);
			}
			if (codeInput.textComponent.textInfo.characterCount == 0)
			{
				return;
			}
			TMP_CharacterInfo characterAtSourceIndex = codeInput.GetCharacterAtSourceIndex(errorStartIndex);
			TMP_CharacterInfo characterAtSourceIndex2 = codeInput.GetCharacterAtSourceIndex(Math.Max(errorStartIndex, errorEndIndex));
			Vector3 vector2 = BlinkManager.GetCodeOffset(codeInput.GetComponent<RectTransform>());
			if (revealError)
			{
				ScrollToStringPosition(errorStartIndex);
			}
			vector = codeInput.transform.TransformPoint(characterAtSourceIndex.bottomLeft) + vector2;
			right = codeInput.transform.TransformPoint(characterAtSourceIndex2.bottomRight) + vector2;
			if (revealError && component != null && OptionHolder.GetString("focus errors", "enabled") == "enabled")
			{
				workspace.MoveCameraTo(component, alwaysMoveWindow: false, errorStartIndex, codeInput);
			}
		}
		RectTransform visibleArea = (((object)component != null && component.isMinimized) ? null : scrollViewRect);
		if (revealError)
		{
			errorMessage.ShowError(errorString, vector, right, visibleArea);
		}
		else
		{
			errorMessage.UpdatePosition(vector, right, visibleArea);
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
		if (MainSim.Inst.IsUnlocked("import"))
		{
			list.Add("__name__");
		}
		list.Sort();
		return list;
	}

	private List<string> GetSubWordList(string domain)
	{
		IEnumerable<string> enumerable = domain switch
		{
			"Entities" => from f in ResourceManager.GetAllEntitites()
				select f.objectName into s
				where MainSim.Inst.IsUnlocked(s)
				select s, 
			"Grounds" => from f in ResourceManager.GetAllGrounds()
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
				where l.dlc switch
				{
					EDlcType.None => MainSim.Inst.IsUnlocked("leaderboard"), 
					EDlcType.Mining => MainSim.Inst.IsUnlocked("underground_leaderboard"), 
					_ => false, 
				}
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
			Vector3 bottomLeft = codeInput.GetCharacterAtSourceIndex(hoverWordStart).bottomLeft;
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
public class DLCStatusButton : MonoBehaviour
{
	public EDlcType dlc;

	public string openUrl;

	public GameObject checkmark;

	private Button button;

	private void OnEnable()
	{
		if (TryGetComponent<Button>(out button))
		{
			button.onClick.AddListener(OnClick);
		}
		bool active = PlatformManager.IsDlcInstalled(dlc);
		if (checkmark != null)
		{
			checkmark.SetActive(active);
		}
	}

	private void OnDisable()
	{
		if (button != null)
		{
			button.onClick.RemoveListener(OnClick);
		}
	}

	private void OnClick()
	{
		TitleWindow.OpenSteamUrl(openUrl);
	}
}
public class DocsWindow : MonoBehaviour
{
	private const int MaxHistorySize = 64;

	private const string TechTreeLink = "tech_tree";

	private const string HomeDoc = "docs/home.md";

	[SerializeField]
	private ScrollRect scrollView;

	[SerializeField]
	private RectTransform container;

	[SerializeField]
	private MarkdownText markdownPrefab;

	[SerializeField]
	private ColoredButton homeButton;

	[SerializeField]
	private ColoredButton backButton;

	private readonly Deque<(string doc, float scroll)> history = new Deque<(string, float)>(64);

	public string openDoc;

	public string fullOpenDoc;

	public MarkdownText OpenMarkdownText { get; private set; }

	public void LoadDoc(string doc)
	{
		if (!string.IsNullOrEmpty(openDoc) && openDoc != doc)
		{
			if (history.Count >= 64)
			{
				history.PopFront();
			}
			history.Add((openDoc, scrollView.verticalNormalizedPosition));
		}
		DisplayDoc(doc);
	}

	private void DisplayDoc(string doc)
	{
		if (container.childCount > 0)
		{
			Transform child = container.GetChild(0);
			container.DetachChildren();
			UnityEngine.Object.Destroy(child.gameObject);
		}
		StringBuilder stringBuilder = new StringBuilder();
		UnlockSO missingUnlock = GetMissingUnlock(doc);
		if (missingUnlock != null)
		{
			stringBuilder.Append(string.Format(Localizer.Localize("missing_unlock_page"), Localizer.Localize(missingUnlock.unlockName), TooltipUtils.UnlockTooltip(missingUnlock.unlockName).text));
		}
		else if (doc.StartsWith("functions/"))
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
		else if (doc.StartsWith("grounds/"))
		{
			string text4 = doc.Substring("grounds/".Length);
			stringBuilder.Append(TooltipUtils.GroundTooltip(text4).text);
			AddUnlockedIn(stringBuilder, text4);
		}
		else
		{
			stringBuilder.Append(Localizer.LoadDoc(doc));
		}
		container.anchoredPosition = new Vector2(0f, 0f);
		MarkdownText markdownText = UnityEngine.Object.Instantiate(markdownPrefab, container);
		fullOpenDoc = stringBuilder.ToString();
		openDoc = doc;
		markdownText.BasePath = Path.GetDirectoryName(Path.Combine(Application.streamingAssetsPath, "Languages", Localizer.Lang, doc));
		markdownText.Setup(fullOpenDoc, LinkCalled);
		OpenMarkdownText = markdownText;
		UpdateButtons();
		MainSim.Inst.workspace.searchBox.RefreshSearchResults();
	}

	private UnlockSO GetMissingUnlock(string doc)
	{
		if (doc == "docs/output.md")
		{
			return null;
		}
		string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(doc);
		UnlockSO unlockSO = ResourceManager.GetUnlockOf(fileNameWithoutExtension) ?? ResourceManager.GetUnlockOf(fileNameWithoutExtension.ToLowerInvariant());
		if (unlockSO == null || MainSim.Inst.IsUnlocked(fileNameWithoutExtension))
		{
			return null;
		}
		return unlockSO;
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
		else if (link == "tech_tree")
		{
			if (!MainSim.Inst.researchMenu.IsOpen)
			{
				MainSim.Inst.researchMenu.OpenCloseMenu();
			}
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

	public async void GoBack()
	{
		if (history.TryDequeue(out var item))
		{
			DisplayDoc(item.doc);
			await Awaitable.NextFrameAsync(base.destroyCancellationToken);
			await Awaitable.NextFrameAsync(base.destroyCancellationToken);
			if (!(item.doc != openDoc))
			{
				scrollView.verticalNormalizedPosition = item.scroll;
			}
		}
	}

	private void UpdateButtons()
	{
		if (homeButton != null)
		{
			homeButton.Interactable = openDoc != "docs/home.md";
		}
		if (backButton != null)
		{
			backButton.gameObject.SetActive(history.Count > 0);
		}
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

	private RectTransform visibleArea;

	private readonly Vector3[] corners = new Vector3[4];

	private bool updateOnEnable;

	private bool playSoundOnUpdate;

	private bool hasDisplayedError;

	public bool IsShowing()
	{
		return base.gameObject.activeInHierarchy;
	}

	public void ShowError(string error, Vector3 left, Vector3 right, RectTransform visibleArea = null)
	{
		this.error = error;
		this.left = left;
		this.right = right;
		this.visibleArea = visibleArea;
		if (!hasDisplayedError)
		{
			hasDisplayedError = true;
			playSoundOnUpdate = true;
		}
		if (base.gameObject.activeInHierarchy)
		{
			UpdateErrorMessage();
			return;
		}
		updateOnEnable = true;
		base.gameObject.SetActive(value: true);
	}

	public void UpdatePosition(Vector3 left, Vector3 right, RectTransform visibleArea = null)
	{
		this.left = left;
		this.right = right;
		this.visibleArea = visibleArea;
		if (base.gameObject.activeInHierarchy)
		{
			UpdateErrorPosition();
		}
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
		errorText.text = Localizer.Localize(error);
		RectTransform obj = (RectTransform)base.transform;
		obj.sizeDelta = new Vector2(obj.sizeDelta.x, errorText.preferredHeight + errorBoxHeight);
		UpdateErrorPosition();
		ColorTheme theme = ThemeManager.Inst.Theme;
		background.color = theme.code.ErrorBackgroundColor;
		messageBorder.color = theme.code.ErrorBorderColor;
		errorText.color = theme.code.ErrorMessageColor;
		errorTitle.color = theme.code.ErrorTitleColor;
		if (codeBorder.TryGetComponent<Image>(out var component))
		{
			component.color = theme.code.ErrorBorderColor;
		}
		if (playSoundOnUpdate)
		{
			playSoundOnUpdate = false;
			FMODSoundManager.PlaySound(SoundEffectType.CodeError, default(Vector3));
		}
	}

	private void UpdateErrorPosition()
	{
		RectTransform rectTransform = (RectTransform)base.transform;
		rectTransform.position = (left + right) / 2f;
		codeBorder.sizeDelta = new Vector2((rectTransform.InverseTransformPoint(right) - rectTransform.InverseTransformPoint(left)).x + codeBoxMargin, codeBorder.sizeDelta.y);
		if (visibleArea != null)
		{
			ClampToVisibleArea(rectTransform);
		}
	}

	private void ClampToVisibleArea(RectTransform errorTransform)
	{
		visibleArea.GetWorldCorners(corners);
		float x = corners[0].x;
		float y = corners[0].y;
		float x2 = corners[2].x;
		float y2 = corners[2].y;
		codeBorder.GetWorldCorners(corners);
		float num = (corners[0].x + corners[2].x) / 2f;
		float num2 = (corners[0].y + corners[2].y) / 2f;
		float num3 = Mathf.Clamp(num, x, x2);
		float num4 = Mathf.Clamp(num2, y, y2);
		Vector3 vector = new Vector3(num3 - num, num4 - num2, 0f);
		errorTransform.position += vector;
	}

	public void Close()
	{
		hasDisplayedError = false;
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
			FMODSoundManager.PlaySound(SoundEffectType.CosmeticUnlock, default(Vector3));
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
public class HorizontalFitLayoutElement : LayoutElement
{
	private RectTransform rt;

	private Image image;

	private VideoUI video;

	public override float preferredHeight
	{
		get
		{
			float num = base.preferredHeight;
			if (num < 0f)
			{
				float reverseAspectRatio = GetReverseAspectRatio();
				if (reverseAspectRatio >= 0f)
				{
					num = rt.rect.width * reverseAspectRatio;
				}
			}
			return num;
		}
		set
		{
			base.preferredHeight = value;
		}
	}

	protected override void Awake()
	{
		base.Awake();
		TryGetComponent<RectTransform>(out rt);
		TryGetComponent<Image>(out image);
		TryGetComponent<VideoUI>(out video);
	}

	private float GetReverseAspectRatio()
	{
		if (image != null)
		{
			return image.preferredHeight / image.preferredWidth;
		}
		if (video != null && video.fitter != null)
		{
			return 1f / video.fitter.aspectRatio;
		}
		return -1f;
	}
}
[RequireComponent(typeof(Image))]
public class ImageLoader : MonoBehaviour
{
	public string image;

	private Image img;

	public bool IsLoading { get; private set; }

	public async void Show(string image, string basePath = null)
	{
		try
		{
			await ShowAsync(image, basePath, base.destroyCancellationToken);
		}
		catch (OperationCanceledException)
		{
		}
	}

	public async Awaitable ShowAsync(string image, string basePath = null, CancellationToken cancellation = default(CancellationToken))
	{
		if (!(img == null) || TryGetComponent<Image>(out img))
		{
			this.image = image;
			img.sprite = null;
			IsLoading = true;
			Sprite sprite = await ResolveSprite(image, basePath, cancellation);
			if (img != null)
			{
				img.sprite = sprite;
			}
			IsLoading = false;
		}
	}

	public static async Awaitable<Texture2D> ResolveTexture(string image, string basePath = null, CancellationToken cancellation = default(CancellationToken))
	{
		if (Path.GetExtension(image).Length == 0)
		{
			return ResourceManager.GetSprite(image).texture;
		}
		if (image.StartsWith("file:") || image.StartsWith("http"))
		{
			using (UnityWebRequest request = UnityWebRequestTexture.GetTexture(image, nonReadable: true))
			{
				await Awaitable.FromAsyncOperation(request.SendWebRequest(), cancellation);
				if (request.result != UnityWebRequest.Result.Success)
				{
					UnityEngine.Debug.LogError("ImageLoader: Failed to load image URL '" + image + "'");
					return null;
				}
				return DownloadHandlerTexture.GetContent(request);
			}
		}
		string path = image;
		if (basePath != null && !Path.IsPathFullyQualified(path))
		{
			path = Path.Combine(basePath, path);
		}
		if (!PlatformManager.PlatformHandler.StreamingFileExists(path))
		{
			UnityEngine.Debug.LogError("ImageLoader: Streaming assets image not found '" + path + "'");
			return null;
		}
		byte[] array = await PlatformManager.PlatformHandler.ReadStreamingBytesAsync(path);
		if (array == null)
		{
			UnityEngine.Debug.LogError("ImageLoader: Failed to load streaming assets image '" + path + "'");
			return null;
		}
		Texture2D texture2D = new Texture2D(2, 2, TextureFormat.ARGB32, mipChain: true);
		if (!texture2D.LoadImage(array, markNonReadable: true))
		{
			UnityEngine.Debug.LogError("ImageLoader: Failed to decode streaming assets image '" + path + "'");
			return null;
		}
		return texture2D;
	}

	public static async Awaitable<Sprite> ResolveSprite(string image, string basePath = null, CancellationToken cancellation = default(CancellationToken))
	{
		if (Path.GetExtension(image).Length == 0)
		{
			return ResourceManager.GetSprite(image);
		}
		Texture2D texture2D = await ResolveTexture(image, basePath, cancellation);
		if (texture2D == null)
		{
			return null;
		}
		return Sprite.Create(texture2D, new Rect(0f, 0f, texture2D.width, texture2D.height), Vector2.zero);
	}

	private void OnEnable()
	{
		if (!TryGetComponent<Image>(out img))
		{
			base.enabled = false;
		}
		else if (img.sprite == null && !IsLoading && !string.IsNullOrEmpty(image))
		{
			Show(image);
		}
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
		if (getItemBlock == null)
		{
			return;
		}
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

	public void Disconnect()
	{
		getItemBlock = null;
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

	private bool showProductionRate;

	private string productionRateText;

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
		showProductionRate = item.trackStats && GetComponentInParent<Inventory>() == MainSim.Inst.inv;
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
		bool flag = false;
		if (newAmount != amount && !isAnimating)
		{
			bool increase = newAmount > amount;
			amount = newAmount;
			string text = Helper.NrToText(amount);
			flag = true;
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
		if (updateTooltipCallback != null)
		{
			string text2 = GetProductionRateText();
			if (flag || text2 != productionRateText)
			{
				updateTooltipCallback();
			}
		}
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

	private string GetProductionRateText()
	{
		if (!showProductionRate)
		{
			return null;
		}
		if (!MainSim.Inst.MightBeSimulating())
		{
			Achievements.UpdateSum(MainSim.Inst.GetCurrentTime());
		}
		double number = Achievements.GetSum().GetNumber(item.itemId);
		double number2 = Achievements.GetBest().GetNumber(item.itemId);
		return string.Format(Localizer.Localize("item_tooltip_template_rate"), FormatRate(number), FormatRate(number2));
		static string FormatRate(double value)
		{
			return "<font=\"FiraCode-Regular SDF\"><color=" + ThemeManager.Inst.Theme.code.number + ">" + Helper.NrToText(value) + "</color></font>";
		}
	}

	public TooltipInfo GetTooltipInfo(Action updateTooltipCallback)
	{
		this.updateTooltipCallback = updateTooltipCallback;
		TooltipInfo tooltipInfo = TooltipUtils.ItemTooltip(item.name);
		if (tooltipInfo != null)
		{
			productionRateText = GetProductionRateText();
			if (productionRateText != null)
			{
				tooltipInfo.text = tooltipInfo.text + "\n\n" + productionRateText;
			}
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
		PlatformManager.PlatformHandler.LoadLeaderboard(leaderboardName, score, OnPlayerLoaded, OnEntriesLoaded);
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

	private Color runFailedColor;

	public bool IsRunning => overlay.activeInHierarchy;

	public bool IsLeaderBoardScreenOpen => leaderboardScreen.activeInHierarchy;

	private void Awake()
	{
		runFailedColor = runCancelled.GetComponent<TextMeshProUGUI>().color;
	}

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
		bool flag = timeSpan.TotalMilliseconds > 2147483647.0;
		finishTimeText.text = ((finished && flag) ? ("<size=60%>" + Localizer.Localize("leaderboard_time_limit") + "</size>") : StringFromTimeSpan(timeSpan));
		TextMeshProUGUI component = runCancelled.GetComponent<TextMeshProUGUI>();
		component.text = (finished ? "run_completed" : "run_cancelled");
		component.color = (finished ? Color.white : runFailedColor);
		runCancelled.SetActive(value: true);
		int score = ((finished && !flag) ? ((int)timeSpan.TotalMilliseconds) : 0);
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
public class MarkdownLink : MonoBehaviour, IPointerClickHandler, IEventSystemHandler
{
	public MarkdownText markdown;

	public string url;

	public void OnPointerClick(PointerEventData eventData)
	{
		if (!string.IsNullOrEmpty(url) && !(markdown == null))
		{
			markdown.TriggerLinkClick(url);
		}
	}
}
public class MarkdownText : MonoBehaviour, IPointerMoveHandler, IEventSystemHandler, IPointerExitHandler
{
	private enum SectionType
	{
		Text,
		Image,
		HorizontalRule,
		Custom,
		LeftRight,
		Columns
	}

	private struct TextSection
	{
		public SectionType type;

		public string text;

		public bool isSpoiler;

		public string spoilerText;

		public string rightText;

		public string[] columnItems;

		public int blankLinesBefore;

		public int blankLinesAfter;

		public TextSection(SectionType type, string text, bool isSpoiler, string spoilerText = null, string rightText = null, string[] columnItems = null, int blankLinesBefore = 0, int blankLinesAfter = 0)
		{
			this.type = type;
			this.text = text;
			this.isSpoiler = isSpoiler;
			this.spoilerText = spoilerText;
			this.rightText = rightText;
			this.columnItems = columnItems;
			this.blankLinesBefore = blankLinesBefore;
			this.blankLinesAfter = blankLinesAfter;
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
	private VideoUI videoPrefab;

	[SerializeField]
	private Image horizontalLinePrefab;

	[SerializeField]
	private float horizontalLineSpacing = 20f;

	[SerializeField]
	private float codeExampleMargin = 10f;

	[SerializeField]
	private float codeExampleBottomMargin = 20f;

	[SerializeField]
	private OutputText outputPrefab;

	[SerializeField]
	private Inventory invPrefab;

	[SerializeField]
	private CodeExample codeExamplePrefab;

	private List<CodeInputField> textFields = new List<CodeInputField>();

	private string currentSearchTerm = "";

	private int currentSearchOccurrenceIndex = -1;

	private bool refreshSearchAfterColumnRebuild;

	private Action<string> clickLinkCallback;

	private string downLinkID;

	private HoverInfo hoverInfo;

	public string BasePath { get; set; }

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
		if (refreshSearchAfterColumnRebuild)
		{
			refreshSearchAfterColumnRebuild = false;
			ApplySearch(currentSearchTerm, currentSearchOccurrenceIndex);
		}
		if (Input.GetKeyDown(KeyCode.Mouse0))
		{
			downLinkID = hoverInfo.linkID;
		}
		else if (Input.GetKeyUp(KeyCode.Mouse0))
		{
			ReleaseLinkClick();
		}
	}

	private void ReleaseLinkClick()
	{
		string text = downLinkID;
		downLinkID = null;
		if (!string.IsNullOrEmpty(text) && text == hoverInfo.linkID)
		{
			TriggerLinkClick(text);
		}
	}

	private void OnDisable()
	{
		downLinkID = null;
		hoverInfo = default(HoverInfo);
	}

	public void TriggerLinkClick(string link)
	{
		clickLinkCallback?.Invoke(link);
	}

	public int UpdateSearch(string searchTerm, int occurenceIndex)
	{
		currentSearchTerm = searchTerm;
		currentSearchOccurrenceIndex = occurenceIndex;
		return ApplySearch(searchTerm, occurenceIndex);
	}

	private int ApplySearch(string searchTerm, int occurenceIndex)
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

	public static string ProcessMetadata(string text, Dictionary<string, string> metadata)
	{
		Match match = new Regex("<meta\\s+((?:\"(?:[^\"\\\\]|\\\\\"|\\\\\\\\)*\"|[^\">])*?)\\/?>\\s*").Match(text);
		if (!match.Success)
		{
			return text;
		}
		StringBuilder stringBuilder = new StringBuilder();
		int num = 0;
		while (match.Success)
		{
			stringBuilder.Append(text.Substring(num, match.Index - num));
			num = match.Index + match.Length;
			if (metadata != null)
			{
				Match match2 = new Regex("\\s*([^=]+?)\\s*=\\s*(?:\"([^\"]+)\"|([^\\s]+))").Match(match.Groups[1].Value);
				while (match2.Success)
				{
					string value = match2.Groups[1].Value;
					string value2 = (match2.Groups[2].Success ? match2.Groups[2] : match2.Groups[3]).Value;
					metadata[value] = value2;
					match2 = match2.NextMatch();
				}
			}
			match = match.NextMatch();
		}
		stringBuilder.Append(text.Substring(num));
		return stringBuilder.ToString();
	}

	public void Setup(string text, Action<string> clickLinkCallback, Dictionary<string, string> metadata = null)
	{
		text = text.Replace("\r\n", "\n");
		this.clickLinkCallback = clickLinkCallback;
		ColorTheme theme = ThemeManager.Inst.Theme;
		List<Func<TextSection, IEnumerable<TextSection>>> obj = new List<Func<TextSection, IEnumerable<TextSection>>>
		{
			ApplyDlcs,
			InsertCustomTexts,
			(TextSection section) => Enumerable.Repeat(new TextSection(section.type, CodeUtilities.ApplyCodeTags(section.text), section.isSpoiler), 1),
			(TextSection section) => Enumerable.Repeat(new TextSection(section.type, ApplyBoldTags(section.text), section.isSpoiler), 1),
			ApplyHeadings,
			ApplyLinks,
			ApplyUnlocks,
			ApplySpoilers,
			ApplyImages,
			InsertCustomSections,
			ApplyHorizontalRules,
			ApplyAlignment,
			ApplyColumns
		};
		text = ProcessMetadata(text, metadata);
		IEnumerable<TextSection> enumerable = Enumerable.Repeat(new TextSection(SectionType.Text, text, isSpoiler: false), 1);
		foreach (Func<TextSection, IEnumerable<TextSection>> stage in obj)
		{
			enumerable = enumerable.SelectMany((TextSection section) => (section.type != SectionType.Text) ? Enumerable.Repeat(section, 1) : stage(section));
		}
		Transform transform = null;
		SpoilerWarning spoilerWarning = null;
		foreach (TextSection item in enumerable)
		{
			if (!item.isSpoiler)
			{
				transform = null;
				spoilerWarning = null;
			}
			else if (transform == null)
			{
				transform = CreateSpoilerContainer();
				spoilerWarning = CreateSpoilerWarning(transform, item.spoilerText);
			}
			if (string.IsNullOrEmpty(item.text) && (item.type != SectionType.LeftRight || string.IsNullOrEmpty(item.rightText)) && item.type != SectionType.Columns)
			{
				continue;
			}
			Transform parent = (item.isSpoiler ? transform : base.transform);
			switch (item.type)
			{
			case SectionType.Text:
				CreateTextField(item.text, parent, theme);
				break;
			case SectionType.LeftRight:
				CreateLeftRightSection(item, parent, theme);
				break;
			case SectionType.Columns:
				CreateColumnsSection(item, parent, theme);
				break;
			case SectionType.Image:
			{
				int num5 = item.text.IndexOf('\u001e');
				if (num5 < 0)
				{
					break;
				}
				string text3 = item.text.Substring(0, num5);
				string text4 = item.text.Substring(num5 + 1);
				string text5 = null;
				num5 = text4.IndexOf('\u001e');
				if (num5 > 0)
				{
					text5 = text4.Substring(num5 + 1);
					text4 = text4.Substring(0, num5);
				}
				bool num6 = text4.StartsWith("video:", StringComparison.OrdinalIgnoreCase);
				UnityEngine.Component component = null;
				if (!num6)
				{
					Image image = UnityEngine.Object.Instantiate(imgPrefab, parent);
					component = image;
					if (image.TryGetComponent<ImageLoader>(out var component2))
					{
						component2.Show(text4, BasePath);
					}
					else
					{
						image.sprite = ResourceManager.GetSprite(text4);
					}
				}
				else
				{
					UnityEngine.Component component3 = (component = UnityEngine.Object.Instantiate(videoPrefab, parent));
					text4 = text4.Substring(6);
					((VideoUI)component3).Play(text4, (string)null, BasePath);
				}
				if (!string.IsNullOrEmpty(text5) && component.TryGetComponent<MarkdownLink>(out var component4))
				{
					component4.markdown = this;
					component4.url = text5;
				}
				if (!component.TryGetComponent<LayoutElement>(out var component5))
				{
					break;
				}
				int num7 = text3.IndexOf('|');
				if (num7 >= 0)
				{
					string text6 = text3.Substring(num7 + 1);
					int num8 = text6.IndexOf('x');
					string text7 = null;
					string text8 = null;
					if (num8 >= 0)
					{
						text7 = text6.Substring(0, num8);
						text8 = text6.Substring(num8 + 1);
					}
					if (text7 != null && int.TryParse(text7, out var result))
					{
						component5.preferredWidth = result;
					}
					else
					{
						component5.flexibleWidth = 1f;
					}
					if (text8 != null && int.TryParse(text8, out var result2))
					{
						component5.preferredHeight = result2;
					}
					else
					{
						component5.flexibleHeight = 1f;
					}
				}
				break;
			}
			case SectionType.HorizontalRule:
				CreateHorizontalRule(item, parent, theme);
				break;
			case SectionType.Custom:
				if (item.text == "output")
				{
					OutputText outputText = UnityEngine.Object.Instantiate(outputPrefab, parent);
					theme.docs.text.ApplyTo(outputText.Text);
					outputText.CoupleToSim();
				}
				else if (item.text.StartsWith("codeexample"))
				{
					int num = item.text.IndexOf('{');
					int num2 = item.text.IndexOf("#SETUP");
					int num3 = item.text.IndexOf("#CODE");
					if (num != -1 && num3 >= num)
					{
						int num4 = ((num2 != -1) ? num2 : num3);
						string text2 = item.text.Substring(num, num4 - num);
						string setupCode = ((num2 != -1) ? item.text.Substring(num2 + 7, num3 - (num2 + 7)) : "");
						string code = item.text.Substring(num3 + 6).TrimEnd();
						CodeExample.CodeExampleSettings settings;
						try
						{
							settings = JsonUtility.FromJson<CodeExample.CodeExampleSettings>(text2);
						}
						catch (Exception arg)
						{
							UnityEngine.Debug.LogError("Failed to parse codeexample settings in docs directory '" + BasePath + "'. " + $"Transformed JSON:\n{text2}\n{arg}");
							settings = new CodeExample.CodeExampleSettings();
						}
						CreateVerticalSpacer(parent, codeExampleMargin);
						UnityEngine.Object.Instantiate(codeExamplePrefab, parent).Setup(code, setupCode, settings);
						CreateVerticalSpacer(parent, codeExampleBottomMargin);
					}
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
						up = ((array[1] == "tooltip") ? ((Func<ItemBlock>)(() => MainSim.Inst.workspace.tooltip.Info?.itemBlock)) : ((!(array[1] == "tooltip_ground")) ? ((Func<ItemBlock>)(() => (ItemBlock)null)) : ((Func<ItemBlock>)(() => MainSim.Inst.workspace.tooltip.Info?.groundItemBlock))));
					}
					else if (array[2] == "object")
					{
						EntitySO fo = ResourceManager.GetEntity(array[3]);
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
					UnityEngine.Object.Instantiate(invPrefab, parent).SetUp(up);
				}
				break;
			}
			if (spoilerWarning != null)
			{
				spoilerWarning.transform.SetAsLastSibling();
			}
		}
	}

	private Transform CreateSpoilerContainer()
	{
		GameObject obj = new GameObject("Spoiler", typeof(RectTransform), typeof(VerticalLayoutGroup));
		obj.layer = base.gameObject.layer;
		obj.transform.SetParent(base.transform, worldPositionStays: false);
		VerticalLayoutGroup component = obj.GetComponent<VerticalLayoutGroup>();
		component.childControlWidth = true;
		component.childControlHeight = true;
		component.childForceExpandWidth = false;
		component.childForceExpandHeight = true;
		return obj.transform;
	}

	private void CreateVerticalSpacer(Transform parent, float height)
	{
		GameObject obj = new GameObject("CodeExampleMargin", typeof(RectTransform), typeof(LayoutElement));
		obj.layer = base.gameObject.layer;
		obj.transform.SetParent(parent, worldPositionStays: false);
		LayoutElement component = obj.GetComponent<LayoutElement>();
		component.minHeight = height;
		component.preferredHeight = height;
		component.flexibleHeight = 0f;
	}

	private IEnumerable<TextSection> ApplyDlcs(TextSection section)
	{
		section.text = ApplyDlcTags(section.text, PlatformManager.IsDlcInstalled(EDlcType.Mining));
		return Enumerable.Repeat(section, 1);
	}

	public static string ApplyDlcTags(string text, bool isDlcInstalled)
	{
		return Regex.Replace(text, "<dlc>(.*?)</dlc>", (Match match) => (!isDlcInstalled) ? "" : match.Groups[1].Value, RegexOptions.Singleline);
	}

	public static string ApplyBoldTags(string text)
	{
		string[] array = Regex.Split(text, "(<font=\"FiraCode-Regular SDF\">[\\s\\S]*?</font>)");
		for (int i = 0; i < array.Length; i += 2)
		{
			array[i] = Regex.Replace(array[i], "(?<!\\\\)\\*\\*(?=\\S)(?<content>[^\\r\\n]*?\\S)(?<!\\\\)\\*\\*", "<b>${content}</b>");
		}
		return string.Concat(array);
	}

	private CodeInputField CreateTextField(string text, Transform parent, ColorTheme theme)
	{
		CodeInputField codeInputField = UnityEngine.Object.Instantiate(textPrefab, parent);
		theme.docs.text.ApplyTo(codeInputField);
		ReserveUnderlineMeshCapacity(codeInputField.textComponent, text);
		codeInputField.text = text;
		textFields.Add(codeInputField);
		return codeInputField;
	}

	private SpoilerWarning CreateSpoilerWarning(Transform parent, string text)
	{
		SpoilerWarning obj = UnityEngine.Object.Instantiate(spoilerWarning, parent);
		obj.SetText(text);
		return obj;
	}

	private void ReserveUnderlineMeshCapacity(TMP_Text textComponent, string text)
	{
		if (!text.Contains("<u>"))
		{
			return;
		}
		int num = Mathf.NextPowerOfTwo(text.Length);
		TMP_TextInfo textInfo = textComponent.textInfo;
		if (textInfo.meshInfo.Length == 0 || textComponent.mesh == null)
		{
			UnderlineMeshCapacityReserver underlineMeshCapacityReserver = textComponent.GetComponent<UnderlineMeshCapacityReserver>();
			if (underlineMeshCapacityReserver == null)
			{
				underlineMeshCapacityReserver = textComponent.gameObject.AddComponent<UnderlineMeshCapacityReserver>();
			}
			underlineMeshCapacityReserver.Initialize(num);
		}
		else if (textInfo.meshInfo[0].vertices == null)
		{
			textInfo.meshInfo[0] = new TMP_MeshInfo(textComponent.mesh, num);
		}
		else if (textInfo.meshInfo[0].vertices.Length < num * 4)
		{
			textInfo.meshInfo[0].ResizeMeshInfo(num);
		}
	}

	private void CreateLeftRightSection(TextSection section, Transform parent, ColorTheme theme)
	{
		GameObject obj = new GameObject("LeftRight", typeof(RectTransform), typeof(HorizontalLayoutGroup))
		{
			layer = base.gameObject.layer
		};
		RectTransform component = obj.GetComponent<RectTransform>();
		component.SetParent(parent, worldPositionStays: false);
		HorizontalLayoutGroup component2 = obj.GetComponent<HorizontalLayoutGroup>();
		component2.childControlWidth = true;
		component2.childControlHeight = true;
		component2.childForceExpandWidth = true;
		component2.childForceExpandHeight = true;
		CreateTextField(section.text, component, theme);
		CreateTextField(section.rightText, component, theme).textComponent.horizontalAlignment = HorizontalAlignmentOptions.Right;
	}

	private void CreateColumnsSection(TextSection section, Transform parent, ColorTheme theme)
	{
		GameObject gameObject = new GameObject("Columns", typeof(RectTransform), typeof(WrappingLayoutGroup));
		gameObject.layer = base.gameObject.layer;
		RectTransform component = gameObject.GetComponent<RectTransform>();
		component.SetParent(parent, worldPositionStays: false);
		CodeInputField[] array = new CodeInputField[WrappingLayoutGroup.GetMaxPopulatedColumnCount(section.columnItems.Length)];
		for (int i = 0; i < array.Length; i++)
		{
			array[i] = CreateTextField("", component, theme);
		}
		gameObject.GetComponent<WrappingLayoutGroup>().Initialize(section.columnItems, array, SetColumnText);
	}

	private void SetColumnText(CodeInputField textField, string text)
	{
		ReserveUnderlineMeshCapacity(textField.textComponent, text);
		textField.text = text;
		hoverInfo = default(HoverInfo);
		refreshSearchAfterColumnRebuild |= !string.IsNullOrEmpty(currentSearchTerm);
	}

	private void CreateHorizontalRule(TextSection section, Transform parent, ColorTheme theme)
	{
		GameObject gameObject = new GameObject("HorizontalRule", typeof(RectTransform), typeof(LayoutElement));
		gameObject.layer = base.gameObject.layer;
		RectTransform component = gameObject.GetComponent<RectTransform>();
		component.SetParent(parent, worldPositionStays: false);
		Image image = UnityEngine.Object.Instantiate(horizontalLinePrefab, component);
		LayoutElement component2 = image.GetComponent<LayoutElement>();
		float minHeight = component2.minHeight;
		component2.ignoreLayout = true;
		float num = (float)section.blankLinesBefore * horizontalLineSpacing;
		float num2 = (float)section.blankLinesAfter * horizontalLineSpacing;
		LayoutElement component3 = gameObject.GetComponent<LayoutElement>();
		component3.preferredHeight = num + minHeight + num2;
		component3.flexibleWidth = 1f;
		RectTransform rectTransform = image.rectTransform;
		rectTransform.anchorMin = new Vector2(0f, 0f);
		rectTransform.anchorMax = new Vector2(1f, 0f);
		rectTransform.anchoredPosition = new Vector2(0f, num2 + minHeight * 0.5f);
		rectTransform.sizeDelta = new Vector2(0f, minHeight);
		Color color = theme.docs.text.TextColor;
		color.a *= horizontalLinePrefab.color.a;
		image.color = color;
		image.raycastTarget = false;
	}

	public void UpdateText(string text)
	{
		ClearText();
		Setup(text, clickLinkCallback);
	}

	public void ClearText()
	{
		for (int num = base.transform.childCount - 1; num >= 0; num--)
		{
			UnityEngine.Object.Destroy(base.transform.GetChild(num).gameObject);
		}
		textFields.Clear();
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
			string value = $"<size={num2}px>{arg}</size><line-height=50%>\n</line-height>";
			stringBuilder.Insert(capture.Index, value);
		}
		section.text = stringBuilder.ToString();
		return Enumerable.Repeat(section, 1);
	}

	private IEnumerable<TextSection> ApplyLinks(TextSection section)
	{
		ColorTheme theme = ThemeManager.Inst.Theme;
		Regex regex = new Regex("(?<!!)\\[(?!!).*?\\]\\(.*?\\)");
		StringBuilder stringBuilder = new StringBuilder(section.text);
		foreach (Match item in regex.Matches(section.text).Reverse())
		{
			Capture capture = item.Captures.First();
			int num = capture.Value.IndexOf(']');
			string arg = capture.Value.Substring(1, num - 1);
			string text = capture.Value.Substring(num + 2, capture.Value.Length - (num + 2) - 1);
			stringBuilder.Remove(capture.Index, capture.Length);
			if (PlatformManager.IsDlcInstalled(ResourceManager.GetDlcForLink(text)))
			{
				string value = $"<font=\"FiraCode-Regular SDF\"><color={theme.docs.link}><u><link=\"{text}\">{arg}</link></u></color></font>";
				stringBuilder.Insert(capture.Index, value);
			}
		}
		section.text = stringBuilder.ToString();
		return Enumerable.Repeat(section, 1);
	}

	private IEnumerable<TextSection> ApplyAlignment(TextSection section)
	{
		Regex regex = new Regex("(?m)^(?<left>[^\\r\\n]*?)<right>(?<right>[^\\r\\n]*?)(?:</right>)?[ \\t]*\\r?(?:\\n<right>(?<right>[^\\r\\n]*?)(?:</right>)?[ \\t]*\\r?)*$");
		List<TextSection> list = new List<TextSection>();
		int num = 0;
		foreach (Match item in regex.Matches(section.text))
		{
			string value = item.Groups["left"].Value;
			string rightText = string.Join("\n", item.Groups["right"].Captures.Select((Capture capture) => capture.Value));
			int num2 = item.Index;
			if (num2 > num && section.text[num2 - 1] == '\n')
			{
				num2--;
				if (num2 > num && section.text[num2 - 1] == '\r')
				{
					num2--;
				}
			}
			list.Add(new TextSection(SectionType.Text, ApplyLineAlignment(section.text.Substring(num, num2 - num)), section.isSpoiler, section.spoilerText));
			list.Add(new TextSection(SectionType.LeftRight, value, section.isSpoiler, section.spoilerText, rightText));
			num = item.Index + item.Length;
			if (num < section.text.Length && section.text[num] == '\n')
			{
				num++;
			}
		}
		if (list.Count == 0)
		{
			section.text = ApplyLineAlignment(section.text);
			return Enumerable.Repeat(section, 1);
		}
		list.Add(new TextSection(SectionType.Text, ApplyLineAlignment(section.text.Substring(num)), section.isSpoiler, section.spoilerText));
		return list;
	}

	private string ApplyLineAlignment(string text)
	{
		return text.Replace("<right>", "<align=right>").Replace("</right>", "</align>");
	}

	private IEnumerable<TextSection> ApplyColumns(TextSection section)
	{
		Regex regex = new Regex("<columns>(?<content>[\\s\\S]*?)</columns>");
		List<TextSection> list = new List<TextSection>();
		int num = 0;
		foreach (Match item in regex.Matches(section.text))
		{
			string[] array = (from item in Regex.Split(item.Groups["content"].Value.Trim('\r', '\n'), "\\r?\\n")
				where !string.IsNullOrWhiteSpace(item)
				select item.Trim()).ToArray();
			list.Add(new TextSection(SectionType.Text, section.text.Substring(num, item.Index - num), section.isSpoiler, section.spoilerText));
			if (array.Length != 0)
			{
				list.Add(new TextSection(SectionType.Columns, "", section.isSpoiler, section.spoilerText, null, array));
			}
			num = item.Index + item.Length;
		}
		if (list.Count == 0)
		{
			return Enumerable.Repeat(section, 1);
		}
		list.Add(new TextSection(SectionType.Text, section.text.Substring(num), section.isSpoiler, section.spoilerText));
		return list;
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
		Match match = new Regex("!\\[(.*?)\\]\\((.*?)\\)|\\[!\\[(.*?)\\]\\((.*?)\\)\\]\\((.*?)\\)").Match(section.text);
		int num = 0;
		List<TextSection> list = new List<TextSection>();
		while (match.Success)
		{
			if (num < match.Index)
			{
				string text = section.text.Substring(num, match.Index - num);
				list.Add(new TextSection(SectionType.Text, text, section.isSpoiler, section.spoilerText));
			}
			string text2;
			if (match.Groups[1].Success)
			{
				string value = match.Groups[1].Value;
				string value2 = match.Groups[2].Value;
				text2 = value + "\u001e" + value2;
			}
			else
			{
				string value3 = match.Groups[3].Value;
				string value4 = match.Groups[4].Value;
				string value5 = match.Groups[5].Value;
				text2 = value3 + "\u001e" + value4 + "\u001e" + value5;
			}
			TextSection item = new TextSection(SectionType.Image, text2, section.isSpoiler, section.spoilerText);
			list.Add(item);
			num = match.Index + match.Length;
			match = match.NextMatch();
		}
		if (num < section.text.Length)
		{
			string text3 = section.text.Substring(num, section.text.Length - num);
			list.Add(new TextSection(SectionType.Text, text3, section.isSpoiler, section.spoilerText));
		}
		return list;
	}

	private IEnumerable<TextSection> ApplyHorizontalRules(TextSection section)
	{
		Regex regex = new Regex("(?m)^[ \\t]{0,3}(?:(?:\\*[ \\t]*){3,}|(?:-[ \\t]*){3,}|(?:_[ \\t]*){3,})\\r?$");
		List<TextSection> list = new List<TextSection>();
		int num = 0;
		foreach (Match item in regex.Matches(section.text))
		{
			int num2 = section.text.LastIndexOf("<font=\"FiraCode-Regular SDF\">", item.Index, StringComparison.Ordinal);
			int num3 = section.text.LastIndexOf("</font>", item.Index, StringComparison.Ordinal);
			if (num2 <= num3)
			{
				int index = item.Index;
				int num4 = ConsumeLineBreaksBackward(section.text, num, ref index);
				int index2 = item.Index + item.Length;
				int num5 = ConsumeLineBreaksForward(section.text, ref index2);
				list.Add(new TextSection(SectionType.Text, section.text.Substring(num, index - num), section.isSpoiler, section.spoilerText));
				list.Add(new TextSection(SectionType.HorizontalRule, item.Value, section.isSpoiler, section.spoilerText, null, null, Mathf.Max(0, num4 - 1), Mathf.Max(0, num5 - 1)));
				num = index2;
			}
		}
		if (list.Count == 0)
		{
			return Enumerable.Repeat(section, 1);
		}
		list.Add(new TextSection(SectionType.Text, section.text.Substring(num), section.isSpoiler, section.spoilerText));
		return list;
	}

	private int ConsumeLineBreaksBackward(string text, int startIndex, ref int index)
	{
		int num = 0;
		while (index > startIndex)
		{
			if (text[index - 1] == '\n')
			{
				index--;
				if (index > startIndex && text[index - 1] == '\r')
				{
					index--;
				}
			}
			else
			{
				if (text[index - 1] != '\r')
				{
					break;
				}
				index--;
			}
			num++;
		}
		return num;
	}

	private int ConsumeLineBreaksForward(string text, ref int index)
	{
		int num = 0;
		while (index < text.Length)
		{
			if (text[index] == '\r')
			{
				index++;
				if (index < text.Length && text[index] == '\n')
				{
					index++;
				}
			}
			else
			{
				if (text[index] != '\n')
				{
					break;
				}
				index++;
			}
			num++;
		}
		return num;
	}

	private IEnumerable<TextSection> InsertCustomTexts(TextSection section)
	{
		Regex regex = new Regex("{{.*?}}");
		StringBuilder stringBuilder = new StringBuilder(section.text);
		foreach (Match item in regex.Matches(section.text).Reverse())
		{
			Capture capture = item.Captures.First();
			string text = capture.Value.Substring(2, capture.Value.Length - 4);
			stringBuilder.Remove(capture.Index, capture.Length);
			string value = capture.Value;
			if (text.StartsWith("@"))
			{
				value = Localizer.Localize(text.Substring(1));
			}
			stringBuilder.Insert(capture.Index, value);
		}
		section.text = stringBuilder.ToString();
		return Enumerable.Repeat(section, 1);
	}

	private IEnumerable<TextSection> InsertCustomSections(TextSection section)
	{
		Regex regex = new Regex("{{[\\s\\S]*?}}");
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
		for (int num2 = 0; num2 < list.Count; num2++)
		{
			if (list[num2].type == SectionType.Custom && list[num2].text.StartsWith("codeexample"))
			{
				if (num2 > 0)
				{
					TextSection value = list[num2 - 1];
					value.text = value.text.TrimEnd('\r', '\n');
					list[num2 - 1] = value;
				}
				if (num2 + 1 < list.Count)
				{
					TextSection value2 = list[num2 + 1];
					value2.text = value2.text.TrimStart('\r', '\n');
					list[num2 + 1] = value2;
				}
			}
		}
		return list;
	}
}
internal sealed class UnderlineMeshCapacityReserver : MonoBehaviour
{
	private int reservedQuadCount;

	public void Initialize(int reservedQuadCount)
	{
		this.reservedQuadCount = Mathf.Max(this.reservedQuadCount, reservedQuadCount);
		TryReserve();
	}

	private void Awake()
	{
		TryReserve();
	}

	private void OnEnable()
	{
		TryReserve();
	}

	private void TryReserve()
	{
		if (reservedQuadCount == 0)
		{
			return;
		}
		TMP_Text component = GetComponent<TMP_Text>();
		TMP_TextInfo textInfo = component.textInfo;
		if (textInfo.meshInfo.Length != 0 && !(component.mesh == null))
		{
			if (textInfo.meshInfo[0].vertices == null)
			{
				textInfo.meshInfo[0] = new TMP_MeshInfo(component.mesh, reservedQuadCount);
			}
			else if (textInfo.meshInfo[0].vertices.Length < reservedQuadCount * 4)
			{
				textInfo.meshInfo[0].ResizeMeshInfo(reservedQuadCount);
			}
			reservedQuadCount = 0;
			UnityEngine.Object.Destroy(this);
		}
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

	public TitleWorkspace titleWorkspace;

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
		Localizer.Localize("ok");
		bool currentSaveGameExists = Saver.GetCurrentSaveGameExists();
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
		Saver.LoadTitleSave(this);
		StartCoroutine(OpenLatestNews(!currentSaveGameExists));
		RestartAutosave("autosave");
		RestartAutosave("autosave progress");
		OptionHolder.OnOptionChanged -= RestartAutosave;
		OptionHolder.OnOptionChanged += RestartAutosave;
	}

	private void OnDisable()
	{
		Saver.SaveTitleSave(this);
	}

	private IEnumerator OpenLatestNews(bool firstTime)
	{
		yield return null;
		titleWorkspace.FitWindowsIntoContainer();
		titleWorkspace.OpenLatestNews(firstTime);
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
		FMODSoundManager.SetGameStateParam(1f);
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
		if (Saver.Save(MainSim.Inst))
		{
			saveButton.Text = Localizer.Localize("saved");
		}
		Saver.SaveTitleSave(this);
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
		FMODSoundManager.SetGameStateParam(0f);
	}

	public void Options()
	{
		titlePage.gameObject.SetActive(value: false);
		options.gameObject.SetActive(value: true);
		options.Setup();
	}

	public void Quit()
	{
		Saver.SaveTitleSave(this);
		if (MainSim.Inst.dirty)
		{
			List<WarningPopup.ButtonData> buttonsToAdd = new List<WarningPopup.ButtonData>
			{
				new WarningPopup.ButtonData("save", delegate
				{
					if (Saver.Save(MainSim.Inst))
					{
						Application.Quit();
					}
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
			where PlatformManager.IsDlcInstalled(o.dlc)
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
					if (Saver.Save(MainSim.Inst))
					{
						menu.LoadSave(saveName);
						SceneManager.LoadScene(0);
					}
					else
					{
						Saver.StartFileWatcher();
					}
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
public class OpenFeedbackForm : MonoBehaviour
{
	public string formUrl;

	public string simplifiedChineseFormUrl;

	public uint limitToSteamAppId;

	private void OnApplicationQuit()
	{
		if (limitToSteamAppId != 0)
		{
			if (!SteamManager.Initialized)
			{
				return;
			}
			uint appId = SteamUtils.GetAppID().m_AppId;
			if (appId == 0 || appId != limitToSteamAppId)
			{
				return;
			}
		}
		string text = ((OptionHolder.GetString("language", "EN") == "ZH" && !string.IsNullOrEmpty(simplifiedChineseFormUrl)) ? simplifiedChineseFormUrl : formUrl);
		if (!string.IsNullOrEmpty(text))
		{
			Application.OpenURL(text);
		}
	}
}
[RequireComponent(typeof(CodeInputField))]
public class OutputText : MonoBehaviour
{
	[SerializeField]
	private bool displayUISimsOutput;

	private ISimRunner _simRunner;

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

	private ISimRunner SimRunner
	{
		get
		{
			if (_simRunner == null)
			{
				ISimRunner simRunner;
				if (!displayUISimsOutput)
				{
					ISimRunner inst = MainSim.Inst;
					simRunner = inst;
				}
				else
				{
					ISimRunner inst = UISim.Inst;
					simRunner = inst;
				}
				_simRunner = simRunner;
			}
			return _simRunner;
		}
	}

	private void Update()
	{
		if (dirty)
		{
			Text.text = SimRunner.Logger.GetOutputString();
			dirty = false;
		}
	}

	private void OnDestroy()
	{
		DecoupleFromSim();
	}

	public void CoupleToSim()
	{
		dirty = true;
		SimRunner.Logger.OnOutputChanged -= OutputChanged;
		SimRunner.Logger.OnOutputChanged += OutputChanged;
	}

	public void DecoupleFromSim()
	{
		if (SimRunner.Logger != null)
		{
			SimRunner.Logger.OnOutputChanged -= OutputChanged;
		}
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
			if (allUnlock.enabled && PlatformManager.IsDlcInstalled(allUnlock.dlc))
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
		openCloseButton.SetTooltipDescription(flag ? "button_tooltip_open_farm" : "button_tooltip_open_unlock_menu");
		MainSim.Inst.workspace.gameObject.SetActive(!flag);
		base.transform.GetChild(0).gameObject.SetActive(flag);
		farmIcon.SetActive(flag);
		unlockIcon.SetActive(!flag);
		plusButton.SetActive(!flag);
		infoButton.SetActive(!flag);
		FMODSoundManager.SetGameStateParam(flag ? 2f : 1f);
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
		Vector3 mousePosition = Input.mousePosition;
		Vector3 vector = container.parent.InverseTransformPoint(mousePosition);
		float num = Helper.ZoomWithScrollDelta(zoomSpeed, zoom);
		base.transform.localScale = Vector2.one * Mathf.Clamp(base.transform.localScale.x * num, minZoomScale, maxZoomScale);
		Vector3 vector2 = container.parent.InverseTransformPoint(mousePosition);
		container.anchoredPosition -= (Vector2)(vector - vector2);
	}
}
public class ScaledScrollRect : ScrollRect
{
	public Transform zoomContainer;

	private bool gridDrag;

	private Vector3 dragHitPos;

	private Vector2 lastLocalPointerPosition;

	private Canvas rootCanvas;

	protected override void Awake()
	{
		base.Awake();
		zoomContainer = base.content.parent;
		rootCanvas = GetComponentInParent<Canvas>();
	}

	public override void OnBeginDrag(PointerEventData eventData)
	{
		base.OnBeginDrag(eventData);
		Ray ray = MainSim.Inst.mainCamera.ScreenPointToRay(eventData.position);
		gridDrag = MainSim.Inst.Raycast(ray, out var _, out dragHitPos);
		RectTransformUtility.ScreenPointToLocalPointInRectangle(base.viewport, eventData.position, eventData.pressEventCamera, out lastLocalPointerPosition);
	}

	public override void OnDrag(PointerEventData eventData)
	{
		if (IsActive() && !(base.content == null))
		{
			Vector2 localPoint;
			if (gridDrag)
			{
				Camera mainCamera = MainSim.Inst.mainCamera;
				Ray ray = mainCamera.ScreenPointToRay(eventData.position);
				float num = (mainCamera.transform.position.z - dragHitPos.z) / (0f - ray.direction.z);
				Vector3 cameraPos = dragHitPos - ray.direction * num;
				Vector2 contentAnchoredPosition = CameraController.Inst.CameraToScrollPos(cameraPos);
				SetContentAnchoredPosition(contentAnchoredPosition);
			}
			else if (RectTransformUtility.ScreenPointToLocalPointInRectangle(base.viewport, eventData.position, eventData.pressEventCamera, out localPoint))
			{
				Vector2 vector = ((zoomContainer != null) ? ((Vector2)zoomContainer.lossyScale) : Vector2.one);
				vector /= rootCanvas.scaleFactor;
				Vector2 vector2 = localPoint - lastLocalPointerPosition;
				vector2 /= vector;
				Vector2 contentAnchoredPosition2 = base.content.anchoredPosition + vector2;
				SetContentAnchoredPosition(contentAnchoredPosition2);
				lastLocalPointerPosition = localPoint;
			}
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
			foreach (Window openWindow in MainSim.Inst.workspace.OpenWindows)
			{
				DocsWindow component2;
				if (openWindow.TryGetComponent<CodeWindow>(out var component))
				{
					component.UpdateSearch("");
				}
				else if (openWindow.TryGetComponent<DocsWindow>(out component2))
				{
					component2.OpenMarkdownText.UpdateSearch("", -1);
				}
			}
			currentSearchString = "";
			searchIndexText.text = "0 / 0";
			LeaveCurrentSearchResult();
			return;
		}
		foreach (Window openWindow2 in MainSim.Inst.workspace.OpenWindows)
		{
			DocsWindow component4;
			if (openWindow2.TryGetComponent<CodeWindow>(out var component3))
			{
				string text = component3.CodeInput.text;
				for (int num2 = text.IndexOf(searchString, 0, StringComparison.OrdinalIgnoreCase); num2 != -1; num2 = text.IndexOf(searchString, num2 + searchString.Length, StringComparison.OrdinalIgnoreCase))
				{
					searchResults.Add(new SearchResult(component3, num2));
				}
				component3.UpdateSearch(searchString);
			}
			else if (openWindow2.TryGetComponent<DocsWindow>(out component4))
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
public class TitleWindow : MonoBehaviour
{
	[SerializeField]
	private ScrollRect scrollView;

	[SerializeField]
	private RectTransform container;

	[SerializeField]
	private TMP_Text title;

	[SerializeField]
	private MarkdownText markdownPrefab;

	public string openPage;

	public string openLanguage;

	private TitleWorkspace titleWorkspace;

	public MarkdownText OpenMarkdownText { get; private set; }

	public Dictionary<string, string> Metadata { get; private set; }

	public void LoadPage(string doc)
	{
		if (container.childCount > 0)
		{
			Transform child = container.GetChild(0);
			container.DetachChildren();
			UnityEngine.Object.Destroy(child.gameObject);
		}
		container.anchoredPosition = new Vector2(0f, 0f);
		if (TryGetComponent<Window>(out var component) && component.workspace is TitleWorkspace titleWorkspace)
		{
			this.titleWorkspace = titleWorkspace;
			string path = Path.Combine(this.titleWorkspace.NewsPath, doc);
			string text = null;
			text = ((doc == "index") ? this.titleWorkspace.GetNewsIndexPage() : ((!PlatformManager.PlatformHandler.StreamingFileExists(path)) ? "" : PlatformManager.PlatformHandler.ReadStreamingFileText(path)));
			Metadata = new Dictionary<string, string>();
			MarkdownText markdownText = UnityEngine.Object.Instantiate(markdownPrefab, container);
			markdownText.BasePath = Path.GetDirectoryName(path);
			markdownText.Setup(text, LinkCalled, Metadata);
			if (title != null && Metadata.TryGetValue("titlebar", out var value) && !string.IsNullOrEmpty(value))
			{
				title.gameObject.SetActive(value: true);
				title.text = value;
			}
			else
			{
				title.gameObject.SetActive(value: false);
			}
			openPage = doc;
			openLanguage = this.titleWorkspace.NewsLanguage;
			OpenMarkdownText = markdownText;
		}
	}

	private void LinkCalled(string link)
	{
		if (link.StartsWith("persistent_data_path/"))
		{
			Process.Start(Path.Combine(Helper.persistentDataPath, link.Substring("persistent_data_path/".Length)));
			return;
		}
		if (link.StartsWith("https://store.steampowered.com/app/"))
		{
			OpenSteamUrl(link);
			return;
		}
		if (link.StartsWith("https"))
		{
			Process.Start(link);
			return;
		}
		string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(link);
		Window openWindow = titleWorkspace.GetOpenWindow(fileNameWithoutExtension);
		if (openWindow == null)
		{
			titleWorkspace.OpenWindow(fileNameWithoutExtension, link);
		}
		else
		{
			openWindow.MoveToFront();
		}
	}

	public void Scroll(float scroll)
	{
		container.anchoredPosition += new Vector2(0f, scroll * -500f);
	}

	private void Awake()
	{
		TitleWorkspace.OnNewsChanged += OnNewsChanged;
		ThemeManager.Inst.OnThemeChanged += OnThemeChanged;
	}

	private void OnEnable()
	{
		if (!string.IsNullOrEmpty(openPage) && openLanguage != titleWorkspace.NewsLanguage)
		{
			LoadPage(openPage);
		}
	}

	private void OnDestroy()
	{
		TitleWorkspace.OnNewsChanged -= OnNewsChanged;
		ThemeManager.Inst.OnThemeChanged -= OnThemeChanged;
	}

	private void OnNewsChanged()
	{
		if (!string.IsNullOrEmpty(openPage))
		{
			LoadPage(openPage);
		}
	}

	private void OnThemeChanged(ColorTheme theme)
	{
		theme.ui.text.ApplyTo(title);
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
		LoadPage(openPage);
	}

	public static void OpenSteamUrl(string link)
	{
		if (link.StartsWith("https://store.steampowered.com/app/"))
		{
			string text = link.Substring(35);
			int num = text.IndexOf('/');
			uint result;
			if (num < 0)
			{
				UnityEngine.Debug.LogError("Failed to parse Steam App ID from url: " + link);
			}
			else if (!uint.TryParse(text.Substring(0, num), out result))
			{
				UnityEngine.Debug.LogError("Failed to parse Steam App ID from url: " + link);
			}
			else if (!TryShowOverlay(result))
			{
				Application.OpenURL(link);
			}
		}
		else
		{
			Application.OpenURL(link);
		}
	}

	private static bool TryShowOverlay(uint appId)
	{
		if (!SteamManager.Initialized)
		{
			return false;
		}
		if (!SteamUtils.IsOverlayEnabled())
		{
			return false;
		}
		SteamFriends.ActivateGameOverlayToStore(new AppId_t(appId), EOverlayToStoreFlag.k_EOverlayToStoreFlag_None);
		return true;
	}
}
public class TitleWorkspace : WorkspaceBase
{
	public TitleWindow tilteWinPrefab;

	public GameObject openNewsButton;

	[NonSerialized]
	public HashSet<string> windowHistory = new HashSet<string>();

	public List<Dictionary<string, string>> allNews;

	public const string MetaFilePath = "filePath";

	public const string MetaFileName = "fileName";

	public const string MetaNewsType = "newsType";

	public const string NewsTypeDefault = "default";

	public const string NewsTypeUpdate = "update";

	public const string NewsTypePinned = "pinned";

	public const string MetaOpenOnClose = "openOnClose";

	public const string MetaWindowType = "windowType";

	public const string WindowTypeMaximized = "maximized";

	public const string WindowTypeCorner = "corner";

	public const string WindowTypeSide = "side";

	public const string MetaWindowWidth = "windowWidth";

	public const string MetaWindowHeight = "windowHeight";

	public const string MetaWindowPositionX = "windowX";

	public const string MetaWindowPositionY = "windowY";

	public const string MetaTitlebar = "titlebar";

	public const string MetaTitle = "title";

	private string currentLanguage;

	public string NewsLanguage => currentLanguage;

	public string NewsPath
	{
		get
		{
			if (currentLanguage == null)
			{
				UnityEngine.Debug.LogError("TitleWorkspace: NewsPath called before currentLanguage is initialized, using 'EN'");
				return Path.Combine(Application.streamingAssetsPath, "news", "EN");
			}
			return Path.Combine(Application.streamingAssetsPath, "news", currentLanguage);
		}
	}

	public static event Action OnNewsChanged;

	public TitleWindow OpenWindow(string windowName, string windowPage, Vector2 offset = default(Vector2), Vector2 size = default(Vector2))
	{
		if (IsWindowOpen(windowName))
		{
			windowName = GenerateFileName(windowName);
		}
		if (windowHistory == null)
		{
			windowHistory = new HashSet<string>();
		}
		windowHistory.Add(windowName);
		TitleWindow titleWindow = OpenWindow(tilteWinPrefab, windowName, offset, size);
		titleWindow.LoadPage(windowPage);
		if (titleWindow.Metadata.TryGetValue("newsType", out var value) && value == "pinned")
		{
			PositionPinnedWindow(titleWindow);
		}
		else if (offset == default(Vector2) && size == default(Vector2))
		{
			PositionNewWindow(titleWindow);
		}
		return titleWindow;
	}

	public void OpenNewsIndexWindow()
	{
		OpenWindow("news_index", "index");
	}

	public void Scroll(float scroll)
	{
		Window openWindow = GetOpenWindow(Input.mousePosition);
		if (openWindow != null && openWindow.TryGetComponent<TitleWindow>(out var component))
		{
			component.Scroll(scroll);
		}
	}

	public void FitWindowsIntoContainer()
	{
		foreach (Window openWindow in base.OpenWindows)
		{
			if (openWindow.movable)
			{
				Rect rect = container.rect;
				RectTransform component = openWindow.GetComponent<RectTransform>();
				Rect rect2 = component.rect;
				Matrix4x4 matrix4x = Matrix4x4.TRS(component.localPosition, component.localRotation, component.localScale);
				rect2.position = matrix4x.MultiplyPoint(rect2.position);
				rect2.size = matrix4x.MultiplyVector(rect2.size);
				if (rect2.yMax > rect.yMax)
				{
					Vector3 localPosition = component.localPosition;
					localPosition.y -= rect2.yMax - rect.yMax;
					component.localPosition = localPosition;
				}
				else if (rect2.yMax - 30f < rect.yMin)
				{
					Vector3 localPosition2 = component.localPosition;
					localPosition2.y += rect.yMin - (rect2.yMax - 30f);
					component.localPosition = localPosition2;
				}
				if (rect2.xMin + 30f > rect.xMax)
				{
					Vector3 localPosition3 = component.localPosition;
					localPosition3.x -= rect2.xMin + 30f - rect.xMax;
					component.localPosition = localPosition3;
				}
				else if (rect2.xMax - 30f < rect.xMin)
				{
					Vector3 localPosition4 = component.localPosition;
					localPosition4.x += rect.xMin - (rect2.xMax - 30f);
					component.localPosition = localPosition4;
				}
			}
		}
	}

	public void OpenLatestNews(bool firstTime)
	{
		if (allNews == null)
		{
			UnityEngine.Debug.LogError("TitleWorkspace: OpenLatestNews called before workspace was active and enabled");
			return;
		}
		string text = null;
		string text2 = null;
		foreach (Dictionary<string, string> item in allNews)
		{
			if (!item.TryGetValue("newsType", out var value))
			{
				value = "default";
			}
			if (!item.TryGetValue("filePath", out var value2) || !item.TryGetValue("fileName", out var value3))
			{
				continue;
			}
			if (firstTime && value == "update")
			{
				windowHistory.Add(value3);
			}
			else if (value == "pinned")
			{
				if (windowHistory.Add(value3))
				{
					OpenWindow(value3, value2);
				}
			}
			else if (text == null || string.CompareOrdinal(value3, text2) > 0)
			{
				text = value2;
				text2 = value3;
			}
		}
		if (!firstTime && text != null)
		{
			HashSet<string> hashSet = windowHistory;
			if (hashSet == null || !hashSet.Contains(text2))
			{
				OpenWindow(text2, text);
			}
		}
	}

	public string GetNewsIndexPage()
	{
		StringBuilder stringBuilder = new StringBuilder();
		stringBuilder.AppendLine("<meta windowType=side>");
		stringBuilder.Append("# ").AppendLine(Localizer.Localize("@latest_news"));
		if (allNews != null)
		{
			foreach (Dictionary<string, string> item in allNews.OrderByDescending((Dictionary<string, string> n) => n["fileName"], StringComparer.OrdinalIgnoreCase))
			{
				if (!item.TryGetValue("filePath", out var value))
				{
					continue;
				}
				if (!item.TryGetValue("title", out var value2))
				{
					string value4;
					if (item.TryGetValue("titlebar", out var value3))
					{
						value2 = value3;
					}
					else if (item.TryGetValue("fileName", out value4))
					{
						value2 = value4;
					}
				}
				if (!string.IsNullOrEmpty(value2))
				{
					stringBuilder.AppendLine("[" + value2 + "](" + value + ")");
				}
			}
		}
		return stringBuilder.ToString();
	}

	public override void RemoveWindow(Window window)
	{
		base.RemoveWindow(window);
		if (!window.TryGetComponent<TitleWindow>(out var component) || !component.Metadata.TryGetValue("openOnClose", out var value) || !(value != component.openPage))
		{
			return;
		}
		foreach (Dictionary<string, string> item in allNews)
		{
			if (item.TryGetValue("filePath", out var value2) && Path.GetFileName(value2) == value)
			{
				OpenWindow(item["fileName"], value2);
				break;
			}
		}
	}

	private void OnEnable()
	{
		OptionHolder.OnOptionChanged += OnOptionChanged;
		if (currentLanguage != Localizer.Lang)
		{
			FindAllNews();
		}
	}

	protected override void OnDisable()
	{
		base.OnDisable();
		OptionHolder.OnOptionChanged -= OnOptionChanged;
	}

	private void OnOptionChanged(string item)
	{
		if (item == "language")
		{
			FindAllNews();
		}
	}

	private void FindAllNews()
	{
		if (allNews == null)
		{
			allNews = new List<Dictionary<string, string>>();
		}
		allNews.Clear();
		currentLanguage = Localizer.Lang;
		string newsPath = NewsPath;
		if (!PlatformManager.PlatformHandler.StreamingDirectoryExists(newsPath))
		{
			currentLanguage = "EN";
			newsPath = NewsPath;
			if (!PlatformManager.PlatformHandler.StreamingDirectoryExists(newsPath))
			{
				return;
			}
		}
		foreach (string item in PlatformManager.PlatformHandler.GetFilesInStreamingDirectory(newsPath))
		{
			if (item.EndsWith(".md"))
			{
				string value = item.Substring(NewsPath.Length + 1);
				string fileNameWithoutExtension = Path.GetFileNameWithoutExtension(item);
				string text = PlatformManager.PlatformHandler.ReadStreamingFileText(item);
				Dictionary<string, string> dictionary = new Dictionary<string, string>();
				MarkdownText.ProcessMetadata(text, dictionary);
				dictionary["fileName"] = fileNameWithoutExtension;
				dictionary["filePath"] = value;
				allNews.Add(dictionary);
			}
		}
		if (openNewsButton != null)
		{
			openNewsButton.SetActive(allNews.Count > 0);
		}
		TitleWorkspace.OnNewsChanged?.Invoke();
	}

	private void PositionNewWindow(TitleWindow titleWin)
	{
		if (!titleWin.TryGetComponent<Window>(out var component))
		{
			return;
		}
		titleWin.Metadata.TryGetValue("windowType", out var value);
		Vector2 vector = default(Vector2);
		if (titleWin.Metadata.TryGetValue("windowWidth", out var value2))
		{
			float.TryParse(value2, out vector.x);
		}
		if (titleWin.Metadata.TryGetValue("windowHeight", out var value3))
		{
			float.TryParse(value3, out vector.y);
		}
		RectTransform component2 = component.GetComponent<RectTransform>();
		Rect rect = container.rect;
		if (string.Equals(value, "maximized", StringComparison.OrdinalIgnoreCase))
		{
			if (vector.x <= 0f)
			{
				vector.x = rect.size.x;
			}
			if (vector.y <= 0f)
			{
				vector.y = rect.size.y;
			}
			Window window = component;
			Vector2 playerSetSize = (component2.sizeDelta = (vector - 2f * new Vector2(50f, 50f)) / component2.localScale.x);
			window.playerSetSize = playerSetSize;
			component2.anchoredPosition = new Vector2(50f, component2.sizeDelta.y * component2.localScale.y / 2f);
		}
		else if (string.Equals(value, "corner", StringComparison.OrdinalIgnoreCase))
		{
			if (vector.x <= 0f)
			{
				vector.x = 250f;
			}
			if (vector.y <= 0f)
			{
				vector.y = 150f;
			}
			Window window2 = component;
			Vector2 playerSetSize = (component2.sizeDelta = vector / component2.localScale.x);
			window2.playerSetSize = playerSetSize;
			component2.localPosition = new Vector2(rect.xMax - 20f - vector.x, rect.yMin + 20f + vector.y) - rect.center;
		}
		else
		{
			if (vector.x <= 0f)
			{
				vector.x = rect.width - 375f - 75f;
			}
			if (vector.y <= 0f)
			{
				vector.y = rect.height - 150f;
			}
			Window window3 = component;
			Vector2 playerSetSize = (component2.sizeDelta = vector / component2.localScale.x);
			window3.playerSetSize = playerSetSize;
			component2.anchoredPosition = new Vector2(375f, component2.sizeDelta.y * component2.localScale.y / 2f);
		}
	}

	private void PositionPinnedWindow(TitleWindow titleWin)
	{
		Window component = titleWin.GetComponent<Window>();
		component.movable = (component.resizable = (component.minimizable = (component.dockable = false)));
		titleWin.Metadata.TryGetValue("windowType", out var _);
		Vector2 vector = default(Vector2);
		if (titleWin.Metadata.TryGetValue("windowWidth", out var value2))
		{
			float.TryParse(value2, out vector.x);
		}
		if (titleWin.Metadata.TryGetValue("windowHeight", out var value3))
		{
			float.TryParse(value3, out vector.y);
		}
		Vector2 anchoredPosition = default(Vector2);
		if (titleWin.Metadata.TryGetValue("windowX", out var value4))
		{
			float.TryParse(value4, out anchoredPosition.x);
		}
		if (titleWin.Metadata.TryGetValue("windowY", out var value5))
		{
			float.TryParse(value5, out anchoredPosition.y);
		}
		RectTransform component2 = component.GetComponent<RectTransform>();
		Vector2 anchorMin = (component2.anchorMax = new Vector2(1f, 0f));
		component2.anchorMin = anchorMin;
		component2.pivot = new Vector2(1f, 0f);
		anchorMin = (component2.sizeDelta = vector / component2.localScale.x);
		component.playerSetSize = anchorMin;
		component2.anchoredPosition = anchoredPosition;
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

	private RectTransform rt;

	public GameObject Container => container;

	public TooltipInfo Info => info;

	private bool IsImmediateTooltip => tooltipGameObject == MainSim.Inst.workspace.workspaceContainer.gameObject;

	private void Update()
	{
		Vector3 mousePosition = Input.mousePosition;
		GameObject gameObject = ((!Application.isFocused || !(mousePosition.x >= 0f) || !(mousePosition.y >= 0f) || !(mousePosition.x < (float)Screen.width) || !(mousePosition.y < (float)Screen.height)) ? null : inputModule.GetPointerData()?.pointerCurrentRaycast.gameObject);
		if ((!IsImmediateTooltip || !(gameObject == null)) && gameObject != tooltipGameObject)
		{
			if (tooltipGameObject != null)
			{
				tooltipGameObject.GetComponent<TooltipAccessor>()?.TooltipGone();
			}
			tooltipGameObject = gameObject;
			UpdateTooltip();
		}
		else if ((object)tooltipGameObject != null && tooltipGameObject == null)
		{
			tooltipGameObject = null;
			UpdateTooltip();
		}
		if (info != null)
		{
			UpdatePosition();
			if (container.transform.localScale != Vector3.zero && !string.IsNullOrEmpty(info.docs) && Input.GetKeyDown(KeyCode.Mouse1))
			{
				MainSim.Inst.workspace.OpenAndGoTo(info.docs);
			}
		}
	}

	private void Awake()
	{
		rt = (RectTransform)base.transform;
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
		ClearTooltip();
		if (tooltipGameObject != null && tooltipGameObject.TryGetComponent<TooltipAccessor>(out var component))
		{
			info = component.GetTooltipInfo(UpdateTooltip);
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

	private bool SetTooltip(GameObject tooltipObject)
	{
		if (tooltipObject != tooltipGameObject || info == null)
		{
			return false;
		}
		if ((object)rt == null)
		{
			rt = (RectTransform)base.transform;
		}
		bool flag = container.transform.localScale != Vector3.zero;
		if (string.IsNullOrEmpty(info.text))
		{
			container.transform.localScale = Vector3.zero;
			return false;
		}
		text.UpdateText(info.text);
		container.transform.localScale = Vector3.one;
		UpdatePosition();
		docsNotice.gameObject.SetActive(!string.IsNullOrEmpty(info.docs));
		return !flag;
	}

	public bool CanShowTooltipImmediate()
	{
		if (!base.isActiveAndEnabled)
		{
			return false;
		}
		if (!(tooltipGameObject == null))
		{
			return tooltipGameObject == MainSim.Inst.workspace.workspaceContainer.gameObject;
		}
		return true;
	}

	public bool SetTooltipImmediate(TooltipInfo info)
	{
		if (info == null)
		{
			if (!IsImmediateTooltip)
			{
				return false;
			}
			this.info = null;
			tooltipGameObject = null;
			ClearTooltip();
			return false;
		}
		if (!CanShowTooltipImmediate())
		{
			return false;
		}
		if (this.info == info)
		{
			return false;
		}
		if (this.info != null && info != null && this.info.text == info.text)
		{
			this.info = info;
			return false;
		}
		this.info = info;
		tooltipGameObject = MainSim.Inst.workspace.workspaceContainer.gameObject;
		return SetTooltip(tooltipGameObject);
	}

	private void ClearTooltip()
	{
		container.transform.localScale = Vector3.zero;
		text.ClearText();
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
		Vector2 vector = offset;
		TooltipInfo.Anchor anchor = info?.anchor ?? TooltipInfo.Anchor.Auto;
		Vector2 pivot = default(Vector2);
		if ((Input.mousePosition.x * 2f > (float)Screen.width && anchor != TooltipInfo.Anchor.BottomRight && anchor != TooltipInfo.Anchor.TopRight) || anchor == TooltipInfo.Anchor.BottomLeft || anchor == TooltipInfo.Anchor.TopLeft)
		{
			pivot.x = 1f;
		}
		else
		{
			pivot.x = 0f;
			vector *= new Vector2(-1f, 1f);
		}
		if ((Input.mousePosition.y * 2f > (float)Screen.height && anchor != TooltipInfo.Anchor.TopLeft && anchor != TooltipInfo.Anchor.TopRight) || anchor == TooltipInfo.Anchor.BottomLeft || anchor == TooltipInfo.Anchor.BottomRight)
		{
			pivot.y = 1f;
		}
		else
		{
			pivot.y = 0f;
			vector *= new Vector2(1f, -1f);
		}
		rt.pivot = pivot;
		rt.anchoredPosition = ((Vector2)Input.mousePosition + vector) / canvas.scaleFactor;
		if (info != null && info.fixedPosition != Vector3.zero)
		{
			rt.position = info.fixedPosition;
		}
		PreventOffscreen();
	}

	private void PreventOffscreen()
	{
		Rect rect = (base.transform.parent as RectTransform).rect;
		Rect rectInParentSpace = GetRectInParentSpace();
		if (rectInParentSpace.x < 0f)
		{
			rt.anchoredPosition = new Vector2(rt.anchoredPosition.x - rectInParentSpace.x, rt.anchoredPosition.y);
		}
		else if (rectInParentSpace.xMax > rect.width)
		{
			rt.anchoredPosition = new Vector2(rt.anchoredPosition.x + (rect.width - rectInParentSpace.xMax), rt.anchoredPosition.y);
		}
		if (rectInParentSpace.y < 0f)
		{
			rt.anchoredPosition = new Vector2(rt.anchoredPosition.x, rt.anchoredPosition.y - rectInParentSpace.y);
		}
		else if (rectInParentSpace.yMax > rect.height)
		{
			rt.anchoredPosition = new Vector2(rt.anchoredPosition.x, rt.anchoredPosition.y + (rect.height - rectInParentSpace.yMax));
		}
	}

	private Rect GetRectInParentSpace()
	{
		Rect rect = rt.rect;
		Vector2 vector = rt.offsetMin + Vector2.Scale(rt.pivot, rect.size);
		if (rt.parent is RectTransform rectTransform)
		{
			vector += Vector2.Scale(rt.anchorMin, rectTransform.rect.size);
		}
		rect.x += vector.x;
		rect.y += vector.y;
		return rect;
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
		EntitySO entity = ResourceManager.GetEntity(objectName);
		if (entity == null || !MainSim.Inst.IsUnlocked(objectName))
		{
			return null;
		}
		string text = ((entity.cost == null || entity.cost.IsEmpty()) ? "" : ("\n\n" + string.Format(Localizer.Localize("object_tooltip_template_cost"), entity.objectName)));
		string text2 = "";
		return new TooltipInfo($"## {CodeUtilities.ToUpperSnake(entity.objectName)}\n{Localizer.Localize(entity.GetDescription())}{text2}{text}", 0f, default(Vector3), TooltipInfo.Anchor.Auto, entity.docs);
	}

	public static TooltipInfo GroundTooltip(string objectName)
	{
		GroundSO ground = ResourceManager.GetGround(objectName);
		if (ground == null || !MainSim.Inst.IsUnlocked(objectName))
		{
			return null;
		}
		return new TooltipInfo($"## {CodeUtilities.ToUpperSnake(ground.objectName)}\n{Localizer.Localize(ground.GetDescription())}", 0f, default(Vector3), TooltipInfo.Anchor.Auto, ground.docs);
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
				string format2 = (flag ? "{0}\n{1}x{2}" : "{0}\n{1}x{2} => {3}x{3}");
				Vector2Int worldSize = MainSim.Inst.GetWorldSize();
				int num4 = Helper.WorldSizeScale(num2 + 1);
				text = string.Format(format2, text, worldSize.x, worldSize.y, num4);
				break;
			}
			case MultiUnlockDescrMode.Per10Seconds:
			{
				string format = (flag ? "{0}\n{1}/s" : "{0}\n{1}/s => {2}/s");
				float num3 = (float)(1 << Mathf.Max(0, num2 - 1)) * 0.1f;
				text = string.Format(format, text, num3, num3 * 2f);
				break;
			}
			case MultiUnlockDescrMode.Megafarm:
				text = string.Format(flag ? "{0}\n{1}" : "{0}\n{1} => {2}", text, Helper.NumDrones(num2), Helper.NumDrones(num2 + 1));
				break;
			case MultiUnlockDescrMode.Additive:
				text = string.Format(flag ? "{0}\n{1}" : "{0}\n{1} => {2}", text, unlock.additivePercentFactor * (float)(num2 - 1) + unlock.additivePercentStart, unlock.additivePercentFactor * (float)num2 + unlock.additivePercentStart);
				break;
			}
		}
		else
		{
			text = Localizer.Localize(unlock.description);
		}
		string arg = "";
		if (unlock.additionalUnlockRequirement != null && !string.IsNullOrEmpty(unlock.additionalUnlockRequirement.unlockName) && MainSim.Inst.NumUnlocked(unlock.additionalUnlockRequirement.unlockName) < unlock.additionalUnlockRequirement.level)
		{
			arg = "\n\n" + string.Format(Localizer.Localize("unlock_tooltip_template_additional_requirement"), Localizer.Localize(unlock.additionalUnlockRequirement.unlockName), unlock.additionalUnlockRequirement.level);
		}
		else
		{
			ItemBlock unlockCost = MainSim.Inst.GetUnlockCost(unlock);
			if (unlockCost != null && !unlockCost.IsEmpty())
			{
				arg = "\n\n" + string.Format(Localizer.Localize("unlock_tooltip_template_cost"), unlock.unlockName);
			}
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
		UnlockSO unlockOf = ResourceManager.GetUnlockOf(keyword);
		if (unlockOf == null)
		{
			return "";
		}
		string text = "docs/scripting/" + keyword;
		if (Localizer.LoadDoc(text) != "")
		{
			return text;
		}
		return unlockOf.docs;
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
				return GroundTooltip(word);
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
	private Image gainImage;

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
			if (!string.IsNullOrEmpty(unlockSO.gainResource))
			{
				gainImage.gameObject.SetActive(value: true);
				gainImage.sprite = Resources.Load<Sprite>("ItemTextures/" + unlockSO.gainResource);
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
public class VideoUI : MonoBehaviour
{
	public VideoPlayer player;

	public RawImage image;

	public AspectRatioFitter fitter;

	private RenderTexture rt;

	private string fallbackTexture;

	public void Play(string video, string fallbackTexture = null, string basePath = null)
	{
		if (player == null || image == null)
		{
			return;
		}
		if (fallbackTexture == null)
		{
			int num = video.LastIndexOf('|');
			if (num >= 0)
			{
				fallbackTexture = video.Substring(num + 1);
				video = video.Substring(0, num);
			}
		}
		if (Path.GetExtension(video) == "")
		{
			VideoClip videoClip = Resources.Load<VideoClip>(video);
			if (videoClip == null)
			{
				UnityEngine.Debug.LogError("VideoUI: Couldn't load video resource '" + video + "'");
				return;
			}
			player.clip = videoClip;
		}
		else if (video.StartsWith("http") || video.StartsWith("file:"))
		{
			player.url = video;
		}
		else
		{
			string text = video;
			if (basePath != null && !Path.IsPathFullyQualified(text))
			{
				text = Path.Combine(basePath, text);
			}
			player.url = text;
		}
		this.fallbackTexture = fallbackTexture;
		if (player.enabled)
		{
			player.Prepare();
		}
	}

	public async void ShowFallback(string fallback)
	{
		if (string.IsNullOrEmpty(fallback))
		{
			return;
		}
		Texture2D texture2D = await ImageLoader.ResolveTexture(fallback);
		if (!(texture2D == null))
		{
			image.enabled = true;
			image.texture = texture2D;
			if (fitter != null)
			{
				fitter.aspectRatio = (float)texture2D.width / (float)texture2D.height;
			}
			LayoutRebuilder.MarkLayoutForRebuild(base.transform as RectTransform);
		}
	}

	private void OnEnable()
	{
		if (player == null || image == null)
		{
			base.enabled = false;
			return;
		}
		image.enabled = false;
		player.errorReceived += OnErrorReceived;
		player.prepareCompleted += OnVideoPrepared;
		if (player.isPrepared)
		{
			OnVideoPrepared(player);
		}
		else if ((player.clip != null || !string.IsNullOrEmpty(player.url)) && !player.isPrepared)
		{
			player.Prepare();
		}
	}

	private void OnDisable()
	{
		player.errorReceived -= OnErrorReceived;
		player.prepareCompleted -= OnVideoPrepared;
	}

	private void OnDestroy()
	{
		if (rt != null)
		{
			UnityEngine.Object.Destroy(rt);
			rt = null;
		}
	}

	private void OnErrorReceived(VideoPlayer player, string message)
	{
		UnityEngine.Debug.LogError("VideoUI: Failed to play video: " + message);
		ShowFallback(fallbackTexture);
	}

	private void OnVideoPrepared(VideoPlayer source)
	{
		uint width = source.width;
		uint height = source.height;
		if (width == 0 || height == 0)
		{
			return;
		}
		if (rt == null || rt.width != width || rt.height != height)
		{
			if (rt != null)
			{
				UnityEngine.Object.Destroy(rt);
			}
			rt = new RenderTexture((int)width, (int)height, 0, RenderTextureFormat.Default, 0)
			{
				antiAliasing = 1,
				wrapMode = TextureWrapMode.Clamp,
				filterMode = FilterMode.Point,
				anisoLevel = 0
			};
		}
		image.enabled = true;
		if (fitter != null)
		{
			fitter.aspectRatio = (float)width / (float)height;
		}
		player.renderMode = VideoRenderMode.RenderTexture;
		player.targetTexture = rt;
		image.texture = rt;
		player.Play();
		LayoutRebuilder.MarkLayoutForRebuild(base.transform as RectTransform);
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
	public bool movable;

	public bool resizable;

	public bool minimizable;

	public bool dockable;

	public RectTransform dockPosition;

	public WorkspaceBase workspace;

	public string windowName;

	public GameObject minimizeButton;

	public bool isMinimized;

	public Vector2 minimizedSize;

	public Vector2 playerSetSize;

	public Vector2 automaticSize;

	public Vector2 minSize;

	public float resizeMargin = 10f;

	public List<GameObject> disableOnMinimize;

	public UnityEvent<bool> OnMinimizeChanged;

	public UnityEvent OnFocused;

	private bool horitontalResize;

	private bool verticalResize;

	private Vector2 beginDragSize;

	private RectTransform windowRect;

	public Window dockedParent { get; private set; }

	public RectTransform WindowRect => windowRect;

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
				num += windowRect.rect.height;
				window = window.DockedChild;
			}
			return num;
		}
	}

	public void SetMinmized(bool minimized)
	{
		if (!minimizable)
		{
			return;
		}
		isMinimized = minimized;
		workspace.OnWindowRectChanged(this);
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
		workspace.RemoveWindow(this);
		UnityEngine.Object.Destroy(base.gameObject);
	}

	public void UpdateSize()
	{
		TryGetComponent<RectTransform>(out windowRect);
		if (isMinimized)
		{
			windowRect.sizeDelta = minimizedSize;
			return;
		}
		Vector2 sizeDelta = Vector2.Max(playerSetSize, minSize);
		if (playerSetSize.y < minSize.y)
		{
			sizeDelta.y = MathF.Max(automaticSize.y, minSize.y);
		}
		windowRect.sizeDelta = sizeDelta;
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
		if (eventData.button != PointerEventData.InputButton.Left)
		{
			return;
		}
		if (resizable && (horitontalResize || verticalResize))
		{
			Vector2 vector = eventData.position - eventData.pressPosition;
			Vector2 vector2 = windowRect.InverseTransformVector(vector);
			if (horitontalResize)
			{
				playerSetSize.x = beginDragSize.x + vector2.x;
				playerSetSize.x = MathF.Max(playerSetSize.x, minSize.x);
			}
			if (verticalResize)
			{
				playerSetSize.y = beginDragSize.y - vector2.y;
				playerSetSize.y = MathF.Max(playerSetSize.y, minSize.y);
			}
			if (horitontalResize || verticalResize)
			{
				UpdateSize();
			}
		}
		else if (movable)
		{
			Vector2 vector3 = windowRect.parent.InverseTransformVector(eventData.delta);
			windowRect.anchoredPosition += vector3;
		}
	}

	public void OnBeginDrag(PointerEventData eventData)
	{
		if (eventData.button == PointerEventData.InputButton.Left)
		{
			if (resizable && IsPointerOnResizeArea(eventData.pressPosition, out horitontalResize, out verticalResize))
			{
				workspace.ResizingWindow = this;
				beginDragSize = (playerSetSize = windowRect.sizeDelta);
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
		workspace.OnWindowRectChanged(this);
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
		if (horitontalResize || verticalResize)
		{
			horitontalResize = false;
			verticalResize = false;
			if (workspace.ResizingWindow == this)
			{
				workspace.ResizingWindow = null;
			}
		}
	}

	public void OnPointerDown(PointerEventData eventData)
	{
		if (eventData.button == PointerEventData.InputButton.Left)
		{
			MoveToFront();
			OnFocused?.Invoke();
		}
	}

	public bool IsPointerOnResizeArea(Vector2 screenPoint, out bool horizontal, out bool vertical)
	{
		horizontal = (vertical = false);
		if (!resizable)
		{
			return false;
		}
		if (horitontalResize || verticalResize)
		{
			horizontal = horitontalResize;
			vertical = verticalResize;
			return true;
		}
		if (isMinimized)
		{
			return false;
		}
		RectTransformUtility.ScreenPointToLocalPointInRectangle(windowRect, screenPoint, null, out var localPoint);
		localPoint.y = 0f - localPoint.y;
		Rect rect = windowRect.rect;
		horizontal = rect.width - localPoint.x < resizeMargin;
		vertical = rect.height - localPoint.y < resizeMargin;
		return horizontal | vertical;
	}

	public void MoveToFront()
	{
		HighestDockedParent.transform.SetAsLastSibling();
	}

	public void DockOnto(Window other)
	{
		if (OptionHolder.GetString("window docking", "enabled") != "enabled" || other == null || !other.dockable || !dockable)
		{
			return;
		}
		Window window = other;
		do
		{
			if (window == this)
			{
				UnityEngine.Debug.LogError("Docking window '" + windowName + "' onto '" + other.windowName + "' would create a docking loop, prevented docking.");
				return;
			}
			window = window.dockedParent;
		}
		while (window != null);
		other.DockedChild?.DockOnto(LeastDockedChild);
		base.transform.SetParent(other.dockPosition, worldPositionStays: false);
		windowRect.anchoredPosition = Vector2.zero;
		dockedParent = other;
	}

	public void Undock()
	{
		if (dockedParent != null)
		{
			base.transform.SetParent(workspace.container);
			dockedParent = null;
		}
	}

	private void Awake()
	{
		TryGetComponent<RectTransform>(out windowRect);
	}

	private void Start()
	{
		if (minimizeButton != null)
		{
			minimizeButton.SetActive(minimizable);
		}
	}
}
public class Workspace : WorkspaceBase
{
	public RectTransform workspaceContainer;

	public RectTransform zoomContainer;

	public RectTransform farmPosition;

	public Canvas editorCanvas;

	public CodeCompleter codeCompleter;

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

	public Window activeWindow;

	public UndoHistory undoHistory = new UndoHistory();

	public volatile ConcurrentDictionary<string, CodeWindow> codeWindows = new ConcurrentDictionary<string, CodeWindow>();

	private CanvasGroup containerGroup;

	private bool containerDirty;

	private Window transitionTarget;

	private int transitionTargetCharIndex;

	private CodeInputField transitionTargetInputField;

	private float transitionStartTime;

	private float transitionEndTime;

	private Vector2 transitionStartPosition;

	public static bool InputIgnoreWindows
	{
		get
		{
			if (!Input.GetKey(KeyCode.LeftAlt))
			{
				return Input.GetKey(KeyCode.RightAlt);
			}
			return true;
		}
	}

	public void Scroll(float scroll)
	{
		if (!InputIgnoreWindows)
		{
			Window openWindow = GetOpenWindow(Input.mousePosition);
			if (openWindow != null && openWindow.TryGetComponent<DocsWindow>(out var component))
			{
				component.Scroll(scroll);
				return;
			}
			if (openWindow != null && openWindow.TryGetComponent<CodeWindow>(out var component2))
			{
				component2.Scroll(scroll);
				return;
			}
		}
		Zoom(scroll);
	}

	public void Zoom(float zoom)
	{
		Vector3 mousePosition = Input.mousePosition;
		Vector3 vector = workspaceContainer.parent.InverseTransformPoint(mousePosition);
		float num = Helper.ZoomWithScrollDelta(zoomSpeed, zoom);
		cameraController.zoom = Mathf.Clamp(cameraController.zoom * num, minCanvasScaleFactor, maxCanvasScaleFactor);
		zoomContainer.localScale = Vector3.one * cameraController.zoom;
		workspaceContainer.GetComponent<ContainerScaler>().UpdateMarginSize();
		Vector3 vector2 = workspaceContainer.parent.InverseTransformPoint(mousePosition);
		workspaceContainer.anchoredPosition -= (Vector2)(vector - vector2);
	}

	protected override void Update()
	{
		base.Update();
		if (containerDirty)
		{
			UpdateContainerSizeInternal();
		}
		LerpCameraToTarget();
		if (containerGroup != null)
		{
			containerGroup.blocksRaycasts = !InputIgnoreWindows;
		}
	}

	protected override void Start()
	{
		base.Start();
		SetViewportOptions("viewport sliding");
		OptionHolder.OnOptionChanged += SetViewportOptions;
		container.TryGetComponent<CanvasGroup>(out containerGroup);
	}

	protected override Texture2D GetCursorForHoveredWindow(Window window)
	{
		if (InputIgnoreWindows)
		{
			return null;
		}
		Texture2D cursorForHoveredWindow = base.GetCursorForHoveredWindow(window);
		if (cursorForHoveredWindow != null)
		{
			return cursorForHoveredWindow;
		}
		if (window.TryGetComponent<CodeWindow>(out var component) && component.IsPointerOverCodeInput())
		{
			return textCursor;
		}
		return null;
	}

	private void SetViewportOptions(string option)
	{
		if (option == "viewport sliding")
		{
			scrollRect.inertia = OptionHolder.GetString("viewport sliding") == "enabled";
		}
	}

	public override void OnWindowRectChanged(Window window)
	{
		base.OnWindowRectChanged(window);
		containerDirty = true;
	}

	private void UpdateContainerSizeInternal()
	{
		workspaceContainer.GetComponent<ContainerScaler>().UpdateSize();
		containerDirty = false;
	}

	public void OpenCodeWindow(string fileName, string code, Vector2 offset, Vector2 size = default(Vector2))
	{
		if (!IsWindowOpen(fileName, ignoreCase: true))
		{
			CodeWindow codeWindow = OpenWindow(codeWinPrefab, fileName, offset, size);
			codeWindow.workspace = this;
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
		OpenWindow(docWinPrefab, windowName, offset, size).LoadDoc(docsPage);
	}

	public void OpenAndGoTo(string doc)
	{
		AddNewDocsWindow(doc);
		if (MainSim.Inst.researchMenu.IsOpen)
		{
			MainSim.Inst.researchMenu.OpenCloseMenu();
		}
	}

	public override void RemoveWindow(Window window)
	{
		base.RemoveWindow(window);
		codeWindows.Remove(window.windowName, out var _);
	}

	public override void RenameWindow(Window window, string newWindowName)
	{
		if (window.TryGetComponent<CodeWindow>(out var component))
		{
			codeWindows.Remove(window.windowName, out var _);
			codeWindows[newWindowName] = component;
		}
		base.RenameWindow(window, newWindowName);
	}

	protected override void RegisterWindow(Window win, string name, Vector2 offset, Vector2 size = default(Vector2))
	{
		base.RegisterWindow(win, name, offset, size);
		if (win.TryGetComponent<CodeWindow>(out var component))
		{
			component.fileName = name;
			codeWindows[name] = component;
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
				if (inputField.textComponent.textInfo.characterCount == 0)
				{
					return;
				}
				Vector3 bottomRight = inputField.GetCharacterAtSourceIndex(charIndex).bottomRight;
				Vector3 vector = inputField.textComponent.rectTransform.TransformPoint(bottomRight);
				if (vector.x >= 0f && vector.x < (float)Screen.width && vector.y >= 0f && vector.y < (float)Screen.height)
				{
					return;
				}
			}
			else
			{
				Rect rect = new Rect(0f, 0f, Screen.width, Screen.height);
				Rect rect2 = component.rect;
				rect2.position = component.TransformPoint(rect2.position);
				rect2.size = component.TransformVector(rect2.size);
				if (rect2.Intersection(rect).Area() > rect2.Area() * 0.5f)
				{
					return;
				}
			}
		}
		float num = 0.2f;
		transitionStartPosition = workspaceContainer.anchoredPosition;
		transitionStartTime = Time.time;
		transitionEndTime = transitionStartTime + num;
		transitionTarget = target;
		transitionTargetCharIndex = charIndex;
		transitionTargetInputField = inputField;
	}

	private void LerpCameraToTarget()
	{
		if (transitionTarget == null)
		{
			return;
		}
		RectTransform windowRect = transitionTarget.WindowRect;
		Vector3 position;
		if (transitionTargetInputField != null)
		{
			if (transitionTargetInputField.textComponent.textInfo.characterCount == 0)
			{
				return;
			}
			Vector3 bottomRight = transitionTargetInputField.GetCharacterAtSourceIndex(transitionTargetCharIndex).bottomRight;
			position = transitionTargetInputField.textComponent.rectTransform.TransformPoint(bottomRight);
		}
		else
		{
			Vector2 center = windowRect.rect.center;
			position = windowRect.TransformPoint(center);
		}
		Vector3 vector = workspaceContainer.parent.InverseTransformPoint(position);
		Vector2 b = workspaceContainer.anchoredPosition - (Vector2)vector;
		float t = (Time.time - transitionStartTime) / (transitionEndTime - transitionStartTime);
		workspaceContainer.anchoredPosition = Vector2.Lerp(transitionStartPosition, b, t);
		if (Time.time > transitionEndTime)
		{
			transitionTarget = null;
		}
	}

	public override bool IsValidFileName(string fileName)
	{
		if (!Saver.IsValidCodeFileName(fileName))
		{
			return false;
		}
		return base.IsValidFileName(fileName);
	}

	public void AddNewWindow()
	{
		OpenCodeWindow(GenerateFileName("f"), "", -workspaceContainer.anchoredPosition + spawnWindowOffset);
		if (codeWindows.Count >= 20)
		{
			Achievements.UnlockAchievement("CHAOS");
		}
	}

	public void AddNewDocsWindow(string doc = "docs/home.md", Vector2 offset = default(Vector2))
	{
		OpenDocsWindow(GenerateFileName("docs"), doc, -workspaceContainer.anchoredPosition + spawnDocsWindowOffset + offset);
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
public class WorkspaceBase : MonoBehaviour
{
	public RectTransform container;

	public Camera uiCam;

	[SerializeField]
	private Texture2D horizontalResizeCursor;

	[SerializeField]
	private Texture2D verticalResizeCursor;

	[SerializeField]
	private Texture2D bidirectionalResizeCursor;

	protected Dictionary<string, Window> openWindows = new Dictionary<string, Window>();

	public IEnumerable<Window> OpenWindows => openWindows.Values;

	public Window ResizingWindow { get; set; }

	public TWindow OpenWindow<TWindow>(TWindow prefab, string windowName, Vector2 offset, Vector2 size = default(Vector2)) where TWindow : UnityEngine.Component
	{
		TWindow val = UnityEngine.Object.Instantiate(prefab, container);
		if (!val.TryGetComponent<Window>(out var component))
		{
			UnityEngine.Debug.LogError("Invalid window prefab '" + prefab.name + "': No Window component found", prefab);
			return null;
		}
		RegisterWindow(component, windowName, offset, size);
		return val;
	}

	public virtual void OnWindowRectChanged(Window window)
	{
	}

	public bool IsWindowOpen(string windowName)
	{
		return openWindows.ContainsKey(windowName);
	}

	public bool IsWindowOpen(string windowName, bool ignoreCase = false)
	{
		if (!ignoreCase)
		{
			return openWindows.ContainsKey(windowName);
		}
		foreach (string key in openWindows.Keys)
		{
			if (StringComparer.OrdinalIgnoreCase.Equals(key, windowName))
			{
				return true;
			}
		}
		return false;
	}

	public Window GetOpenWindow(string windowName)
	{
		return openWindows.GetValueOrDefault(windowName);
	}

	public bool TryGetOpenWindow(string windowName, out Window window)
	{
		return openWindows.TryGetValue(windowName, out window);
	}

	public Window GetOpenWindow(Vector2 screenPos)
	{
		Window result = null;
		int num = -1;
		foreach (Window value in openWindows.Values)
		{
			int siblingIndex = value.HighestDockedParent.transform.GetSiblingIndex();
			if (siblingIndex >= num && RectTransformUtility.RectangleContainsScreenPoint(value.WindowRect, screenPos, uiCam))
			{
				result = value;
				num = siblingIndex;
			}
		}
		return result;
	}

	public bool TryGetOpenWindow(Vector2 screenPos, out Window window)
	{
		window = GetOpenWindow(screenPos);
		return window != null;
	}

	public virtual void RenameWindow(Window window, string newWindowName)
	{
		openWindows.Remove(window.windowName);
		openWindows[newWindowName] = window;
		window.windowName = newWindowName;
	}

	public virtual void RemoveWindow(Window window)
	{
		openWindows.Remove(window.windowName);
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

	public virtual bool IsValidFileName(string fileName)
	{
		if (!Saver.IsValidPortableFileName(fileName) || IsWindowOpen(fileName, ignoreCase: true))
		{
			return false;
		}
		return true;
	}

	protected virtual void Start()
	{
	}

	protected virtual void OnDisable()
	{
		Cursor.SetCursor(null, Vector2.zero, CursorMode.Auto);
	}

	protected virtual void Update()
	{
		Texture2D texture2D = null;
		Window window;
		if (ResizingWindow != null)
		{
			texture2D = GetCursorForHoveredWindow(ResizingWindow);
		}
		else if (TryGetOpenWindow(Input.mousePosition, out window))
		{
			texture2D = GetCursorForHoveredWindow(window);
		}
		if (texture2D != null)
		{
			Cursor.SetCursor(texture2D, new Vector2((float)texture2D.width / 2f, (float)texture2D.height / 2f), CursorMode.Auto);
		}
		else
		{
			Cursor.SetCursor(null, Vector2.zero, CursorMode.Auto);
		}
	}

	protected virtual void RegisterWindow(Window window, string windowName, Vector2 offset, Vector2 size = default(Vector2))
	{
		window.workspace = this;
		openWindows[windowName] = window;
		window.windowName = windowName;
		window.GetComponent<RectTransform>().anchoredPosition = offset;
		if (size != default(Vector2))
		{
			window.playerSetSize = size;
			window.UpdateSize();
		}
	}

	protected virtual Texture2D GetCursorForHoveredWindow(Window window)
	{
		if (window.IsPointerOnResizeArea(Input.mousePosition, out var horizontal, out var vertical))
		{
			if (horizontal && vertical)
			{
				return bidirectionalResizeCursor;
			}
			if (horizontal)
			{
				return horizontalResizeCursor;
			}
			return verticalResizeCursor;
		}
		return null;
	}
}
public sealed class WrappingLayoutGroup : LayoutGroup
{
	private const float MinColumnWidth = 240f;

	private const float ColumnSpacing = 24f;

	private const int MinLinesPerColumn = 3;

	private string[] lines;

	private CodeInputField[] textColumns;

	private Action<CodeInputField, string> setText;

	private int gridColumnCount = 1;

	private int populatedColumnCount;

	private float columnWidth;

	public void Initialize(string[] lines, CodeInputField[] textColumns, Action<CodeInputField, string> setText)
	{
		this.lines = lines;
		this.textColumns = textColumns;
		this.setText = setText;
		populatedColumnCount = -1;
		RebuildColumnsIfNeeded();
		SetDirty();
	}

	private void Update()
	{
		if (RebuildColumnsIfNeeded())
		{
			SetDirty();
		}
	}

	public override void CalculateLayoutInputHorizontal()
	{
		UpdateColumnMetrics();
		base.CalculateLayoutInputHorizontal();
		SetLayoutInputForAxis((float)base.padding.horizontal + 240f, (float)base.padding.horizontal + 240f, 1f, 0);
	}

	public override void CalculateLayoutInputVertical()
	{
		float num = 0f;
		int num2 = Mathf.Min(populatedColumnCount, base.rectChildren.Count);
		for (int i = 0; i < num2; i++)
		{
			num = Mathf.Max(num, LayoutUtility.GetPreferredHeight(base.rectChildren[i]));
		}
		num += (float)base.padding.vertical;
		SetLayoutInputForAxis(num, num, -1f, 1);
	}

	public override void SetLayoutHorizontal()
	{
		UpdateColumnMetrics();
		for (int i = 0; i < base.rectChildren.Count; i++)
		{
			bool flag = i < populatedColumnCount;
			float pos = (flag ? ((float)base.padding.left + (float)i * (columnWidth + 24f)) : ((float)base.padding.left));
			SetChildAlongAxis(base.rectChildren[i], 0, pos, flag ? columnWidth : 0f);
		}
	}

	public override void SetLayoutVertical()
	{
		float num = Mathf.Max(0f, base.rectTransform.rect.height - (float)base.padding.vertical);
		for (int i = 0; i < base.rectChildren.Count; i++)
		{
			SetChildAlongAxis(base.rectChildren[i], 1, base.padding.top, (i < populatedColumnCount) ? num : 0f);
		}
	}

	private bool RebuildColumnsIfNeeded()
	{
		UpdateColumnMetrics();
		if (lines == null || textColumns == null)
		{
			return false;
		}
		int num = GetPopulatedColumnCount(lines.Length, gridColumnCount);
		if (num == populatedColumnCount)
		{
			return false;
		}
		populatedColumnCount = num;
		int num2 = 0;
		int num3 = lines.Length / populatedColumnCount;
		int num4 = lines.Length % populatedColumnCount;
		for (int i = 0; i < textColumns.Length; i++)
		{
			if (i >= populatedColumnCount)
			{
				setText(textColumns[i], "");
				continue;
			}
			int num5 = num3 + ((i < num4) ? 1 : 0);
			setText(textColumns[i], string.Join("\n", lines, num2, num5));
			num2 += num5;
		}
		return true;
	}

	private void UpdateColumnMetrics()
	{
		float num = Mathf.Max(0f, base.rectTransform.rect.width - (float)base.padding.horizontal);
		gridColumnCount = Mathf.Max(Mathf.FloorToInt((num + 24f) / 264f), 1);
		columnWidth = Mathf.Max(0f, (num - (float)(gridColumnCount - 1) * 24f) / (float)gridColumnCount);
	}

	private static int GetPopulatedColumnCount(int lineCount, int gridColumnCount)
	{
		return Mathf.Min(gridColumnCount, GetMaxPopulatedColumnCount(lineCount));
	}

	public static int GetMaxPopulatedColumnCount(int lineCount)
	{
		return Mathf.Max(1, lineCount / 3);
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
			FilePathsData = new byte[8177]
			{
				0, 0, 0, 2, 0, 0, 0, 36, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 65,
				99, 104, 105, 101, 118, 101, 109, 101, 110, 116,
				115, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 40, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 97, 109, 101, 114, 97, 67,
				111, 110, 116, 114, 111, 108, 108, 101, 114, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 36,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 67, 104, 101, 97, 116, 67, 111, 110, 115,
				111, 108, 101, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 49, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 67, 111, 110, 116, 101,
				110, 116, 92, 70, 97, 114, 109, 79, 98, 106,
				101, 99, 116, 83, 92, 65, 112, 112, 108, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				50, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 66, 97, 109, 98, 111, 111, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 53, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 70, 97,
				114, 109, 79, 98, 106, 101, 99, 116, 83, 92,
				66, 117, 115, 104, 80, 108, 97, 110, 116, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 50,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 67, 111, 110, 116, 101, 110, 116, 92, 70,
				97, 114, 109, 79, 98, 106, 101, 99, 116, 83,
				92, 67, 97, 99, 116, 117, 115, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 55, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 67,
				111, 110, 116, 101, 110, 116, 92, 70, 97, 114,
				109, 79, 98, 106, 101, 99, 116, 83, 92, 68,
				101, 97, 100, 80, 117, 109, 112, 107, 105, 110,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				52, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 68, 105, 110, 111, 115, 97, 117, 114,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				52, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 68, 121, 110, 97, 109, 105, 116, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				52, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 69, 110, 116, 105, 116, 121, 83, 79,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				54, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 70, 97, 114, 109, 79, 98, 106, 101,
				99, 116, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 58, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 67, 111, 110, 116, 101, 110,
				116, 92, 70, 97, 114, 109, 79, 98, 106, 101,
				99, 116, 83, 92, 71, 114, 105, 100, 67, 111,
				110, 116, 114, 111, 108, 108, 101, 114, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 52, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 70, 97,
				114, 109, 79, 98, 106, 101, 99, 116, 83, 92,
				71, 114, 111, 117, 110, 100, 83, 79, 46, 99,
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
				46, 99, 115, 0, 0, 0, 2, 0, 0, 0,
				62, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 77, 117, 115, 104, 114, 111, 111, 109,
				67, 111, 110, 116, 114, 111, 108, 108, 101, 114,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				60, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				70, 97, 114, 109, 79, 98, 106, 101, 99, 116,
				83, 92, 77, 117, 115, 104, 114, 111, 111, 109,
				71, 114, 111, 117, 110, 100, 83, 79, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 51, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 70, 97,
				114, 109, 79, 98, 106, 101, 99, 116, 83, 92,
				80, 117, 109, 112, 107, 105, 110, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 61, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 67,
				111, 110, 116, 101, 110, 116, 92, 70, 97, 114,
				109, 79, 98, 106, 101, 99, 116, 83, 92, 80,
				117, 109, 112, 107, 105, 110, 67, 111, 110, 116,
				114, 111, 108, 108, 101, 114, 46, 99, 115, 0,
				0, 0, 2, 0, 0, 0, 61, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 70, 97, 114, 109,
				79, 98, 106, 101, 99, 116, 83, 92, 80, 121,
				114, 97, 109, 105, 100, 67, 111, 110, 116, 114,
				111, 108, 108, 101, 114, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 48, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 67, 111, 110,
				116, 101, 110, 116, 92, 70, 97, 114, 109, 79,
				98, 106, 101, 99, 116, 83, 92, 82, 105, 99,
				101, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 53, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 111, 110, 116, 101, 110, 116,
				92, 70, 97, 114, 109, 79, 98, 106, 101, 99,
				116, 83, 92, 83, 117, 110, 102, 108, 111, 119,
				101, 114, 46, 99, 115, 0, 0, 0, 2, 0,
				0, 0, 61, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 67, 111, 110, 116, 101, 110,
				116, 92, 70, 97, 114, 109, 79, 98, 106, 101,
				99, 116, 83, 92, 83, 119, 101, 101, 112, 101,
				114, 67, 111, 110, 116, 114, 111, 108, 108, 101,
				114, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 52, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 111, 110, 116, 101, 110, 116,
				92, 70, 97, 114, 109, 79, 98, 106, 101, 99,
				116, 83, 92, 84, 114, 101, 97, 115, 117, 114,
				101, 46, 99, 115, 0, 0, 0, 3, 0, 0,
				0, 65, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 111, 110, 116, 101, 110, 116,
				92, 70, 97, 114, 109, 79, 98, 106, 101, 99,
				116, 83, 92, 84, 114, 101, 97, 115, 117, 114,
				101, 77, 97, 112, 67, 111, 110, 116, 114, 111,
				108, 108, 101, 114, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 53, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 67, 111, 110, 116,
				101, 110, 116, 92, 70, 97, 114, 109, 79, 98,
				106, 101, 99, 116, 83, 92, 84, 114, 101, 101,
				80, 108, 97, 110, 116, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 63, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 67, 111, 110,
				116, 101, 110, 116, 92, 70, 97, 114, 109, 79,
				98, 106, 101, 99, 116, 83, 92, 85, 110, 100,
				101, 114, 103, 114, 111, 117, 110, 100, 84, 114,
				101, 97, 115, 117, 114, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 48, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 72, 97, 116, 115,
				92, 68, 105, 110, 111, 115, 97, 117, 114, 72,
				97, 116, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 48, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 67, 111, 110, 116, 101, 110,
				116, 92, 72, 97, 116, 115, 92, 68, 121, 110,
				97, 109, 105, 116, 101, 72, 97, 116, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 40, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 72, 97,
				116, 115, 92, 72, 97, 116, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 42, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 72, 97, 116, 115,
				92, 72, 97, 116, 83, 79, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 45, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 76, 101, 97, 100,
				101, 114, 98, 111, 97, 114, 100, 83, 79, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 47,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 67, 111, 110, 116, 101, 110, 116, 92, 82,
				101, 115, 111, 117, 114, 99, 101, 77, 97, 110,
				97, 103, 101, 114, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 39, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 67, 111, 110, 116,
				101, 110, 116, 92, 84, 114, 97, 100, 101, 83,
				79, 46, 99, 115, 0, 0, 0, 2, 0, 0,
				0, 40, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 111, 110, 116, 101, 110, 116,
				92, 85, 110, 108, 111, 99, 107, 83, 79, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 70,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 67, 111, 110, 116, 101, 110, 116, 92, 87,
				111, 114, 108, 100, 71, 101, 110, 92, 65, 100,
				100, 105, 116, 105, 118, 101, 83, 116, 97, 98,
				105, 108, 105, 116, 121, 78, 111, 105, 115, 101,
				70, 101, 97, 116, 117, 114, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 53, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 67,
				111, 110, 116, 101, 110, 116, 92, 87, 111, 114,
				108, 100, 71, 101, 110, 92, 66, 108, 111, 99,
				107, 70, 101, 97, 116, 117, 114, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 52, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 87, 111,
				114, 108, 100, 71, 101, 110, 92, 67, 108, 97,
				121, 70, 101, 97, 116, 117, 114, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 52, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 87, 111,
				114, 108, 100, 71, 101, 110, 92, 67, 111, 97,
				108, 70, 101, 97, 116, 117, 114, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 62, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 87, 111,
				114, 108, 100, 71, 101, 110, 92, 68, 117, 109,
				109, 121, 71, 114, 97, 115, 115, 108, 97, 110,
				100, 70, 101, 97, 116, 117, 114, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 56, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 87, 111,
				114, 108, 100, 71, 101, 110, 92, 70, 117, 108,
				108, 83, 105, 122, 101, 70, 101, 97, 116, 117,
				114, 101, 46, 99, 115, 0, 0, 0, 3, 0,
				0, 0, 54, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 67, 111, 110, 116, 101, 110,
				116, 92, 87, 111, 114, 108, 100, 71, 101, 110,
				92, 71, 114, 111, 117, 110, 100, 70, 101, 97,
				116, 117, 114, 101, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 59, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 67, 111, 110, 116,
				101, 110, 116, 92, 87, 111, 114, 108, 100, 71,
				101, 110, 92, 72, 97, 114, 100, 80, 97, 116,
				99, 104, 101, 115, 70, 101, 97, 116, 117, 114,
				101, 46, 99, 115, 0, 0, 0, 2, 0, 0,
				0, 64, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 67, 111, 110, 116, 101, 110, 116,
				92, 87, 111, 114, 108, 100, 71, 101, 110, 92,
				76, 97, 121, 101, 114, 101, 100, 71, 114, 111,
				117, 110, 100, 71, 101, 110, 70, 101, 97, 116,
				117, 114, 101, 46, 99, 115, 0, 0, 0, 2,
				0, 0, 0, 56, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 67, 111, 110, 116, 101,
				110, 116, 92, 87, 111, 114, 108, 100, 71, 101,
				110, 92, 77, 117, 115, 104, 114, 111, 111, 109,
				70, 101, 97, 116, 117, 114, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 55, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 67,
				111, 110, 116, 101, 110, 116, 92, 87, 111, 114,
				108, 100, 71, 101, 110, 92, 79, 114, 101, 86,
				101, 105, 110, 70, 101, 97, 116, 117, 114, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				65, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 67, 111, 110, 116, 101, 110, 116, 92,
				87, 111, 114, 108, 100, 71, 101, 110, 92, 80,
				101, 116, 114, 105, 102, 105, 101, 100, 80, 117,
				109, 112, 107, 105, 110, 115, 70, 101, 97, 116,
				117, 114, 101, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 55, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 67, 111, 110, 116, 101,
				110, 116, 92, 87, 111, 114, 108, 100, 71, 101,
				110, 92, 80, 121, 114, 97, 109, 105, 100, 70,
				101, 97, 116, 117, 114, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 54, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 87, 111, 114, 108,
				100, 71, 101, 110, 92, 81, 117, 97, 114, 116,
				122, 70, 101, 97, 116, 117, 114, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 60, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				67, 111, 110, 116, 101, 110, 116, 92, 87, 111,
				114, 108, 100, 71, 101, 110, 92, 83, 112, 101,
				99, 105, 97, 108, 83, 111, 105, 108, 115, 70,
				101, 97, 116, 117, 114, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 62, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 87, 111, 114, 108,
				100, 71, 101, 110, 92, 83, 119, 101, 101, 112,
				101, 114, 83, 116, 114, 97, 116, 117, 109, 70,
				101, 97, 116, 117, 114, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 59, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 67, 111,
				110, 116, 101, 110, 116, 92, 87, 111, 114, 108,
				100, 71, 101, 110, 92, 84, 114, 101, 97, 115,
				117, 114, 101, 77, 97, 112, 70, 101, 97, 116,
				117, 114, 101, 46, 99, 115, 0, 0, 0, 4,
				0, 0, 0, 42, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 69, 102, 102, 101, 99,
				116, 115, 92, 86, 70, 88, 77, 97, 110, 97,
				103, 101, 114, 46, 99, 115, 0, 0, 0, 1,
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
				46, 99, 115, 0, 0, 0, 2, 0, 0, 0,
				41, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 70, 97, 114, 109, 92, 70, 97, 114,
				109, 82, 101, 110, 100, 101, 114, 101, 114, 46,
				99, 115, 0, 0, 0, 2, 0, 0, 0, 40,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 70, 97, 114, 109, 92, 71, 114, 105, 100,
				77, 97, 110, 97, 103, 101, 114, 46, 99, 115,
				0, 0, 0, 2, 0, 0, 0, 39, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 70,
				97, 114, 109, 92, 71, 114, 111, 117, 110, 100,
				68, 97, 116, 97, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 39, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 70, 97, 114, 109,
				92, 73, 83, 105, 109, 82, 117, 110, 110, 101,
				114, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 39, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 70, 97, 114, 109, 92, 73, 116,
				101, 109, 69, 102, 102, 101, 99, 116, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 36, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				70, 97, 114, 109, 92, 77, 97, 105, 110, 83,
				105, 109, 46, 99, 115, 0, 0, 0, 2, 0,
				0, 0, 38, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 70, 97, 114, 109, 92, 80,
				105, 103, 103, 121, 66, 97, 110, 107, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 42, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				70, 97, 114, 109, 92, 82, 101, 110, 100, 101,
				114, 80, 97, 99, 107, 97, 103, 101, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 39, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				70, 97, 114, 109, 92, 83, 105, 109, 117, 108,
				97, 116, 105, 111, 110, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 34, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 70, 97, 114,
				109, 92, 85, 73, 83, 105, 109, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 33, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 73,
				110, 112, 117, 116, 66, 111, 115, 115, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 49, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 66,
				117, 105, 108, 116, 105, 110, 70, 117, 110, 99,
				116, 105, 111, 110, 115, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 42, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 69, 120, 101, 99,
				117, 116, 105, 111, 110, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 39, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 76, 111, 103, 103,
				101, 114, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 44, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 80, 114, 111, 103, 76, 97,
				110, 103, 92, 77, 111, 100, 117, 108, 101, 83,
				116, 97, 116, 101, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 53, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 80, 114, 111, 103,
				76, 97, 110, 103, 92, 78, 111, 100, 101, 115,
				92, 65, 115, 115, 105, 103, 110, 109, 101, 110,
				116, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 53, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 66, 105, 110, 97, 114, 121, 69, 120,
				112, 114, 78, 111, 100, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 50, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 80, 114,
				111, 103, 76, 97, 110, 103, 92, 78, 111, 100,
				101, 115, 92, 66, 114, 97, 99, 107, 101, 116,
				78, 111, 100, 101, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 49, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 80, 114, 111, 103,
				76, 97, 110, 103, 92, 78, 111, 100, 101, 115,
				92, 66, 114, 97, 110, 99, 104, 78, 111, 100,
				101, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 48, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 78, 111, 100, 101, 115, 92, 66, 114,
				101, 97, 107, 78, 111, 100, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 47, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 80,
				114, 111, 103, 76, 97, 110, 103, 92, 78, 111,
				100, 101, 115, 92, 67, 97, 108, 108, 78, 111,
				100, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 53, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 80, 114, 111, 103, 76, 97,
				110, 103, 92, 78, 111, 100, 101, 115, 92, 67,
				111, 109, 112, 97, 114, 105, 115, 111, 110, 78,
				111, 100, 101, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 51, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 80, 114, 111, 103, 76,
				97, 110, 103, 92, 78, 111, 100, 101, 115, 92,
				67, 111, 110, 116, 105, 110, 117, 101, 78, 111,
				100, 101, 46, 99, 115, 0, 0, 0, 2, 0,
				0, 0, 46, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 80, 114, 111, 103, 76, 97,
				110, 103, 92, 78, 111, 100, 101, 115, 92, 68,
				101, 102, 78, 111, 100, 101, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 47, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 80, 114,
				111, 103, 76, 97, 110, 103, 92, 78, 111, 100,
				101, 115, 92, 68, 105, 99, 116, 78, 111, 100,
				101, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 46, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 78, 111, 100, 101, 115, 92, 70, 111,
				114, 78, 111, 100, 101, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 51, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 80, 114, 111,
				103, 76, 97, 110, 103, 92, 78, 111, 100, 101,
				115, 92, 70, 117, 110, 99, 116, 105, 111, 110,
				78, 111, 100, 101, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 49, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 80, 114, 111, 103,
				76, 97, 110, 103, 92, 78, 111, 100, 101, 115,
				92, 71, 108, 111, 98, 97, 108, 78, 111, 100,
				101, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 49, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 78, 111, 100, 101, 115, 92, 73, 109,
				112, 111, 114, 116, 78, 111, 100, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 47, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 76, 105, 115, 116, 78,
				111, 100, 101, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 50, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 80, 114, 111, 103, 76,
				97, 110, 103, 92, 78, 111, 100, 101, 115, 92,
				76, 105, 116, 101, 114, 97, 108, 78, 111, 100,
				101, 46, 99, 115, 0, 0, 0, 2, 0, 0,
				0, 43, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 78, 111, 100, 101, 115, 92, 78, 111,
				100, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 47, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 80, 114, 111, 103, 76, 97,
				110, 103, 92, 78, 111, 100, 101, 115, 92, 78,
				111, 79, 112, 78, 111, 100, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 47, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 80,
				114, 111, 103, 76, 97, 110, 103, 92, 78, 111,
				100, 101, 115, 92, 80, 97, 115, 115, 78, 111,
				100, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 49, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 80, 114, 111, 103, 76, 97,
				110, 103, 92, 78, 111, 100, 101, 115, 92, 82,
				101, 116, 117, 114, 110, 78, 111, 100, 101, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 51,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 80, 114, 111, 103, 76, 97, 110, 103, 92,
				78, 111, 100, 101, 115, 92, 83, 101, 113, 117,
				101, 110, 99, 101, 78, 111, 100, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 46, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 83, 101, 116, 78, 111,
				100, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 48, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 80, 114, 111, 103, 76, 97,
				110, 103, 92, 78, 111, 100, 101, 115, 92, 84,
				117, 112, 108, 101, 78, 111, 100, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 52, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 85, 110, 97, 114, 121,
				69, 120, 112, 114, 78, 111, 100, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 48, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				80, 114, 111, 103, 76, 97, 110, 103, 92, 78,
				111, 100, 101, 115, 92, 86, 97, 108, 117, 101,
				78, 111, 100, 101, 46, 99, 115, 0, 0, 0,
				3, 0, 0, 0, 39, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 80, 114, 111, 103,
				76, 97, 110, 103, 92, 80, 97, 114, 115, 101,
				114, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 45, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 80, 114, 111, 103, 76, 97, 110,
				103, 92, 80, 114, 111, 103, 114, 97, 109, 83,
				116, 97, 116, 101, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 38, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 80, 114, 111, 103,
				76, 97, 110, 103, 92, 83, 99, 111, 112, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				42, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 80, 114, 111, 103, 76, 97, 110, 103,
				92, 84, 111, 107, 101, 110, 105, 122, 101, 114,
				46, 99, 115, 0, 0, 0, 2, 0, 0, 0,
				44, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 80, 114, 111, 103, 76, 97, 110, 103,
				92, 84, 111, 107, 101, 110, 83, 116, 114, 101,
				97, 109, 46, 99, 115, 0, 0, 0, 7, 0,
				0, 0, 29, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 83, 97, 118, 101, 114, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 35,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 83, 116, 101, 97, 109, 83, 99, 114, 105,
				112, 116, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 38, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 83, 116, 101, 97, 109, 83,
				116, 97, 116, 115, 76, 111, 111, 112, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 39, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				85, 73, 92, 66, 108, 105, 110, 107, 77, 97,
				110, 97, 103, 101, 114, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 42, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				66, 114, 101, 97, 107, 80, 111, 105, 110, 116,
				80, 97, 110, 101, 108, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 40, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				67, 111, 100, 101, 67, 111, 109, 112, 108, 101,
				116, 101, 114, 46, 99, 115, 0, 0, 0, 4,
				0, 0, 0, 38, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 67, 111,
				100, 101, 69, 120, 97, 109, 112, 108, 101, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 37,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 67, 111, 100, 101, 79, 112,
				116, 105, 111, 110, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 37, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 67,
				111, 100, 101, 87, 105, 110, 100, 111, 119, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 42,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 67, 111, 110, 116, 97, 105,
				110, 101, 114, 83, 99, 97, 108, 101, 114, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 42,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 68, 76, 67, 83, 116, 97,
				116, 117, 115, 66, 117, 116, 116, 111, 110, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 37,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 68, 111, 99, 115, 87, 105,
				110, 100, 111, 119, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 43, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 68,
				114, 111, 112, 100, 111, 119, 110, 84, 111, 111,
				108, 116, 105, 112, 115, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 39, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				69, 114, 114, 111, 114, 77, 101, 115, 115, 97,
				103, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 41, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 70, 108, 97,
				115, 104, 105, 110, 103, 66, 117, 116, 116, 111,
				110, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 35, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 72, 97, 116, 80,
				111, 112, 117, 112, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 53, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 72,
				111, 114, 105, 122, 111, 110, 116, 97, 108, 70,
				105, 116, 76, 97, 121, 111, 117, 116, 69, 108,
				101, 109, 101, 110, 116, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 38, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				73, 109, 97, 103, 101, 76, 111, 97, 100, 101,
				114, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 36, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 73, 110, 118, 101,
				110, 116, 111, 114, 121, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 33, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				73, 116, 101, 109, 85, 73, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 38, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 85, 73,
				92, 76, 101, 97, 100, 101, 114, 98, 111, 97,
				114, 100, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 43, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 76, 101, 97,
				100, 101, 114, 98, 111, 97, 114, 100, 69, 110,
				116, 114, 121, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 45, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 76, 101,
				97, 100, 101, 114, 98, 111, 97, 114, 100, 77,
				97, 110, 97, 103, 101, 114, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 39, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 85, 73,
				92, 77, 97, 114, 107, 100, 111, 119, 110, 76,
				105, 110, 107, 46, 99, 115, 0, 0, 0, 4,
				0, 0, 0, 39, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 77, 97,
				114, 107, 100, 111, 119, 110, 84, 101, 120, 116,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				36, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 77, 101, 110, 117, 92,
				77, 101, 110, 117, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 42, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 77,
				101, 110, 117, 92, 79, 112, 116, 105, 111, 110,
				77, 101, 110, 117, 46, 99, 115, 0, 0, 0,
				1, 0, 0, 0, 43, 92, 65, 115, 115, 101,
				116, 115, 92, 83, 99, 114, 105, 112, 116, 115,
				92, 67, 111, 114, 101, 92, 85, 73, 92, 77,
				101, 110, 117, 92, 83, 97, 118, 101, 67, 104,
				111, 111, 115, 101, 114, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 42, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				77, 101, 110, 117, 92, 83, 97, 118, 101, 79,
				112, 116, 105, 111, 110, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 43, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				79, 112, 101, 110, 70, 101, 101, 100, 98, 97,
				99, 107, 70, 111, 114, 109, 46, 99, 115, 0,
				0, 0, 1, 0, 0, 0, 37, 92, 65, 115,
				115, 101, 116, 115, 92, 83, 99, 114, 105, 112,
				116, 115, 92, 67, 111, 114, 101, 92, 85, 73,
				92, 79, 117, 116, 112, 117, 116, 84, 101, 120,
				116, 46, 99, 115, 0, 0, 0, 2, 0, 0,
				0, 39, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 82, 101, 115, 101,
				97, 114, 99, 104, 77, 101, 110, 117, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 43, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				85, 73, 92, 83, 99, 97, 108, 101, 100, 83,
				99, 114, 111, 108, 108, 82, 101, 99, 116, 46,
				99, 115, 0, 0, 0, 2, 0, 0, 0, 36,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 83, 101, 97, 114, 99, 104,
				66, 111, 120, 46, 99, 115, 0, 0, 0, 1,
				0, 0, 0, 41, 92, 65, 115, 115, 101, 116,
				115, 92, 83, 99, 114, 105, 112, 116, 115, 92,
				67, 111, 114, 101, 92, 85, 73, 92, 83, 112,
				111, 105, 108, 101, 114, 87, 97, 114, 110, 105,
				110, 103, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 38, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 84, 105, 116,
				108, 101, 87, 105, 110, 100, 111, 119, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 41, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				85, 73, 92, 84, 105, 116, 108, 101, 87, 111,
				114, 107, 115, 112, 97, 99, 101, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 63, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 85,
				73, 92, 116, 111, 111, 108, 116, 105, 112, 115,
				92, 67, 117, 115, 116, 111, 109, 83, 116, 97,
				110, 100, 97, 108, 111, 110, 101, 73, 110, 112,
				117, 116, 77, 111, 100, 117, 108, 101, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 43, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				85, 73, 92, 116, 111, 111, 108, 116, 105, 112,
				115, 92, 84, 111, 111, 108, 116, 105, 112, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 51,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 116, 111, 111, 108, 116, 105,
				112, 115, 92, 84, 111, 111, 108, 116, 105, 112,
				65, 99, 99, 101, 115, 115, 111, 114, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 53, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				85, 73, 92, 116, 111, 111, 108, 116, 105, 112,
				115, 92, 84, 111, 111, 108, 116, 105, 112, 80,
				111, 115, 105, 116, 105, 111, 110, 101, 114, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 48,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 116, 111, 111, 108, 116, 105,
				112, 115, 92, 84, 111, 111, 108, 116, 105, 112,
				85, 116, 105, 108, 115, 46, 99, 115, 0, 0,
				0, 1, 0, 0, 0, 36, 92, 65, 115, 115,
				101, 116, 115, 92, 83, 99, 114, 105, 112, 116,
				115, 92, 67, 111, 114, 101, 92, 85, 73, 92,
				85, 110, 108, 111, 99, 107, 66, 111, 120, 46,
				99, 115, 0, 0, 0, 1, 0, 0, 0, 34,
				92, 65, 115, 115, 101, 116, 115, 92, 83, 99,
				114, 105, 112, 116, 115, 92, 67, 111, 114, 101,
				92, 85, 73, 92, 86, 105, 100, 101, 111, 85,
				73, 46, 99, 115, 0, 0, 0, 1, 0, 0,
				0, 38, 92, 65, 115, 115, 101, 116, 115, 92,
				83, 99, 114, 105, 112, 116, 115, 92, 67, 111,
				114, 101, 92, 85, 73, 92, 87, 97, 114, 110,
				105, 110, 103, 73, 99, 111, 110, 46, 99, 115,
				0, 0, 0, 1, 0, 0, 0, 33, 92, 65,
				115, 115, 101, 116, 115, 92, 83, 99, 114, 105,
				112, 116, 115, 92, 67, 111, 114, 101, 92, 85,
				73, 92, 87, 105, 110, 100, 111, 119, 46, 99,
				115, 0, 0, 0, 1, 0, 0, 0, 36, 92,
				65, 115, 115, 101, 116, 115, 92, 83, 99, 114,
				105, 112, 116, 115, 92, 67, 111, 114, 101, 92,
				85, 73, 92, 87, 111, 114, 107, 115, 112, 97,
				99, 101, 46, 99, 115, 0, 0, 0, 1, 0,
				0, 0, 40, 92, 65, 115, 115, 101, 116, 115,
				92, 83, 99, 114, 105, 112, 116, 115, 92, 67,
				111, 114, 101, 92, 85, 73, 92, 87, 111, 114,
				107, 115, 112, 97, 99, 101, 66, 97, 115, 101,
				46, 99, 115, 0, 0, 0, 1, 0, 0, 0,
				46, 92, 65, 115, 115, 101, 116, 115, 92, 83,
				99, 114, 105, 112, 116, 115, 92, 67, 111, 114,
				101, 92, 85, 73, 92, 87, 114, 97, 112, 112,
				105, 110, 103, 76, 97, 121, 111, 117, 116, 71,
				114, 111, 117, 112, 46, 99, 115
			},
			TypesData = new byte[3848]
			{
				0, 0, 0, 0, 13, 124, 65, 99, 104, 105,
				101, 118, 101, 109, 101, 110, 116, 115, 0, 0,
				0, 0, 25, 65, 99, 104, 105, 101, 118, 101,
				109, 101, 110, 116, 115, 124, 73, 116, 101, 109,
				65, 100, 100, 105, 116, 105, 111, 110, 0, 0,
				0, 0, 17, 124, 67, 97, 109, 101, 114, 97,
				67, 111, 110, 116, 114, 111, 108, 108, 101, 114,
				0, 0, 0, 0, 13, 124, 67, 104, 101, 97,
				116, 67, 111, 110, 115, 111, 108, 101, 0, 0,
				0, 0, 6, 124, 65, 112, 112, 108, 101, 0,
				0, 0, 0, 31, 67, 111, 114, 101, 46, 67,
				111, 110, 116, 101, 110, 116, 46, 70, 97, 114,
				109, 79, 98, 106, 101, 99, 116, 83, 124, 66,
				97, 109, 98, 111, 111, 0, 0, 0, 0, 10,
				124, 66, 117, 115, 104, 80, 108, 97, 110, 116,
				0, 0, 0, 0, 7, 124, 67, 97, 99, 116,
				117, 115, 0, 0, 0, 0, 12, 124, 68, 101,
				97, 100, 80, 117, 109, 112, 107, 105, 110, 0,
				0, 0, 0, 9, 124, 68, 105, 110, 111, 115,
				97, 117, 114, 0, 0, 0, 0, 9, 124, 68,
				121, 110, 97, 109, 105, 116, 101, 0, 0, 0,
				0, 9, 124, 69, 110, 116, 105, 116, 121, 83,
				79, 0, 0, 0, 0, 7, 124, 69, 110, 116,
				105, 116, 121, 0, 0, 0, 0, 15, 124, 71,
				114, 105, 100, 67, 111, 110, 116, 114, 111, 108,
				108, 101, 114, 0, 0, 0, 0, 9, 124, 71,
				114, 111, 117, 110, 100, 83, 79, 0, 0, 0,
				0, 25, 71, 114, 111, 117, 110, 100, 83, 79,
				124, 71, 114, 111, 117, 110, 100, 68, 101, 99,
				111, 114, 97, 116, 105, 111, 110, 0, 0, 0,
				0, 9, 124, 71, 114, 111, 119, 97, 98, 108,
				101, 0, 0, 0, 0, 11, 124, 72, 101, 100,
				103, 101, 80, 108, 97, 110, 116, 0, 0, 0,
				0, 19, 124, 77, 117, 115, 104, 114, 111, 111,
				109, 67, 111, 110, 116, 114, 111, 108, 108, 101,
				114, 0, 0, 0, 0, 26, 77, 117, 115, 104,
				114, 111, 111, 109, 67, 111, 110, 116, 114, 111,
				108, 108, 101, 114, 124, 83, 116, 114, 97, 116,
				117, 109, 0, 0, 0, 0, 17, 124, 77, 117,
				115, 104, 114, 111, 111, 109, 71, 114, 111, 117,
				110, 100, 83, 79, 0, 0, 0, 0, 8, 124,
				80, 117, 109, 112, 107, 105, 110, 0, 0, 0,
				0, 18, 124, 80, 117, 109, 112, 107, 105, 110,
				67, 111, 110, 116, 114, 111, 108, 108, 101, 114,
				0, 0, 0, 0, 18, 124, 80, 121, 114, 97,
				109, 105, 100, 67, 111, 110, 116, 114, 111, 108,
				108, 101, 114, 0, 0, 0, 0, 25, 80, 121,
				114, 97, 109, 105, 100, 67, 111, 110, 116, 114,
				111, 108, 108, 101, 114, 124, 80, 121, 114, 97,
				109, 105, 100, 0, 0, 0, 0, 29, 67, 111,
				114, 101, 46, 67, 111, 110, 116, 101, 110, 116,
				46, 70, 97, 114, 109, 79, 98, 106, 101, 99,
				116, 83, 124, 82, 105, 99, 101, 0, 0, 0,
				0, 10, 124, 83, 117, 110, 102, 108, 111, 119,
				101, 114, 0, 0, 0, 0, 18, 124, 83, 119,
				101, 101, 112, 101, 114, 67, 111, 110, 116, 114,
				111, 108, 108, 101, 114, 0, 0, 0, 0, 29,
				83, 119, 101, 101, 112, 101, 114, 67, 111, 110,
				116, 114, 111, 108, 108, 101, 114, 124, 83, 116,
				114, 97, 116, 117, 109, 68, 97, 116, 97, 0,
				0, 0, 0, 9, 124, 84, 114, 101, 97, 115,
				117, 114, 101, 0, 0, 0, 0, 22, 124, 84,
				114, 101, 97, 115, 117, 114, 101, 77, 97, 112,
				67, 111, 110, 116, 114, 111, 108, 108, 101, 114,
				0, 0, 0, 0, 30, 84, 114, 101, 97, 115,
				117, 114, 101, 77, 97, 112, 67, 111, 110, 116,
				114, 111, 108, 108, 101, 114, 124, 80, 97, 116,
				104, 68, 97, 116, 97, 0, 0, 0, 0, 39,
				84, 114, 101, 97, 115, 117, 114, 101, 77, 97,
				112, 67, 111, 110, 116, 114, 111, 108, 108, 101,
				114, 124, 71, 101, 110, 101, 114, 97, 116, 105,
				111, 110, 67, 111, 110, 116, 101, 120, 116, 0,
				0, 0, 0, 10, 124, 84, 114, 101, 101, 80,
				108, 97, 110, 116, 0, 0, 0, 0, 20, 124,
				85, 110, 100, 101, 114, 103, 114, 111, 117, 110,
				100, 84, 114, 101, 97, 115, 117, 114, 101, 0,
				0, 0, 0, 12, 124, 68, 105, 110, 111, 115,
				97, 117, 114, 72, 97, 116, 0, 0, 0, 0,
				12, 124, 68, 121, 110, 97, 109, 105, 116, 101,
				72, 97, 116, 0, 0, 0, 0, 4, 124, 72,
				97, 116, 0, 0, 0, 0, 6, 124, 72, 97,
				116, 83, 79, 0, 0, 0, 0, 14, 124, 76,
				101, 97, 100, 101, 114, 98, 111, 97, 114, 100,
				83, 79, 0, 0, 0, 0, 16, 124, 82, 101,
				115, 111, 117, 114, 99, 101, 77, 97, 110, 97,
				103, 101, 114, 0, 0, 0, 0, 8, 124, 84,
				114, 97, 100, 101, 83, 79, 0, 0, 0, 0,
				9, 124, 85, 110, 108, 111, 99, 107, 83, 79,
				0, 0, 0, 0, 28, 124, 65, 100, 100, 105,
				116, 105, 111, 110, 97, 108, 85, 110, 108, 111,
				99, 107, 82, 101, 113, 117, 105, 114, 101, 109,
				101, 110, 116, 0, 0, 0, 0, 51, 67, 111,
				114, 101, 46, 67, 111, 110, 116, 101, 110, 116,
				46, 87, 111, 114, 108, 100, 71, 101, 110, 124,
				65, 100, 100, 105, 116, 105, 118, 101, 83, 116,
				97, 98, 105, 108, 105, 116, 121, 78, 111, 105,
				115, 101, 70, 101, 97, 116, 117, 114, 101, 0,
				0, 0, 0, 13, 124, 66, 108, 111, 99, 107,
				70, 101, 97, 116, 117, 114, 101, 0, 0, 0,
				0, 12, 124, 67, 108, 97, 121, 70, 101, 97,
				116, 117, 114, 101, 0, 0, 0, 0, 12, 124,
				67, 111, 97, 108, 70, 101, 97, 116, 117, 114,
				101, 0, 0, 0, 0, 22, 124, 68, 117, 109,
				109, 121, 71, 114, 97, 115, 115, 108, 97, 110,
				100, 70, 101, 97, 116, 117, 114, 101, 0, 0,
				0, 0, 16, 124, 70, 117, 108, 108, 83, 105,
				122, 101, 70, 101, 97, 116, 117, 114, 101, 0,
				0, 0, 0, 14, 124, 71, 114, 111, 117, 110,
				100, 70, 101, 97, 116, 117, 114, 101, 0, 0,
				0, 0, 21, 71, 114, 111, 117, 110, 100, 70,
				101, 97, 116, 117, 114, 101, 124, 67, 111, 110,
				116, 101, 120, 116, 0, 0, 0, 0, 30, 71,
				114, 111, 117, 110, 100, 70, 101, 97, 116, 117,
				114, 101, 124, 71, 101, 110, 101, 114, 97, 116,
				101, 100, 70, 101, 97, 116, 117, 114, 101, 0,
				0, 0, 0, 40, 67, 111, 114, 101, 46, 67,
				111, 110, 116, 101, 110, 116, 46, 87, 111, 114,
				108, 100, 71, 101, 110, 124, 72, 97, 114, 100,
				80, 97, 116, 99, 104, 101, 115, 70, 101, 97,
				116, 117, 114, 101, 0, 0, 0, 0, 45, 67,
				111, 114, 101, 46, 67, 111, 110, 116, 101, 110,
				116, 46, 87, 111, 114, 108, 100, 71, 101, 110,
				124, 76, 97, 121, 101, 114, 101, 100, 71, 114,
				111, 117, 110, 100, 71, 101, 110, 70, 101, 97,
				116, 117, 114, 101, 0, 0, 0, 0, 26, 67,
				111, 114, 101, 46, 67, 111, 110, 116, 101, 110,
				116, 46, 87, 111, 114, 108, 100, 71, 101, 110,
				124, 66, 97, 110, 100, 0, 0, 0, 0, 16,
				124, 77, 117, 115, 104, 114, 111, 111, 109, 70,
				101, 97, 116, 117, 114, 101, 0, 0, 0, 0,
				23, 77, 117, 115, 104, 114, 111, 111, 109, 70,
				101, 97, 116, 117, 114, 101, 124, 65, 114, 114,
				97, 121, 50, 68, 0, 0, 0, 0, 15, 124,
				79, 114, 101, 86, 101, 105, 110, 70, 101, 97,
				116, 117, 114, 101, 0, 0, 0, 0, 46, 67,
				111, 114, 101, 46, 67, 111, 110, 116, 101, 110,
				116, 46, 87, 111, 114, 108, 100, 71, 101, 110,
				124, 80, 101, 116, 114, 105, 102, 105, 101, 100,
				80, 117, 109, 112, 107, 105, 110, 115, 70, 101,
				97, 116, 117, 114, 101, 0, 0, 0, 0, 15,
				124, 80, 121, 114, 97, 109, 105, 100, 70, 101,
				97, 116, 117, 114, 101, 0, 0, 0, 0, 18,
				124, 81, 117, 97, 114, 116, 122, 86, 101, 105,
				110, 70, 101, 97, 116, 117, 114, 101, 0, 0,
				0, 0, 20, 124, 83, 112, 101, 99, 105, 97,
				108, 83, 111, 105, 108, 115, 70, 101, 97, 116,
				117, 114, 101, 0, 0, 0, 0, 22, 124, 83,
				119, 101, 101, 112, 101, 114, 83, 116, 114, 97,
				116, 117, 109, 70, 101, 97, 116, 117, 114, 101,
				0, 0, 0, 0, 19, 124, 84, 114, 101, 97,
				115, 117, 114, 101, 77, 97, 112, 70, 101, 97,
				116, 117, 114, 101, 0, 0, 0, 0, 11, 124,
				86, 70, 88, 77, 97, 110, 97, 103, 101, 114,
				0, 0, 0, 0, 17, 124, 77, 111, 118, 105,
				110, 103, 77, 101, 115, 104, 69, 102, 102, 101,
				99, 116, 0, 0, 0, 0, 14, 124, 67, 114,
				117, 109, 98, 108, 101, 69, 102, 102, 101, 99,
				116, 0, 0, 0, 0, 18, 124, 67, 114, 117,
				109, 98, 108, 101, 68, 101, 99, 111, 114, 97,
				116, 105, 111, 110, 0, 0, 0, 0, 6, 124,
				68, 114, 111, 110, 101, 0, 0, 0, 0, 8,
				124, 68, 114, 111, 110, 101, 83, 79, 0, 0,
				0, 0, 5, 124, 70, 97, 114, 109, 0, 0,
				0, 0, 13, 124, 70, 97, 114, 109, 82, 101,
				110, 100, 101, 114, 101, 114, 0, 0, 0, 0,
				23, 70, 97, 114, 109, 82, 101, 110, 100, 101,
				114, 101, 114, 124, 70, 97, 99, 101, 86, 105,
				115, 117, 97, 108, 0, 0, 0, 0, 12, 124,
				71, 114, 105, 100, 77, 97, 110, 97, 103, 101,
				114, 0, 0, 0, 0, 16, 71, 114, 105, 100,
				77, 97, 110, 97, 103, 101, 114, 124, 67, 101,
				108, 108, 0, 0, 0, 0, 11, 124, 71, 114,
				111, 117, 110, 100, 68, 97, 116, 97, 0, 0,
				0, 0, 17, 71, 114, 111, 117, 110, 100, 68,
				97, 116, 97, 124, 71, 114, 111, 117, 110, 100,
				0, 0, 0, 0, 11, 124, 73, 83, 105, 109,
				82, 117, 110, 110, 101, 114, 0, 0, 0, 0,
				11, 124, 73, 116, 101, 109, 69, 102, 102, 101,
				99, 116, 0, 0, 0, 0, 8, 124, 77, 97,
				105, 110, 83, 105, 109, 0, 0, 0, 0, 28,
				77, 97, 105, 110, 83, 105, 109, 124, 76, 101,
				97, 100, 101, 114, 98, 111, 97, 114, 100, 83,
				116, 97, 114, 116, 65, 114, 103, 115, 0, 0,
				0, 0, 10, 124, 80, 105, 103, 103, 121, 66,
				97, 110, 107, 0, 0, 0, 0, 22, 80, 105,
				103, 103, 121, 66, 97, 110, 107, 124, 65, 99,
				116, 105, 118, 101, 69, 102, 102, 101, 99, 116,
				0, 0, 0, 0, 19, 124, 67, 114, 117, 109,
				98, 108, 105, 110, 103, 66, 108, 111, 99, 107,
				67, 97, 108, 108, 0, 0, 0, 0, 17, 124,
				83, 108, 105, 100, 105, 110, 103, 66, 108, 111,
				99, 107, 67, 97, 108, 108, 0, 0, 0, 0,
				11, 124, 83, 105, 109, 117, 108, 97, 116, 105,
				111, 110, 0, 0, 0, 0, 16, 83, 105, 109,
				117, 108, 97, 116, 105, 111, 110, 124, 84, 105,
				109, 101, 114, 0, 0, 0, 0, 6, 124, 85,
				73, 83, 105, 109, 0, 0, 0, 0, 10, 124,
				73, 110, 112, 117, 116, 66, 111, 115, 115, 0,
				0, 0, 0, 17, 124, 66, 117, 105, 108, 116,
				105, 110, 70, 117, 110, 99, 116, 105, 111, 110,
				115, 0, 0, 0, 0, 10, 124, 69, 120, 101,
				99, 117, 116, 105, 111, 110, 0, 0, 0, 0,
				7, 124, 76, 111, 103, 103, 101, 114, 0, 0,
				0, 0, 12, 124, 77, 111, 100, 117, 108, 101,
				83, 116, 97, 116, 101, 0, 0, 0, 0, 15,
				124, 65, 115, 115, 105, 103, 110, 109, 101, 110,
				116, 78, 111, 100, 101, 0, 0, 0, 0, 15,
				124, 66, 105, 110, 97, 114, 121, 69, 120, 112,
				114, 78, 111, 100, 101, 0, 0, 0, 0, 12,
				124, 66, 114, 97, 99, 107, 101, 116, 78, 111,
				100, 101, 0, 0, 0, 0, 11, 124, 66, 114,
				97, 110, 99, 104, 78, 111, 100, 101, 0, 0,
				0, 0, 10, 124, 66, 114, 101, 97, 107, 78,
				111, 100, 101, 0, 0, 0, 0, 9, 124, 67,
				97, 108, 108, 78, 111, 100, 101, 0, 0, 0,
				0, 15, 124, 67, 111, 109, 112, 97, 114, 105,
				115, 111, 110, 78, 111, 100, 101, 0, 0, 0,
				0, 13, 124, 67, 111, 110, 116, 105, 110, 117,
				101, 78, 111, 100, 101, 0, 0, 0, 0, 8,
				124, 68, 101, 102, 78, 111, 100, 101, 0, 0,
				0, 0, 11, 124, 80, 121, 70, 117, 110, 99,
				116, 105, 111, 110, 0, 0, 0, 0, 9, 124,
				68, 105, 99, 116, 78, 111, 100, 101, 0, 0,
				0, 0, 8, 124, 70, 111, 114, 78, 111, 100,
				101, 0, 0, 0, 0, 13, 124, 70, 117, 110,
				99, 116, 105, 111, 110, 78, 111, 100, 101, 0,
				0, 0, 0, 11, 124, 71, 108, 111, 98, 97,
				108, 78, 111, 100, 101, 0, 0, 0, 0, 11,
				124, 73, 109, 112, 111, 114, 116, 78, 111, 100,
				101, 0, 0, 0, 0, 9, 124, 76, 105, 115,
				116, 78, 111, 100, 101, 0, 0, 0, 0, 12,
				124, 76, 105, 116, 101, 114, 97, 108, 78, 111,
				100, 101, 0, 0, 0, 0, 5, 124, 78, 111,
				100, 101, 0, 0, 0, 0, 16, 124, 66, 111,
				120, 101, 100, 78, 111, 100, 101, 80, 97, 114,
				97, 109, 115, 0, 0, 0, 0, 9, 124, 78,
				111, 79, 112, 78, 111, 100, 101, 0, 0, 0,
				0, 9, 124, 80, 97, 115, 115, 78, 111, 100,
				101, 0, 0, 0, 0, 11, 124, 82, 101, 116,
				117, 114, 110, 78, 111, 100, 101, 0, 0, 0,
				0, 13, 124, 83, 101, 113, 117, 101, 110, 99,
				101, 78, 111, 100, 101, 0, 0, 0, 0, 8,
				124, 83, 101, 116, 78, 111, 100, 101, 0, 0,
				0, 0, 10, 124, 84, 117, 112, 108, 101, 78,
				111, 100, 101, 0, 0, 0, 0, 14, 124, 85,
				110, 97, 114, 121, 69, 120, 112, 114, 78, 111,
				100, 101, 0, 0, 0, 0, 10, 124, 86, 97,
				108, 117, 101, 78, 111, 100, 101, 0, 0, 0,
				0, 7, 124, 80, 97, 114, 115, 101, 114, 0,
				0, 0, 0, 8, 124, 80, 114, 111, 103, 114,
				97, 109, 0, 0, 0, 0, 15, 124, 80, 97,
				114, 115, 101, 69, 120, 99, 101, 112, 116, 105,
				111, 110, 0, 0, 0, 0, 13, 124, 80, 114,
				111, 103, 114, 97, 109, 83, 116, 97, 116, 101,
				0, 0, 0, 0, 6, 124, 83, 99, 111, 112,
				101, 0, 0, 0, 0, 10, 124, 84, 111, 107,
				101, 110, 105, 122, 101, 114, 0, 0, 0, 0,
				12, 124, 84, 111, 107, 101, 110, 83, 116, 114,
				101, 97, 109, 0, 0, 0, 0, 6, 124, 84,
				111, 107, 101, 110, 0, 0, 0, 0, 6, 124,
				83, 97, 118, 101, 114, 0, 0, 0, 0, 23,
				83, 97, 118, 101, 114, 124, 80, 101, 110, 100,
				105, 110, 103, 67, 111, 100, 101, 67, 104, 97,
				110, 103, 101, 0, 0, 0, 0, 12, 124, 79,
				108, 100, 83, 97, 118, 101, 71, 97, 109, 101,
				0, 0, 0, 0, 9, 124, 83, 97, 118, 101,
				71, 97, 109, 101, 0, 0, 0, 0, 10, 124,
				84, 105, 116, 108, 101, 83, 97, 118, 101, 0,
				0, 0, 0, 4, 124, 83, 70, 79, 0, 0,
				0, 0, 5, 124, 80, 97, 105, 114, 0, 0,
				0, 0, 12, 124, 83, 116, 101, 97, 109, 83,
				99, 114, 105, 112, 116, 0, 0, 0, 0, 15,
				124, 83, 116, 101, 97, 109, 83, 116, 97, 116,
				115, 76, 111, 111, 112, 0, 0, 0, 0, 13,
				124, 66, 108, 105, 110, 107, 77, 97, 110, 97,
				103, 101, 114, 0, 0, 0, 0, 16, 124, 66,
				114, 101, 97, 107, 80, 111, 105, 110, 116, 80,
				97, 110, 101, 108, 0, 0, 0, 0, 14, 124,
				67, 111, 100, 101, 67, 111, 109, 112, 108, 101,
				116, 101, 114, 0, 0, 0, 0, 12, 124, 67,
				111, 100, 101, 69, 120, 97, 109, 112, 108, 101,
				0, 0, 0, 0, 31, 67, 111, 100, 101, 69,
				120, 97, 109, 112, 108, 101, 124, 80, 111, 105,
				110, 116, 101, 114, 69, 110, 116, 101, 114, 72,
				97, 110, 100, 108, 101, 114, 0, 0, 0, 0,
				31, 67, 111, 100, 101, 69, 120, 97, 109, 112,
				108, 101, 124, 67, 111, 100, 101, 69, 120, 97,
				109, 112, 108, 101, 83, 101, 116, 116, 105, 110,
				103, 115, 0, 0, 0, 0, 41, 67, 111, 100,
				101, 69, 120, 97, 109, 112, 108, 101, 43, 67,
				111, 100, 101, 69, 120, 97, 109, 112, 108, 101,
				83, 101, 116, 116, 105, 110, 103, 115, 124, 73,
				116, 101, 109, 69, 110, 116, 114, 121, 0, 0,
				0, 0, 11, 124, 67, 111, 100, 101, 79, 112,
				116, 105, 111, 110, 0, 0, 0, 0, 11, 124,
				67, 111, 100, 101, 87, 105, 110, 100, 111, 119,
				0, 0, 0, 0, 16, 124, 67, 111, 110, 116,
				97, 105, 110, 101, 114, 83, 99, 97, 108, 101,
				114, 0, 0, 0, 0, 16, 124, 68, 76, 67,
				83, 116, 97, 116, 117, 115, 66, 117, 116, 116,
				111, 110, 0, 0, 0, 0, 11, 124, 68, 111,
				99, 115, 87, 105, 110, 100, 111, 119, 0, 0,
				0, 0, 17, 124, 68, 114, 111, 112, 100, 111,
				119, 110, 84, 111, 111, 108, 116, 105, 112, 115,
				0, 0, 0, 0, 13, 124, 69, 114, 114, 111,
				114, 77, 101, 115, 115, 97, 103, 101, 0, 0,
				0, 0, 15, 124, 70, 108, 97, 115, 104, 105,
				110, 103, 66, 117, 116, 116, 111, 110, 0, 0,
				0, 0, 9, 124, 72, 97, 116, 80, 111, 112,
				117, 112, 0, 0, 0, 0, 27, 124, 72, 111,
				114, 105, 122, 111, 110, 116, 97, 108, 70, 105,
				116, 76, 97, 121, 111, 117, 116, 69, 108, 101,
				109, 101, 110, 116, 0, 0, 0, 0, 12, 124,
				73, 109, 97, 103, 101, 76, 111, 97, 100, 101,
				114, 0, 0, 0, 0, 10, 124, 73, 110, 118,
				101, 110, 116, 111, 114, 121, 0, 0, 0, 0,
				7, 124, 73, 116, 101, 109, 85, 73, 0, 0,
				0, 0, 12, 124, 76, 101, 97, 100, 101, 114,
				98, 111, 97, 114, 100, 0, 0, 0, 0, 17,
				124, 76, 101, 97, 100, 101, 114, 98, 111, 97,
				114, 100, 69, 110, 116, 114, 121, 0, 0, 0,
				0, 19, 124, 76, 101, 97, 100, 101, 114, 98,
				111, 97, 114, 100, 77, 97, 110, 97, 103, 101,
				114, 0, 0, 0, 0, 13, 124, 77, 97, 114,
				107, 100, 111, 119, 110, 76, 105, 110, 107, 0,
				0, 0, 0, 13, 124, 77, 97, 114, 107, 100,
				111, 119, 110, 84, 101, 120, 116, 0, 0, 0,
				0, 24, 77, 97, 114, 107, 100, 111, 119, 110,
				84, 101, 120, 116, 124, 84, 101, 120, 116, 83,
				101, 99, 116, 105, 111, 110, 0, 0, 0, 0,
				22, 77, 97, 114, 107, 100, 111, 119, 110, 84,
				101, 120, 116, 124, 72, 111, 118, 101, 114, 73,
				110, 102, 111, 0, 0, 0, 0, 30, 124, 85,
				110, 100, 101, 114, 108, 105, 110, 101, 77, 101,
				115, 104, 67, 97, 112, 97, 99, 105, 116, 121,
				82, 101, 115, 101, 114, 118, 101, 114, 0, 0,
				0, 0, 5, 124, 77, 101, 110, 117, 0, 0,
				0, 0, 11, 124, 79, 112, 116, 105, 111, 110,
				77, 101, 110, 117, 0, 0, 0, 0, 12, 124,
				83, 97, 118, 101, 67, 104, 111, 111, 115, 101,
				114, 0, 0, 0, 0, 11, 124, 83, 97, 118,
				101, 79, 112, 116, 105, 111, 110, 0, 0, 0,
				0, 17, 124, 79, 112, 101, 110, 70, 101, 101,
				100, 98, 97, 99, 107, 70, 111, 114, 109, 0,
				0, 0, 0, 11, 124, 79, 117, 116, 112, 117,
				116, 84, 101, 120, 116, 0, 0, 0, 0, 13,
				124, 82, 101, 115, 101, 97, 114, 99, 104, 77,
				101, 110, 117, 0, 0, 0, 0, 25, 82, 101,
				115, 101, 97, 114, 99, 104, 77, 101, 110, 117,
				124, 85, 110, 108, 111, 99, 107, 76, 97, 121,
				111, 117, 116, 0, 0, 0, 0, 17, 124, 83,
				99, 97, 108, 101, 100, 83, 99, 114, 111, 108,
				108, 82, 101, 99, 116, 0, 0, 0, 0, 10,
				124, 83, 101, 97, 114, 99, 104, 66, 111, 120,
				0, 0, 0, 0, 22, 83, 101, 97, 114, 99,
				104, 66, 111, 120, 124, 83, 101, 97, 114, 99,
				104, 82, 101, 115, 117, 108, 116, 0, 0, 0,
				0, 15, 124, 83, 112, 111, 105, 108, 101, 114,
				87, 97, 114, 110, 105, 110, 103, 0, 0, 0,
				0, 12, 124, 84, 105, 116, 108, 101, 87, 105,
				110, 100, 111, 119, 0, 0, 0, 0, 15, 124,
				84, 105, 116, 108, 101, 87, 111, 114, 107, 115,
				112, 97, 99, 101, 0, 0, 0, 0, 28, 124,
				67, 117, 115, 116, 111, 109, 83, 116, 97, 110,
				100, 97, 108, 111, 110, 101, 73, 110, 112, 117,
				116, 77, 111, 100, 117, 108, 101, 0, 0, 0,
				0, 8, 124, 84, 111, 111, 108, 116, 105, 112,
				0, 0, 0, 0, 16, 124, 84, 111, 111, 108,
				116, 105, 112, 65, 99, 99, 101, 115, 115, 111,
				114, 0, 0, 0, 0, 18, 124, 84, 111, 111,
				108, 116, 105, 112, 80, 111, 115, 105, 116, 105,
				111, 110, 101, 114, 0, 0, 0, 0, 13, 124,
				84, 111, 111, 108, 116, 105, 112, 85, 116, 105,
				108, 115, 0, 0, 0, 0, 10, 124, 85, 110,
				108, 111, 99, 107, 66, 111, 120, 0, 0, 0,
				0, 8, 124, 86, 105, 100, 101, 111, 85, 73,
				0, 0, 0, 0, 12, 124, 87, 97, 114, 110,
				105, 110, 103, 73, 99, 111, 110, 0, 0, 0,
				0, 7, 124, 87, 105, 110, 100, 111, 119, 0,
				0, 0, 0, 10, 124, 87, 111, 114, 107, 115,
				112, 97, 99, 101, 0, 0, 0, 0, 14, 124,
				87, 111, 114, 107, 115, 112, 97, 99, 101, 66,
				97, 115, 101, 0, 0, 0, 0, 20, 124, 87,
				114, 97, 112, 112, 105, 110, 103, 76, 97, 121,
				111, 117, 116, 71, 114, 111, 117, 112
			},
			TotalFiles = 151,
			TotalTypes = 192,
			IsEditorOnly = false
		};
	}
}
namespace Core.Content.WorldGen
{
	[CreateAssetMenu(fileName = "AdditiveStabilityNoiseFeature", menuName = "ScriptableObjects/AdditiveStabilityNoise", order = 20)]
	public class AdditiveStabilityNoiseFeature : GroundFeature
	{
		public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
		{
			Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
			OpenSimplexNoise openSimplexNoise = new OpenSimplexNoise(ctx.random.Next());
			for (int i = 0; i < worldSize.x; i++)
			{
				for (int j = 0; j < worldSize.y; j++)
				{
					for (int k = ctx.chunk.startingDepth; k < ctx.chunk.startingDepth + 16; k++)
					{
						int num = (int)(3.0 * Math.Abs(openSimplexNoise.Evaluate((double)i / 3.0, (double)j / 3.0, (double)k / 3.0))) - 1;
						GroundData.Ground ground = ctx.chunk.GroundAt(new Vector3Int(i, j, k), worldSize);
						if (ground.groundSo != null)
						{
							int overrideStability = Math.Clamp(ground.stability + num, 1, DesignConstants.Inst.balancingDesignConstants.maxStability);
							ctx.chunk.GroundAt(new Vector3Int(i, j, k), worldSize) = new GroundData.Ground(ground.groundSo, ground.hardness, overrideStability);
						}
					}
				}
			}
			return new BoundingBoxInt[0];
		}
	}
	[CreateAssetMenu(fileName = "HardPatchesFeature ", menuName = "ScriptableObjects/HardPatches", order = 5)]
	public class HardPatchesFeature : GroundFeature
	{
		public int periodHorizontal = 4;

		public int periodVertical = 8;

		public float skipAllChance = 0.35f;

		public float skipTileChance = 0.1f;

		public float hardnessIncreaseFrequency = 0.2f;

		public int baseHardness = 2;

		private const int patchSize = 2;

		public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
		{
			Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
			List<BoundingBoxInt> list = new List<BoundingBoxInt>();
			int num = ctx.chunk.startingDepth + 16;
			for (int i = 0; i < worldSize.x; i += periodHorizontal)
			{
				int num2 = Math.Min(periodHorizontal, worldSize.x - i) - 2;
				if (num2 < 0)
				{
					continue;
				}
				for (int j = 0; j < worldSize.y; j += periodHorizontal)
				{
					int num3 = Math.Min(periodHorizontal, worldSize.y - j) - 2;
					if (num3 < 0)
					{
						continue;
					}
					for (int k = ctx.chunk.startingDepth; k < num; k += periodVertical)
					{
						int num4 = Math.Min(periodVertical, num - k) - 2;
						if (num4 < 0 || ctx.random.NextDouble() < (double)skipAllChance)
						{
							continue;
						}
						int num5 = i + ctx.random.Next(num2 + 1);
						int num6 = j + ctx.random.Next(num3 + 1);
						int num7 = k + ctx.random.Next(num4 + 1);
						for (int l = 0; l < 2; l++)
						{
							for (int m = 0; m < 2; m++)
							{
								for (int n = 0; n < 2; n++)
								{
									if (!((float)ctx.random.Next() < skipTileChance))
									{
										int num8 = (int)((float)baseHardness + hardnessIncreaseFrequency * (float)(num7 + n - ctx.loopStartDepth));
										ctx.chunk.GroundAt(num5 + l, num6 + m, num7 + n, worldSize) = new GroundData.Ground(ResourceManager.GetGround("rock"), num8, Math.Min(num8, DesignConstants.Inst.balancingDesignConstants.maxStability));
									}
								}
							}
						}
						list.Add(new BoundingBoxInt(new Vector3Int(num5, num6, num7), new Vector3Int(num5 + 2, num6 + 2, num7 + 2)));
					}
				}
			}
			return list;
		}
	}
	[CreateAssetMenu(fileName = "LayeredGroundGenFeature ", menuName = "ScriptableObjects/LayeredGroundGen", order = 20)]
	public class LayeredGroundGenFeature : GroundFeature
	{
		public float hardnessIncreaseFrequency = 0.2f;

		public List<Band> bands = new List<Band>
		{
			new Band
			{
				start = -1,
				end = -1,
				hardnessAfterTransition = HardnessBehaviorAfterTransition.Reset
			}
		};

		public void OnValidate()
		{
			bands.Sort((Band b1, Band b2) => b1.start.CompareTo(b2.start));
			int num = bands.FindIndex((Band b) => b.groundSoOrNull == null && b.hardnessAfterTransition != HardnessBehaviorAfterTransition.Reset);
			if (num != -1)
			{
				UnityEngine.Debug.LogError(string.Format("Ground band {0} must set a {1} or {2} must be {3}", num, "GroundSO", "hardnessAfterTransition", "Reset"));
			}
		}

		public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
		{
			OpenSimplexNoise noise = new OpenSimplexNoise(ctx.random.Next());
			Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
			for (int i = 0; i < worldSize.x; i++)
			{
				for (int j = 0; j < worldSize.y; j++)
				{
					for (int k = ctx.chunk.startingDepth; k < ctx.chunk.startingDepth + 16; k++)
					{
						if ((object)ctx.chunk.GroundAt(i, j, k, worldSize).groundSo == null)
						{
							ctx.chunk.GroundAt(i, j, k, worldSize) = MakeGroundTile(in ctx, i, j, k, noise, ResourceManager.GetGround("dirt"));
						}
					}
				}
			}
			return new BoundingBoxInt[0];
		}

		public GroundData.Ground MakeGroundTile(in Context ctx, int x, int y, int z, OpenSimplexNoise noise, GroundSO defaultGround)
		{
			if (z >= 200000000)
			{
				return new GroundData.Ground(ResourceManager.GetGround("bedrock"));
			}
			int num = ((!ctx.pretendedChunkDepth.HasValue) ? (z - ctx.loopStartDepth) : (z - ctx.chunk.startingDepth + ctx.pretendedChunkDepth.Value));
			int i;
			for (i = 0; i < bands.Count && num >= bands[i].end; i++)
			{
			}
			if (i < bands.Count && num >= bands[i].start)
			{
				return new GroundData.Ground(bands[i].groundSoOrNull ?? defaultGround);
			}
			int end = bands[i - 1].end;
			int num2 = bands[i - 1].groundSoOrNull?.maxHardness ?? defaultGround.maxHardness;
			int num3 = bands[i - 1].hardnessAfterTransition switch
			{
				HardnessBehaviorAfterTransition.ContinueWithSameHardness => -Eval(x, y, end, noise) + num2, 
				HardnessBehaviorAfterTransition.AddOne => -Eval(x, y, end, noise) + num2 + 1, 
				HardnessBehaviorAfterTransition.Reset => 0, 
				_ => throw new ArgumentOutOfRangeException(), 
			};
			int value = Eval(x, y, num, noise) + num3;
			int num4 = Math.Clamp(value, 1, DesignConstants.Inst.balancingDesignConstants.maxHardness);
			int overrideStability = Math.Clamp(value, 1, DesignConstants.Inst.balancingDesignConstants.maxStability);
			return new GroundData.Ground(MapHardnessAndDepthToGroundSO(num4, num, defaultGround), num4, overrideStability);
		}

		private static GroundSO MapHardnessAndDepthToGroundSO(int hardness, int loopRelativeDepth, GroundSO defaultGround)
		{
			if (loopRelativeDepth < 16)
			{
				return ResourceManager.GetGround("dirt");
			}
			return hardness switch
			{
				2 => ResourceManager.GetGround("rock"), 
				3 => ResourceManager.GetGround("rock"), 
				_ => defaultGround, 
			};
		}

		private int Eval(int x, int y, int loopRelativeZ, OpenSimplexNoise noise)
		{
			float num = (float)noise.Evaluate((float)x / 25f + 100f, (float)y / 25f + 100f, (float)loopRelativeZ / 10f);
			float b = ((float)loopRelativeZ + num * 15f) * hardnessIncreaseFrequency;
			float a = (float)noise.Evaluate(x, y, loopRelativeZ) + 1f;
			float num2 = (float)noise.Evaluate(-100.0, -100.0, (float)loopRelativeZ / 15f) * 0.5f + 0.5f;
			b = Mathf.Lerp(a, b, num2 * 0.66f + 0.33f);
			float num3 = 1.2f;
			return (int)((float)Mathf.RoundToInt(b / num3) * num3);
		}
	}
	[Serializable]
	public class Band
	{
		public int start;

		public int end;

		public GroundSO groundSoOrNull;

		public Fuziness endFuziness;

		public HardnessBehaviorAfterTransition hardnessAfterTransition;
	}
	public enum Fuziness
	{
		None,
		Upwards,
		Downwards
	}
	public enum HardnessBehaviorAfterTransition
	{
		ContinueWithSameHardness,
		AddOne,
		Reset
	}
	[CreateAssetMenu(fileName = "PetrifiedPumpkinsFeature", menuName = "ScriptableObjects/PetrifiedPumpkins", order = 5)]
	public class PetrifiedPumpkinsFeature : GroundFeature
	{
		public float probability = 0.4f;

		public int periodHorizontalSmall = 6;

		public int periodHorizontalLarge = 8;

		public int periodVertical = 8;

		public float skipSpawnChance = 0.4f;

		public float largePumpkinChance = 0.3f;

		public Mesh topMiddleMesh;

		public Mesh topDiagonalMesh;

		public Mesh topCornerMesh;

		public Mesh sideCornerMeshL;

		public Mesh sideCornerMeshR;

		public Mesh sideEdgeMeshL;

		public Mesh sideEdgeMeshR;

		public Mesh straightMesh;

		public Mesh straightEdgeMesh;

		private const int patchSizeSmall = 3;

		private const int patchSizeLarge = 5;

		private static readonly Color decoratedBlockColor = new Color32(228, 148, 0, byte.MaxValue);

		private readonly Dictionary<int, GroundSO[,,]> decoratedGrounds = new Dictionary<int, GroundSO[,,]>();

		public override void OnLoaded()
		{
			decoratedGrounds.Clear();
			CreateDecoratedGrounds(3);
			CreateDecoratedGrounds(5);
		}

		public override float GetProbability(in Context ctx)
		{
			Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
			if (worldSize.x <= 3 && worldSize.y <= 3)
			{
				return 0f;
			}
			return probability;
		}

		public override IEnumerable<BoundingBoxInt> Generate(in Context ctx)
		{
			Vector2Int worldSize = ctx.sim.farm.grid.WorldSize;
			bool flag = worldSize.x > 5;
			int num = (flag ? periodHorizontalSmall : periodHorizontalLarge);
			List<BoundingBoxInt> list = new List<BoundingBoxInt>();
			int num2 = ctx.chunk.startingDepth + 16;
			for (int i = 0; i < worldSize.x; i += num)
			{
				int num3 = ((!flag) ? 3 : ((ctx.random.NextDouble() < (double)largePumpkinChance) ? 5 : 3));
				int num4 = Math.Min(num, worldSize.x - i) - num3;
				if (num4 < 0)
				{
					continue;
				}
				for (int j = 0; j < worldSize.y; j += num)
				{
					int num5 = Math.Min(num, worldSize.y - j) - num3;
					if (num5 < 0)
					{
						continue;
					}
					for (int k = ctx.chunk.startingDepth + 1; k < num2; k += periodVertical)
					{
						int num6 = Math.Min(periodVertical, num2 - k) - num3;
						if (num6 < 0 || ctx.random.NextDouble() < (double)skipSpawnChance)
						{
							continue;
						}
						int num7 = i + ctx.random.Next(num4 + 1);
						int num8 = j + ctx.random.Next(num5 + 1);
						int num9 = k + ctx.random.Next(num6 + 1);
						GroundSO[,,] array = decoratedGrounds[num3];
						for (int l = 0; l < num3; l++)
						{
							for (int m = 0; m < num3; m++)
							{
								Vector3Int vector3Int = new Vector3Int(num7 + l, num8 + m, num9 - 1);
								if (!ctx.OtherFeatureContains(vector3Int))
								{
									ctx.chunk.GroundAt(vector3Int, worldSize) = new GroundData.Ground(ResourceManager.GetGround("dirt"), 1, 0);
								}
								for (int n = 0; n < num3; n++)
								{
									ctx.chunk.GroundAt(num7 + l, num8 + m, num9 + n, worldSize) = new GroundData.Ground(array[l, m, n]);
								}
							}
						}
						list.Add(new BoundingBoxInt(new Vector3Int(num7, num8, num9), new Vector3Int(num7 + num3, num8 + num3, num9 + num3)));
					}
				}
			}
			return list;
		}

		private void CreateDecoratedGrounds(int size)
		{
			GroundSO ground = ResourceManager.GetGround("petrified_pumpkin");
			GroundSO[,,] array = new GroundSO[size, size, size];
			for (int i = 0; i < size; i++)
			{
				for (int j = 0; j < size; j++)
				{
					for (int k = 0; k < size; k++)
					{
						List<GroundSO.GroundDecoration> list = new List<GroundSO.GroundDecoration>(3);
						if (k == 0)
						{
							AddTopDecoration(list, i, j, size);
						}
						if (i == 0)
						{
							AddSideDecoration(list, size - 1 - j, k, size, FarmRenderer.FaceDirection.West);
						}
						if (i == size - 1)
						{
							AddSideDecoration(list, j, k, size, FarmRenderer.FaceDirection.East);
						}
						if (j == 0)
						{
							AddSideDecoration(list, i, k, size, FarmRenderer.FaceDirection.South);
						}
						if (j == size - 1)
						{
							AddSideDecoration(list, size - 1 - i, k, size, FarmRenderer.FaceDirection.North);
						}
						bool flag = k == size - 1;
						if (list.Count == 0 && !flag)
						{
							array[i, j, k] = ground;
							continue;
						}
						GroundSO groundSO = UnityEngine.Object.Instantiate(ground);
						groundSO.dropItemId = ground.dropItemId;
						groundSO.decorations = list.ToArray();
						groundSO.colorGradient = CreateDecoratedBlockGradient();
						array[i, j, k] = groundSO;
					}
				}
			}
			decoratedGrounds.Add(size, array);
		}

		private static Gradient CreateDecoratedBlockGradient()
		{
			Gradient gradient = new Gradient();
			gradient.SetKeys(new GradientColorKey[2]
			{
				new GradientColorKey(decoratedBlockColor, 0f),
				new GradientColorKey(decoratedBlockColor, 1f)
			}, new GradientAlphaKey[2]
			{
				new GradientAlphaKey(1f, 0f),
				new GradientAlphaKey(1f, 1f)
			});
			return gradient;
		}

		private void AddTopDecoration(List<GroundSO.GroundDecoration> decorations, int x, int y, int size)
		{
			int num = size - 1;
			int num2 = size / 2;
			bool flag = x == 0 || x == num;
			bool flag2 = y == 0 || y == num;
			Mesh mesh;
			float rotation;
			if (flag && flag2)
			{
				mesh = topCornerMesh;
				rotation = RotationForQuadrant(x, y, num2);
			}
			else if (flag || flag2)
			{
				mesh = straightEdgeMesh;
				rotation = RotationTowardsEdge(x, y, num2);
			}
			else if (x == num2 && y == num2)
			{
				mesh = topMiddleMesh;
				rotation = 0f;
			}
			else if (Math.Abs(x - num2) == Math.Abs(y - num2))
			{
				mesh = topDiagonalMesh;
				rotation = RotationForQuadrant(x, y, num2);
			}
			else
			{
				mesh = straightMesh;
				rotation = RotationTowardsEdge(x, y, num2);
			}
			AddDecoration(decorations, mesh, rotation, FarmRenderer.FaceDirection.Top);
		}

		private void AddSideDecoration(List<GroundSO.GroundDecoration> decorations, int horizontal, int depth, int size, FarmRenderer.FaceDirection face)
		{
			int num = size - 1;
			Mesh mesh = ((depth != 0) ? ((horizontal == 0) ? sideEdgeMeshL : ((horizontal == num) ? sideEdgeMeshR : straightMesh)) : ((horizontal == 0) ? sideCornerMeshL : ((horizontal == num) ? sideCornerMeshR : straightEdgeMesh)));
			AddDecoration(decorations, mesh, -90f, face);
		}

		private static void AddDecoration(List<GroundSO.GroundDecoration> decorations, Mesh mesh, float rotation, FarmRenderer.FaceDirection face)
		{
			if (!(mesh == null))
			{
				decorations.Add(new GroundSO.GroundDecoration
				{
					mesh = mesh,
					wetMeshes = Array.Empty<Mesh>(),
					probability = 1f,
					top = (face == FarmRenderer.FaceDirection.Top),
					sides = (face != FarmRenderer.FaceDirection.Top),
					randomRotation = false,
					fixedRotation = rotation,
					face = face
				});
			}
		}

		private static float RotationTowardsEdge(int x, int y, int middle)
		{
			if (y > middle)
			{
				return 270f;
			}
			if (x > middle)
			{
				return 0f;
			}
			if (y < middle)
			{
				return 90f;
			}
			return 180f;
		}

		private static float RotationForQuadrant(int x, int y, int middle)
		{
			if (x > middle)
			{
				return (y <= middle) ? 90 : 0;
			}
			return (y < middle) ? 180 : 270;
		}
	}
}
namespace Core.Content.FarmObjectS
{
	public class Bamboo : Growable
	{
		public readonly int flowerRangeMin = 2;

		public readonly int flowerRangeMax = 5;

		private const int FLOWERS = 3;

		private List<int> flowerLocations = new List<int>();

		private int indexOfNextGrownFlower;

		private int height = 1;

		protected override float InitialGrowthScale => 0f;

		public int Height => height;

		public override ItemBlock GetYield()
		{
			return GetDrops(height);
		}

		private ItemBlock GetDrops(int numCut)
		{
			double n = objectSO.dropAmount * YieldFactor * (double)Mathf.Pow(numCut, 2f);
			return new ItemBlock(objectSO.dropItemId, n);
		}

		public override ItemBlock Harvest(out Duration collectionDuration)
		{
			collectionDuration = Duration.FromSeconds(0.0);
			CutToHeight(0, collectDrops: false);
			HarvestEffects(HasCompanion());
			if (!Harvestable)
			{
				return ItemBlock.CreateEmpty();
			}
			return GetDrops(height);
		}

		protected override void OnFullyGrown()
		{
			base.OnFullyGrown();
			TryGrowOneStage();
		}

		private void TryGrowOneStage(int ignoreDroneId = -1)
		{
			if (AnyDronesBlockingGrowth(ignoreDroneId))
			{
				return;
			}
			int num = height;
			List<int> list = flowerLocations;
			if (num < list[list.Count - 1])
			{
				int num2 = flowerLocations[indexOfNextGrownFlower];
				if (height != num2)
				{
					height++;
					RestartGrowth();
				}
			}
		}

		private bool AnyDronesBlockingGrowth(int exceptId = -1)
		{
			for (int i = 0; i < sim.farm.drones.Count; i++)
			{
				if (i != exceptId)
				{
					Vector2Int? vector2Int = sim.farm.drones[i]?.pos;
					Vector2Int vector2Int2 = base.pos;
					if (vector2Int.HasValue && (!vector2Int.HasValue || vector2Int.GetValueOrDefault() == vector2Int2) && sim.farm.drones[i]?.fleightHeight <= height)
					{
						return true;
					}
				}
			}
			return false;
		}

		public void OnDroneEntered(int fleightHeight)
		{
			CutToHeight(fleightHeight);
		}

		public void OnDroneLeft(int droneId)
		{
			if (base.GrownPercent == 1.0)
			{
				TryGrowOneStage(droneId);
			}
		}

		public void CutToHeight(int newHeight, bool collectDrops = true)
		{
			if (newHeight >= height)
			{
				return;
			}
			sim.simRunner?.PlaySound(SoundEffectType.HarvestBamboo, base.pos);
			int depth = sim.farm.grid.CellAt(base.pos).depth;
			float num = Mathf.Pow(height - newHeight, 0.5f);
			float num2 = newHeight;
			int num3 = 0;
			for (int i = newHeight; i < height; i++)
			{
				if ((float)i >= num2 && num3 < 3)
				{
					Vector3 vector = new Vector3(base.pos.x, base.pos.y, depth - i);
					sim.simRunner?.PlayEffect(VFXType.falling_bamboo, GridManager.CellToLocal(vector));
					num2 += num;
					num3++;
				}
			}
			if (collectDrops)
			{
				ItemBlock drops = GetDrops(height - newHeight);
				sim.farm.CollectItems(drops, GetTransform().GetPosition());
			}
			if (newHeight == 0)
			{
				sim.farm.grid.RemoveEntity(base.pos);
				return;
			}
			if (newHeight >= flowerLocations[indexOfNextGrownFlower] - 1)
			{
				indexOfNextGrownFlower = Math.Min(indexOfNextGrownFlower + 1, flowerLocations.Count - 1);
			}
			else
			{
				indexOfNextGrownFlower = 0;
				while (indexOfNextGrownFlower < flowerLocations.Count - 1 && newHeight >= flowerLocations[indexOfNextGrownFlower])
				{
					indexOfNextGrownFlower++;
				}
			}
			height = newHeight;
			Instagrow();
		}

		public override IEnumerable<(Mesh, Matrix4x4)> GetMeshes()
		{
			int flowerMeshIndex = objectSO.meshes.Count - 1;
			int zPos = sim.farm.grid.CellAt(base.pos).depth;
			Matrix4x4 transform = GetTransform();
			for (int i = 0; i < height; i++)
			{
				int index = ((i + 1 == flowerLocations[indexOfNextGrownFlower]) ? flowerMeshIndex : Math.Min(i, flowerMeshIndex - 1));
				Matrix4x4 matrix4x = Matrix4x4.Rotate(transform.rotation);
				if (i == height - 1)
				{
					matrix4x *= Matrix4x4.Scale(transform.lossyScale);
				}
				Vector3 vector = GridManager.CellToLocal(new Vector3Int(base.pos.x, base.pos.y, zPos - i));
				yield return (objectSO.meshes[index], Matrix4x4.Translate(vector) * matrix4x);
			}
		}

		public override void OnRestart()
		{
			base.OnRestart();
			flowerLocations.Clear();
			int num = 1;
			num += sim.randomBamboo.Next(flowerRangeMin, flowerRangeMax) + (int)Math.Round(sim.farm.grid.bambooNoise.Evaluate((double)base.pos.x / 2.0 + 97.0, (double)base.pos.y / 2.0 + 97.0) / 2.0 + 0.5);
			flowerLocations.Add(num);
			num += Mathf.Max(3, sim.randomBamboo.Next(flowerRangeMin, flowerRangeMax) + (int)Math.Round(sim.farm.grid.bambooNoise.Evaluate((double)base.pos.x / 2.0 + 97.0, (double)base.pos.y / 2.0 + 97.0) / 2.0 + 0.5));
			flowerLocations.Add(num);
			num += Mathf.Max(3, sim.randomBamboo.Next(flowerRangeMin, flowerRangeMax) + (int)Math.Round(sim.farm.grid.bambooNoise.Evaluate((double)base.pos.x / 2.0 + 97.0, (double)base.pos.y / 2.0 + 97.0) / 2.0 + 0.5));
			flowerLocations.Add(num);
		}

		public override IPyObject Measure()
		{
			return new PyNumber(flowerLocations[indexOfNextGrownFlower] - 1);
		}
	}
	public class Rice : Growable
	{
		public override void OnPlanted(Drone drone)
		{
			base.OnPlanted(drone);
			if (sim.farm.grid.GroundAt(base.pos).groundSo.objectName == "clay")
			{
				sim.farm.grid.SetGround(base.pos, "rice_terrace");
			}
		}

		protected override void OnFullyGrown()
		{
			base.OnFullyGrown();
			sim.farm.grid.SetGround(base.pos, "dry_rice_terrace");
		}
	}
}
