from MusicXMLAnalyzer import MusicXMLAnalyzer

analyzer = MusicXMLAnalyzer("musicXML\sample.musicxml", "major", "src\setting.ini")
analyzer.analyze()
analyzer.export_MusicXML("result_sample\sample.musicxml")
