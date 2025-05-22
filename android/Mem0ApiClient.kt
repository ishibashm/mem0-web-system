package com.example.mem0app

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException

/**
 * Mem0 Web SystemのAPIクライアント
 * Android優先実装
 */
class Mem0ApiClient(
    private val baseUrl: String,
    private val authToken: String
) {
    private val client = OkHttpClient()
    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    /**
     * ユーザープロファイルを取得
     */
    suspend fun getUserProfile(): Result<JSONObject> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/api/v1/user/profile")
                .addHeader("Authorization", "Bearer $authToken")
                .get()
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()

            if (response.isSuccessful && responseBody != null) {
                Result.success(JSONObject(responseBody))
            } else {
                Result.failure(IOException("API呼び出しに失敗しました: ${response.code}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * メモリを検索
     */
    suspend fun searchMemories(
        query: String,
        searchType: String,
        userId: String,
        scope: String = "personal",
        limit: Int = 10,
        offset: Int = 0
    ): Result<JSONArray> = withContext(Dispatchers.IO) {
        try {
            val jsonBody = JSONObject().apply {
                put("query", query)
                put("search_type", searchType)
                put("user_id", userId)
                put("scope", scope)
                put("limit", limit)
                put("offset", offset)
            }

            val requestBody = jsonBody.toString().toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/api/v1/search")
                .addHeader("Authorization", "Bearer $authToken")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()

            if (response.isSuccessful && responseBody != null) {
                Result.success(JSONArray(responseBody))
            } else {
                Result.failure(IOException("API呼び出しに失敗しました: ${response.code}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * チャットメッセージを送信
     */
    suspend fun sendChatMessage(
        messages: List<Map<String, String>>,
        userId: String,
        scope: String = "personal",
        topicId: Int? = null
    ): Result<JSONObject> = withContext(Dispatchers.IO) {
        try {
            val messagesArray = JSONArray()
            messages.forEach { message ->
                val messageObj = JSONObject()
                messageObj.put("role", message["role"])
                messageObj.put("content", message["content"])
                message["image_url"]?.let { messageObj.put("image_url", it) }
                messagesArray.put(messageObj)
            }

            val jsonBody = JSONObject().apply {
                put("messages", messagesArray)
                put("user_id", userId)
                put("scope", scope)
                topicId?.let { put("topic_id", it) }
            }

            val requestBody = jsonBody.toString().toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/api/v1/chat")
                .addHeader("Authorization", "Bearer $authToken")
                .post(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()

            if (response.isSuccessful && responseBody != null) {
                Result.success(JSONObject(responseBody))
            } else {
                Result.failure(IOException("API呼び出しに失敗しました: ${response.code}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * ユーザー設定を取得
     */
    suspend fun getUserSettings(): Result<JSONObject> = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url("$baseUrl/settings")
                .addHeader("Authorization", "Bearer $authToken")
                .get()
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()

            if (response.isSuccessful && responseBody != null) {
                Result.success(JSONObject(responseBody))
            } else {
                Result.failure(IOException("API呼び出しに失敗しました: ${response.code}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * ユーザー設定を更新
     */
    suspend fun updateUserSettings(settings: Map<String, Any>): Result<JSONObject> = withContext(Dispatchers.IO) {
        try {
            val jsonBody = JSONObject(settings)
            val requestBody = jsonBody.toString().toRequestBody(jsonMediaType)

            val request = Request.Builder()
                .url("$baseUrl/settings")
                .addHeader("Authorization", "Bearer $authToken")
                .put(requestBody)
                .build()

            val response = client.newCall(request).execute()
            val responseBody = response.body?.string()

            if (response.isSuccessful && responseBody != null) {
                Result.success(JSONObject(responseBody))
            } else {
                Result.failure(IOException("API呼び出しに失敗しました: ${response.code}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
