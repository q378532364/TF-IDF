from sklearn.feature_extraction.text import TfidfVectorizer


class AagService():
    def __init__(self):
        self.main()
        pass

    def main(self):
        corpus = [
            'apple apple apple',
            'egg banana apple',
            'banana banana banana apple',
            'apple apple apple apple egg banana',
        ]
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(corpus)
        print(vectorizer.get_feature_names_out())
        test=['apple apple apple apple banana banana apple egg']
        tf_fit=vectorizer.transform(test)
        print(tf_fit.toarray())


if __name__ == '__main__':
   obj=AagService()



