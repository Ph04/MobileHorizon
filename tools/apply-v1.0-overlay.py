#!/usr/bin/env python3
"""Apply the Horizon Android 1.0.0 UI, import-progress and native-preflight overlay."""
from pathlib import Path
import shutil
import sys

repo = Path(".")
root = Path(sys.argv[1] if len(sys.argv) > 1 else "HorizonAndroidPrep")
activity = root / "app/src/main/java/dev/horizon/androidprep/MainActivity.java"
gradle = root / "app/build.gradle"
bridge_src = repo / "android-overlay/nativeprep/NativePreparationBridge.java"
bridge_dst = root / "app/src/main/java/dev/horizon/androidprep/NativePreparationBridge.java"

for path in (activity, gradle, bridge_src):
    if not path.is_file():
        raise SystemExit(f"Required file is missing: {path}")

s = activity.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    s = s.replace(old, new, 1)

def replace_method(start_anchor: str, end_anchor: str, replacement: str, label: str) -> None:
    global s
    start = s.find(start_anchor)
    if start < 0:
        raise SystemExit(f"{label}: start anchor not found")
    end = s.find(end_anchor, start + len(start_anchor))
    if end < 0:
        raise SystemExit(f"{label}: end anchor not found")
    s = s[:start] + replacement.rstrip() + "\n\n" + s[end:]

replace_once(
    "import android.widget.LinearLayout;\n",
    "import android.widget.LinearLayout;\nimport android.widget.ProgressBar;\n",
    "progress bar import")
replace_once(
    "    private TextView detailView;\n",
    "    private TextView detailView;\n    private TextView importProgressLabel;\n    private ProgressBar importProgressBar;\n",
    "import progress fields")

NEW_UI = r"""
    private void buildUi() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);

        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(22), dp(24), dp(22), dp(28));
        root.setBackgroundColor(Color.rgb(14, 18, 28));
        scroll.addView(root);

        TextView title = text("HORIZON", 32, Color.WHITE, true);
        root.addView(title);

        TextView subtitle = text("Minecraft Java 26.3 · Preparador Android 1.0.0", 14,
                Color.rgb(157, 178, 216), false);
        LinearLayout.LayoutParams subParams = params(-1, -2);
        subParams.bottomMargin = dp(20);
        root.addView(subtitle, subParams);

        sectionHeading(root, "ARQUIVOS DO JOGO");
        addButton(root, "Baixar Minecraft 26.3", v -> startOfficialDownload(false));
        addButton(root, "Baixar também todos os assets", v -> confirmFullAssetDownload());
        addButton(root, "Mais opções de importação…", v -> showImportOptions());

        sectionHeading(root, "RECURSOS HORIZON");
        addButton(root, "Importar pasta de recursos preparada", v -> pickPreparedResourceTree());
        validateButton = addButton(root, "Verificar arquivos · diagnóstico nativo", v -> validateFiles());
        validateButton.setEnabled(true);
        addButton(root, "Abrir Horizon", v -> openNativeClient());

        TextView nativeNotice = text(
                "PREPARADOR NATIVO · FASE 1\n" +
                "A ponte ARM64 já verifica os arquivos de entrada. A geração completa de recursos ainda está em desenvolvimento; por enquanto, importe a pasta 26.3 que você já preparou para testar o cliente.",
                13, Color.rgb(188, 201, 223), false);
        nativeNotice.setPadding(dp(12), dp(12), dp(12), dp(12));
        android.graphics.drawable.GradientDrawable noticeBg = new android.graphics.drawable.GradientDrawable();
        noticeBg.setColor(Color.rgb(27, 35, 51));
        noticeBg.setCornerRadius(dp(12));
        nativeNotice.setBackground(noticeBg);
        LinearLayout.LayoutParams noticeParams = params(-1, -2);
        noticeParams.topMargin = dp(8);
        noticeParams.bottomMargin = dp(18);
        root.addView(nativeNotice, noticeParams);

        sectionHeading(root, "STATUS DA OPERAÇÃO");
        statusView = text("Aguardando ação.", 17, Color.WHITE, true);
        statusView.setPadding(0, dp(6), 0, dp(6));
        root.addView(statusView);

        detailView = text(
                "Os arquivos são processados localmente. A importação da pasta preparada continua disponível para testar os recursos já gerados.",
                13, Color.rgb(190, 199, 216), false);
        detailView.setTextIsSelectable(true);
        root.addView(detailView);

        importProgressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        importProgressBar.setMax(100);
        importProgressBar.setProgress(0);
        LinearLayout.LayoutParams progressParams = params(-1, dp(8));
        progressParams.topMargin = dp(14);
        root.addView(importProgressBar, progressParams);

        importProgressLabel = text("Importação: aguardando seleção da pasta.", 12,
                Color.rgb(145, 166, 206), false);
        LinearLayout.LayoutParams labelParams = params(-1, -2);
        labelParams.topMargin = dp(7);
        root.addView(importProgressLabel, labelParams);

        setContentView(scroll);
    }

    private void sectionHeading(LinearLayout parent, String value) {
        TextView heading = text(value, 11, Color.rgb(111, 151, 239), true);
        LinearLayout.LayoutParams lp = params(-1, -2);
        lp.topMargin = dp(12);
        lp.bottomMargin = dp(7);
        parent.addView(heading, lp);
    }

    private void showImportOptions() {
        final String[] choices = new String[] {
                "Importar pasta .minecraft",
                "Importar ZIP de uma instalação",
                "Importar server.jar separado"
        };
        new AlertDialog.Builder(this)
                .setTitle("Mais opções de importação")
                .setItems(choices, (dialog, which) -> {
                    if (which == 0) pickMinecraftTree();
                    else if (which == 1) pickMinecraftZip();
                    else if (which == 2) pickServerJar();
                })
                .setNegativeButton("Cancelar", null)
                .show();
    }
"""
replace_method("    private void buildUi() {", "    private TextView text(", NEW_UI, "compact main UI")

replace_once(
    '    private Button addButton(LinearLayout parent, String label, View.OnClickListener click) {\n        Button button = new Button(this);\n        button.setText(label);\n        button.setAllCaps(false);\n        button.setTextSize(15);\n',
    '    private Button addButton(LinearLayout parent, String label, View.OnClickListener click) {\n        Button button = new Button(this);\n        button.setText(label);\n        button.setAllCaps(false);\n        button.setTextSize(14);\n        button.setTextColor(Color.WHITE);\n        button.setBackgroundTintList(android.content.res.ColorStateList.valueOf(Color.rgb(40, 57, 91)));\n        button.setPadding(dp(12), dp(8), dp(12), dp(8));\n',
    "style buttons")

replace_once(
    'setStatus("Validação concluída", validateSummary(true));',
    'setStatus("Validação concluída", validateSummary(true) + nativePreparationSummary());',
    "append native preflight report")

NATIVE_SUMMARY = r"""
    private String nativePreparationSummary() {
        try {
            JSONObject probe = new JSONObject(NativePreparationBridge.inspectMinecraftRoot(minecraftRoot.getCanonicalPath()));
            return "\n\nPreparador nativo (fase 1)" +
                    "\nPonte ARM64: " + probe.optString("bridge_status", "sem estado") +
                    "\nEntradas encontradas: " + probe.optInt("present_inputs", 0) + "/" + probe.optInt("expected_inputs", 6) +
                    "\nGeração completa de recursos: " + (probe.optBoolean("resource_generation", false) ? "disponível" : "ainda em desenvolvimento") +
                    "\n" + probe.optString("message", "O diagnóstico terminou.");
        } catch (Throwable e) {
            String message = e.getMessage();
            return "\n\nPreparador nativo: diagnóstico indisponível (" + e.getClass().getSimpleName() +
                    (message == null ? "" : ": " + message) + "). A importação de recursos preparados continua disponível.";
        }
    }
"""
replace_method("    private void validateFiles() {", "    private String validateSummary(", NATIVE_SUMMARY + "\n    private void validateFiles() {\n        setStatus(\"Validando arquivos…\", \"Conferindo versão, checksums e bibliotecas necessárias.\");\n        worker.execute(() -> {\n            try { setStatus(\"Validação concluída\", validateSummary(true) + nativePreparationSummary()); }\n            catch (Exception e) { setStatus(\"Validação falhou\", explain(e)); }\n        });\n    }\n\n", "native validation bridge")
# The replacement above ends just before the existing validateSummary declaration and contains one replacement copy.
# Remove any accidental duplicate old validator body if the source shape changes instead of silently producing bad Java.
if s.count("private void validateFiles()") != 1:
    raise SystemExit("Expected exactly one validateFiles method after native preflight injection")

IMPORT_METHOD = r"""
    /**
     * Imports Horizon resources produced by horizon-prepare. This remains available so the
     * Android-native client can be tested while the full resource generator is being ported.
     */
    private void importPreparedResources(Uri treeUri) {
        File staging = null;
        File backup = null;
        File destination = new File(new File(getFilesDir(), ".local/horizon-client"), "26.3");
        try {
            String rootId = DocumentsContract.getTreeDocumentId(treeUri);
            if (!treeHasFile(treeUri, rootId, "horizon-resources.json")) {
                throw new IllegalArgumentException("A pasta selecionada não contém horizon-resources.json na raiz. Selecione a pasta 26.3 gerada pelo preparador.");
            }

            setStatus("Analisando pasta preparada…", "Contando arquivos e estimando o tamanho antes de copiar.");
            setImportProgress(-1, "Analisando estrutura da pasta…", "A importação ainda não começou.");
            TreeStats stats = scanPreparedTree(treeUri, rootId, new HashSet<>(), 0);
            if (stats.files <= 0) throw new IllegalArgumentException("A pasta selecionada está vazia.");
            ImportProgress progress = new ImportProgress(stats.files, stats.bytes, stats.byteSizesKnown);
            publishImportProgress(progress, "Preparando cópia…", true);

            File parent = new File(getFilesDir(), ".local/horizon-client");
            if (!parent.isDirectory() && !parent.mkdirs()) throw new IllegalStateException("Não consegui criar a pasta privada de recursos.");
            staging = new File(parent, "26.3.importing");
            backup = new File(parent, "26.3.previous");
            deleteRecursively(staging);
            if (!staging.mkdirs()) throw new IllegalStateException("Não consegui criar a pasta temporária de importação.");

            Set<String> visited = new HashSet<>();
            int[] count = new int[] {0};
            copyPreparedTree(treeUri, rootId, "", staging, visited, count, 0, progress);

            setImportProgress(99, "Cópia concluída · validando recursos", "Arquivos copiados: " + progress.copiedFiles + "/" + stats.files +
                    "\nDados copiados: " + formatBytes(progress.copiedBytes) + "\nVerificando schema, versão e arquivos essenciais.");
            setStatus("Validando recursos importados…", "Conferindo data_version, schema e arquivos necessários antes de ativar a pasta.");

            File manifest = new File(staging, "horizon-resources.json");
            if (!manifest.isFile()) throw new IllegalStateException("A cópia terminou sem horizon-resources.json.");
            JSONObject manifestJson = new JSONObject(readText(manifest));
            if (manifestJson.optInt("data_version", -1) != HORIZON_DATA_VERSION) {
                throw new IllegalArgumentException("Os recursos não correspondem à versão de dados esperada (data_version=" + HORIZON_DATA_VERSION + "). Não instalei esses arquivos.");
            }
            if (manifestJson.optInt("schema", -1) != HORIZON_RESOURCE_SCHEMA) {
                throw new IllegalArgumentException("O schema dos recursos não corresponde à versão esperada (" + HORIZON_RESOURCE_SCHEMA + "). Não instalei esses arquivos.");
            }
            List<String> resourceIssues = preparedResourceIssues(staging);
            if (!resourceIssues.isEmpty()) {
                throw new IllegalArgumentException("Os recursos copiados não estão completos para iniciar o cliente:\n" +
                        android.text.TextUtils.join("\n", resourceIssues));
            }

            deleteRecursively(backup);
            if (destination.exists() && !destination.renameTo(backup)) {
                throw new IllegalStateException("Não consegui preservar a pasta de recursos já instalada.");
            }
            if (!staging.renameTo(destination)) {
                if (backup.exists()) backup.renameTo(destination);
                throw new IllegalStateException("Não consegui ativar os recursos copiados.");
            }
            deleteRecursively(backup);
            setImportProgress(100, "Importação concluída · 100%", "Arquivos: " + progress.copiedFiles +
                    "\nDados: " + formatBytes(progress.copiedBytes) + "\nDestino privado: .local/horizon-client/26.3");
            setStatus("Recursos Horizon importados", "Data version: " + HORIZON_DATA_VERSION +
                    "\nSchema: " + HORIZON_RESOURCE_SCHEMA +
                    "\nArquivos copiados: " + progress.copiedFiles +
                    "\nDestino privado: .local/horizon-client/26.3\n\nAgora você pode tocar em “Abrir Horizon” para testar o cliente nativo.");
        } catch (Exception e) {
            try {
                if (staging != null) deleteRecursively(staging);
                if (backup != null && backup.exists() && !destination.exists()) backup.renameTo(destination);
            } catch (Exception ignored) {
                // Preserve the original diagnostic.
            }
            setStatus("Falha ao importar recursos Horizon", explain(e));
            setImportProgress(-1, "Importação interrompida", explain(e));
        }
    }
"""
replace_method("    private void importPreparedResources(Uri treeUri) {", "    private boolean treeHasFile(", IMPORT_METHOD, "prepared resource import with progress")

PROGRESS_METHODS = r"""
    private static final class TreeStats {
        int entries;
        int files;
        long bytes;
        boolean byteSizesKnown = true;
    }

    private static final class ImportProgress {
        final int totalFiles;
        final long totalBytes;
        final boolean byteSizesKnown;
        int copiedFiles;
        long copiedBytes;
        long lastUiUpdate;
        ImportProgress(int totalFiles, long totalBytes, boolean byteSizesKnown) {
            this.totalFiles = totalFiles;
            this.totalBytes = totalBytes;
            this.byteSizesKnown = byteSizesKnown;
        }
    }

    private TreeStats scanPreparedTree(Uri treeUri, String documentId, Set<String> visited, int depth) throws Exception {
        if (depth > MAX_PREPARED_RESOURCE_DEPTH) throw new IllegalArgumentException("A pasta de recursos tem níveis demais.");
        if (!visited.add(documentId)) throw new IllegalArgumentException("O provedor retornou uma referência repetida; análise interrompida por segurança.");
        TreeStats stats = new TreeStats();
        Uri childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, documentId);
        String[] projection = new String[] {
                DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                DocumentsContract.Document.COLUMN_MIME_TYPE,
                DocumentsContract.Document.COLUMN_SIZE
        };
        try (Cursor cursor = getContentResolver().query(childrenUri, projection, null, null, null)) {
            if (cursor == null) throw new IllegalStateException("O provedor não retornou a lista de arquivos.");
            int sizeIndex = cursor.getColumnIndex(DocumentsContract.Document.COLUMN_SIZE);
            while (cursor.moveToNext()) {
                String id = cursor.getString(0);
                String name = cursor.getString(1);
                String mime = cursor.getString(2);
                if (name == null || name.isEmpty() || name.equals(".") || name.equals("..") || name.contains("/") || name.contains("\\")) continue;
                stats.entries++;
                if (stats.entries > MAX_PREPARED_RESOURCE_ENTRIES) throw new IllegalArgumentException("A pasta contém mais de " + MAX_PREPARED_RESOURCE_ENTRIES + " itens.");
                if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                    TreeStats nested = scanPreparedTree(treeUri, id, visited, depth + 1);
                    stats.entries += nested.entries;
                    stats.files += nested.files;
                    stats.bytes += nested.bytes;
                    stats.byteSizesKnown &= nested.byteSizesKnown;
                    if (stats.entries > MAX_PREPARED_RESOURCE_ENTRIES) throw new IllegalArgumentException("A pasta contém mais de " + MAX_PREPARED_RESOURCE_ENTRIES + " itens.");
                } else {
                    stats.files++;
                    if (sizeIndex < 0 || cursor.isNull(sizeIndex)) {
                        stats.byteSizesKnown = false;
                    } else {
                        stats.bytes += Math.max(0L, cursor.getLong(sizeIndex));
                    }
                }
            }
        }
        return stats;
    }

    private void publishImportProgress(ImportProgress progress, String currentPath, boolean force) {
        long now = android.os.SystemClock.uptimeMillis();
        if (!force && now - progress.lastUiUpdate < 300) return;
        progress.lastUiUpdate = now;
        int percent;
        if (progress.byteSizesKnown && progress.totalBytes > 0) {
            percent = (int) Math.min(99L, progress.copiedBytes * 100L / progress.totalBytes);
        } else if (progress.totalFiles > 0) {
            percent = (int) Math.min(99L, progress.copiedFiles * 100L / progress.totalFiles);
        } else {
            percent = 0;
        }
        String detail = "Arquivos: " + progress.copiedFiles + "/" + progress.totalFiles +
                "\nDados: " + formatBytes(progress.copiedBytes) +
                (progress.byteSizesKnown && progress.totalBytes > 0 ? " de " + formatBytes(progress.totalBytes) : "") +
                "\nAtual: " + currentPath;
        setImportProgress(percent, "Importando recursos Horizon · " + percent + "%", detail);
    }

    private void setImportProgress(int percent, String label, String detail) {
        runOnUiThread(() -> {
            if (importProgressBar != null) {
                importProgressBar.setIndeterminate(percent < 0);
                if (percent >= 0) importProgressBar.setProgress(Math.min(100, percent));
            }
            if (importProgressLabel != null) importProgressLabel.setText(label);
            if (statusView != null && label.startsWith("Importando recursos Horizon")) statusView.setText(label);
            if (detailView != null && detail != null) detailView.setText(detail);
        });
    }

    private String formatBytes(long bytes) {
        if (bytes < 1024L) return bytes + " B";
        if (bytes < 1024L * 1024L) return String.format(Locale.ROOT, "%.1f KB", bytes / 1024.0);
        return String.format(Locale.ROOT, "%.1f MB", bytes / (1024.0 * 1024.0));
    }

    private void copyPreparedTree(Uri treeUri, String documentId, String relative, File destinationRoot,
                                  Set<String> visited, int[] count, int depth, ImportProgress progress) throws Exception {
        if (depth > MAX_PREPARED_RESOURCE_DEPTH) throw new IllegalArgumentException("A pasta de recursos tem níveis demais.");
        if (!visited.add(documentId)) throw new IllegalArgumentException("O provedor de arquivos retornou uma referência repetida; importação interrompida por segurança.");
        Uri childrenUri = DocumentsContract.buildChildDocumentsUriUsingTree(treeUri, documentId);
        String[] projection = new String[] {
                DocumentsContract.Document.COLUMN_DOCUMENT_ID,
                DocumentsContract.Document.COLUMN_DISPLAY_NAME,
                DocumentsContract.Document.COLUMN_MIME_TYPE
        };
        try (Cursor cursor = getContentResolver().query(childrenUri, projection, null, null, null)) {
            if (cursor == null) throw new IllegalStateException("O provedor não retornou a lista de arquivos.");
            while (cursor.moveToNext()) {
                String id = cursor.getString(0);
                String name = cursor.getString(1);
                String mime = cursor.getString(2);
                if (name == null || name.isEmpty() || name.equals(".") || name.equals("..") || name.contains("/") || name.contains("\\")) continue;
                String child = relative.isEmpty() ? name : relative + "/" + name;
                if (!safeRelative(child)) throw new IllegalArgumentException("Caminho inseguro retornado pelo provedor: " + child);
                count[0]++;
                if (count[0] > MAX_PREPARED_RESOURCE_ENTRIES) throw new IllegalArgumentException("A pasta contém mais de " + MAX_PREPARED_RESOURCE_ENTRIES + " itens; importação cancelada.");
                if (DocumentsContract.Document.MIME_TYPE_DIR.equals(mime)) {
                    File outDir = safeFile(destinationRoot, child);
                    if (!outDir.isDirectory() && !outDir.mkdirs()) throw new IllegalStateException("Não consegui criar " + child);
                    copyPreparedTree(treeUri, id, child, destinationRoot, visited, count, depth + 1, progress);
                } else {
                    Uri fileUri = DocumentsContract.buildDocumentUriUsingTree(treeUri, id);
                    File out = safeFile(destinationRoot, child);
                    try (InputStream in = getContentResolver().openInputStream(fileUri)) {
                        if (in == null) throw new IllegalStateException("Não consegui ler " + child);
                        copyPreparedStream(in, out, progress, child);
                    }
                    progress.copiedFiles++;
                    publishImportProgress(progress, child, true);
                }
            }
        }
    }

    private void copyPreparedStream(InputStream source, File target, ImportProgress progress, String relative) throws Exception {
        File parent = target.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new IllegalStateException("Não consegui criar a pasta de " + relative);
        File temporary = new File(parent, target.getName() + ".partial");
        try (InputStream in = new BufferedInputStream(source); OutputStream out = new BufferedOutputStream(new FileOutputStream(temporary))) {
            byte[] buffer = new byte[64 * 1024];
            int n;
            while ((n = in.read(buffer)) != -1) {
                out.write(buffer, 0, n);
                progress.copiedBytes += n;
                publishImportProgress(progress, relative, false);
            }
        }
        if (target.exists() && !target.delete()) throw new IllegalStateException("Não consegui substituir " + target.getName());
        if (!temporary.renameTo(target)) {
            try (InputStream in = new FileInputStream(temporary); OutputStream out = new BufferedOutputStream(new FileOutputStream(target))) {
                byte[] buffer = new byte[64 * 1024];
                int n;
                while ((n = in.read(buffer)) != -1) out.write(buffer, 0, n);
            }
            if (!temporary.delete()) temporary.deleteOnExit();
        }
    }
"""
replace_method("    private void copyPreparedTree(", "    private void deleteRecursively(", PROGRESS_METHODS, "streaming import progress")

# The old text setter still handles downloads. Import progress is updated separately so it does
# not send thousands of notifications while copying large binary resources.
replace_once(
    "    versionCode 17\n",
    "    versionCode 18\n",
    "version code")
replace_once(
    "    versionName '0.9.9'\n",
    "    versionName '1.0.0'\n",
    "version name")

activity.write_text(s, encoding="utf-8")
shutil.copyfile(bridge_src, bridge_dst)
print("Applied Horizon Android 1.0.0 compact UI and import-progress overlay.")
print(f"Activity: {activity}")
print(f"Native Java bridge: {bridge_dst}")
