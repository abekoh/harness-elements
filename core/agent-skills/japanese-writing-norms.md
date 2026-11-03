---
summary: AI に日本語の文書を書かせるときは、japanese-tech-writing と cognitive-rhythm-writing の 2 つのスキルを入れておく
stance: adopt
tags: [agents, writing]
depends_on: []
created: 2026-11-03
updated: 2026-11-03
models: [claude-opus-5-5]
---

# japanese-tech-writing と cognitive-rhythm-writing

## 概要

k16shikano 氏が gist で公開している、日本語の文章規範の Agent Skill です。2 つで 1 組になっています。

- japanese-tech-writing: 日本語の技術文書の規範。段落と論証の組み立て、論証の厳密さ、読み手の負荷の管理などを定める。
- cognitive-rhythm-writing: 説明的な文章に緩急をつける規範。japanese-tech-writing を前提にしている。

AI に日本語を書かせると、「本章では〜を扱う」のような予告、「不可欠」「多角的」のような中身のない語、英語を直訳した比喩、同じ主張の言い換えが混ざりがちです。論証が行ったり来たりしたり、推量を根拠なく断定に変えたりもします。逆に、ツッコミどころを消すと、正しいけれど平坦で読み進める気にならない文章になります。japanese-tech-writing は前者を、cognitive-rhythm-writing は後者を、書く段階で防ぐための規範です。

## 方針

AI に日本語の文書を書かせるとき、最初に入れておく規範として使えるため adopt とします。迷ったら、ひとまず 2 つとも入れておきます。

- 日本語の文書を書くエージェントには、japanese-tech-writing と cognitive-rhythm-writing の両方を入れる。
- 日本語の文書を執筆・推敲するときは 2 つを併用するよう、CLAUDE.md や AGENTS.md に書く。

  ```markdown
  ## 日本語文書

  日本語の文書を執筆または推敲するときは、次のスキルを併用する。

  - `japanese-tech-writing`
  - `cognitive-rhythm-writing`
  ```


## 解説

### japanese-tech-writing の規範

技術書の章、記事、解説文を書く・推敲するときの規範で、次の項目を定めています。

| 項目 | 主な内容 |
| --- | --- |
| 段落と論証の構成 | 1 段落 1 トピック。段落の冒頭で前の段落との関係を接続表現で示す。反論を処理してから結論を一度だけ置く |
| 論証の厳密さ | 推量を根拠なく断定に変えない。別々のものを「同じ」とまとめない。因果にはその仕組みを一文で添える。「必ず」を避けて条件を書く |
| 読み手の負荷の管理 | 読者が覚えておく情報は一度に一段だけ増やす。あとで使わない固有名を出さない。新しい例を足すときは前の例との違いを述べる |
| 視点と語り | 論証の中で読者を「あなた」と呼ばない。術語は定義したら同じ語で通す |
| 演出の抑制 | 太字は一節に一、二か所まで。「重要なのは〜」の前置きや「A ではなく B だ」の決め台詞を多用しない |
| LLM っぽい空句の禁止 | 「本章では〜を扱う」のような予告、「不可欠」「多角的」「掘り下げる」などの語、「さらに」「また」の連打を避ける |
| 翻訳調の比喩と擬人化の禁止 | 「運ぶ」「効く」のような直訳の比喩や、「モデルは〜を知っている」のような擬人化を避ける。字義どおりの動作を想像できる比喩は言い直す |
| 冗長の排除 | 同じ主張の言い換え、描写の直後の要約し直しを避ける |
| 見出しの付け方 | 節が答える問いか、扱う対象を指す具体的な見出しにする |
| 読者への誠実さ | 確かめていないことを確かめたように書かない |

### cognitive-rhythm-writing の規範

「密度はあるが平坦な文章」を直すための規範です。作業前に japanese-tech-writing を読むよう指示しています。

- 基本原理: 緩急は情報量ではなく、読者の認知モード(観察、逡巡、断定、再観察)の切り替えで作る。文章には答えの出ていない問いなどの「未回収の緊張」を常に一つ開いておく。
- 生成側の制約: 緊張の材料は、対象そのものの性質や読者が抱く反問から取る。本文の進行を語る文(「次に〜を説明する」)で代用しない。規範に出てくる手法の名前(「緊張」「回収」など)を本文に書かない。
- 短文化の禁止: 拍を作るために必要な文脈を削らない。
- 文と段落: 文は「立てる→流す→止める」の拍で書く。密な段落が 2〜3 続いたら疎な段落を挟む。
- 節の入り方と結び: 「本節では〜」と宣言せず、違和感や反問から入る。結びは抽象で終えず、読者の持つ具体に着地させる。
- 駄文の判定と点検: 文が「状況を更新しているか、文書を更新しているか」で判定し、文書だけを更新する文(進行の実況など)は削る。書いたあとは、決められた順で機械的に点検する。

### 導入

どちらも gist の `SKILL.md` 1 ファイルです。スキルのディレクトリに置きます。cognitive-rhythm-writing は `../japanese-tech-writing/SKILL.md` を読むため、2 つを同じ階層に置きます。

```sh
mkdir -p ~/.claude/skills/japanese-tech-writing ~/.claude/skills/cognitive-rhythm-writing
gh gist view fd287c3133457c4fd8f5601d34aa817d -f SKILL.md > ~/.claude/skills/japanese-tech-writing/SKILL.md
gh gist view eb2929f13ed19c97188393d297be8432 -f SKILL.md > ~/.claude/skills/cognitive-rhythm-writing/SKILL.md
```

gist にはバージョンがないため、更新を取り込むときは同じコマンドで取り直します。japanese-tech-writing のライセンスは Unlicense です。2026-11-03 時点で、japanese-tech-writing は 7 回、cognitive-rhythm-writing は 3 回改訂されています。

## トレードオフ

### 得られるもの

- AI が書いた日本語から、予告や空句、直訳の比喩、言い換えの繰り返しが減る。
- 論証の向きがそろい、推量と断定の区別が保たれる。
- 読み物として書く文章が平坦になりにくい。

### 失われるもの

- 規範が長く、コンテキストを多く使う。
- 規範どうしや、ほかの日本語の推敲スキル(yomiyasu など)と指示が食い違うことがある。
- 個人の gist なので、バージョンがなく、更新は自分で取り込む必要がある。
- cognitive-rhythm-writing は読み物向けで、仕様書や手順書には合わない規則もある(問いから節に入る、など)。

## 採用すべき？

### 採用すべきケース

- AI に日本語の技術文書、記事、解説文、PR の説明などを書かせる。
- AI の日本語の書き方に迷ったときの最初の一手として。

### 採用すべきでないケース

- エージェントが日本語の文章をほとんど書かない。
- 組織で別の文章規範やスタイルガイドが決まっていて、指示が食い違う。

## 参考情報

- [japanese-tech-writing/SKILL.md(k16shikano)](https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d)
- [cognitive-rhythm-writing/SKILL.md(k16shikano)](https://gist.github.com/k16shikano/eb2929f13ed19c97188393d297be8432)
- [Agent Skills | Claude Code Docs](https://code.claude.com/docs/en/skills)

## 履歴

- 2026-11-03: 新規作成。
