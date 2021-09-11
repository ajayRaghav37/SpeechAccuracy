import json
from django.http.response import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import nltk
nltk.download('punkt')

from nltk.tokenize import word_tokenize
from gensim import corpora
import gensim.downloader as api
from gensim.utils import simple_preprocess
from gensim.matutils import softcossim

glove = api.load("glove-wiki-gigaword-50")


def test(request):
    return render(request, 'hello/test.html')

def speech(request):
    try:
        f = open("speech.txt", "r")
        text = f.read()
    except:
        text = ''

    return render(request, 'hello/speech.html', {
        "speech": text
    })


@csrf_exempt
def update(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        text = request_body['text']
        f = open("speech.txt", "w")
        f.write(text)
        f.close()
        return JsonResponse({
            # "averageScore": max((sum(scores)/len(scores) - 50) * 100 / 50, 0),
            "status": "Speech updated successfully"
        })
    else:
        return HttpResponseNotFound('Woah!')


@csrf_exempt
def compare(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)
        text1 = request_body['text']
        try:
            f = open("speech.txt", "r")
            text2 = f.read()
        except:
            return JsonResponse({
            "weighted_avg": "No speech found to compare with"
        })

        def similarity(string1, string2):
            corpus = [string1, string2]
            dictionary = corpora.Dictionary(
                [simple_preprocess(doc) for doc in corpus])
            sim_matrix = glove.similarity_matrix(dictionary=dictionary)
            sent_1 = dictionary.doc2bow(simple_preprocess(corpus[0]))
            sent_2 = dictionary.doc2bow(simple_preprocess(corpus[1]))
            cossim = softcossim(sent_1, sent_2, sim_matrix)
            return cossim*100

        def jaccard_similarity(doc_1, doc_2):
            a = set(word_tokenize(doc_1))
            b = set(word_tokenize(doc_2))
            c = a.intersection(b)
            return float(100 * len(c)) / (len(a) + len(b) - len(c))
        # sentences1 = sent_tokenize(text1)
        # sentences2 = sent_tokenize(text2)

        # scores = []

        # for sent1 in sentences1:
        #     max_score = 0

        #     for sent2 in sentences2:
        #         score = similarity(sent1, sent2)

        #         if score > max_score:
        #             max_score = score

        #     scores.append(max_score)

        sim = similarity(text1, text2)
        jac_sim = jaccard_similarity(text1, text2)

        total_length = len(text1) + len(text2)
        x = max(3, min(1000/total_length, 10)) 

        # 100 => 10
        # 
        # 1000 => 3

        y = 10 - x

        return JsonResponse({
            # "averageScore": max((sum(scores)/len(scores) - 50) * 100 / 50, 0),
            "semantic": sim,
            "semantic_scaled_down": max((sim - 70) * 100 / 30, 0),
            "lexical": jac_sim,
            "weighted_avg": str(round((x*sim + y*jac_sim)/10,2)) + ' %'
        })
    else:
        return HttpResponseNotFound('Woah!')
