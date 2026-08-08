# L3 — 被引用スキャン(先行チェック)

実施日: **2026-08-08**(全クエリ同日実行。再現手順を各項に記録)

## 判定: **周辺あり(要差分明示)— 直接競合なし、STOP 非該当**

- arXiv:2606.22531 の被引用は **0 件**(2 データベースで一致)
- 2026-06-21(Le v1 投稿)以降、Kinnersley/warp shell/photon rocket/warp drive の
  いずれの検索でも新着論文なし
- 「周辺」は Le 自身の引用文献に既に含まれるもののみ(下記)。我々の成果物
  (許容性拘束つき機動カタログ+観測署名)を先取りする計算は未発見

## 1. 被引用データベース

| ソース | クエリ / 手順 | 結果 |
|---|---|---|
| Semantic Scholar | `GET api.semanticscholar.org/graph/v1/paper/arXiv:2606.22531/citations` | `{"offset": 0, "data": []}` — **0 件** |
| INSPIRE-HEP | レコード 3170996(2026-06-23 作成、2026-07-17 更新)`citation_count` | **0** |
| INSPIRE-HEP | `q=refersto:recid:3170996` | total: **0** |
| Google(Web 検索) | 「arXiv 2606.22531 Le "warp drive" cited OR citations 2026」 | 引用論文なし(arXiv 本体・ミラーのみ) |

注: NASA ADS は API キー未設定のため未照会。Semantic Scholar・INSPIRE の
2 系統一致(ともに 0)で十分とみなす。次回スキャン時に ADS を追加可。

## 2. arXiv 新着スキャン(投稿日降順、export.arxiv.org/api/query)

| クエリ | Le v1 (2026-06-21) 以降の新着 | 直近のヒット(参考) |
|---|---|---|
| `all:Kinnersley` | **なし** | 2026-06-08「Hawking Temperatures … Vaidya and Kinnersley Geometries」(RVB 留数法。無関係) |
| `all:"warp shell"` | **なし** | 2605.25417(Le 自身の境界コスト論文)のみ |
| `all:"photon rocket"` | **なし** | 首位が 2606.22531 自身。次点 2021 年 |
| `cat:gr-qc AND all:"warp drive"` | **なし** | 首位が 2606.22531 自身 |
| `ti:"photon rocket steering"` 相当(上記 photon rocket 検索に包含) | なし | — |

## 3. 周辺文献(すべて Le v3 の引用文献内 = 差分は Le 論文自身が既に処理)

- **Barzegar–Buchert–Vigneron** 2602.16495(2026-02)= Le [16]。warp 時空の分類と
  no-go(R-Warp は DEC 違反等)。我々は Le の外側に出ないので影響なし
- **Buchert–Frackowiak** 2605.03653(2026-05-05)= Le [18]。metric-first 級の実現と
  不安定性報告。同上
- **Fuchs et al.** 2405.02709 = Le [10]。定速の正エネルギー殻(加速なし)。
  Le 13.4 節が差分処理済み
- **Lentz–Felton** 2405.19381 = v2[75]/v3[87]、**Clough–Dietrich–Khan** 2406.02466 =
  v2[76]/v3[88] → 詳細は L4_refs_75_76.md。Lentz–Felton は warp 放射の
  シミュレーション研究計画を「提案」しており(計算成果物は無し)、我々の
  Phase 2 に最も近い周辺。**差分を論文イントロで明示する必要あり**:
  (i) 我々は Le の許容性制約(認証済み [R]/[N] 拘束)下の具体的機動カタログから
  L(u) = −ṁ と角度パターンを「計算」する。(ii) ボロメトリック+パラメータ化
  シナリオに限定(スペクトル微視物理を主張しない)。(iii) 対象は Alcubierre 型
  ではなく Le の radiative momentum warpshell

## 4. 判定の根拠(三値)

- 直接競合(= Le 理論の許容性制約つき機動カタログ/観測署名の計算)は 0 件
- 周辺 = Lentz–Felton の「提案」論文。彼らの研究計画が実行されれば競合し得るが、
  現時点で公開された計算はない。→ **周辺あり(要差分明示)**、STOP 非該当
- 本スキャンは 2026-08-08 時点。**Phase 2 着手前に再実行を推奨**(クエリは上表の
  とおり再現可能)
