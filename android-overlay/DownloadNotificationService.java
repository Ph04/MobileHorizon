package dev.horizon.androidprep;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;

import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Keeps official Minecraft file downloads alive while MainActivity is in the background and
 * exposes progress/completion in the Android notification shade. The actual download remains
 * performed by OfficialMinecraftInstaller, which verifies official SHA-1 pins.
 */
public final class DownloadNotificationService extends Service {
    private static final String CHANNEL_ID = "horizon_downloads";
    private static final int NOTIFICATION_ID = 9306;

    private static final String ACTION_BEGIN = "dev.horizon.androidprep.download.BEGIN";
    private static final String ACTION_UPDATE = "dev.horizon.androidprep.download.UPDATE";
    private static final String ACTION_FINISH = "dev.horizon.androidprep.download.FINISH";
    private static final String EXTRA_TITLE = "title";
    private static final String EXTRA_DETAILS = "details";

    private static final Pattern PROGRESS_PATTERN =
            Pattern.compile("(\\d+)\\s*(?:/|de)\\s*(\\d+)", Pattern.CASE_INSENSITIVE);

    private static volatile boolean active;

    private NotificationManager notificationManager;
    private boolean foregroundStarted;
    private String lastTitle = "Download Minecraft 26.3";
    private String lastDetails = "Preparando os arquivos oficiais.";

    public static boolean isActive() {
        return active;
    }

    public static void begin(Context context, String title, String details) {
        active = true;
        Intent intent = action(context, ACTION_BEGIN, title, details);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.startForegroundService(intent);
        } else {
            context.startService(intent);
        }
    }

    public static void update(Context context, String title, String details) {
        if (!active) return;
        context.startService(action(context, ACTION_UPDATE, title, details));
    }

    public static void finish(Context context, String title, String details) {
        if (!active) return;
        active = false;
        context.startService(action(context, ACTION_FINISH, title, details));
    }

    private static Intent action(Context context, String action, String title, String details) {
        Intent intent = new Intent(context, DownloadNotificationService.class);
        intent.setAction(action);
        intent.putExtra(EXTRA_TITLE, title);
        intent.putExtra(EXTRA_DETAILS, details);
        return intent;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        notificationManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
        createNotificationChannel();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent == null ? ACTION_BEGIN : intent.getAction();
        if (intent != null) {
            String title = intent.getStringExtra(EXTRA_TITLE);
            String details = intent.getStringExtra(EXTRA_DETAILS);
            if (title != null && !title.trim().isEmpty()) lastTitle = title;
            if (details != null) lastDetails = details;
        }

        if (ACTION_FINISH.equals(action)) {
            boolean failed = lastTitle.toLowerCase(Locale.ROOT).contains("falha");
            Notification finalNotification = buildNotification(lastTitle, lastDetails, false);
            notificationManager.notify(NOTIFICATION_ID, finalNotification);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                stopForeground(STOP_FOREGROUND_DETACH);
            } else {
                stopForeground(false);
            }
            foregroundStarted = false;
            active = false;
            stopSelf(startId);
            return START_NOT_STICKY;
        }

        if (ACTION_BEGIN.equals(action) || !foregroundStarted) {
            Notification notification = buildNotification(lastTitle, lastDetails, true);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC);
            } else {
                startForeground(NOTIFICATION_ID, notification);
            }
            foregroundStarted = true;
            active = true;
        } else if (ACTION_UPDATE.equals(action)) {
            notificationManager.notify(NOTIFICATION_ID, buildNotification(lastTitle, lastDetails, true));
        }

        return START_NOT_STICKY;
    }

    private Notification buildNotification(String title, String details, boolean ongoing) {
        boolean failed = title.toLowerCase(Locale.ROOT).contains("falha");
        boolean completed = !ongoing && !failed;
        int icon = ongoing
                ? android.R.drawable.stat_sys_download
                : (failed ? android.R.drawable.stat_notify_error : android.R.drawable.stat_sys_download_done);

        Intent openApp = new Intent(this, MainActivity.class);
        openApp.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP | Intent.FLAG_ACTIVITY_CLEAR_TOP);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this,
                NOTIFICATION_ID,
                openApp,
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        );

        String displayText = firstLine(details);
        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(this, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }

        builder.setSmallIcon(icon)
                .setContentTitle(title)
                .setContentText(displayText)
                .setStyle(new Notification.BigTextStyle().bigText(details == null ? displayText : details))
                .setContentIntent(pendingIntent)
                .setCategory(ongoing ? Notification.CATEGORY_PROGRESS : Notification.CATEGORY_STATUS)
                .setOnlyAlertOnce(true)
                .setOngoing(ongoing)
                .setAutoCancel(!ongoing)
                .setPriority(ongoing ? Notification.PRIORITY_LOW : Notification.PRIORITY_DEFAULT);

        if (ongoing) {
            Matcher matcher = PROGRESS_PATTERN.matcher(details == null ? "" : details);
            if (matcher.find()) {
                try {
                    long current = Long.parseLong(matcher.group(1));
                    long total = Long.parseLong(matcher.group(2));
                    if (total > 0) {
                        int percent = (int) Math.max(0, Math.min(100, (current * 100L) / total));
                        builder.setProgress(100, percent, false);
                        builder.setContentText(percent + "% · " + displayText);
                    } else {
                        builder.setProgress(0, 0, true);
                    }
                } catch (NumberFormatException ignored) {
                    builder.setProgress(0, 0, true);
                }
            } else {
                builder.setProgress(0, 0, true);
            }
        } else {
            builder.setProgress(0, 0, false);
        }

        return builder.build();
    }

    private String firstLine(String text) {
        if (text == null || text.trim().isEmpty()) return "Acompanhe o andamento do download.";
        String line = text.split("\\n", 2)[0].trim();
        if (line.length() > 140) line = line.substring(0, 137) + "...";
        return line;
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return;
        NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID,
                "Downloads do Horizon",
                NotificationManager.IMPORTANCE_LOW
        );
        channel.setDescription("Progresso e conclusão do download dos arquivos oficiais do Minecraft.");
        channel.setShowBadge(false);
        notificationManager.createNotificationChannel(channel);
    }

    @Override
    public void onDestroy() {
        active = false;
        foregroundStarted = false;
        super.onDestroy();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}