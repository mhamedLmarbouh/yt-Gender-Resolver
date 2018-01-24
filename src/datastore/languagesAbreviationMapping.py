# mongodb supported languages
mongodb_supported_languages = (
    'da','nl','en','fi','fr','de','hu','it',
    'nb','pt','ro','ru','es','sv','tr'
)
# key:language abbreviation
# value:language name equivalent supported by nltk SnowballStemmer
language_long_name = {
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'fi': 'finnish',
    'fr': 'french',
    'de': 'german',
    'hu': 'hungarian',
    'it': 'italian',
    'nb': 'norwegian',
    'pt': 'portuguese',
    'ro': 'romanian',
    'ru': 'russian',
    'es': 'spanish',
    'sv': 'swedish',
    'ar': 'arabic'
}


def inverse_dictionary(lang_dict):
    inv_dict = dict()
    for key, val in lang_dict.items():
        inv_dict.update({val: key})
    return inv_dict

