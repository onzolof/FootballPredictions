import matplotlib.pyplot as plt
import pickle
import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV
import seaborn as sns


# function to plot the top n most important features
def plot_variable_importance(model, X, n=10, inverse=False):
    imp = get_variable_importance(model, X).sort_values("importance", ascending=True)
    imp = imp.head(n) if inverse else imp.tail(n)  # Select the top n rows
    fig, ax = plt.subplots(figsize=(imp.shape[0] / 2, imp.shape[0] / 2))  # Adjusted size for fewer variables
    ax.barh(imp["feature"], imp["importance"], color="green")
    ax.set_xlabel('\nVariable Importance')
    ax.set_ylabel('Features\n')
    ax.set_title(f"{'Flop' if inverse else 'Top'} {str(n)} Variable Importance\n")
    plt.show()


# function to plot the top n most important numerical features, to exclude the dummy-variable-noise
def plot_numeric_variable_importance(model, X):
    variable_importances = get_variable_importance(model, X)
    numeric_features = variable_importances[~variable_importances['feature'].str.contains('_')].sort_values('importance', ascending=False)
    sns.barplot(x='importance', y='feature', data=numeric_features, palette='hls')
    plt.gca().set_xlabel('\nVariable Importance')
    plt.gca().set_ylabel('Features\n')
    plt.gca().set_title(f"Numeric Variable Importance\n")
    plt.show()


# create a dataframe out of the feature importances
def get_variable_importance(model, X):
    return pd.DataFrame({"feature": X.columns, "importance": model.feature_importances_})

# create dummy variables for a given column, while bundling non-frequent values in an other-category
def process_categorical(df, column, min_count=10):
    value_counts = df[column].value_counts()
    frequent_categories = value_counts[value_counts >= min_count].index  # count the frequency per nominal value
    df.loc[:, 'processed_' + column] = df[column].apply(lambda x: x if x in frequent_categories else 'other')  # assign a category according to the frequency
    dummies = pd.get_dummies(df['processed_' + column], prefix=column)  # create dummys on the created categories
    df = df.drop(column, axis=1)
    df = df.drop('processed_' + column, axis=1)  # drop unnecessary column
    df = pd.concat([df, dummies], axis=1)  # append dummies to dataframe
    return df


# build the rmse scorer
def get_rmse_scorer():
    return make_scorer(mean_squared_error, squared=False, greater_is_better=False)


# execute the RancomSearchCV on a given model and select the best estimator
def optimise_model(model, params, X, y, scoring=get_rmse_scorer(), n_iter=100):
    search = RandomizedSearchCV(estimator=model, param_distributions=params, n_iter=n_iter, random_state=1, n_jobs=-1,
                                cv=5, verbose=2, scoring=scoring)
    search.fit(X, y)
    cv_results = pd.DataFrame(search.cv_results_)[['params', 'mean_test_score', 'rank_test_score']] # summarize the result in a dataframe
    cv_results = cv_results.sort_values('rank_test_score')
    return search.best_estimator_, cv_results

# execute recursive feature elimination on a given estimator
def recursive_feature_elimination(estimator, X, y):
    selector = RFE(estimator=estimator, step=1)
    selector.fit(X, y)
    df_features = pd.DataFrame(columns=['feature', 'support', 'ranking'])  # create a dataframe with all features and their rank
    for i in range(len(X.columns)):
        row = {'feature': X.columns[i], 'support': selector.support_[i], 'ranking': selector.ranking_[i]}
        df_features = df_features.append(row, ignore_index=True)
    return df_features.sort_values(by='ranking')


def save_model(model, model_name):
    # serialize model for a given name
    with open('../models/' + model_name + '.pkl', 'wb') as f:
        pickle.dump(model, f)


def load_model(model_name):
    # deserialize model for a given name
    with open('../models/' + model_name + '.pkl', 'rb') as f:
        return pickle.load(f)


def print_performance_measures(X, y, y_pred, file=None):
    # measure performance of the regressor and print it
    r2 = r2_score(y, y_pred)
    adj_r2 = 1-(1-r2)*(len(X.index)-1)/(len(X.index)-len(X.columns)-1)
    rmse = mean_squared_error(y, y_pred, squared=False)
    print(f"RMSE:\t\t{round(rmse, 4)}\nR^2:\t\t{round(r2, 4)}\nAdj. R^2:\t{round(adj_r2, 4)}")
    if file is not None:
        # save the performance to a file as well if a filepath is given as input
        save_performance(file, X, r2, adj_r2, rmse)


def save_performance(file, X, r2, adj_r2, rmse):
    # save the performance measures together with the used features in a file to compare the feature selection with its performance
    features = set()

    for col in X.columns: # get all variables by ignoring the many duplicated dummies
        if '_' in col:
            features.add(col.split('_')[0])
        else:
            features.add(col)

    with open(file, "a") as f:  # write to the file
        f.write(f"{rmse},{r2},{adj_r2},{features}\n")