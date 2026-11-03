---
summary: Go のインタフェースから型安全なモック・スタブを生成し、呼び出し記録を Go の基本構文で検証する
stance: recommended
tags: [library, testing, go]
depends_on: [testing/mock-vs-stub, testing/mock-unmanaged-deps-only, testing/given-when-then]
version: "0.8"
verified_at: 2026-11-03
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# moq

## 概要

moq は、Go のインタフェース定義からテスト・ダブルの構造体を生成する CLI です。`go generate` から呼び出す前提で作られています。

Go で依存をテスト・ダブルに差し替えるには、インタフェースを実装した構造体を手で書く必要があり、メソッドが増えるほど手間がかかります。moq はこの構造体を自動で生成します。生成した構造体はメソッドごとに関数フィールドを持ち、テストの中でその関数を書くだけで振る舞いを決められます。呼び出しの記録も残るため、スタブとしてもモック(スパイ)としても使えます。

## 方針

型安全で、Given-When-Then の形を崩さずに書けるため recommended とします。

- Go のテスト・ダブルは moq で生成する。
- 使い方は [モックとスタブの使い分け](../../testing/mock-vs-stub.md) に従う。
  - スタブとしては `XxxFunc` に戻り値を定義するだけにし、受け取った引数は検証しない。
  - モックとしては管理外の依存への出力だけを `XxxCalls()` の記録で検証する([モックは管理外の依存にだけ使う](../../testing/mock-unmanaged-deps-only.md))。
- テストは [Given-When-Then](../../testing/given-when-then.md) で書き、検証には [testify](testify.md) を使う。
- モックを使うテストではテーブル駆動テストを使わない。

```sh
moq -out main_moq.go . ExternalAPIClient
```

## 解説

### 仕組み

moq は、指定したインタフェースのメソッドごとに次のものを持つ構造体(既定の名前は `インタフェース名Mock`)を生成します。

- `XxxFunc` フィールド: 元のメソッドと同じシグネチャの関数。メソッドを呼ぶと、この関数が実行される。
- `XxxCalls()` メソッド: 呼び出しの記録を、引数の型を保った構造体のスライスで返す。
- インタフェースを実装していることを確かめるコード(`var _ Xxx = &XxxMock{}`)。

このため、次の特徴があります。

- スタブを型安全に書け、エディタの補完も効く。
- 引数の検証も呼び出し回数(`len(mock.XxxCalls())`)も、Go の基本構文で書ける。
- `XxxFunc` を設定していないメソッドを呼ぶと panic する。使うメソッドだけを設定すればよい。

### 使い方

`go install github.com/matryer/moq@latest` で導入し、インタフェースを定義したファイルに `//go:generate` を書いて `go generate` を実行します。引数の 1 つ目はインタフェースを定義したディレクトリで、import パスではありません。

```go
//go:generate moq -out email_sender_moq_test.go . EmailSender

type EmailSender interface {
	Send(to, subject, body string) error
}
```

テストでは、使うメソッドの関数フィールドだけを設定し、呼び出しの記録で検証します。

```go
func TestCompleteSignUp(t *testing.T) {
	// Given
	sender := &EmailSenderMock{
		SendFunc: func(to, subject, body string) error { return nil },
	}

	// When
	err := CompleteSignUp("me@example.com", sender)

	// Then
	require.NoError(t, err)
	require.Len(t, sender.SendCalls(), 1)
	assert.Equal(t, "me@example.com", sender.SendCalls()[0].To)
}
```

主なオプションは次のとおりです。

| オプション | 内容 |
| --- | --- |
| `-out` | 出力先のファイル。省略すると標準出力に出す |
| `-pkg` | 生成するパッケージ名。省略すると推測する |
| `-stub` | 関数フィールドが未設定のとき、panic せずにゼロ値を返す |
| `-skip-ensure` | インタフェースの実装を確かめるコードを生成しない。テスト対象の外に生成して import が循環するときに使う |
| `-with-resets` | 呼び出しの記録を消す `ResetCalls()` などを生成する |
| `-rm` | 生成の前に出力先のファイルを消す |
| `-fmt` | 整形に使うツール(`gofmt` / `goimports` / `noop`) |

`Interface:Alias` の形で、生成する構造体の名前を変えられます。

### gomock との比較

gomock(現在は uber-go/mock)は、Matcher による柔軟な検証ができます。一方で、次の弱点があります。

- 引数が `any` になり、スタブを型安全に書けない。
- 期待する呼び出しを Given の段階で書くため、Given-When-Then の形が崩れる。

golang/mock はアーカイブされ、uber-go/mock に引き継がれました。ただし、gomock から moq への移行は、テストの書き方そのものが変わるため単純ではありません。

### メンテナンス状況

| 項目 | 内容 |
| --- | --- |
| メンテナ | Mat Ryer(個人のリポジトリ)。sudo-suhas ほかの貢献者が参加 |
| GitHub スター数 | 約 2,200 |
| 最新コミット | 2026-10-14 |
| 最新リリース | v0.8.1(2026-10-14) |
| 確認日 | 2026-11-03 |

## トレードオフ

### 得られるもの

- 型安全なスタブと、Go の基本構文で書ける検証。
- Given-When-Then の形を保ったテスト。

### 失われるもの

- gomock の Matcher のような、引数の柔軟な照合の仕組み。
- 呼び出し順序の検証などは自分で書く必要がある。

## 採用すべき？

### 採用すべきケース

- Go でテスト・ダブルを使い、モックとスタブの役割を分けて書きたい。

### 採用すべきでないケース

- gomock で書いた大量のテストがあり、書き方ごと移行するコストに見合わない。

## 参考情報

- [matryer/moq](https://github.com/matryer/moq)
- [uber-go/mock](https://github.com/uber-go/mock)
- [moqを使ったGoのテスト](https://zenn.dev/abekoh/articles/21acde07e1f555)

## 履歴

- 2026-11-03: 新規作成。
