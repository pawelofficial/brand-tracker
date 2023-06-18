from transformers import pipeline
import numpy as np 

nlp = pipeline("text-classification",model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)

labels=[v for k,v in nlp.model.config.id2label.items()]

print (labels)
exit(1)
# Use the pipeline to analyze some text
lines=['i hate this movie'
       ,'this movie is ok'
       ,' i think this movie is neutral'
        ,'i didnt enjoy this movie'
        ,'i disliked the movie'
        ,'i hated the movie '
       ]

def parse_output(result,nlp):
    keys_dic={v:'' for k,v in nlp.model.config.id2label.items()}
    for d in result:
        label=d['label']
        score=d['score']
        if label not in keys_dic:
            raise 
        else:
            keys_dic[label]=np.round(score,3)*100
    return keys_dic


for l in lines:

    result = nlp(l)[0]
    print(result)
    d=parse_output(result,nlp)
    print(d)
    exit(1)


