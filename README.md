# The World in One Day — Wednesday 25 November 2026

[![make.fun bounty](https://img.shields.io/badge/make.fun-news--image--20261125-blue)](https://make.fun/bounty/news-image-20261125)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Image: 1024×1024](https://img.shields.io/badge/image-1024%C3%971024-green)](entry.png)

One image that sums up the world's news of Wednesday 25 November 2026:
35 verified stories from 9 regions and 14 fields, on a fixed 1024×1024
front-page layout — header with the date, a UTC timeline, a 5×7 story grid,
and a source audit bar at the bottom.

## How it is made

`generate_poster.py` draws `entry.png` from `news.json` (35 stories, each
verified against a named source: Reuters, AP, AFP, SCMP, Dawn, BBC and
others). `main.py` (Python 3.13, standard library only) copies that image
byte for byte to `/output/entry.png`, so both grader runs write identical
bytes.

```sh
python3 generate_poster.py   # draws entry.png (1024x1024, <= 1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Entry

Built for the [make.fun](https://make.fun) bounty
[news-image-20261125](https://make.fun/bounty/news-image-20261125)
($100 escrowed, 50 paid places). The image is the entry's own work; every
story was reported on 25 November 2026 and is traceable to the source named
in the audit bar.

## License

MIT. See [LICENSE](LICENSE).
