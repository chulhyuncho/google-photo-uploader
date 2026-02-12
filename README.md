# Google Photos Parallel Uploader

[English](#english) | [한국어](#한국어) | [简体中文](#简体中文) | [日本語](#日本語)

---

<a name="english"></a>
## English

A robust, high-speed CLI tool to upload photos and videos to Google Photos with automatic parallelization, batch registration, and local cleanup.

### Why I Developed This
I was always unhappy with the photos and videos piling up on my disks. I could upload them to Google Photos or Google Drive, but I didn't want to upload them to Google Drive in an unorganized state. While I wanted to upload them to Google Photos, I didn't want to spend more money on Google Cloud while already paying for Apple iCloud. Above all, it was just too much of a hassle.

Recently, while exploring "AI Vibe Coding", I found the process of quickly building things to be surprisingly fun. It made me want to create something I wouldn't normally make, and today, I suddenly felt the urge to build this. Although the AI did the coding, I'm releasing this as a commemoration of finally resolving this long-standing personal project. I'm not sure how useful this will be to others, but I've decided to share it with the world.

**Contact**:
- **Email**: ch.cho@devworld.co.kr
- **Facebook**: [ilovehojin](https://facebook.com/ilovehojin)
- **Instagram**: [@chulhyuncho](https://instagram.com/chulhyuncho)
- **Threads**: [@chulhyuncho](https://threads.net/@chulhyuncho)

> [!NOTE]  
> Please don't complain about bugs. Think of this as something I developed in passing. If you find an issue, feel free to request a fix, submit a PR, or just fork it and fix it yourself!

### Key Features
- **Parallel Uploads**: Uses `ThreadPoolExecutor` for concurrent transfers.
- **Batched Registration**: Minimizes API calls by grouping up to 50 items.
- **Resilience**: Exponential backoff for `429 Too Many Requests` errors.
- **Storage Optimization**: Deletes local files and empty parent folders after successful upload.
- **Real-time Monitoring**: Use `--watch` to monitor folders indefinitely.

### Installation & Setup

#### 1. Requirements
- Python 3.10+ required.

#### 2. Virtual Environment Setup
```bash
git clone <your-repo-url>
cd googledrive-uploader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. Obtaining `credentials.json` (Detailed Guide)
1.  **Google Cloud Console**: Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  **Create Project**: Click the project dropdown (top left) and select **New Project**. Give it a name and click **Create**.
3.  **Enable API**: In the search bar, type "Google Photos Library API", select it, and click **Enable**.
4.  **OAuth Consent Screen**:
    - Go to **APIs & Services** > **OAuth consent screen**.
    - Choose **External** and click **Create**.
    - Fill in App Name and Email.
    - **Crucial**: Under "Test users", click **Add Users** and add your own Google email address.
5.  **Create Credentials**:
    - Go to **APIs & Services** > **Credentials**.
    - Click **+ Create Credentials** > **OAuth client ID**.
    - Select **Desktop App** as the Application type.
    - Click **Create**.
6.  **Download**: Click the download icon (JSON) for your new client ID. Rename it to `credentials.json` and place it in the project root directory.

### Command-Line Options
| Option | Description |
| :--- | :--- |
| `folder` | **Required**. Path to the local folder to scan. It scans all subfolders recursively. |
| `--watch` | **Real-time Mode**. Continuously monitors the folder for new files and uploads them immediately. |
| `--workers` | **Parallelism**. Number of concurrent upload threads. Default is 4. Increase this (e.g., 20) for faster transfers on high-speed connections. |
| `--max-size` | **Size Filter**. Maximum file size in MB. Files larger than this will be automatically skipped to save bandwidth. |

---

<a name="한국어"></a>
## 한국어

자동 병렬 처리, 배치 등록 및 로컬 정리 기능을 갖춘 고성능 Google 포토 업로드 CLI 도구입니다.

### 개발 동기
늘 디스크에 쌓여있는 사진과 동영상이 불만이었다. 구글 포토나 구글 드라이브에 올리면 되지만, 정리 안된 상태로 구글 드라이브에 올리는 건 싫고, 구글 포토에 올리고 싶었으나, 애플 아이클라우드를 쓰면서 구글 클라우드에 또 돈을 들이기는 싫었다.. 무엇보다도, 귀찮았다.

최근 AI 바이브 코딩을 하면서.. 뭔가 뚝딱 만드는 과정이 재미있기도 하고, 평소에 안만들던 걸 만들고 싶다는 생각이 들었는데... 오늘 갑자기 이게 만들고 싶어졌다. 코딩은 AI가 했지만.. 그동안의 숙원 사업이 해결된 거 같은 기념으로 공개한다. 앞으로도 뭔 쓸모가 있을지 모르겠지만.. 공개라는 걸 좀 해볼까 한다.

**문의**:
- **이메일**: ch.cho@devworld.co.kr
- **페이스북**: [ilovehojin](https://facebook.com/ilovehojin)
- **인스타그램**: [@chulhyuncho](https://instagram.com/chulhyuncho)
- **쓰레드**: [@chulhyuncho](https://threads.net/@chulhyuncho)

> [!NOTE]  
> 버그 있다고 뭐라하지마라.. 지나가는 길에 개발했다고 생각해줘. 수정 요청을 하던지 PR을 날라던지, 포크 해다가 고쳐서 써.

### 주요 기능
- **병렬 업로드**: `ThreadPoolExecutor`를 사용하여 여러 파일을 동시에 전송합니다.
- **배치 등록**: 최대 50개 항목을 묶어 API 호출을 최소화하고 쿼터를 효율적으로 관리합니다.
- **탄력적 대응**: `429 Too Many Requests` 오류 발생 시 지수 백오프 자동 적용.
- **저장 공간 최적화**: 업로드 성공 후 로컬 파일 및 빈 상위 폴더를 자동으로 삭제합니다.
- **실시간 감시**: `--watch` 옵션으로 새로운 파일을 실시간으로 감지하고 업로드합니다.

### 설치 및 설정

#### 1. 요구 사항
- Python 3.10 이상 필요.

#### 2. 가상 환경 설정
```bash
git clone <your-repo-url>
cd googledrive-uploader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. `credentials.json` 획득 방법 (상세 가이드)
1.  **Google Cloud 콘솔**: [Google Cloud Console](https://console.cloud.google.com/)에 접속합니다.
2.  **프로젝트 생성**: 왼쪽 상단의 프로젝트 선택창에서 **새 프로젝트**를 클릭하여 생성합니다.
3.  **API 활성화**: 검색창에 "Google Photos Library API"를 입력하고 선택한 후 **사용**을 클릭합니다.
4.  **OAuth 동의 화면**:
    - **API 및 서비스** > **OAuth 동의 화면**으로 이동합니다.
    - User Type을 **외부(External)**로 선택하고 **만들기**를 클릭합니다.
    - 앱 이름과 이메일을 입력합니다.
    - **중요**: 하단의 "테스트 사용자" 섹션에서 **Add Users**를 클릭하여 본인의 구글 이메일을 추가해야 합니다.
5.  **사용자 인증 정보 생성**:
    - **API 및 서비스** > **사용자 인증 정보**로 이동합니다.
    - **+ 사용자 인증 정보 만들기** > **OAuth 클라이언트 ID**를 클릭합니다.
    - 애플리케이션 유형을 **데스크톱 앱(Desktop App)**으로 선택하고 **만들기**를 클릭합니다.
6.  **다운로드**: 생성된 클라이언트 ID의 다운로드 아이콘(JSON)을 클릭합니다. 파일 이름을 `credentials.json`으로 변경하여 프로젝트 루트 폴더에 넣습니다.

### 명령줄 옵션 설명
| 옵션 | 설명 |
| :--- | :--- |
| `folder` | **필수**. 미디어를 스캔할 로컬 폴더 경로입니다. 하위 폴더를 모두 재귀적으로 탐색합니다. |
| `--watch` | **실시간 모드**. 폴더를 계속 감시하면서 새로운 파일이 생기면 즉시 업로드합니다. |
| `--workers` | **병렬 처리**. 동시에 업로드를 수행할 스레드 수입니다. (기본값: 4). 고속 인터넷 환경에서는 10~30 정도로 높여 속도를 대폭 향상시킬 수 있습니다. |
| `--max-size` | **용량 제한**. 업로드 허용 최대 파일 크기(MB)입니다. 설정값보다 큰 파일은 대역폭 절약을 위해 자동으로 제외됩니다. |

---

<a name="简体中文"></a>
## 简体中文

一款功能强大的高效率 Google 相册上传 CLI 工具，支持自动并行处理、批量注册和本地清理。

### 为什么开发这个程序
我一直对磁盘上堆积的照片和视频感到不满。虽然可以将它们上传到 Google 相册或 Google 云端硬盘，但我不想在杂乱无章的情况下上传到云端硬盘。虽然我想上传到 Google 相册，但我已经在使用 Apple iCloud，不想在 Google Cloud 上再花钱。最重要的是，手动操作太麻烦了。

最近，在尝试“AI Vibe Coding”时，我发现快速构建工具的过程非常有趣。这让我产生了一种想要制作一些平时不会做的东西的冲动，于是今天，我突然想开发这个工具。虽然代码是由 AI 编写自开发，但为了纪念这个多年来的夙愿终于实现，我决定将其公开。我不知道它将来会有多大的用途，但我还是决定分享出来。

**联系方式**:
- **电子邮件**: ch.cho@devworld.co.kr
- **Facebook**: [ilovehojin](https://facebook.com/ilovehojin)
- **Instagram**: [@chulhyuncho](https://instagram.com/chulhyuncho)
- **Threads**: [@chulhyuncho](https://threads.net/@chulhyuncho)

> [!NOTE]  
> 不要抱怨有 Bug。就当作是我路过时顺手开发的。要么提交修复请求，要么发 PR，或者干脆自己 Fork 之后修改使用。

### 主要功能
- **并行上传**：使用 `ThreadPoolExecutor` 进行并发传输。
- **批量注册**：每次最多合并 50 个项目进行注册，减少 API 调用次数。
- **容错机制**：针对 `429 Too Many Requests` 错误自动执行指数退避重试。
- **存储优化**：上传成功后自动删除本地文件及空的父文件夹。
- **实时监控**：使用 `--watch` 参数实时监测并上传新文件。

### 安装与设置

#### 1. 环境要求
- 需要 Python 3.10 或更高版本。

#### 2. 虚拟环境设置
```bash
git clone <your-repo-url>
cd googledrive-uploader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. 获取 `credentials.json` (详细指南)
1.  **Google Cloud 控制台**：访问 [Google Cloud Console](https://console.cloud.google.com/)。
2.  **创建项目**：点击左上角的项目下拉菜单，选择 **新建项目** 并创建。
3.  **启用 API**：搜索 "Google Photos Library API"，进入页面并点击 **启用**。
4.  **OAuth 同意屏幕**：
    - 进入 **API 和服务** > **OAuth 同意屏幕**。
    - 选择 **外部 (External)**，然后点击 **创建**。
    - 填写应用名称和邮件。
    - **至关重要**：在“测试用户”下，点击 **ADD USERS** 并添加您的 Google 邮箱地址。
5.  **创建凭据**：
    - 进入 **API 和服务** > **凭据**。
    - 点击 **+ 创建凭据** > **OAuth 客户端 ID**。
    - 应用类型选择 **桌面应用 (Desktop App)**。
    - 点击 **创建**。
6.  **下载**：点击对应客户端 ID 的下载图标 (JSON)。将其重命名为 `credentials.json` 并移动到项目根目录下。

### 命令行选项详解
| 选项 | 描述 |
| :--- | :--- |
| `folder` | **必填**。要扫描的本地文件夹路径。程序会递归扫描所有子目录。 |
| `--watch` | **实时模式**。持续监控文件夹中的新项目，并自动即时上传。 |
| `--workers` | **并行数**。同时进行的上传线程数量。默认为 4。在高速网络环境下，建议增加此值（如 20）以大幅提升速度。 |
| `--max-size` | **大小过滤**。允许上传的最大文件大小 (MB)。超过此限制的文件将被自动跳过以节省带宽。 |

---

<a name="日本語"></a>
## 日本語

自動並列処理、バッチ登録、ローカルクリーンアップ機能を備えた、高機能な Google フォトアップロード CLI ツールです。

### 開発のきっかけ
ディスクに溜まっていく写真や動画にいつも不満を感じていました。Google フォトや Google ドライブにアップロードすればいいのですが、整理されていない状態で Google ドライブに上げるのは嫌でしたし、Google フォトに上げたいと思いつつも、すでに Apple iCloud を利用しているため、Google Cloud にさらにお金をかけるのは気が進みませんでした。何よりも、面倒でした。

最近、「AI Vibe Coding」をしながら、何かをさっと作り上げる過程が楽しくなり、普段作らないようなものを作りたいという思いが湧いてきました。そんな中、今日突然これを作りたくなりました。コーディングは AI が行いましたが、長年の懸案事項が解決した記念として公開します. 今後どのような役に立つかは分かりませんが、公開というものをやってみようと思います。

**お問い合わせ**:
- **メール**: ch.cho@devworld.co.kr
- **Facebook**: [ilovehojin](https://facebook.com/ilovehojin)
- **Instagram**: [@chulhyuncho](https://instagram.com/chulhyuncho)
- **Threads**: [@chulhyuncho](https://threads.net/@chulhyuncho)

> [!NOTE]  
> バグについて文句を言わないでください。通りすがりに開発したものだと思ってください。修正をリクエストするか、PRを送るか、あるいはフォークして自分で直して使ってください。

### 主な機能
- **並列アップロード**: `ThreadPoolExecutor` を使用した高速な並列転送。
- **バッチ登録**: 最大 50 項目をまとめて登録し、API 呼び出し回数を削減。
- **エラー耐性**: `429 Too Many Requests` エラー時の指数バックオフによる自動再試行。
- **ストレージ最適化**: アップロード成功後、ローカルファイルと空の親フォルダを自動削除。
- **リアルタイム監視**: `--watch` オプションでフォルダを監視し、新規ファイルを自動アップロード。

### インストールと設定

#### 1. 動作環境
- Python 3.10 以上が必要です。

#### 2. 仮想環境の構築
```bash
git clone <your-repo-url>
cd googledrive-uploader
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### 3. `credentials.json` の取得方法 (詳細ガイド)
1.  **Google Cloud Console**: [Google Cloud Console](https://console.cloud.google.com/) にアクセスします。
2.  **プロジェクトの作成**: 左上のプロジェクト選択から **新しいプロジェクト** を作成します。
3.  **API の有効化**: 検索バーに "Google Photos Library API" と入力して選択し、**有効にする** をクリックします。
4.  **OAuth 同意画面**:
    - **API とサービス** > **OAuth 同意画面** に移動します。
    - User Type を **外部 (External)** に設定し、**作成** をクリックします。
    - アプリ名とメールアドレスを入力します。
    - **重要**: 下部の「テストユーザー」セクションで **ADD USERS** をクリックし、自身の Google メールアドレスを追加してください。
5.  **認証情報の作成**:
    - **API とサービス** > **認証情報** に移動します。
    - **+ 認証情報を作成** > **OAuth クライアント ID** を選びます。
    - アプリケーションの種類を **デスクトップ アプリ (Desktop App)** に設定し、**作成** をクリックします。
6.  **ダウンロード**: 作成されたクライアント ID のダウンロードアイコン (JSON) をクリックします。ファイル名を `credentials.json` に変更し、プロジェクトのルートフォルダに保存します。

### コマンドラインオプションの詳細
| オプション | 説明 |
| :--- | :--- |
| `folder` | **必須**。スキャン対象のローカルフォルダのパスです。サブフォルダも再帰的に全てスキャンします。 |
| `--watch` | **リアルタイム監視**。フォルダを常時監視し、新しいファイルが追加されると即座にアップロードします。 |
| `--workers` | **並列処理**。同時にアップロードを行うスレッド数です（デフォルト: 4）。高速回線をご利用の場合は、20などの大きな値を設定して高速化できます。 |
| `--max-size` | **サイズ制限**。アップロードを許可する最大ファイルサイズ (MB) です。この値を超えるファイルは帯域節約のため自動的にスキップされます。 |

---

## License
MIT
