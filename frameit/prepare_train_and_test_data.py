'''
Calls (data_to_xml or data_to_xml_with_attributes) and drop_gold_from_train to prepare gold test data and training sets that do not include it
input file should have header:
_unit_id |		frame_name |frame_confidence |	locations    |	attribute_confidence |	original_index	| text
1664728371		meal				1		"husband:4:Person  1.0 						4					My husband and I after working dinner day cooking together while my daughter had about how was your day at school.
'''

from frameit.data_to_xml import CsvToXML
from frameit.data_to_xml_with_attributes import AttributeCsvToXML
from drop_gold_from_train import dropRepeats
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('annotated_file', help='string filename of crowd-labeled to provide a subset that will be converted to gold set xml')
parser.add_argument('--attributes', '-a', help='boolean, default True, if True adds attribute labeling to xml')
parser.add_argument('--confidence', '-c', help='boolean, default True, if True only uses confidence values above a threhhold (default .6)')
parser.add_argument('--confidence_value', '-cv', help='float, default 0.6, set a custome threshold')
parser.add_argument('--prefix', '-p', help='Set a string file prefix for all files to be written by this script, default \"../resources/prepared_data/\"')
parser.add_argument('--use_index', '-i', help='boolean, default True, if false will not attempt to recompile indices')
parser.add_argument('--training_file', '-t', help='string, filename of file to be used for training that needs duplicates with test set dropped. Default \"../resources/hm_indexed.csv\"')
parser.add_argument('--size', '-s', help='int, set size of gold set, default 100')
parser.add_argument('--tfile_index', '-ti', help='string, default \"0\", name of column containing indices in training file')
args = parser.parse_args()

def main(args):
	if args.attributes:
		attr = eval(args.attributes)
	else:
		attr = True
	if args.confidence:
		confidence = eval(args.confidence)
	else:
		confidence = True
	if args.prefix:
		prefix = args.prefix
	else:
		prefix = ''
	if args.confidence_value:
		confidence_value = float(args.confidence_value)
	else:
		confidence_value = .6
	if args.use_index:
		use_index = eval(args.use_index)
	else:
		use_index = True
	if args.training_file:
		training_file = args.training_file
	else:
		training_file = '../resources/hm_indexed.csv'
	if args.size:
		size = int(args.size)
	else:
		size = 100
	if args.tfile_index:
		tfile_index = args.tfile_index
	else:
		tfile_index = 0
	wrapper(annotated_file=args.annotated_file, attributes = attr, confidence=confidence, prefix=prefix, use_index=use_index,
		training_file=training_file, size=size, tfile_index=tfile_index, threshold=confidence_value)

def wrapper(annotated_file='../resources/sample_frameit_eval_input.csv', attributes=True,
 		confidence=True, prefix='', use_index=True, training_file='../resources/hm_indexed.csv', size=100, tfile_index=0,
 		threshold=.6):
	'''
	Keyword arguments:
		annotated_file: string, the filename of the file containing crowd worker annotation data that we want converted to an xml gold set
		attributes: boolean, default True, if True adds attribute annotation info to gold xml
		confidence: boolean, default True, if True only uses examples with confidence metric above a given threshold
		threshold: float, default .6, used for confidence calculations
		prefix: string, default '', filepath prefix to be appended to all files written out of this script
		use_index: boolean, default True, if False ignores file indexing when dropping duplicate data
		training_file: string, default '../resources/hm_indexed.csv', training filename to drop test examples from
		size: int, default 100, size of gold set to be produced. Make sure this is smaller than the full size of annotated_file
		tfile_index: string, name of the column containing indices in the training file, default '0'

	'''
	confidence_limit = threshold
	if prefix != '':
		out_prefix = prefix
	else:
		out_prefix = '../resources/prepared_data/'
	if attributes:
		intermediate_files = AttributeCsvToXML(annotated_file, id_col='_unit_id', results_col='frame_name', confidence_col='frame_confidence',
			original_index_col='original_index', text_col='text', label_confidence_col='attribute_confidence',confidence_threshold=confidence_limit,
			attribute_index='locations', use_confidence=confidence, target=out_prefix, indices=use_index).intermediate_files
	else:
		intermediate_files = CsvToXML(annotated_file, id_col = '_unit_id', results_col='frame_name', confidence_col='frame_confidence', original_index_col='original_index',
			text_col='text', confidence_threshold=confidence_limit, use_confidence=confidence, target=out_prefix).intermediate_files
	print('Now dropping duplicates from training data, ', str(intermediate_files))
	for file in intermediate_files:
		print('Dropping duplicates from ', file)
		if '/' in file:
			start_index = file.rindex('/')
		else:
			start_index = 0
		print (start_index)
		intermediate_prefix = file[start_index+1:]
		print("Intermediate prefix ", intermediate_prefix)
		file_prefix = intermediate_prefix[:intermediate_prefix.index('-')]
		print("neg prefix ", file_prefix)
		negative = out_prefix + file_prefix + '-semi_gold_set.xml'
		dropRepeats(training_file, file, negative, size, prefix=out_prefix, index_column_name=tfile_index, file_prefix=file_prefix)

# def __init__ == "__main__":
# 	if len(sys.argv) == 3:
# 		wrapper(annotated_file=argv[1], training_file=argv[2])
# 	else:
# 		print("You must pass in the annotated file, following with the training file")
main(args)