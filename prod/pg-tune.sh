#!/bin/sh
set -e

# Perform all actions as user 'postgres'
export PGUSER="$POSTGRES_USER"

# DB Version: 10
# OS Type: linux
# DB Type: web
# Total Memory (RAM): 20 GB
# CPUs num: 8
# Connections num: 100
# Data Storage: hdd

psql --dbname="$POSTGRES_DB" <<EOSQL
ALTER SYSTEM SET
 max_connections = '500';
ALTER SYSTEM SET
 shared_buffers = '2560MB';
ALTER SYSTEM SET
 effective_cache_size = '7680MB';
ALTER SYSTEM SET
 maintenance_work_mem = '640MB';
ALTER SYSTEM SET
 checkpoint_completion_target = '0.7';
ALTER SYSTEM SET
 wal_buffers = '16MB';
ALTER SYSTEM SET
 default_statistics_target = '100';
ALTER SYSTEM SET
 random_page_cost = '4';
ALTER SYSTEM SET
 effective_io_concurrency = '2';
ALTER SYSTEM SET
 work_mem = '6553kB';
ALTER SYSTEM SET
 min_wal_size = '1GB';
ALTER SYSTEM SET
 max_wal_size = '2GB';
ALTER SYSTEM SET
 max_worker_processes = '8';
ALTER SYSTEM SET
 max_parallel_workers_per_gather = '4';
ALTER SYSTEM SET
 max_parallel_workers = '8';
EOSQL

