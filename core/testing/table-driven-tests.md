---
summary: テーブル駆動テストは、テスト項目ごとの準備・実行・確認の差が小さいときだけ使う。差が大きければサブテストに Given-When-Then で書く
stance: adopt
tags: [testing, go]
depends_on: [testing/given-when-then]
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# テーブル駆動テスト

## 概要

テーブル駆動テスト(Table-driven testing)は、入力値と期待値を並べた表(構造体のスライスなど)を作り、ループで 1 件ずつ実行するテストの書き方です。Go でよく使われ、`gotests` で生成されるテストのひな形もこの形です。表を見るだけで、どんな入力に何を期待しているかが分かります。

ただし、すべてのテスト項目を 1 つの表に押し込むと、テストが読みにくくなることがあります。この素材では、テーブル駆動テストを使う条件と、使わないときの書き方を決めます。

## 方針

条件が合えば簡潔に書ける一方、合わないテストに使うと Given-When-Then の構造が崩れます。使うかどうかを判断する書き方なので adopt とします。

- テスト項目ごとの Given(準備)・When(実行)・Then(確認)の差が、入力値と期待値だけのときはテーブル駆動テストを使う。
- テスト項目によって準備や確認の内容が変わるときは、表を作らない。`t.Run()` のサブテストを項目ごとに書き、それぞれを [Given-When-Then](given-when-then.md) で書く。
- 表のフィールドに、準備用の関数(`prepare func(...)`)や、項目によって使ったり使わなかったりする期待値(`wantErr`、`wantList` など)を足したくなったら、表をやめるサインとみなす。
- ループの中で、項目によって処理を分ける `if` を書かない。
- 状態に依存するテストが書きにくいときは、対象を状態を持たない関数に書き換えられないかも考える([データとコードの分離](../principles/data-code-separation.md))。

## 解説

### 向いているテスト

同じ呼び出し方で、大量の入力値と期待値を試すテストです。純粋関数のテストが典型です。

```go
func TestSum(t *testing.T) {
	tests := []struct {
		a, b int
		want int
	}{
		{a: 0, b: 0, want: 0},
		{a: 1, b: 2, want: 3},
		{a: 10, b: -10, want: 0},
	}
	for _, tt := range tests {
		t.Run(fmt.Sprintf("%d+%d", tt.a, tt.b), func(t *testing.T) {
			assert.Equal(t, tt.want, Sum(tt.a, tt.b))
		})
	}
}
```

### 向かないテスト

次のようなテストを 1 つの表にまとめると、読みにくくなります。

- 状態によって動作が変わるテスト
- テスト項目によって準備が違うテスト
- テスト項目によって確かめたいものが違うテスト

たとえば、ユーザを保存するリポジトリの `Create` をテストするとします。「名前が空ならエラー」「同じ名前がすでにあればエラー」「ID が連番で振られる」と項目を足すたびに、表に `wantErr`、`prepare`、`wantList` といったフィールドが増えます。ループの中には `if tt.prepare != nil` や `if tt.wantList != nil` が並びます。

その結果、1 つのテスト項目の Given・When・Then が、表の定義とループの中に散らばります。読む人は表とループを行き来しなければなりません。どのテスト項目も同じ形を強いられ、その項目では関心のない入力値まで書くことになります。

### サブテストに書き直す

表をやめ、`t.Run()` の中に各項目を素直に書くと、Given・When・Then が 1 か所にまとまります。準備や確認の量は、項目ごとに変えてかまいません。

```go
func TestUserRepository_Create(t *testing.T) {
	t.Run("同じ名前がすでにあればエラー", func(t *testing.T) {
		// Given
		r := NewUserRepository()
		_, err := r.Create(UserInput{Name: "Alice"})
		require.NoError(t, err)

		// When
		_, err = r.Create(UserInput{Name: "Alice"})

		// Then
		assert.Error(t, err)
	})

	t.Run("ID が連番で振られる", func(t *testing.T) {
		// Given
		r := NewUserRepository()
		for i := range 5 {
			_, err := r.Create(UserInput{Name: fmt.Sprintf("User%d", i+1)})
			require.NoError(t, err)
		}

		// When
		got, err := r.Create(UserInput{Name: "Alice"})

		// Then
		require.NoError(t, err)
		assert.Equal(t, User{ID: 6, Name: "Alice"}, got)
	})
}
```

Go の標準ライブラリにも、表を使わず `t.Run()` でテスト項目を並べている例があります(`archive/zip`、`strconv` など)。表で書きにくいテストはライブラリより Web アプリケーションを書くときに出てきやすいようです。

## トレードオフ

### 得られるもの

- テスト項目ごとに Given・When・Then が 1 か所にまとまり、上から順に読める。
- 項目ごとに必要な準備と確認だけを書ける。
- 表のフィールドや、ループの中の分岐が増えない。

### 失われるもの

- サブテストで書くと、似た準備や呼び出しを項目ごとに繰り返すことになり、コードが長くなる。
- 入力値と期待値の一覧を、表のように一目で見渡せなくなる。

## 採用すべき？

### 採用すべきケース

- 純粋関数など、入力値と期待値の組み合わせを大量に試すテスト。
- どのテスト項目でも、準備と確認の内容が同じテスト。

### 採用すべきでないケース

- 状態に依存し、テスト項目ごとに事前データの準備が違うテスト。
- 正常系では戻り値を、異常系ではエラーを、別の項目では保存後の状態を確かめるなど、確認の内容が項目によって違うテスト。

## 参考情報

- [Go Wiki: TableDrivenTests](https://go.dev/wiki/TableDrivenTests)
- [Table-driven testing に縛られない Go のテストパターン](https://speakerdeck.com/abekoh/table-driven-testing-nifu-rarenai-gonotesutopatan)
- [3A - Arrange, Act, Assert - XP123](https://xp123.com/3a-arrange-act-assert/)
- 『テスト駆動開発』Kent Beck 著(第 19 章)
- 『単体テストの考え方/使い方』Vladimir Khorikov 著
- [テーブル駆動テストと状態](https://speakerdeck.com/hazumirr/teburuqu-dong-tesutotozhuang-tai)

## 履歴

- 2026-11-03: 新規作成。
