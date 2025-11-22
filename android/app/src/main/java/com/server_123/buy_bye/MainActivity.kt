package com.server_123.buy_bye

import android.Manifest
import android.os.Build
import android.os.Bundle
import android.util.Log
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import android.content.pm.PackageManager
import android.provider.Settings
import android.app.AlertDialog
import android.content.Intent
import android.net.Uri

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private var isAccessibilityDialogShowing = false;

    private val accessibilitySettingsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) {
        isAccessibilityDialogShowing = false

        checkAccessibilityService()
    }

    private val requestPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted: Boolean ->
            if (isGranted) {
                checkAccessibilityService()
            } else {
                showPermissionDeniedDialog()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.main_webview)

        webView.settings.javaScriptEnabled = true
        webView.webViewClient = WebViewClient()
        webView.loadUrl("https://x-thon.nexcode.kr/")

        checkNotificationPermission()
    }

    override fun onResume() {
        super.onResume()
        if (::webView.isInitialized) {
            webView.reload()
            Log.d("WebView", "App resumed, content reloaded automatically.")
        }
        checkAccessibilityService()
    }

    private fun checkNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            when {
                ContextCompat.checkSelfPermission(
                    this,
                    Manifest.permission.POST_NOTIFICATIONS
                ) == PackageManager.PERMISSION_GRANTED -> {
                    checkAccessibilityService()
                }
                shouldShowRequestPermissionRationale(Manifest.permission.POST_NOTIFICATIONS) -> {
                    showNotificationRationale()
                }
                else -> {
                    requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
            }
        } else {
            checkAccessibilityService()
        }
    }

    private fun isAccessibilityServiceEnabled(): Boolean {
        val expectedServiceName = packageName + "/" + MyAccessibilityService::class.java.name

        val settingValue = Settings.Secure.getString(
            contentResolver,
            Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
        )

        val cleanedSettingValue = settingValue?.replace("\\s".toRegex(), "")

        return cleanedSettingValue?.contains(expectedServiceName) == true
    }

    private fun checkAccessibilityService() {
        val isEnabled = isAccessibilityServiceEnabled()

        if (!isAccessibilityServiceEnabled()) {
            if(!isAccessibilityDialogShowing) {
                showAccessibilityServiceDialog()
                isAccessibilityDialogShowing = true
            }
            else {
                isAccessibilityDialogShowing = false
            }
        }
    }

    private fun showNotificationRationale() {
        AlertDialog.Builder(this)
            .setTitle("알림 권한 필수")
            .setMessage("이 앱은 알림을 보내기 위해 알림 권한이 반드시 필요합니다.")
            .setPositiveButton("확인") { _, _ ->
                requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
            .setNegativeButton("취소") { dialog, _ ->
                dialog.dismiss()
                showPermissionDeniedDialog()
            }
            .show()
    }

    private fun showAccessibilityServiceDialog() {
        AlertDialog.Builder(this)
            .setTitle("접근성 권한 필수")
            .setMessage("서비스를 이용하기 위해 접근성 권한이 필요합니다.\n\n[설정]으로 이동하여 앱 이름을 찾고 활성화해주세요.")
            .setCancelable(false)
            .setPositiveButton("설정으로 이동") { _, _ ->
                val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                accessibilitySettingsLauncher.launch(intent)
            }
            .setNegativeButton("취소") { dialog, which ->
                isAccessibilityDialogShowing = false
                dialog.dismiss()
            }
            .show()
    }

    private fun showPermissionDeniedDialog() {
        AlertDialog.Builder(this)
            .setTitle("권한 부족")
            .setMessage("알림 기능을 사용할 수 없습니다. 앱의 모든 기능을 위해 권한을 허용해주세요.")
            .setPositiveButton("앱 설정으로 이동") { dialog, _ ->
                val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                val uri = Uri.fromParts("package", packageName, null)
                intent.data = uri
                startActivity(intent)
            }
            .setNegativeButton("닫기") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
}