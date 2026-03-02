Objective

The objective of Milestone 1 is to design and implement a structured data processing pipeline that cleans, validates, and transforms raw global weather data into a reliable and analysis-ready dataset.

This milestone establishes the backend foundation for further analytical and dashboard development.

:Technologies Used
->Python
->Pandas
->NumPy
->Git & GitHub
->VS Code

Step 1: Data Preparation
->Loaded raw dataset
->Removed duplicate records
->Handled missing values
->Converted date column to proper datetime format
->Saved cleaned dataset to:data/processed/weather_clean.csv

Step 2: Data Validation
->The validation module checks:
->Total missing values
->Duplicate rows
->Invalid humidity values
->Invalid temperature values
->Invalid wind speed values
->This ensures data integrity before analysis.

Step 3: Feature Engineering
->Created new analytical datasets:
->Monthly average temperature per country
->Yearly average temperature per country

Saved as:
->monthly_avg_temperature.csv
->yearly_avg_temperature.csv

Step 4: Automated Climate Summary
Generated automatic insights including:

->Hottest Country
-> Coldest Country
-> Worst Air Quality Country
-> Highest Humidity Country
This module provides quick high-level climate understanding.