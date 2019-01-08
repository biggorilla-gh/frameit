#Note: this script maintains a slight syntactic difference in the xml file between positive and negative examples, see line 33/34
#Note: This script takes separate filenames for gold set positive and negative examples. Because it exclusively searches for positive examples 
# 		in the positive one, and negative in the negative (see line 21/22), these two filenames can actually be the same, and neither must exclusively contain examples of its assigned valence

from frameit.utils import set_seed
import random
import pandas
import uuid
import os
from xml.dom import minidom


def dropGold(train_file, positive_examples, negative_examples, sample_size=-1, is_random=None, index_column_name=0, prefix='', file_prefix=''):
	'''
	removes gold-set examples from the training set
	Parameters:
	train_file: the filename of the corpus to be used for training

	positive_examples: the filename of an xml file containing gold positive examples

	negative_examples:  the filename of an xml file containing gold negative examples. Note that if you have positive and negative gold examples in the same file, you can pass the same file to both parameters (the script checks for whether the examples are labeled as positive or negative)

	sample_size: default -1, in which case the script will use the entire gold set. If you would prefer to use a random subset of the gold set, provide an integer of the desired size.

	is_random: default None, which causes the script to use a random seed for sampling. If passed an integer, it will use that integer as a seed, allowing for deterministic output.

	index_column_name: default 0, set the column number for the column in the data set that contains the index.

	prefix: default empty string, set the file hierarchy prefix for the desired output files (e.g. "../resources")

	file_prefix: default empty string, set any desired prefix to be added to the output filenames. This is useful if you want to label your data set with a date or other identifiable name.
	'''
	if is_random is None:
		seed = random.randint(0,100)
		set_seed(seed)
	elif isinstance(random, int):
		seed = random
		set_seed(seed)
	print("Seed is ", seed)
	session_id = uuid.uuid4()
	positive_xml = minidom.parse(positive_examples)
	negative_xml = minidom.parse(negative_examples)
	positive_list = positive_xml.getElementsByTagName('positive')
	negative_list = negative_xml.getElementsByTagName('negative')
	gold_set = set()
	training_dict, column_names = indexTrainingFile(train_file, index_column_name)
	#Default mode: use all gold examples
	if sample_size < 0:
		for ex in positive_list + negative_list:
			gold_set.add(ex)
			if 'index' in ex.attributes.keys():
				ind = ex.attributes['index'].value 
			else:
				ind = ex.attributes['id'].value
			if isinstance(ind, int):
				del training_dict[ind]
			elif isinstance(ind, str):
				if int(ind) in training_dict.keys():
					del training_dict[int(ind)]
			else:
				print('Caught exception, ' + str(ind))
				print(type(ind))
	#Sampling mode: use a random sample of gold examples
	else:
		for i in range(0,sample_size):
			pos_choice = random.choice(positive_list)
			neg_choice = random.choice(negative_list)
			while pos_choice in gold_set:
				pos_choice = random.choice(positive_list)
			while neg_choice in gold_set:
				neg_choice = random.choice(negative_list)
			gold_set.add(pos_choice)
			gold_set.add(neg_choice)
			if 'index' in pos_choice.attributes.keys():
				ind = pos_choice.attributes['index'].value 
			else:
				ind = pos_choice.attributes['id'].value

			if 'index' in neg_choice.attributes.keys():
				neg_ind = neg_choice.attributes['index'].value
			else:
				neg_ind = neg_choice.attributes['id'].value

			if isinstance(ind, int):
				del training_dict[ind]
			elif isinstance(ind, str):
				if int(ind) in training_dict.keys():
					del training_dict[int(ind)]
			else:
				print('Caught exception, ' + str(ind))
				print(type(ind))
			if isinstance(neg_ind, int):
				del training_dict[neg_ind]
			elif isinstance(neg_ind, str):
				if int(neg_ind) in training_dict.keys():
					del training_dict[int(neg_ind)]
			else:
				print('Caught exception, ' + str(neg_ind))
				print(type(neg_ind))
	new_training_file = recompileTrainingFile(training_dict, column_names, session_id, train_file, file_prefix, prefix)
	gold_file = writeGoldSet(gold_set,session_id,positive_examples, file_prefix, prefix)
	print('Done')
	return new_training_file, gold_file

def indexTrainingFile(file, index_column_name):
	'''
	Converts the training file into a hash map for easy access and modification
	'''
	out = {}
	print('Indexing data file')
	with open(file, 'rb') as training_file:
		source = pandas.read_csv(training_file)
		column_names = list(source)
		for i, line in source.iterrows():
			new_line = list()
			for element in line:
				new_line.append(element)
			out[line[index_column_name]] = line
	return out, column_names

def writeGoldSet(gold_set, session_id, old_filename, file_prefix, prefix):
	'''
	Writes the gold set to a file
	'''
	print('Writing gold set to xml file')
	filename = prefix + file_prefix + 'gold_examples' + str(session_id) + '.xml'
	with open(filename, 'w') as file:
		file.write('<?xml version=\"1.0\" ?>')
		file.write('<wrapper>')
		for e in gold_set:
			file.write(e.toprettyxml(indent=" "))
		file.write('</wrapper>')
	return filename

def recompileTrainingFile(training_dictionary, column_names, session_id, filename, file_name, prefix):
	'''
	Converts the modified training set backinto a csv for use by FrameIt
	'''
	print('Recompiling training file')
	out_list = []
	print("file_prefix ",file_name)
	out = pandas.DataFrame(list(training_dictionary.values()), columns=column_names)
	new_filename = prefix + filename[filename.rindex('/'):-4] + file_name + '_drop_v'+str(session_id) + '.csv'
	out.to_csv(new_filename, sep=',')
	return new_filename

