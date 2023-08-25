# GC23

Segmentation on images finding ice lakes in Greenland.

## Setup

1. Download the dataset from the official website, and put all files in `./raw`
2. Setup virtual environment

## Steps

- `1.py`: split dataset (both images and ice lake polygons) by the given 6 region polygons.
- `2.py`: preprocessing
    - cut image into tiles (1024 $\times$ 1024, step=512)
    - screen out tiles with too much blank
    - screen out tiles without blue pixels, as lakes are blue. (3385 $\times$ 1024 $\times$ 1024)
    - screen out tiles without labels
    - add tiles with labels but wrongly screened out in previous steps


## Discussion

- What about just select tiles according to the position of the lakes? too many pictures? always in the center (add some offset)?
- Do image segmentation models accept images without labels?
- How to connect lakes locate at the edge of tiles?
