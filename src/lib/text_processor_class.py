from difflib import SequenceMatcher
import pandas as pd
import regex as re
import unicodedata
from polyglot.detect import Detector
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sentiment_analysis_spanish import sentiment_analysis


class Text_processor:
    """
    This class is used to do all the processing of the texts, can be used to:

        - Clean strings, Remove all not alphanumeric values
        - Check how similar are all words of a list between each other. Replace the similar by the most frequent
        - Check the language of the comments
        - Check if a comment is possitive or negative based on the language

    check the file GUIDE.text_processor_class for more details

    by jzar
    """

    def __init__(self):

        print("Initialized text_processor class")

        self.analyzer_en = SentimentIntensityAnalyzer()
        self.analyzer_es = sentiment_analysis.SentimentAnalysisSpanish()

    # ---------------- Text cleaning ------------------------

    def cleaning_function(self, a):
        """
        function used for clining a list of strings
        """
        a1 = self.lower_array(a)

        a2 = self.strip_accents_array(a1)

        a3 = self.remove_punct_array(a2)

        a4 = self.remove_first_the(a3)

        return a4

    @staticmethod
    def remove_first_the(s1):
        return [re.sub('(?:^|(?:[.!?]\s))(the |el |la |las |los )', '', word) for word in s1]

    @staticmethod
    def lower_array(a):
        return [(str(word)).lower() for word in a]

    @staticmethod
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')

    def strip_accents_array(self, a):
        return [self.strip_accents(str(word)) for word in a]

    @staticmethod
    def remove_punct(s):
        # replace - and / by space
        s0 = s.replace('-', ' ').replace('/', ' ')

        # replace 2+ spaces by 1 space
        t = re.compile(r"\s+")
        s1 = t.sub(" ", s0).strip()

        # remove punctuations
        s2 = re.sub(r'[^A-Za-z ]+', '', s1)

        # remove first space   
        s3 = re.sub('^\s', '', s2)

        # remove last space   
        s4 = s3.rstrip()

        return s4

    def remove_punct_array(self, a):
        return [self.remove_punct(str(word)) for word in a]

    # ---------------- Similar strings ------------------------

    @staticmethod
    def included(a, b):
        """
        This functions checks if 'a' word is included in 'b' phrase and the opposite
        """
        a = " " + a + " "
        b = " " + b + " "
        if (a in b) or (b in a):
            return True
        return False

    @staticmethod
    def similar(a, b):
        """
        This function compares 2 strings and gives you a similarity rate between 0-1        """

        return SequenceMatcher(None, a, b, autojunk=True).ratio()

    @staticmethod
    def replace_frequent(a, b, ls):
        """
        Compare the occurrences of each string of a list and
        then returns a list with the strings replaced by the most frequent value
        """
        if ls.count(a) > ls.count(b):
            return [a if (s == b) else s for s in ls]
        else:
            return [b if (s == a) else s for s in ls]

    def replace_similar_array(self, arr, similarity=0.9, similarity_ask=1, show=False):
        """
        This functions compares every string of a list with each other and replaces if they are similar.
        It keeps the most frequent value and replaces the occurences of the other one

        input:
        arr -> np.array with the strings we want to compare
        similarity -> the similarity threshold, automatically does the correction
        similarity_ask -> this threshold asks the user if the text is similar or not before correcting
        show -> True for a results viewer

        output:
        The np.array with the similar values replaced
        """

        str_arr = arr.copy()

        for index1 in range(len(str_arr)):
            for index2 in range(index1 + 1, len(str_arr)):

                name1 = str_arr[index1]
                name2 = str_arr[index2]

                if name1 != name2:
                    inc = self.included(name1, name2)

                    if inc:
                        str_arr = self.replace_frequent(name1, name2, str_arr)

                    else:
                        sim = self.similar(name1, name2)

                        if (sim > similarity) & (sim != 1):

                            if show is True:
                                print("Replacing all the values with", name2, "by", name1, ". Similarity: ", sim)
                            str_arr = self.replace_frequent(name1, name2, str_arr)

                        elif (sim > similarity_ask) & (sim != 1):

                            print('Are they the same? (n if not) -> ', name1, " <<>> ", name2, " (", sim, ")")
                            x = input()

                            if x != 'n':
                                str_arr = self.replace_frequent(name1, name2, str_arr)
                                print("Replacing all the values with", name2, "by", name1, ". Similarity: ", sim)

        return str_arr

    @staticmethod
    def replace_frequent_uniq(a, b, uniq_ls, orig_ls):
        """
        Compare the occurrences of each string of a unique list and
        then returns this unique list with the strings replaced by the most frequent values on the original list
        """
        freq = a if (orig_ls.count(a) > orig_ls.count(b)) else b

        if freq == a:
            return [a if (s == b) else s for s in uniq_ls]
        else:
            return [b if (s == a) else s for s in uniq_ls]

    def replace_frequent_with_table(self, orig_ls, similarity=0.85, similarity_ask=1, show=False):
        """

        -- This method improves the one above for large repetitive lists, check GUIDE.text_processor_class for more
        details --

        This method is replacing the similar values of a list by the most frequent one.
        In this approach first we calculate the unique values and then we make the replacement table.
        Finally, we search for the replacements of the list on this table saving us time (exponentially)

        input:
        orig_ls -> the list
        show -> if true it shows all the logs

        output:
        it returns the list

        """
        arr_original = orig_ls.copy()

        arr_uniq = pd.array(arr_original).unique()

        arr_uniq_copy = arr_uniq.copy()

        for index1 in range(len(arr_uniq)):
            for index2 in range(index1 + 1, len(arr_uniq)):

                name1 = arr_uniq_copy[index1]
                name2 = arr_uniq_copy[index2]

                if name1 != name2:
                    inc = self.included(name1, name2)

                    if inc:
                        arr_uniq_copy = self.replace_frequent_uniq(name1, name2, arr_uniq_copy, arr_original)

                    else:
                        sim = self.similar(name1, name2)

                        if (sim > similarity) & (sim != 1):

                            if show is True:
                                print("Replacing all the values with", name2, "by", name1, ". Similarity: ", sim)
                            arr_uniq_copy = self.replace_frequent_uniq(name1, name2, arr_uniq_copy, arr_original)

                        elif (sim > similarity_ask) & (sim != 1):

                            print('Are they the same? (n if not) -> ', name1, " <<>> ", name2, " (", sim, ")")
                            x = input()

                            if x != 'n':
                                arr_uniq_copy = self.replace_frequent_uniq(name1, name2, arr_uniq_copy, arr_original)
                                print("Replacing all the values with", name2, "by", name1, ". Similarity: ", sim)

        # We create the table
        rep_table = pd.DataFrame({'original': arr_uniq, 'most_freq': arr_uniq_copy})

        if show:
            display(rep_table)

        ls_orig_rep = [rep_table[rep_table.original == value].most_freq.values[0] for value in orig_ls]

        return ls_orig_rep

    # ---------------- Language ------------------------

    @staticmethod
    def Language_check(mixed_text, lang_check='en'):
        """
        This function checks if the language of the text is the expected

        inputs:
        - mixef_text => text to analyze
        - lang_check => the language we want to validate

        output:
        boolean, true or false
        """

        det = Detector(mixed_text, quiet=True)
        lang = det.languages[0].code
        conf = det.languages[0].confidence

        if (lang == lang_check) and (conf > 0.5):
            return True

        return False

    # ---------------- Sentiment ------------------------

    # English
    def English_sentiment(self, sentence, show=False):
        """
        This function analyzes a sentence in english to see if it is possitive or negative

        inputs:
        - sentence => text to analyze
        - show => if its True then it will show the results

        output:
        returns a float between +-1 whith the result
        """

        vs = self.analyzer_en.polarity_scores(sentence)
        if (vs['compound'] != 0) and show:
            print('----------------------------------------------')
            print(sentence)
            print(vs['compound'])

        return vs['compound']

    # Spanish
    def Spanish_sentiment(self, sentence, show=False):
        """
        This function analyzes a sentence in spanish to see if it is possitive or negative

        inputs:
        - sentence => text to analyze
        - show => if its True then it will show the results

        output:
        returns a float between +-1 whith the result
        """

        vs = self.analyzer_es.sentiment(sentence) * 2 - 1
        if (vs != 0) and show:
            print('----------------------------------------------')
            print(sentence)
            print(vs)

        return vs

    # -------------- Language + Sentiment ------------------

    def comment_sentiment(self, comment, show=False):
        """
        This functions takes a comment, checks the language and if its english it checks the sentiment
        input:
        - comment -> text to analyze
        - show -> if you want to show results

        output:
        sentiment is a value between +-1
        """

        try:
            # Check if its in english
            is_english = self.Language_check(comment)

            if is_english:
                # Check the sentiment
                return self.English_sentiment(comment, show)

            # Works for both
            is_spanish = self.Language_check(comment, 'es')
            is_italian = self.Language_check(comment, 'it')

            if is_spanish or is_italian:
                # Check the sentiment
                return self.Spanish_sentiment(comment, show)

            return 0

        except:
            return 0
