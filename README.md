# MOLLER Experiment Digitizer Python Scripts and library

## Command Line Usage

- To discover a MOLLER Digitizer on the local subnet

`moller-ctl discover`

Ex:
```
> moller-ctl discover

Beacon received from 192.168.1.229 [Vendor: 'TRIUMF', Product: 'MOLLER 16-Channel Integrating ADC', deviceID: 00:04:A3:0B:00:07:DC:6F, logicalID: 18446744073709551615, hwRev: 0, fwRev: 0.9.1, Uptime: 26494]
```

### To get the status of a MOLLER Digitizer

`moller-ctl <ip> status`

### To manually align ADCs and get alignment plot

`moller-ctl <ip> align`

### To plot out all or one ADC channel in real-time

`moller-ctl <ip> plot [all]` or `moller-ctl [ip] plot [1-16]`

### To read an individual register

`moller-ctl <ip> read [address]`

### To write an individual register

`moller-ctl <ip> write [address] [data]`

Response:  `<hex value> [decimal value]`


The full register set (excluding TINode) can be found here: [Register Set](REG_MOLLER.md)

Example Usage:

To get the current register set revision

```
> moller-ctl 192.168.1.229 read 0x40`

0x0000011F [287]
```