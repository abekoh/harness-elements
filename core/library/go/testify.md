---
summary: Go のテストのアサーションには testify の assert / require を使う
stance: recommended
tags: [library, testing, go]
version: "1.12"
verified_at: 2026-11-03
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# testify

## 概要

testify は Go のテスト用のツールキットです。標準の `testing` パッケージには期待値と実際の値を比べるアサーションがないため、検証のたびに `if` 文と `t.Errorf` を書く必要があります。testify の `assert` と `require` のパッケージを使うと、等価性やエラーの有無などを 1 行で検証でき、失敗時には差分つきのメッセージが出ます。

## 方針

検証を短く読みやすく書けるため recommended とします。標準の `testing` パッケージだけで書く「Go らしさ」よりも、読みやすさを優先します。

- アサーションには testify を使う。
- 以降の検証が意味をなさなくなる前提条件(エラーが起きていないことなど)は `require` で書き、失敗したらその場でテストを止める。
- それ以外の検証は `assert` で書き、1 回の実行で失敗をまとめて確認できるようにする。
- testify の `mock` パッケージは使わない。テスト・ダブルは [moq](moq.md) で生成する。

```go
// Then
require.NoError(t, err)
assert.Len(t, repo.UpdateUserCalls(), 1)
assert.Equal(t, "new name", repo.UpdateUserCalls()[0].User.Name)
```

## 解説

### 仕組みと使い方

`go get github.com/stretchr/testify` で導入します。主なパッケージは次の 4 つです。

| パッケージ | 内容 |
| --- | --- |
| `assert` | 検証に失敗しても `t.Errorf` で記録し、テストを続ける。戻り値の bool で成否が分かる |
| `require` | `assert` と同じ関数を持ち、失敗すると `t.FailNow` でテストを止める |
| `mock` | 呼び出しを期待値として登録するモックの仕組み。この素材では使わない |
| `suite` | セットアップと後始末をまとめたテストスイートを書く仕組み |

標準の `testing` パッケージだけで書くと、`if got != want { t.Errorf(...) }` を検証のたびに書くことになります。`assert.Equal` などを使うと、この比較と失敗時のメッセージの出力を 1 行で書けます。

### メンテナンス状況

| 項目 | 内容 |
| --- | --- |
| メンテナ | stretchr(GitHub の Organization)。複数のメンテナが参加 |
| GitHub スター数 | 約 26,000 |
| 最新コミット | 2026-09-24 |
| 最新リリース | v1.12.1(2026-08-19) |
| 確認日 | 2026-11-03 |

## トレードオフ

### 得られるもの

- 検証が 1 行で書け、Then の部分が読みやすい。
- 失敗時に期待値と実際の値の差分が表示される。

### 失われるもの

- 外部ライブラリへの依存が増える。
- 標準ライブラリだけで書く Go の慣習から外れる。

## 採用すべき？

### 採用すべきケース

- Go でテストを書く。

### 採用すべきでないケース

- 外部依存を最小にしたいライブラリで、テストも標準ライブラリだけで書く方針がある。

## 参考情報

- [stretchr/testify](https://github.com/stretchr/testify)
- [testify - pkg.go.dev](https://pkg.go.dev/github.com/stretchr/testify)
- [moqを使ったGoのテスト](https://zenn.dev/abekoh/articles/21acde07e1f555)

## 履歴

- 2026-11-03: 新規作成。
