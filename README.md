# MobileHorizon — Horizon experimental para Android ARM64

Este repositório monta o APK Android experimental para o Horizon usando a biblioteca nativa ARM64 pré-compilada no pacote de origem.

## Atualização 0.9.8 — downloads em segundo plano

- Os downloads oficiais do Minecraft Java 26.3 passam a usar um serviço Android em primeiro plano para continuarem enquanto o app fica minimizado.
- A notificação mostra o estado do download e, quando o instalador informa os totais, uma barra/percentual de progresso.
- Ao terminar, fica uma notificação de conclusão ou falha. Tocar nela abre o app.
- Android 13 ou superior solicita permissão para mostrar notificações. Se ela for negada, o download ainda pode continuar, mas a notificação na gaveta pode ser ocultada pelo Android.
- O instalador mantém a verificação de SHA-1 e tamanho dos arquivos oficiais; os arquivos são armazenados no espaço privado do aplicativo, não neste repositório.

No app, a opção **Baixar Minecraft 26.3 + todos os assets** baixa o conjunto oficial completo listado para a versão. Isso pode usar centenas de MB; confira o espaço livre e prefira Wi-Fi.

## O que ainda falta para jogar

O teste Vulkan valida a Activity nativa e o renderer, mas não prova que o cliente carregue. O APK continua usando uma biblioteca Rust pré-compilada — este workflow não recompila o motor.

Também falta executar/integrar o preparador oficial de recursos do Horizon. Os arquivos oficiais baixados são as entradas dessa etapa, não os recursos preparados: o diretório final deve conter `horizon-resources.json`, os dados de jogo/worldgen e os demais arquivos exigidos pelo cliente. O preparador atual depende de Rust, Python e JDK 25/exportadores Java; essa preparação ainda não está portada para o Android.

Até lá, use **Importar recursos Horizon já preparados** para escolher no seletor de pastas a saída local válida `.local/horizon-client/26.3` de uma preparação feita no ambiente adequado. A tela de validação informa os arquivos ausentes e não considera um download simples como equivalente aos recursos preparados.

O projeto Horizon pede que a preparação seja feita a partir da cópia própria do Minecraft Java Edition 26.3. Não distribuímos neste repositório os assets nem os recursos derivados do jogo.

## Compilar o APK

Abra **Actions → Android ARM64 package** no GitHub. O workflow remonta o pacote de origem, aplica o overlay Android de notificações, verifica a biblioteca nativa, executa os testes estáticos e constrói um APK debug. O artefato se chama `horizon-android-prebuilt-debug`.

Um workflow bem-sucedido verifica compilação e empacotamento — não substitui o teste no aparelho, nem comprova entrada em mundo ou desempenho jogável.
