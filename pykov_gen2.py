import pykov
import nltk
import six
import random
import sys

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
    """
    Process the file with the source text.
    :param file_name:
    :return: a list of words
    """
    f = open(file_name, "r")
    remove_colon = True   # toggle it off to have result with colons
    if remove_colon:
        # trying to remove the name of the speaker from the text
        raw = ""
        char_buffer = ""
        for char in f.read():
            if char.isalnum() or char == "_":
                char_buffer += char.lower()
            else:
                if char != ":":
                    raw += char_buffer
                    raw += char
                char_buffer = ""
    else:
        raw = [char.lower() for char in f.read()]
        raw = "".join(raw)

    f.close()

    # "tokenized_sentences" looks like this: [ [ word, word word ], [word, word] ]
    tokenized_sentences = [nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(raw)]

    tokenized_lexica = []
    for sent in tokenized_sentences:
        #tokenized_lexica.append("START")  # removed for now for the sake of simplicity
        for token in sent:
            tokenized_lexica.append(token)
        #tokenized_lexica.append("END")  # removed for now for the sake of simplicity
    return tokenized_lexica


def generate_word_word_matrix(tokenized_lexica, isDebug=False):
    """
    Generate a Pykov matrix which calculates probabilities of [word, word] pairs
    :param tokenized_lexica:
    :return:
    """
    # create a list of bigrams
    all_bigrams = list(nltk.bigrams(tokenized_lexica))

    # make a matrix which shows probabilities of bigrams in text
    cfdist = nltk.ConditionalFreqDist(all_bigrams)
    matrix_word_word = pykov.Matrix()  # essentially a dictionary with two keys and an integer value
    for bigram in all_bigrams:
        matrix_word_word[bigram[0], bigram[1]] = cfdist[bigram[0]][bigram[1]]
        #print("DEBUG", bigram, matrix_word_word[bigram[0], bigram[1]])

    # set a sum of each row equal to 1, matrix values will show probabilities, not frequencies
    stochastic(matrix_word_word)  # overridden pykov function

    if isDebug:
        print("bigrams probabilities test:", matrix_word_word.items())

    return matrix_word_word


def generate_word_pos_matrix(tagged_word_pairs, isDebug=False):
    """
    Generate a Pykov matrix which calculates probabilities of [word, tag] pairs
    :param tagged_word_pairs:
    :return:
    """
    cfdist = nltk.ConditionalFreqDist(tagged_word_pairs)
    matrix_word_pos = pykov.Matrix()  # first - terminal, second - tag

    for pair in tagged_word_pairs:
        matrix_word_pos[pair[0], pair[1]] = cfdist[pair[0]][pair[1]]

    stochastic(matrix_word_pos)

    if isDebug:
            print("part-of-speech probabilities test:", matrix_word_pos.items())

    return matrix_word_pos


def generate_pos_pos_matrix(tagged_word_pairs, isDebug=False):
    """
    Generate a Pykov matrix which calculates probabilities of [tag, tag] pairs
    :param tagged_word_pairs:
    :return:
    """
    # make a list of tag bigrams [tag, tag]
    only_tags = [pair[1] for pair in tagged_word_pairs]
    tag_bigrams = list(nltk.bigrams(only_tags))

    # make a matrix which calculates probabilities of [tag, tag] pairs
    cfdist = nltk.ConditionalFreqDist(tag_bigrams)
    matrix_pos_pos = pykov.Matrix()
    for bigram in tag_bigrams:
        matrix_pos_pos[bigram[0], bigram[1]] = cfdist[bigram[0]][bigram[1]]

    stochastic(matrix_pos_pos)  # overridden

    if isDebug:
        print("tags probabilities test:", matrix_pos_pos.items())

    return matrix_pos_pos


def generate(tagged_words, matrices, length=10):  # tagged_words is a list of lists
    """
    Continue the tagged_words list using probability matrices.
    :param tagged_words: a pos-tagged and tokenized user input
    :param matrices: 3 probability matrices
    :param length: number of words which we are going to generate
    :return: modified tagged_words with generates pairs added at the end of the list
    """
    matrix_word_word = matrices[0]
    matrix_word_pos = matrices[1]
    matrix_pos_pos = matrices[2]

    while length > 0:
        length -= 1
        word_n_tag = tagged_words[-1]  # the content looks like ["i", "PRP"]

        next_word_probability = {}  # key - word, value - probability

        # probability based on word-word bigrams
        for pair in matrix_word_word.succ(word_n_tag[0]).items():  # [('A', 2), ('B', 6)]
            for tag_prob in matrix_word_pos.succ(pair[0]).items():
                next_word_probability[pair[0], tag_prob[0]] = pair[1] * tag_prob[1] + random.uniform(0.01, 0.1)

        # probability based on pos-pos bigrams
        for tag_prob in matrix_pos_pos.succ(word_n_tag[1]).items():  # [('A', 2), ('B', 6)]
            for word_prob in matrix_word_pos.pred(tag_prob[0]).items():
                if (word_prob[0], tag_prob[0]) in next_word_probability.keys():
                    next_word_probability[(word_prob[0], tag_prob[0])] += word_prob[1] * tag_prob[1]
                else:
                    next_word_probability[(word_prob[0], tag_prob[0])] = word_prob[1] * tag_prob[1]

        # probability based on what word comes next
        for output_pair in next_word_probability.keys():
            item = matrix_word_word.succ(word_n_tag[0]).items()
            #print("DEBUG", item)
            if list(item)[0] == output_pair[0]:
                next_word_probability[output_pair] += list(item)[1]
            if len([pair[1] for pair in tagged_words if output_pair[1] == pair[1]]) > (length/2):
                # penalty for repeating words
                next_word_probability[output_pair] -= 0.3
            if output_pair in tagged_words:
                next_word_probability[output_pair] -= 0.2

        tagged_words.append(max(next_word_probability, key=lambda k: next_word_probability[k]))
        """
        for pair in next_word_probability.items():
            if pair[-1] > 0.5:
                print pair
                print ""
        """
    return tagged_words


def start(file_name, user_sentence, length=10, is_debug=False):
    """
    Entry point.
    :param file_name: name of the source text file
    :param user_sentence: a starting sentence, string, provided by the user
    :param length: how many words should we generate
    :return:
    """
    lexica = process_file(file_name)

    tagged_word_pairs = nltk.pos_tag(lexica)
    # TODO: this line is inefficient, it seems to tag words without taking into account their context. However, might be fast.

    tokenized_user_input = nltk.word_tokenize(user_sentence)
    user_input_pairs = nltk.pos_tag(tokenized_user_input)

    if (tokenized_user_input[-1]) not in lexica:
        return "Error! Please try a different word - the last word of your sentence is not present in the original text."
    # TODO: the last word of the text will raise an error in case it has no corresponding pair. Needs fixing. Maybe by adding an "END" token.

    try:
        number_of_words = int(length)
    except ValueError:
        return "Error! Please make sure to input a number!"

    probability_matrices = (generate_word_word_matrix(lexica, is_debug),
                            generate_word_pos_matrix(tagged_word_pairs, is_debug),
                            generate_pos_pos_matrix(tagged_word_pairs, is_debug)
                            )

    output = generate(user_input_pairs, probability_matrices, number_of_words)

    #output = generate([("i", "PRP")], probability_matrices, 42)

    return " ".join([pair[0] for pair in output])


if __name__ == "__main__":
    console_user_input = input("Enter the name of the source plain-text file: "), \
        input("Write first word(s): ").lower(), \
        input("How many words should we generate? ")
    print("Input accepted.")
    print(start(*console_user_input))
