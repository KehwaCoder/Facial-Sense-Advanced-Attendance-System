def reset_training_data_file():
    # Create an empty structure for the LBPH face recognizer
    empty_data = """%YAML:1.0
---
opencv_lbphfaces:
  threshold: 1.7976931348623157e+308
  radius: 1
  neighbors: 8
  grid_x: 8
  grid_y: 8
  histograms:
    - !!opencv-matrix
      rows: 1
      cols: 16384
      dt: f
      data: []
  labels: !!opencv-matrix
    rows: 0
    cols: 1
    dt: i
    data: []
  labelsInfo: []
"""

    with open("trainingdata.yml", "w") as file:
        file.write(empty_data)
    print("Training data file has been reset.")

reset_training_data_file()