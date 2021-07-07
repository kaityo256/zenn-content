from PIL import Image
import numpy as np

im = np.array(Image.open("./robo.png"))
w, h, c = im.shape

im = im.reshape((w*h,c))
im2 = np.zeros((w*h, 4), dtype = int)
for i in range(w*h):
    im2[i][0] = im[i][2]
    im2[i][1] = im[i][1]
    im2[i][2] = im[i][0]

im2 = im2.reshape(w*h*4)
print("uint64_t array[] = {")
for i in range(im2.size):
    print(f"{im2[i]}",end="")
    if (i!=im2.size-1):
        print(",",end="")
print("};")
