import pykov
import nltk
import six
import random

FILE_NAME = "orwell.txt"

def stochastic(self):  # from pykov, modified
    """
        Make a right stochastic matrix.

        Set the sum of every row equal to one,
        raise ``PykovError`` if it is not possible.

        >>> T = pykov.Matrix({('A','B'): 3, ('A','A'): 7, ('B','A'): .2})
        >>> stochastic(T)
        >>> T
        {('B', 'A'): 1.0, ('A', 'B'): 0.3, ('A', 'A'): 0.7}
        >>> T[('A','C')]=1
        >>> stochastic(T)
        pykov.PykovError: 'Zero links from node C'
    """
    s = {}
    for k, v in self.succ().items():
        summ = float(sum(v.values()))
        if summ:
            s[k] = summ
        else:
            s[k] = 0
    for k in six.iterkeys(self):
        self[k] = self[k] / s[k[0]]


f = open(FILE_NAME, "r")
remove_colon = True   # toggle it off to have result with colons
if remove_colon:
    # trying to remove the name of the speaker from the text
    raw = ""
    char_buffer = ""
    for char in f.read():
        if char.isalnum() or char == "_":
            char_buffer+=char.lower()
        else:
            if char != ":":
                raw += char_buffer
                raw += char
            char_buffer = ""
else:
    raw = [ char.lower() for char in f.read()]  
    raw = "".join(raw)

f.close()

# "sents" looks like this: [ [ word, word word ], [word, word] ]
sents = [nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(raw)]


# adding START and END of sentence tokens
# TEMPORARY REMOVED
words = []
for sent in sents:
    #words.append("START")
    for token in sent:
        words.append(token)
    #words.append("END")


# creates a list of bigrams (tuples) 

all_bigrams = list(nltk.bigrams(words))

# making a matrix which calculates probabilities of bigrams in text
cfdist = nltk.ConditionalFreqDist(all_bigrams)
matrix_word_word = pykov.Matrix() # essentially a dictionary with two keys and integer value
for bigram in all_bigrams:
    matrix_word_word[bigram[0], bigram[1]] = cfdist[bigram[0]][bigram[1]]
    #print("DEBUG", bigram, matrix_word_word[bigram[0], bigram[1]])


# setting a sum of each row equal to 1
stochastic(matrix_word_word) # overriden

print("bigrams probabilities test:", matrix_word_word.items())

# making a list of lists [word, tag]

all_words = [word for sent in sents for word in sent]
tagged = nltk.pos_tag(all_words)


# making a matrix which calculates probabilities of [word, tag] pairs
cfdist = nltk.ConditionalFreqDist(tagged)
#print cfdist[":"][":"]
matrix_word_pos = pykov.Matrix()  # first - terminal, second - tag

for pair in tagged:
    matrix_word_pos[pair[0], pair[1]] = cfdist[pair[0]][pair[1]]

stochastic(matrix_word_pos) # overriden



print("part-of-speech probabilities test:", matrix_word_pos.items())



# making a list of tag bigrams [tag, tag]
only_tags = [pair[1] for pair in tagged]  # we allow only words here
tag_bigrams = list(nltk.bigrams(only_tags))


# making a matrix which calculates probabilities of [tag, tag] pairs
cfdist = nltk.ConditionalFreqDist(tag_bigrams)
matrix_pos_pos = pykov.Matrix()
for bigram in tag_bigrams:
    matrix_pos_pos[bigram[0], bigram[1]] = cfdist[bigram[0]][bigram[1]]

stochastic(matrix_pos_pos) # overriden

print("tags probabilities test:", matrix_pos_pos.items())


def generate(tagged_words, length=5):  # tagged_words is a list of lists
    global matrix_word_word
    global matrix_word_pos
    global matrix_pos_pos

    while length > 0:
        length -= 1
        word_n_tag = tagged_words[-1]

        output_words = {} # key - word, value - probability
        
        # probability based on bigrams
        print("DEBUG", word_n_tag, matrix_word_word[word_n_tag[0]])
        for pair in matrix_word_word.succ(word_n_tag[0]).items(): # [('A', 2), ('B', 6)]
            """
            if pair[0] == "END":
                length = 0
                break
            if pair[0] == "START":
                break;
            """
            for tag_prob in matrix_word_pos.succ(pair[0]).items():
                output_words[pair[0], tag_prob[0]] = pair[1] * tag_prob[1] + random.uniform(0.01, 0.1)
                
                
        # probability based on matrix_pos_pos
        for tag_prob in matrix_pos_pos.succ(word_n_tag[1]).items(): # [('A', 2), ('B', 6)]
            for word_prob in matrix_word_pos.pred(tag_prob[0]).items():
                if (word_prob[0], tag_prob[0]) in output_words.keys():
                    output_words[(word_prob[0], tag_prob[0])] += word_prob[1] * tag_prob[1]
                else:
                    output_words[(word_prob[0], tag_prob[0])] = word_prob[1] * tag_prob[1]

        # probability based on what word comes next
        for output_pair in output_words.keys():
            item = matrix_word_word.succ(word_n_tag[0]).items()
            #print("DEBUG", item)
            if list(item)[0] == output_pair[0]:
                output_words[output_pair] += list(item)[1]
            if len([pair[1] for pair in tagged_words if output_pair[1] == pair[1]]) > (length/2):
                # penalty for repeating matrix_pos_pos
                output_words[output_pair] -= 0.3
            if output_pair in tagged_words:
                output_words[output_pair] -= 0.2
            
                
        chosen = max(output_words, key=lambda k: output_words[k])
        tagged_words.append(chosen)
        """
        for pair in output_words.items():
            if pair[-1] > 0.5:
                print pair
                print ""
        """

    return tagged_words


def start():
    user_input = input("Write first word(s):").lower()
    tokenized_user_input = nltk.pos_tag(nltk.word_tokenize(user_input))
    number = int(input("How many words? "))
    print("Input accepted.")

    generated = generate(tokenized_user_input, number)

    #generated = generate([("i", "PRP")], 42)

    print(" ".join([pair[0] for pair in generated]))

start()


        
            
        

