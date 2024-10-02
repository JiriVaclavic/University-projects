#!/usr/bin/env python3
"""
Dynamic analyser of a cart controller.
"""

MAX_CAPACITY = 150
MAX_SLOTS = 4

CAPACITY = 0
SLOT_FULLNESS = 0

# Queue for storing material requests
MATERIALS = []

# 4 slots where the first value is binary value if the slot is filled
# and second value is material itself 
SLOTS = [[0,None], [0,None], [0,None],[0,None]]
TOTAL_WEIGHT = 0

COVERAGE_SLOTS = [[0,0,0,0], [0,0,0,0],[0,0,0,0],[0,0,0,0]]

def report_coverage():    
    global COVERAGE_SLOTS        
    "Coverage reporter"
    coverage = 0
    for i in range(len(COVERAGE_SLOTS)):
        for i2 in range(len(COVERAGE_SLOTS[i])):
            if(COVERAGE_SLOTS[i][i2]):
                coverage += 1
    print('CartCoverage %d%%' % ((coverage/(len(COVERAGE_SLOTS)*4))*100))    
def onmoving(time, pos1, pos2):
    global COVERAGE_SLOTS, SLOT_FULLNESS, TRACK_COUNT
    "priklad event-handleru pro udalost moving"

    time = int(time)    
    print('%d:debug: got moving from %s to %s' % (time, pos1, pos2))    
    
    # PROPERTY3
    loadedMaterial = findLoadedMaterial(pos1)
    if loadedMaterial is not None:
        print(time, ' | Error: Slot', loadedMaterial,'is not unloaded while in his destination: ', pos1)
            

# function searches for the material through its target destination and returns its slot or None
# used in property3
def findLoadedMaterial(dst):
    global SLOTS
    for i in range(MAX_SLOTS):
        if(SLOTS[i][0] == 1 and SLOTS[i][1]["dst"] == dst):
            return i
    return None

# function searches for materials with given source in material requests variable
# return list of found materials
def findDestination(src):
    global MATERIALS
    listDst = []
    for i in range(len(MATERIALS)):
        MATERIAL  = MATERIALS[i]
        if(MATERIAL["src"] == src):
            listDst.append([MATERIAL,i])
    return listDst

# function searches for material in material requests variable
# returns material and index or None
def findMaterial(src, content):
    listDst = findDestination(src)
    for i in range(len(listDst)):
        MATERIAL,index = listDst[i]        
        if(MATERIAL["content"] == content):
            return (MATERIAL,index)
    return None, None

# Function takes material from request material queue and stores it in the slot
def onloading(time, pos, content, w, slot):    
    global SLOT_FULLNESS, MAX_SLOTS, SLOTS, MATERIALS, TOTAL_WEIGHT
    
    # PROPERTY1
    if(SLOTS[int(slot)][0] == 1):
        print(time, ' | Error: Loading into full slot: ', slot)            
    
    
    MATERIAL, index = findMaterial(pos, content)
    in_station = 0
    
    # PROPERTY5
    if(MATERIAL is None):
        print(time, ' | Error: Loading without request in station: ', pos)   
    else:
        in_station = 1         

    # PROPERTY6
    if SLOT_FULLNESS+1 > MAX_SLOTS:
        print(time, ' | Error: Loading while all slots are full')
        SLOTS[int(slot)] = 0
    else:
        if(in_station):
            SLOT_FULLNESS+=1        
            itemWeight = MATERIAL["weight"]
            
            # PROPERTY7
            if(TOTAL_WEIGHT + itemWeight > MAX_CAPACITY):
                print(time, ' | Error: Maximal weight limit overreached while loading content: ', content)
            else: 
                TOTAL_WEIGHT += itemWeight
                SLOTS[int(slot)] = 1, MATERIAL
                MATERIALS.pop(index)
        

            
    # Coverage calculation
    if pos == 'A':
        COVERAGE_SLOTS[0][int(slot)] = 1
    elif pos == 'B':
        COVERAGE_SLOTS[1][int(slot)] = 1
    elif pos == 'C':
        COVERAGE_SLOTS[2][int(slot)] = 1
    else:
        COVERAGE_SLOTS[3][int(slot)] = 1
    
        
    #print('Destinace: ', DST) 
    #print('MATERIALS: ', MATERIALS) 
    #print('SLOTS: ', SLOTS) 
    

def onunloading(time, pos, content, w, slot):
    global SLOT_FULLNESS, SLOTS, TOTAL_WEIGHT
    
    # PROPERTY2
    if(SLOTS[int(slot)][0] == 0):
        print(time, ' | Error: Unloading from empty slot: ', slot)
    else:    
        TOTAL_WEIGHT -= int(w)
        SLOTS[int(slot)] = 0, None        
        SLOT_FULLNESS -= 1    

# Function takes new material request and appends it to Material queue   
def onrequesting(time, src, dst, content, w):
    global MATERIALS 
    newMaterial = {
        "src" : src,
        "dst" : dst,
        "content" : content,
        "weight" : int(w)
    }
    MATERIALS.append(newMaterial)
    
def onidle(time, pos):
    global MATERIALS, SLOTS
    
    # PROPERTY9
    if(len(MATERIALS) > 0 ):
        print(time, ' | Error: Idle while request exists ')
    else:
        for i in range(MAX_SLOTS):
            if(SLOTS[i][0] == 1):
                print(time, ' | Error: Idle while request exists ')
                break
        
    
def onevent(event):
    
    "Event handler. event = [TIME, EVENT_ID, ...]"
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ZDE IMPLEMENTUJTE MONITORY
    print(event)

    # vyjmeme identifikaci udalosti z dane n-tice
    event_id = event[1]

    del(event[1])
    # priklad predani ke zpracovani udalosti moving
    if event_id == 'moving':
        # predame n-tici jako jednotlive parametry pri zachovani poradi
        onmoving(*event)
    elif event_id == 'loading':
        onloading(*event)
    elif event_id == 'unloading':
        onunloading(*event)
    elif event_id == 'requesting':
        onrequesting(*event)
    elif event_id == 'idle':
        onidle(*event)
    #elif event_id == '....':
    #    ...

###########################################################
# Nize netreba menit.

def monitor(reader):
    "Main function"
    for line in reader:
        line = line.strip()
        onevent(line.split())
    report_coverage()

if __name__ == "__main__":
    import sys
    monitor(sys.stdin)
