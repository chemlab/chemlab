import re

# Utility
def partition(alist, indices):
    return [alist[i:j] for i, j in zip([0]+indices, indices+[None])]
    
def grep(pattern, filename):
    """Given a regex *pattern* return the lines in the file *filename*
    that contains the pattern.

    """
    return greplines(pattern, open(filename))
    
def greplines(pattern, lines):
    """Given a list of strings *lines* return the lines that match
    pattern.

    """
    res = []
    for line in lines:
        match = re.search(pattern, line)
        if match is not None:
            res.append(line)
    return res
    
def sections(start, end, text, line=True):
    """Given the *text* to analyze return the section the start and
    end matchers. If line=True return the lines between the line that
    matches *start* and the line that matches *end* regexps.

    If line=False return the text between the matching start and end
    
    The match is in the regexp lingo *ungreedy*.

    """
    if not line:
        return re.findall(start+"(.*?)"+end, text, re.DOTALL)
    
    lines = text.splitlines()
    
    # This is a state-machine with the states MATCHING = True/False
    MATCHING = False
    section_list = []
    sre = re.compile(start)
    ere = re.compile(end)
    
    for line in lines:
        if MATCHING == False:
            if sre.search(line):
                # Start to take stuff
                MATCHING = True
                section = [] 
                continue
        
        if MATCHING == True:
            if ere.search(line):
                MATCHING = False
                section_list.append('\n'.join(section))
            else:
                section.append(line)
    return section_list

def grep_split(pattern, text):
    '''Take the lines in *text* and split them each time the pattern
    matches a line.

    '''
    lines = text.splitlines()
    indices = [i for i, line in enumerate(lines)
               if re.search(pattern, line)]
    
    return ['\n'.join(part) for part in partition(lines, indices)]
    
def between(text, start, end):
    pass