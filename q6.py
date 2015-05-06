from subprocess import PIPE
import sys, subprocess
from collections import defaultdict

# Using Perceptron algorithm 
def perceptron(train_sentences, train_model):
	gold_server = subprocess.Popen(['python', 'tagger_history_generator.py', 'GOLD'], stdin=PIPE, stdout=PIPE)
	enum_server = subprocess.Popen(['python', 'tagger_history_generator.py', 'ENUM'], stdin=PIPE, stdout=PIPE)
	decoder_server = subprocess.Popen(["python", "tagger_decoder.py", "HISTORY"], stdin=PIPE, stdout=PIPE)
	# Iterate for 5 times
	model_1 = defaultdict(float)
	gold_dict = {}
	gold_features = {}
	gold_words = {}
	for i in range(0, 5):
		print "This is" + str(i) + "iteration"
		h = 0
		for sentence in train_sentences:
			if i == 0:
				gold_words[h] = call(gold_server, sentence)
				gold_word = gold_words[h].split('\n')
				gold_dict[h] = get_features(gold_word, sentence.split('\n'), {}, 0)
				#gold_features[h], gold_dict[h] = set_gold_features(gold_words[h].split('\n'), sentence.split('\n'), {})
			# Compute the histories highest scores
			histories = call(enum_server, sentence).split('\n')
			#sentence = sentence.split()
			#print model_1
			#weight_history = assign_weight({}, histories, sentence.split('\n'))
			
			weight_history = get_features(histories, sentence.split('\n'), model_1, 1)
			highest_tag = call(decoder_server, weight_history).split('\n')
			#highest_features, feature_model = set_gold_features(highest_tag, sentence.split('\n'), {})
			#if highest_features!= gold_features[h]:
			if highest_tag != gold_words[h]:
				features = get_features(highest_tag, sentence.split('\n'), {}, 0)
				for hi in gold_dict[h].iterkeys():
					model_1[hi] += gold_dict[h][hi]
				for hig in features.iterkeys():
					model_1[hig] -= features[hig]

			#print "weight history" + str(weight_history)
			
			#print "gold feature" + str(highest_features)
			#print gold_features[h] == highest_features
			h += 1

	outfile = open(train_model, 'w')
	for f in model_1.iterkeys():
		outfile.write(f + ' ' + str(model_1[f]) + '\n')
	outfile.close()
	return model_1

def assign_weight(feature_model, histories, sentence):
	# Iterate through one sentence
	weight_history = ''
	#features = []
	for history in histories:
		
		his_seg = history.split()
		if len(his_seg) > 0 and his_seg[2] != 'STOP':
			features = []
			position = int(his_seg[0]) - 1
			#print position
			word = sentence[position].split()[0]
			tagger = his_seg[2]	
			bigram_feature = 'BIGRAM:' + his_seg[1] + ':' + his_seg[2]
			features.append(bigram_feature)
			tag_feature = 'TAG:' + sentence[position].split()[0] + ':' + his_seg[2]
			features.append(tag_feature)
			features.extend(['SUFFIX:' + word[-3:] + ':' + tagger, 'SUFFIX:' + word[-2:] + ':' + tagger, 'SUFFIX:'+word[-1:] + ':' + tagger])
			weight = 0
			for feature in features:
				if feature in feature_model:
					weight += feature_model[feature]
			temp_his = history + ' ' + str(weight) + '\n'
			weight_history += temp_his
	return weight_history[:-1]

# Create gold features based on gold taggers and sentence
def set_gold_features(gold_words, sentence, model):
	gold_features = []
	print gold_words
	for gold_word in gold_words:
		
		gold_word = gold_word.split()
		if len(gold_word) > 0 and gold_word[2] != 'STOP':
			temp_features = []
			position = int(gold_word[0]) - 1
			word = sentence[position].split()[0]
			tagger = gold_word[2]
			bigram_feature = 'BIGRAM:' + gold_word[1] + ':' + gold_word[2]
			gold_features.append(bigram_feature)
			temp_features.append(bigram_feature)
			tag_feature = 'TAG:' + sentence[position].split()[0] + ':' + gold_word[2]
			gold_features.append(tag_feature)
			temp_features.append(tag_feature)
			gold_features.extend(['SUFFIX:' + word[-3:] + ':' + tagger, 'SUFFIX:' + word[-2:] + ':'+ tagger, 'SUFFIX:'+word[-1:] + ':' +tagger])
			temp_features.extend(['SUFFIX:' + word[-3:] + ':' + tagger, 'SUFFIX:' + word[-2:] + ':'+ tagger, 'SUFFIX:'+word[-1:] + ':' +tagger])
			for f in temp_features:
				if f in model:
					model[f] += 1.0
				else:
					model[f] =1.0
	return gold_features, model

def features_set(word, tag, features):
    """Return all model features (suffix only for this model)."""
    features.extend(['SUFFIX:' + word[-3:] + ':3:' + tag, 'SUFFIX:' + word[-2:] + ':2:' + tag, 'SUFFIX:' + word[-1:] + ':1:' + tag])
    # Additional Features are here

    return features

def get_features(histories, sentence, model, score):
    """Return scored histories, or dictionary of features."""
    result = ''
    for history in histories:
        history_list = history.split()
        if len(history_list) > 0 and history_list[2] != 'STOP':
			pos = int(history_list[0]) - 1
			# get the word and the tag
			word = sentence[pos].split()[0]
			tag = history_list[2]
			weight = 0            
			bigram = 'BIGRAM:' + history_list[1] + ':' + tag
			t = 'TAG:' + word + ':' + tag
			features = features_set(word, tag, [bigram, t])
			#Additional Features are here
			currentf = "CURRENTWORD" + ':' + word + ':' + tag
			features.append(currentf)
			if pos > 0:
				previousf = "PREVIOUSWORD" + ":" + sentence[pos-1].split()[0] + ":" + tag;
				features.append(previousf);
			if pos > 1:
				previoustwo = "WORDTWOBACK" + ':' + sentence[pos-2].split()[0] + ":" + tag;
				features.append(previoustwo);
			if pos < len(sentence) - 1:
				nextf = "NEXTWORD" + ':' + sentence[pos+1].split()[0] + ":" + tag;
				features.append(nextf)
			if pos < len(sentence) - 2:
				nexttf = "WORDTWOAHEAD" + ":" + sentence[pos+2].split()[0] + ":" + tag;
				features.append(nexttf)
			#Prefix
			features.extend(['PREFIX:' + word[:3] + ':3:' + tag, 'PREFIX:' + word[:2] + ':2:' + tag, 'PREFIX:' + word[:1] + ':1:' + tag])
			#features.append('LEN:' + str(len(word)) + ':' + tag)
            # calculate the weight for this history
			if pos > 1:
				wordbi1 = 'WORDBI1' + ':' + sentence[pos-2].split()[0] + ':' + sentence[pos-1].split()[0] + ':' +tag
				features.append(wordbi1)
			if pos > 0:
				wordbi2 = "WORDBI2" + ':' + sentence[pos-1].split()[0] + ':' + word + ':' +tag
				features.append(wordbi2)
			for feature in features:
                # calculate the weight for this history
				if score == 1:
					if feature in model:
						weight += model[feature]
                # for training
				else:
					if feature in model:
						model[feature] += 1
					else:
						model[feature] = 1
			result += (history + ' ' + str(weight) + '\n')
    if score == 1:
        return result[:-1]
    return model

# Enumerate all trainning sentences (words with tags)
def setsentence(tag_train):
	sentence =[]
	sen = ''
	tag_file = open(tag_train, 'r')
	for line in tag_file:
		if len(line) > 1:
			sen += line
		else:
			sen = sen[:-1]
			sentence.append(sen)
			sen = ''
	tag_file.close()		
	return sentence 

def call(process, stdin):
    """For use with given processes."""
    output = process.stdin.write(stdin + '\n\n')
    line = ''
    while 1:
        l = process.stdout.readline()
        if not l.strip(): 
            break
        line += l
    return line

def main(args):
	perceptron(setsentence(args[1]),args[2])

if __name__ == "__main__":
	main(sys.argv)