---
summary: API と DB のスキーマは 1 か所で定義し、コードは生成ツールで作って二重管理しない
stance: adopt
tags: [principles, architecture]
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# スキーマを二重管理しない

## 概要

API のスキーマと DB のスキーマは、それぞれ 1 か所だけで定義します。型やクライアントのコードは、その定義から生成します。

## 方針

同じ知識が複数の場所にあると修正漏れが起きるため adopt とします。

- API は OpenAPI や GraphQL のスキーマを正とし(Schema First)、サーバとクライアントのコードを生成する。
- DB はマイグレーションや SQL を正とし、アクセス用のコードを生成する。
- フレームワークの仕組みでスキーマを一元管理できる言語では、それに任せる(Code First)。
- 生成したコードは手で編集しない。

## 解説

スキーマの知識がコードとドキュメント、あるいはサーバとクライアントに分かれていると、片方だけを直す事故が起きます。DRY 原則を、コードだけでなくスキーマにも当てはめる考え方です。

Go では次のツールが使えます。

| 対象 | ツール |
| --- | --- |
| REST API(OpenAPI) | oapi-codegen |
| GraphQL | gqlgen |
| DB | sqlc、SQLBoiler |

## トレードオフ

### 得られるもの

- スキーマの変更が型エラーとして利用箇所まで伝わる。
- 修正漏れによる不具合が減る。

### 失われるもの

- 生成ツールの制約(対応していない構文、生成コードの形)に縛られる。
- ビルド手順に生成の工程が増える。

## 採用すべき？

### 採用すべきケース

- API のサーバとクライアントを別々に実装している。
- DB のテーブルが多く、手書きのマッピングが負担になっている。

### 採用すべきでないケース

- 使い捨てのプロトタイプなど、スキーマがすぐに変わり、生成の仕組みを整えるほうが高くつく。

## 参考情報

- [oapi-codegen](https://github.com/oapi-codegen/oapi-codegen)
- [gqlgen](https://gqlgen.com/)
- [sqlc](https://sqlc.dev/)
- [SQLBoiler](https://github.com/volatiletech/sqlboiler)
- 『達人プログラマー 職人から名匠への道』(第 20 章 コードジェネレータ。第 2 版では削除)
- [開発効率を追い求めた実装プラクティス集](https://zenn.dev/micin/articles/effective-development-practices)

## 履歴

- 2026-11-03: 新規作成。
