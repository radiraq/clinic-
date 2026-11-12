package iq.clinic.secretary;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.os.Build;
import android.os.PowerManager;
import android.os.VibrationEffect;
import android.os.Vibrator;

/** One loud bell + a lock-screen notification for each doctor/writer alert. */
final class Bell {
    static final String ALERTS = "alerts_v1";
    static final String SERVICE = "service_v1";
    private static int nextId = 100;
    private static MediaPlayer player;

    static void channels(Context c) {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        NotificationChannel a = new NotificationChannel(ALERTS, "تنبيهات الطبيب", NotificationManager.IMPORTANCE_HIGH);
        a.setDescription("تنبيه الطبيب والكاتبة");
        a.setSound(null, null); // the app plays its own loud bell on the alarm volume
        a.enableVibration(true);
        a.setVibrationPattern(new long[]{0, 400, 150, 400});
        a.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
        a.setBypassDnd(true);
        nm.createNotificationChannel(a);
        NotificationChannel s = new NotificationChannel(SERVICE, "تشغيل البرنامج", NotificationManager.IMPORTANCE_LOW);
        s.setShowBadge(false);
        nm.createNotificationChannel(s);
    }

    static void ring(Context ctx, String text) { ring(ctx, text, R.raw.bell); }

    static void ring(Context ctx, String text, int sound) {
        Context c = ctx.getApplicationContext();
        channels(c);
        // Wake the screen briefly so the alert is seen.
        try {
            PowerManager pm = (PowerManager) c.getSystemService(Context.POWER_SERVICE);
            @SuppressWarnings("deprecation")
            PowerManager.WakeLock wl = pm.newWakeLock(PowerManager.SCREEN_BRIGHT_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP, "clinic:alert");
            wl.acquire(6000);
        } catch (Exception ignored) {}
        // Loud bell on the alarm stream: rings even when the phone is on silent.
        try {
            synchronized (Bell.class) {
                if (player != null) { try { player.release(); } catch (Exception ignored) {} }
                player = new MediaPlayer();
                player.setAudioAttributes(new AudioAttributes.Builder()
                        .setUsage(AudioAttributes.USAGE_ALARM)
                        .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION).build());
                player.setDataSource(c, android.net.Uri.parse("android.resource://" + c.getPackageName() + "/" + sound));
                player.setOnCompletionListener(MediaPlayer::release);
                player.prepare();
                player.start();
            }
        } catch (Exception ignored) {}
        try {
            Vibrator v = (Vibrator) c.getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null) {
                if (Build.VERSION.SDK_INT >= 26) v.vibrate(VibrationEffect.createWaveform(new long[]{0, 400, 150, 400}, -1));
                else v.vibrate(new long[]{0, 400, 150, 400}, -1);
            }
        } catch (Exception ignored) {}
        Intent open = new Intent(c, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pi = PendingIntent.getActivity(c, 1, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification.Builder b = Build.VERSION.SDK_INT >= 26 ? new Notification.Builder(c, ALERTS) : new Notification.Builder(c);
        b.setSmallIcon(android.R.drawable.ic_popup_reminder)
                .setContentTitle("🔔 " + text)
                .setContentText("اضغطي لفتح شاشة السكرتارية")
                .setStyle(new Notification.BigTextStyle().bigText(text))
                .setCategory(Notification.CATEGORY_ALARM)
                .setVisibility(Notification.VISIBILITY_PUBLIC)
                .setPriority(Notification.PRIORITY_MAX)
                .setAutoCancel(true)
                .setContentIntent(pi)
                .setFullScreenIntent(pi, true);
        try {
            NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
            nm.notify(nextId++, b.build());
        } catch (Exception ignored) {}
    }
}
