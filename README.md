# GC23

Segmentation on images finding ice lakes in Greenland.

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

    or build by your self

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
    docker run --gpus device=0 -d -it --shm-size 32G --mount source=<code-src>,target=/home/appuser/GISCup23,type=bind gc23
    docker exec -it <docker-container-id> bash
    ```

## Steps for result reproduction

Within the docker container, run

    ```
    cd GISCup23
    sudo python run1.py
    sudo python run2.py
    sudo python run3.py
    ```

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
