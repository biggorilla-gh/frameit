#Creates XML files for each labeled intent in a .csv
#If called from function, be sure to specify filename, results column name, and any other optional arguments
#If called from command line, supply filename, results column name, and optionally custom confidence and file prefix for the output location
import csv
import pandas
import xml.etree.cElementTree as ET
import xml.dom.minidom
import argparse

class CsvToXML:
	def __init__(self, filename, id_col=0, results_col=5, confidence_col=6,original_index_col=7,
		text_col=9,confidence_threshold=0.6,use_confidence=True,target=None):
		'''
		Convert a CSV file with data labeled for a frame intent and attributes into an XML file for use as a gold set
		filename: the string name of the CSV file to be converted into a gold XML set
		id_col: column number (int) or name (str) corresponding to a column with a unique identifier in the csv
		results_col: column number (int) or name (str) corresponding to the column with frame intent labels
		confidence_col: column number (int) or name (str) corresponding to a confidence value for the frame intent result
		original_index_col: column number (int) or name (str) for the column containing indices
		text_col: column number (int) or name (str) corresponding to a column with the actual sentence data points in string form
		confidence_threshold: float, sets a confidence threshold. Examples with labels that have lower confidence than the threshold will be ignored. 
		use_confidence: bool, if True uses the confidence_threshold. If False, all examples will be added to the gold set regardless of confidence
		target: string, file prefix for output file

		'''
		with open(filename, 'rb') as csvfile:
			self.data = pandas.read_csv(csvfile, header=0)
			self.id_col = self.data.columns.get_loc(id_col) if type(id_col) == str else id_col
			self.results_col = self.data.columns.get_loc(results_col) if type(results_col) == str else results_col
			self.confidence_col = self.data.columns.get_loc(confidence_col) if type(confidence_col) == str else confidence_col
			self.original_index_col = self.data.columns.get_loc(original_index_col) if type(original_index_col) == str else original_index_col
			self.text_col = self.data.columns.get_loc(text_col) if type(text_col) == str else text_col
			self.confidence_threshold = confidence_threshold
			self.use_confidence = use_confidence
			self.frame_names = set(self.data[results_col])
			self.target = target
			self.frames_dict = self.splitIntoFrames()
			self.intermediate_files = self.convertFramesToXML()

	def splitIntoFrames(self):
		dict_of_frames = dict()
		for frame_name in self.frame_names:
			pos = str(frame_name) + '_pos'
			neg = str(frame_name) + '_neg'
			dict_of_frames[pos] = set()
			dict_of_frames[neg] = set()
		for index, row in self.data.iterrows():
			if self.use_confidence:
				if row[self.confidence_col] < self.confidence_threshold:
					continue
			label = row[self.results_col]
			pos_label = str(label) + '_pos'
			for frame_name in self.frame_names:
				if label == frame_name:
					# if row[self.attribute_index] is not None:
						# row[self.text_col] = self.addAttributeNotation(row)
					dict_of_frames[pos_label].add(tuple(row))
				else:
					neg_label = str(frame_name) + '_neg'
					dict_of_frames[neg_label].add(tuple(row))
		return dict_of_frames

	def convertFramesToXML(self):
		ret = []
		for frame in self.frame_names:
			root = ET.Element(str(frame))
			# ET.SubElement(root, "field1")
			positive_set_name = str(frame) + '_pos'
			negative_set_name = str(frame) + '_neg'
			for item in self.frames_dict[positive_set_name]:
				ET.SubElement(root, 'positive', id=str(item[self.original_index_col])).text = item[self.text_col]
			for item in self.frames_dict[negative_set_name]:
				ET.SubElement(root, 'negative', id=str(item[self.original_index_col])).text = item[self.text_col]
			tree = ET.ElementTree(root)
			filename = str(self.target)+ str(frame) + '_semi_gold_set.xml'
			print('Writing to file, ',filename)
			out = xml.dom.minidom.parseString(ET.tostring(tree.getroot(),'utf-8')).toprettyxml(indent=" ")
			with open(filename, 'w') as f:
				f.write(out)
			ret.append(filename)
		return ret
			# tree.write(filename)
	def addAttributeNotation(self, row):
		crowdflower_notation = row[self.attribute_index].split('\n')
		for att in crowdflower_notation:
			end_att_name_index = att.index(':')
			att_name = row[self.attribute_index][:end_att_name_index]
			begin_att_type_index = att.rfind(':')
			att_type = att[begin_att_type_index:]
			span_start = int(att[end_att_name_index, begin_att_type_index])
			span = [span_start, (span_start + len(att_name))]
			open_xml_string = '<'+ att_type + '>'
			close_xml_string = '</' + att_type + '>'
			modified_text = row[self.text_col][:span[0]] + open_xml_string + att_name + close_xml_string + row[self.text_col][span[1]:]
			return modified_text




# main(args)

# CsvToXML('../Notebooks/Jo_Workspace/labeled_data/hm_labeled_aggregate.csv', results_col='hm_intents_results')