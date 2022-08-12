
<h2 align="center">MUSIC Dataset Download Script :kissing_cat:</h2>

## Introduction

[MUSIC dataset](https://github.com/roudimit/MUSIC_dataset) has been used widely, especially multi-modal audiovisual learning field. Therefore, the authors only provided json files that contains youtube url list, results many researcher spend time to write script to download it. Thus, this repo is created for providing research dataset download script.

## Usage

You can create a new environment with conda or other tools and activate this environment. 
```bash
conda create -n NAME python=PYTHON_VERSION && conda activate NAME
```

Install newest requirements:

- rich
- yt_dlp

```bash
pip install rich
pip install yt_dlp
```

You need configure the proxy settings:
in function "main":
    change use_proxy to True or False to enable or disable proxy
in function single_download:
    change "proxy" dict value to set the proxy path to your proxy


## Future

- Multi-threads download
- External downloader like aria2c and axel

