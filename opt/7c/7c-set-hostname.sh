#!/bin/bash

hostname `cat /sys/firmware/devicetree/base/serial-number | tail -c +9`
