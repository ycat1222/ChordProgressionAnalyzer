# -*- coding: utf-8 -*-

# クラスの中で自己のクラスのオブジェクトを利用できる
from __future__ import annotations

from music21.harmony import ChordSymbol, CHORD_TYPES
from music21.pitch import Pitch
from music21.key import Key

class AnalyzedChord:

    __measure: int       = None
    __chord: ChordSymbol = None
    __chord_name: str    = None
    __root_note: Pitch   = None
    __chord_type: str    = None
    __bass_note: Pitch   = None
    __key:  Key          = None

    __degree_name: str      = "?"
    __dominant_motion: str  = "?"
    __substitute_dominant_motion: str = "?"
    __related_IIm: str      = "?"
    __conjunct_motion: str  = "?"
    __line_cliche: str      = "?"
    __passing_diminished: str = "?"
    __pivot_chord: AnalyzedChord = None

    __NORMALIZATION_DICT = {
        " ": "",
        "♯": "#",
        "b": "-", "♭": "-",
        "△": "M",                     # major (7th) chord -> "M"
        "Ø": "ø", "φ": "ø", "Φ": "ø",  # Half-diminished chord -> "ø"
        "◯": "dim", "°": "dim",       # Diminished chord -> "dim"
        "on": "/"
    }

    def __init__(self, chord: str | ChordSymbol, key: str | Key):
        """ Convert from string to chord.

        Parameters
        ----
        chord : str | ChordSymbol
            Chord name string (For example, "Cb", "C#m7", "Cbb M7" and "C--7")

            Available characters:

                Sharp: #, ♯ (Do not use "+")

                Flat:  -, b, ♭

                Other:
                    Major: M7, maj7, △7
                    Minor: m, m7, mM7, m△7, m maj7, m7-5, m7b5, m7♭5 (Do not use "-")

                    Half-diminished: ø, Ø, φ, Φ, ø7, Ø7, φ7, Φ7, mb5, m♭5
                    Diminished: dim, o, °, ◯, m-5, dim7, o7, °7, ◯7

                    Augmented: aug, +
                    Suspended: sus4, 7sus4, sus2, 7sus2
                    6: 6, m6
                    Tension: 9, m9, 11, m11, 13, m13

        key_name : str |Key
            * Major key: For example, "C", "C#" and "Cb" (Uppercase)
            * Minor key: For example, "c", "c#" and "cb" (lowercase)
        """

        # Remove unnecessary spaces, "b" and "♭" replaced by "-"
        if type(chord) is str:
            for k in self.__NORMALIZATION_DICT:
                chord = chord.replace(k, self.__NORMALIZATION_DICT[k])

            # 最低音の退避 Save bass note
            # For example, "C7add9,11 on E" -> "C7/E"
            bass_tone = None
            if "/" in chord:
                if "add" in chord and chord.index("add") < chord.index("/"):
                    bass_tone = chord.split("/")[1].split("add")[0].split("omit")[0]
                elif "omit" in chord and chord.index("omit") < chord.index("/"):
                    bass_tone = chord.split("/")[1].split("add")[0].split("omit")[0]

            # add や omit の削除 Remove "add ..." and "omit ..."
            chord = chord.split("add")[0].split("omit")[0]

            if bass_tone != None:
                chord += "/" + bass_tone

            chord = ChordSymbol(chord)

        self.__chord_name = chord.figure
        self.__chord = chord

        if type(key) is str:
            for k in self.__NORMALIZATION_DICT:
                key = key.replace(k, self.__NORMALIZATION_DICT[k])
            key = Key(key)

        self.__chord.key = key
        self.__key = key

        self.__root_note = self.__chord.root()
        self.__bass_note = self.__chord.bass()

        # CHORD_TYPES = {"major": ["1,3,5", ["",   "M", "maj"]], ...}
        #              [chordKind = "major"] [1][0]
        self.__chord_type = CHORD_TYPES[self.__chord.chordKind][1][0]

        if self.__chord == None:
            raise ValueError(f"ValueError: {chord} is NOT supported chord.")

    @property
    def measure(self):
        return self.__measure
    @measure.setter
    def measure(self, measure: int):
        self.__measure = measure

    @property
    def chord(self):
        return self.__chord

    @property
    def chord_name(self):
        return self.__chord_name

    @property
    def root_note(self):
        return self.__root_note

    @property
    def chord_type(self):
        return self.__chord_type

    @property
    def bass_note(self):
        return self.__bass_note

    @property
    def key(self):
        return self.__key
    @key.setter
    def key(self, key: str | Key):
        if type(key) is str:
            key = Key(key)
        self.__key = key

    @property
    def degree_name(self):
        return self.__degree_name
    @degree_name.setter
    def degree_name(self, degree_name: str):
        self.__degree_name = degree_name

    @property
    def dominant_motion(self):
        """State of dominant motion

        Parameters
        ----------
        state : str
            * "?": This chord has not been analyzed.
            * "-": This chord is NOT related to the dominant motion.
            * "start": This chord is BEGINNING of the (extended) dominant motion.
            * "continue": This chord is in the PROCESS of the extended dominant motion.
            * "end": This chord is END of the (extended) dominant motion.
        """
        return self.__dominant_motion
    @dominant_motion.setter
    def dominant_motion(self, state: str):
        if state in ["?", "-", "start", "continue", "end"]:
            self.__dominant_motion = state
        else:
            raise ValueError(f"{state} is not supported state in dominant motion.")

    @property
    def substitute_dominant_motion(self):
        """State of substitute dominant motion

        Parameters
        ----------
        state : str
            * "?": This chord has not been analyzed.
            * "-": This chord is NOT related to the substitute dominant motion.
            * "start": This chord is BEGINNING of the substitute dominant motion.
            * "continue": This chord is in the PROCESS of the substitute dominant motion.
            * "end": This chord is END of the substitute dominant motion.
        """
        return self.__substitute_dominant_motion
    @substitute_dominant_motion.setter
    def substitute_dominant_motion(self, state: str):
        if state in ["?", "-", "start", "continue", "end"]:
            self.__substitute_dominant_motion = state
        else:
            raise ValueError(f"{state} is not supported state in substitute dominant motion.")

    @property
    def related_IIm(self):
        """State of related IIm

        Parameters
        ----
        state : str
            * "?": This chord has not been analyzed.
            * "-": This chord is NOT related to the related IIm.
            * "start": This chord is BEGINNING of the related IIm.
            * "end": This chord is END of the related IIm.
        """
        return self.__related_IIm
    @related_IIm.setter
    def related_IIm(self, state: str):

        if state in ["?", "-", "start", "end"]:
            self.__related_IIm = state
        else:
            raise ValueError(f"{state} is not supported state in related IIm.")

    @property
    def line_cliche(self):
        """ State of line cliche

        Parameters
        ----
        state : str
            * "?": This chord has not been analyzed.
            * "-": This chord is NOT related to the line cliche.
            * "start":     This chord is BEGINNING of the line cliche.
            * "continue":  This chord is in the PROCESS of the line cliche.
            * "end":       This chord is END of the line cliche.
            * "end/start": This chord is END of the line cliche and START of the next line cliche.
        """
        return self.__line_cliche
    @line_cliche.setter
    def line_cliche(self, state: str):

        if state in ["?", "-", "start", "continue", "end", "end/start"]:
            self.__line_cliche = state
        else:
            raise ValueError(f"{state} is not supported state in line cliche.")

    @property
    def conjunct_motion(self):
        """ State of conjunct motion (順次進行)

        Parameters
        ----
        state : str
            * "?": This chord has not been analyzed.
            * "-": This chord is NOT related to the conjunct motion.
            * "start":     This chord is BEGINNING of the conjunct motion.
            * "continue":  This chord is in the PROCESS of the conjunct motion.
            * "end":       This chord is END of the conjunct motion.
            * "end/start": This chord is END of the conjunct motion and START of the next conjunct motion.
        """
        return self.__conjunct_motion
    @conjunct_motion.setter
    def conjunct_motion(self, state: str):
        if state in ["?", "-", "start", "continue", "end", "end/start"]:
            self.__conjunct_motion = state
        else:
            raise ValueError(f"{state} is not supported state in conjunct motion.")

    @property
    def passing_diminished(self):
        """ State of passing diminished

        Parameters
        ----
        state : str
            * "?": This chord has not been analyzed.
            * "-":  This chord is NOT related to the passing diminished.
            * "start": This chord is BEGINNING of the passing diminished.
            * "end":   This chord is END of the passing diminished.
        """
        return self.__passing_diminished
    @passing_diminished.setter
    def passing_diminished(self, state: str):
        if state in ["?", "-", "start", "end"]:
            self.__passing_diminished = state
        else:
            raise ValueError(f"{state} is not supported state in passing diminished.")

    @property
    def pivot_chord(self) -> AnalyzedChord | None:
        """ Pivot chord before and after modulation

        Parameters
        -------
        pivot_chord : AnalyzedChord
            Pivot chord before and after modulation
        """
        return self.__pivot_chord
    @pivot_chord.setter
    def pivot_chord(self, analyzed_chord: AnalyzedChord):
        self.__pivot_chord = analyzed_chord


if __name__ == "__main__":
    try:
        c = AnalyzedChord(chord="Cbb△7 add b9/E-", key="Bbb")
        print(c.chord)
        print(c.root_note)
        print(c.bass_note)
        print(c.key)

        cc = ChordSymbol("Cm11")
        print(cc.chordKind)
        print(cc.pitchClasses)

        ch = ChordSymbol("D7")
        ch.key = "C"
        print(ch.chordKindStr)

        ch = ChordSymbol("F#7 add #9")
        print(ch.chordKindStr)


    except ValueError as e:
        print(e)
