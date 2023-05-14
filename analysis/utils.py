import matplotlib.pyplot as plt
import pickle
import pandas as pd
from sklearn.feature_selection import RFE
from sklearn.metrics import make_scorer, mean_squared_error, r2_score
from sklearn.model_selection import RandomizedSearchCV


def plot_variable_importance(model, X, n=10, inverse=False):
    imp = pd.DataFrame({"imp": model.feature_importances_, "names": X.columns}).sort_values("imp", ascending=True)
    imp = imp.head(n) if inverse else imp.tail(n)  # Select the top n rows
    fig, ax = plt.subplots(figsize=(imp.shape[0] / 2, imp.shape[0] / 2))  # Adjusted size for fewer variables
    ax.barh(imp["names"], imp["imp"], color="green")
    ax.set_xlabel('\nVariable Importance')
    ax.set_ylabel('Features\n')
    ax.set_title(f"{'Flop' if inverse else 'Top'} {str(n)} Variable Importance")
    plt.show()


def process_categorical(df, column, min_count=10):
    value_counts = df[column].value_counts()
    frequent_categories = value_counts[value_counts >= min_count].index
    df.loc[:, 'processed_' + column] = df[column].apply(lambda x: x if x in frequent_categories else 'other')
    dummies = pd.get_dummies(df['processed_' + column], prefix=column)
    df = df.drop(column, axis=1)
    df = df.drop('processed_' + column, axis=1)
    df = pd.concat([df, dummies], axis=1)
    return df


def get_rmse_scorer():
    return make_scorer(mean_squared_error, squared=False, greater_is_better=False)


def optimise_model(model, params, X, y, scoring=get_rmse_scorer(), n_iter=100):
    search = RandomizedSearchCV(estimator=model, param_distributions=params, n_iter=n_iter, random_state=1, n_jobs=-1,
                                cv=5, verbose=2, scoring=scoring)
    search.fit(X, y)
    cv_results = pd.DataFrame(search.cv_results_)[['params', 'mean_test_score', 'rank_test_score']]
    cv_results = cv_results.sort_values('rank_test_score')
    return search.best_estimator_, cv_results


def recursive_feature_elimination(estimator, X, y):
    selector = RFE(estimator=estimator, step=1)
    selector.fit(X, y)
    df_features = pd.DataFrame(columns=['feature', 'support', 'ranking'])
    for i in range(len(X.columns)):
        row = {'feature': X.columns[i], 'support': selector.support_[i], 'ranking': selector.ranking_[i]}
        df_features = df_features.append(row, ignore_index=True)
    return df_features.sort_values(by='ranking')


def save_model(model, model_name):
    with open('../models/' + model_name + '.pkl', 'wb') as f:
        pickle.dump(model, f)


def load_model(model_name):
    with open('../models/' + model_name + '.pkl', 'rb') as f:
        return pickle.load(f)


def print_performance_measures(y, y_pred):
    print(f"RMSE:\t{round(mean_squared_error(y, y_pred, squared=False), 4)}\nR^2:\t{round(r2_score(y, y_pred), 4)}")
