# Mem0 Web System - Android連携サンプル

このディレクトリには、Mem0 Web SystemのAPIと連携するためのAndroidサンプルコードが含まれています。

## 主な機能

- ユーザー認証（JWTトークン）
- メモリ検索（キーワード、ベクトル、時系列）
- チャットメッセージの送受信
- ユーザー設定の取得と更新

## 使用方法

1. `Mem0ApiClient.kt`をAndroidプロジェクトに追加
2. 以下のように初期化して使用

```kotlin
// クライアントの初期化
val apiClient = Mem0ApiClient(
    baseUrl = "https://your-api-url.com",
    authToken = "your-jwt-token"
)

// コルーチンスコープ内で使用
lifecycleScope.launch {
    // ユーザープロファイルの取得
    val profileResult = apiClient.getUserProfile()
    profileResult.onSuccess { profile ->
        // プロファイル情報を処理
    }

    // メモリの検索
    val searchResult = apiClient.searchMemories(
        query = "検索キーワード",
        searchType = "keyword", // "keyword", "vector", "time"
        userId = "user123",
        scope = "personal"
    )
    searchResult.onSuccess { memories ->
        // 検索結果を処理
    }

    // チャットメッセージの送信
    val messages = listOf(
        mapOf("role" to "user", "content" to "こんにちは")
    )
    val chatResult = apiClient.sendChatMessage(
        messages = messages,
        userId = "user123"
    )
    chatResult.onSuccess { response ->
        // レスポンスを処理
    }
}
```

## 必要な依存関係

```gradle
dependencies {
    implementation 'com.squareup.okhttp3:okhttp:4.10.0'
    implementation 'org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4'
}
```

## 注意事項

- このサンプルコードは基本的な機能を示すためのものです
- 実際のアプリケーションでは、適切なエラーハンドリングとUI連携を実装してください
- 認証トークンの安全な保存には、Android Keystore Systemの使用を検討してください
