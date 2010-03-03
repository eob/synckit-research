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

test_batch_name values:
(Wiki Camera Ready)---for Wiki Flying Templates, Traditional
SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Wiki Camera Ready' AND (style = 'Flying Templates' OR style = 'Traditional')
;

(Blog Camera Ready 1)---for Blog Flying Templates, Traditional
SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Blog Camera Ready 1' AND (style = 'Flying Templates' OR style = 'Traditional')
;

(Blog/Wiki Synckit Camera Ready)---for Wiki and Blog Sync Kit
SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Blog/Wiki Synckit Camera Ready' AND style = 'Sync Kit'
;

Blog outliers attempt
SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Blog Sync Kit Camera Ready Outliers';

SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Blog Traditional Camera Ready Outliers 1';

\f ',' 
\a 
\o ../perf/camera_ready/output-clientside/wiki_tokyo_outliers.csv
SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Wiki Tokyo Camera Ready Outliers';
\o 
\q

\f ',' 
\a 
\o ../perf/camera_ready/output-clientside/wiki_synckit_outliers.csv
SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Wiki Sync Kit Camera Ready Outlier Last Time';
\o 
\q

\f ',' 
\a 
\o ../perf/camera_ready/output-clientside/blog_tokyo_outliers.csv
SELECT 'Test' AS test, 
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
WHERE test_batch_name = 'Blog Flying Templates Camera Ready Last One!';
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

