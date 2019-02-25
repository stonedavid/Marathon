
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 08:03:51 2019
Marathon is a program to automatically create a 50% microrhythm between two
rhythmic patterns in MIDI.
Maraton takes a MIDI file by the name "marathon_in.mid" located in the same
folder as itself containing two MIDI tracks of same length and number of notes.
Marathon then creates the file "marathon_out.mid" by calculating the average
duration of each note pair in the two tracks and copying the channel, velocity,
and pitch pattern of the first track.
Known issues:
    —Does not work properly with chords and multiple voices on one track.
    —May behave unexpectedly with time signatures or tempo changes and other
        more complex actions.
Suggestions:
    —Create simple MIDI files with a DAW to feed the program.
    —Create monophonic tracks. If you want multiphonic results, I suggest you
        create a MIDI file for each voice. Remember to write the same number of
        notes in each track if you want similar results. You can then manually
        recombine the different output files into one track on a DAW.
    —Tempo or time signature change, note bends, and other more complex actions
        are to be avoided for better results. You can apply those changes
        manually on the output track.
@author: DaveTremblay
"""

import midi
import sys

file_in = "marathon_in.mid"
file_out = "marathon_out.mid"

read_1 = midi.read_midifile(file_in)

track1 = str(read_1).split("midi.Track(\\")[2]
track2 = str(read_1).split("midi.Track(\\")[3]

notes1 = str(track1).split("),")
notes2 = str(track2).split("),")


if len(notes1)-1 == len(notes2):

    fm = str(read_1).split("format=")[1].split(", resolution")[0]
    rm = str(read_1).split("resolution=")[1].split(", tracks")[0]
    dm = str(read_1).split("data=[")[1].split("]")[0]

    pat = midi.Pattern(format=int(fm), resolution=int(rm))
    tra = midi.Track()
    pat.append(tra)

    #
    # Convert onset ticks to absolute values
    #

    onsetListA = []
    pitchList = []
    velList = []
    runningTickCounterA = 0

    onsetListB = []
    runningTickCounterB = 0

    for event in notes1:
        print(event)
        if "Note" in event:
            if "NoteOff" in event or event.split(", ")[-1] == "0]":
                print("noteoff")
                runningTickCounterA += int(event.split("tick=")[1].split(", channel")[0])
                
            else:
                
                runningTickCounterA += int(event.split("tick=")[1].split(", channel")[0])
                onsetListA.append(runningTickCounterA)
                pitchList.append(event.split("data=[")[1].split(", ")[0])
                velList.append(event.split("data=[")[1].split(", ")[1].split("]")[0])

    for event in notes2:
        if "Note" in event:
            if "NoteOff" in event or event.split(", ")[-1] == "0]":

                print("noteoff")
                runningTickCounterB += int(event.split("tick=")[1].split(", channel")[0])
                
            else:

                runningTickCounterB += int(event.split("tick=")[1].split(", channel")[0])
                onsetListB.append(runningTickCounterB)

    #
    # Interpolate onsets with weight ( 0.0 = )
    #

    weight = float(sys.argv[1])

    w1 = 100*(1-weight)
    w2 = 100*weight
    w3 = w1 + w2

    interpOnsets = [int(((o1 * w1) + (o2 * w2))/w3) for o1, o2 in zip(onsetListA, onsetListB)]


    #
    # Create new midi NoteOns using interpolated values and original pitches
    #


    for i,pitch in enumerate(pitchList):

        if i:

            relativeTick = interpOnsets[i] - interpOnsets[i-1]

            noteoff = midi.NoteOffEvent(tick=relativeTick-1, channel=0, data=[int(pitchList[i-1]), 0])
            tra.append(noteoff)

            noteon = midi.NoteOnEvent(tick=1, channel=0, data=[int(pitch), int(velList[i])])
            tra.append(noteon)
            
            if i == len(pitchList) - 1:
                noteoff = midi.NoteOffEvent(tick=500, channel=9, data=[int(pitch), 0])
                tra.append(noteoff)
        
        else:
   
            noteon = midi.NoteOnEvent(tick=interpOnsets[i], channel=0, data=[int(pitchList[i]), int(velList[i])])
            tra.append(noteon)

        

    trackend = midi.EndOfTrackEvent(tick=1)
    tra.append(trackend)
    midi.write_midifile(file_out, pat)

else:
    print("Error: The number of notes in the two tracks is different.")


"""for event in notes2:
        #print(event)
        #print(event.split(", ")[-1])
        #print("\n")
        eventName = event.split(".")[1].split("(")[0]
        if eventName == "NoteOnEvent" and event.split(", ")[-1] == "0]":
            tick1 = int(notes1[e].split("tick=")[1].split(", channel")[0])
            tick2 = int(notes2[e].split("tick=")[1].split(", channel")[0])
            tickm = int((w1 * tick1) + (w2 * tick2))
            cm = int(notes1[e].split("channel=")[1].split(", data")[0])
            dm1on = notes1[e-1].split("data=[")[1].split(", ")[0]
            dm1off = notes1[e].split("data=[")[1].split(", ")[0]
            dm2on = notes1[e-1].split("data=[")[1].split(", ")[1].split("]")[0]
            dm2off = notes1[e].split("data=[")[1].split(", ")[1].split("]")[0]
            noteon = midi.NoteOnEvent(tick=0, channel=cm, data=[int(dm1on), int(dm2on)])
            tra.append(noteon)
            noteoff = midi.NoteOffEvent(tick=tickm, channel=cm, data=[int(dm1off), int(dm2off)])
            tra.append(noteoff)
            e += 1
        else:
            e += 1
    trackend = midi.EndOfTrackEvent(tick=1)
    tra.append(trackend)
    midi.write_midifile(file_out, pat)""" 
