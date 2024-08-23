# For Shaw Singapore Malls ----> GTO Integration with Loyverse POS
Objective:
Integrate Loyverse POS with Shaw Singapore Malls' GTO system by sending hourly sales data.

**Current Implementation:**

Sales Data Accuracy:
The daily total sales figures from Loyverse, including refunds, are accurate.

Timing Issue:
There is currently a discrepancy in the timing of the reports being sent.

**Solution:**

Crontab Scheduling:
Use crontab on a Linux system to schedule the execution of a Python script that sends the hourly GTO data from Loyverse POS to Shaw.
Future Enhancements:

Timing Correction:
In the next version, the timing issue will be resolved to ensure accurate hourly reporting.

Streamlit Portal:
A Streamlit-based portal will be developed to facilitate the automatic upload of any missing sales reports.
