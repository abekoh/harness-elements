---
summary: ブログやドキュメントなど、コンテンツが中心の静的サイトは Astro で作り、frontmatter は Content Collections のスキーマで検証する
stance: adopt
tags: [library, frontend, typescript]
depends_on: []
version: "7.4"
verified_at: 2026-11-03
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# Astro

## 概要

Astro はブログ、ドキュメント、マーケティングサイトのような、コンテンツが中心の Web サイトを作るためのフレームワークです。

React や Vue で作ったサイトは、静的なページでもクライアント側で JavaScript を読み込んで描画するため、表示が遅くなりがちです。Hugo のような静的サイトジェネレータは速い一方で、独自のテンプレート言語を覚える必要があり、UI コンポーネントも再利用しにくくなります。Astro はページをビルド時に HTML として出力し、既定ではクライアント側に JavaScript を送りません。動きが必要な部分だけを React などのコンポーネントにします(アイランド)。テンプレートは JSX に近い `.astro` 形式で書けます。

## 方針

SSG に必要な機能とプラグインがそろっており、`.astro` も JSX に近い書き心地で扱いやすいため adopt とします。ただし、対象はコンテンツが中心の静的サイトに限ります。

- ブログ、ドキュメント、ポートフォリオなど、コンテンツが中心の静的サイトは Astro で作る。
- Markdown の記事は Content Collections で管理し、frontmatter のスキーマを `astro/zod` で定義する。frontmatter の誤りはビルドの時点で検出する([スキーマファースト](../../principles/schema-first.md)と同じ考え方)。
- 既定の出力は静的サイト(SSG)にする。サーバでの描画が必要なページだけを、アダプタを入れてオンデマンドで描画する。
- クライアント側の JavaScript は、操作が必要なコンポーネントにだけ `client:*` ディレクティブを付けて送る。
- 言語は TypeScript にする。
- 状態を多く持つ Web アプリケーション(管理画面、SaaS の画面など)には使わない。

## 解説

### 仕組み

Astro には次の特徴があります。

- **サーバファースト**: ページは、ビルド時(SSG)またはリクエスト時(オンデマンド描画)にサーバ側で HTML にします。
- **既定で JavaScript を送らない**: `.astro` コンポーネントは HTML と CSS だけを出力します。
- **アイランドアーキテクチャ**: React、Preact、Svelte、Vue、Solid などのコンポーネントをページに埋め込めます。`client:load`(読み込み時)、`client:idle`(ブラウザが空いたとき)、`client:visible`(画面に入ったとき)などのディレクティブを付けた部分だけが、クライアント側で動きます。
- **Vite ベース**: 開発サーバとビルドに Vite を使います。

### .astro ファイル

`---` で囲んだ部分(コンポーネントスクリプト)はビルド時やサーバ側で実行され、その下に JSX に近い記法でテンプレートを書きます。

```astro
---
import Layout from "../layouts/Layout.astro";
const { title } = Astro.props;
const items = ["a", "b"];
---
<Layout title={title}>
  <ul>
    {items.map((item) => <li>{item}</li>)}
  </ul>
</Layout>
```

JSX と違い、`class` 属性をそのまま書けます。`<style>` に書いた CSS は既定でそのコンポーネントだけに適用されます。

### Content Collections

Markdown、MDX、JSON、YAML などのコンテンツを、スキーマ付きのコレクションとして扱う機能です。`src/content.config.ts` で定義します。

```ts
import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const blog = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/blog" }),
  schema: z.object({
    title: z.string(),
    pubDate: z.coerce.date(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
  }),
});

export const collections = { blog };
```

- `loader` でデータの読み込み元を決めます。`glob()` はファイル群を、`file()` は 1 つのファイルを読みます。外部の CMS や API からは、自作またはコミュニティ製のローダーで読み込めます。
- `schema` から TypeScript の型が生成され、frontmatter がスキーマに合わないとビルドが失敗します。`reference()` で別のコレクションのエントリを参照できます。
- 取り出すときは `getCollection("blog")` や `getEntry("blog", id)` を使い、本文は `render(entry)` で HTML にします。`getCollection` の結果は順序が保証されないため、自分で並べ替えます。
- 実行時にデータを取得するライブコレクション(`src/live.config.ts`)もあります。オンデマンド描画用のアダプタが必要です。

### 導入

```sh
npm create astro@latest
npx astro add react      # UI フレームワークの統合を追加する
npx astro add cloudflare # オンデマンド描画用のアダプタを追加する
```

Node.js 22 以降が必要です。アダプタには Cloudflare、Netlify、Node、Vercel などがあります。

### 7 系での主な変更

7.0 では Vite 8 への移行、コンパイラの Go 製から Rust 製への置き換え、Markdown の既定の処理系の変更、`@astrojs/db` の削除などがありました。6 系以前の記事やサンプルを参考にするときは、この差に気をつけます。

### メンテナンス状況

| 項目 | 内容 |
| --- | --- |
| メンテナ | The Astro Technology Company(2026 年 1 月に Cloudflare が買収)とコミュニティ。MIT ライセンスのまま公開されている |
| GitHub スター数 | 63,684 |
| 最新コミット | 2026-11-02 |
| 最新リリース | astro@7.4.5(2026-11-02) |
| 確認日 | 2026-11-03 |

## トレードオフ

### 得られるもの

- JavaScript をほとんど送らない、表示の速いサイト。
- Content Collections による frontmatter の型付けとビルド時の検証。Git だけで記事を管理しても、CMS に近い安全性を得られる。
- React などの既存のコンポーネントを、必要な部分だけで使える。
- SSG まわりの統合やプラグインが多い。

### 失われるもの

- 状態を多く持つ画面には向かない。アイランドどうしで状態を共有するには、別の仕組みが要る。
- `.astro` は独自の形式のため、エディタの対応が React などほど安定していないことがある。
- メジャーバージョンごとに破壊的な変更が入り、追従の手間がかかる。
- 開発の主体が Cloudflare という 1 社になった。

## 採用すべき？

### 採用すべきケース

- ブログ、ドキュメント、ポートフォリオ、LP など、コンテンツが中心のサイトを作る。
- Markdown を Git で管理し、frontmatter の誤りをビルドで止めたい。

### 採用すべきでないケース

- ログイン後の画面など、状態を多く持つ Web アプリケーションを作る。
- ページの大半でクライアント側の操作が必要になる。

## 参考情報

- [Astro Docs](https://docs.astro.build/)
- [Content collections | Astro Docs](https://docs.astro.build/en/guides/content-collections/)
- [Why Astro? | Astro Docs](https://docs.astro.build/en/concepts/why-astro/)
- [withastro/astro](https://github.com/withastro/astro)
- [Astro, Tailwind CSS, Cloudflare Pagesでブログリニューアル](https://blog.abekoh.dev/posts/blog-v3)
- [abekoh/blog-v3](https://github.com/abekoh/blog-v3)

## 履歴

- 2026-11-03: 新規作成。
