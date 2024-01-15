#!/bin/bash

rpcbind -w
rpc.mountd -N 2 -V 3 -p 4004
rpc.nfsd -N 4 -V 4 -p 4005 8
