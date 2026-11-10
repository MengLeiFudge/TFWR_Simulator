"""只读导出原版资源供C#宿主使用；不读取或修改Save0。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
from UnityPy.helpers.TypeTreeNode import TypeTreeNode
from UnityPy.classes import PPtr

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'game_control' / 'src'))
from tfwr_orchestrator.config import resolve_game_root


def fix(node):
    kind = 'vector' if node.m_Name in {'placeableOn', 'unlocks', 'whitelistedGroundFeatureUnlocks'} else node.m_Type
    return TypeTreeNode(node.m_Level, kind, node.m_Name, node.m_ByteSize, node.m_Version,
                        [fix(c) for c in node.m_Children], m_TypeFlags=node.m_TypeFlags,
                        m_VariableCount=node.m_VariableCount, m_Index=node.m_Index,
                        m_MetaFlag=node.m_MetaFlag, m_RefTypeHash=node.m_RefTypeHash)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    game = resolve_game_root()
    data = game / 'TheFarmerWasReplaced_Data'
    assemblies = {name: hashlib.sha256((data / 'Managed' / name).read_bytes()).hexdigest()
                  for name in ('Core.dll', 'Utils.dll')}
    expected = {'Core.dll': 'f0efda7c138de8028b1769c121a4b5c17b6bb538aeae5a67d1881e7c4ebd7d25',
                'Utils.dll': '1939c19ce4bca3ffa570a2db0f80f3117e6eba7a2a8f706c8aec2d0ed0edaf1d'}
    if assemblies != expected:
        raise ValueError('Game assemblies changed; update and validate native source before exporting resources')
    paths = [data / n for n in ('resources.assets', 'globalgamemanagers.assets', 'sharedassets0.assets', 'level0')]
    env = UnityPy.load(*(str(p) for p in paths))
    gen = TypeTreeGenerator(next(iter(env.files.values())).unity_version)
    gen.load_local_game(str(game))
    env.typetree_generator = gen
    rows = []
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        head = obj.parse_monobehaviour_head()
        script = head.m_Script.read()
        kind = script.m_ClassName
        if not (kind.endswith('Feature') or kind in {'ItemSO','EntitySO','GroundSO','MushroomGroundSO','HatSO','DroneSO','UnlockSO','LeaderboardSO','DesignConstants'}):
            continue
        fields = obj.parse_as_dict(node=fix(obj.generate_monobehaviour_node()), check_read=False)
        def refs(value):
            if isinstance(value, dict):
                if set(value) == {'m_FileID', 'm_PathID'}:
                    if value['m_PathID'] == 0:
                        return None
                    ptr = PPtr(**value, assetsfile=obj.assets_file).deref()
                    return {'ref': f'{ptr.assets_file.name}:{ptr.path_id}'}
                return {k: refs(v) for k, v in value.items() if not k.startswith('m_Script') and k != 'm_GameObject'}
            if isinstance(value, list):
                return [refs(v) for v in value]
            return value
        rows.append({'id': f'{obj.assets_file.name}:{obj.path_id}', 'type': kind, 'name': head.m_Name, 'fields': refs(fields)})
    payload = {'source_assemblies': assemblies, 'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}, 'objects': rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'Exported {len(rows)} objects to {args.output}', flush=True)

if __name__ == '__main__':
    main()
