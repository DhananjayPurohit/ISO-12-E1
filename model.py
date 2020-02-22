from nltk.corpus import twitter_samples, stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tag import pos_tag 
from nltk.tokenize import word_tokenize
from nltk import NaiveBayesClassifier
import re, string 
import random 
import pickle
import pandas as pd 

class Sentiment:

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.positive_cleaned_tokens_list = []
        self.negative_cleaned_tokens_list = []
        self.positive_tweets_tokens = twitter_samples.tokenized('positive_tweets.json')
        self.negative_tweets_tokens = twitter_samples.tokenized('negative_tweets.json')
        self.non_abusive = self.positive_tweets_tokens[:808] + self.negative_tweets_tokens[:811]
        self.abusive_words = pd.read_csv('bad-words.csv')['jigaboo']
        self.abusive = []
        for word in self.abusive_words:
            self.abusive.append(word)

    def remove_noise(self, token_):
        cleaned_tokens = []

        for token, tag in pos_tag(token_):
            '''
            Here regex removes the unwanted hyperlinks and username preceded by @
            '''
            token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
            token = re.sub("(@[A-Za-z0-9_]+)","", token)

            if tag.startswith('NN'):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'

            lemmatizer = WordNetLemmatizer()
            token = lemmatizer.lemmatize(token, pos)

            if len(token)>0 and token not in string.punctuation and token.lower() not in self.stop_words:
                cleaned_tokens.append(token.lower())

        return cleaned_tokens

        
    def get_tweet_for_model(self, cleaned_tokens_list, sen):
        if sen == 'p':
            for tweet_tokens in cleaned_tokens_list:
                yield dict([token, True] for token in tweet_tokens)
        else:
            for tweet_tokens in cleaned_tokens_list:
                yield dict([tweet_tokens, True])


    def preprocess_data(self):

        for tokens in self.non_abusive:
            self.positive_cleaned_tokens_list.append(self.remove_noise(tokens))

        positive_tokens_for_model = self.get_tweet_for_model(self.positive_cleaned_tokens_list, 'p')
        negative_tokens_for_model = []

        for word in self.abusive:
            dict_ = {word: True}
            e = (dict_, 'Negative')
            negative_tokens_for_model.append(e)

        positive_dataset = [(tweet_dict, "Positive") for tweet_dict in positive_tokens_for_model]
        negative_dataset = negative_tokens_for_model

        dataset = positive_dataset + negative_dataset
        random.shuffle(dataset)

        # Splitting data [70:30 ratio]
        train_data = dataset[:6000]

        return train_data

    
    def train_data(self):
        train_set = self.preprocess_data()
        classifier = NaiveBayesClassifier.train(train_set)
        f = open('my_classifier.pickle', 'wb')
        pickle.dump(classifier, f)
        return classifier 
