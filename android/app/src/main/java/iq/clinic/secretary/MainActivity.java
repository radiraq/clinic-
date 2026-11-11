package iq.clinic.secretary;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {
    static final String BASE = "https://radiraq.github.io/clinic-/test/";
    private WebView web;
    private SharedPreferences prefs;

    @SuppressLint({"SetJavaScriptEnabled", "AddJavascriptInterface"})
    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        prefs = getSharedPreferences("app", MODE_PRIVATE);
        Bell.channels(this);
        getWindow().setStatusBarColor(Color.parseColor("#101a28"));
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#101a28"));
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setCacheMode(WebSettings.LOAD_DEFAULT);
        web.addJavascriptInterface(new Bridge(), "AndroidBell");
        web.setWebChromeClient(new WebChromeClient());
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                if ("radiraq.github.io".equals(u.getHost())) return false;
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception ignored) {}
                return true;
            }
        });
        setContentView(web);
        askPermissions();
        String clinic = prefs.getString("clinic", null);
        if (clinic == null) chooseClinic(); else open(clinic);
    }

    private void open(String clinic) {
        BellService.start(this);
        web.loadUrl(BASE + ("karma".equals(clinic) ? "secretary-karma-test.html" : "secretary-test.html"));
    }

    private void chooseClinic() {
        new AlertDialog.Builder(this)
                .setTitle("اختاري العيادة")
                .setItems(new String[]{"عيادة الفلوجة", "عيادة الكرمة"}, (d, w) -> {
                    String c = w == 1 ? "karma" : "fallujah";
                    prefs.edit().putString("clinic", c).apply();
                    open(c);
                })
                .setCancelable(false).show();
    }

    private void askPermissions() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED)
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 1);
        try {
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            if (!pm.isIgnoringBatteryOptimizations(getPackageName())) {
                Intent i = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
                i.setData(Uri.parse("package:" + getPackageName()));
                startActivity(i);
            }
        } catch (Exception ignored) {}
    }

    // Keep the page running in the background: never pause the WebView here.
    @Override protected void onPause() { super.onPause(); }

    @SuppressWarnings("deprecation")
    @Override public void onBackPressed() {
        if (web.canGoBack()) { web.goBack(); return; }
        new AlertDialog.Builder(this)
                .setItems(new String[]{"إخفاء البرنامج (التنبيهات تبقى شغالة)", "تغيير العيادة", "إيقاف البرنامج والتنبيهات"}, (d, w) -> {
                    if (w == 0) moveTaskToBack(true);
                    else if (w == 1) chooseClinic();
                    else { stopService(new Intent(this, BellService.class)); finishAndRemoveTask(); }
                }).show();
    }

    final class Bridge {
        @JavascriptInterface public void alert(String text) { Bell.ring(MainActivity.this, text == null ? "تنبيه جديد" : text); }
        @JavascriptInterface public boolean isApp() { return true; }
    }
}
