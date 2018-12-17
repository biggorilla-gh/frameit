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

<?xml version="1.0" ?><wrapper>
<positive index="43900">Had a great <Exercise>workout</Exercise>at the gym this afternoon.</positive>
<negative id="3957">Yesterday, I watched my grandfather play with my son and their bond was the most touching thing I've seen in a long time.</negative>
<positive index="1089">
 After my <Exercise>workout</Exercise>I exhaled with confidence in knowing I gave it all I had.</positive>

