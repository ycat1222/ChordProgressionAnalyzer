# -*- coding: utf-8 -*-
import pandas as pd
import copy

from music21.pitch import Pitch
from music21.key import Key

from AnalyzedChord import AnalyzedChord

class ChordProgressionAnalyzer:
    chord_list: list[AnalyzedChord] = []
    __is_analyzed: bool = False


    # Reference: 清水響著 コード理論大全
    # Major: P.99
    # Minor: P.110, 111
    __CHORD_TYPE_MAJOR_I      = ["", "maj7", "6", "M9", "M13", "sus", "sus2"] # sus = sus4
    __CHORD_TYPE_MAJOR_IIm    = ["m", "m7", "m6", "m9", "m13", "sus", "sus2"]
    __CHORD_TYPE_MAJOR_IIIm   = ["m", "m7", "m11", "sus"]
    __CHORD_TYPE_MAJOR_IV     = ["", "maj7", "6", "M9", "M13", "sus2"]
    __CHORD_TYPE_MAJOR_V      = ["", "7", "6", "9", "13", "sus", "sus2"]
    __CHORD_TYPE_MAJOR_VIm    = ["m", "m7", "m6", "m9", "m11", "sus", "sus2"]
    __CHORD_TYPE_MAJOR_VIImb5 = ["dim", "ø7", "ø11"]

    __CHORD_TYPE_MINOR_Im      = ["m", "m7", "m9", "m11", "sus", "sus2"]
    __CHORD_TYPE_MINOR_IImb5   = ["dim", "ø7", "ø11"]
    __CHORD_TYPE_MINOR_bIII    = ["", "maj7", "6", "M9", "M13", "sus", "sus2"]
    __CHORD_TYPE_MINOR_IVm     = ["m", "m7", "m6", "m9", "m13", "sus", "sus2"]
    __CHORD_TYPE_MINOR_Vm      = ["m", "m7", "m11", "sus"]
    __CHORD_TYPE_MINOR_V       = ["", "7", "9", "13", "sus"]
    __CHORD_TYPE_MINOR_bVI     = ["", "maj7", "6", "M9", "M13", "sus2"]
    __CHORD_TYPE_MINOR_bVII    = ["", "7", "6", "9", "13", "sus", "sus2"]

    __CHORD_TYPE_TONIC_FUNCTION = (__CHORD_TYPE_MAJOR_I + __CHORD_TYPE_MAJOR_VIm +
                                    __CHORD_TYPE_MINOR_Im + __CHORD_TYPE_MINOR_bIII)
    __CHORD_TYPE_DOMINANT_FUNCTION = (__CHORD_TYPE_MAJOR_V + __CHORD_TYPE_MINOR_V)

    def __init__(self, _chord_list: str | list[str], key_name: str):
        """ Initialize with a list of chords.

        Parameters
        ----------
        _chord_list : str | list[str]
            * str: "C F G/B C"
            * list[str]: ["C", "F", "G/B", "C"]
        """
        self.chord_list = []
        self.__is_analyzed = False

        if type(_chord_list) is str:
            _chord_list = _chord_list.split(" ")

        for ch in _chord_list:
            self.chord_list.append(AnalyzedChord(ch, key_name))

        self.__original_chord_list = copy.deepcopy(self.chord_list)

    def analyze(self, mode: str | None = None):
        """ Analyze chord progression

        Parameters
        ----------
        mode : str | None, optional
            * None: Default key
            * "major": Major key
            * "minor": Minor key
            * "relative": Relative key

        Returns
        -------
        List[AnalyzedChord]
            Analysis results
        """

        if self.__is_analyzed:
            self.__init_analyzed_results()

        if mode == "major":
            self.to_major_key()

        elif mode == "minor":
            self.to_minor_key()

        elif mode == "relative":
            self.to_relative_key()

        # 主要なコードにディグリーネームを付ける
        self.__assign_degree_names_to_basic_chords()

        # コード進行の解析を行う (文脈から)
        self.__analyze_chord_progression()

        self.__is_analyzed = True

        return self.chord_list

    def __init_analyzed_results(self):
        self.__is_analyzed = False

        for i in range(len(self.chord_list)):
            self.chord_list[i].degree_name = "?"
            self.chord_list[i].dominant_motion = "?"
            self.chord_list[i].substitute_dominant_motion = "?"
            self.chord_list[i].related_IIm = "?"
            self.chord_list[i].conjunct_motion = "?"
            self.chord_list[i].line_cliche = "?"
            self.chord_list[i].passing_diminished = "?"
            self.chord_list[i].pivot_chord = None

    def to_relative_key(self):
        """ Change to relative key
        """
        for i, ch in enumerate(self.chord_list):
            ch.key = ch.key.relative
            ch.chord.key = ch.key.relative
            self.chord_list[i] = ch

    def to_major_key(self):
        """ Change to major key
        """
        for i, ch in enumerate(self.chord_list):
            if ch.key.mode == "minor":
                ch.key = ch.key.relative
                ch.chord.key = ch.key.relative
                self.chord_list[i] = ch

    def to_minor_key(self):
        """ Change to minor key
        """
        for i, ch in enumerate(self.chord_list):
            if ch.key.mode == "major":
                ch.key = ch.key.relative
                ch.chord.key = ch.key.relative
                self.chord_list[i] = ch

    def restore_to_original_key(self):
        """ Restore to original key
        """
        self.chord_list = copy.deepcopy(self.__original_chord_list)

    def __assign_degree_names_to_basic_chords(self):
        for i in range(len(self.chord_list)):
            self.chord_list[i] = self.__assign_degree_name_to_basic_chord(self.chord_list[i])

    def __assign_degree_name_to_basic_chord(self, ch: AnalyzedChord):
        tonic_note_pitch_class = ch.key.pitches[0].pitchClass
        root_note_pitch_class = ch.root_note.pitchClass
        diff_tonic_root_pitch_class = (root_note_pitch_class - tonic_note_pitch_class)%12

        # Major Key
        if ch.key.mode == "major":
            # I, IM7
            if diff_tonic_root_pitch_class == 0:
                ch.related_IIm = "-"
                if ch.chord_type in self.__CHORD_TYPE_MAJOR_I:
                    ch.degree_name = "I" + ch.chord_type

            # IIm, IIm7
            elif diff_tonic_root_pitch_class == 2:
                if ch.chord_type in self.__CHORD_TYPE_MAJOR_IIm:
                    ch.degree_name = "II" + ch.chord_type

            # IIIm, IIIm7
            elif diff_tonic_root_pitch_class == 4:
                if ch.chord_type in self.__CHORD_TYPE_MAJOR_IIIm:
                    ch.degree_name = "III" + ch.chord_type

            # IV, IVM7
            elif diff_tonic_root_pitch_class == 5:
                ch.related_IIm = "-"
                if ch.chord_type in self.__CHORD_TYPE_MAJOR_IV:
                    ch.degree_name = "IV" + ch.chord_type

            # V, V7
            elif diff_tonic_root_pitch_class == 7:
                ch.related_IIm = "-"
                if ch.chord_type in self.__CHORD_TYPE_MAJOR_V:
                    ch.degree_name = "V" + ch.chord_type

            # VIm, VIm7
            elif diff_tonic_root_pitch_class == 9:
                if ch.chord_type in self.__CHORD_TYPE_MAJOR_VIm:
                    ch.degree_name = "VI" + ch.chord_type

            # VIIm-5, VIIm7-5
            elif diff_tonic_root_pitch_class == 11:
                if ch.chord_type in self.__CHORD_TYPE_MAJOR_VIImb5:
                    ch.degree_name = "VII" + ch.chord_type

            # IVm, IVm7 (Subdominant Minor)
            elif diff_tonic_root_pitch_class == 5:
                if ch.chord_type == "m":
                    ch.degree_name = "IVm"
                elif ch.chord_type == "m7":
                    ch.degree_name = "IVm7"

            # bVI, bVIM7 (Subdominant Minor)
            elif diff_tonic_root_pitch_class == 8:
                if ch.chord_type == "":
                    ch.degree_name = "bVI"
                elif ch.chord_type == "M7":
                    ch.degree_name = "bVIM7"

            # bVII, bVIIM7 (Subdominant Minor)
            elif diff_tonic_root_pitch_class == 10:
                if ch.chord_type == "":
                    ch.degree_name = "bVII"
                elif ch.chord_type == "M7":
                    ch.degree_name = "bVIIM7"

        if ch.key.mode == "minor":
            # Im, Im7
            if diff_tonic_root_pitch_class == 0:
                ch.related_IIm = "-"
                if ch.chord_type in self.__CHORD_TYPE_MINOR_Im:
                    ch.degree_name = "I" + ch.chord_type

            # IImb5, IIm7b5
            elif diff_tonic_root_pitch_class == 2:
                if ch.chord_type in self.__CHORD_TYPE_MINOR_IImb5:
                    ch.degree_name = "II" + ch.chord_type

            # bIII, bIIIm7
            elif diff_tonic_root_pitch_class == 3:
                ch.related_IIm = "-"
                if ch.chord_type in self.__CHORD_TYPE_MINOR_bIII:
                    ch.degree_name = "bIII" + ch.chord_type

            # IVm, IVm7
            elif diff_tonic_root_pitch_class == 5:
                if ch.chord_type in self.__CHORD_TYPE_MINOR_IVm:
                    ch.degree_name = "IV" + ch.chord_type

            # Vm, Vm7,  V, V7
            elif diff_tonic_root_pitch_class == 7:
                # Vm, Vm7
                if ch.chord_type in self.__CHORD_TYPE_MINOR_Vm:
                    ch.degree_name = "V" + ch.chord_type
                # V, V7 (Only minor key)
                elif ch.chord_type in self.__CHORD_TYPE_MINOR_V: #
                    ch.degree_name = "V" + ch.chord_type

            # bVI, bVIM7
            elif diff_tonic_root_pitch_class == 8:
                if ch.chord_type in self.__CHORD_TYPE_MINOR_bVI:
                    ch.degree_name = "bVI" + ch.chord_type

            # bVII, bVII7
            elif diff_tonic_root_pitch_class == 10:
                if ch.chord_type in self.__CHORD_TYPE_MINOR_bVII:
                    ch.degree_name = "bVII" + ch.chord_type

        return ch


    def __analyze_chord_progression(self):
        chord_num = len(self.chord_list)
        # First Chord
        _prev = None
        _now = self.chord_list[0]
        _next = self.chord_list[1]

        for i in range(chord_num):

            if _prev != None and len(_prev.chord.pitches) > 2 and len(_now.chord.pitches) > 2:
                _prev_tonic_pitch_class = _prev.key.pitches[0].pitchClass
                _prev_root_pitch_class = _prev.root_note.pitchClass
                _prev_bass_pitch_class = _prev.bass_note.pitchClass

                _now_tonic_pitch_class = _now.key.pitches[0].pitchClass
                _now_root_pitch_class = _now.root_note.pitchClass
                _now_bass_pitch_class = _now.bass_note.pitchClass

                _prev_diff_pitch_class = (_prev_root_pitch_class - _prev_tonic_pitch_class)%12
                # I -> IV, bIII -> bVI is not dominant motion
                # I -> #I is not substitute dominant motion
                # 0: I and Im (Major and Minor key)
                # 9: VIm (Major key)
                # 3: bIII (Minor key)
                # Not (Tonic pitch class ∩ Tonic chord type) -> Not (Tonic function chord)
                if not (_prev_diff_pitch_class in [0, 9, 3] and
                        _prev.chord_type in self.__CHORD_TYPE_TONIC_FUNCTION):

                    # Dominant motion
                    if ( (_prev_root_pitch_class - _now_root_pitch_class)%12 == 7  and # Perfect 5th
                        _prev.chord_type in ["", "7"]): # Dominant chord (major or 7th)

                        if _prev.dominant_motion == "?": # Dominant motion
                            _prev.dominant_motion = "start"
                            if _now.degree_name not in ["I",  "IM7", "I6",  "IM9", "IM13",
                                                        "Im", "Im7", "Im9", "Im11"]:

                                if _prev.chord_type == "":
                                    _prev.degree_name = f"V/{_now.degree_name}" # V/◯
                                elif _prev.chord_type == "7":
                                    _prev.degree_name = f"V7/{_now.degree_name}" # V7/◯

                        else: # Extended or Secondary dominant motion
                            _prev.dominant_motion = "continue"

                        _now.dominant_motion = "end"

                    # Substitute Dominant Motion
                    elif ( (_prev_root_pitch_class - _now_root_pitch_class)%12 == 1 and
                            _prev.chord_type in self.__CHORD_TYPE_DOMINANT_FUNCTION): # Substitute dominant chord (major or 7th)

                        if _prev.substitute_dominant_motion == "?":
                            _prev.substitute_dominant_motion = "start"
                            if _prev.chord_type == "":
                                _prev.degree_name = f"subV/{_now.degree_name}"
                            elif _prev.chord_type == "7":
                                _prev.degree_name = f"subV7/{_now.degree_name}"
                        else:
                            _prev.substitute_dominant_motion = "continue"

                        _now.substitute_dominant_motion = "end"

                # Passing diminished approach
                if ( (_now_root_pitch_class - _prev_root_pitch_class)%12 == 1 and
                    _prev.chord_type in ["dim", "dim7", "ø7"]):

                    if _prev.passing_diminished == "?":
                        _prev.passing_diminished = "start"

                    _now.passing_diminished = "end"

                if _next is not None and len(_next.chord.pitches) > 2:
                    _next_tonic_pitch_class = _next.key.pitches[0].pitchClass
                    _next_root_pitch_class = _next.root_note.pitchClass
                    _next_bass_pitch_class = _next.bass_note.pitchClass

                    # Conjunct motion
                    # Index of the root note in the same key
                    matched_note = _prev.key.match([_prev.bass_note, _now.bass_note, _next.bass_note])
                    if ( matched_note["notMatched"] == [] and
                        _prev.key == _now.key and _now.key == _next.key):

                        _prev_i = self.__index_of_note_in_key(_prev.key, _prev.bass_note)
                        _now_i  = self.__index_of_note_in_key(_prev.key, _now.bass_note)
                        _next_i = self.__index_of_note_in_key(_prev.key, _next.bass_note)

                        # Conjunct motion (順次進行、Down 下行)
                        if ((_prev_i - _now_i)%7 == 1 and (_now_i - _next_i)%7 == 1 and (_prev_i - _next_i)%7 == 2):
                            if _prev.conjunct_motion == "?":
                                _prev.conjunct_motion = "start"
                            elif _prev.conjunct_motion == "end":
                                _prev.conjunct_motion = "end/start"
                            else:
                                _prev.conjunct_motion = "continue"

                            _now.conjunct_motion = "continue"
                            _next.conjunct_motion = "end"

                        # Conjunct motion (順次進行、Down 上行)
                        if ((_now_i - _prev_i)%7 == 1 and (_next_i - _now_i)%7 == 1 and (_next_i - _prev_i)%7 == 2):
                            if _prev.conjunct_motion == "?":
                                _prev.conjunct_motion = "start"
                            elif _prev.conjunct_motion == "end":
                                _prev.conjunct_motion = "end/start"
                            else:
                                _prev.conjunct_motion = "continue"

                            _now.conjunct_motion = "continue"
                            _next.conjunct_motion = "end"

                    # Line cliche
                    # Line cliche (Down 下行)
                    # C B Bb -> (C - B) == 1 && (B - Bb) == 1 && (C - Bb) == 2
                    if( (_prev_bass_pitch_class - _now_bass_pitch_class)%12 == 1 and
                        (_now_bass_pitch_class - _next_bass_pitch_class)%12 == 1 and
                        (_prev_bass_pitch_class - _next_bass_pitch_class)%12 == 2):

                        if _prev.line_cliche == "?":
                            _prev.line_cliche = "start"
                        elif _prev.line_cliche == "end":
                            _prev.line_cliche = "end/start"
                        else:
                            _prev.line_cliche = "continue"

                        _now.line_cliche = "continue"
                        _next.line_cliche = "end"

                    # Line cliche (Down, 3rd)
                    elif( (_prev.chord.pitches[1].pitchClass - _now.chord.pitches[1].pitchClass)%12 == 1 and
                        (_now.chord.pitches[1].pitchClass - _next.chord.pitches[1].pitchClass)%12 == 1 and
                        (_prev.chord.pitches[1].pitchClass - _next.chord.pitches[1].pitchClass)%12 == 2):

                        if _prev.line_cliche == "?":
                            _prev.line_cliche = "start"
                        elif _prev.line_cliche == "end":
                            _prev.line_cliche = "end/start"
                        else:
                            _prev.line_cliche = "continue"

                        _now.line_cliche = "continue"
                        _next.line_cliche = "end"

                    # Line cliche (Down, 5th)
                    elif( (_prev.chord.pitches[2].pitchClass - _now.chord.pitches[2].pitchClass)%12 == 1 and
                        (_now.chord.pitches[2].pitchClass - _next.chord.pitches[2].pitchClass)%12 == 1 and
                        (_prev.chord.pitches[2].pitchClass - _next.chord.pitches[2].pitchClass)%12 == 2):

                        if _prev.line_cliche == "?":
                            _prev.line_cliche = "start"
                        elif _prev.line_cliche == "end":
                            _prev.line_cliche = "end/start"
                        else:
                            _prev.line_cliche = "continue"

                        _now.line_cliche = "continue"
                        _next.line_cliche = "end"

                    # Line cliche (Up 上行)
                    # C C# D -> (C# - C) == 1 && (D - C#) == 1 && (D - C) == 2
                    if( (_now_bass_pitch_class - _prev_bass_pitch_class)%12 == 1 and
                        (_next_bass_pitch_class - _now_bass_pitch_class)%12 == 1 and
                        (_next_bass_pitch_class - _prev_bass_pitch_class)%12 == 2):

                        if _prev.line_cliche == "?":
                            _prev.line_cliche = "start"
                        elif _prev.line_cliche == "end":
                            _prev.line_cliche = "end/start"
                        else:
                            _prev.line_cliche = "continue"

                        _now.line_cliche = "continue"
                        _next.line_cliche = "end"

                    # Line cliche (Up, 3rd)
                    elif( (_now.chord.pitches[1].pitchClass - _prev.chord.pitches[1].pitchClass)%12 == 1 and
                        (_next.chord.pitches[1].pitchClass - _now.chord.pitches[1].pitchClass)%12 == 1 and
                        (_next.chord.pitches[1].pitchClass - _prev.chord.pitches[1].pitchClass)%12 == 2):

                        if _prev.line_cliche == "?":
                            _prev.line_cliche = "start"
                        elif _prev.line_cliche == "end":
                            _prev.line_cliche = "end/start"
                        else:
                            _prev.line_cliche = "continue"

                        _now.line_cliche = "continue"
                        _next.line_cliche = "end"

                    # Line cliche (Up, 5th)
                    elif( (_now.chord.pitches[2].pitchClass - _prev.chord.pitches[2].pitchClass)%12 == 1 and
                        (_next.chord.pitches[2].pitchClass - _now.chord.pitches[2].pitchClass)%12 == 1 and
                        (_next.chord.pitches[2].pitchClass - _prev.chord.pitches[2].pitchClass)%12 == 2):

                        if _prev.line_cliche == "?":
                            _prev.line_cliche = "start"
                        elif _prev.line_cliche == "end":
                            _prev.line_cliche = "end/start"
                        else:
                            _prev.line_cliche = "continue"

                        _now.line_cliche = "continue"
                        _next.line_cliche = "end"

                    # Modulation (_prev _now | _next)
                    #                        ^ Modulation timing
                    if _now.key != _next.key:
                        # Analyze chords _prev and _now in _next key
                        _prev.pivot_chord = self.__assign_degree_name_to_basic_chord(AnalyzedChord(_prev.chord_name, _next.key))
                        _now.pivot_chord  = self.__assign_degree_name_to_basic_chord(AnalyzedChord(_now.chord_name, _next.key))

                        # Analyze chords _next in _prev key
                        _next.pivot_chord = self.__assign_degree_name_to_basic_chord(AnalyzedChord(_next.chord_name, _prev.key))

                    self.chord_list[i+1] = _next
                    # End of if _next is not None:

                self.chord_list[i-1] = _prev
                # End of if _prev is not None:

            self.chord_list[i] = _now

            _prev = self.chord_list[i]

            if i + 1 < chord_num:
                _now  = self.chord_list[i+1]
            else:
                _now = None

            if i + 2 < chord_num:
                _next = self.chord_list[i+2]
            else:
                _next = None


        for i in range(chord_num):
            # Related IIm(7)
            # Dm -> G -> C
            if i > 1 and i < chord_num:
                if ( (self.chord_list[i - 1].root_note.pitchClass - self.chord_list[i].root_note.pitchClass)%12 == 7  and # Perfect 5th
                    self.chord_list[i - 1].chord_type in ["m", "m7", "m6", "m9", "m11", "m13", "dim", "ø7"] and  # Minor chord (related IIm(7))
                    self.chord_list[i].dominant_motion != "?"):

                    self.chord_list[i - 1].related_IIm = "start"
                    self.chord_list[i].related_IIm = "end"

            if self.chord_list[i].dominant_motion == "?":
                self.chord_list[i].dominant_motion = "-"

            if self.chord_list[i].substitute_dominant_motion == "?":
                self.chord_list[i].substitute_dominant_motion = "-"

            if self.chord_list[i].conjunct_motion == "?":
                self.chord_list[i].conjunct_motion = "-"

            if self.chord_list[i].line_cliche == "?":
                self.chord_list[i].line_cliche = "-"

            if self.chord_list[i].passing_diminished == "?":
                self.chord_list[i].passing_diminished = "-"

    @staticmethod
    def __index_of_note_in_key(key: Key, pitch: Pitch) -> int:
        """Pitch to index of the key

        For example, key == "C",
        pitch == "C3" -> 0, pitch == "D3" -> 1, pitch == "G2" -> 4

        Parameters
        ----------
        key : Key
            Key of the note
        pitch : Pitch
            Pitch of the note

        Returns
        -------
        index : int
            For example, key == "C",
                pitch == "C3" -> 0
                pitch == "D3" -> 1
                pitch == "G2" -> 4
                ...
                pitch == "C#" -> 7 (C# is not in C major key)
        """

        pitch_list = key.getPitches()
        index: int = 0

        for index, p in enumerate(pitch_list):
            if (pitch.midi - p.midi)%12 == 0:
                return index

        return 7

    def append_chord(self, chord: AnalyzedChord):
        """Append A chord to the chord_list

        Parameters
        ----------
        chord : AnalyzedChord
        """
        self.chord_list.append(chord)

    def append_chord_list(self, chords: str | list[str], key: str):
        """Append chords to the chord_list

        Parameters
        ----------
        chords : str| list[str]
            str : For example, "C Dm G C"
            list : For example, ["C", "Dm", "G", "C"]
        key : str
            Key of the chords
        """
        if type(chords) is str:
            chords = chords.split(" ")

        for c in chords:
            self.chord_list.append(AnalyzedChord(c, key))


    def export_csv(self, file_name: str):
        """ Export analyzed result to CSV file

        Parameters
        ----------
        file_name : str
            File name of CSV file
        """
        analyzed_data: list[list[str|int]] = []

        for i in range(len(self.chord_list)):
            ch = self.chord_list[i]
            if ch.pivot_chord is None:
                analyzed_data.append([
                    i + 1, ch.chord_name, ch.key,
                    ch.degree_name, ch.dominant_motion, ch.substitute_dominant_motion, ch.related_IIm, ch.conjunct_motion, ch.line_cliche, ch.passing_diminished, "-"
                ])
            else:
                analyzed_data.append([
                    i + 1, ch.chord_name, ch.key,
                    ch.degree_name, ch.dominant_motion, ch.substitute_dominant_motion, ch.related_IIm, ch.conjunct_motion, ch.line_cliche, ch.passing_diminished, ch.pivot_chord.degree_name
                ])

        df = pd.DataFrame(
            analyzed_data,
            columns=["No.", "chord name", "key",
                    "degree name", "dominant motion", "substitute dominant motion", "related IIm", "conjunct motion", "line cliche", "passing diminished", "pivot chord"])

        df.to_csv(file_name, encoding="utf-8", index=False)


if __name__ == "__main__":
    chord_list = "C A7 Dm7 G7 C F C#7 C D7 G7 C/E F G7 C F F#dim G C"

    analyzer = ChordProgressionAnalyzer(chord_list, "C")

    analyzer.analyze()
    analyzer.export_csv("result_sample/result.csv")

    chord_list2_in_G = "G C C#dim7 D7 G/B C D7 G"
    analyzer.append_chord_list(chord_list2_in_G, "G")
    analyzer.analyze()
    analyzer.export_csv("result_sample/result2.csv")

    analyzer.analyze(mode="relative")
    analyzer.export_csv("result_sample/result3.csv")

    # d = RomanNumeral("I", Key("C"))
    # k = Key("C")
    # d = RomanNumeral("I", k)
    # print(d)
    # print(k)
