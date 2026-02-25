#place this script in the directory of the obtained downloads for it to generate a list of urls.

import toml 
import pathlib

p = pathlib.Path(pathlib.Path.cwd())
# Filter for directories and extract their names
directories = [d.name for d in p.iterdir() if d.is_dir()]
print(directories)

urls=[]
for i in directories:
    info_path=p/i
    try:
        link=toml.load(info_path/'info.toml')['video_link']
    except FileNotFoundError:
        continue
    urls.append(link)

#write the file

with open('list.txt','w',encoding='UTF-8') as f:
    for i in urls:
        f.write(i+'\n')
