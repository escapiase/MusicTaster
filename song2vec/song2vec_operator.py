# coding=utf-8

"""
Created by jayvee on 17/2/22.
https://github.com/JayveeHe
"""
import pickle

from gensim import matutils
from gensim.models.word2vec_inner import REAL
from numpy.core.multiarray import ndarray, array, dot


class Song2VecOperator:
    def __init__(self, song2vec_model_path=None, artist2vec_model_path=None):
        try:
            if song2vec_model_path:
                with open(song2vec_model_path, 'rb') as s2v_file:
                    self.song2vec_model = pickle.load(s2v_file)
            if artist2vec_model_path:
                with open(artist2vec_model_path, 'rb') as a2v_file:
                    self.artist2vec_model = pickle.load(a2v_file)
            self.song2vec_model.init_sims()
            self.artist2vec_model.init_sims()
        except IOError, ioe:
            print '%s' % ioe

    def calc_song_artist_similar(self, positive_songs=[], negative_songs=[],
                                 positive_artists=[], negative_artists=[],
                                 song_weight=1.0, artist_weight=1.5,
                                 topn=10, restrict_vocab=None):
        """
        计算歌曲和歌手的加减相似度,求出最近似的歌曲top n
        Args:
            topn:
            restrict_vocab:
            artist_weight:
            song_weight:
            positive_songs:
            negative_songs:
            positive_artists:
            negative_artists:

        Returns:

        """
        try:
            positive_songs = [(word, song_weight) for word in positive_songs]
            negative_songs = [(word, -song_weight) for word in negative_songs]
            positive_artists = [(word, artist_weight) for word in positive_artists]
            negative_artists = [(word, -artist_weight) for word in negative_artists]
            all_words, mean = set(), []
            for song, weight in positive_songs + negative_songs:
                if isinstance(song, ndarray):
                    mean.append(weight * song)
                elif song in self.song2vec_model.vocab:
                    mean.append(weight * self.song2vec_model.syn0norm[self.song2vec_model.vocab[song].index])
                    all_words.add(self.song2vec_model.vocab[song].index)
                else:
                    raise KeyError("song '%s' not in vocabulary" % song)
            # limited = self.song2vec_model.syn0norm if restrict_vocab is None \
            #     else self.song2vec_model.syn0norm[:restrict_vocab]
            for artist, weight in positive_artists + negative_artists:
                if isinstance(word, ndarray):
                    mean.append(weight * artist)
                elif word in self.artist2vec_model.vocab:
                    mean.append(weight * self.artist2vec_model.syn0norm[self.artist2vec_model.vocab[artist].index])
                    all_words.add(self.artist2vec_model.vocab[artist].index)
                else:
                    raise KeyError("artist '%s' not in vocabulary" % artist)
            if not mean:
                raise ValueError("cannot compute similarity with no input")
            mean = matutils.unitvec(array(mean).mean(axis=0)).astype(REAL)
            limited = self.song2vec_model.syn0norm if restrict_vocab is None \
                else self.song2vec_model.syn0norm[:restrict_vocab]
            # limited += self.artist2vec_model.syn0norm if restrict_vocab is None \
            #     else self.artist2vec_model.syn0norm[:restrict_vocab]
            dists = dot(limited, mean)
            if not topn:
                return dists
            best = matutils.argsort(dists, topn=topn + len(all_words), reverse=True)
            # ignore (don't return) words from the input
            result = [(self.song2vec_model.index2word[sim], float(dists[sim])) for sim in best if sim not in all_words]
            return result[:topn]
        except Exception, e:
            print 'error = %s' % e


if __name__ == '__main__':
    s2vo = Song2VecOperator(song2vec_model_path='../datas/[full]50d_20iter_10win_5min_song2vec.model',
                            artist2vec_model_path='../datas/[full]50d_20iter_10win_5min_artist2vec.model')
    res = s2vo.calc_song_artist_similar(positive_songs=[u'time machine', u'yellow', u'viva la vida'],
                                        negative_songs=[],
                                        positive_artists=[],
                                        negative_artists=[],
                                        artist_weight=1.0, topn=20)

    for i in res:
        print i[0], i[1]
