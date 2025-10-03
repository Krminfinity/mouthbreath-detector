# 開発タスク分割・バックログ

作成日: 2025-10-03

---
## 1) 開発タスク分割（バックログ → 優先順）

### P0｜MVPの骨格

| ID | タスク | 内容概要 | DoD |
|----|--------|----------|-----|
| T0 | プロジェクト雛形 | WPF + トレイアイコン + 自動起動設定/権限チェック | 常駐・トレイON/OFF切替・例外ログ出力 |
| T1 | マイク入力ストリーミング | 16kHz/mono、RMSメーター、デバイス選択 | デバイス切替・停止/再開・無音時安定 |
| T2 | DSP前処理 | プリエンファシス、50–7kHzバンドパス、25ms/10msシフト | RMS/ZCR/帯域エネルギー可視化 |
| T3 | 口呼吸スコアリング v1 | ルールベース s_t, ŝ_t, 状態機械 | s_t∈[0,1], ŝ_t算出, mouth/nasal/unknown遷移 |
| T4 | 通知エンジン | 連続L秒≥T_highで通知、クールダウン、サイレント帯 | 条件/クールダウン/サイレントが仕様通り |
| T5 | ログ保存 | CSV/JSONローテ、保持期間、エクスポート | `metrics_YYYYMMDD.csv`出力/削除ポリシー |
| T6 | ダッシュボード | 当日サマリ/10分時系列/状態インジケータ | 指標4種表示・時系列描画 |
| T7 | 設定画面 | 感度/閾値・通知・プライバシー・プロファイル | 即時反映・再起動不要・録音保存OFF既定 |

### P1｜品質と適応

| ID | タスク | 内容概要 |
|----|--------|----------|
| T8 | 環境ノイズ学習 | ノイズフロアE₀逐次更新・自己適応 |
| T9 | キャリブレーション | 鼻/口デモ→自動閾値調整 GUI |
| T10 | 偽陽性抑制 | タイピング/送風パターン検出・フィルタ |

### P2｜拡張の入口

| ID | タスク | 内容概要 |
|----|--------|----------|
| T11 | Webカメラ開口比 | MAR推定・即時破棄方針 |
| T12 | Late Fusion | 音×映像 AND/OR/重み投票 |

---
## 2) UIワイヤーフレーム（テキスト）

### トレイメニュー
- 状態表示（●緑=鼻 / ●橙=口 / ●灰=不明）
- ON/OFF トグル
- 一時停止（30/60/90分）
- ダッシュボード
- 設定
- 終了

### ミニウィジェット
`状態アイコン ｜ スコアバー(0–1) ｜ 一時停止ボタン`

### ダッシュボード
- ヘッダ：今日の総稼働 / 口呼吸合計 / 割合 / 通知回数
- グラフ：10分粒度ヒートマップ or 折れ線（mouth割合）
- イベントリスト：`時刻｜連続秒数｜ピークスコア`
- フッタ：エクスポート / 保持期間 / プライバシー確認

### 設定
- 入力：デバイス選択、入力レベルテスト
- 検出：感度（低/標準/高/カスタム）、T_high/T_low、L/M秒
- 通知：トースト/音/クールダウン、サイレント時間帯
- プライバシー：録音保存OFF（既定）、特徴量のみ保存、保持日数
- プロファイル：静音室 / オフィス / カフェ
- キャリブレーション開始ボタン

---
## 3) 初期アルゴリズム & しきい値（MVP）

- フレーム：25ms、シフト10ms、Hamming
- 特徴量（各フレーム）：RMS, ZCR, Bark帯域エネルギー（0.3–1k / 1–3k / 3–7kHz）、スペクトル傾斜(Slope)、高周波比 HFB=3–7k / 0.3–1k
- ノイズフロア：E₀=無音RMSの指数移動平均
- スコア s_t (0–1):
  `s_t = w1·norm(HFB) + w2·norm(ZCR) + w3·norm(Slope_flatness)` （w1=0.5, w2=0.3, w3=0.2）
- 移動平均：`ŝ_t = MA(s_t, 窓=2s)`
- 状態遷移（既定）：
  - T_high=0.62, T_low=0.45
  - 開始: ŝ_t ≥ T_high が L=6s 連続
  - 終了: ŝ_t ≤ T_low が M=4s 連続
- 通知：mouth状態 30秒連続で発火、クールダウン5分
- 偽陽性抑制（初期）：ZCR極端高＋瞬間ピーク→除外、3–7kHz鋭い狭帯域ピーク（キーボード）→ダウンクレジット

---
## 4) データ仕様（ログ）

### 行ログ
`timestamp, session_id, state(nasal/mouth/unknown), score, rms, noise_floor, profile, event(start/end/none)`

### 10分アグリゲート
`bucket_start, total_secs, mouth_secs, ratio, events`

### 保存方針
- パス: `/logs/metrics_YYYYMMDD.csv` (UTF-8, 日次ローテ)
- 保持: 既定30日（期限超過自動削除）

---
## 5) 受け入れ基準（MVP）

- 8時間連続稼働でクラッシュなし、CPU < ~15%、メモリ < ~300MB
- 条件通知（30秒連続・クールダウン）が仕様通り作動
- ダッシュボードに「総モニタ/口呼吸/割合/回数」表示 & CSV出力可
- プライバシー既定：録音ファイル不保存・特徴量のみ保存

---
## 6) 検証計画・テストプロトコル

### 機能テストシナリオ
| シナリオ | 期待結果 |
|----------|----------|
| 静音 | state=unknown維持 |
| 扇風機 | 偽mouth抑制（連続条件満たさず） |
| キーボード多打 | s_t一時上昇もmouth未確定または速やか復帰 |
| 会話 | 会話継続で mouth確定しない（unknown寄り） |
| 鼻呼吸 | s_t低・mouth不発 |
| 口呼吸 | s_t上昇→6sでmouth開始→30sで通知 |

### 設定反映テスト
- 感度プリセット変更で T_high/T_low が即反映
- サイレント帯設定中は通知抑制
- クールダウン中の再通知防止

### ログテスト
- 日跨ぎで新ファイル生成
- 保持期間超の旧ファイル削除

### 定量評価（社内）
- 参加者N人×各5分（鼻/口/会話/タイピング）
- 指標: Precision / Recall / F1 （自己申告 or 口開閉ラベル）

---
## 7) プロジェクト雛形（構成案）

```
MouthBreathMonitor/
 ├─ src/
 │   ├─ App.xaml / App.xaml.cs
 │   ├─ MainWindow.xaml(.cs)        # ダッシュボード
 │   ├─ TrayService.cs
 │   ├─ Audio/
 │   │   ├─ AudioInput.cs           # NAudioでのキャプチャ
 │   │   └─ FeatureExtractor.cs     # RMS/ZCR/帯域エネ
 │   ├─ Detect/
 │   │   ├─ Scorer.cs               # s_t, ŝ_t
 │   │   └─ StateMachine.cs         # 開始/終了判定
 │   ├─ Notify/Notifier.cs
 │   ├─ Logging/LogWriter.cs
 │   ├─ Settings/Config.cs
 │   └─ Views/SettingsWindow.xaml(.cs)
 ├─ assets/
 ├─ logs/    # 日次ローテ
 ├─ MouthBreathMonitor.csproj
 └─ README.md
```

### 主要依存（候補）
- NAudio（音声入力）
- Microsoft.Toolkit.Uwp.Notifications（トースト）
- LiveCharts2（グラフ）
- （将来）Microsoft.ML / Microsoft.ML.OnnxRuntime

---
## 8) 擬似コード（検出ループ要旨）

```csharp
while (capturing) {
  var frame = audio.ReadFrame(25ms);
  var feat = Extract(frame); // rms, zcr, bandEnergies, slope
  var s = Score(feat, noiseFloor);
  var s_hat = MovAvg.Update(s);
  state = fsm.Step(s_hat, T_high, T_low, L, M);
  ui.Update(state, s_hat);
  logger.Write(ts, state, s_hat, feat.rms, noiseFloor);
  notifier.MaybeFire(state, duration, cooldown);
}
```

---
## 9) 今後の拡張（短冊）

- Webカメラ開口比（Dlib/Mediapipe→MAR）／Late Fusion
- プロファイル自動切替（環境音クラスタ）
- 軽量DNN分類（呼吸/会話/打鍵/送風 多クラス）
- 外部連携（ローカルWebhook）簡易API

---
（以上）