#!/usr/bin/python

""" 
Use code from lesson 3 (Decision Trees) to tune classifier for final project
"""
    
import sys
sys.path.append("../tools/")
from sklearn.cross_validation import train_test_split
import numpy
from tester import test_classifier
from feature_format import featureFormat, targetFeatureSplit


#features_train, features_test, labels_train, labels_test = train_test_split(features, labels, random_state = 42, test_size = 0.3)

##Create Classiier
from sklearn import tree

features_list = ['poi', 'exercised_stock_options',  
'fraction_to_poi', 'fraction_s_bonus']


### features_train and features_test are the features for the training
### and testing datasets, respectively
### labels_train and labels_test are the corresponding item labels

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

#split data into test and training groups
features_train, features_test, labels_train, labels_test = train_test_split(features, labels, random_state = 42, test_size = 0.3)

#build classifier and calculate accuracy (r2), precision and recall
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.grid_search import GridSearchCV

#min_samples = [2, 6, 8, 10, 15, 20, 30]
#max_depth = [2, 6, 8, 10, 15, 20, 30]
#min_samples = [2, 6, 10, 20]
#max_depth = [2, 6, 10, 20]

criterion = ['gini', 'entropy']
min_samples = [2, 6, 10, 20]
max_depth = [2, 6, 10, 20]
for c in criterion:
    for dep in max_depth:
        for smp in min_samples:
            clf = tree.DecisionTreeClassifier(max_depth = dep, criterion = c, min_samples_split = smp)
#            clf = clf.fit(features_train, labels_train)
#            pred = clf.predict(features_test)
#
#            acc = accuracy_score(pred, labels_test)
#            prec = precision_score(pred, labels_test)
#            recall = recall_score(pred, labels_test)
#            print "criterion, min samples, max dept: ", c, smp, dep
#            print "accuracy, precision, recall: ", acc, prec, recall
            result = test_classifier(clf, my_dataset, features_list, folds = 1000)
            print result
#==============================================================================
# #get most important features
# clf = tree.DecisionTreeClassifier( min_samples_split = 10, max_depth = 2, criterion = 'entropy')
# clf= clf.fit(features_train, labels_train)
# for i in range(0,len(clf.feature_importances_)):
#     print features_list[i], clf.feature_importances_[i]
#==============================================================================

# fit classifier with GridSearchCV

print "Fitting the classifier to the training set"
param_grid = { 'criterion': ['gini', 'entropy'],
         'min_samples_split': [2, 6, 8, 10, 15, 20, 30],
          'max_depth': [2, 6, 8, 10, 15, 20, 30] }
clf = GridSearchCV(tree.DecisionTreeClassifier(), param_grid, scoring = 'recall')
clf = clf.fit(features_train, labels_train)
print "Best estimator found by grid search:"
print clf.best_estimator_
clf = tree.DecisionTreeClassifier(max_depth = 6, criterion = 'entropy', min_samples_split = 10)
result = test_classifier(clf, my_dataset, features_list, folds = 1000)
