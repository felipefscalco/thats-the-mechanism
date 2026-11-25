#!/usr/bin/env bash
# Bootstrap That's the Mechanism on Linux or macOS.
#   scripts/setup.sh           # full: Python venv, npm install, Kokoro models, whisper.cpp + small.en
#   scripts/setup.sh --fast    # dry/fast: venv + npm only (enough for `npx tsc --noEmit`)
#   scripts/setup.sh --check   # print dependency status and exit
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAST=0
CHECK=0
for arg in "$@"; do
  case "$arg" in
    --fast|--dry) FAST=1 ;;
    --check) CHECK=1 ;;
    -h|--help)
      sed -n '2,6p' "$0"
      exit 0
      ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

need() {
  local name="$1" cmd="$2" hint="$3"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "  ok  $name: $("$cmd" --version 2>&1 | head -n1)"
    return 0
  fi
  echo "  MISSING  $name — $hint"
  return 1
}

OS="$(uname -s)"
echo "That's the Mechanism setup  (os=$OS  fast=$FAST)"
echo
echo "== checking tools =="
missing=0
need Node.js node "install Node 20.19+ / 22.13+ (https://nodejs.org or nvm)" || missing=1
need npm npm "comes with Node.js" || missing=1
need Python3 python3 "install Python 3.10+ (Linux: python3, macOS: brew install python)" || missing=1
need FFmpeg ffmpeg "Linux: sudo apt install ffmpeg   macOS: brew install ffmpeg" || missing=1
need ffprobe ffprobe "same package as FFmpeg" || missing=1
need git git "Linux: sudo apt install git   macOS: xcode-select --install / brew install git" || missing=1
if [[ $FAST -eq 0 ]]; then
  need cmake cmake "Linux: sudo apt install cmake build-essential   macOS: brew install cmake" || missing=1
  if ! command -v make >/dev/null 2>&1; then
    echo "  MISSING  make — Linux: sudo apt install build-essential   macOS: xcode-select --install"
    missing=1
  else
    echo "  ok  make"
  fi
fi

# Node version gate (Remotion engines field)
if command -v node >/dev/null 2>&1; then
  node -e '
    const [maj, min] = process.versions.node.split(".").map(Number);
    const ok = (maj === 20 && min >= 19) || (maj === 22 && min >= 13) || maj >= 24;
    if (!ok) { console.error("  WARN  Node " + process.versions.node + " may be too old (need ^20.19 || ^22.13 || >=24)"); process.exit(1); }
  ' || true
fi

if [[ $CHECK -eq 1 ]]; then
  [[ $missing -eq 0 ]] && echo "all required tools present" && exit 0
  echo "missing tools listed above" >&2
  exit 1
fi
if [[ $missing -ne 0 ]]; then
  echo "Install the missing tools and re-run." >&2
  exit 1
fi

echo
echo "== Python venv (.venv-tts) =="
if [[ ! -x .venv-tts/bin/python ]]; then
  python3 -m venv .venv-tts
fi
.venv-tts/bin/pip install -U pip
.venv-tts/bin/pip install -r requirements.txt

echo
echo "== Remotion npm install =="
(cd remotion && npm install)

if [[ $FAST -eq 1 ]]; then
  echo
  echo "Fast setup done. Run a typecheck with:  (cd remotion && npx tsc --noEmit -p .)"
  echo "For TTS and captions, re-run without --fast to download Kokoro + whisper.cpp."
  exit 0
fi

echo
echo "== Kokoro models =="
mkdir -p models
KOKORO_BASE="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
download() {
  local url="$1" dest="$2"
  if [[ -f "$dest" && -s "$dest" ]]; then
    echo "  exists $dest"
    return 0
  fi
  echo "  downloading $url"
  if command -v curl >/dev/null 2>&1; then
    curl -L --fail --retry 3 -o "$dest.partial" "$url"
  else
    wget -O "$dest.partial" "$url"
  fi
  mv "$dest.partial" "$dest"
}
download "$KOKORO_BASE/kokoro-v1.0.onnx" models/kokoro-v1.0.onnx
download "$KOKORO_BASE/voices-v1.0.bin" models/voices-v1.0.bin

echo
echo "== whisper.cpp + small.en =="
if [[ ! -d tools/whisper.cpp/.git ]]; then
  mkdir -p tools
  git clone --depth 1 https://github.com/ggml-org/whisper.cpp tools/whisper.cpp
fi
if [[ ! -x tools/whisper.cpp/build/bin/whisper-cli ]]; then
  cmake -S tools/whisper.cpp -B tools/whisper.cpp/build
  cmake --build tools/whisper.cpp/build -j"$(command -v nproc >/dev/null && nproc || sysctl -n hw.ncpu)"
fi
if [[ ! -s tools/whisper.cpp/models/ggml-small.en.bin ]]; then
  (cd tools/whisper.cpp && bash models/download-ggml-model.sh small.en)
fi

echo
echo "Full setup done."
echo "  Typecheck:  (cd remotion && npx tsc --noEmit -p .)"
echo "  New episode: see AGENTS.md  (scripts/new-episode.sh … && scripts/build-episode.sh …)"
