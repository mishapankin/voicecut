from .splitter import split_audio_on_silence
from pydub import AudioSegment


def voicecut_main():
    import argparse
    import sys
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Split audio file on silence into multiple segments."
    )
    parser.add_argument("audio_file", help="Path to the audio file to split")
    parser.add_argument(
        "--segment-length",
        type=float,
        default=600.0,
        help="Target segment length in seconds (default: 600)",
    )
    parser.add_argument(
        "--segment-delta",
        type=float,
        default=30.0,
        help="Allowed deviation from segment length in seconds (default: 30)",
    )
    parser.add_argument(
        "--silence-thresh-delta",
        type=int,
        default=-16,
        help="Silence threshold delta in dB (default: -16)",
    )
    parser.add_argument(
        "--min-silence-len",
        type=float,
        default=0.5,
        help="Minimum silence length in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=".",
        help="Output directory for split segments (default: current directory)",
    )

    args = parser.parse_args()

    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"Error: Audio file '{audio_path}' does not exist", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        audio = AudioSegment.from_file(str(audio_path))
    except Exception as e:
        print(f"Error loading audio file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        segments = split_audio_on_silence(
            audio,
            segment_length=args.segment_length,
            segment_delta=args.segment_delta,
            silence_thresh_delta=args.silence_thresh_delta,
            min_silence_len_ms=args.min_silence_len,
        )
    except Exception as e:
        print(f"Error splitting audio: {e}", file=sys.stderr)
        sys.exit(1)

    stem = audio_path.stem
    suffix = audio_path.suffix

    for i, segment in enumerate(segments):
        output_path = output_dir / f"{stem}_part{i + 1:03d}{suffix}"
        try:
            segment.export(str(output_path), format=suffix.lstrip("."))
            print(f"Exported segment {i + 1} to {output_path}")
        except Exception as e:
            print(f"Error exporting segment {i + 1}: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"Successfully split audio into {len(segments)} segments")


if __name__ == "__main__":
    voicecut_main()
