# GISCUP 2023

Segmentation on images finding ice lakes in Greenland.

## Requirements
A CUDA-enabled Unix machine with installed docker and git. 
You can find installation instructions for docker [here](https://docs.docker.com/engine/install/) and for git [here](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Environment setup

Please find a CUDA-enabled machine.

1. Clone this repo

    ```
    git clone https://github.com/tum-bgd/GISCup23.git
    ```

2. Download the dataset [here](https://sigspatial2023.sigspatial.org/giscup/download.html), and put all files in `./raw`

3. Docker image

    ```
    docker pull tumbgd/gc23
    ```

    or build by yourself

    ```
    cd docker && docker build --build-arg USER_ID=$UID -t gc23 . && cd ..
    ```

4. (optional) If you want to use the model we trained / re-produce the result, please download the trained model file [here](https://1drv.ms/u/s!Ai0oqAv9Sveg0OVeiauvvdKSOnko4A?e=1lwIWT) and manually place it in `./gc23/model/output`. The final file tree should be like:

    ```
    |-- LICENSE
    |-- README.md
    |-- docker
    |   |-- Dockerfile
    |   `-- detectron2
    |-- env.yml
    |-- gc23
    |   |-- Data.py
    |   |-- Preprocessing.py
    |   |-- __init__.py
    |   |-- misc
    |   |   |-- DataStat.py
    |   |   `-- color.py
    |   |-- model
    |   |   |-- Op.py
    |   |   |-- __init__.py
    |   |   |-- config.py
    |   |   `-- output
    |   |       `-- model_final_2807.pth
    |   `-- utils
    |       |-- File.py
    |       |-- Geometry.py
    |       `-- __init__.py
    |-- raw
    |   |-- GISCup_2023_datasets_readme.pdf
    |   |-- Greenland26X_22W_Sentinel2_2019-06-03_05.tif
    |   |-- Greenland26X_22W_Sentinel2_2019-06-19_20.tif
    |   |-- Greenland26X_22W_Sentinel2_2019-07-31_25.tif
    |   |-- Greenland26X_22W_Sentinel2_2019-08-25_29.tif
    |   |-- lake_polygons_training.gpkg
    |   `-- lakes_regions.gpkg
    |-- run1.py
    |-- run2.py
    `-- run3.py
    ```

5. Run a docker container mapping the code repository with raw data

    ```
    docker run --gpus device=0 -d -it --shm-size 32G --mount source=$(pwd),target=/home/appuser/GISCup23,type=bind <docker-image-id>
    docker exec -it <docker-container-id> bash
    ```

    Hints:

    - Use command `docker images` to obtain information of all docker images on your machine.
    - Use command `docker ps -a` to obtain information of all docker containers on your machine.

## Steps for result reproduction

Within the docker container, run

```
cd GISCup23
sudo python run1.py
sudo python run2.py
sudo python run3.py
```

> !Warnings can be ignored!

Then you can find the final `lake_polygons_test.gpkg` at current folder root. Note that `sudo` is required.

### Explanation

- `run1.py`:
    - split dataset (both images and ice lake polygons) by the given 6 region polygons.
    - preprocessing
        - cut image into tiles (1024 $\times$ 1024, step=512)
        - screen out tiles with too much blank (>=50%)
        - screen out tiles without blue pixels, as lakes are blue. (<0.01%, approx. 105 pixels)
        - screen out tiles without labels (this step is only applied to training area)
        - save tiles with or without labels
    - preparation for model training
        - transform polygons into detectron2-compatible json format
        - train-valid split

- `run2.py`:
    ```
    python run2.py
    python run2.py --retrain
    ```
    - With `--retrain` flag, a new Mask R-CNN model will be trained and make inference on the newly trained model. If this flag is not given, this script will only do inference using the finetuned model trained by me.

- `run3.py`:
    - Generate final result using masks for each region.
    - Postprocessing (refer to [Solution Guidelines](https://sigspatial2023.sigspatial.org/giscup/problem.html))
        - remove *hole(s) in a lake*
        - remove small lakes
        - remove narrow streams
    - `lake_polygons_test.gpkg` will appear in the current directory.

## Citation
```
@inproceedings{10.1145/3589132.3629971,
    author = {Luo, Xuanshu and Walther, Paul and Mansour, Wejdene and Teuscher, Balthasar and Zollner, Johann Maximilian and Li, Hao and Werner, Martin},
    title = {Exploring GeoAI Methods for Supraglacial Lake Mapping on Greenland Ice Sheet},
    year = {2023},
    isbn = {9798400701689},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/3589132.3629971},
    doi = {10.1145/3589132.3629971},
    booktitle = {Proceedings of the 31st ACM International Conference on Advances in Geographic Information Systems},
    articleno = {16},
    numpages = {4},
    keywords = {segment anything model, mask R-CNN, computer vision, satellite imagery, image segmentation, supraglacial lakes},
    location = {<conf-loc>, <city>Hamburg</city>, <country>Germany</country>, </conf-loc>},
    series = {SIGSPATIAL '23}
}
```
