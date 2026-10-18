# MobileHorizon — Horizon experimental para Android ARM64

Este repositório monta o APK Android experimental para o Horizon usando a biblioteca nativa ARM64 pré-compilada no pacote de origem.

## Atualização 0.9.9 — downloads e exportação local para preparação de recursos

- Os downloads oficiais do Minecraft Java 26.3 continuam enquanto o app fica minimizado, com notificação de progresso e de conclusão.
- A nova opção **“Exportar arquivos para preparar recursos no Termux”** grava um ZIP local com a cópia do usuário de `versions/`, `libraries/`, `assets/` e `server.jar`. O app não envia esses dados pela internet.
- O preparador oficial `horizon-prepare` roda no próprio Android por meio do Termux, usando Rust 1.90+ e JDK 25 para compilar/executar os exportadores Java do jogo.
- Depois da preparação, importe a pasta gerada, contendo `horizon-resources.json`, pelo botão **“Importar recursos Horizon já preparados”**. A tela valida schema, versão dos dados e arquivos essenciais.

Consulte o fluxo completo em [docs/TERMUX_RESOURCE_PREPARATION.md](docs/TERMUX_RESOURCE_PREPARATION.md). O script [tools/prepare-horizon-resources-termux.sh](tools/prepare-horizon-resources-termux.sh) automatiza as etapas do Termux a partir do ZIP exportado pelo app.

A opção **“Baixar Minecraft 26.3 + todos os assets”** pode usar centenas de MB. A exportação e a árvore preparada exigem espaço adicional, então confira o armazenamento livre antes de começar. Em telefones com 4 GB de RAM, mantenha o Termux em primeiro plano, feche outros apps pesados e use Wi-Fi. O processo pode falhar por limite de memória do Android; isso não significa automaticamente que os arquivos de entrada estejam corrompidos.

## Privacidade dos arquivos do jogo

Os assets do Minecraft e os recursos preparados são derivados do jogo e devem permanecer locais. Não faça commit, release, upload ou compartilhamento do ZIP exportado nem da pasta `.local/horizon-client/26.3`. Somente o código original do app e os scripts de preparação são versionados aqui.

## O que ainda falta para jogar

O APK ainda usa uma biblioteca Rust pré-compilada — este workflow não recompila o motor. A compilação valida o app Android e o empacotamento da biblioteca nativa, mas não prova que Horizon abra um mundo no aparelho.

O fluxo 0.9.9 automatiza a **exportação e a preparação dos recursos via Termux**; o primeiro uso da preparação ainda precisa ser executado no telefone. Depois de importar uma pasta de recursos completa, o próximo passo é testar a inicialização do cliente no Galaxy A15. Não declare a jogabilidade confirmada até esse teste real.

## Compilar o APK

Abra **Actions → Android ARM64 package** no GitHub. O workflow remonta o pacote de origem, aplica as atualizações de notificações e exportação local, valida a biblioteca nativa e constrói um APK debug. O artefato se chama `horizon-android-prebuilt-debug`.

Um workflow bem-sucedido comprova compilação e empacotamento, não a inicialização do jogo ou o desempenho jogável.
