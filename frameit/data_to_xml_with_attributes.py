#Creates XML files for each labeled intent in a .csv
#Note: You will likely want to change the default column values based on your specific csv file's column names
#If called from function, be sure to specify filename, results column name, and any other optional arguments
#If called from command line, supply filename, results column name, and optionally custom confidence and file prefix for the output location
import csv
import pandas
import xml.etree.cElementTree as ET
import xml.dom.minidom
import argparse
import math

# parser = argparse.ArgumentParser()
# parser.add_argument('filename', help='filename of csv to be converted')
# parser.add_argument('results_col', help='name of column containing result labels')
# parser.add_argument('--text', help='name of the text column')
# parser.add_argument('--ignore_confidence', '-i', help=' set boolean to ignore confidence threshold, default False')
# parser.add_argument('--confidence_value', '-c', '-cv', type=float, help='confidence threshold for labels')
# parser.add_argument('--attribute_col', '-a', help='name of column containing attribute info')
# parser.add_argument('--target', '-t', help='Filename prefix of output files')
# parser.add_argument('--ref', '-n', help='False if its not needed to created referencing ids')
# args = parser.parse_args()

# def main(args):
# 	if args.target:
# 		target = args.target
# 	else:
# 		target=""
# 	if args.text:
# 		text = args.text
# 		original_index = 0
# 	else:
# 		text = 20
# 		original_index = 9
# 	if args.ignore_confidence:
# 		if args.ignore_confidence != 'False':
# 			print('Ignoring confidence metrics')
# 			use_confidence = False
# 		else:
# 			use_confidence = True
# 	else:
# 		use_confidence = True

# 	indices = True
# 	if args.ref: 
# 		if args.ref == 'False':
# 			indices = False
# 		else: 
# 			indices = True

# 	if args.confidence_value:
# 		print('running with custom threshold')
# 		CsvToXML(args.filename, results_col=args.results_col, original_index_col =original_index,  text_col=text, confidence_threshold=args.confidence_value, target=target, indices=indices)
# 	else:
# 		CsvToXML(args.filename, results_col=args.results_col, original_index_col =original_index, text_col=text,use_confidence=use_confidence, target=target, indices=indices)

class AttributeCsvToXML:
	def __init__(self, filename, id_col=0, results_col=16, confidence_col=6,original_index_col=9,
		text_col=20,label_confidence_col=8,confidence_threshold=0.6,attribute_index='locations',use_confidence=True,target=None, indices=True):
		with open(filename, 'rb') as csvfile:
			self.data = pandas.read_csv(csvfile, header=0)
			self.filename = filename

			self.id_col = self.data.columns.get_loc(id_col) if type(id_col) == str else id_col
			self.results_col = self.data.columns.get_loc(results_col) if type(results_col) == str else results_col
			self.confidence_col = self.data.columns.get_loc(confidence_col) if type(confidence_col) == str else confidence_col
			self.original_index_col = self.data.columns.get_loc(original_index_col) if type(original_index_col) == str else original_index_col
			self.text_col = self.data.columns.get_loc(text_col) if type(text_col) == str else text_col

			self.confidence_threshold = confidence_threshold
			self.use_confidence = use_confidence
			self.frame_names = set(self.data[results_col])
			self.attribute_index = self.data.columns.get_loc(attribute_index) if type(attribute_index) == str else attribute_index
			self.label_confidence_col = self.data.columns.get_loc(label_confidence_col) if type(label_confidence_col) == str else label_confidence_col
			self.target = target
			print('Adding column numbers')
			if indices:
				self.data[self.id_col] = self.addColumnNumbers()
			print('Done adding column numbers')
			print('Converting to XML')
			self.frames_dict = self.splitIntoFrames(original_index_col)
			self.intermediate_files = self.convertFramesToXML()
	
	def addColumnNumbers(self):
		# old_data_filename = '../resources/hm_indexed.csv'
		# old_text_column = 'text'
		# old_index_column = 'Index'
		old_data_filename = self.filename
		old_text_column = self.text_col
		old_index_column = self.original_index_col

		index_dict = {}
		print('Indexing original datafile')
		with open(old_data_filename, 'rb') as f:
			index_source = pandas.read_csv(f)
			for i, line in index_source.iterrows():
				index_dict[line[old_text_column]] = line[old_index_column]
		print('Cross-referencing indices')
		out = []
		for index, row in self.data.iterrows():
			if index % 100 == 0:
				print(str(index) + '/' + str(len(self.data)))
			text = row[self.text_col]
			if text in index_dict.keys():
				row[self.id_col] = index_dict[text]
				out.append(index_dict[text])
			else:
				row[self.id_col] = None
				out.append(None)
		return out

	def splitIntoFrames(self,original_index_col):
		# print(self.data[self.id_col])
		# print(self.data.loc[0,0])
		dict_of_frames = dict()
		for frame_name in self.frame_names:
			pos = str(frame_name) + '_pos'
			neg = str(frame_name) + '_neg'
			dict_of_frames[pos] = set()
			dict_of_frames[neg] = set()
		for index, row in self.data.iterrows():
			# if isinstance(self.data.loc[index,self.original_index_col], str):
				# print(self.data.loc[index,self.original_index_col])
			# print(str(self.data.loc[index,8'0']))
			if not math.isnan(self.data.loc[index,original_index_col]):
				row['_unit_id'] = int(self.data.loc[index,original_index_col])
			else:
				row['_unit_id'] = None
			if self.use_confidence:
				if row[self.confidence_col] < self.confidence_threshold:
					continue
			label = row[self.results_col]
			pos_label = str(label) + '_pos'
			for frame_name in self.frame_names:
				if label == frame_name:
					if row[self.attribute_index] is not None:
						# print(row[self.text_col])
						row[self.text_col] = self.addAttributeNotation(row)
					dict_of_frames[pos_label].add(tuple(row))
				else:
					neg_label = str(frame_name) + '_neg'
					dict_of_frames[neg_label].add(tuple(row))
		return dict_of_frames

	def convertFramesToXML(self):
		# print (self.original_index_col)
		ret = []
		for frame in self.frame_names:
			print("Processing frame: ", frame)
			root = ET.Element(str(frame))
			# ET.SubElement(root, "field1")
			positive_set_name = str(frame) + '_pos'
			negative_set_name = str(frame) + '_neg'
			for item in self.frames_dict[positive_set_name]:
				# if not isinstance(item[self.id_col], int):
					# print("Possible exception: ", item[self.id_col])
					# continue
				ET.SubElement(root, 'positive', index=str(item[self.id_col])).text = item[self.text_col]
			for item in self.frames_dict[negative_set_name]:
				ET.SubElement(root, 'negative', index=str(item[self.id_col])).text = item[self.text_col]
			tree = ET.ElementTree(root)
			filename = str(self.target)+ str(frame) + '-semi_gold_set.xml'
			# print(ET.tostring(tree.getroot(),'utf-8')[0:50])
			out = xml.dom.minidom.parseString(ET.tostring(tree.getroot(),'utf-8')).toprettyxml(indent=" ")
			replacements = {'&lt;': '<', '&gt;':'>'}
			for src, target in replacements.items():
				out = out.replace(src, target)
			print('Writing to file, ', filename)
			with open(filename, 'w') as f:
				f.write(out)
			ret.append(filename)
		return ret
			# tree.write(filename)
	def addAttributeNotation(self, row):
		# print(row[self.attribute_index])
		# print(type(row[self.attribute_index]))
		if isinstance(row[self.attribute_index], float) :
			return row[self.text_col]
		crowdflower_notation = row[self.attribute_index].split('\n')
		if self.use_confidence:
			confidence = row[self.label_confidence_col].split('\n')
		completed = []
		text = row[self.text_col]
		for i, att in enumerate(crowdflower_notation):
			if self.use_confidence:
				if float(confidence[i]) < self.confidence_threshold:
					continue
			mod = 0
			# end_att_name_index = att.index(':')
			begin_att_type_index = att.rfind(':')+1
			end_att_name_index = att[:begin_att_type_index-1].rfind(':')
			att_name = att[:end_att_name_index]
			att_type = att[begin_att_type_index:]
			span_start = int(att[end_att_name_index+1:begin_att_type_index-1])
			span = [span_start, (span_start + len(att_name))]
			for e in completed:
				if e[0] < span[0]:
					mod += e[1]
			open_xml_string = '<'+ att_type + '>'
			close_xml_string = '</' + att_type + '> '
			xml_addition = open_xml_string + att_name + close_xml_string
			# print(xml_addition)
			# print(row[self.text_col])
			modified_text = text[:span[0]-1+mod] + xml_addition + text[span[1]+mod:]
			completed.append([span_start,len(open_xml_string)+len(close_xml_string)-1])
			text = modified_text
		# print(text)
		return text




# main(args)

# CsvToXML('../Notebooks/Jo_Workspace/labeled_data/hm_labeled_aggregate.csv', results_col='hm_intents_results')