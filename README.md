# MobileHorizon — compilação Android ARM64

Este repositório prepara uma compilação do aplicativo experimental Horizon Android usando a biblioteca nativa ARM64 já validada no pacote 0.9.7.

## Estado

- Workflow GitHub Actions: configurado em `.github/workflows/android-package.yml`.
- Biblioteca nativa local do pacote: ELF64/AArch64 para Android API 26; o workflow a valida e confirma que está empacotada no APK.
- APK: ainda não compilado. A execução do workflow depende do envio das três partes do arquivo ZIP.
- Recursos completos do jogo produzidos por `horizon-prepare`: não incluídos. Portanto, mesmo que o APK compile, isso não prova que o cliente jogue; ele ainda precisará dos recursos preparados/importados.

## Enviar as partes do pacote

Carregue estes três arquivos na raiz deste repositório, mantendo exatamente os nomes:

- `HorizonAndroidPrep_0.9.7_with_native.zip.part-00`
- `HorizonAndroidPrep_0.9.7_with_native.zip.part-01`
- `HorizonAndroidPrep_0.9.7_with_native.zip.part-02`

Pode enviá-los juntos em um único commit pelo botão **Add file → Upload files** do GitHub. Cada parte faz parte do mesmo arquivo binário; não renomeie, não abra e não converta para texto.

O workflow remontará o ZIP e verificará o SHA-256 esperado:
`c3e8de14e3beacbff203f2134afabe3fb801bea8eda7de42491aacfe00a2b302`.

Depois, abra **Actions → Android ARM64 package**. Em caso de sucesso, baixe o artefato `horizon-android-prebuilt-debug` e extraia o APK.

## Observação importante

Esta etapa empacota a biblioteca nativa existente; ela não recompila o motor Rust. O teste de APK confirma o empacotamento da biblioteca, não a inicialização do Horizon nem a renderização Vulkan no Galaxy A15.