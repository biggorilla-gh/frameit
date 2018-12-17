FrameIt2
--------
FrameIts is a system for creating custom frames for text corpora.
FrameIt2 uses Python3 + Spacy2

Features
--------

* Intent detection using a CNN model
* Attribute extraction paired with intents using either CNN or heuristic models
* SRL system allows for loading multiple Frames for intent detection simultaneously, allowing for the differentiation of similar domains
* Easy to train and customize using jupyter notebooks
* Evaluation scripts for convenient experimental design and iteration

Installation
------------
$ pip install virtualenv . (if you're using virtualenv to create an environment, another way is conda)


Quick start instructions
------------------------
Create a virtual environment

First you need to create a virtual environment the usual way. For those unfamiliar with the workflow, it is shown below.

```
$ cd <path/to/framit/project>  
$ virtualenv --python=/usr/bin/python3.6 env_frameit 
```

Or conda create --name framers python=3.6

```
$ source env_frameit/bin/activate
```

or (if you're using conda) 

```$
$ source activate framers 
```

Install the FrameIt2 module

```
$ pip install -U -e .
```

\# Install spacy language model 

```
$ python -m spacy download en
$ python -m spacy download en_core_web_lg
```

\# Enable widgets for the notebook may be required if the loading widget doesn't work

```
$ jupyter nbextension enable --py --sys-prefix widgetsnbextension
```

\# Run the notebooks in the folder "Generic frame training notebooks" after install is complete and follow the instructions there. Generic frame exploration includes code to both collect data for a Frame for intent detection, as well as a call to a training function that will combine exploration data from that notebook and (optionally) data for entity-extraction from the other two notebooks to create a Frame that can be saved to a file and loaded in python.


* Free software: Apache Software License 2.0
* Documentation: https://frameit.readthedocs.io.


Credits
-------

FrameIt was designed by Megagon Labs

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
