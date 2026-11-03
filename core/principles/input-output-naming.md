---
summary: ドメインロジックの関数の入出力型には Input/Output 接尾辞を付け、関数名・引数名と形を揃える
stance: adopt
tags: [principles, ai-coding]
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# Input/Output の命名

## 概要

ドメインロジックを書く関数では、入力の型と出力の型に `Input` / `Output` の接尾辞を付けます。関数名、型名、引数名を一定の形に揃えます。

## 方針

命名の規則が一定だと、人間も AI も次に書くコードを推測しやすいため adopt とします。

- 関数 `XxxYyy` の入力型は `XxxYyyInput`、出力型は `XxxYyyOutput` にする。
- 引数名は `input`、戻り値の変数名は `output` に揃える。
- 適用するのは、[データとコードの分離](data-code-separation.md) で書くドメインロジックの関数とする。

```go
type UpdateUserNameInput struct {
	User    User
	NewName string
}

type UpdateUserNameOutput struct {
	User User
}

func UpdateUserName(input UpdateUserNameInput) (UpdateUserNameOutput, error)
```

## 解説

ドメインロジックの関数は数が多くなります。型名と関数名の対応が決まっていれば、関数を 1 つ書いた時点で、AI が残りの型や呼び出し側のコードを正しく補完しやすくなります。人間にとっても型名から関数を探せます。

## トレードオフ

### 得られるもの

- 型と関数の対応が名前から分かる。
- AI の補完が規則に沿いやすい。

### 失われるもの

- 入出力が 1 値だけの単純な関数でも、型を定義する手間がかかる。
- 型名が長くなる。

## 採用すべき？

### 採用すべきケース

- ドメインロジックの関数が多く、入出力に複数の値を持つ。

### 採用すべきでないケース

- ユーティリティ関数など、ドメインロジック以外の関数。

## 参考情報

- [開発効率を追い求めた実装プラクティス集](https://zenn.dev/micin/articles/effective-development-practices)

## 履歴

- 2026-11-03: 新規作成。
