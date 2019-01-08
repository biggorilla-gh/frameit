Evaluation (EvalAFrame.py) script documentation
------------------------

Parameters
------------------------

frame_filename: file where trained frame is stored

gold_filename: xml file of examples correctly labeled for a positive or negative match of the frame, as well as annotated for attributes

verbose_frame: boolean, if True script prints debug information about Frame for each sentence. Default False

verbose_attribte: boolean, if True script prints debug information about attribute matches for each sentence. Default False
limit: int, sets cap on number of messages to print in verbose mode. Default 5.

skip: specify names of attributes to ignore in evaluation. Default None

fuzzy: bool, if True, attributes extracted which are substrings of the gold-data attribute are ignored when calculating accuracy (normally they would be considered incorrect answers). Default False.

generous: bool, only used if fuzzy is also True. If True, fuzzy answers are instead counted as correct answers. Default False.


Evaluation data format
------------------------
Note that positive examples can also have entities labeled (in this case <Exercise></Exercise>)

<?xml version="1.0" ?><wrapper>
<positive index="43900">Had a great <Exercise>workout</Exercise>at the gym this afternoon.</positive>
<negative index="3957">Yesterday, I watched my grandfather play with my son and their bond was the most touching thing I've seen in a long time.</negative>
<positive index="1089">
 After my <Exercise>workout</Exercise>I exhaled with confidence in knowing I gave it all I had.</positive>
<negative index="2049">I chatted with Julia today.</negative>
</wrapper>

drop_gold_from_train documentation
-------------------------------

In order to avoid overfitting to evaluation data, we've provided a script called dropGold() in the file frameit/drop_gold_from_train.py. Given a file with gold-data in the above XML format and a corpus for training, it returns a gold set file and a corpus file with the gold examples removed. Optionally, you can choose to have it only use a (random) subset of the gold set. Note that for this to work, the "index" values in the gold set must correspond to the correct index values in the corpus.

Parameters
-----------
train_file: the filename of the corpus to be used for training

positive_examples: the filename of an xml file containing gold positive examples

negative_examples:  the filename of an xml file containing gold negative examples. Note that if you have positive and negative gold examples in the same file, you can pass the same file to both parameters (the script checks for whether the examples are labeled as positive or negative)

sample_size: default -1, in which case the script will use the entire gold set. If you would prefer to use a random subset of the gold set, provide an integer of the desired size.

is_random: default None, which causes the script to use a random seed for sampling. If passed an integer, it will use that integer as a seed, allowing for deterministic output.

index_column_name: default 0, set the column number for the column in the data set that contains the index.

prefix: default empty string, set the file hierarchy prefix for the desired output files (e.g. "../resources")

file_prefix: default empty string, set any desired prefix to be added to the output filenames. This is useful if you want to label your data set with a date or other identifiable name.