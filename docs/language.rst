Using FrameIt for languages other than English
=====================================

FrameIt supports any language for which Spacy2 models exist. As of January 2019, Spacy supports English, Spanish, German, Italian, Portuguese, French, and Dutch.

Install language files
----------------------------
You can install the Spacy model for other languages similar to how you installed the English spacy model.

::

   $ python -m spacy download en

The model names for various languages are as follows:

::

   	    'de': 'de_core_news_sm',
            'es': 'es_core_news_sm',
            'pt': 'pt_core_news_sm',
            'it': 'it_core_news_sm',
            'nl': 'nl_core_news_sm',
            'fr': 'fr_core_news_sm',

Running FrameIt in other languages
------------------------------------
Language-dependent Spacy models are used when instantiating new Utterances. Thus, we need to pass a language value whenever we initialize a new Utterance or Corpus (which in turn creates Utterances). In most cases, you will only need to initialize a Corpus (as is shown in the frame training notebook tutorials). However, you may want to generate spacy embeddings for individual sentences, as seen in the lambda_rule notebook.

To set a desired language, simply use the parameter “lang” and set it equal to the two-letter code for the language of your choice. If no language is provided, English will be selected by default. Language codes must also be provided to SRLs.

Corpus initialization example

:: 

   corpus = Corpus(corpus_file, build_index=False, lang=‘de’)

Sentence initialization example

::

    tp = TextProcessing()
    sent = tp.nlp[‘de’](“Friedrich hat mir gestern geholfen”)

SRL initialization example

::

   srl = SRL(lang="de")

Note that Frames and SRLs are designed to be language specific: loading frames built for multiple different languages into the same SRL is not advised.

