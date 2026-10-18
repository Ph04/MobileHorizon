#include <jni.h>
#include <sys/stat.h>

#include <sstream>
#include <string>

namespace {

bool path_is_file(const std::string& path) {
    struct stat info {};
    return ::stat(path.c_str(), &info) == 0 && S_ISREG(info.st_mode);
}

bool path_is_directory(const std::string& path) {
    struct stat info {};
    return ::stat(path.c_str(), &info) == 0 && S_ISDIR(info.st_mode);
}

std::string join_path(const std::string& root, const char* relative) {
    if (root.empty()) return std::string(relative);
    if (root.back() == '/') return root + relative;
    return root + "/" + relative;
}

}  // namespace

extern "C" JNIEXPORT jstring JNICALL
Java_dev_horizon_androidprep_NativePreparationBridge_nativeInspectMinecraftRoot(
        JNIEnv* env, jclass, jstring root_path) {
    if (root_path == nullptr) {
        return env->NewStringUTF(
                "{\"bridge_status\":\"ativa\",\"present_inputs\":0,\"expected_inputs\":6,"
                "\"resource_generation\":false,\"message\":\"O caminho de entrada e nulo.\"}");
    }

    const char* raw = env->GetStringUTFChars(root_path, nullptr);
    if (raw == nullptr) return nullptr;
    const std::string root(raw);
    env->ReleaseStringUTFChars(root_path, raw);

    const bool version_json = path_is_file(join_path(root, "versions/26.3/26.3.json"));
    const bool client_jar = path_is_file(join_path(root, "versions/26.3/26.3.jar"));
    const bool server_jar = path_is_file(join_path(root, "server.jar"));
    const bool libraries = path_is_directory(join_path(root, "libraries"));
    const bool asset_indexes = path_is_directory(join_path(root, "assets/indexes"));
    const bool asset_objects = path_is_directory(join_path(root, "assets/objects"));

    const int present = (version_json ? 1 : 0) + (client_jar ? 1 : 0) +
            (server_jar ? 1 : 0) + (libraries ? 1 : 0) +
            (asset_indexes ? 1 : 0) + (asset_objects ? 1 : 0);

    std::ostringstream report;
    report << "{\"bridge_status\":\"ativa\",\"present_inputs\":" << present
           << ",\"expected_inputs\":6,"
           << "\"version_json\":" << (version_json ? "true" : "false") << ","
           << "\"client_jar\":" << (client_jar ? "true" : "false") << ","
           << "\"server_jar\":" << (server_jar ? "true" : "false") << ","
           << "\"libraries\":" << (libraries ? "true" : "false") << ","
           << "\"asset_indexes\":" << (asset_indexes ? "true" : "false") << ","
           << "\"asset_objects\":" << (asset_objects ? "true" : "false") << ","
           << "\"resource_generation\":false,"
           << "\"message\":\"Esta fase nativa verifica a arvore local; a geracao final ainda exige migrar os exportadores Java 25.\"}";

    return env->NewStringUTF(report.str().c_str());
}
