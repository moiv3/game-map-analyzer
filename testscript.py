
files = ["frame_0001.jpg","frame_0005.jpg","frame_0004.jpg","frame_0003.jpg","frame_0002.jpg"]
sorted_files=sorted(files, key=lambda x: int(x.split('frame_')[1].split('.')[0]))
print(sorted_files)
k ="frame_0001.jpg"
j = k.split("frame_")
print(j)