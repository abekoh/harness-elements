---
summary: Go のインタフェースから型安全なモック・スタブを生成し、呼び出し記録を Go の基本構文で検証する
stance: adopt
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

moq は Go のインタフェース定義からテスト・ダブルを生成する CLI です。生成した構造体は、スタブとして値を返す機能と、呼び出しを記録するスパイの機能を持ちます。

## 方針

型安全で、Given-When-Then の形を崩さずに書けるため adopt とします。

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

moq が生成する構造体には、次の特徴があります。

- `XxxFunc` フィールドが元のインタフェースと同じ型を持つため、スタブを型安全に書け、エディタの補完も効く。
- 呼び出しの記録も引数の型を保っている。Go の基本構文だけで検証でき、呼び出し回数も `len(mock.XxxCalls())` で分かる。
- 定義していないメソッドを呼ぶと panic する。`-stub` オプションを付けると、panic せずにゼロ値を返す。

### gomock との比較

gomock(現在は uber-go/mock)は、Matcher による柔軟な検証ができます。一方で、次の弱点があります。

- 引数が `any` になり、スタブを型安全に書けない。
- 期待する呼び出しを Given の段階で書くため、Given-When-Then の形が崩れる。

golang/mock はアーカイブされ、uber-go/mock に引き継がれました。ただし、gomock から moq への移行は、テストの書き方そのものが変わるため単純ではありません。

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
- [gomock と比較される moq，こいつはモックを作るライブラリじゃなくてスタブを作るだけの責務放棄したライブラリや！](https://zenn.dev/mpyw/scraps/feffc9b3760000)
- [moqを使ったGoのテスト](https://zenn.dev/abekoh/articles/21acde07e1f555)

## 履歴

- 2026-11-03: 新規作成。
