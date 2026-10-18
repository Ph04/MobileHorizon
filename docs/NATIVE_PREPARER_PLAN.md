# Horizon Android 1.0.0 — import progress and native-preparer groundwork

## Included in this iteration

- The already-prepared resource-tree importer remains available, so users can test the output from horizon-prepare.
- The importer performs a pre-scan, shows a determinate progress bar when the Android document provider reports file sizes, otherwise falls back to file-count progress, and reports the current path, copied file count, and bytes copied.
- Copying still goes into a staging directory. Schema, data version, and required-resource checks run before the new tree replaces the currently installed tree. A failed import does not intentionally replace the previous valid resources.
- The main page now keeps the common actions prominent and moves legacy installation import methods into a small secondary dialog. Touch and Vulkan smoke-test buttons are hidden from the primary page but their diagnostic methods remain in source.

## Native preparation: phase 1 only

NativePreparationBridge and horizon_prepare_bridge.cpp are the initial JNI boundary for a local ARM64 preparation pipeline. The native function audits the local Minecraft input tree and reports which expected folders/files are present. The in-app validation action displays this report.

This native probe does **not** generate horizon-resources.json and does not claim the full preparer works without Termux. The official horizon-prepare pipeline still compiles and runs multiple Java 25 exporters that call Minecraft's own client/server APIs. The next stage must either supply a tested Android-compatible Java 25 runtime in the app-private directory or port each exporter to native code and prove parity against schema 7 / data version 5023. Merely compiling the Rust crate into a shared library is insufficient while those Java stages remain.

## Next stages

1. Make the native preparation pipeline consume the user's already-downloaded versions/, libraries/, assets/, and server.jar directly from app-private storage.
2. Resolve Java 25 exporter execution for Android ARM64; test actual java/javac behavior rather than assuming a desktop JDK or Termux package can be relocated into another app's storage.
3. Port and test exporters incrementally. Compare generated output to the official preparer's schema 7 output on identical local inputs, without committing or uploading the Minecraft JARs, assets, or generated resource tree.
4. Stream progress and logs through the existing Android status panel, then enable the automatic-preparation control only after complete resource-generation tests pass.
5. On the Galaxy A15 / 4 GB RAM, verify peak memory, retry behavior after process death, and a real client launch.

All Minecraft files and generated resources remain local. The APK build packages only the native preflight bridge and application code, not the user's Minecraft-derived resource data.
