# -*- coding: utf-8 -*-
import music21
from music21.stream import Score, Measure
from music21.note import Note
from music21.key import Key, KeySignature
from music21.chord import Chord
from music21.harmony import ChordSymbol

import configparser

from ChordProgressionAnalyzer import ChordProgressionAnalyzer, AnalyzedChord
from AnalyzedNote import AnalyzedNote

class MusicXMLAnalyzer(ChordProgressionAnalyzer):

    score: Score = None
    modulation_count: int = -1
    modulation_list: list[None | Key] = [None]
    """ modulation_list[measure_no] = Key
    (modulation_list[0] = None) """
    note_list: list[AnalyzedNote] = []

    __DEFAULT_SETTING: dict[str, str | bool] = {
        "unknown_degree_name": "",
        "dominant_motion_start": "→",
        "dominant_motion_continue": "→",
        "dominant_motion_end": "",
        "related_IIm_start": "┗━┛",
        "related_IIm_end": "",
        "substitute_dominant_motion_start": "-->",
        "substitute_dominant_motion_continue": "-->",
        "substitute_dominant_motion_end": "",
        "conjunct_motion_start": "conjunct->",
        "conjunct_continue": "-conjunct->",
        "conjunct_motion_end": "->conjunct",
        "line_cliche_start": "cliche->",
        "line_cliche_continue": "-cliche->",
        "line_cliche_end": "->cliche",
        "print_analyzed_melody": True,
    }

    def __init__(self, file_name: str, key_type: str = "major", setting_file_name: None | str = None, setting_section_name: str = "DEFAULT") -> None:
        """ Read MusicXML file and add to chord_list
        Warning: The key of all chords is processed as major.

        Parameters
        ----------
        file_name : str
            MusicXML file name
        key_type : str, optional
            Key type, "major" or "minor", by default "major"
        setting_file_name : None | str, optional
            Setting file name (.ini) , by default None
        setting_section_name : str, optional
            Setting section name in setting file(.ini), by default "DEFAULT"
        """

        self.score = music21.converter.parse(file_name, format="musicxml")
        self.modulation_count: int = -1
        self.modulation_list: list[None | Key] = [None]
        self.note_list: list[AnalyzedNote] = []

        # 設定ファイルの読み込み
        # Load setting file
        if setting_file_name != None:
            self.__setting_parser = configparser.RawConfigParser()
            self.__setting_parser.read(setting_file_name, encoding="utf-8")
            self.setting = dict(self.__setting_parser[setting_section_name])
            self.setting["print_analyzed_melody"] = self.__setting_parser[setting_section_name].getboolean("print_analyzed_melody")
        else:
            self.setting = self.__DEFAULT_SETTING

        # music21でMusicXMLファイルを読み込むと、コードシンボルが各パートに生成されてしまうため、
        # 0番目以外のパートのコードシンボルを削除する
        # When reading a MusicXML file with music21, chord symbols are generated for each part,
        # so delete the chord symbols of parts other than 0th.
        measure_no: int = 1
        for part_no in range(1, len(self.score.parts)):
            while True:
                measure: Measure = self.score.parts[part_no].measure(measure_no)

                if measure == None:
                    break

                for ele in measure:
                    if isinstance(ele, ChordSymbol):
                        measure.remove(ele)
                measure_no += 1

        # 0番目のパートのコードシンボルを追加する
        # Add chord symbols to the 0th part
        key: Key = None
        measure_no = 1

        while True:
            measure: Measure = self.score.parts[0].measure(measure_no)
            if measure == None:
                break

            chords = measure.getElementsByClass(ChordSymbol)
            key_signature = measure.getElementsByClass(KeySignature)

            if len(key_signature) > 0:
                # Default: major
                key = key_signature[0].asKey(mode=key_type)
                self.modulation_count += 1

            self.modulation_list.append(key)

            for c in chords:
                tmp_chord = AnalyzedChord(c, key)
                tmp_chord.measure = measure_no
                self.chord_list.append(tmp_chord)

            measure_no += 1

    def analyze(self, mode: str | None = None):
        """ Analyze chord progression and melody

        Parameters
        ----------
        mode : str | None, optional
            * None: Default key
            * "major": Major key
            * "minor": Minor key
            * "relative": Relative key

        Returns
        -------
        (List[AnalyzedChord], List[AnalyzedNote])
            Analysis results
        """

        chord_result = super().analyze(mode)

        # メロディーの解析を行う
        # Analyze melody
        chord_index = 0

        for measure_no in range(1, len(self.modulation_list)):
            # 0番目のパートの中で、最も高い音をメロディー構成音として扱う
            # Treat the highest note in the 0th part as the melody note
            measure: Measure = self.score.parts[0].measure(
                measureNumber=measure_no,
                collect=("Note", "Chord", "ChordSymbol"))

            if measure == None:
                break

            flatten_measure = measure.flatten()

            if len(flatten_measure) == 0:
                continue

            # 小説内の全てのNoteを取得する
            # Get all Notes in the measure
            notes: list[Note] = []
            for ele in flatten_measure:
                if type(ele) == Chord:
                    for n in ele.notes:
                        n.offset = ele.offset
                        notes.append(n)

                elif type(ele) == Note:
                    notes.append(ele)

            # オフセットごとに高い音→低い音の順にソートする
            # Sort from high to low note for each offset
            notes.sort(key=lambda x: (x.offset, -x.pitch.midi))

            if len(notes) == 0:
                continue

            note_index = 0
            prev_note_offset = notes[0].offset
            tmp_midi = -1


            if chord_index < len(self.chord_list) - 1:
                # 1小節に含まれるコードが1つだけのとき、
                # When there is only one chord in a measure,
                if self.chord_list[chord_index + 1].measure != measure_no:
                    # 小節最後の音符のオフセットより少し大きな値を次のコードのオフセットとして扱う
                    # Treat a value slightly larger than the offset of the last note in the measure as the offset of the next chord
                    next_chord_offset = notes[-1].offset + 1
                else:
                    next_chord_offset = self.chord_list[chord_index + 1].chord.offset
            else:
                next_chord_offset = notes[-1].offset + 1

            # 各コードの間にあるノートを探し、オフセットが相異なる最も高い音をメロディー構成音として扱う
            # Find the notes between each chord and treat the highest note with different offsets as the melody note
            while note_index < len(notes):

                # N.C.の場合の処理
                # Processing for N.C.
                while ( note_index < len(notes) and
                        measure_no <= self.chord_list[chord_index].measure and
                        notes[note_index].offset < self.chord_list[chord_index].chord.offset):

                    # 最高音を探す
                    # Find the highest note
                    while note_index < len(notes) and prev_note_offset == notes[note_index].offset:

                        if tmp_midi < notes[note_index].pitch.midi:
                            tmp_midi = notes[note_index].pitch.midi
                            melody_note = AnalyzedNote(note=notes[note_index], chord=None, key=self.modulation_list[measure_no])

                        prev_note_offset = notes[note_index].offset
                        note_index += 1

                    if self.setting["print_analyzed_melody"]:
                        note_text_exp = music21.expressions.TextExpression(
                            f"{melody_note.interval_from_tonic}/{melody_note.interval_from_root}")
                        note_text_exp.placement = "below"
                        measure.insert(melody_note.note.offset, note_text_exp)
                    self.note_list.append(melody_note)

                    tmp_midi = -1
                    if note_index >= len(notes):
                        break
                    prev_note_offset = notes[note_index].offset

                # 今のコードと次のコードの間にある場合のノートについて調べる
                # Look at the notes between the current chord and the next chord
                while ( note_index < len(notes) and
                        notes[note_index].offset >= self.chord_list[chord_index].chord.offset and
                        notes[note_index].offset <  next_chord_offset):

                    # この処理は1つのoffsetごとに、必ず1回は実行される
                    # This process is executed at least once for each offset
                    while note_index < len(notes) and prev_note_offset == notes[note_index].offset:
                        # 最高音を探す
                        # Find the highest note
                        if tmp_midi < notes[note_index].pitch.midi:
                            tmp_midi = notes[note_index].pitch.midi
                            melody_note = AnalyzedNote(note=notes[note_index], chord=self.chord_list[chord_index])

                        prev_note_offset = notes[note_index].offset
                        note_index += 1

                    if self.setting["print_analyzed_melody"]:
                        note_text_exp = music21.expressions.TextExpression(
                            f"{melody_note.interval_from_tonic}/{melody_note.interval_from_root}")
                        note_text_exp.placement = "below"
                        measure.insert(melody_note.note.offset, note_text_exp)
                    self.note_list.append(melody_note)

                    tmp_midi = -1
                    if note_index >= len(notes):
                        break
                    prev_note_offset = notes[note_index].offset

                chord_index += 1
                # 1小節に含まれるコードが1つだけのとき、
                # When there is only one chord in a measure,
                if chord_index < len(self.chord_list) - 1:
                    if self.chord_list[chord_index + 1].measure != measure_no:
                        # 小節最後の音符のオフセットより少し大きな値を次のコードのオフセットとして扱う
                        # Treat a value slightly larger than the offset of the last note in the measure as the offset of the next chord
                        next_chord_offset = notes[-1].offset + 1
                    else:
                        next_chord_offset = self.chord_list[chord_index + 1].chord.offset
                else:
                    # chord_listの末尾の場合の処理
                    # Processing for the end of chord_list
                    next_chord_offset = notes[-1].offset + 1

        return chord_result, self.note_list



    def change_key(self, measure: int | list[int], key: Key, after_analyze: bool = False):
        """ Change key of chord_list \\
        When measures 1 through 8 are in C major and \\
        measures 9 through 16 are in G major, \\
        change_key(3, Key("G")) will cause measures 3 through 8 to be in G major.
        change_key([3, 4, 5], Key("G")) will cause measures 3 through 5 to be in G major.

        Parameters
        ----------
        measure : int | list[int]
            measure number
        key : Key
            key
        after_analyze : bool, optional
            If True, change the key of the chord_list after analyze(), by default False
        """

        pre_modified_key: Key = None

        if type(measure) == int:
            for c in self.chord_list:
                if c.measure == measure:
                    pre_modified_key = c.key
                    c.key = key
                    self.modulation_list[measure] = key

                elif c.measure > measure:
                    if c.key == pre_modified_key:
                        c.key = key
                        self.modulation_list[c.measure] = key
                    else:
                        break

        elif type(measure) == list:
            for measure_no in measure:
                for c in self.chord_list:
                    if c.measure == measure_no:
                        pre_modified_key = c.key
                        c.key = key
                        self.modulation_list[measure_no] = key
                    elif c.measure > measure_no:
                        break

        # 転調の回数を再計算する
        # Recalculate the number of modulations
        pre_key = self.modulation_list[1]
        self.modulation_count = 0
        for k in self.modulation_list:
            if k == None:
                continue

            elif k == pre_key:
                pre_key = k

            elif k != pre_key:
                self.modulation_count += 1
                pre_key = k

        if after_analyze:
            self.analyze()


    def export_MusicXML(self, file_name: str):
        """ Export MusicXML file from chord_list

        Parameters
        ----------
        file_name : str
            MusicXML file name (file path)
        """

        measure_no: int = 1
        chord_count: int = 0

        while True:
            measure: Measure = self.score.parts[0].measure(measure_no)
            if measure == None:
                break

            for ele in measure:
                if type(ele) == music21.harmony.ChordSymbol:
                    ch = self.chord_list[chord_count]

                    chord_text = ""
                    if ch.degree_name != "?":
                        chord_text = ch.degree_name + "\n"
                    if ch.dominant_motion == "start":
                        chord_text += self.setting["dominant_motion_start"] + "\n"
                    if ch.dominant_motion == "continue":
                        chord_text += self.setting["dominant_motion_continue"] + "\n"
                    if ch.dominant_motion == "end":
                        chord_text += self.setting["dominant_motion_end"] + "\n"

                    if ch.related_IIm == "start":
                        chord_text += self.setting["related_iim_start"] + "\n"
                    if ch.related_IIm == "end":
                        chord_text += self.setting["related_iim_end"] + "\n"

                    if ch.substitute_dominant_motion == "start":
                        chord_text += self.setting["substitute_dominant_motion_start"] + "\n"
                    if ch.substitute_dominant_motion == "continue":
                        chord_text += self.setting["substitute_dominant_motion_continue"] + "\n"
                    if ch.substitute_dominant_motion == "end":
                        chord_text += self.setting["substitute_dominant_motion_end"] + "\n"

                    if ch.conjunct_motion == "start":
                        chord_text += self.setting["conjunct_motion_start"] + "\n"
                    if ch.conjunct_motion == "continue":
                        chord_text += self.setting["conjunct_motion_continue"] + "\n"
                    if ch.conjunct_motion == "end":
                        chord_text += self.setting["conjunct_motion_end"] + "\n"
                    if ch.conjunct_motion == "end/start":
                        chord_text += self.setting["conjunct_motion_end"] + "\n"
                        chord_text += self.setting["conjunct_motion_start"] + "\n"

                    if ch.line_cliche == "start":
                        chord_text += self.setting["line_cliche_start"] + "\n"
                    if ch.line_cliche == "continue":
                        chord_text += self.setting["line_cliche_continue"] + "\n"
                    if ch.line_cliche == "end":
                        chord_text += self.setting["line_cliche_end"] + "\n"
                    if ch.line_cliche == "end/start":
                        chord_text += self.setting["line_cliche_end"] + "\n"
                        chord_text += self.setting["line_cliche_start"] + "\n"

                    # degree name用のテキストを作成 (最後の改行を削除)、改行だけの行を削除
                    # Create text for degree name (delete last line break), delete lines with only line breaks
                    chord_text_exp = music21.expressions.TextExpression(chord_text[0:-1].replace("\n\n", "\n"))
                    chord_text_exp.placement = "above"

                    # ele.offset: 小節内の位置 (Position within the measure)
                    measure.insert(ele.offset, chord_text_exp)
                    chord_count += 1

            measure_no += 1

        self.score.write(fmt=".musicxml", fp=file_name)

    def write(self, format: str, file_name: str):
        """ Write to any format file

        Parameters
        ----------
        format : str
            File format
            ex) "musicxml", "midi", "lily", "text"...
        file_name : str
            File name (file path)
        """
        self.score.write(fmt=format, fp=file_name)

    def export_setting(self, file_name: str):
        """ Export setting file (.ini)

        Parameters
        ----------
        file_name : str
            Setting file name (file path)
        """
        with open(file_name, "w", encoding="utf-8") as f:
            self.__setting_parser.write(f)

    def load_setting(self, file_name: str, section_name: str = "DEFAULT"):
        """ Load setting file (.ini)

        Parameters
        ----------
        file_name : str
            Setting file name (file path)
        """
        file_list = self.__setting_parser.read(file_name, encoding="utf-8")
        if len(file_list) == 0:
            raise FileNotFoundError(f"File not found: {file_name}")
        self.setting = self.__setting_parser[section_name]


if __name__ == "__main__":
    analyzer = MusicXMLAnalyzer("musicXML\sample.musicxml", "major", "src\setting.ini")
    analyzer.analyze()
    analyzer.export_MusicXML("result_sample/sample.musicxml")
    analyzer.export_csv("result_sample/sample.csv")

