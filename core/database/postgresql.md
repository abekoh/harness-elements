---
summary: RDB で迷ったら PostgreSQL を使う。外部キーとインデックスは別に設計し、豊富なデータ型とインデックスを活かす
stance: adopt
tags: [database, middleware]
depends_on: []
version: "18"
verified_at: 2026-11-03
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# PostgreSQL

## 概要

PostgreSQL はオープンソースのリレーショナルデータベース(RDB)です。PostgreSQL Global Development Group が開発しています。

RDB を選ぶとき、データ型、インデックス、クエリの実行方法の選択肢が少ないと、アプリケーション側で工夫する部分が増えます。PostgreSQL は配列、JSONB、範囲型などのデータ型と、B-tree 以外の多くのインデックスを標準で持ち、結合の方法も複数から選べます。PostgreSQL 互換をうたうクラウドのデータベースも増えており、身につけた知識をほかの製品でも使えます。

## 方針

MySQL と比べてデータ型、インデックス、結合の方法が豊富で、互換のデータベースも増えているため adopt とします。RDB で迷ったら PostgreSQL を使います。

- 新しく RDB を選ぶときは、特別な理由がなければ PostgreSQL にする。
- 外部キーとインデックスは別の概念として扱う。外部キーを張っても参照元の列にはインデックスが作られないため、必要なインデックスは自分で作る。
- 用途に合ったデータ型を使う。ID には `uuid`(18 以降は時刻順に並ぶ `uuidv7()` を使える)、日時には `timestamptz`、半構造データには `jsonb` を使う。
- B-tree で足りないときは、部分インデックス、式インデックス、GIN などを検討する。
- マネージドサービスや互換のデータベースを使うときは、使いたい拡張や機能に対応しているかを先に確かめる。

## 解説

### MySQL との主な違い

| 観点 | PostgreSQL | MySQL(InnoDB) |
| --- | --- | --- |
| データ型 | 配列、`jsonb`、範囲型、`uuid`、`inet`、列挙型、複合型など | JSON 型はあるが、配列型や範囲型はない |
| 外部キーとインデックス | 参照元の列にインデックスを自動では作らない | 参照元の列にインデックスがなければ自動で作る |
| インデックスの種類 | B-tree、Hash、GiST、SP-GiST、GIN、BRIN | 主に B-tree(全文検索と空間インデックスもある) |
| 部分インデックス | ある(`WHERE` 付きのインデックス) | ない |
| 式インデックス | ある | 8.0.13 以降で関数キーパーツとして使える |
| 結合の方法 | ネステッドループ結合、ハッシュ結合、マージ結合 | ネステッドループ結合、ハッシュ結合(8.0.18 以降) |

### 外部キーとインデックス

PostgreSQL では、外部キーの参照先の列には主キーか一意制約のインデックスが必ずあります。一方、参照元の列のインデックスは自動では作られません。参照先の行を `DELETE` したり、参照先の列を `UPDATE` したりすると、参照元のテーブルを探す必要があるため、多くの場合は参照元の列にもインデックスを作ります。どの列の組み合わせでインデックスを作るかを自分で選べるのは、インデックスと外部キーが分かれている利点です。

```sql
CREATE TABLE orders (
  id          uuid PRIMARY KEY DEFAULT uuidv7(),
  customer_id uuid NOT NULL REFERENCES customers (id),
  status      text NOT NULL,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- 外部キーの列のインデックスは自分で作る
CREATE INDEX orders_customer_id_created_at_idx ON orders (customer_id, created_at);
```

### インデックスの種類

| 種類 | 主な用途 |
| --- | --- |
| B-tree | 既定。等価と範囲の検索、並べ替え |
| Hash | 等価の検索だけ |
| GIN | 配列、`jsonb`、全文検索のように、1 つの値が複数の要素を持つデータ |
| GiST / SP-GiST | 範囲型、幾何データ、近傍の検索 |
| BRIN | 時系列のログのように、物理的な並びと値が相関する巨大なテーブル |

条件に合う行だけを対象にする部分インデックスと、式の結果を対象にする式インデックスも作れます。

```sql
-- 未処理の注文だけを対象にする
CREATE INDEX orders_pending_idx ON orders (created_at) WHERE status = 'pending';

-- 大文字・小文字を区別しない検索に使う
CREATE INDEX users_lower_email_idx ON users (lower(email));
```

### PostgreSQL 互換のデータベース

PostgreSQL と互換のある SQL やプロトコルを持つデータベースが増えています。

- Amazon Aurora PostgreSQL、Amazon Aurora DSQL
- Google Cloud の AlloyDB for PostgreSQL、Spanner の PostgreSQL インタフェース
- CockroachDB、YugabyteDB(分散 SQL)

互換の範囲は製品によって違い、使えない拡張や機能もあります。

### バージョンとサポート

メジャーバージョンはおよそ年に 1 回出て、初回のリリースから 5 年間サポートされます。メジャーバージョンを上げるときは、`pg_upgrade`、ダンプと再ロード、論理レプリケーションのどれかが必要です。

18(2025-09-25)では非同期 I/O、B-tree のスキップスキャン、`uuidv7()`、仮想生成列、OAuth 認証、`RETURNING` での `OLD` / `NEW` が入りました。確認日の時点で、19 は RC 1(2026-10-15)が出ています。

### メンテナンス状況

| 項目 | 内容 |
| --- | --- |
| メンテナ | PostgreSQL Global Development Group(コミュニティ) |
| GitHub スター数 | 22,684(postgres/postgres。公式リポジトリのミラー) |
| 最新コミット | 2026-11-03 |
| 最新リリース | 18.6(2026-08-13) |
| 確認日 | 2026-11-03 |

開発は GitHub ではなく、公式の Git リポジトリとメーリングリストで進められています。

## トレードオフ

### 得られるもの

- 豊富なデータ型とインデックスにより、アプリケーション側の工夫が減る。
- 外部キーとインデックスが分かれていて、インデックスの設計を自分で決められる。
- 互換のデータベースが多く、知識や SQL をほかの製品でも使える。

### 失われるもの

- 外部キーの列のインデックスを付け忘れると、参照先の削除や更新が遅くなる。
- 更新のたびに古い行が残るため、VACUUM の仕組みを理解して運用する必要がある。
- メジャーバージョンを上げるたびに、`pg_upgrade` などの作業が要る。

## 採用すべき？

### 採用すべきケース

- 新しく RDB を選ぶとき。
- 配列や `jsonb`、範囲型などのデータ型や、部分インデックスや GIN などを使いたい。

### 採用すべきでないケース

- 既存のシステムが MySQL で動いていて、移行のコストに見合わない。
- 組織の運用ノウハウやマネージドサービスが MySQL に偏っている。

## 参考情報

- [PostgreSQL](https://www.postgresql.org/)
- [PostgreSQL Documentation: Constraints(Foreign Keys)](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL Documentation: Index Types](https://www.postgresql.org/docs/current/indexes-types.html)
- [PostgreSQL Documentation: Release 18](https://www.postgresql.org/docs/current/release-18.html)
- [Versioning Policy](https://www.postgresql.org/support/versioning/)
- [MySQL 8.4 Reference Manual: FOREIGN KEY Constraints](https://dev.mysql.com/doc/refman/8.4/en/create-table-foreign-keys.html)

## 履歴

- 2026-11-03: 新規作成。
