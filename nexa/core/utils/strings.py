def pluralize(word):

    if word.endswith('y'):

        return word[:-1] + 'ies'

    return word + 's'
    
def pascal_case(string):
    return ''.join(word.capitalize() for word in string.replace('_', ' ').replace('-', ' ').split())

def snake_case(string):
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()