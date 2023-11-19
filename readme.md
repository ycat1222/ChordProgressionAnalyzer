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
from MusicXMLAnalyzer import MusicXMLAnalyzer

analyzer = MusicXMLAnalyzer("MusicXML/sample.musicxml", "major", "setting.ini")
analyzer.analyze()
analyzer.export_MusicXML("result/sample.musicxml")
```

## License
This software is released under the [MIT](http://opensource.org/licenses/mit-license.php) License, see LICENSE.
