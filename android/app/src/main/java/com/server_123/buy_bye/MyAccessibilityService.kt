package com.server_123.buy_bye

import android.accessibilityservice.AccessibilityService
import android.app.AlarmManager
import android.app.Notification
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.SystemClock
import android.util.Log
import android.view.accessibility.AccessibilityEvent
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.Calendar
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MyAccessibilityService : AccessibilityService() {
    private val client = OkHttpClient()
    private val SERVER_URL = "https://x-thon.nexcode.kr:16010/debug"

    override fun onServiceConnected() {
        super.onServiceConnected()

        val expectedName = packageName + "/" + MyAccessibilityService::class.java.simpleName
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event?.eventType == AccessibilityEvent.TYPE_NOTIFICATION_STATE_CHANGED) {
            val packageName = event.packageName?.toString() ?: "UnknownApp"

            var notificationText = event.text.joinToString(" ")

            if (notificationText.isBlank() && event.parcelableData is Notification) {
                val notification = event.parcelableData as Notification
                val extras = notification.extras

                val title = extras.getString(Notification.EXTRA_TITLE)?.trim() ?: ""
                val text = extras.getString(Notification.EXTRA_TEXT)?.trim() ?: ""
                val subText = extras.getString(Notification.EXTRA_SUB_TEXT)?.trim() ?: ""
                val bigText = extras.getString(Notification.EXTRA_BIG_TEXT)?.trim() ?: ""

                notificationText = "$title $text $subText $bigText".trim()
            }

            Log.d("NOTI_RAW", "[App: $packageName] Raw Notification: $notificationText")

            // 결제 관련 알림인지 필터링
            if (notificationText.contains("원") && notificationText.contains("출금")) {

                Log.d("Scraping", "결제 알림 감지: $notificationText")

                val amount = extractAmount(notificationText)
                val merchant = extractMerchant(notificationText)

                val eventUptime = event.eventTime
                val currentUptime = SystemClock.uptimeMillis()
                val currentTimeEpoch = System.currentTimeMillis()

                val actualEpochTime = currentTimeEpoch - (currentUptime - eventUptime)

                val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
                val timestamp = dateFormat.format(Date(actualEpochTime))

                if (amount != "0") {
                    sendToServer(amount, merchant, timestamp)
                    scheduleNotification(merchant)
                }
            }
        }
    }

    // 금액 추출 함수
    private fun extractAmount(text: String): String {
        val regex = "(\\d[\\d,]+)원".toRegex()
        val match = regex.find(text)
        return match?.groups?.get(1)?.value?.replace(",", "") ?: "0"
    }

    // 가맹점 추출 함수
    private fun extractMerchant(text: String): String {
        val regex = "→\\s*(.*)".toRegex()
        val match = regex.find(text)
        return match?.groups?.get(1)?.value?.trim() ?: "기타"
    }

    // 서버 전송 함수
    private fun sendToServer(amount: String, merchant: String, timestamp: String) {
        val json = JSONObject()
        json.put("amount", amount)
        json.put("merchant", merchant)
        json.put("timestamp", timestamp)

        val body = json.toString().toRequestBody("application/json; charset=utf-8".toMediaType())

        val request = Request.Builder()
            .url(SERVER_URL)
            .post(body)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                Log.e("APIPOST", "전송 실패: ${e.message}")
            }
            override fun onResponse(call: Call, response: Response) {
                Log.d("APIPOST", "전송 성공: ${response.body?.string()}")
            }
        })
    }

    // 1시간 알림 예약 함수 (테스트용 10초)
    private fun scheduleNotification(merchant: String) {
        val alarmManager = getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val intent = Intent(this, AlarmReceiver::class.java).apply {
            putExtra("merchant", merchant)
        }

        val pendingIntent = PendingIntent.getBroadcast(
            this, System.currentTimeMillis().toInt(), intent, PendingIntent.FLAG_IMMUTABLE
        )

        // 테스트용: 10초 후 (실제 배포 시 1시간으로 변경하려면 10 * 1000 대신 60 * 60 * 1000 사용)
        val triggerTime = Calendar.getInstance().timeInMillis + (10 * 1000)

        try {
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                triggerTime,
                pendingIntent
            )
            Log.d("Alarm", "정확한 알람 예약 완료: 10초 후 $merchant 알림")
        } catch (e: SecurityException) {
            alarmManager.set(AlarmManager.RTC_WAKEUP, triggerTime, pendingIntent)
            Log.e("Alarm", "알람 예약 중 SecurityException 발생. 일반 set 사용.")
        }
    }

    override fun onInterrupt() {}
}