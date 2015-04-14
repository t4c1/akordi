__author__ = 'Tadej'
import guitarpro
print "start"
a=guitarpro.parse(r"Guns N Roses - Patience.gp5")
for track in a.tracks[0:1]:
    print track,track.name
    for measure in track.measures:
        #print "\t",measure
        for voice in measure.voices:
            #print "\t\t",voice
            for beat in voice.beats:
                d=beat.duration
                #print "\t\t",beat.start,beat.index,beat.octave,d.value
                for note in beat.notes:
                    print "\t\t\t",note.value,note.velocity,note.string,note.durationPercent,note.realValue
print note.beat

#start cetrtinka=960
#1/duration je trajanje v celinkah
#note.realvalue - 49 = C1   1=pol tona          =MIDI zapis