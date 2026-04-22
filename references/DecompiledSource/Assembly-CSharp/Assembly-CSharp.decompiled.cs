using System;
using System.CodeDom.Compiler;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using TMPro;
using UnityEngine;
using UnityEngine.Rendering;

[assembly: CompilationRelaxations(8)]
[assembly: RuntimeCompatibility(WrapNonExceptionThrows = true)]
[assembly: Debuggable(DebuggableAttribute.DebuggingModes.IgnoreSymbolStoreSequencePoints)]
[assembly: AssemblyVersion("0.0.0.0")]
[CreateAssetMenu(fileName = "Achievement", menuName = "ScriptableObjects/Achievement", order = 1)]
public class AchievementSO : ScriptableObject
{
	public Mesh mesh;

	public string iconText;
}
public class CreateItemTextures : MonoBehaviour
{
	[Serializable]
	public struct NameMeshPair
	{
		public string name;

		public Mesh mesh;

		public NameMeshPair(string name, Mesh mesh)
		{
			this.name = name;
			this.mesh = mesh;
		}
	}

	public enum TextureObjectType
	{
		Item,
		UnlockMeshes,
		Achievements
	}

	public enum OutlineType
	{
		None,
		Outline,
		Underlay
	}

	public Camera captureCamera;

	public Camera uiCamera;

	public MeshFilter itemMeshFilter;

	public RenderPipelineAsset transparentRenderPipelineAsset;

	public Transform itemTransform;

	public TextMeshProUGUI iconText;

	public int width = 256;

	public int height = 256;

	public int frameCount = 60;

	public TextureObjectType textureObjectType;

	public float cameraSizeBoundsScale;

	public float defaultObjectBoundsMagnitude;

	public OutlineType outlineType;

	public int outlineThickness = 1;

	public Color outlineColor = Color.black;

	public Vector2 underlayOffset = new Vector2(1f, -1f);

	public Color achievementBackgroundColor;

	public Color achievementGrayBackgroundColor;

	public Color glowColor;

	public int glowThickness = 2;

	public float glowFactor = 1f;

	public float glowExponent = 1f;

	public Color borderColor;

	public Color borderGrayColor;

	public int borderThickness = 10;

	private void Start()
	{
		Capture();
	}

	private void Capture()
	{
		QualitySettings.renderPipeline = transparentRenderPipelineAsset;
		captureCamera.clearFlags = CameraClearFlags.Color;
		captureCamera.backgroundColor = new Color(0f, 0f, 0f, 0f);
		if (textureObjectType == TextureObjectType.Achievements)
		{
			width = 256;
			height = 256;
		}
		RenderTexture renderTexture = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
		captureCamera.targetTexture = renderTexture;
		Vector3 position = captureCamera.transform.position;
		if (textureObjectType == TextureObjectType.Item)
		{
			ItemSO[] array = Resources.LoadAll<ItemSO>("Items/");
			foreach (ItemSO itemSO in array)
			{
				itemMeshFilter.mesh = itemSO.mesh;
				Texture2D[] array2 = new Texture2D[frameCount];
				for (int j = 0; j < frameCount; j++)
				{
					itemTransform.localRotation = Quaternion.Euler(0f, 0f, (float)j * (360f / (float)frameCount) + 135f);
					captureCamera.Render();
					RenderTexture.active = renderTexture;
					Texture2D texture2D = new Texture2D(width, height, TextureFormat.RGBA32, mipChain: false);
					texture2D.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
					texture2D.Apply();
					array2[j] = texture2D;
				}
				string text = Path.Combine(Application.dataPath, "Resources/ItemTextures");
				if (!Directory.Exists(text))
				{
					Directory.CreateDirectory(text);
				}
				string filePath = Path.Combine(text, itemSO.itemName + ".png");
				CreateTextureAtlas(array2, filePath);
			}
		}
		else if (textureObjectType == TextureObjectType.UnlockMeshes)
		{
			UnlockSO[] array3 = Resources.LoadAll<UnlockSO>("Unlocks/");
			foreach (UnlockSO unlockSO in array3)
			{
				if (!(unlockSO.mesh == null))
				{
					itemMeshFilter.mesh = unlockSO.mesh;
					float z = unlockSO.mesh.bounds.center.z;
					UnityEngine.Debug.Log(unlockSO.mesh.bounds.extents.magnitude);
					captureCamera.orthographicSize = 0.5f + cameraSizeBoundsScale * (unlockSO.mesh.bounds.extents.magnitude - defaultObjectBoundsMagnitude);
					captureCamera.transform.position = position + new Vector3(0f, 0f, z);
					Texture2D[] array4 = new Texture2D[frameCount];
					for (int k = 0; k < frameCount; k++)
					{
						itemTransform.localRotation = Quaternion.Euler(0f, 0f, (float)k * (360f / (float)frameCount) + 160f);
						captureCamera.Render();
						RenderTexture.active = renderTexture;
						Texture2D texture2D2 = new Texture2D(width, height, TextureFormat.RGBA32, mipChain: false);
						texture2D2.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
						texture2D2.Apply();
						array4[k] = texture2D2;
					}
					string text2 = Path.Combine(Application.dataPath, "Resources/UnlockTextures");
					if (!Directory.Exists(text2))
					{
						Directory.CreateDirectory(text2);
					}
					string filePath2 = Path.Combine(text2, unlockSO.unlockName + ".png");
					CreateTextureAtlas(array4, filePath2);
				}
			}
		}
		else if (textureObjectType == TextureObjectType.Achievements)
		{
			RenderTexture renderTexture2 = new RenderTexture(width, height, 24, RenderTextureFormat.ARGB32);
			uiCamera.targetTexture = renderTexture2;
			AchievementSO[] array5 = Resources.LoadAll<AchievementSO>("Achievements/");
			foreach (AchievementSO achievementSO in array5)
			{
				itemTransform.localRotation = Quaternion.Euler(0f, 0f, 160f);
				itemMeshFilter.mesh = achievementSO.mesh;
				iconText.text = achievementSO.iconText;
				float z2 = achievementSO.mesh.bounds.center.z;
				captureCamera.orthographicSize = 0.5f + cameraSizeBoundsScale * (achievementSO.mesh.bounds.extents.magnitude - defaultObjectBoundsMagnitude);
				captureCamera.transform.position = position + new Vector3(0f, 0f, z2);
				captureCamera.Render();
				RenderTexture.active = renderTexture;
				Texture2D texture2D3 = new Texture2D(width, height, TextureFormat.RGBA32, mipChain: false);
				texture2D3.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
				texture2D3.Apply();
				uiCamera.Render();
				RenderTexture.active = renderTexture2;
				Texture2D texture2D4 = new Texture2D(width, height, TextureFormat.RGBA32, mipChain: false);
				texture2D4.ReadPixels(new Rect(0f, 0f, width, height), 0, 0);
				texture2D4.Apply();
				string text3 = Path.Combine(Application.dataPath, "../../AchievementIcons");
				if (!Directory.Exists(text3))
				{
					Directory.CreateDirectory(text3);
				}
				string filePath3 = Path.Combine(text3, achievementSO.name + ".png");
				string grayFilePath = Path.Combine(text3, achievementSO.name + "_gray.png");
				SaveAchievementTexture(texture2D3, texture2D4, filePath3, grayFilePath);
			}
		}
		captureCamera.targetTexture = null;
		RenderTexture.active = null;
		UnityEngine.Object.Destroy(renderTexture);
	}

	private void SaveAchievementTexture(Texture2D texture, Texture2D UItexture, string filePath, string grayFilePath)
	{
		Color[] pixels = texture.GetPixels();
		Color[] glowPixels = GetGlowPixels(texture, pixels);
		Color[] underlayPixels = GetUnderlayPixels(texture);
		Color[] backgroundPixels = GetBackgroundPixels(texture, achievementBackgroundColor);
		Color[] borderPixels = GetBorderPixels(texture, borderColor);
		Color[] pixels2 = UItexture.GetPixels();
		Color[] pixels3 = new Color[pixels.Length];
		OverlayPixels(pixels3, backgroundPixels);
		OverlayPixels(pixels3, borderPixels);
		OverlayPixels(pixels3, underlayPixels);
		OverlayPixels(pixels3, glowPixels);
		OverlayPixels(pixels3, pixels);
		OverlayPixels(pixels3, pixels2);
		texture.SetPixels(pixels3);
		File.WriteAllBytes(filePath, texture.EncodeToPNG());
		backgroundPixels = GetBackgroundPixels(texture, achievementBackgroundColor);
		borderPixels = GetBorderPixels(texture, borderGrayColor);
		pixels3 = new Color[pixels.Length];
		OverlayPixels(pixels3, backgroundPixels);
		OverlayPixels(pixels3, borderPixels);
		OverlayPixels(pixels3, underlayPixels);
		OverlayPixels(pixels3, pixels);
		OverlayPixels(pixels3, pixels2);
		for (int i = 0; i < pixels3.Length; i++)
		{
			Color color = pixels3[i];
			float grayscale = color.grayscale;
			pixels3[i] = new Color(grayscale, grayscale, grayscale, color.a);
		}
		texture.SetPixels(pixels3);
		File.WriteAllBytes(grayFilePath, texture.EncodeToPNG());
	}

	private void CreateTextureAtlas(Texture2D[] textures, string filePath)
	{
		for (int i = 0; i < textures.Length; i++)
		{
			switch (outlineType)
			{
			case OutlineType.Outline:
			{
				Color[] pixels2 = textures[i].GetPixels();
				Color[] outlinePixels = GetOutlinePixels(textures[i]);
				OverlayPixels(pixels2, outlinePixels);
				textures[i].SetPixels(pixels2);
				break;
			}
			case OutlineType.Underlay:
			{
				Color[] underlayPixels = GetUnderlayPixels(textures[i]);
				Color[] pixels = new Color[textures[i].width * textures[i].height];
				OverlayPixels(pixels, underlayPixels);
				OverlayPixels(pixels, textures[i].GetPixels());
				textures[i].SetPixels(pixels);
				break;
			}
			}
		}
		Texture2D texture2D = new Texture2D(width * textures.Length, height);
		for (int j = 0; j < textures.Length; j++)
		{
			texture2D.SetPixels(j * width, 0, width, height, textures[j].GetPixels());
		}
		texture2D.Apply();
		File.WriteAllBytes(filePath, texture2D.EncodeToPNG());
	}

	private Color[] GetOutlinePixels(Texture2D texture)
	{
		Color[] pixels = texture.GetPixels();
		Color[] array = new Color[pixels.Length];
		for (int i = 0; i < texture.height; i++)
		{
			for (int j = 0; j < texture.width; j++)
			{
				if (!(pixels[i * texture.width + j].a < 1f))
				{
					continue;
				}
				for (int k = -outlineThickness; k <= outlineThickness; k++)
				{
					for (int l = -outlineThickness; l <= outlineThickness; l++)
					{
						if (l != 0 || k != 0)
						{
							int num = j + l;
							int num2 = i + k;
							if (num >= 0 && num < texture.width && num2 >= 0 && num2 < texture.height && pixels[num2 * texture.width + num].a == 1f)
							{
								array[i * texture.width + j] = outlineColor;
							}
						}
					}
				}
			}
		}
		return array;
	}

	private Color[] GetUnderlayPixels(Texture2D texture)
	{
		Color[] pixels = texture.GetPixels();
		Color[] array = new Color[pixels.Length];
		for (int i = 0; i < texture.height; i++)
		{
			for (int j = 0; j < texture.width; j++)
			{
				Color color = pixels[i * texture.width + j];
				if (!(color.a > 0f))
				{
					continue;
				}
				int num = j + (int)underlayOffset.x;
				int num2 = i + (int)underlayOffset.y;
				if (num >= 0 && num < texture.width && num2 >= 0 && num2 < texture.height)
				{
					Color b = pixels[num2 * texture.width + num];
					if (b.a != 1f)
					{
						float t = Mathf.Clamp01(b.a);
						b.a = 1f;
						Color color2 = Color.Lerp(outlineColor, b, t);
						color2.a *= color.a;
						array[num2 * texture.width + num] = color2;
					}
				}
			}
		}
		return array;
	}

	private Color[] GetGlowPixels(Texture2D texture, Color[] originalPixels)
	{
		Color[] array = new Color[originalPixels.Length];
		int num = 0;
		for (int i = 0; i < originalPixels.Length; i++)
		{
			Color color = originalPixels[i];
			array[i] = new Color(glowColor.r, glowColor.g, glowColor.b, color.a);
			if (color.a > 0f)
			{
				num++;
			}
		}
		for (int j = 0; j < array.Length; j++)
		{
			float f = (float)num / (float)array.Length;
			Color color2 = array[j];
			color2.a *= glowFactor * 1f / Mathf.Pow(f, glowExponent);
			array[j] = color2;
		}
		return BlurTexture(array, texture.width, texture.height, glowThickness);
	}

	private Color[] BlurTexture(Color[] pixels, int width, int height, int blurRadius)
	{
		Color[] array = new Color[pixels.Length];
		float num = (float)blurRadius / 3f;
		float[] array2 = new float[blurRadius * 2 + 1];
		float num2 = 0f;
		for (int i = 0; i < array2.Length; i++)
		{
			int num3 = i - blurRadius;
			array2[i] = Mathf.Exp((float)(-(num3 * num3)) / (2f * num * num));
			num2 += array2[i];
		}
		for (int j = 0; j < array2.Length; j++)
		{
			array2[j] /= num2;
		}
		Color[] array3 = new Color[pixels.Length];
		for (int k = 0; k < height; k++)
		{
			for (int l = 0; l < width; l++)
			{
				float num4 = 0f;
				float num5 = 0f;
				float num6 = 0f;
				float num7 = 0f;
				for (int m = -blurRadius; m <= blurRadius; m++)
				{
					int num8 = Mathf.Clamp(l + m, 0, width - 1);
					Color color = pixels[k * width + num8];
					float num9 = array2[m + blurRadius];
					num4 += color.r * num9;
					num5 += color.g * num9;
					num6 += color.b * num9;
					num7 += color.a * num9;
				}
				array3[k * width + l] = new Color(num4, num5, num6, num7);
			}
		}
		for (int n = 0; n < height; n++)
		{
			for (int num10 = 0; num10 < width; num10++)
			{
				float num11 = 0f;
				float num12 = 0f;
				float num13 = 0f;
				float num14 = 0f;
				for (int num15 = -blurRadius; num15 <= blurRadius; num15++)
				{
					int num16 = Mathf.Clamp(n + num15, 0, height - 1);
					Color color2 = array3[num16 * width + num10];
					float num17 = array2[num15 + blurRadius];
					num11 += color2.r * num17;
					num12 += color2.g * num17;
					num13 += color2.b * num17;
					num14 += color2.a * num17;
				}
				array[n * width + num10] = new Color(num11, num12, num13, num14);
			}
		}
		return array;
	}

	private Color[] GetBackgroundPixels(Texture2D texture, Color backgroundColor)
	{
		Color[] array = new Color[texture.width * texture.height];
		for (int i = 0; i < array.Length; i++)
		{
			Color color = array[i];
			float num = 1f - color.a;
			float a = color.a;
			array[i] = new Color(a * color.r + backgroundColor.r * num, a * color.g + backgroundColor.g * num, a * color.b + backgroundColor.b * num, Mathf.Clamp01(a + backgroundColor.a * num));
		}
		return array;
	}

	private Color[] GetBorderPixels(Texture2D texture, Color borderColor)
	{
		Color[] array = new Color[texture.width * texture.height];
		for (int i = 0; i < texture.height; i++)
		{
			for (int j = 0; j < texture.width; j++)
			{
				if (j < borderThickness || j >= texture.width - borderThickness || i < borderThickness || i >= texture.height - borderThickness)
				{
					array[i * texture.width + j] = borderColor;
				}
			}
		}
		return array;
	}

	private void OverlayPixels(Color[] pixels, Color[] pixelsToOverlay)
	{
		for (int i = 0; i < pixels.Length; i++)
		{
			pixels[i] = Color.Lerp(pixels[i], pixelsToOverlay[i], pixelsToOverlay[i].a);
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
			FilePathsData = new byte[127]
			{
				0, 0, 0, 1, 0, 0, 0, 53, 92, 65,
				115, 115, 101, 116, 115, 92, 77, 105, 115, 99,
				92, 83, 99, 101, 110, 101, 115, 92, 73, 116,
				101, 109, 67, 97, 112, 116, 117, 114, 101, 83,
				99, 101, 110, 101, 92, 65, 99, 104, 105, 101,
				118, 101, 109, 101, 110, 116, 83, 79, 46, 99,
				115, 0, 0, 0, 2, 0, 0, 0, 58, 92,
				65, 115, 115, 101, 116, 115, 92, 77, 105, 115,
				99, 92, 83, 99, 101, 110, 101, 115, 92, 73,
				116, 101, 109, 67, 97, 112, 116, 117, 114, 101,
				83, 99, 101, 110, 101, 92, 67, 114, 101, 97,
				116, 101, 73, 116, 101, 109, 84, 101, 120, 116,
				117, 114, 101, 115, 46, 99, 115
			},
			TypesData = new byte[79]
			{
				0, 0, 0, 0, 14, 124, 65, 99, 104, 105,
				101, 118, 101, 109, 101, 110, 116, 83, 79, 0,
				0, 0, 0, 19, 124, 67, 114, 101, 97, 116,
				101, 73, 116, 101, 109, 84, 101, 120, 116, 117,
				114, 101, 115, 0, 0, 0, 0, 31, 67, 114,
				101, 97, 116, 101, 73, 116, 101, 109, 84, 101,
				120, 116, 117, 114, 101, 115, 124, 78, 97, 109,
				101, 77, 101, 115, 104, 80, 97, 105, 114
			},
			TotalFiles = 2,
			TotalTypes = 3,
			IsEditorOnly = false
		};
	}
}
