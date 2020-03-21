# COVID19_tracker

This script fetches the daily data of confiremed cases of COVID-19 in different country/regions, as well as recovered and mortality cases. 
## Data source
Data is fetched from [here]
(https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases)

## Depndencies
It uses the usual Python 3 libraries. You might need to install 'wget' and 'click'. The former is used to dowload the data, and the latetr to handle command prompt parameters. 

## Usage
In a bash command prompt or anadonca bash in windows, you can use it as below:

```bash
python script_COVID19_tracker.py --x_ax 'cumsum' --y_ax 'linear'
python script_COVID19_tracker.py --x_ax 'diff' --y_ax 'linear'
python script_COVID19_tracker.py --x_ax 'cumsum' --y_ax 'semilogy'
python script_COVID19_tracker.py --x_ax 'diff' --y_ax 'semilogy'
```
