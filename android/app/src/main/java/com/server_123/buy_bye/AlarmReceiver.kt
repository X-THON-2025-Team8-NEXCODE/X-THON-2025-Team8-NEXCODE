package com.server_123.buy_bye

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.app.NotificationManager
import android.app.NotificationChannel
import android.app.PendingIntent
import android.os.Build
import androidx.core.app.NotificationCompat
import android.util.Log

class AlarmReceiver : BroadcastReceiver() {
    private val CHANNEL_ID = "hour_regret_channel"
    private val NOTIFICATION_ID = 101

    override fun onReceive(context: Context, intent: Intent) {
        val merchant = intent.getStringExtra("merchant") ?: "이전 지출"
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        createNotificationChannel(notificationManager)

        val appIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }

        val pendingIntent: PendingIntent = PendingIntent.getActivity(
            context,
            0,
            appIntent,
            PendingIntent.FLAG_IMMUTABLE
        )

        // 3. 알림 콘텐츠 정의
        val notification = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("💸 1시간 전 지출 알림")
            .setContentText("$merchant 결제한 지 1시간 지났어요! 이번 소비는 만족스러웠나요?")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)

            .setContentIntent(pendingIntent)

            .build()

        // 5. 알림 표시
        notificationManager.notify(NOTIFICATION_ID, notification)
        Log.d("AlarmReceiver", "후회 알림 표시 완료: $merchant")
    }

    private fun createNotificationChannel(notificationManager: NotificationManager) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channelName = "후회 알림 채널"
            val importance = NotificationManager.IMPORTANCE_HIGH

            val channel = NotificationChannel(CHANNEL_ID, channelName, importance)
            notificationManager.createNotificationChannel(channel)
        }
    }
}