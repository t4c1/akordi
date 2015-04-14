import guitarpro,music21

def flatten(gpfile):
    res=[]
    for track in gpfile.tracks:
        res.append([])
        for measure in track.measures:
            for voice in measure.voices:
                for beat in voice.beats:
                    res[-1].append(beat)
    return res

def filterGP(flattenedSong):
    """
    iz komada poisce samo instrumente, ki igrajo akorde
    za gp
    """
    res=[]
    for track in flattenedSong[:]:
        for beat in track[:10]:#preveri samo prvih 10 tonov/akordov
            if len(beat.notes)>3:
                res.append(track)
                break
    return res

def filterM21(song):
    res=music21.stream.Score()
    for part in song:
        for chord in part.notes[:100]:
            if isinstance(chord,music21.chord.Chord):
                res.append(part)
                break
    return res

def gp2music21(track):
    """
    dela, ampak zaenkrat se nekaj manjka...
    """
    res=music21.stream.Part()
    res.append(music21.instrument.AcousticGuitar())
    for beat in track:
        pitches=[]
        for note in beat.notes:
            d=music21.duration.Duration(velocity=note.velocity)
            n=music21.note.Note(note.realValue,duration=d)
            n.quarterLength=4.0/beat.duration.value
            pitches.append(n)
        c=music21.chord.Chord(pitches)
        res.append(c)
    return res

def test_gp():
    import time
    t=time.time()
    gpfile=guitarpro.parse(r"Guns N Roses - Patience.gp5")
    print "open:", time.time()-t
    t=time.time()
    flat=flatten(gpfile)
    print "flatten:",time.time()-t
    t=time.time()
    song=music21.stream.Score()
    for track in flat:
        song.append(gp2music21(track))
    print "convert:",time.time()-t
    t=time.time()
    song.show("midi")
    print "midi:",time.time()-t
    t=time.time()
    #gp2music21(filter(flatten(gpfile))[1]).show("midi")

def test_midi():
    song=music21.converter.parse("Guns N Roses - Patience.mid")
    filterM21(song).show("midi")

if __name__=="__main__":
    test_midi()