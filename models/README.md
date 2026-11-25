# Models

Large model files are **not** stored in git. `scripts/setup.sh` downloads them here:

| file | source | use |
|---|---|---|
| `kokoro-v1.0.onnx` (~310 MB) | [kokoro-onnx model-files-v1.0](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0) | TTS |
| `voices-v1.0.bin` (~27 MB) | same release | Kokoro voice bank |

whisper.cpp and `ggml-small.en.bin` (~465 MB) live under `tools/whisper.cpp/` (also gitignored, also installed by setup).
