Question 4
Instruction:
1.python q4.py tag_dev.dat tag.model tag_dev.out
This instruction gives out the result in tag_dev.out
2.python eval_tagger.py tag_dev.key tag_dev.out 
This instruction helps you to get the evaluation results.
Results:
2226 2459 0.905246034974

Question 5
Instruction:
1.python q5.py tag_train.dat suffix_tagger.model
Use perceptron algorithm to compute the weight vector
2.python q4.py tag_dev.dat suffix_tagger.model tag_dev_5.out
Then create the sentence with tags as question 4 does
3.python eval_tagger.py tag_dev.key tag_dev_5.out
Results:
2265 2459 0.921106140708
There is a increase in accuracy when applying the suffix features

Question 6 
Instructions:
1.python q6.py tag_train.dat mixed_tagger.model
Use perceptron algorithm to compute the weight vector
Three addtional feature combinations used:
1)word + tag 
ex. feature combines of next word and current tag:"NEXTWORD" + ':' + sentence[position+1].split()[0] + ":" + tag;
2)prefix
3)bigrams + tag
ex.bigrams + current tag 'WORDBI1' + ':' + sentence[position -2] + ':' + sentence[position -1] + ':' +tag
2.python q4.py tag_dev.dat mixed_tagger.model tag_dev_6.out
3.python eval_tagger.py tag_dev.key tag_dev_6.out
Result:
2340 2459 0.951606344042
Thoughts: I think the accuracy increases because I take word combination and tag as a whole, which puts more emphasis on the word dependy and semantic meanings.
