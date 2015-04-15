import guitarpro,music21,random,copy

def myBeatEg(self,other):
    #print 1
    return self.duration.value==other.duration.value and frozenset(self.notes)==frozenset(other.notes)

def myBeatHash(self):
    #print "h1"
    return hash((self.duration.value,frozenset(self.notes)))

def myNoteEq(self,other):
    #print 2
    return self.realValue==other.realValue and self.velocity==other.velocity

def myNoteHash(self):
    #print "h2"
    return hash((self.realValue,self.velocity))

#pri preverjanju enakosti akordov so se vsi primerjali kot različni, zato je bilo treba po svoje definirati funkcije za primerjanje in izracun hasha
guitarpro.base.Note.__eq__=myNoteEq
guitarpro.base.Note.__hash__=myNoteHash
guitarpro.base.Beat.__eq__=myBeatEg
guitarpro.base.Beat.__hash__=myBeatHash

def myChordEq(self,other):
    return isinstance(other,self.__class__) and \
           frozenset(self.pitches)==frozenset(other.pitches) and \
           self.duration.quarterLength==other.duration.quarterLength# and \
           #self.duration.velocity==other.duration.velocity

def myChordHash(self):
    return hash((frozenset(self.pitches),self.duration.quarterLength))#,self.duration.velocity

music21.chord.Chord.__eq__=myChordEq
music21.chord.Chord.__hash__=myChordHash
# music21.note.Note.__eq__=myChordEq
# music21.note.Note.__hash__=myChordHash


def flatten(gpfile):
    """
    izlusci vse note(in akorde) iz guitarpro file objekta v seznam
    """
    res=[]
    for track in gpfile.tracks:
        res.append([])
        for measure in track.measures:
            for voice in measure.voices:
                for beat in voice.beats:
                    if beat.notes:
                        res[-1].append(beat)
    return res

def filterGP(flattenedSong):
    """
    iz komada poisce samo instrumente, ki igrajo akorde
    za pyguitarpro
    """
    res=[]
    for track in flattenedSong[:]:
        res.append([])
        for beat in track:
            if len(beat.notes)>3:
                res[-1].append(beat)
                #break
    return res

def filterM21(song):
    """
    iz music21 pesmi poisce sfiltrira vse akorde
    """
    res=music21.stream.Score()
    for part in song:
        for chord in part.notes:
            if isinstance(chord,music21.chord.Chord):
                res.append(chord)
                #break
    return res

def gp2music21(track):
    """
    spremeni zapis iz pyguitarpro objektov v music21 objekte
    """
    res=music21.stream.Part()
    res.append(music21.instrument.Xylophone())#AcousticGuitar()
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



def makeMat2(songs,hist=1):
    """
    zgradi "matriko" prehodov med stanji
    """
    mat={}
    vhodi={tuple([None]*hist):0}
    izhodi={}
    for song in songs:
        locHist=tuple([None]*hist)
        for chord in song:
            if locHist not in mat:
                mat[locHist]={}
            if chord not in mat[locHist]:
                mat[locHist][chord]=1
            else:
                mat[locHist][chord]+=1
            locHist=tuple(locHist[1:]+(chord,))
    for i in mat:
        s=float(sum(mat[i].values()))
        for j in mat[i]:
            mat[i][j]/=s
    return mat

def generate(mat,hist,dolzina):
    """
    zgenerira zaporedje akordov zeljene dolzine iz matrike prehodov
    hist je stevilo akordov glede na katere generira naslednjega
    """
    locHist=tuple([None]*hist)
    res=[]
    try:
        for i in range(dolzina):
            rnd=random.random()
            for akord in mat[locHist]:
                rnd-=mat[locHist][akord]
                if rnd<=0:
                    locHist=tuple(locHist[1:]+(akord,))
                    if locHist not in mat:
                        locHist=tuple([None]*hist)
                        print 1,
                    res.append(akord)
                    break
            else:
                raise Exception,(rnd,locHist)
    except KeyError:
        print locHist,"\n",res,"\n",mat
        raise
    return res

def test_midi():
    """
    testna funkcija, za delovanje z branjem midi file-ov
    nakaj tukaj ne dela popolnoma
    """
    songs=[]
    for name in ("ACDC - Back In Black.mid","Guns N Roses - Patience.mid","Guns N Roses - Knockin on Heavens door.mid","Guns N Roses - Knockin on Heavens door.mid")[1:2]:
        song=music21.converter.parse(name)
        print "opened",len(song.notes)
        #song.parts[3].show("midi")
        f=filterM21(song)
        #f.show("midi")
        print "filtered",len(f.notes),len(set(f.notes))
        songs.append(f)
    hist=3
    mat=makeMat2(songs,hist)
    print "mat",[len(mat[i]) for i in mat]
    res=generate(mat,hist,50)
    print "res len",len(res)
    song=music21.stream.Score(copy.copy(i) for i in res)
    song.insert(0,music21.instrument.AcousticGuitar())
    song.show("midi")
    #song.show("text")

def test_gp():
    """
    testna funkcija, za delovanje z branjem guitar pro file-ov
    nakaj tukaj ne dela popolnoma
    """
    songs=[]
    for name in ("ACDC - Back In Black.gp5","Guns N Roses - Patience.gp5","Guns N Roses - Knockin on Heavens door.gp5","Deep Purple - Smoke On The Water.gp5"):
        gpfile=guitarpro.parse(name)
        flat=flatten(gpfile)
        songs+=filterGP(flat)
        print "opened",name
    hist=2
    mat=makeMat2(songs,hist)#
    print mat
    res=generate(mat,hist,50)
    gp2music21(res).show("midi")

if __name__=="__main__":
    test_gp()

print