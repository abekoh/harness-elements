---
extends: null
---

# core

筆者(abekoh)の基本的な考えをまとめたレイヤーです。ほかのレイヤーはすべて、このレイヤーを起点に継承します。

## 素材

<!-- index:start -->

| 素材 | stance | 要約 |
| --- | --- | --- |
| [library/go/moq](library/go/moq.md) | recommended | Go のインタフェースから型安全なモック・スタブを生成し、呼び出し記録を Go の基本構文で検証する |
| [library/go/testify](library/go/testify.md) | recommended | Go のテストのアサーションには testify の assert / require を使う |
| [library/typescript/astro](library/typescript/astro.md) | adopt | ブログやドキュメントなど、コンテンツが中心の静的サイトは Astro で作り、frontmatter は Content Collections のスキーマで検証する |
| [principles/cqrs-without-event-sourcing](principles/cqrs-without-event-sourcing.md) | adopt | 読み込みは Query Service が SQL で DTO を直接組み立て、書き込みだけドメインモデルを通す |
| [principles/data-code-separation](principles/data-code-separation.md) | adopt | エンティティはデータとして扱い、振る舞いはデータを引数で受け取るステートレスな関数に書く |
| [principles/hide-details-only-when-needed](principles/hide-details-only-when-needed.md) | adopt | DB や外部コンポーネントの詳細は、3 つの条件のどれかに当てはまるときだけインタフェースで隠す |
| [principles/schema-first](principles/schema-first.md) | adopt | システムの境界を流れるデータの形はスキーマで先に定義し、型やコードはそこから生成して二重管理しない |
| [testing/given-when-then](testing/given-when-then.md) | adopt | テストは Given(準備)・When(実行)・Then(確認)の 3 つに分けて書く |
| [testing/mock-unmanaged-deps-only](testing/mock-unmanaged-deps-only.md) | adopt | モックは外部 API やメール送信など、制御下にない依存への出力にだけ使う(古典学派) |
| [testing/mock-vs-stub](testing/mock-vs-stub.md) | adopt | モックは外部への出力を、スタブは内部への入力を模倣する。スタブへの入力は検証しない |
| [testing/observable-behavior](testing/observable-behavior.md) | adopt | テストでは実装の詳細ではなく、観測可能な振る舞いだけを検証する |
| [testing/test-level-roles](testing/test-level-roles.md) | adopt | ドメインロジックは単体テストで網羅し、統合テストは正常系の通しと単体テストで拾えない箇所を受け持つ |

<!-- index:end -->
