from MusicXMLAnalyzer import MusicXMLAnalyzer

analyzer = MusicXMLAnalyzer("MusicXML/sample.musicxml", "major", "setting.ini")
analyzer.analyze()
analyzer.export_MusicXML("result/sample.musicxml")
