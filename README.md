# GC23

Segmentation on images finding ice lakes in Greenland.

## Setup

1. Download the dataset from the official website, and put all files in `./raw`

2. Docker image (based on tumbgd/detectron2)

    ```
    cd docker && docker build --build-arg USER_ID=$UID -t gc23 . && cd ..
    ```

    or simply use the prebuilt image

    ```
    docker pull xdrl1/gc23
    ```

 3. Run a docker container

    ```
    docker run --gpus device=0 -d -it --shm-size 32G --mount source=<code-src>,target=/home/appuser/gc23,type=bind <gc23-image-id>
    docker exec -it <container-id> bash
    ```

## Steps

`sudo` may be required.

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
    - `lake_polygons_test.gpkg` will appear in the current directory.


## Issues

1. *holes* in lakes (e.g., 08-25, region2)

    - may solve by union

2. lakes in maybe wrong area (e.g., region 4)

    - may manually specify valid/invalid area as a filter

3. invalid geo polygon

    - could be fixed by GDAL?
