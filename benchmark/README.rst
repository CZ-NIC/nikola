Benchmark
=========

This software is used to perform benchmarks on our firewall log collecting infrastructure.
It is quite simple and might be improved in the future.

Features:

- delayed start (starts at a selected time)
- offline (no central elements, no need to keep open sockets to other entities)
- reproducible benchmarks (the same data can be send to the server twice)

Requirements:

- python 2.7
- nikola (syslog_parser and jsonrpclib)


How to run
----------
There are 2 phases which are required to perfom the benchmarks.
Note that there is a Makefile which should be able to prepare a setup for a single client.


Batch generating phase
______________________
This phase should be performed on a signle place. All batches for all clients are generated in this step (in csv format). Then they should be manually distributed among the clients.

|
|   python generate_requests.py client-config.json
|

User can set up some parameters (e.g. number of clients) in the config file.
A several files (based on the client count) are generated afterwards:

- client-config_2016-02-29-10-50-00_0000.csv
- client-config_2016-02-29-10-50-00_0001.csv
- client-config_2016-02-29-10-50-00_0002.csv
- ...


Client phase
____________
This phase is performed on a couple of clients.
They read the csv file generated in the previous step and based on that the actual data which will be send to the server are generated (if it hasn't been generated yet).
It has a similar format as syslog files on the routers and can be processed by the nikola's parser.

- 0000_ac41-8e20-85b2-6924
- 0000_bc3e-03c4-d473-5f74
- ...

Then the clients will wait for the specified time (--start-time) and they will start to send the batches of data to the server.
Note that the each batch should be send to the server at start time + time_delta (column in the csv file).

|
|   python client.py -c client-config.json -r client-config_2016-02-29-10-50-00_0000.csv -s '2016-02-29_10:30:00'
|

Before you can perform such command, be sure to have some benchmark user(s) in the db with a correct serial and key and set in the json config file.

|
|   {
|       "serial": "0000000000000001",
|       "key": "0000000000000000000000000000000000000000000000000000000000000000"
|   }
|
