#!/bin/bash

if [ $EUID != 0 ]; then
    echo "This script must be run as root, use sudo $0 instead" 1>&2
    exit 1
fi

set -xe

psql -v ON_ERROR_STOP=1 --username heweidong <<-EOSQL
    drop database if exists test_backend;
    drop user if exists test;
    create user test with password 'Bl666666' login createdb;
    create database test_backend owner test;
EOSQL

echo "Creating database Done"