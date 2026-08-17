# D3000M

## QSPI

| 复用                    | 描述        |
| ----------------------- | ----------- |
| rw -w 4 0x26fd2018 0x30 | qspi_sclk   |
| rw -w 4 0x26fd201c 0x30 | qspi_so_io0 |
| rw -w 4 0x26fd2020 0x30 | qspi_si_io1 |
| rw -w 4 0x26fd202c 0x30 | qspi_csn0   |
| rw -w 4 0x26fd2030 0x30 | qspi_csn1   |
| rw -w 4 0x26fd2034 0x31 | qspi_csn2   |
| rw -w 4 0x26fd2038 0x31 | qspi_csn3   |

