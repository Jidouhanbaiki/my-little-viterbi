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


def process_file(file_name):
    f = open(file_name, "r")
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

    # "tokenized_sentences" looks like this: [ [ word, word word ], [word, word] ]
    tokenized_sentences = [nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(raw)]


    # adding START and END of sentence tokens
    # TEMPORARY REMOVED
    tokenized_lexica = []  #used in order to filter the input later
    for sent in tokenized_sentences:
        #tokenized_lexica.append("START")
        for token in sent:
            tokenized_lexica.append(token)
        #tokenized_lexica.append("END")
    return tokenized_lexica


def generate_word_word_matrix(tokenized_lexica):
    # creates a list of bigrams (tuples)
    all_bigrams = list(nltk.bigrams(tokenized_lexica))

    # making a matrix which calculates probabilities of bigrams in text
    cfdist = nltk.ConditionalFreqDist(all_bigrams)
    matrix_word_word = pykov.Matrix() # essentially a dictionary with two keys and integer value
    for bigram in all_bigrams:
        matrix_word_word[bigram[0], bigram[1]] = cfdist[bigram[0]][bigram[1]]
        #print("DEBUG", bigram, matrix_word_word[bigram[0], bigram[1]])

    # setting a sum of each row equal to 1
    stochastic(matrix_word_word) # overriden pykov function

    print("bigrams probabilities test:", matrix_word_word.items())
    return matrix_word_word


def generate_word_pos_matrix(tagged_word_pairs):
    # making a matrix which calculates probabilities of [word, tag] pairs
    cfdist = nltk.ConditionalFreqDist(tagged_word_pairs)
    #print cfdist[":"][":"]
    matrix_word_pos = pykov.Matrix()  # first - terminal, second - tag

    for pair in tagged_word_pairs:
        matrix_word_pos[pair[0], pair[1]] = cfdist[pair[0]][pair[1]]

    stochastic(matrix_word_pos) # overriden
    print("part-of-speech probabilities test:", matrix_word_pos.items())
    return matrix_word_pos


def generate_pos_pos_matrix(tagged_word_pairs):
    # making a list of tag bigrams [tag, tag]
    only_tags = [pair[1] for pair in tagged_word_pairs]  # we allow only tokenized_lexica here
    tag_bigrams = list(nltk.bigrams(only_tags))

    # making a matrix which calculates probabilities of [tag, tag] pairs
    cfdist = nltk.ConditionalFreqDist(tag_bigrams)
    matrix_pos_pos = pykov.Matrix()
    for bigram in tag_bigrams:
        matrix_pos_pos[bigram[0], bigram[1]] = cfdist[bigram[0]][bigram[1]]

    stochastic(matrix_pos_pos) # overriden
    print("tags probabilities test:", matrix_pos_pos.items())
    return matrix_pos_pos


def generate(tagged_words, matrices, length=5):  # tagged_words is a list of lists
    matrix_word_word = matrices[0]
    matrix_word_pos = matrices[1]
    matrix_pos_pos = matrices[2]

    while length > 0:
        length -= 1
        word_n_tag = tagged_words[-1]

        output_words = {} # key - word, value - probability
        
        # probability based on bigrams
        #print("DEBUG", word_n_tag, matrix_word_word[word_n_tag[0]])
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
    lexica = process_file(FILE_NAME)

    tagged_word_pairs = nltk.pos_tag(lexica)
    # TODO: this line is inefficient, it seems to tag words without taking into account their context. However, might be fast.

    probability_matrices = (generate_word_word_matrix(lexica),
                            generate_word_pos_matrix(tagged_word_pairs),
                            generate_pos_pos_matrix(tagged_word_pairs)
    )

    tokenized_user_input = nltk.word_tokenize(input("Write first word(s):").lower())

    if (tokenized_user_input[-1]) not in lexica:
        return "Error! Please try a different word - the last word of your sentence is not present in the original text."
    # TODO: the last word of the text will raise an error in case it has no corresponding pair. Needs fixing. Maybe by adding an "END" token.
    user_input_pairs = nltk.pos_tag(tokenized_user_input)
    try:
        number_of_words = int(input("How many words should we generate? "))
    except ValueError:
        return "Error! Please make sure to input a number!"

    print("Input accepted.")


    output = generate(user_input_pairs, probability_matrices, number_of_words)

    #output = generate([("i", "PRP")], probability_matrices, 42)

    return " ".join([pair[0] for pair in output])


if __name__ == "__main__":
    print(start())


        
            
        

