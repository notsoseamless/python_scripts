
replace unix to windows seperators
file_path = line[1].replace('/','\\')

check for function
line.split(' ',1)[0] == 'void'

substitution
num = re.sub(r'(\.\.\/)*', url, line)
word = re.sub(';', '', word)




def set_logger():
    global logger
    logger = logging.getLogger(log_path)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)





try:
    SRC_FILE_PTR = open('..\\..\\' + file_path, 'r')
    logger.info(file_path + ' opened for parsing')
except IOError:
    logger.error('failed to open ' + file_path)
    panic()



def remove_comments(text):
    """ remove c-style comments.
        text: blob of text with comments (can include newlines)
        returns: text with comments removed
    """
    pattern = r"""
                            #  --------- COMMENT ---------
           /\*              #  Start of /* ... */ comment
           [^*]*\*+         #  Non-* followed by 1-or-more *'s
           (                #
             [^/*][^*]*\*+  #
           )*               #  0-or-more things which don't start with /
                            #    but do end with '*'
           /                #  End of /* ... */ comment
         |                  #  -OR-  various things which aren't comments:
           (                # 
                            #  ------ " ... " STRING ------
             "              #  Start of " ... " string
             (              #
               \\.          #  Escaped char
             |              #  -OR-
               [^"\\]       #  Non "\ characters
             )*             #
             "              #  End of " ... " string
           |                #  -OR-
                            #
                            #  ------ ' ... ' STRING ------
             '              #  Start of ' ... ' string
             (              #
               \\.          #  Escaped char
             |              #  -OR-
               [^'\\]       #  Non '\ characters
             )*             #
             '              #  End of ' ... ' string
           |                #  -OR-
                            #
                            #  ------ ANYTHING ELSE -------
             .              #  Anything other char
             [^/"'\\]*      #  Chars which doesn't start a comment, string
           )                #    or escape
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    noncomments = [m.group(2) for m in regex.finditer(text) if m.group(2)]

    return "".join(noncomments)











