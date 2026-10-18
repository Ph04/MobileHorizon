#!/usr/bin/env python3
"""Apply the local resource-preparation export bridge after the notification overlay."""
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "HorizonAndroidPrep")
app = root / "app/src/main"
activity = app / "java/dev/horizon/androidprep/MainActivity.java"
gradle = root / "app/build.gradle"

for path in (activity, gradle):
    if not path.is_file():
        raise SystemExit(f"Required source file is missing: {path}")

s = activity.read_text(encoding="utf-8")

def replace_once(old: str, new: str, label: str) -> None:
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    s = s.replace(old, new, 1)

replace_once(
'''    private static final int PICK_PREPARED_RESOURCE_TREE = 1004;
    private static final int REQUEST_DOWNLOAD_NOTIFICATION_PERMISSION = 1105;
''',
'''    private static final int PICK_PREPARED_RESOURCE_TREE = 1004;
    private static final int EXPORT_PREPARATION_INPUT = 1005;
    private static final int REQUEST_DOWNLOAD_NOTIFICATION_PERMISSION = 1105;
''',
"export request constant")

replace_once(
'''text("Downloads em segundo plano · versão 0.9.8", 15, Color.rgb(159, 177, 210), false)''',
'''text("Preparador Android · versão 0.9.9 · recursos via Termux", 15, Color.rgb(159, 177, 210), false)''',
"app version label")

replace_once(
'''        addButton(root, "6 · Importar recursos Horizon já preparados", v -> pickPreparedResourceTree());
        addButton(root, "7 · Testar controles touch (protótipo)", v ->
                startActivity(new Intent(this, TouchTestActivity.class)));
        addButton(root, "8 · Testar NativeActivity + Vulkan (sem recursos do jogo)", v -> openNativeSmokeTest());
        addButton(root, "9 · Abrir cliente Horizon (precisa do motor + recursos)", v -> openNativeClient());''',
'''        addButton(root, "6 · Importar recursos Horizon já preparados", v -> pickPreparedResourceTree());
        addButton(root, "7 · Exportar arquivos para preparar recursos no Termux", v -> confirmPreparationExport());
        addButton(root, "8 · Testar controles touch (protótipo)", v ->
                startActivity(new Intent(this, TouchTestActivity.class)));
        addButton(root, "9 · Testar NativeActivity + Vulkan (sem recursos do jogo)", v -> openNativeSmokeTest());
        addButton(root, "10 · Abrir cliente Horizon (precisa do motor + recursos)", v -> openNativeClient());''',
"app button group")

replace_once(
'''        TextView warning = text(
                "A opção 1 baixa o manifesto e os arquivos oficiais de Minecraft 26.3, sem precisar " +
                "copiar arquivos de um PC. Os downloads podem continuar em segundo plano com notificação de progresso e conclusão. " +
                "A opção 2 também baixa o catálogo completo de assets, que pode ocupar centenas de MB. " +
                "Os recursos preparados do Horizon ainda precisam ser importados separadamente.", 14, Color.rgb(205, 211, 226), false);''',
'''        TextView warning = text(
                "A opção 1 baixa os arquivos oficiais de Minecraft 26.3. A opção 2 baixa também todos os assets. " +
                "A opção 7 exporta uma cópia local desses arquivos para o preparador oficial executado no Termux; " +
                "o ZIP pode ter centenas de MB e não é enviado pela internet. Depois importe a pasta gerada por horizon-prepare.", 14, Color.rgb(205, 211, 226), false);''',
"app resource warning")

replace_once(
'''    private void pickPreparedResourceTree() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(intent, PICK_PREPARED_RESOURCE_TREE);
    }

    @Override''',
'''    private void pickPreparedResourceTree() {
        Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
        startActivityForResult(intent, PICK_PREPARED_RESOURCE_TREE);
    }

    private void confirmPreparationExport() {
        try {
            String summary = checkPreparationInputFiles();
            new AlertDialog.Builder(this)
                    .setTitle("Exportar entrada do preparador")
                    .setMessage(summary + "\\n\\nSerá criado um ZIP local com versions/, libraries/, assets/ e server.jar. " +
                            "O arquivo pode ter centenas de MB e exige espaço livre adicional. " +
                            "Ele ficará somente no destino que você escolher; o app não fará upload. " +
                            "Depois execute o preparador oficial no Termux e importe a pasta resultante.")
                    .setPositiveButton("Escolher destino", (dialog, which) -> {
                        Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                        intent.addCategory(Intent.CATEGORY_OPENABLE);
                        intent.setType("application/zip");
                        intent.putExtra(Intent.EXTRA_TITLE, "Horizon-26.3-prep-input.zip");
                        intent.addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        startActivityForResult(intent, EXPORT_PREPARATION_INPUT);
                    })
                    .setNegativeButton("Cancelar", null)
                    .show();
        } catch (Exception e) {
            new AlertDialog.Builder(this)
                    .setTitle("Arquivos incompletos para exportação")
                    .setMessage(explain(e) + "\\n\\nConclua primeiro a opção 2 · Baixar Minecraft 26.3 + todos os assets e valide os arquivos.")
                    .setPositiveButton("OK", null)
                    .show();
        }
    }

    private String checkPreparationInputFiles() throws Exception {
        File root = getMinecraftRoot();
        File versionDir = new File(root, "versions/" + GAME_VERSION);
        File versionJson = new File(versionDir, GAME_VERSION + ".json");
        File clientJar = new File(versionDir, GAME_VERSION + ".jar");
        File serverJarFile = new File(root, "server.jar");
        File libraries = new File(root, "libraries");
        if (!versionJson.isFile() || !clientJar.isFile() || !serverJarFile.isFile() || !libraries.isDirectory()) {
            throw new IllegalStateException("Faltam arquivos essenciais: verifique o JSON, o cliente, server.jar e libraries/.");
        }
        JSONObject version = new JSONObject(readText(versionJson));
        JSONObject assetIndex = version.optJSONObject("assetIndex");
        String assetIndexId = assetIndex == null ? "" : assetIndex.optString("id", "");
        if (assetIndexId.isEmpty()) throw new IllegalStateException("O JSON oficial não informa o índice de assets.");
        File assetIndexFile = new File(root, "assets/indexes/" + assetIndexId + ".json");
        if (!assetIndexFile.isFile()) throw new IllegalStateException("Falta assets/indexes/" + assetIndexId + ".json. Baixe todos os assets pela opção 2.");
        JSONObject index = new JSONObject(readText(assetIndexFile));
        JSONObject objects = index.optJSONObject("objects");
        if (objects == null || objects.length() == 0) throw new IllegalStateException("O índice de assets está vazio ou inválido.");
        Set<String> hashes = new HashSet<>();
        java.util.Iterator<String> keys = objects.keys();
        while (keys.hasNext()) {
            JSONObject entry = objects.optJSONObject(keys.next());
            String hash = entry == null ? "" : entry.optString("hash", "");
            if (hash.length() != 40 || !hash.matches("[0-9a-fA-F]{40}")) {
                throw new IllegalStateException("O índice oficial contém um hash de asset inválido.");
            }
            hashes.add(hash.toLowerCase(Locale.ROOT));
        }
        File objectsRoot = new File(root, "assets/objects");
        int missing = 0;
        for (String hash : hashes) {
            if (!new File(new File(objectsRoot, hash.substring(0, 2)), hash).isFile()) missing++;
        }
        if (missing != 0) throw new IllegalStateException("Faltam " + missing + " assets do índice " + assetIndexId + ". Use a opção 2 para baixar todos os assets e tente novamente.");
        return "Minecraft " + GAME_VERSION + " pronto para exportar.\\nAssets esperados: " + hashes.size() +
                " objetos; todos os caminhos existem.\\nÍndice oficial: " + assetIndexId + ".";
    }

    @Override''',
"export dialog and asset preflight")

replace_once(
'''        if (requestCode == PICK_PREPARED_RESOURCE_TREE) {
            setStatus("Importando recursos Horizon…", "Copiando a pasta de recursos preparada para o armazenamento privado. Isso pode ocupar centenas de MB.");
            worker.execute(() -> importPreparedResources(uri));''',
'''        if (requestCode == EXPORT_PREPARATION_INPUT) {
            setStatus("Exportando arquivos oficiais…", "Compactando os JARs, as bibliotecas e os assets para o preparador local. Isso pode levar algum tempo.");
            worker.execute(() -> exportPreparationInput(uri));
        } else if (requestCode == PICK_PREPARED_RESOURCE_TREE) {
            setStatus("Importando recursos Horizon…", "Copiando a pasta de recursos preparada para o armazenamento privado. Isso pode ocupar centenas de MB.");
            worker.execute(() -> importPreparedResources(uri));''',
"export activity result")

replace_once(
'''    private void importFromTree(Uri treeUri) {''',
'''    private void exportPreparationInput(Uri destinationUri) {
        try {
            File root = getMinecraftRoot();
            String ready = checkPreparationInputFiles();
            OutputStream raw = getContentResolver().openOutputStream(destinationUri);
            if (raw == null) throw new IllegalStateException("O seletor de documentos não abriu o arquivo de destino.");
            int[] entryCount = new int[] {0};
            long[] bytesWritten = new long[] {0L};
            try (java.util.zip.ZipOutputStream zip = new java.util.zip.ZipOutputStream(new BufferedOutputStream(raw))) {
                zip.setLevel(java.util.zip.Deflater.BEST_SPEED);
                for (String name : new String[] {"versions", "libraries", "assets"}) {
                    File source = new File(root, name);
                    if (!source.isDirectory()) throw new IllegalStateException("Falta a pasta " + name + "/.");
                    zipPreparationTree(root, source, zip, entryCount, bytesWritten, 0);
                }
                File server = new File(root, "server.jar");
                zipPreparationFile(root, server, zip, entryCount, bytesWritten);
            }
            setStatus("Entrada do preparador exportada", ready + "\\n\\nArquivo ZIP criado no destino escolhido.\\nArquivos incluídos: " + entryCount[0] +
                    "\\nDados lidos: " + String.format(Locale.ROOT, "%.1f MB", bytesWritten[0] / (1024.0 * 1024.0)) +
                    "\\n\\nPróximo passo: execute tools/prepare-horizon-resources-termux.sh no Termux usando este ZIP. " +
                    "O preparador oficial gera a pasta .local/horizon-client/26.3; copie essa pasta para Download e importe-a pela opção 6.");
        } catch (Exception e) {
            setStatus("Falha ao exportar entrada do preparador", explain(e) +
                    "\\n\\nNenhum arquivo foi enviado pela internet. Confira o espaço livre e tente novamente.");
        }
    }

    private void zipPreparationTree(File root, File current, java.util.zip.ZipOutputStream zip,
                                    int[] entryCount, long[] bytesWritten, int depth) throws Exception {
        if (depth > 64) throw new IllegalArgumentException("A árvore dos arquivos oficiais tem níveis demais.");
        String rootPath = root.getCanonicalPath() + File.separator;
        String currentPath = current.getCanonicalPath();
        if (!currentPath.startsWith(rootPath)) throw new IllegalArgumentException("Foi encontrado um caminho fora do diretório Minecraft.");
        if (current.isDirectory()) {
            File[] children = current.listFiles();
            if (children == null) throw new IllegalStateException("Não consegui listar " + current.getName());
            Arrays.sort(children, java.util.Comparator.comparing(File::getName));
            for (File child : children) zipPreparationTree(root, child, zip, entryCount, bytesWritten, depth + 1);
        } else if (current.isFile()) {
            zipPreparationFile(root, current, zip, entryCount, bytesWritten);
        }
    }

    private void zipPreparationFile(File root, File source, java.util.zip.ZipOutputStream zip,
                                    int[] entryCount, long[] bytesWritten) throws Exception {
        String rootPath = root.getCanonicalPath() + File.separator;
        String sourcePath = source.getCanonicalPath();
        if (!sourcePath.startsWith(rootPath)) throw new IllegalArgumentException("Foi encontrado um arquivo fora do diretório Minecraft.");
        String relative = sourcePath.substring(rootPath.length()).replace(File.separatorChar, '/');
        if (!safeRelative(relative)) throw new IllegalArgumentException("Caminho inseguro no arquivo de entrada: " + relative);
        entryCount[0]++;
        if (entryCount[0] > MAX_PREPARED_RESOURCE_ENTRIES) throw new IllegalArgumentException("Há arquivos demais na instalação para exportar com segurança.");
        zip.putNextEntry(new ZipEntry(relative));
        try (InputStream input = new BufferedInputStream(new FileInputStream(source))) {
            byte[] buffer = new byte[64 * 1024];
            int n;
            while ((n = input.read(buffer)) != -1) {
                zip.write(buffer, 0, n);
                bytesWritten[0] += n;
            }
        }
        zip.closeEntry();
        if (entryCount[0] == 1 || entryCount[0] % 100 == 0) {
            setStatus("Exportando entrada do preparador…", "Arquivos: " + entryCount[0] +
                    "\\nDados lidos: " + String.format(Locale.ROOT, "%.1f MB", bytesWritten[0] / (1024.0 * 1024.0)) +
                    "\\nO ZIP está sendo salvo no destino escolhido.");
        }
    }

    private void importFromTree(Uri treeUri) {''',
"ZIP export implementation")

s = s.replace("    versionCode 16\\n", "    versionCode 17\\n")
s = s.replace("    versionName '0.9.8'\\n", "    versionName '0.9.9'\\n")
if "versionName '0.9.9'" not in gradle.read_text(encoding="utf-8"):
    g = gradle.read_text(encoding="utf-8")
    if g.count("versionName '0.9.8'") != 1 or g.count("versionCode 16") != 1:
        raise SystemExit("Gradle version did not match the expected 0.9.8 base")
    gradle.write_text(g.replace("versionCode 16", "versionCode 17", 1).replace("versionName '0.9.8'", "versionName '0.9.9'", 1), encoding="utf-8")
else:
    raise SystemExit("Gradle already appears to be 0.9.9; refusing to apply overlay twice")

activity.write_text(s, encoding="utf-8")

print("Applied local Termux resource-preparation export.")
print(f"Activity: {activity}")
print(f"Gradle: {gradle}")
