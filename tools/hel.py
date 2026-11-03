# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6"]
# ///
"""harness-elements の検査と索引生成を行う。

使い方:
    uv run tools/hel.py check   # 検査。問題があれば終了コード 1
    uv run tools/hel.py index   # 各レイヤー README.md の索引を書き換える
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

STANCES = ["required", "recommended", "adopt", "trial", "assess", "hold", "forbidden"]
INHERITS = ["replace", "extend"]
SECTIONS = ["概要", "方針", "解説", "トレードオフ", "採用すべき？", "参考情報", "履歴"]
MAINTENANCE = "メンテナンス状況"

REQUIRED_KEYS = {"summary", "stance", "tags", "created", "updated", "models"}
OPTIONAL_KEYS = {"inherit", "depends_on", "version", "verified_at"}

INDEX_START = "<!-- index:start -->"
INDEX_END = "<!-- index:end -->"

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:/[a-z0-9]+(?:-[a-z0-9]+)*)*$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)


@dataclass
class Layer:
    name: str
    path: Path
    extends: str | None
    tags: dict[str, str] = field(default_factory=dict)
    materials: dict[str, "Material"] = field(default_factory=dict)


@dataclass
class Material:
    layer: str
    id: str
    path: Path
    meta: dict
    body: str


class Errors:
    def __init__(self) -> None:
        self.items: list[str] = []

    def add(self, path: Path | str, msg: str) -> None:
        rel = path.relative_to(ROOT) if isinstance(path, Path) else path
        self.items.append(f"{rel}: {msg}")


def split_frontmatter(text: str) -> tuple[dict | None, str]:
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, text
    meta = yaml.safe_load(text[4:end]) or {}
    return meta, text[end + 5 :]


def as_date(value) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return None
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def is_attachment(rel: Path, layer_path: Path) -> bool:
    """素材と同名のディレクトリ配下(付属物)にあるか。"""
    for parent in rel.parents:
        if parent == Path("."):
            break
        if (layer_path / parent.with_suffix(".md")).is_file():
            return True
    return False


def load_layers(errors: Errors) -> dict[str, Layer]:
    layers: dict[str, Layer] = {}
    for d in sorted(ROOT.iterdir()):
        readme = d / "README.md"
        if not d.is_dir() or d.name.startswith(".") or not readme.is_file():
            continue
        meta, _ = split_frontmatter(readme.read_text(encoding="utf-8"))
        if meta is None or "extends" not in meta:
            continue
        layer = Layer(name=d.name, path=d, extends=meta["extends"])
        tags_file = d / "tags.yaml"
        if tags_file.is_file():
            tags = yaml.safe_load(tags_file.read_text(encoding="utf-8")) or {}
            if not isinstance(tags, dict):
                errors.add(tags_file, "タグ名から説明への対応表にしてください")
            else:
                layer.tags = {str(k): str(v) for k, v in tags.items()}
        layers[d.name] = layer
    return layers


def chain(layers: dict[str, Layer], name: str) -> list[Layer]:
    """自身から上位へ向かうレイヤー列。循環や欠落があれば途中で止まる。"""
    result: list[Layer] = []
    seen: set[str] = set()
    current: str | None = name
    while current is not None and current in layers and current not in seen:
        seen.add(current)
        result.append(layers[current])
        current = layers[current].extends
    return result


def check_layers(layers: dict[str, Layer], errors: Errors) -> None:
    if "core" not in layers:
        errors.add("core/README.md", "core レイヤーがありません")
    for layer in layers.values():
        readme = layer.path / "README.md"
        if layer.name == "core":
            if layer.extends is not None:
                errors.add(readme, "core は extends: null にしてください")
            continue
        if layer.extends is None:
            errors.add(readme, "extends に親レイヤーを指定してください")
            continue
        if layer.extends not in layers:
            errors.add(readme, f"extends の親レイヤー '{layer.extends}' がありません")
            continue
        names = [l.name for l in chain(layers, layer.name)]
        if names[-1] != "core":
            errors.add(readme, f"レイヤーの継承が core に到達しません: {' -> '.join(names)}")


def load_materials(layers: dict[str, Layer], errors: Errors) -> None:
    for layer in layers.values():
        for path in sorted(layer.path.rglob("*.md")):
            rel = path.relative_to(layer.path)
            if rel == Path("README.md") or is_attachment(rel, layer.path):
                continue
            mid = rel.with_suffix("").as_posix()
            if not ID_RE.match(mid):
                errors.add(path, "パスは英小文字・数字の kebab-case にしてください")
            try:
                meta, body = split_frontmatter(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                errors.add(path, f"frontmatter を解釈できません: {e}")
                continue
            if meta is None:
                errors.add(path, "frontmatter がありません")
                continue
            layer.materials[mid] = Material(layer.name, mid, path, meta, body)


def check_frontmatter(m: Material, layers: dict[str, Layer], errors: Errors) -> None:
    meta = m.meta
    for key in sorted(REQUIRED_KEYS - meta.keys()):
        errors.add(m.path, f"frontmatter に {key} がありません")
    for key in sorted(meta.keys() - REQUIRED_KEYS - OPTIONAL_KEYS):
        errors.add(m.path, f"frontmatter に未定義の項目 {key} があります")

    if "summary" in meta and (not isinstance(meta["summary"], str) or not meta["summary"].strip()):
        errors.add(m.path, "summary は空でない文字列にしてください")
    if "stance" in meta and meta["stance"] not in STANCES:
        errors.add(m.path, f"stance は {' / '.join(STANCES)} のいずれかにしてください")

    inherit = meta.get("inherit", "replace")
    if inherit not in INHERITS:
        errors.add(m.path, f"inherit は {' / '.join(INHERITS)} のいずれかにしてください")
    if m.layer == "core" and "inherit" in meta:
        errors.add(m.path, "core の素材には inherit を書けません")
    if inherit == "extend" and m.layer != "core":
        parents = chain(layers, m.layer)[1:]
        if not any(m.id in l.materials for l in parents):
            errors.add(m.path, "inherit: extend ですが、上位レイヤーに同じ ID の素材がありません")

    tags = meta.get("tags")
    if "tags" in meta:
        if not isinstance(tags, list) or not tags or not all(isinstance(t, str) for t in tags):
            errors.add(m.path, "tags は 1 つ以上の文字列のリストにしてください")
        else:
            allowed = set().union(*(l.tags.keys() for l in chain(layers, m.layer)))
            for t in tags:
                if t not in allowed:
                    errors.add(m.path, f"タグ '{t}' が tags.yaml に登録されていません")

    models = meta.get("models")
    if "models" in meta and (
        not isinstance(models, list) or not models or not all(isinstance(x, str) for x in models)
    ):
        errors.add(m.path, "models は 1 つ以上の文字列のリストにしてください")

    dates = {}
    for key in ("created", "updated", "verified_at"):
        if key in meta:
            d = as_date(meta[key])
            if d is None:
                errors.add(m.path, f"{key} は YYYY-MM-DD 形式の日付にしてください")
            dates[key] = d
    if dates.get("created") and dates.get("updated") and dates["updated"] < dates["created"]:
        errors.add(m.path, "updated が created より前になっています")
    if "version" in meta:
        if not isinstance(meta["version"], str):
            errors.add(m.path, 'version は文字列にしてください(例: "1.25")')
        if "verified_at" not in meta:
            errors.add(m.path, "version を書く場合は verified_at も必要です")
    elif "verified_at" in meta:
        errors.add(m.path, "verified_at は version とセットで書いてください")

    deps = meta.get("depends_on", [])
    if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps):
        errors.add(m.path, "depends_on は論理 ID のリストにしてください")
    else:
        visible = set().union(*(l.materials.keys() for l in chain(layers, m.layer)))
        for dep in deps:
            if dep == m.id:
                errors.add(m.path, "depends_on に自分自身が含まれています")
            elif dep not in visible:
                errors.add(m.path, f"depends_on の '{dep}' がこのレイヤーから解決できません")


def check_sections(m: Material, errors: Errors) -> None:
    body = FENCE_RE.sub("", m.body)
    h1 = re.findall(r"^# (.+)$", body, re.M)
    if len(h1) != 1:
        errors.add(m.path, "H1 見出しはちょうど 1 つにしてください")
    if m.meta.get("inherit") == "extend":
        return
    h2 = [s.strip() for s in re.findall(r"^## (.+)$", body, re.M)]
    if h2 != SECTIONS:
        errors.add(
            m.path,
            f"H2 見出しは {' / '.join(SECTIONS)} の順にしてください(現在: {' / '.join(h2) or 'なし'})",
        )
    if "version" in m.meta:
        match = re.search(r"^## 解説$(.*?)(?=^## |\Z)", body, re.M | re.S)
        if not match or not re.search(rf"^### {MAINTENANCE}$", match.group(1), re.M):
            errors.add(m.path, f"version を書く素材は、解説節に H3「{MAINTENANCE}」を置いてください")


def check_links(path: Path, errors: Errors) -> None:
    text = FENCE_RE.sub("", path.read_text(encoding="utf-8"))
    text = re.sub(r"`[^`\n]*`", "", text)
    for target in LINK_RE.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        file_part = target.split("#", 1)[0]
        resolved = (path.parent / file_part).resolve()
        if not resolved.exists():
            errors.add(path, f"リンク切れ: {target}")


def render_index(layer: Layer) -> str:
    if not layer.materials:
        return "素材はまだありません。"
    lines = ["| 素材 | stance | 要約 |", "| --- | --- | --- |"]
    for mid, m in sorted(layer.materials.items()):
        rel = m.path.relative_to(layer.path).as_posix()
        mark = "(extend)" if m.meta.get("inherit") == "extend" else ""
        summary = str(m.meta.get("summary", "")).replace("|", "\\|").strip()
        lines.append(f"| [{mid}]({rel}){mark} | {m.meta.get('stance', '')} | {summary} |")
    return "\n".join(lines)


def replace_index(text: str, index: str) -> str | None:
    start = text.find(INDEX_START)
    end = text.find(INDEX_END)
    if start == -1 or end == -1 or end < start:
        return None
    return text[: start + len(INDEX_START)] + "\n\n" + index + "\n\n" + text[end:]


def load_all(errors: Errors) -> dict[str, Layer]:
    layers = load_layers(errors)
    check_layers(layers, errors)
    load_materials(layers, errors)
    return layers


def cmd_check() -> int:
    errors = Errors()
    layers = load_all(errors)
    for layer in layers.values():
        for m in layer.materials.values():
            check_frontmatter(m, layers, errors)
            check_sections(m, errors)
        for path in sorted(layer.path.rglob("*.md")):
            check_links(path, errors)
        readme = layer.path / "README.md"
        text = readme.read_text(encoding="utf-8")
        expected = replace_index(text, render_index(layer))
        if expected is None:
            errors.add(readme, f"索引の目印 {INDEX_START} / {INDEX_END} がありません")
        elif expected != text:
            errors.add(readme, "索引が古くなっています。uv run tools/hel.py index を実行してください")
    root_readme = ROOT / "README.md"
    if root_readme.is_file():
        check_links(root_readme, errors)

    for e in errors.items:
        print(f"ERROR {e}")
    count = sum(len(l.materials) for l in layers.values())
    print(f"{len(layers)} レイヤー、{count} 素材を検査しました。エラー {len(errors.items)} 件")
    return 1 if errors.items else 0


def cmd_index() -> int:
    errors = Errors()
    layers = load_all(errors)
    for layer in layers.values():
        readme = layer.path / "README.md"
        text = readme.read_text(encoding="utf-8")
        updated = replace_index(text, render_index(layer))
        if updated is None:
            errors.add(readme, f"索引の目印 {INDEX_START} / {INDEX_END} がありません")
            continue
        if updated != text:
            readme.write_text(updated, encoding="utf-8")
            print(f"更新: {readme.relative_to(ROOT)}")
    for e in errors.items:
        print(f"ERROR {e}")
    return 1 if errors.items else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["check", "index"])
    args = parser.parse_args()
    return cmd_check() if args.command == "check" else cmd_index()


if __name__ == "__main__":
    sys.exit(main())
