# Measurements of Feature Importance (First) 机器学习衡量特征重要性的方法 (一)：Weight, Gain, Cover, Mean Decrease Impurity and Permutation Value.

**Analyzing and interpreting feature importance should be very careful and comprehensive, or it would give misleading outcomes and sometimes totally opposite/contradictory results when using different evaluating index.**

<font color=#E74C3C size=4> This object of this blog is to summarize the popular and handy tools and concepts to analyze feature importance. In addtion, collect useful and informative links for review </font>

For example, when I was doing my thesis, I used the xgboost Python API to plot feature importance. And I got a confusing results like this:

![Figure4_2&4_3](/Users/kadima/Library/Application Support/typora-user-images/image-20200529113027798.png)

![Figure4.4](/Users/kadima/Library/Application Support/typora-user-images/image-20200529113054399.png)

Figures 4.2, 4.3 and 4.4 illustrate the outcomes of feature importance by using three different methods to compute. The first method is called “weight”, whose value means the number of times a feature used to split the data across all trees. The **“weight”** method is the default choice of feature importance. The second method **“cover”** indicates the number of times a feature used to split the data across all trees weighted by the number of training data points that go through those splits. The method used in Figure 4.4 is called **“Gain”**, which represents the average training loss reduction gained when using a feature for splitting.

As we can see, three plots exhibit extremely different outcomes of feature importance. The “weight” method suggests that variable ***age*** and ***temp*** are very important for this model, while the “cover” method indicates that two variables -- ***shivering*** and ***diarrhea*** are most equivalently paramount. On the contrary, the “gain” method demonstrates that ***diarrhea*** and ***shivering*** variables are least important. 

Here is another example

<center>    <img style="border-radius: 0.3125em;    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);"     src="https://miro.medium.com/max/2000/1*qdvN5WQhN33hO4wWG7RtDw.png">    <br>    <div style="color:orange; border-bottom: 1px solid #d9d9d9;    display: inline-block;    color: #999;    padding: 2px;">The figure shows the significant difference between importance values, given to same features, by different importance metrics.</div> </center>

Therefore, extra feature importance measures are necessary to solve these contradictory outcomes.

----

## XGBoost inherent feature importance: Weight, Gain, Cover

The explanation of the different measurements are as follows from [official website](https://xgboost.readthedocs.io/en/latest/python/python_api.html#xgboost.plot_importance):

>**importance_type** ([*str*](https://docs.python.org/3.6/library/stdtypes.html#str)*,* *default "weight"*) –
>
>How the importance is calculated: either “weight”, “gain”, or “cover”
>
>- ”weight” is the number of times a feature appears in a tree
>- ”gain” is the average gain of splits which use the feature
>- ”cover” is the average coverage of splits which use the feature where coverage is defined as the number of samples affected by the split

Besies, the meanings of those choices are also explained at <font color=#C0392B>xgboost. Booster</font> object parameters get_score

> <font color= #C0392B >get_score</font>(*fmap**=**''*, *importance_type**=**'weight'*)
>
> Get feature importance of each feature. Importance type can be defined as:
>
> - ‘weight’: the number of times a feature is used to split the data across all trees.
> - ‘gain’: the average gain across all splits the feature is used in.
> - ‘cover’: the average coverage across all splits the feature is used in.
> - ‘total_gain’: the total gain across all splits the feature is used in.
> - ‘total_cover’: the total coverage across all splits the feature is used in.

In addition, I also recommend [this site](https://datascience.stackexchange.com/questions/12318/how-to-interpret-the-output-of-xgboost-importance) to see the more detailed explanation by [Sandeep S. Sandhu](https://datascience.stackexchange.com/users/18540/sandeep-s-sandhu):

> 1. The ***Gain\*** implies the relative contribution of the corresponding feature to the model calculated by taking each feature's contribution for each tree in the model. A higher value of this metric when compared to another feature implies it is more important for generating a prediction.
> 2. The ***Cover\*** metric means the relative number of observations related to this feature. For example, if you have 100 observations, 4 features and 3 trees, and suppose feature1 is used to decide the leaf node for 10, 5, and 2 observations in tree1, tree2 and tree3 respectively; then the metric will count cover for this feature as 10+5+2 = 17 observations. This will be calculated for all the 4 features and the cover will be 17 expressed as a percentage for all features' cover metrics.
> 3. The ***Frequency\*** (/'Frequence') is the percentage representing the relative number of times a particular feature occurs in the trees of the model. In the above example, if feature1 occurred in 2 splits, 1 split and 3 splits in each of tree1, tree2 and tree3; then the weightage for feature1 will be 2+1+3 = 6. The frequency for feature1 is calculated as its percentage weight over weights of all features.

----

### Why is it important to understand your feature importance results?

Let me slightly modify the explanation of [this blog](https://towardsdatascience.com/be-careful-when-interpreting-your-features-importance-in-xgboost-6e16132588e7)

Suppose that you have a binary feature, say gender, which is highly correlated with your target variable (it could be regression task like salary, height, or classification scenario such as occupation). Furthermore, you observed that the inclusion/ removal of this feature form your training set highly affects the final results. If you investigate the importance given to such feature by different metrics, you might see some **contradictions**:

Most likely, the variable gender has much smaller cardinality (often only two: male/female) compared to other predictors in your data. So this binary feature can be used at most once in each tree (if you do not understand this, then try to imagine that if the first split is gender, say left is Female and right is Male, then it is impossible to get another gender as splitter below it), while, let say, age (with a higher cardinality) might appear much more often on different levels of the trees. Therefore, such binary feature will get a very low importance based on the frequency/weight metric, but a very high importance based on both the gain, and coverage metrics!

*For how to deal with the high cardinality feature, [this discussion](https://www.kaggle.com/c/ga-customer-revenue-prediction/discussion/66260) form kaggle  and [this blog](https://towardsdatascience.com/getting-deeper-into-categorical-encodings-for-machine-learning-2312acd347c8) may help. For me, I tried many easy encoding methods, such as hash, bit, etc, their behaviour are usually good. Now there is an excellent tree-based algorithm to deal with those categorical feature, whose name is CatBoost. I may well discuss this algorithm in my future blog*

>A comparison between feature importance calculation in *scikit-learn* Random Forest (or GradientBoosting) and XGBoost is provided in [[1](https://forums.fast.ai/t/feature-importance-of-random-forest-vs-xgboost/17561)]. Looking into the documentation of *scikit-lean* ensembles, the weight/frequency feature importance is not implemented. This might indicate that this type of feature importance is less indicative of the predictive contribution of a feature for the whole model.
>
>So, before using the results coming out from the default features importance function, which is the weight/frequency, take few minutes to think about it, and make sure it makes sense. If it doesn’t, maybe you should consider exploring other available metrics.

To learn something on Decision Tree CART, I recommend [this blog in English](https://sefiks.com/2018/08/27/a-step-by-step-cart-decision-tree-example/) ,  [this blog in Chinese](https://zhuanlan.zhihu.com/p/32003259) and [blog in Chinese](XGBoost算法梳理 - End小fa的文章 - 知乎 https://zhuanlan.zhihu.com/p/58292935)

## Mean Decrease Impurity (Tree-based)

This is the most basic but popular way of explaining a tree-based model and its ensembles. A Sci-Kit Learn make it available and easy to use in tree-based models. 

> The mean decrease in impurity importance of a feature is computed by measuring how effective the feature is at reducing uncertainty (classifiers) or variance (regressors) when creating decision trees within any ensemble Decision Tree method(Random Forest, Gradient Boosting, etc.).
>
> The **advantages** of the technique are:
>
> - A fast and easy way of getting feature importance
> - Readily available in Sci-kit Learn and Decision Tree implementation in R
> - It is pretty intuitive to explain to a layman
>
> from [this website](https://www.kdnuggets.com/2019/12/interpretability-black-box-part-2.html)

[Gini Impurity](https://en.wikipedia.org/wiki/Decision_tree_learning#Gini_impurity) measures how often a randomly chosen record from the data set used to train the model will be incorrectly labeled if it was randomly labeled according to the distribution of labels in the subset (e.g., if half of the records in a group are "A" and the other half of the records are "B", a record randomly labeled based on the composition of that group has a 50% chance of being labeled incorrectly). Gini Impurity reaches zero when all records in a group fall into a single category (i.e., if there is only one possible label in a group, a record will be given that label 100% of the time). This measure is essentially the probability of a new record being incorrectly classified at a given node in a Decision Tree, based on the training data.  

To compute Gini impurity for a set of items with $J$ classes, suppose $i \in \{1,2,...,J\}$, and let $p_{i}$ be the fraction of items labeled with class $i$ in the set.

$I_{G}(p) = \sum_{i=0}^J p_{i} \sum_{k\neq i} p_{k} = \sum_{i=1}^J p_i (1-p_i) = 1 - \sum_{i=1}^J p_i ^2$ 

**Mean Decrease in Gini** a.k.a **Gini Importance** is the average (mean) of a variable’s total decrease in node impurity, weighted by the proportion of samples reaching that node in each individual decision tree in the random forest. This is effectively a measure of how important a variable is for estimating the value of the target variable across all of the trees that make up the forest. A higher Mean Decrease in Gini indicates higher variable importance. Variables are sorted and displayed in the Variable Importance Plot created for the Random Forest by this measure. The most important variables to the model will be highest in the plot and have the largest Mean Decrease in Gini Values, conversely, the least important variable will be lowest in the plot, and have the smallest Mean Decrease in Gini values. 

> *In scikit-learn, we implement the importance as described in [1] (often cited, but unfortunately rarely read…). It is sometimes called “gini importance” or “mean decrease impurity” and is defined as the* **total decrease in node impurity** *(weighted by the probability of reaching that node (which is approximated by the proportion of samples reaching that node)) averaged over all trees of the ensemble.*

The scikit-learn points out under the [DecisionTreeClassifier](https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html) that:

> The importance of a feature is computed as the (normalized) total reduction of the criterion brought by that feature. It is also known as the Gini importance. 
>
> Warning: impurity-based feature importances can be misleading for high cardinality features (many unique values). See [`sklearn.inspection.permutation_importance`](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html#sklearn.inspection.permutation_importance) as an alternative.

> In 2007, Strobl *et al* [1] also pointed out in [Bias in random forest variable importance measures: Illustrations, sources and a solution](https://link.springer.com/article/10.1186%2F1471-2105-8-25) that “*the variable importance measures of Breiman’s original Random Forest method … are not reliable in situations where potential predictor variables vary in their scale of measurement or their number of categories*.”

To sum up:

The **advantages** of the technique are:

- A fast and easy way of getting feature importance
- Readily available in Sci-kit Learn and Decision Tree implementation in R
- It is pretty intuitive to explain to a layman

The **disadvantages of the techniques**:

- Easy to be affected by high cardinality feature. But not always be fooled. You can refer to [this answer](c4.5为什么使用信息增益比来选择特征？ - 夕小瑶的回答 - 知乎 https://www.zhihu.com/question/22928442/answer/440836807) from 知乎Zhihu (I think the example is very excellent and understandable)

For impementation, please refer to this [simple example](https://www.kdnuggets.com/2019/12/interpretability-black-box-part-2.html)

## Permutation Value (Tree-based)

![An example of permuation value](https://miro.medium.com/max/1128/1*PFNS_2AhU3woIZ5l9d3xKA.png)

<center>Permutation value can have a reliable range on its value</center>

![Another example by eli5 library](https://miro.medium.com/max/980/1*8uCcJc3BZrJ1QdIGXPpXDQ.png)

<center> A computed permutation value by using the eli5 library from a tutorial</center>

[this tutorial](https://medium.com/towards-artificial-intelligence/how-to-use-scikit-learn-eli5-library-to-compute-permutation-importance-9af131ece387)

**Permutation feature importance** is quite simple: The permutation feature importance is defined to be the decrease in a model score when a single feature value is randomly shuffled. This technique measures the difference in performance if you permute or shuffle a feature vector. The key idea is that a feature is important if the model performance drops if that feature is shuffled.

> **ALGORITHM**
>
> 1. Calculate a baseline score using the metric, trained model, the feature matrix and the target vector
> 2. For each feature in the feature matrix, make a copy of the feature matrix.
> 3. Shuffle the feature column, pass it through the trained model to get a prediction and use the metric to calculate the performance.
> 4. Importance = Baseline – CurrentScore
> 5. Repeat for N times for statistical stability and take an average importance across trials <-- That's why the permutation value can offer a confidence interval

For more detailed information, please visit the [scikitLearn Explanation Document](https://scikit-learn.org/stable/modules/permutation_importance.html), and [scikitLearn permutation_importance object](https://scikit-learn.org/stable/modules/generated/sklearn.inspection.permutation_importance.html#sklearn.inspection.permutation_importance) and the[ELI5 explanation](https://eli5.readthedocs.io/en/latest/autodocs/permutation_importance.html)  as well as [ELI5 implementation](https://eli5.readthedocs.io/en/latest/autodocs/sklearn.html#module-eli5.sklearn.permutation_importance) (ELI5 is a Python package which helps to debug machine learning classifiers and explain their predictions. It provides support for the main-stream machine learning frameworks and packages such as scikit-learn, XGBoost, LightGBM, CatBoost, Keras, etc.  you can easily install it by `pip install eli5`

[Relation to impurity-based importance in trees](https://scikit-learn.org/stable/modules/permutation_importance.html#relation-to-impurity-based-importance-in-trees)

### Summary:

**Advantages** of Permutation Value:

1. Permutation-based feature importance can avoid the issue from mean decrease in impurity (MDI) that giving high importance to features that may not be predictive on unseen data when the model is overfitting. Because the permutation importance can be computed on unseen data. (it mess up a specific column, so the value of that column is not important anymore when calculating feature importance of that column)
2. Because this algorithm needs to compute the feature importance in several repeats. It can report a range of feature importance like 0.204 +/- 0.050 instead of a simple value.
3. The computation of feature importance on different columns can be parallelized.
4. Permutation importances can be computed either on the training set or on a held-out testing or validation set. Using a held-out set makes it possible to highlight which features contribute the most to the generalization power of the inspected model.

**Disadvantages** of Permutation Value:

1. It is not stable when comparing feature importance across models. Before using it to check feature importance, we need to make sure that the model has relatively strong predictive power.

>Warning from [sklearn](https://scikit-learn.org/stable/modules/permutation_importance.html)
>
> Features that are deemed of **low importance for a bad model** (low cross-validation score) could be **very important for a good model**. Therefore it is always important to evaluate the predictive power of a model using a held-out set (or better with cross-validation) prior to computing importances. Permutation importance does not reflect to the intrinsic predictive value of a feature by itself but **how important this feature is for a particular model**.

2. High computation cost. Getting a reliable and stable feature importance value of a column needs to go over several runs. Therefore, if data use to compute is large or there are many columns, it could be slow to getting the outcome.

3. Features that are important on the training set but not on the held-out set might cause the model to overfit.

4. Misleading values on strongly correlated features: 

   >
   >
   >When two features are correlated and one of the features is permuted, the model will still have access to the feature through its correlated feature. This will result in a lower importance value for both features, where they might actually be important.
   >
   >One way to handle this is to cluster features that are correlated and only keep one feature from each cluster. This strategy is explored in the following example: [Permutation Importance with Multicollinear or Correlated Features](https://scikit-learn.org/stable/auto_examples/inspection/plot_permutation_importance_multicollinear.html#sphx-glr-auto-examples-inspection-plot-permutation-importance-multicollinear-py). (One way to handle multicollinear features is by performing hierarchical clustering on the Spearman rank-order correlations, picking a threshold, and keeping a single feature from each cluster.)



The next chapter may discuss the SHAP Value