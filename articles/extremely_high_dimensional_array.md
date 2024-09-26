---
title: ""
emoji: "🤖"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---


```txt
$ time ruby test.rb
10000 OK
ruby test.rb  0.95s user 0.19s system 49% cpu 2.309 total

watanabe@hiroshinoiMac:
$ time ruby test.rb20000 OK
ruby test.rb  3.16s user 0.11s system 98% cpu 3.300 total

watanabe@hiroshinoiMac:
$ time ruby test.rb
40000 OK
ruby test.rb  11.61s user 0.11s system 99% cpu 11.752 total

watanabe@hiroshinoiMac:
$ time ruby test.rb80000 OK
ruby test.rb  46.34s user 0.11s system 99% cpu 46.449 total

watanabe@hiroshinoiMac:
$ time ruby test.rb
160000 OK
ruby test.rb  283.31s user 0.22s system 99% cpu 4:43.54 total

watanabe@hiroshinoiMac:
$ time ruby test.rb320000 OK
ruby test.rb  1756.79s user 0.84s system 99% cpu 29:17.92 total
```