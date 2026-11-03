---
summary: テストは Given(準備)・When(実行)・Then(確認)の 3 つに分けて書く
stance: adopt
tags: [testing]
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# Given-When-Then

## 概要

1 つのテストを、Given(準備)、When(実行)、Then(確認)の 3 つの部分に分けて書きます。Arrange-Act-Assert(AAA)と同じ考え方です。

## 方針

テストの構造が一定になり、複雑になりにくいため adopt とします。

- テストの本文を Given / When / Then の順に並べ、それぞれの始まりにコメントで区切りを書く。
- When で実行するのは、テスト対象の呼び出し 1 回だけにする。
- 検証は Then にまとめる。Given の中で検証の内容を書かない。

```go
func TestService_UpdateUserName(t *testing.T) {
	// Given
	repo := &RepositoryMock{ /* スタブの定義 */ }
	svc := NewService(repo)

	// When
	err := svc.UpdateUserName(ctx, userID, "new name")

	// Then
	require.NoError(t, err)
	assert.Len(t, repo.UpdateUserCalls(), 1)
}
```

## 解説

3 つの部分が混ざると、何を準備して何を確かめているのかが読み取りにくくなります。とくに、モックへの期待値を Given で設定する書き方では、検証の内容が準備の中に入り込み、構造が崩れます。

Given-When-Then は BDD や Spock で使われる呼び方で、AAA と意味は同じです。

## トレードオフ

### 得られるもの

- どのテストも同じ形で読める。
- 1 つのテストで複数の振る舞いを確かめる書き方を避けられる。

### 失われるもの

- テーブル駆動テストのように、入力と期待値を表にまとめる書き方とは相性がよくない。

## 採用すべき？

### 採用すべきケース

- 常に採用する。

### 採用すべきでないケース

- 入出力の組み合わせだけを大量に確かめる純粋関数のテストでは、テーブル駆動テストのほうが簡潔な場合がある。

## 参考情報

- [GivenWhenThen - Martin Fowler](https://martinfowler.com/bliki/GivenWhenThen.html)
- [Spock Framework](https://spockframework.org/)
- 『単体テストの考え方/使い方』Vladimir Khorikov 著(第 3 章 AAA パターン)
- [moqを使ったGoのテスト](https://zenn.dev/abekoh/articles/21acde07e1f555)

## 履歴

- 2026-11-03: 新規作成。
