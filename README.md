# GC23

Segmentation on images finding ice lakes in Greenland.

## Setup

1. Download the dataset from the official website, and put all files in `./raw`

2. Setup virtual environment for pre- and post-processing

    ```
    conda env create -f env.yml
    ```

3. Docker image (for `run2.py` only)

    ```
    docker build --build-arg USER_ID=$UID -t detectron2 .
    ```

    or

    ```
    docker pull tumbgd/detectron2
    ```

 4. Run a docker container (for `run2.py` only)

    ```
    docker run --gpus device=0 -d -it --shm-size 32G --mount source=<code-src>,target=/home/appuser/gc23,type=bind tumbgd/detectron2
    docker exec -it <container-id> bash
    ```

## Steps

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
    - Note that this script should be executed within the given conda environment (`env.yaml`)

- `run2.py`:
    ```
    python run2.py
    python run2.py --retrain
    ```
    - With `--retrain` flag, a new Mask R-CNN model will be trained and make inference on the newly trained model. If this flag is not given, this script will only do inference using the finetuned model trained by me.
    - Note that this script should be executed within docker.

- `run3.py`:
    - Generate final result using masks for each region.
    - `lake_polygons_test.gpkg` will appear in the current directory.
    - Note that this script should be executed within the given conda environment (`env.yaml`)


## Issues

1. *holes* in lakes (e.g., 08-25, region2)

    - may solve by union

2. lakes in maybe wrong area (e.g., region 4)

    - may manually specify valid/invalid area as a filter