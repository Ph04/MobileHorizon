#!/data/data/com.termux/files/usr/bin/bash
# Prepare Horizon 26.3 resources entirely on the user's Android device.
# Usage: bash prepare-horizon-resources-termux.sh /path/to/Horizon-26.3-prep-input.zip
set -Eeuo pipefail

die() { printf 'ERRO: %s\n' "$*" >&2; exit 1; }
info() { printf '\n==> %s\n' "$*"; }

if [[ $# -lt 1 || -z "$1" ]]; then
  die "Informe o ZIP exportado pelo app Horizon. Exemplo: bash $0 ~/storage/shared/Download/Horizon-26.3-prep-input.zip"
fi
INPUT="$1"
[[ -f "$INPUT" ]] || die "Não encontrei o ZIP: $INPUT"
INPUT="$(realpath "$INPUT")"

info "Conferindo espaço livre. A preparação pode precisar de vários GB e usa JDK 25."
df -h "$HOME" || true
printf 'O pacote de entrada permanece no seu aparelho; este script não faz upload.\n'
printf 'Mantenha o Termux em primeiro plano e feche outros apps pesados durante a preparação.\n'

if ! command -v pkg >/dev/null 2>&1; then
  die "Este script precisa ser executado dentro do Termux."
fi

info "Instalando ferramentas locais (Git, unzip, Rust, Python e JDK 25)."
pkg update
pkg install -y git unzip rust python openjdk-25

export JAVA_HOME="$PREFIX/lib/jvm/java-25-openjdk"
export PATH="$JAVA_HOME/bin:$PATH"

command -v git >/dev/null || die "Git não foi instalado."
command -v cargo >/dev/null || die "Cargo/Rust não foi instalado."
command -v javac >/dev/null || die "O JDK não contém javac."
command -v java >/dev/null || die "Java não está no PATH."

JAVAC_VERSION="$(javac -version 2>&1)"
JAVA_VERSION="$(java -version 2>&1 | head -n 1)"
RUST_VERSION="$(rustc --version)"
printf 'JDK: %s\n%s\n' "$JAVAC_VERSION" "$JAVA_VERSION"
printf '%s\n' "$RUST_VERSION"
printf '%s\n' "$JAVAC_VERSION" | grep -Eq 'javac 25([. ]|$)' || die "O horizon-prepare exige um JDK 25; encontrado: $JAVAC_VERSION"

RUST_OK="$(printf '%s\n' "$RUST_VERSION" | awk '{ split($2,v,"."); if (v[1] > 1 || (v[1] == 1 && v[2] >= 90)) print "yes"; else print "no"; }')"
[[ "$RUST_OK" == "yes" ]] || die "O Horizon requer Rust 1.90 ou mais recente. Atualize o pacote rust do Termux e tente novamente."

if [[ ! -d "$HOME/storage/shared/Download" ]]; then
  info "Solicitando acesso ao armazenamento compartilhado do Android."
  termux-setup-storage
fi
[[ -d "$HOME/storage/shared/Download" ]] || die "O Termux ainda não tem acesso ao armazenamento compartilhado. Permita o acesso e execute novamente."

GAME_DIR="$HOME/minecraft-horizon-26.3"
HORIZON_DIR="$HOME/src/horizon-resource-preparer"
mkdir -p "$GAME_DIR" "$HOME/src"

info "Verificando o ZIP de entrada."
unzip -tq "$INPUT" || die "O ZIP está incompleto ou corrompido."
unzip -Z1 "$INPUT" | grep -Fxq "versions/26.3/26.3.json" || die "O ZIP não contém versions/26.3/26.3.json; exporte novamente usando o app atualizado."
unzip -Z1 "$INPUT" | grep -Fxq "versions/26.3/26.3.jar" || die "O ZIP não contém versions/26.3/26.3.jar; exporte novamente usando o app atualizado."
unzip -Z1 "$INPUT" | grep -Fxq "server.jar" || die "O ZIP não contém server.jar; exporte novamente usando o app atualizado."
unzip -Z1 "$INPUT" | grep -q '^assets/indexes/' || die "O ZIP não contém o índice de assets; use a opção de baixar todos os assets antes de exportar."

info "Extraindo a cópia privada do Minecraft para $GAME_DIR."
unzip -oq "$INPUT" -d "$GAME_DIR"
[[ -s "$GAME_DIR/server.jar" ]] || die "server.jar não foi extraído."
[[ -d "$GAME_DIR/assets/objects" ]] || die "A pasta de assets está ausente. No app, use a opção de baixar todos os assets antes de exportar."
[[ -d "$GAME_DIR/libraries" ]] || die "A pasta libraries está ausente."
[[ -s "$GAME_DIR/versions/26.3/26.3.json" && -s "$GAME_DIR/versions/26.3/26.3.jar" ]] || die "Os arquivos da versão 26.3 estão incompletos."

info "Obtendo o preparador oficial Horizon. Nenhum JAR ou asset do jogo será enviado ao GitHub."
if [[ ! -d "$HORIZON_DIR/.git" ]]; then
  git clone --depth 1 https://github.com/ludovic111/horizon.git "$HORIZON_DIR"
else
  git -C "$HORIZON_DIR" fetch --depth 1 origin main
  git -C "$HORIZON_DIR" checkout -B main FETCH_HEAD
fi
[[ -s "$HORIZON_DIR/research-lock.json" ]] || die "O repositório não contém research-lock.json."
[[ -d "$HORIZON_DIR/mods/horizon/src/test/java/dev/horizonlab/parity" ]] || die "Os exportadores Java necessários não foram encontrados no repositório Horizon."

info "Preparando os recursos. Esta etapa compila somente o crate horizon-prepare, não o motor completo do jogo."
cd "$HORIZON_DIR"
export CARGO_BUILD_JOBS=1
cargo run --release --locked -p horizon-prepare -- \
  --prepare \
  --server-jar "$GAME_DIR/server.jar" \
  --minecraft-dir "$GAME_DIR"

RESOURCE_DIR="$HORIZON_DIR/.local/horizon-client/26.3"
[[ -s "$RESOURCE_DIR/horizon-resources.json" ]] || die "A execução terminou sem horizon-resources.json."
grep -Eq '"data_version"[[:space:]]*:[[:space:]]*5023' "$RESOURCE_DIR/horizon-resources.json" || die "A data version gerada não é 5023."
grep -Eq '"schema"[[:space:]]*:[[:space:]]*7' "$RESOURCE_DIR/horizon-resources.json" || die "O schema gerado não é 7."

STAMP="$(date +%Y%m%d-%H%M%S)"
DEST="$HOME/storage/shared/Download/HorizonPrepared-$STAMP/26.3"
mkdir -p "$DEST"
info "Copiando os recursos para uma pasta que o seletor de documentos do Android consegue abrir: $DEST"
# Java classes and logs are preparer caches, not runtime resources. Keep the generated
# manifest/assets/data/worldgen tree intact, but do not copy these build caches.
tar -C "$RESOURCE_DIR" --exclude='./classes' --exclude='./client-classes' --exclude='*.log' -cf - . | tar -C "$DEST" -xf -
[[ -s "$DEST/horizon-resources.json" ]] || die "A cópia final não contém horizon-resources.json."

printf '\nPRONTO: recursos Horizon 26.3 preparados localmente.\n'
printf 'Pasta: %s\n' "$DEST"
du -sh "$DEST" || true
printf '\nAbra o app Horizon Android → “Importar recursos Horizon já preparados” → selecione exatamente a pasta 26.3 acima.\n'
printf 'Mantenha o ZIP e a pasta preparada no seu armazenamento local; não os publique nem os envie a terceiros.\n'
