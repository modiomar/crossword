This program generates crossword puzzles, you provide a text file with the words you wish to be used and a structure that determines
what the puzzle will look like i.e. its structure, the rest is handled by the program!
If you don't feel like providing those just yet, you can use the ready to use word and structure text files in the 'data' folder.
To generate a puzzle, follow these simple instructions:
- open a terminal in the main directory, called 'crossword'
- to download the module dependencies, run: pip install -r requirements.txt
- to generate the puzzle, run the following command: python generate.py data/structure1.txt data/words1.txt output.png
    note: you can replace 'structure1.txt' and 'words1.txt' with those you made (and had placed inside 'data')
- now, you should be able to find 'output.png' image, containing your puzzle in the 'crossword' directory
- enjoy!

