def pluralize(word):

    if word.endswith('y'):

        return word[:-1] + 'ies'

    return word + 's'