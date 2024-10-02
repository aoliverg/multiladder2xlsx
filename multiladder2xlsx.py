import sys
import codecs
import argparse
import xlsxwriter

import sys
import itertools
import os

'''file -> array holding the lines of the file'''
def readfile(name):
    # Open the input files and read lines
    with open(name, 'r') as infile:
        lines = list(map(lambda s: s.strip("\n"), infile.readlines()))
    return lines

'''s -> (s0,s1), (s1,s2), (s2, s3), ...
see https://docs.python.org/3/library/itertools.html'''
def pairwise(iterable):
    a, b = itertools.tee(iterable)
    next(b)
    return zip(a, b)

'''Create aligned text from two sentence files and hunalign's ladder-style output.
Usage: ladder2text.py <aligner.ladder> <hu.sen> <en.sen> > aligned.txt
See http://mokk.bme.hu/resources/hunalign for detailed format specification and more.
The output file is tab-delimited, with three columns. The first is a probability score.
The second and third columns are the chunks corresponding to each other.
" ~~~ " is the sentence delimiter inside chunks.
'''
def ladder2text(ladderfile, hufile, enfile,outfile):
    #if len(sys.argv) == 4:
    ladderlines = readfile(ladderfile)
    hulines = readfile(hufile)
    enlines = readfile(enfile)

    def parseLadderLine(l):
        a = l.split()
        assert len(a) == 3
        return (int(a[0]), int(a[1]), a[2])  # The score we leave as a string, to avoid small diffs caused by different numerical representations.

    ladder = map(parseLadderLine, ladderlines)
    # the next map() does all the work, so here are some comments...
    # the map() iterates over the holes of the ladder.
    # a hole is supposed to be two consecutive items in the array holding the lines of the ladder. /an array of holes is returned by pairwise(ladder)/
    # the following segment returns an interval of sentences corresponding to a hole:
    # hulines[int(hole[0][0]):int(hole[1][0])]
    outputlines = map(lambda hole:
                      
                      " ~~~ ".join(hulines[int(hole[0][0]):int(hole[1][0])])
                      + "\t" +
                      " ~~~ ".join(enlines[int(hole[0][1]):int(hole[1][1])])
                      + "\t" +
                      hole[0][2]
                      ,
                      pairwise(ladder)
                      )

    sortida=codecs.open(outfile,"w",encoding="utf-8")
    for l in outputlines:
        sortida.write(str(l)+"\n")
    #else:
    #    print('usage: ladder2text.py <aligned.ladder> <hu.raw> <en.raw> > aligned.txt')
    #    sys.exit(-1)
    sortida.close()

def can_be_converted_to_int(variable):
    try:
        int(variable)
        return True
    except ValueError:
        return False
        
def includeCSP(lista,element):
    element.sort()
    if not element in lista:
        lista.append(element)
    return(lista)

def merge_and_sort_sublists(sublists):
    from collections import defaultdict

    if not all(isinstance(sublist, list) for sublist in sublists):
        raise ValueError("All elements in the input list must be lists.")

    # Dictionary to keep track of which sublists contain each element
    element_to_sublists = defaultdict(set)

    # Populate the dictionary
    for sublist in sublists:
        for element in sublist:
            element_to_sublists[element].add(tuple(sublist))

    # Function to merge two sublists
    def merge_lists(list1, list2):
        return list(sorted(set(list1) | set(list2)))

    # Set to track processed sublists
    processed = set()
    result = []

    # Function to find and merge all connected sublists
    def find_and_merge_sublists(start_sublist):
        to_process = [start_sublist]
        merged_list = set(start_sublist)

        while to_process:
            current_sublist = to_process.pop()
            if tuple(current_sublist) in processed:
                continue
            processed.add(tuple(current_sublist))
            for element in current_sublist:
                for connected_sublist in element_to_sublists[element]:
                    if tuple(connected_sublist) not in processed:
                        merged_list.update(connected_sublist)
                        to_process.append(list(connected_sublist))

        return sorted(merged_list)

    # Iterate over sublists to merge connected ones
    for sublist in sublists:
        if tuple(sublist) not in processed:
            merged_sublist = find_and_merge_sublists(sublist)
            result.append(merged_sublist)

    return result

def find_closest_key(d, target):
    closest_key = min(d.keys(), key=lambda k: abs(k - target))
    return closest_key

# Create the parser
parser = argparse.ArgumentParser(description='Align multiple files.')

# Add an argument for the list of files
parser.add_argument( '-l','--ladders', type=str, nargs='+', help='The ladder files to process')
parser.add_argument( '-f','--files',  type=str, nargs='+', help='The common source and target segmented files')
parser.add_argument( '-o','--output',  type=str, help='The common source and target segmented files. It will create Excel and text files')

# Parse the command-line arguments
args = parser.parse_args()

# Access the list of files
ladder_list = args.ladders

files=args.files

output=args.output

falineacion=output
ffladders=output.replace(".txt","")+".ladder"

excelfile=output+".xlsx"


sortidanumbers=codecs.open("numbers.txt","w",encoding="utf-8")

maxlines=1000000
for i in range(0,maxlines):
    sortidanumbers.write(str(i)+"\n")

sortidanumbers.close()

contfile=1
number_list=[]
for lf in ladder_list:
    outfilename="laddernumbers-"+str(contfile)+".txt"
    number_list.append(outfilename)
    ladder2text(lf, "numbers.txt", "numbers.txt",outfilename)
    contfile+=1


sortidaalineacion=codecs.open(falineacion,"w",encoding="utf-8")
sortidaladders=codecs.open(ffladders,"w",encoding="utf-8")
sortidaexcel=falineacion.replace(".txt","")+".xlsx"
workbook = xlsxwriter.Workbook(sortidaexcel)
bold   = workbook.add_format({'bold': True})
normal = workbook.add_format({'bold': False})
red = workbook.add_format({'text_wrap': 1, 'valign': 'top','font_color': 'red'})
redorange = workbook.add_format({'text_wrap': 1, 'valign': 'top','font_color': 'red','bg_color': '#FFA500'})


text_wrap = workbook.add_format({'text_wrap': 1, 'valign': 'top'})
sheetAligned = workbook.add_worksheet("Aligned")
sheetAligned.set_column(0, len(files), 22)
sheetRevision = workbook.add_worksheet("Revision")
sheetRevision.set_column(0, len(files), 22)

# Print the list of files (for demonstration purposes)
print('Files to process:', ladder_list)

segmentedfiles=[]
segments={}
cont=0
numsegments={}
cont=0
segmentsprocessed={}
for f in files:
    segmentsprocessed[f]=[]
    segmentedfiles.append(f)
    entrada=codecs.open(f,"r",encoding="utf-8")
    segments[f]=[]
    contlinia=0
    for linia in entrada:
        linia=linia.rstrip()
        linia=linia.replace("\t"," ")
        segments[f].append(linia)
        contlinia+=1
    numsegments[f]=contlinia
    cont+=1
    entrada.close()
    
sourceline2targetlines={}
commonsourcepart=[]
cont=1
ladderfile2segmentfile={}
segmentfile2ladderfile={}
for ladderfile in number_list:
    sourceline2targetlines[ladderfile]={}
    entrada=codecs.open(ladderfile,"r",encoding="utf-8")
    for l in entrada:
        l=l.rstrip()
        (iLC,iLn,score)=l.split("\t")
        score=float(score)
        iC=iLC.split(" ~~~ ")
        iL=iLn.split(" ~~~ ")
        iCint=[]
        for element in iC:
            try:
                elementINT=int(element)
                iCint.append(elementINT)
            except:
                pass
        iLint=[]
        for element in iL:
            try:
                elementINT=int(element)
                iLint.append(elementINT)
            except:
                pass
        
        #RELATION BETWEEN SOURCE LINE AND TARGET LINE
        for sourceline in iCint:
            if can_be_converted_to_int(sourceline) and not sourceline in sourceline2targetlines[ladderfile]:
                sourceline2targetlines[ladderfile][int(sourceline)]=[]
            for targetline in iL:
                if can_be_converted_to_int(sourceline) and can_be_converted_to_int(targetline) and int(targetline) not in sourceline2targetlines[ladderfile][int(sourceline)]:
                    sourceline2targetlines[ladderfile][int(sourceline)].append(int(targetline))
        #CREATION OF THE COMMON SOURCE PART
        #if not iCint[0]=="":
        commonsourcepart=includeCSP(commonsourcepart,iCint)
    ladderfile2segmentfile[ladderfile]=files[cont]
    segmentfile2ladderfile[files[cont]]=ladderfile
    cont+=1


commonsourcepart=merge_and_sort_sublists(commonsourcepart)

commonsourcepartSorted=[]

for cs in commonsourcepart:
    cs.sort()
    commonsourcepartSorted.append(cs)

infoalineacion=[]
infoladders=[]
whereissegment={}
contposition=0
registre=[]
for o in range(0,len(files)):
    whereissegment[o]={}
for i in commonsourcepartSorted:
    cadenafinal=[]
    #SOURCE
    segmentoriginal=[]
    ladderorig= ":".join([str(element) for element in i])
    fileorder=0 #es el original
    for num in i:
        whereissegment[0][num]=contposition
    for s in i:
        segmentoriginal.append(segments[files[0]][int(s)])
        segmentsprocessed[files[0]].append(s)
    segmentoriginal=" ".join(segmentoriginal).strip()
    
    if len(segmentoriginal)==0:
        segmentoriginal="EMPTY SEGMENT"
    #TARGETLANGUAGES
    targetsegments=[]
    targetladders=[]
    for y in range(1,len(files)):
        fileorder=y #son els targets
        
        targetlines=[]
        lf=segmentfile2ladderfile[files[y]]
        for s in i:
            try:
                whereissegment[fileorder][s]=contposition
                targetlines.extend(sourceline2targetlines[lf][s])
                segmentsprocessed[files[y]].extend(sourceline2targetlines[lf][s])
            except:
                pass
            
        targetlines=list(set(targetlines))
        targetlines.sort()
        targetlinesSTR = [str(num) for num in targetlines]
        targetladders.append(":".join(targetlinesSTR))
        targetsegment=[]
        for tl in targetlines:
            ts=segments[files[y]][tl].strip()
            targetsegment.append(ts)
        targetsegment=" ".join(targetsegment).strip()
        if len(targetsegment)==0:
            targetsegment="EMPTY SEGMENT"
        targetsegments.append(targetsegment)
    cadenatarget="\t".join(targetsegments)
    cadena=segmentoriginal+"\t"+cadenatarget
    
    toWrite=True
    if cadena.find("<p>")>-1 or cadena.find("EMPTY SEGMENT")>-1:
        toWrite=False
    registre.append(cadena)
    infoalineacion.append(cadena.split("\t"))
    cadenaladders=ladderorig+"\t"+"\t".join(targetladders)
    infoladders.append(cadenaladders.split("\t"))
    if segmentoriginal=="EMPTY SEGMENT" and toWrite:
        sheetAligned.write(contposition, 0, segmentoriginal, red)
    elif toWrite:
        sheetAligned.write(contposition, 0, segmentoriginal, text_wrap)
    contts=1
    for targetsegmentEX in targetsegments:
        if targetsegmentEX=="EMPTY SEGMENT" and toWrite:
            sheetAligned.write(contposition, contts, targetsegmentEX, red)
        elif toWrite:    
            sheetAligned.write(contposition, contts, targetsegmentEX, text_wrap)
        contts+=1
    if toWrite: contposition+=1
    
    sortidaalineacion.write(cadena+"\n")
    sortidaladders.write(cadenaladders+"\n")  
    
#infoalineacionmod=infoalineacion.copy()

contlang=0
accum=0




def missing_numbers(lst, max_num):
    return sorted(set(range(max_num + 1)) - set(lst))
controlmissing={}

for filenum in range(0,len(files)):
    maxsegment=len(segmentsprocessed[files[filenum]])
    controllist=[]
    for info in infoladders:
        info2=info[filenum].split(":")
        for i in info2:
            try:
                controllist.append(int(i))
            except:
                pass
    missing=missing_numbers(controllist, maxsegment-1)
    controlmissing[filenum]=missing

def get_smaller_numbers(lst, threshold):
    return [x for x in lst if x < threshold]

def remove_elements(original_list, elements_to_remove):
    return [x for x in original_list if x not in elements_to_remove]

infoalineacionmod=[]
contregistre=0
contfilera=1
for ill in infoladders:
    langnum=0
    for il in ill:                  
        il=il.split(":")
        try:
            previous=get_smaller_numbers(controlmissing[langnum],int(il[0]))
            liniaprevious=[""]*len(files)
            if len(previous)>0:
                controlmissing[langnum]=remove_elements(controlmissing[langnum],previous)
                toinclude=[]
                for pr in previous:
                    toinclude.append(segments[files[langnum]][pr])
                toinclude=" ".join(toinclude)
                liniaprevious[langnum]=toinclude
                
        except:
            liniaprevious=[""]*len(files)
        if  any(element != "" for element in liniaprevious):
            contcolumn=0
            for info in liniaprevious:
                if not info=="<p>" and not info=="<p> <p>" and not info=="<p> <p> <p>" and not info=="<p> <p> <p> <p>" and len(info)>0:
                    sheetRevision.write(contfilera, contcolumn, info, redorange)
                    contfilera+=1
                contcolumn+=1
        langnum2=0
        langnum+=1
    campsregistre=registre[contregistre].split("\t")
    contcolumn=0
    toWriteRevision = all(element in ["<p>", "EMPTY SEGMENT"] for element in campsregistre)
    if not toWriteRevision:
        for info in campsregistre:
            if len(info)==0 or info=="EMPTY SEGMENT":
                info="EMPTY SEGMENT"
                sheetRevision.write(contfilera, contcolumn, info, red)
            else:
                sheetRevision.write(contfilera, contcolumn, info, text_wrap)
            contcolumn+=1
        contfilera+=1
    contregistre+=1
    

workbook.close()


file_path="numbers.txt"
if os.path.exists(file_path):
    os.remove(file_path)
    
for file_path in number_list:
    if os.path.exists(file_path):
        os.remove(file_path)