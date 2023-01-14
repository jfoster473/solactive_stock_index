import datetime as dt
import pandas as pd
import numpy as np

class IndexModel:
    def __init__(self) -> None:

        # Import prices data
        stock_prices = pd.read_csv("data_sources/stock_prices.csv")
        
        # Formate dates and set as the dataframe index
        stock_prices["Date"] = pd.to_datetime(stock_prices["Date"],format="%d/%m/%Y")
        stock_prices = stock_prices.set_index("Date")
        
        # Sort the data in case it is not in order
        stock_prices = stock_prices.sort_index()
        
        # Check for any missing business days
        day_list = pd.period_range(start=min(stock_prices.index), end = max(stock_prices.index), freq="D").to_timestamp()
        workday = day_list[[day_list.weekday[i] in [0,1,2,3,4] for i in range(len(day_list))]]
        if len(stock_prices.index)!=len(workday):
            raise ValueError('The index of stock prices does not match the number of workdays.')
        if all(stock_prices.index==workday)==False:
            raise ValueError('The index includes days that were not workdays.')
        
        # Set values as float in case they are not already
        stock_prices = stock_prices.astype("float")
        
        # Forward fill any null values (i.e., missing data on a weekday use the most recent prices)
        stock_prices = stock_prices.fillna(method="ffill")

        # Create month start and end maps
        month_list = pd.Series(stock_prices.index.month)
        month_list_previous = month_list.shift(-1).fillna(month_list)
        month_list_next = month_list.shift(1).fillna(month_list)
        
        # Select the last available day in the month
        month_change = month_list!=month_list_previous
        end_of_month = pd.Series(month_change.values,index=stock_prices.index.values)
        
        # Select prices as of month end
        rebalance_date = stock_prices[end_of_month].copy()
        
        # Check to make sure that no two prices are equal on a given rebalance date
        for i in range(len(rebalance_date)):
            if len(set(rebalance_date.iloc[i,:]))!=len(rebalance_date.iloc[i,:]):
                date_with_duplicate = pd.to_datetime(rebalance_date.index[i]).strftime("%d %b %Y")
                raise ValueError('There are duplicate prices on '+date_with_duplicate)
        
        # Select the top three securities for each rebalance date
        first_largest = rebalance_date.T.apply(lambda x: x.nlargest(1).idxmin())
        second_largest = rebalance_date.T.apply(lambda x: x.nlargest(2).idxmin())
        third_largest = rebalance_date.T.apply(lambda x: x.nlargest(3).idxmin())
        
        # Generate weights
        weights = pd.DataFrame(np.nan,columns=rebalance_date.columns,index=stock_prices.index)
        for i in rebalance_date.index:
            weights.loc[i,:]=0
            weights.loc[i,first_largest.loc[i]] = 0.5
            weights.loc[i,second_largest.loc[i]] = 0.25
            weights.loc[i,third_largest.loc[i]] = 0.25
        
        # Forward fill weights over the month
        weights = weights.fillna(method="ffill")
        
        # Create variables
        self.weights = weights
        self.stock_prices = stock_prices
        
        pass

    def calc_index_level(self, start_date: dt.date, end_date: dt.date) -> None:

        # Calculate daily returns for the stock prices
        returns = self.stock_prices/self.stock_prices.shift(1)
        
        # Calculate weighted returns
        weighted_returns = returns*self.weights.shift(2)
        weighted_returns = weighted_returns.sum(axis=1)
        weighted_returns = weighted_returns[start_date:end_date]
        
        # Create index
        stock_index = pd.DataFrame(100,index=weighted_returns.index,columns=["index"])
        for i in weighted_returns.index[1:]:
            stock_index.loc[i] = weighted_returns.loc[i]*stock_index.shift(1).loc[i]
        
        # 
        self.stock_index = stock_index
        
        pass

    def export_values(self, file_name: str) -> None:
        
        self.stock_index.to_csv(file_name)
        
        pass
