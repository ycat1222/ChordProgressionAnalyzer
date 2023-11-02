# Chord Progression Analyzer

![png](https://github.com/ycat1222/ChordProgressionAnalyzer/blob/main/sample-result.png)

## Overview
This is a Python library for analyzing chord progression in MusicXML format.

## Requirements
- Python 3.10.11
- music21 9.1.0
- pandas 2.0.3

## Usage
```python
import MusicXMLAnalyzer

analyzer = MusicXMLAnalyzer("musicXML\sample.musicxml", "major", "src\setting.ini")
analyzer.analyze()
analyzer.export_MusicXML("result_sample/sample.musicxml")
```

## License
This software is released under the [MIT](http://opensource.org/licenses/mit-license.php) License, see LICENSE.
