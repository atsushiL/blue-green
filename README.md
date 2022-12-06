<div id="top"></div>

## 使用技術一覧

<!-- シールド一覧 -->
<!-- 該当するプロジェクトの中から任意のものを選ぶ-->
<p style="display: inline">
  <!-- バックエンドのフレームワーク一覧 -->
  <img src="https://img.shields.io/badge/-Django-092E20.svg?logo=django&style=for-the-badge">
  <!-- バックエンドの言語一覧 -->
  <img src="https://img.shields.io/badge/-Python-F2C63C.svg?logo=python&style=for-the-badge">
  <!-- ミドルウェア一覧 -->
  <img src="https://img.shields.io/badge/-Nginx-269539.svg?logo=nginx&style=for-the-badge">
  <img src="https://img.shields.io/badge/-MySQL-4479A1.svg?logo=mysql&style=for-the-badge&logoColor=white">
  <img src="https://img.shields.io/badge/-Gunicorn-199848.svg?logo=gunicorn&style=for-the-badge&logoColor=white">
  <!-- インフラ一覧 -->
  <img src="https://img.shields.io/badge/-Docker-1488C6.svg?logo=docker&style=for-the-badge">
</p>

## 目次

1. [プロジェクトについて](#プロジェクトについて)
2. [環境](#環境)
3. [ディレクトリ構成](#ディレクトリ構成)
4. [ER 図](#er-図)
5. [開発環境構築](#開発環境構築)
6. [Swagger の設定](#swaggerの設定)
7. [リモートデバッグの方法](#リモートデバッグ)
8. [トラブルシューティング](#トラブルシューティング)

<!-- Backlogのwiki(READMEの作成方法のesaのリンクもwikiに貼っておく) -->
<br />
<div align="right">
    <a href="https://pj100.esa.io/posts/4190"><strong>READMEの作成方法 »</strong></a>
</div>
<br />
<!-- Backlogのwiki(Dockerfileのesaのリンクもwikiに貼っておく) -->
<div align="right">
    <a href="https://pj100.esa.io/posts/4196"><strong>Dockerfileの詳細 »</strong></a>
</div>
<br />
<!-- プロジェクト名を記載 -->

## 住まいるリース CRM

<!-- プロジェクトについて -->

### プロジェクトについて

住まいるリースバックの案件管理システム

<!-- プロジェクトの概要を記載 -->

  <p align="left">
    <br />
    <!-- プロジェクト詳細にBacklogのWikiのリンク -->
    <a href="https://aiful100.backlog.com/wiki/PJ_SMILE_LEASEBACK_CRM/Home"><strong>プロジェクト詳細 »</strong></a>
    <br />
    <br />

<p align="right">(<a href="#top">トップへ</a>)</p>

## 環境

| 言語・フレームワーク等 | バージョン |
| ---------------------- | ---------- |
| Django                 | 4.0.6      |
| Python                 | 3.10.6     |
| Django Rest Framework  | 3.13.1     |
| MySQL                  | 8.0.30     |
| Docker Compose         | 2.9.0      |

<!-- 言語、フレームワーク、ミドルウェア、インフラの一覧とバージョンを記載 -->
<p align="right">(<a href="#top">トップへ</a>)</p>

## ディレクトリ構成

<!-- Treeコマンド(tree -d -N -I __pycache__ )を使ってディレクトリ構成を記載 -->

```
.
├── README.md
├── ag_smile_leaseback_crm_back
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── containers
│   ├── django
│   │   └── Dockerfile
│   ├── mysql
│   │   ├── Dockerfile
│   │   ├── init.sql
│   │   └── my.cnf
│   └── nginx
│       ├── Dockerfile
│       ├── Dockerfile.dev
│       ├── conf.d
│       │   └── default.conf
│       └── nginx.dev.conf
├── crm
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── fixtures
│   │   ├── __init__.py
│   │   └── crm.json
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── docker-compose.prod.yml
├── docker-compose.yml
├── entrypoint.bash
├── manage.py
├── poetry.lock
├── pyproject.toml
└── set-up-env.test.sh
└── static
```

<p align="right">(<a href="#top">トップへ</a>)</p>

## ER 図

<!-- Backlogのwiki(draw.ioのリンクもwikiに貼っておく) -->

<a href="https://app.diagrams.net/#G18pfk4_IYhiXwttIcjVe8x194zKJjpRFj"><strong>ER 図詳細 »</strong></a>

<p align="right">(<a href="#top">トップへ</a>)</p>

## 開発環境構築

<!-- コンテナの作成方法、パッケージのインストール方法など、開発環境構築に必要な情報を記載 -->

1. .env ファイルの配置

@shun198 から.env ファイルをもらい、.env ファイルをルートディレクトリ直下に配置

2. イメージの作成

以下コマンドで Docker image を作成します

```
docker-compose build
```

3. コンテナの起動

以下のコマンドでコンテナを起動します

```
docker-compose up -d
```

4. 動作確認

http://127.0.0.1:8000 にアクセスできたら成功

5. テストデータを入れる

以下のコマンドを実行するとテストデータを入れることができます

```
docker-compose exec app poetry run python manage.py loaddata crm.json
```

### コンテナが起動しない時は？

[トラブルシューティング](#トラブルシューティング)へ移動してください

### コンテナの停止

以下のコマンドでコンテナを起動します

```
docker-compose down
```

## Swagger の設定

<a href="https://pj100.esa.io/posts/4699"><strong>詳細 »</strong></a>

## リモートデバッグ

<a href="https://pj100.esa.io/posts/4195"><strong>詳細 »</strong></a>

## トラブルシューティング

### .env: no such file or directory

.env ファイルがないので管理者にお問い合わせください

### docker daemon is not running

Docker Desktop が起動できていないので起動させましょう

### command not found: python

Docker Desktop か docker-compose のバージョンが古すぎるので最新のものにアップデートしましょう

### Ports are not available: address already in use

別のコンテナもしくはローカル上ですでに使っているポートがある可能性があります<br>
下記記事を参考にしてください
https://pj100.esa.io/posts/5023

### Module not found

```
docker-compose build
```

を実行して Docker image を更新してください

<p align="right">(<a href="#top">トップへ</a>)</p>
