FrameIt2
--------
FrameIts is a system for creating custom frames for text corpora.
FrameIt2 uses Python3 + Spacy2

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
\# Running the notebooks in notebooks/Generic_frame_training_notebooks after install is complete

\# Optional if code has changed
```
$ git pull --rebase   
```

```
$ source env_frameit/bin/activate   
$ jupyter notebook  
```


* Free software: Apache Software License 2.0
* Documentation: https://frameit.readthedocs.io.


Features
--------

* Intent detection using a CNN model
* Attribute extraction paired with intents using either CNN or heuristic models
* SRL system allows for loading multiple Frames for intent detection simultaneously, allowing for the differentiation of similar domains
* Easy to train and customize using jupyter notebooks
* Evaluation scripts for convenient experimental design and iteration

Credits
-------

FrameIt was designed by Megagon Labs

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
