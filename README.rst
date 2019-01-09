FrameIt
========
FrameIt is a system for creating custom frames for text corpora.
FrameIt uses Python3 + Spacy2

For an in-depth explanation of the FrameIt system architecture, please see http://www.aclweb.org/anthology/W18-6123
Full citation:
Dan Iter, Alon Halevy, Wang-Chiew Tan. FrameIt: Ontology Discovery for Noisy User-Generated Text. In Proceedings of the 2018 EMNLP Workshop W-NUT: The 4th Workshop on Noisy User-generated Text, Pages 173-183

Features
--------

* Intent detection for individual sentences using a CNN model
* Entity extraction paired with intents using either CNN or heuristic models
* SRL system allows for loading multiple Frames for intent detection simultaneously, allowing for the differentiation of similar domains
* Easy to train and customize using jupyter notebooks
* Evaluation scripts for convenient experimental design and iteration

Data Requirements
------------
In order to ensure accurate results, we recommend training frames with a positive data set that has at least 400 examples. Depending on the domain that you are training for, you may be able to train effective frames with as few as 100 positive examples, but behavior may be less predictable. Provide 1,000+ examples for optimal results.


Installation and quick start instructions
------------------------
After cloning the repository, set up a virtual environment. For those unfamiliar with the workflow, it is shown below.

::

    $ cd <path/to/framit/project>  
    $ virtualenv --python=/usr/bin/python3.6 env_frameit 


Or 

::

    $ conda create --name env_frameit python=3.6

::

    $ source env_frameit/bin/activate


or (if you're using conda) 

::

    $ source activate env_frameit 


Install the FrameIt module


::

    $ pip install -U -e .

Note: The first time you run pip install in a new environment, the code will build 1 GB of /.egg files necessary for organizing various packages for FrameIt. This may take several minutes depending on your hardware.

\# Install spacy language model 

::

    $ python -m spacy download en
    $ python -m spacy download en_core_web_lg


\# Enable widgets for the notebook may be required if the loading widget doesn't work

::

    $ jupyter nbextension enable --py --sys-prefix widgetsnbextension


\# Run the notebooks in the folder "Generic frame training notebooks" after install is complete and follow the instructions there.

To start the jupyter server, run

::

    $ jupyter notebook
    
This will create a new tab in your browser that will show the file hierarchy for your FrameIt installation. From there, just go to "Generic frame training notebooks" and open the first one, then follow the instructions there.

Generic frame exploration includes code to both collect data for a Frame for intent detection, as well as a call to a training function that will combine exploration data from that notebook and (optionally) data for entity-extraction from the other two notebooks to create a Frame that can be saved to a file and loaded in python.

Using a saved frame
--------------------
Once you've trained a Frame and saved it to a file, you can load it with the following Python code:

::

    from frameit import SRL, Frame
    srl = SRL()
    frame = Frame.load('your_frame.json')
    srl.addFrame(frame)

Then you can evaluate sentences with the frame by calling srl.parse:

::

    srl.parse('A string you want to evaluate')

which will return a list of dictionaries (one for each frame that detected its intent in the string) with information about the frame detected and any extracted attributes.

::

    [Sentence: A string you want to evaluate
        Frame: Your Frame Name
        Confidence: 0.74228173
        Attributes: 
 	        Noun_attr=> string (0.99723412378798), you (0.86782987698764)
             You_extracting_attr => you (1.0)]

You can load multiple frames into a single SRL in order to classify an input string among multiple intents. 

Note that while it is possible to pass multiple sentences to an SRL, the system is optimized to evaluate individual sentences at a time, and results may be unpredictable for larger pieces of text.

* Free software: Apache Software License 2.0
* Documentation: https://frameit.readthedocs.io.


Credits
-------

FrameIt was designed by Megagon Labs

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
