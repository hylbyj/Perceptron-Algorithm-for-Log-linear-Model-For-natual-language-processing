from subprocess import PIPE
import string
import sys, subprocess
from collections import defaultdict

# Take the feature model and computer feature vector
def feature_vector(model):
	tag_model = open(model, 'r')
	feature_model = defaultdict(float)
	for line in tag_model:
		lines = line.split()
		feature_model[lines[0]] = float(lines[1])
	tag_model.close()
	return feature_model

# Enumerate all possible histories 
def setsentence(tag_dev):
	sentence =[]
	sen = ''
	tag_file = open(tag_dev, 'r')
	for line in tag_file:
		if len(line) > 1:
			sen += line
		else:
			sen = sen[:-1]
			sentence.append(sen)
			sen = ''
	tag_file.close()		
	return sentence 

def features_set(word, tag, features):
    """Return all model features."""
    # suffixes
    features.extend(['SUFFIX:' + word[-3:] + ':3:' + tag, 'SUFFIX:' + word[-2:] + ':2:' + tag, 'SUFFIX:' + word[-1:] + ':1:' + tag])
    # prefixes
 	
    return features

def assign_weight(feature_model, histories, sentence):
	# Iterate through one sentence
	weight_history = ''
	for history in histories:
		his_seg = history.split()
		if len(his_seg) > 0:
			position = int(his_seg[0]) - 1
			bigram_feature = 'BIGRAM:' + his_seg[1] + ':' + his_seg[2]
			tag_feature = 'TAG:' + sentence[position].split()[0] + ':' + his_seg[2]
			word = sentence[position].split()[0]
			tag = his_seg[2]
			features = features_set(word, tag, [bigram_feature, tag_feature])
			currentf = "CURRENTWORD" + ':' + word + ':' + tag
			features.append(currentf)
			if position > 0:
				previousf = "PREVIOUSWORD" + ":" + sentence[position-1].split()[0] + ":" + tag;
				features.append(previousf);
			if position > 1:
				previoustwo = "WORDTWOBACK" + ':' + sentence[position-2].split()[0] + ":" + tag;
				features.append(previoustwo);
			if position < len(sentence) - 1:
				nextf = "NEXTWORD" + ':' + sentence[position+1].split()[0] + ":" + tag;
				features.append(nextf)
			if position < len(sentence) - 2:
				nexttf = "WORDTWOAHEAD" + ":" + sentence[position+2].split()[0] + ":" + tag;
				features.append(nexttf)
			
			features.extend(['PREFIX:' + word[:3] + ':3:' + tag, 'PREFIX:' + word[:2] + ':2:' + tag, 'PREFIX:' + word[:1] + ':1:' + tag])

			if position > 1:
				wordbi1 = 'WORDBI1' + ':' + sentence[position -2].split()[0] + ':' + sentence[position -1].split()[0] + ':' +tag
				features.append(wordbi1)
			if position > 0:
				wordbi2 = "WORDBI2" + ':' + sentence[position -1].split()[0] + ':' + word + ':' +tag
				features.append(wordbi2)
			weight = 0


			for feature in features:
				if feature in feature_model:
					weight += feature_model[feature]
			temp_his = history + ' ' + str(weight) + '\n'
			weight_history += temp_his
	return weight_history[:-1]

def get_highest_tag(sentences, feature_model, out_file):
	# Subprocess
	enum_server = subprocess.Popen(["python", "tagger_history_generator.py",  "ENUM"], stdin=PIPE, stdout=PIPE)
	decoder_server = subprocess.Popen(["python", "tagger_decoder.py", "HISTORY"], stdin=PIPE, stdout=PIPE)
	outfile = open(out_file, 'w')
	for sentence in sentences:
		histories = call(enum_server, sentence).split('\n')
		sentence = sentence.split()
		weight_history = assign_weight(feature_model, histories, sentence)
		highest_tag = call(decoder_server, weight_history).split('\n')
		for i in range(0, len(sentence)):
			outfile.write(sentence[i] + ' ' + highest_tag[i].split()[2] + '\n')
		outfile.write('\n')

	outfile.close()
	return highest_tag

def call(process, stdin):
  "Send command to a server and get stdout."
  output = process.stdin.write(stdin + "\n\n")
  line = ""
  while 1: 
    l = process.stdout.readline()
    if not l.strip(): 
    	break
    line += l
  return line

def main(args):
	feature_model = feature_vector(args[2])
	sentences = setsentence(args[1])
	get_highest_tag(sentences, feature_model,args[3])

if __name__ == "__main__":
	main(sys.argv)
