#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data
from sklearn.grid_search import GridSearchCV


### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
## See engineer_variables for features beginning with "fraction"


features_list = ['poi', 'exercised_stock_options',  'fraction_to_poi',
'fraction_s_bonus']

##remove bottom feature (feature importances = 0):  'deferred_income', 'long_term_incentive', 
#'total_payments', 'fraction_from_poi', 'fraction_deferral_payments', 

##remove bottom features again:  'total_stock_value', 'restricted_stock',

## 3rd round of removing bottom features (feature importances = 0):  'bonus',  
#'salary', 'fraction_s_deferred_income',

## classifier tuning - step1  salary, shared_receipt_with_poi
#==============================================================================
# final list, R1 submission['poi',  'shared_receipt_with_poi', 'exercised_stock_options',
# 'fraction_to_poi'] 
# 
#==============================================================================
#test 1 - try engineered variables v. original - bonus and deferral payments all four variables (deferral payments, fraction, bonus, fraction)
#'deferral_payments', 'fraction_deferral_payments',  'bonus', 'fraction_s_bonus'
#test2 - remove low feature priority - total payments, long term incentive, fraction from poi
#'total_payments','long_term_incentive',
#'fraction_from_poi','shared_receipt_with_poi', 'exercised_stock_options',

### Load the dictionary containing the dataset
with open("../final_project/final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
data_dict.pop("TOTAL", 0 )
data_dict.pop('TRAVEL AGENCY IN THE PARK', 0)

### Task 3: Create new feature(s)
## create 5 ratios of msgs to POI to all msgs to, msgs from POI to all msgs from

def computeFraction( numerator, denominator ):
    """ given a number messages to/from POI (numerator) 
        and number of all messages to/from a person (denominator),
        return the fraction of messages to/from that person
        that are from/to a POI
   """

    fraction = 0.
    if numerator != 'NaN' and denominator != 'NaN':
        fraction = numerator / float(denominator)
    
    return fraction

submit_dict = {}

for name in data_dict:
    data_point = data_dict[name]
    
#email variables
    from_poi_to_this_person = data_point["from_poi_to_this_person"]
    to_messages = data_point["to_messages"]
    fraction_from_poi = computeFraction( from_poi_to_this_person, to_messages )
    data_point["fraction_from_poi"] = fraction_from_poi


    from_this_person_to_poi = data_point["from_this_person_to_poi"]
    from_messages = data_point["from_messages"]
    fraction_to_poi = computeFraction( from_this_person_to_poi, from_messages )
#    print fraction_to_poi
    data_point["fraction_to_poi"] = fraction_to_poi
    
#financial variables - total payments denominator
    deferral_payments = data_point["deferral_payments"]
    total_payments = data_point["total_payments"]
    fraction_deferral_payments = computeFraction( deferral_payments, total_payments )
    data_point["fraction_deferral_payments"] = fraction_deferral_payments


#financial variables - salary denominator
    deferred_income = data_point["deferred_income"]
    salary = data_point['salary']
    fraction_s_deferred_income = computeFraction( deferred_income, salary )
    data_point["fraction_s_deferred_income"] = fraction_s_deferred_income

    bonus = data_point["bonus"]
    fraction_s_bonus = computeFraction( bonus, salary )
    data_point["fraction_s_bonus"] = fraction_s_bonus

#    num = data_point["num"]
#    den = data_point["den"]
#    fraction_num = computeFraction( num, den )
#    data_point["fraction_num"] = fraction_num
    
    submit_dict[name]={"from_poi_to_this_person":fraction_from_poi,
                       "from_this_person_to_poi":fraction_to_poi, 
                       "fraction_deferral_payments": fraction_deferral_payments,
                       "fraction_s_deferred_income": fraction_s_deferred_income, 
                       "fraction_s_bonus": fraction_s_bonus}
                           
### Store to my_dataset for easy export below.
my_dataset = data_dict

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)
#print features#print features[0], len(features)


### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.

#  Select DT based on best accuracy, precision and recall
from sklearn.naive_bayes import GaussianNB
#clf = GaussianNB()

#>> try svm
from sklearn.svm import SVC
#clf = SVC()

from sklearn import tree
#clf = tree.DecisionTreeClassifier()

from sklearn.neighbors import KNeighborsClassifier
from sklearn.neighbors import RadiusNeighborsClassifier

#clf = KNeighborsClassifier()

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

#clf = tree.DecisionTreeClassifier( min_samples_split = 2, max_depth = 2, criterion = 'entropy')
clf = tree.DecisionTreeClassifier( min_samples_split = 30, max_depth = 6, criterion = 'entropy')
#==============================================================================
#alternate - higher accuracy but lower recall 
#param_grid = { 'criterion': ['gini', 'entropy'],
#          'min_samples_split': [2, 6, 8, 10, 15, 20, 30],
#           'max_depth': [2, 6, 8, 10, 15, 20, 30] }
# clf = GridSearchCV(tree.DecisionTreeClassifier(), param_grid, scoring = 'recall')
# 
#==============================================================================

# Example starting point. Try investigating other evaluation techniques!

from sklearn.cross_validation import train_test_split
features_train, features_test, labels_train, labels_test = \
train_test_split(features, labels, test_size=0.3, random_state=42)

clf = clf.fit(features_train, labels_train)
feature_priority = clf.feature_importances_
#pred = clf.predict(features_test)
acc_test = clf.score(features_test, labels_test)
acc_train = clf.score(features_train, labels_train)
for i in range(1, len(features_list)):
    print features_list[i]
    print feature_priority[i-1]

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)