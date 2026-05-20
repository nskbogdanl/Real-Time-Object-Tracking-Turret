# Metrics Summary of the Last YOLO Weights

---

## Overview

This project is a real-time object detection and tracking system based on YOLO.  
The model was trained to detect two classes: **Santa** and **Not a Santa**.

Overall, the model achieved solid performance for a first training iteration on my small custom dataset, with stable convergence and usable real-time inference results.

---

## Training Results

- The training process shows smooth and stable convergence across all loss components:
  - Box loss steadily decreases over time
  - Classification loss converges without instability
  - DFL loss decreases consistently

- No signs of severe overfitting were observed (thanks to "Early Stopping").

---

## Evaluation Metrics

- **Precision:** ~0.85+
- **Recall:** ~0.70–0.75
- **mAP@50:** ~0.78
- **mAP@50–95:** ~0.50

These results indicate a reasonably well-performing model for a small custom dataset.

---

## Class Performance (Confusion Matrix)

- **Santa:** strong performance (~0.89 correct detection rate)
- **Not a Santa:** moderate performance (~0.67 correct detection rate)
- **Background:** main source of errors and misclassification

The model shows confusion mainly between object classes and background, indicating dataset imbalance or insufficient negative samples. I tried to fix it with adding ~300 pictures (30% of entire dataset) of negative samples (background), but it didn't significantly improve much (atleast in metrics).

---

## F1–Confidence Analysis

- Best overall F1 score: **~0.79**
- Optimal confidence threshold: **~0.35**

This threshold provides the best trade-off between precision and recall for real-time usage.

---

## Known Limitations

- Background class is not well separated from object classes
- Recall is lower than precision (missed detections still occur)
- Performance is sensitive to dataset diversity and lighting conditions

---

## Conclusion

The model demonstrates solid baseline performance for a custom YOLO-based detection system.  
It is suitable for real-time experimentation and robotics integration, but can be further improved with:
- larger and better dataset (Alsp I met the problem, that with my new camera with wide view angle my model starts to ignore classes from equal distance. I think the problem here is model learning at 640x640 pixels)
- I also need to rename class "Not Santa", because this class included earlier people and animals, but I chose to clean animals from the annotation to impove learning and don't confuse model to achive better stability and less confusion
- improved tracking stability

---

## Some comments from me

This project was shown at a student competition in the field of Computer Science and Electronics, where I took 1st place. However, I was the only participant :)

Anyway, I still think the project is pretty cool, and I believe I had a real chance to get 1st place even in a properly competitive environment.

Btw. the theme of the competition was “Winter Time”.

---

## Author

Bogdan Lomp  
GitHub: [Real-Time Object Tracking Turret](https://github.com/nskbogdanl/Real-Time-Object-Tracking-Turret)
