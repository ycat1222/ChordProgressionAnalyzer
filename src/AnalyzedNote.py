# -*- coding: utf-8 -*-

from music21.harmony import ChordSymbol
from music21.key import Key
from music21.note import Note
from music21.interval import Interval

from AnalyzedChord import AnalyzedChord

class AnalyzedNote:

    __note: Note
    __key: Key
    __chord: AnalyzedChord | None
    __measure: int
    __interval_from_tonic: Interval
    __interval_from_root: Interval | None

    def __init__(self, note: Note, chord: ChordSymbol | AnalyzedChord | None, key: Key | None = None):
        """ AnalyzedNote constructor

        Parameters
        ----------
        note : Note
            Note to be analyzed

        chord : ChordSymbol | AnalyzedChord | None
            When chord's type is AnalyzedChord, key is NOT required.

        key : Key
            When chord's type is ChordSymbol or None, key is required.
        """
        if(type(chord) == ChordSymbol):
            if(key is None):
                raise ValueError("Key is required when chord's type is ChordSymbol")
            chord = AnalyzedChord(chord, key)

        if(type(chord) == AnalyzedChord):
            key = chord.key

        if chord == None and key == None:
            raise ValueError("Key is required when chord is None")

        self.__note = note
        self.__key = key
        self.__chord = chord

        if key.tonic.midi < note.pitch.midi:
            self.__interval_from_tonic = Interval(pitchStart=key.tonic, pitchEnd=note.pitch)
        else:
            tonic = key.tonic
            # tonicの音がnoteよりも絶対に低くなるようにする (C-3のような音は、本来midiでは負の値になる)
            # この場合、music21では、midiは必ず正の値になるが、psは負の値になる
            # Tonic tone must be lower than note tone (e.g. C-3 is originally negative value in midi)
            # In this music21, midi is always positive value, but ps is negative value.
            tonic.octave = -3
            self.__interval_from_tonic = Interval(pitchStart=tonic, pitchEnd=note.pitch)

        if chord is not None:
            if  chord.chord.root().midi < note.pitch.midi:
                self.__interval_from_root = Interval(pitchStart=chord.chord.root(), pitchEnd=note.pitch)
            else:
                root = chord.chord.root()
                root.octave = -3
                self.__interval_from_root = Interval(pitchStart=root, pitchEnd=note.pitch)
        else:
            self.__interval_from_root = None

    @property
    def note(self):
        return self.__note

    @property
    def key(self):
        return self.__key

    @property
    def chord(self):
        return self.__chord

    @property
    def measure(self):
        return self.__measure
    @measure.setter
    def measure(self, measure: int):
        self.__measure = measure

    @property
    def interval_from_tonic(self) -> str:
        return self.__interval_from_tonic.simpleName

    @property
    def interval_from_root(self) -> str:
        if self.__interval_from_root is None:
            return ""
        return self.__interval_from_root.simpleName


if __name__ == '__main__':
    note1 = Note("C4")
    note2 = Note("F#")
    key = Key("C")
    chord = ChordSymbol("C")

    analyzed_note = AnalyzedNote(note1, chord, key)
    print(f"Interval from tonic: {analyzed_note.interval_from_tonic}")
    print(f"Interval from root: {analyzed_note.interval_from_root}")

    analyzed_note = AnalyzedNote(note2, chord, key)
    print(f"Interval from tonic: {analyzed_note.interval_from_tonic}")
    print(f"Interval from root: {analyzed_note.interval_from_root}")
