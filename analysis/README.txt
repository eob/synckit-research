Client-Side Stack Queries
=========================

1) Issue the following query. Note that you'll want to change the output file name, and also the WHERE filter.

\f ',' 
\a 
\o monday_night.csv 
SELECT test_name AS test, 
       page_name AS page, 
       style as strategy, 
       visit_number as visitNumber,
       total_time_to_render as ttr,
       data_fetch as dataFetch,
       data_bulkload as dataBulkload,
       template_parse as templateParse,
       latency as latency,
       bandwidth as bandwidth,
       date as date
FROM
       clientlogger_logentry
WHERE
       test_name = 'Feb 2'
;
\o 
\q

2) SCP the file into the analysis directory

3) *** REMOVE THE LAST LINE OF THE CSV FILE -- this is a summary printed by the DB

4) Modify client_time_breakdown.r to have the proper CSV file reference at the top, the proper test name, and page name that you'd like to produce a graph for.

5) Run client_time_breakdown.r


-> Output is in client_time_breakdown.pdf


Throughput 
=========================

1) Run the binary search thing to ultimately get the summary CSVs. Copy
all their lines into the same file. See apache.csv -- this is what it should look like.

2) Run throughput.r

