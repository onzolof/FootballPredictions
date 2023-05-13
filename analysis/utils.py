import matplotlib.pyplot as plt
import pandas as pd


def plot_variable_importance(model, X, n=10):
    imp = pd.DataFrame({"imp": model.feature_importances_, "names": X.columns})
    imp = imp.sort_values("imp", ascending=True).tail(n)  # Select the top n rows
    fig, ax = plt.subplots(figsize=(imp.shape[0] / 2, imp.shape[0] / 2))  # Adjusted size for fewer variables
    ax.barh(imp["names"], imp["imp"], color="green")
    ax.set_xlabel('\nVariable Importance')
    ax.set_ylabel('Features\n')
    ax.set_title('Top ' + str(n) + ' Variable Importance Plot\n')
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