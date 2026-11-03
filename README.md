# harness-elements

ハーネスエンジニアリングで使うハーネスの「素材」を集めたリポジトリです。言語、ライブラリ、ミドルウェア、設計原則、Lint、テスト指針、開発ツール、文書の書き方、AI エージェントの役割、開発プロセスなどを、1 要素につき 1 つの Markdown にまとめています。

ハーネスそのものは、ここにある素材を読んで別のリポジトリに組み立てます。

## レイヤー

| レイヤー | 継承元 | 内容 |
| --- | --- | --- |
| [core](core/README.md) | なし | 筆者(abekoh)の基本的な考え |

組織やチームで使うときは、このリポジトリを fork し、`core/` を継承するレイヤーを追加します。

```
core/        extends: null
banana/      extends: core     Banana 社の方針
banana-be/   extends: banana   Banana 社 Backend チームの方針
```

下位レイヤーに同じ ID の素材を置くと、上位レイヤーの素材を上書き(`inherit: replace`)または拡張(`inherit: extend`)できます。

## 素材の形式

各素材は、frontmatter(stance、タグ、依存など)と、次の節を持つ Markdown です。

概要 / 方針 / 解説 / トレードオフ / 採用すべき？ / 参考情報 / 履歴

stance は、そのレイヤーとしての採否の判断です。ThoughtWorks Technology Radar の ring に、組織の強制力を表す 2 値と、adopt から分けた `recommended` を加えた 7 値で、強い順に並べます。

| 値 | 意味 |
| --- | --- |
| `required` | 使用必須。組織やチームのルールとして必ず使う |
| `recommended` | 推奨。大半のプロジェクトで迷わず採用してよい |
| `adopt` | 採用。トレードオフを考慮したうえで採用してよい |
| `trial` | 試行。リスクを許容できるプロジェクトで試す |
| `assess` | 評価。調べる価値はあるが、まだ使わない |
| `hold` | 保留。新しくは採用しない。既存の利用は止めなくてよい |
| `forbidden` | 使用禁止。組織やチームのルールとして使わない |

詳しい規則は [CLAUDE.md](CLAUDE.md) にあります。

## 更新

素材の本文は AI が書き、すべての変更を Pull Request でレビューします。Claude Code では次のスキルを使います。

- `/ingest`: 新しい素材を追加する(人間が依頼する)
- `/refresh`: バージョンアップなどに合わせて既存素材を更新する
- `/lint`: 構造を検査し、ディレクトリの再配置を提案する

```sh
uv run tools/hel.py check   # 検査
```

各レイヤーの README.md の索引は、main に push されたあとに CI が生成してコミットします。PR では更新しません。
