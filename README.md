# Fullstack Data Challenge

## Installation

1. (Recommended step) Create virtual environment \n
    **_$ python -m venv .venv_**
2.  Activate virtual environment \n
    _$ source .venv/bin/activate_
3. Install requirements \n
    _$ pip3 install -r requirements.txt_
4. Run app \n
    _$ streamlit run 0\_Home.py_


## Project Description
Four pages:
- Home
- Explore
- Compare
- Oracle (The best one)

### Home
Basic overview that lets the user to understand shape of the data.
Offers basic calculations such as _mean value_ and _non-zero points_.

### Explore
Stats and graphs visualizing full data frame.
Lets the user inspect objects(fruits) next to eachother.
Shows correlations. Which fruits are either sold/consumed on same day, opens up for discussion and perhaps point out patterns.

### Compare
Side by side comparison between two objects.

### Oracle
Future prediction of consumtion.
Uses Prophet (ML time series framwork), by Meta.
Shows forecast with the ability to compare to "reality" to ponder over "realistic or not".
Day by day forcasts, good for planning.
Zero value prediciton. Since prophet dont like non-continuos 

## Tips below

- **For planning:** Use **Realistic** forecast mean
- **For risk assessment:** Use **Pessimistic** forecast mean
- **For optimization:** Use **Optimistic** to see potential
- **For accuracy:** The realistic scenario should align with your domain knowledge about product availability


## Highlights
- Streamlit is smooth and incredibly simple :p
- In data control 
- Plain text input cant insert code (minor highlight)
- No below 0 predictions, values decrease exponatially 
- Modularity -> Scalable + Reusable code

## Problems & Improvements
High zero percentage makes for bad forecasts, ex. grape.
Restricted timespan of observations.
No ability to add more data to DB. Would be good for future improvements.
Prophet is not great for non-continuous data. The On/Off(zero or non-zero) behaviour is difficult to interpret.
Streamlit Cloud would be next step.


