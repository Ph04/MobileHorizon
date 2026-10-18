# MobileHorizon — Horizon experimental para Android ARM64

## Versão 1.0.0 — importação com progresso e preparação nativa (fase inicial)

Esta versão mantém o download oficial do Minecraft Java 26.3 e a importação da pasta de recursos produzida pelo preparador oficial. A interface principal foi simplificada para destacar as ações principais e deixar opções de importação menos usadas em um menu secundário.

### O que entrou nesta versão

- **Importação com progresso visível:** o app primeiro analisa a pasta escolhida e depois exibe porcentagem, quantidade de arquivos copiados, bytes processados e caminho atual. Quando o provedor Android não fornece tamanhos, o progresso usa a contagem de arquivos.
- **Importação segura:** os recursos são copiados para uma pasta temporária, validados (manifesto, `schema=7`, `data_version=5023` e arquivos essenciais) e só então ativados. Uma falha durante a cópia não deve substituir a árvore válida já instalada.
- **Interface compacta:** download do jogo, download dos assets, importação dos recursos, diagnóstico e abertura do cliente ficam em primeiro plano. Opções legadas de importação ficam em “Mais opções de importação…”. Os botões de smoke test não ocupam a tela principal.
- **Ponte nativa ARM64 (fase 1):** uma biblioteca JNI verifica se a instalação local contém os seis grupos de entradas esperados e expõe o resultado no diagnóstico do app.
- **Continuidade de uso:** a importação da pasta preparada continua disponível para testar os recursos gerados no Termux na versão 0.9.9.

### Como testar a pasta já preparada

1. Instale o APK 1.0.0.
2. Toque em **Importar pasta de recursos preparada**.
3. No seletor do Android, navegue até `Download/HorizonPrepared-20261018-115754/26.3` (ou a pasta `26.3` criada no seu aparelho).
4. Selecione a própria pasta `26.3`, que deve conter `horizon-resources.json` diretamente na raiz.
5. Observe o painel **Status da operação**. Ele deve mostrar a análise, o avanço da cópia, a validação e o resultado final.
6. Depois de uma importação bem-sucedida, toque em **Abrir Horizon** para testar a inicialização.

### Limites atuais da preparação nativa

**A geração completa de recursos ainda não funciona sem Termux.** Esta versão integra a ponte JNI que inspeciona os arquivos de entrada; ela ainda não substitui o preparador completo `horizon-prepare`. O preparador oficial compila e executa exportadores Java 25 que chamam APIs do próprio Minecraft. O trabalho nativo seguinte precisa executar essa etapa num runtime Java 25 realmente compatível com Android ARM64 ou portar os exportadores gradualmente e provar equivalência com os recursos oficiais antes de ativar a preparação automática.

A biblioteca `libhorizon_android.so` do cliente continua sendo um binário pré-compilado. Uma compilação bem-sucedida comprova o APK e o empacotamento das bibliotecas, não que o Minecraft tenha iniciado ou aberto um mundo no telefone.

### Privacidade e armazenamento

O app mantém os arquivos no dispositivo. Não envie ao GitHub nem publique o ZIP exportado, os JARs, os assets ou `.local/horizon-client/26.3`: são dados derivados do jogo. A importação faz uma cópia local adicional, então mantenha espaço livre suficiente para o diretório original, a pasta preparada e a cópia privada.

No Galaxy A15 com 4 GB de RAM, teste a importação com outros aplicativos pesados fechados. A preparação completa ainda precisa de validação de memória, recuperação após interrupção e teste real de inicialização.

### Compilação

O workflow **Android ARM64 package** recompõe o arquivo-fonte de base, aplica os overlays versionados, compila a ponte JNI com o NDK e gera um APK debug. O artefato de build é `horizon-android-prebuilt-debug`.

Documentação adicional:
- [Plano do preparador nativo e fase atual](docs/NATIVE_PREPARER_PLAN.md)
- [Preparação de recursos 26.3 com o Termux (fluxo de compatibilidade atual)](docs/TERMUX_RESOURCE_PREPARATION.md)
