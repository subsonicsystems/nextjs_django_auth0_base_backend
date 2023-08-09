# nextjs_django_auth0_base_backend
汎用的なWebアプリケーションを作成するプロジェクトです。  
Next.js / Django / Auth0 / Material UI / Joy UIを組み合わせています。

このリポジトリはバックエンドです。  
フロントエンドは  
https://github.com/subsonicsystems/nextjs_django_auth0_base_frontend  
です。

# 設定
## Auth0コンソール
1. Applications | APIs  
[+ Create API]をクリックします
2. New API
    - `Name` API名を入力します
    - `identifier` API Audienceを入力します
      - 例: https://[your-url]
    - `Signing Algorithm` `RS256`を選択します
    - [Create]をクリックします
3. Settingsタブをクリックします
4. Access Settings
    - `Allow Offline Access`を有効にします

## .envの作成
- プロジェクトルートに`.env`を作成します
- `DOMAIN` [テナント名].jp.auth0.com
- `AUDIENCE` Auth0コンソールのApplications | APIsの`API Audience`
