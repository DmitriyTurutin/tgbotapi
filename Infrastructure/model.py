from Infrastructure.Persistence.Repository import Repository
import pickle
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import os
import logging


class Model:
    repository = Repository()

    email = ""
    url = ""
    def __init__(self, email, url) -> None:
        self.email = email
        self.url = url

    def generate_model(self):
        self.sales_data = self.repository.get_all(self.email, self.url)
        user = self.repository.get_user(self.email, self.url)
        id = user[0]

        # Create a DataFrame from the query results
        self.df = pd.DataFrame(self.sales_data, columns=[
                               'title', 'price', 'amount', 'payment_method', 'client', 'time_added'])
        self.df['week_day'] = self.df['time_added'].dt.weekday
        self.df['date'] = self.df['time_added'].dt.date
        self.df['month'] = self.df['time_added'].dt.month

        # The following lines should be added after 'df['date'] = df['time_added'].dt.date'
        self.df = self.df.groupby(['date', 'week_day', 'month']).agg(
            {'price': 'sum', 'client': 'nunique'}).reset_index()
        self.df.rename(columns={'price': 'daily_income',
                       'client': 'unique_visitors'}, inplace=True)
        # select features and target
        X = self.df[['week_day', 'month', 'unique_visitors']]
        y = self.df['daily_income']

        # split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42)

        # define the parameter grid
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 4, 5]
        }

        # create the model
        model = GradientBoostingRegressor()

        # perform grid search
        grid_search = GridSearchCV(
            model, param_grid, cv=5, return_train_score=True)
        grid_search.fit(X_train, y_train)

        # evaluate the model on the test data
        score = grid_search.score(X_test, y_test)
        logging.info("Model for provided data trained")
        logging.info("Test score: %s", score)

        # save the model to disk
        filename = f'./Storage/gradient_boosting_regressor_model_user_{id}.pkl'
        pickle.dump(grid_search, open(filename, 'wb'))
        if os.path.exists(filename):
            print("Model saved successfully")
        else:
            print("Model not saved, check the path")

        # make a prediction for the next day
        # next_day_features = [[3,4,10]] #6 is saturday, 1 is January, 100 is number of unique visitors
        # next_day_income = grid_search.predict(next_day_features)
        # print("Predicted income for the next day: ", next_day_income)
