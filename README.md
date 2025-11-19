# voicecut

[![PyPI version](https://badge.fury.io/py/voicecut.svg)](https://pypi.org/project/voicecut/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A cli utility for splitting a long audio file into shorter chunks based on moments of silence. It is useful for preprocessing audio before performing speech-to-text on it.

## Installation

```bash
pip install voicecut
```

## Usage

### Command Line Interface

Split audio files from the command line:

```bash
voicecut audio.mp3 [OPTIONS]
```

**Options:**
- `--segment-length FLOAT`: Target segment length in seconds (default: 600)
- `--segment-delta FLOAT`: Allowed deviation from segment length in seconds (default: 30)
- `--silence-thresh-delta INT`: Silence threshold delta in dB (default: -16)
- `--min-silence-len FLOAT`: Minimum silence length in seconds (default: 0.5)
- `--output-dir PATH`: Output directory for split segments (default: current directory)

**Example:**
```bash
voicecut audio.mp3 --segment-length 600 --output-dir ./segments
```

### Python API

Split an audio file in roughly 10 minute segments with splits in moments of silence.
```python
from voicecut import split_audio_on_silence
from pydub import AudioSegment

audio = AudioSegment.from_file("example_audio.mp3")

splitted = split_audio_on_silence(audio)

for i, segment in enumerate(splitted):
    segment.export(f"segment_{i}.wav")
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
