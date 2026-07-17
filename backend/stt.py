"""local_stt.py — 本機語音轉文字（faster-whisper，預設引擎）。

不需要任何雲端 API Key；模型第一次使用時會從 Hugging Face 下載到本機快取
（~/.cache/huggingface），之後完全離線可用。用 large-v3-turbo：中英文夾雜
（這個 app 的典型使用情境——邊講話邊夾雜程式術語）辨識效果比純中文微調模型
好，速度也比 large-v3 快得多，CPU 就能跑。

模型物件很重（載入要花幾秒、佔用數百 MB～GB 記憶體），所以用 process 內的
單例，只載入一次、重複使用；真正的推論（CPU-bound）丟到 executor 跑，避免
卡住 event loop。

實測踩到的兩個坑（32-core i9-13900HX 上量出來的，不是理論值）：
- WhisperModel 不帶 cpu_threads 參數時，ctranslate2 內部預設值明顯沒有把
  多核心用起來——一段 7.5 秒的錄音要跑 123 秒（~16x realtime，完全不能用）。
  明確帶 cpu_threads 之後同一段錄音降到 19 秒左右（實測比較過 8/16/32，16
  最快，再往上因為執行緒排程開銷反而變慢）。cpu_threads 用 os.cpu_count()
  夾在 4~16 之間，讓少核心機器也能拿到合理下限、多核心機器不會過度超訂。
- faster-whisper 的中文輸出一律是簡體字，跟 language='zh'/'zh-TW' 這些
  代碼無關——這個 app 全部介面文字都是繁體中文，直接把簡體丟回輸入框，
  使用者第一眼看到滿螢幕簡體字會覺得「完全不能用」，即使辨識內容其實是對
  的。用 opencc 的 s2twp（簡體→繁體，台灣慣用詞轉換，例如「软件」轉成
  「軟體」而不是只轉字形的「軟件」）補一道轉換。
"""

from __future__ import annotations

import asyncio
import io
import os
import threading

MODEL_SIZE = "large-v3-turbo"
_CPU_THREADS = max(4, min(os.cpu_count() or 4, 16))

_model = None
_model_lock = threading.Lock()

_s2twp = None
_s2twp_lock = threading.Lock()


class LocalSttUnavailable(RuntimeError):
    """faster-whisper 沒安裝，或模型載入失敗（例如第一次使用但沒有網路可下載）。"""


def _get_model():
    global _model
    if _model is not None:
        return _model
    with _model_lock:
        if _model is not None:
            return _model
        try:
            from faster_whisper import WhisperModel
        except ImportError as e:
            raise LocalSttUnavailable(
                "faster-whisper 未安裝；請執行 pip install -r requirements.txt"
            ) from e
        try:
            _model = WhisperModel(
                MODEL_SIZE, device="cpu", compute_type="int8", cpu_threads=_CPU_THREADS
            )
        except Exception as e:
            raise LocalSttUnavailable(f"本機語音模型載入失敗：{e}") from e
        return _model


def _get_s2twp():
    """惰性載入簡體轉繁體（台灣慣用詞）轉換器；opencc 沒裝的話原樣跳過，
    不影響辨識結果本身，只是不做字形轉換。"""
    global _s2twp
    if _s2twp is not None:
        return _s2twp
    with _s2twp_lock:
        if _s2twp is not None:
            return _s2twp
        try:
            import opencc
            _s2twp = opencc.OpenCC("s2twp")
        except Exception:
            _s2twp = False
        return _s2twp


def _to_traditional(text: str) -> str:
    converter = _get_s2twp()
    if not converter:
        return text
    try:
        return converter.convert(text)
    except Exception:
        return text


def _transcribe_sync(audio_bytes: bytes, language: str) -> str:
    model = _get_model()
    segments, _info = model.transcribe(
        io.BytesIO(audio_bytes),
        language=language or None,
        vad_filter=True,
    )
    text = "".join(seg.text for seg in segments).strip()
    if (language or "").lower().startswith("zh"):
        text = _to_traditional(text)
    return text


async def transcribe_local(audio_bytes: bytes, language: str = "") -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _transcribe_sync, audio_bytes, language)
