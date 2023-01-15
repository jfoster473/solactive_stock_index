# Assessment Index Modelling

# Index overview

This code produces a total return index of 3 stocks, based on the relative size of the companies. The data source for the prices is stock_prices.csv and the calculations are in index.py.

# Index Rules

- The index is a total return index.
- The index universe consists of all stocks from "Stock_A" to including "Stock_J".
- Every first business day of a month the index selects from the universe the top three stocks based on their market capitalization, 
  based on the close of business values as of the last business day of the immediately preceding month.
- The selected stock with the highest market capitalization gets assigned a 50% weight, while the second and third each 
  get assigned 25%.
- The selection becomes effective close of business on the first business date of each month.
- The index starts with a level of 100.
- The index start date is January 1st 2020.
- The index business days are Monday to Friday.
- There are no additional holidays.

# Additional information

- The index is a stock index made up of imaginary stocks. 
- There are no further corporate actions. 
- The index doesn't resemble any real existing index.
- All provided prices are total return. 
- All companies have the same amount of shares outstanding.
