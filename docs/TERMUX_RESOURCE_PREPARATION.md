# Preparar recursos Horizon 26.3 no próprio Android

O relatório “manifesto válido / 65 bibliotecas / 5.147 assets” significa que os arquivos de entrada foram baixados e conferidos. Isso ainda não produz a árvore que o cliente Horizon lê: o preparador oficial precisa executar horizon-prepare, incluindo exportadores Java e seus dados derivados. A preparação oficial atual usa Rust e um JDK 25; não é simplesmente descompactar os JARs.

Esta ponte mantém o trabalho no telefone: o APK exporta um ZIP local com seus próprios arquivos oficiais; o Termux executa o preparador oficial e copia a saída para uma pasta visível ao seletor do Android; por fim, o APK importa e valida essa pasta. O ZIP, os JARs, os assets e os recursos preparados não são enviados ao GitHub nem devem ser publicados.

## 1. No app Horizon Android

Conclua **“Baixar Minecraft 26.3 + todos os assets”** e confirme que a validação mostra zero bibliotecas com hash incorreto. Depois use **“Exportar arquivos para preparar recursos no Termux”** e salve como **Horizon-26.3-prep-input.zip** em **Download**. A exportação precisa de espaço livre adicional, pois copia localmente milhares de arquivos.

## 2. No Termux

Atualize o Termux de uma fonte atual e autorize o acesso ao armazenamento:

    termux-setup-storage
    pkg update
    pkg install -y curl wget

Baixe o script auxiliar deste repositório e execute-o passando o ZIP. O script instala git, unzip, rust, python e openjdk-25, confere as versões, extrai uma cópia privada do Minecraft, clona o repositório oficial Horizon e executa somente o crate horizon-prepare (não compila o motor de jogo inteiro).

    SCRIPT="$HOME/prepare-horizon-resources-termux.sh"
    URL="https://raw.githubusercontent.com/Ph04/MobileHorizon/main/tools/prepare-horizon-resources-termux.sh"
    curl -fL "$URL" -o "$SCRIPT" || wget -O "$SCRIPT" "$URL"
    bash "$SCRIPT" "$HOME/storage/shared/Download/Horizon-26.3-prep-input.zip"

Se o ZIP foi salvo em outra pasta, ajuste o caminho do último argumento. O JDK 25 para Termux pode ocupar mais de 100 MB de download, e o preparo usa centenas de MB de heap Java; em um telefone com 4 GB de RAM, deixe Termux em primeiro plano, feche outros apps pesados e tenha vários GB livres. Se o processo terminar com “Killed” ou erro de memória, isso não significa automaticamente que os arquivos oficiais estejam corrompidos.

## 3. Importar os recursos no app

Ao concluir, o script imprime um destino como **Download/HorizonPrepared-AAAAMMDD-HHMMSS/26.3**. Volte ao Horizon Android, toque em **“Importar recursos Horizon já preparados”** e selecione exatamente a pasta **26.3** — ela precisa conter horizon-resources.json diretamente na raiz. O app copia os dados para seu armazenamento privado e recusa uma pasta incompleta.

## O que isso não resolve sozinho

A conclusão da preparação remove o bloqueio dos recursos, mas ainda não é uma prova de jogabilidade. A biblioteca libhorizon_android.so no APK atual continua sendo um binário pré-compilado; a compilação e o teste real do motor no Galaxy A15 são etapas separadas.

A preparação segue o procedimento descrito pelo projeto Horizon: precisa da cópia própria do Minecraft Java 26.3 e os dados derivados devem permanecer locais. Não coloque a pasta .local/horizon-client/26.3 nem o ZIP exportado em commits ou releases.
