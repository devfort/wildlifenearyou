#!/bin/bash

if [ -f $1 ]; then
    ln -s $1 $2;
elif [ -f $2 ]; then
    ln -s $2 $1;
fi
