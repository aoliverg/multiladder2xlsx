# multiladder2xlsx
A script to align multiple languages with Hunalign ladder files

To align n documents, you need the n segmented documents (one of them should be the common document in all the alignments, tipically the source language document) and n-1 ladder alignment files obtanied with hunalign.

The option -h shows the help of the program
```
python3 multiladder2xlsx.py -h
usage: multiladder2xlsx.py [-h] [-l LADDERS [LADDERS ...]] [-f FILES [FILES ...]] [-o OUTPUT]

Align multiple files.

options:
  -h, --help            show this help message and exit
  -l LADDERS [LADDERS ...], --ladders LADDERS [LADDERS ...]
                        The ladder files to process
  -f FILES [FILES ...], --files FILES [FILES ...]
                        The common source and target segmented files
  -o OUTPUT, --output OUTPUT
                        The common source and target segmented files. It will create Excel and text files
```

To align a book in seven languages into a single file you should write:

```python3 multiladder2xlsx.py -f book-spa-seg.txt book-fra-seg.txt book-ita-seg.txt book-por-seg.txt book-rom-seg.txt book-hrv-seg.txt book-cat-seg.txt -l ladder-spa-fra.txt ladder-spa-ita.txt ladder-spa-por.txt ladder-spa-rom.txt ladder-spa-hrv.txt ladder-spa-cat.txt -o book-alignment```

A book-alignment.xlsx Excel file will be created. This file has two tabs, "Aligned" contening the alignments with high chance to be correct; and "Revision" containing all alignments, with color marks to make the revision process easier.


