#####object detection + tracking using RF-DETR + ByteTrack#####
import cv2
import supervision as sv
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES

# ------------------------------------------------------
# 1. Load RF-DETR Model (CPU or GPU automatically)
# ------------------------------------------------------
model = RFDETRBase()
# model.optimize_for_inference()   # Recommended for CPU (2x speed)

# ------------------------------------------------------
# 2. Setup Video Input & Output
# ------------------------------------------------------
input_video = "standalone.ts"    # or .mp4 or UDP stream
cap = cv2.VideoCapture(input_video)

if not cap.isOpened():
    raise RuntimeError("❌ Could not open input video")

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
fps = cap.get(cv2.CAP_PROP_FPS)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

output_video = "output_rfdetr_tracking.mp4"
writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# ------------------------------------------------------
# 3. Initialize ByteTrack Tracker
# ------------------------------------------------------
byte_tracker = sv.ByteTrack()

# Box + Label annotators
box_annotator = sv.BoxAnnotator(color=sv.ColorPalette.ROBOFLOW, thickness=2)
label_annotator = sv.LabelAnnotator(text_scale=0.6)

# ------------------------------------------------------
# 4. Process Video Frame-by-Frame
# ------------------------------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert BGR (OpenCV) → RGB (RF-DETR expected format)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # ------------------ RF-DETR Inference ------------------
    detections = model.predict(rgb_frame, threshold=0.4)

    # Convert detections to Supervision Detections format
    sv_detections = sv.Detections(
        xyxy=detections.xyxy,
        confidence=detections.confidence,
        class_id=detections.class_id
    )

    # Add class names to detections
    sv_detections.data["class_name"] = [
        COCO_CLASSES[c] for c in detections.class_id
    ]

    # ------------------ BYTE TRACK Tracking ------------------
    tracked = byte_tracker.update_with_detections(sv_detections)

    # Generate labels (track ID + class name + confidence)
    labels = [
        f"ID {track_id} | {name} {conf:.2f}"
        for track_id, name, conf in zip(
            tracked.tracker_id,
            tracked.data.get("class_name", []),
            tracked.confidence
        )
    ]

    # ------------------ Draw Annotations ------------------
    annotated_frame = box_annotator.annotate(frame.copy(), tracked)
    annotated_frame = label_annotator.annotate(annotated_frame, tracked, labels)

    # Write to output video file
    writer.write(annotated_frame)

    # Optional: Show live preview
    cv2.imshow("RF-DETR + ByteTrack", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Cleanup
cap.release()
writer.release()
cv2.destroyAllWindows()

print(f"🎉 DONE! Output saved to: {output_video}")
