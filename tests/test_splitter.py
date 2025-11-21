import shlex
import subprocess
import tempfile
import unittest
from os import PathLike, chdir
from pathlib import Path

from voicecut.splitter import (
    get_audio_duration,
    get_ffmpeg_path,
    split_audio_file_by_silence,
)


def generate_tone(
    ffmpeg: str,
    filename: str,
    tone: int,
    duration: float,
) -> str:
    cmd = f'{ffmpeg} -y -f lavfi -i "sine=f={tone}:d={duration}" -c:a pcm_s16le {filename}'
    subprocess.run(shlex.split(cmd), check=True)

    return filename


def generate_silence(
    ffmpeg: str,
    filename: str,
    duration: float,
) -> str:
    cmd = f'{ffmpeg} -y -f lavfi -i "anullsrc=r=44100:channel_layout=mono" -t {duration} -c:a pcm_s16le {filename}'
    subprocess.run(shlex.split(cmd), check=True)

    return filename


def merge_audio(
    ffmpeg: str,
    filenames: list[str],
    output: PathLike | str,
) -> PathLike | str:
    list_name = "list.txt"
    with open(list_name, "w") as flist:
        for name in filenames:
            print(f"file '{name}'", file=flist)

    cmd = f"{ffmpeg} -f concat -safe 0 -i {list_name} -c copy {output}"

    subprocess.run(shlex.split(cmd), check=True)

    return output


class TestSplitter(unittest.TestCase):
    def test_split_audio_file_by_silence_synthetic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            chdir(temp_dir)

            audio_file = Path("result.wav")
            out_dir = Path("output")

            ffmpeg = get_ffmpeg_path()

            dur_1 = 53
            dur_2 = 58
            dur_s = 2

            generate_tone(ffmpeg, "tone1.wav", 440, dur_1)
            generate_silence(ffmpeg, "silence.wav", dur_s)
            generate_tone(ffmpeg, "tone2.wav", 880, dur_2)

            merge_audio(ffmpeg, ["tone1.wav", "silence.wav", "tone2.wav"], "result.wav")

            split_audio_file_by_silence(
                audio=audio_file,
                out_dir=out_dir,
                segment_length=60,
                segment_delta=20,
            )

            # Check output files
            output_files = sorted(out_dir.glob("segment_*.wav"))
            self.assertEqual(len(output_files), 2)

            # Check durations
            res_dur_1 = get_audio_duration(output_files[0])
            res_dur_2 = get_audio_duration(output_files[1])

            self.assertAlmostEqual(res_dur_1, dur_1 + dur_s / 2.0, delta=2)
            self.assertAlmostEqual(res_dur_2, dur_2 + dur_s / 2.0, delta=2)


if __name__ == "__main__":
    unittest.main()
