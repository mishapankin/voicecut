# voicecut

[![PyPI version](https://badge.fury.io/py/voicecut.svg)](https://pypi.org/project/voicecut/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A cli utility for splitting a long audio file into shorter chunks based on moments of silence. It is useful for preprocessing audio before performing speech-to-text on it.

## Installation

Through uv (recomended)
```bash
uv tool install voicecut
```

Through pip

```bash
pip install voicecut
```

## Usage

Split audio files from the command line:

```bash
voicecut audio.mp3 [OPTIONS]
```

**Options:**
- `--segment-length FLOAT`: Target segment length in seconds (default: 600)
- `--segment-delta FLOAT`: Allowed deviation from segment length in seconds (default: 30)
- `--silence-thresh-mode {mean, max, auto}`: Mode to determine the silence threshold. 'mean' uses the audio's average dBFS, 'max' uses the audio's peak dBFS, and 'abs' treats --silence-thresh-delta as an absolute dBFS value. For 'mean' and 'max', the computed value is adjusted by --silence-thresh-delta; for 'abs' the delta is used directly as the threshold.
- `--silence-thresh-delta FLOAT`: Silence threshold delta in dB (default: -4)
- `--min-silence-len FLOAT`: Minimum silence length in seconds (default: 0.5)
- `--output-dir PATH`: Output directory for split segments (default: current directory)

**Example:**
```bash
voicecut audio.mp3 --segment-length 600 --output-dir ./segments
```

## Development
It is recomended to use [uv](https://docs.astral.sh/uv/) toolset for development.

## Testing
There are unittests available in the `tests/` directory.
```
uv run pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
