gold_attributes = {}
extracted_attributes = {}



for key in label.attrs.keys():
	if skip is not None:
		if key.name in skip:
			continue
	if key.name not in attr_result_dict.keys():
		#true positive, false positive, missed positive
        attr_result_dict[key.name] = [0,0,0]
    gold_attributes[key.name] = []
    extracted_attributes[key.name] = []
    for token in label.attrs[key]:
    	gold_attributes[key.name].append(token[0].text)
for srl_key in srl_label.attrs.keys():
	if skip is not None:
		if srl_key.name in skip:
			continue
	if srl_key.name not in attr_result_dict.keys():
		attr_result_dict[srl_key.name] = [0,0,0]
	if srl_key.name not in gold_attributes.keys():
		gold_attributes[srl_key.name] = []
	if srl_key.name not in extracted_attributes.keys():
		extracted_attributes[srl_key.name] = []
	for item in srl_label.attrs[srl_key]:
		if item[0].text not in extracted_attributes[srl_key.name]:
			extracted_attributes[srl_key.name].append(item[0].text)
for key2 in gold_attributes.keys():
	for gold_token in gold_attributes[key2]:
		if gold_token in extracted_attributes[key2]:
			individual_attr_true_pos_count += 1
			attr_result_dict[key2][0] += 1
		else:
			individual_attr_false_neg_count += 1
			attr_result_dict[key2][2] += 1
			if verbose_attribute and print_count < limit:
				print('Missed attribute in ', key2)
                print('Sentence: ', text)
                print('Got {0}, wanted {1}\n'.format(extracted_attributes[key2], gold_token)
                print_count += 1
for key3 in extracted_attributes.keys():
	print(gold_attributes[key3])
	for extracted_token in extracted_attributes[key3]:
		if extracted_token not in gold_attributes[key3]:
			individual_attr_false_pos_count += 1
			attr_result_dict[key3][1] += 1
			if verbose_attribute and print_count < limit:
                print('Current attribute is: ', key3)
                print('False positive attribute')
                print('Sentence: ', text)
                print('Got {0}, wanted {1}\n'.format(extracted_token, gold_attributes[key3]))
                print_count += 1




