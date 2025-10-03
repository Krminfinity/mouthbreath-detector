# 口呼吸検出システム (Mouthbreath Detector)

Webカメラを使用してリアルタイムで口呼吸を検出し、Windows通知でお知らせするヘルスケアアプリケーション。

## プロジェクト概要

在宅ワーカーやゲーマー、学習者向けに、作業中の呼吸習慣を把握・改善するためのツールです。MediaPipeによる顔認識でMAR（Mouth Aspect Ratio）を監視し、口呼吸状態を自動検出します。

## 主な特徴

- **リアルタイム検出**: Webカメラで口の開閉を監視し、口呼吸を即座に検出
- **バックグラウンド動作**: 常駐型でデスクトップ通知により口呼吸をお知らせ  
- **プライバシー配慮**: 映像データは保存されず、すべてローカル処理
- **低負荷動作**: MediaPipeによる軽量な顔認識処理
- **簡単起動**: EXEファイル化により、Python環境不要で実行可能

## システム要件

- **OS**: Windows 10/11
- **ハードウェア**: 
  - Webカメラ（内蔵・外付け問わず）
  - Python 3.10以上（開発時のみ）
- **メモリ**: 500MB以上
- **ストレージ**: 100MB以上の空き容量

## 🚀 クイックスタート

### 方法1: EXEファイルを使用（推奨）

1. **EXEファイルをダウンロード**
   - [Releases](https://github.com/Krminfinity/mouthbreath-detector/releases)ページにアクセス
   - 最新リリースの`main_app.exe`をダウンロード
   - ウイルス警告が出る場合は「その他の情報」→「実行」を選択

2. **実行**
   ```bash
   # デフォルト実行（無制限監視）
   main_app.exe
   
   # 30分間監視
   main_app.exe --duration 30
   
   # ヘルプ表示
   main_app.exe --help
   ```
   
   - バックグラウンドで口呼吸監視を開始
   - 口呼吸検出時にWindows通知が表示
   - 'q'キーで終了、またはCtrl+Cで中断

### 方法2: Pythonソースコードから実行

#### 📋 初回セットアップ手順

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/Krminfinity/mouthbreath-detector.git
   cd mouthbreath-detector
   ```

2. **Python仮想環境を作成**
   ```bash
   python -m venv .venv310
   ```

3. **仮想環境を有効化**
   ```bash
   # Windows
   .venv310\Scripts\activate
   
   # Linux/Mac  
   source .venv310/bin/activate
   ```

4. **依存パッケージをインストール**
   ```bash
   pip install mediapipe opencv-python win10toast matplotlib pyinstaller
   ```

#### 🏃‍♂️ アプリケーション実行

1. **バックグラウンド動作（通知のみ）**
   ```bash
   python src/core/main_app.py
   ```

2. **UI表示モード**
   ```bash
   python src/core/main_app.py --ui
   ```

3. **通知テスト**
   ```bash
   python src/core/test_toast.py
   ```

## 📊 使用方法

### バックグラウンド監視モード（デフォルト）
- カメラで顔を認識し、口の開閉状態を監視
- MAR（Mouth Aspect Ratio）が閾値以下の場合に口呼吸と判定  
- 検出時にWindows通知「口呼吸が検出されました」を表示
- 終了: `Ctrl+C`

### UI表示モード
- リアルタイムでカメラ映像を表示
- 口の状態をグラフで可視化
- 判定結果をリアルタイム表示

## ⚙️ 設定・カスタマイズ

### 感度調整
`main_app.py`内の閾値を調整可能：
```python
MOUTH_THRESH = 0.002  # 口呼吸判定の閾値
CONSEC_FRAMES = 3     # 連続フレーム数
```

### 通知設定
- 通知間隔: 1秒間隔で制御
- 通知内容: `win10toast`でカスタマイズ可能

## 🏗️ プロジェクト構成

```
mouthbreath-detector/
├── src/                   # ソースコード
│   └── core/             # コア機能
│       ├── main_app.py   # メインアプリケーション
│       └── test_toast.py # 通知テスト
├── docs/                 # ドキュメント
│   ├── task-backlog.md  # 開発タスク
│   └── development-notes.md # 開発メモ
├── requirements.md       # 要件定義
├── .gitignore           # Git除外設定
└── README.md            # このファイル
```

## 🔧 開発・ビルド

### EXEファイルの作成
```bash
# 仮想環境を有効化後
cd src/core
pyinstaller --onefile --windowed main_app.py
```

### 開発モード
- `main_app.py`: メインアプリケーション
- `test_toast.py`: Windows通知のテスト

## 📝 技術仕様

- **顔認識**: MediaPipe Face Mesh
- **口呼吸判定**: MAR (Mouth Aspect Ratio) 算出
- **閾値**: MAR < 0.002 で口呼吸と判定
- **通知**: win10toast（Windows専用）
- **UI**: tkinter + matplotlib（オプション）

## 🐛 トラブルシューティング

### カメラが認識されない
```bash
# カメラの動作確認
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera:', cap.isOpened()); cap.release()"
```

### 通知が表示されない
1. Windows通知設定を確認
2. `test_toast.py`で通知テスト実行

### MediaPipeエラー
- Python 3.10以上を使用
- OpenCVとの互換性を確認

## 📈 開発状況

### 完了済み
- [x] MVP (最小実行可能プロダクト)
- [x] MAR監視による口呼吸検出
- [x] Windows通知機能  
- [x] バックグラウンド動作
- [x] EXE化対応

### 今後の拡張予定
- [ ] 感度設定UI
- [ ] 統計・履歴機能
- [ ] macOS対応
- [ ] カスタム通知音

## 🔨 開発者向け: EXEビルド手順

```bash
# 1. Python 3.10仮想環境作成
python -m venv .venv310
.venv310\Scripts\activate

# 2. 依存関係インストール
pip install mediapipe opencv-python win10toast pyinstaller

# 3. EXEファイル作成
cd src/core
pyinstaller --onefile --exclude-module matplotlib --exclude-module tkinter --console main_app_exe.py

# 4. 出力確認
ls dist/main_app_exe.exe
```

**注意**: 
- EXEファイルは約95MBになります（MediaPipe等の依存関係を含むため）
- GitHub Releasesで配布（.gitignoreでEXEファイルは除外されています）

## 📄 ライセンス

MIT License

## 👤 作成者

**Makoto Kuramochi**
- GitHub: [@Krminfinity](https://github.com/Krminfinity)

## 🤝 コントリビューション

プルリクエストやIssueを歓迎します！

## 📚 関連ドキュメント

詳細な技術情報については以下を参照：
- [要件定義](./requirements.md)
- [開発タスク/バックログ](./docs/task-backlog.md)  
- [開発メモ](./docs/development-notes.md)

---

🌟 **スター**をつけていただけると嬉しいです！