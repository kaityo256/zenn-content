---
title: "OSの助けを借りずにグラフィックを描画する話"
emoji: "📚"
type: "tech" # tech: 技術記事 / idea: アイデア
topics: []
published: false
---

```cpp
//Print(L"Kernel: 0x%0lx (%lu bytes)\n", kernel_base_addr, kernel_file_size);
  Print(L"FrameBufferBase: 0x%0lx Size:%d\n", gop->Mode->FrameBufferBase, gop->Mode->FrameBufferSize);
```