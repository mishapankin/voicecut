import json
import math
import os
import re
import shlex
import shutil
import subprocess
from itertools import pairwise
from os import PathLike
from pathlib import Path
from typing import Literal, Optional


def get_ffmpeg_path() -> str:
    path = shutil.which("ffmpeg")
    if path is None:
        raise FileNotFoundError(
            "ffmpeg not found. Please install ffmpeg and ensure it is in PATH."
        )
    return path


def get_ffprobe_path() -> str:
    path = shutil.which("ffprobe")
    if path is None:
        raise FileNotFoundError(
            "ffprobe not found. Please install ffprobe and ensure it is in PATH."
        )
    return path


def get_audio_duration(
    audio: PathLike | str,
) -> float:
    ffprobe = get_ffprobe_path()
    cmd = f"{ffprobe} -v error -show_entries format=duration -of json {audio}"

    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    output = json.loads(proc.stdout)

    return float(output["format"]["duration"])


def detect_silence(
    audio: PathLike | str,
    silence_thresh_db: float = -16,  # in dB
    min_silence_len: float = 0.5,  # in seconds
) -> list[tuple[float, float]]:
    ffmpeg = get_ffmpeg_path()
    cmd = f"{ffmpeg} -hide_banner -i {audio} -af  silencedetect=noise={silence_thresh_db}dB:d={min_silence_len} -f null -"

    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    output = proc.stderr

    starts = [
        float(m.group(1)) for m in re.finditer(r"silence_start: ([0-9.]+)", output)
    ]
    ends = [
        float(m.group(1)) for m in re.finditer(r"silence_end: ([0-9.]+) \|", output)
    ]
    return list(zip(starts, ends))


def detect_volume(
    audio: PathLike | str,
    mode: Literal["mean", "max", "abs"] = "mean",
) -> float:
    if mode == "abs":
        return 0.0

    ffmpeg = get_ffmpeg_path()
    cmd = f"{ffmpeg} -hide_banner -i {audio} -af  volumedetect -f null -"

    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    output = proc.stderr

    volume = [
        float(m.group(1)) for m in re.finditer(rf"{mode}_volume: (-?[0-9.]+)", output)
    ]
    if len(volume) != 1:
        raise RuntimeError("Failed to detect volume")
    return volume[0]


def select_silence_splits(
    silences: list[tuple[float, float]],
    duration: float,  # in seconds
    segment_length: float = 600.0,  # in seconds
    segment_delta: float = 30.0,  # in seconds
) -> list[float]:
    segments_count = math.ceil(duration / segment_length)
    new_segment_length = duration / segments_count

    splits = [((i + 1) * new_segment_length, 0.0) for i in range(segments_count - 1)]

    for start, end in silences:
        middle = (start + end) / 2.0
        duration = end - start

        i = int((middle + segment_length / 2.0) / segment_length) - 1
        if (
            abs((i + 1) * new_segment_length - middle) > segment_delta
            or i < 0
            or i >= len(splits)
        ):
            continue

        if duration > splits[i][1]:
            splits[i] = (middle, duration)

    return [s[0] for s in splits]


def cut_audio_segment(
    audio: PathLike | str,
    begin: float,
    end: Optional[float],
    output: PathLike,
) -> None:
    to_substr = "" if end is None else f"-to {end}"

    ffmpeg = get_ffmpeg_path()
    cmd = f"{ffmpeg} -y -i {audio} -ss {begin} {to_substr} -c copy {output}"

    subprocess.run(shlex.split(cmd))


def split_audio_file(
    audio: PathLike | str,
    splits: list[float],
    out_dir: PathLike | str,
    prefix: str = "segment",
) -> list[PathLike]:
    os.makedirs(out_dir, exist_ok=True)

    suffix = Path(audio).suffix

    result: list[PathLike] = []

    for i, (begin, end) in enumerate(pairwise([0.0] + splits + [None])):
        assert begin is not None

        result_path = Path(out_dir, f"{prefix}_{(i + 1):03}{suffix}")
        cut_audio_segment(audio, begin, end, result_path)

        result.append(result_path)

    return result


def split_audio_file_by_silence(
    audio: PathLike | str,
    out_dir: PathLike | str,
    segment_length: float = 600.0,  # in seconds
    silence_thresh_mode: Literal["mean", "max", "abs"] = "mean",
    segment_delta: float = 30.0,  # in seconds
    silence_thresh_delta_db: int = -4,  # in dB
    min_silence_len: float = 0.5,  # in seconds
    prefix: str = "segment",
) -> None:
    duration = get_audio_duration(audio)
    volume = detect_volume(audio, silence_thresh_mode)
    silences = detect_silence(
        audio=audio,
        silence_thresh_db=silence_thresh_delta_db + volume,
        min_silence_len=min_silence_len,
    )
    splits = select_silence_splits(
        silences=silences,
        duration=duration,
        segment_length=segment_length,
        segment_delta=segment_delta,
    )

    split_audio_file(
        audio=audio,
        splits=splits,
        out_dir=out_dir,
        prefix=prefix,
    )
