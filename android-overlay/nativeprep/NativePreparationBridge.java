package dev.horizon.androidprep;

/**
 * Initial JNI boundary for the in-app native resource-preparation work.
 *
 * Version 1.0.0 only audits the local Minecraft input tree. It intentionally does not claim
 * that the full Horizon resource generator is native yet; the Java 25 vanilla exporters still
 * need to be ported or supplied by an Android-compatible runtime.
 */
public final class NativePreparationBridge {
    private static final boolean LOADED;

    static {
        boolean loaded;
        try {
            System.loadLibrary("horizon_prepare_bridge");
            loaded = true;
        } catch (LinkageError error) {
            loaded = false;
        }
        LOADED = loaded;
    }

    private NativePreparationBridge() {
    }

    public static String inspectMinecraftRoot(String rootPath) {
        if (!LOADED) {
            throw new IllegalStateException(
                    "A biblioteca nativa horizon_prepare_bridge nao foi carregada.");
        }
        if (rootPath == null || rootPath.trim().isEmpty()) {
            throw new IllegalArgumentException("O caminho da instalacao Minecraft esta vazio.");
        }
        String result = nativeInspectMinecraftRoot(rootPath);
        if (result == null || result.trim().isEmpty()) {
            throw new IllegalStateException("O diagnostico nativo nao retornou um relatorio.");
        }
        return result;
    }

    private static native String nativeInspectMinecraftRoot(String rootPath);
}
