from .splitter import split_audio_file_by_silence


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
        "-o",
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

    stem = audio_path.stem
    suffix = audio_path.suffix

    try:
        split_audio_file_by_silence(
            audio=str(audio_path),
            out_dir=str(output_dir),
            segment_length=args.segment_length,
            segment_delta=args.segment_delta,
            silence_thresh_db=args.silence_thresh_delta,
            min_silence_len=args.min_silence_len,
            prefix=stem,
        )
    except Exception as e:
        print(f"Error splitting audio: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Completed splitting the audio")


if __name__ == "__main__":
    voicecut_main()
