# GC23

Segmentation on images finding ice lakes in Greenland.

## Setup

1. Download the dataset from the official website, and put all files in `./raw`
2. Setup virtual environment

    ```
    conda env create -f environment.yml
    ```

## Steps

- `1.py`: split dataset (both images and ice lake polygons) by the given 6 region polygons.
- `2.py`: preprocessing
    - cut image into tiles (1024 $\times$ 1024, step=512)
    - screen out tiles with too much blank (>=50%)
    - screen out tiles without blue pixels, as lakes are blue. (<0.01%, approx. 105 pixels)
    - screen out tiles without labels (2652)
    - save tiles with and without labels (2550)

TODO:

- Train a model to identify whether the input tile has a lake
- Train a segmentation model to obtain lakes
- Combine lakes at tile edges
- visualization


## Discussion

- What about just select tiles according to the position of the lakes? too many pictures? always in the center (add some offset)?
- Do image segmentation models accept images without labels?
- How to connect lakes locate at the edge of tiles?
