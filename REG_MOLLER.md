# MOLLER Register Set

|||
| --- | --- |
| **Description** | Moller experiment register map |
| **Default base address** | `0x80000000` |
| **Register width** | 32 bits |
| **Default address width** | 32 bits |
| **Register count** | 19 |
| **Range** | 276 bytes |
| **Revision** | 287 |

## Overview

| Offset | Name | Description | Type |
| --- | --- | --- | --- |
| `0x0` | adc_test_data | ADC Test Pattern Results | ARR[16] |
| `0x40` | revision | Moller register map revision | REG |
| `0x44` | stream_ctrl | ADC Data streaming mode control | REG |
| `0x48` | adc_ctrl |  | REG |
| `0x4C` | freq_td |  | REG |
| `0x50` | freq_osc |  | REG |
| `0x54` | freq_som0 |  | REG |
| `0x58` | freq_som1 |  | REG |
| `0x5C` | status |  | REG |
| `0x60` | adc_delay_in |  | ARR[16] |
| `0xA0` | adc_delay_out |  | ARR[16] |
| `0xE0` | adc_fifo_count |  | REG |
| `0xE4` | run_fifo_count |  | REG |
| `0xE8` | ti_fifo_count |  | REG |
| `0x100` | mac_addr_hi |  | REG |
| `0x104` | mac_addr_lo |  | REG |
| `0x108` | udp_dest_ip |  | REG |
| `0x10C` | udp_dst_port |  | REG |
| `0x110` | udp_src_port |  | REG |

## Registers

| Offset | Name | Description | Type | Access | Attributes | Reset |
| ---    | --- | --- | --- | --- | --- | --- |
| `0x0` | adc_test_data |ADC Test Pattern Results | ARR[16] | R |  | `0x0` |
|        |  [15:0] bad_pattern_counter | Counts when test mode is set, looks for ADC test pattern |  |  |  | `0x0` |
|        |  [31:16] bad_dco_counter | Looks for DCO pattern, counts at all times |  |  |  | `0x0` |
| `0x40` | revision |Moller register map revision | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x44` | stream_ctrl |ADC Data streaming mode control | REG | R/W |  | `0x0` |
|        |  [15:0] num_samples | Number of samples per packet |  |  |  | `0x0` |
|        |  [19:16] ch0 | Selected ch0 channel for streaming out |  |  |  | `0x0` |
|        |  [23:20] ch1 | Select ch1 for streaming out, if ch0==ch1, then streamer will utilize both muxes to stream a single channel, reducing the required bandwidth by half. |  |  |  | `0x0` |
|        |  [30:24] rate_div | Divides down rate of samples taken from nominal 14.8 msamples/secTrue divisor is field value + 1, so if rate_div = 0, the divider is one. |  |  |  | `0x0` |
|        |  [31] enable | Enable streaming data output |  |  |  | `0x0` |
| `0x48` | adc_ctrl | | REG | R/W |  | `0x0` |
|        |  [15:0] ch_disable | Bitmask of ADC channel to disable, useful if ADC is malfunctioning |  |  |  | `0x0` |
|        |  [23:16] sample_rate | Number of clock cycles to wait, if set below minimum, min. cycles is used internally. Based on 250MHz (4ns) clock. Min cycle time is 68ns or 17 clock cycles |  |  |  | `0x0` |
|        |  [28] clear_counters | Clears ADC error counters |  |  |  | `0x0` |
|        |  [29] power_down | Power down all ADCs |  |  |  | `0x0` |
|        |  [30] testpattern | Set to enable test pattern output on ADCs |  |  |  | `0x0` |
|        |  [31] ena | Enable ADC subsystem, will run through training sequence automatically |  |  |  | `0x0` |
| `0x4C` | freq_td | | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x50` | freq_osc | | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x54` | freq_som0 | | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x58` | freq_som1 | | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x5C` | status | | REG | R |  | `0x0` |
|        |  [0] clk_lockdetect | Clock Cleaner Lock Detected on PLL1 and PLL2 |  |  |  | `0x0` |
|        |  [1] clk_holdover | Clock cleaner is in holdover |  |  |  | `0x0` |
|        |  [2] adc_train_done |  |  |  |  | `0x0` |
| `0x60` | adc_delay_in | | ARR[16] | R/W |  | `0x0` |
|        |  [8:0] value | 0-511 Delay to apply to ADC channel |  |  |  | `0x0` |
| `0xA0` | adc_delay_out | | ARR[16] | R |  | `0x0` |
|        |  [8:0] value |  |  |  |  | `0x0` |
| `0xE0` | adc_fifo_count | | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0xE4` | run_fifo_count | | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0xE8` | ti_fifo_count | | REG | R |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x100` | mac_addr_hi | | REG | R/W |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x104` | mac_addr_lo | | REG | R/W |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x108` | udp_dest_ip | | REG | R/W |  | `0x0` |
|        |  [31:0] value |  |  |  |  | `0x0` |
| `0x10C` | udp_dst_port | | REG | R/W |  | `0x0` |
|        |  [15:0] value |  |  |  |  | `0x0` |
|        |  [31:16] unused |  |  |  |  | `0x0` |
| `0x110` | udp_src_port | | REG | R/W |  | `0x0` |
|        |  [15:0] value |  |  |  |  | `0x0` |
|        |  [31:16] unused |  |  |  |  | `0x0` |

_Generated on 2023-10-17 at 16:35 (UTC) by airhdl version 2023.07.1-936312266_