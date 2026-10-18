#!/usr/bin/env python3
"""Apply the Android background-download overlay to the unpacked app source."""
from pathlib import Path
import shutil
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "HorizonAndroidPrep")
app = root / "app" / "src" / "main"
manifest = app / "AndroidManifest.xml"
activity = app / "java" / "dev" / "horizon" / "androidprep" / "MainActivity.java"
gradle = root / "app" / "build.gradle"
overlay = Path("android-overlay") / "DownloadNotificationService.java"
service_target = app / "java" / "dev" / "horizon" / "androidprep" / "DownloadNotificationService.java"

for path in (manifest, activity, gradle, overlay):
    if not path.is_file():
        raise SystemExit(f"Required source file is missing: {path}")

def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match in {path} for {old[:90]!r}, found {count}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")

service_target.parent.mkdir(parents=True, exist_ok=True)
shutil.copyfile(overlay, service_target)

replace_once(
    manifest,
    '    <uses-permission android:name="android.permission.INTERNET" />',
    '    <uses-permission android:name="android.permission.INTERNET" />\n'
    '    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />\n'
    '    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />\n'
    '    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />'
)
replace_once(
    manifest,
    '    </application>\n</manifest>',
    '        <service\n'
    '            android:name=".DownloadNotificationService"\n'
    '            android:exported="false"\n'
    '            android:foregroundServiceType="dataSync" />\n'
    '    </application>\n</manifest>'
)

replace_once(
    activity,
    '    private static final int PICK_PREPARED_RESOURCE_TREE = 1004;\n',
    '    private static final int PICK_PREPARED_RESOURCE_TREE = 1004;\n'
    '    private static final int REQUEST_DOWNLOAD_NOTIFICATION_PERMISSION = 1105;\n'
)
replace_once(
    activity,
    '    private boolean installInProgress;\n',
    '    private boolean installInProgress;\n'
    '    private boolean pendingAllAssets;\n'
)

original_signature = '    private void startOfficialDownload(boolean allAssets) {\n'
wrapper = '''    private void startOfficialDownload(boolean allAssets) {
        if (android.os.Build.VERSION.SDK_INT >= 33
                && checkSelfPermission("android.permission.POST_NOTIFICATIONS")
                != android.content.pm.PackageManager.PERMISSION_GRANTED) {
            pendingAllAssets = allAssets;
            setStatus("Permissão de notificação", "O app precisa de permissão para mostrar o progresso do download na gaveta de notificações. O download começará após sua resposta.");
            requestPermissions(
                    new String[] {"android.permission.POST_NOTIFICATIONS"},
                    REQUEST_DOWNLOAD_NOTIFICATION_PERMISSION);
            return;
        }
        startOfficialDownloadNow(allAssets);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_DOWNLOAD_NOTIFICATION_PERMISSION) {
            if (grantResults.length == 0
                    || grantResults[0] != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                setStatus("Notificações desativadas", "O download continuará, mas o Android pode ocultar a notificação da gaveta. Você ainda poderá acompanhar o estado dentro do app.");
            }
            startOfficialDownloadNow(pendingAllAssets);
        }
    }

    private void startOfficialDownloadNow(boolean allAssets) {
'''
replace_once(activity, original_signature, wrapper)

replace_once(
    activity,
    '        installInProgress = true;\n',
    '        installInProgress = true;\n'
    '        DownloadNotificationService.begin(this, "Download Minecraft Java 26.3", "Preparando o download dos arquivos oficiais.");\n'
)

replace_once(
    activity,
    '''    private void setStatus(String title, String details) {
        runOnUiThread(() -> {
            if (statusView != null) statusView.setText(title);
            if (detailView != null) detailView.setText(details);
        });
    }''',
    '''    private void setStatus(String title, String details) {
        runOnUiThread(() -> {
            if (statusView != null) statusView.setText(title);
            if (detailView != null) detailView.setText(details);
            if (DownloadNotificationService.isActive()) {
                if ("Download oficial concluído".equals(title)
                        || "Falha no download oficial".equals(title)) {
                    DownloadNotificationService.finish(this, title, details);
                } else {
                    DownloadNotificationService.update(this, title, details);
                }
            }
        });
    }'''
)

replace_once(
    activity,
    'text("Preparador Android · versão 0.9.7", 15, Color.rgb(159, 177, 210), false)',
    'text("Downloads em segundo plano · versão 0.9.8", 15, Color.rgb(159, 177, 210), false)'
)

replace_once(
    activity,
    '''        TextView warning = text(
                "A opção 1 baixa o manifesto e os arquivos oficiais de Minecraft 26.3, sem precisar " +
                "copiar arquivos de um PC. A opção 2 também baixa o catálogo completo de assets, " +
                "o que pode ocupar centenas de MB. Os arquivos são guardados no armazenamento privado do app.", 14, Color.rgb(205, 211, 226), false);''',
    '''        TextView warning = text(
                "A opção 1 baixa o manifesto e os arquivos oficiais de Minecraft 26.3, sem precisar " +
                "copiar arquivos de um PC. Os downloads podem continuar em segundo plano com notificação de progresso e conclusão. " +
                "A opção 2 também baixa o catálogo completo de assets, que pode ocupar centenas de MB. " +
                "Os recursos preparados do Horizon ainda precisam ser importados separadamente.", 14, Color.rgb(205, 211, 226), false);'''
)

replace_once(gradle, "    versionCode 15\n", "    versionCode 16\n")
replace_once(gradle, "    versionName '0.9.7'\n", "    versionName '0.9.8'\n")

print("Applied Android background-download notifications.")
print(f"Activity: {activity}")
print(f"Manifest: {manifest}")
print(f"Foreground service: {service_target}")
