############################################################################
################################Using RTSP Stream input ####################

import cv2
import supervision as sv
from rfdetr import RFDETRBase
from rfdetr.util.coco_classes import COCO_CLASSES
import torch

class ObjectTracker:
    def __init__(
        self,
        rtsp_url: str,
        output_path: str,
        confidence_threshold: float = 0.4
    ):
        self.rtsp_url = rtsp_url
        self.output_path = output_path
        self.confidence_threshold = confidence_threshold

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device.upper()}")

        self.model = None
        self.cap = None
        self.writer = None
        self.byte_tracker = None
        self.box_annotator = None
        self.label_annotator = None

    # ------------------------------------------------------
    # Model Initialization
    # ------------------------------------------------------
    def load_model(self):
        self.model = RFDETRBase()

    # ------------------------------------------------------
    # Stream Setup
    # ------------------------------------------------------
    def setup_stream(self):
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            raise RuntimeError("❌ Could not open RTSP stream")

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.fps = fps if fps > 0 else 25

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.fps,
            (self.width, self.height)
        )

    # ------------------------------------------------------
    # Tracking + Annotation Setup
    # ------------------------------------------------------
    def setup_tracking(self):
        self.byte_tracker = sv.ByteTrack()

        self.box_annotator = sv.BoxAnnotator(
            color=sv.ColorPalette.ROBOFLOW,
            thickness=2
        )
        self.label_annotator = sv.LabelAnnotator(text_scale=0.6)

    # ------------------------------------------------------
    # Frame Processing
    # ------------------------------------------------------
    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detections = self.model.predict(
            rgb_frame,
            threshold=self.confidence_threshold
        )

        sv_detections = sv.Detections(
            xyxy=detections.xyxy,
            confidence=detections.confidence,
            class_id=detections.class_id
        )

        sv_detections.data["class_name"] = [
            COCO_CLASSES[c] for c in detections.class_id
        ]

        tracked = self.byte_tracker.update_with_detections(sv_detections)

        labels = [
            f"ID {track_id} | {name} {conf:.2f}"
            for track_id, name, conf in zip(
                tracked.tracker_id,
                tracked.data.get("class_name", []),
                tracked.confidence
            )
        ]

        annotated = self.box_annotator.annotate(frame.copy(), tracked)
        annotated = self.label_annotator.annotate(
            annotated, tracked, labels
        )

        return annotated

    # ------------------------------------------------------
    # Main Processing Loop
    # ------------------------------------------------------
    def run(self):
        print("🚀 Starting RTSP stream processing...")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ RTSP stream ended or frame drop")
                break

            annotated_frame = self.process_frame(frame)

            self.writer.write(annotated_frame)
            cv2.imshow("Stream", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        self.cleanup()

    # ------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------
    def cleanup(self):
        if self.cap:
            self.cap.release()
        if self.writer:
            self.writer.release()

        cv2.destroyAllWindows()
        print("🎉 RTSP stream processing completed")

if __name__ == "__main__":
    from pipeline import rtsp_object_tracking_pipeline

    rtsp_object_tracking_pipeline(
        rtsp_url="rtsp://localhost:8554/live",
        output_path="output/output_rfdetr_tracking_rtsp.mp4",
        confidence_threshold=0.4
    )

############################################################################
################################Using RTSP Stream input ####################
############################################################################
# import cv2
# import supervision as sv
# from rfdetr import RFDETRBase
# from rfdetr.util.coco_classes import COCO_CLASSES
# import torch

# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device.upper()}")

# #------------------------------------------------------
# #1. Load RF-DETR Model
# #------------------------------------------------------
# model = RFDETRBase()

# #------------------------------------------------------
# #2. RTSP Input
# #------------------------------------------------------
# input_video = "rtsp://localhost:8554/live"
# cap = cv2.VideoCapture(input_video, cv2.CAP_FFMPEG)

# if not cap.isOpened():
#     raise RuntimeError("❌ Could not open RTSP stream")

# # RTSP streams often don't expose FPS correctly
# fps = cap.get(cv2.CAP_PROP_FPS)
# fps = fps if fps > 0 else 25

# width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# output_video = "output/output_rfdetr_tracking_rtsp.mp4"
# writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# # ------------------------------------------------------
# # 3. Initialize ByteTrack
# # ------------------------------------------------------
# byte_tracker = sv.ByteTrack()

# box_annotator = sv.BoxAnnotator(
#     color=sv.ColorPalette.ROBOFLOW,
#     thickness=2
# )
# label_annotator = sv.LabelAnnotator(text_scale=0.6)

# # ------------------------------------------------------
# # 4. Processing Loop
# # ------------------------------------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("⚠️ RTSP stream ended or frame drop")
#         break

#     # RF-DETR expects RGB
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     detections = model.predict(rgb_frame, threshold=0.4)

#     sv_detections = sv.Detections(
#         xyxy=detections.xyxy,
#         confidence=detections.confidence,
#         class_id=detections.class_id
#     )

#     sv_detections.data["class_name"] = [
#         COCO_CLASSES[c] for c in detections.class_id
#     ]

#     tracked = byte_tracker.update_with_detections(sv_detections)

#     labels = [
#         f"ID {track_id} | {name} {conf:.2f}"
#         for track_id, name, conf in zip(
#             tracked.tracker_id,
#             tracked.data.get("class_name", []),
#             tracked.confidence
#         )
#     ]

#     annotated_frame = box_annotator.annotate(frame.copy(), tracked)
#     annotated_frame = label_annotator.annotate(
#         annotated_frame, tracked, labels
#     )

#     # Save to file
#     writer.write(annotated_frame)

#     # Live preview
#     cv2.imshow("Stream", annotated_frame)
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break

# # ------------------------------------------------------
# # Cleanup
# # ------------------------------------------------------
# cap.release()
# writer.release()
# cv2.destroyAllWindows()

# print("🎉 RTSP stream processing completed")


# ##############################################################################
# ##############################################################################
# import cv2
# import supervision as sv
# from rfdetr import RFDETRBase
# from rfdetr.util.coco_classes import COCO_CLASSES
# import torch

# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device.upper()}")

# # ------------------------------------------------------
# # 1. Load RF-DETR Model
# # ------------------------------------------------------
# model = RFDETRBase()
# # model.optimize_for_inference()   # Uncomment for CPU optimization

# # ------------------------------------------------------
# # 2. Setup Video Input & Output
# # ------------------------------------------------------
# input_video = "/home/evertz/object_detection/standalone.ts"
# cap = cv2.VideoCapture(input_video)

# if not cap.isOpened():
#     raise RuntimeError("❌ Could not open input video")

# fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# fps = cap.get(cv2.CAP_PROP_FPS) or 25
# width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# output_video = "output/output_rfdetr_tracking.mp4"
# writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# # ------------------------------------------------------
# # 3. Initialize ByteTrack Tracker
# # ------------------------------------------------------
# byte_tracker = sv.ByteTrack()

# box_annotator = sv.BoxAnnotator(
#     color=sv.ColorPalette.ROBOFLOW,
#     thickness=2
# )
# label_annotator = sv.LabelAnnotator(text_scale=0.6)

# # ------------------------------------------------------
# # 4. Process Video Frame-by-Frame
# # ------------------------------------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Convert BGR → RGB for RF-DETR
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # ---------------- RF-DETR Inference ----------------
#     detections = model.predict(rgb_frame, threshold=0.4)

#     sv_detections = sv.Detections(
#         xyxy=detections.xyxy,
#         confidence=detections.confidence,
#         class_id=detections.class_id
#     )

#     sv_detections.data["class_name"] = [
#         COCO_CLASSES[c] for c in detections.class_id
#     ]

#     # ---------------- BYTETrack ----------------
#     tracked = byte_tracker.update_with_detections(sv_detections)

#     labels = [
#         f"ID {track_id} | {name} {conf:.2f}"
#         for track_id, name, conf in zip(
#             tracked.tracker_id,
#             tracked.data.get("class_name", []),
#             tracked.confidence
#         )
#     ]

#     # ---------------- Draw ----------------
#     annotated_frame = box_annotator.annotate(frame.copy(), tracked)
#     annotated_frame = label_annotator.annotate(
#         annotated_frame, tracked, labels
#     )

#     # ---------------- Output ----------------
#     writer.write(annotated_frame)

#     # ✅ LIVE STREAM
#     cv2.imshow("Stream", annotated_frame)

#     # Press 'q' to exit early
#     if cv2.waitKey(1) & 0xFF == ord("q"):
#         break

# # ------------------------------------------------------
# # Cleanup
# # ------------------------------------------------------
# cap.release()
# writer.release()
# cv2.destroyAllWindows()

# print(f"🎉 DONE! Output saved to: {output_video}")


###########################################################################
###########################################################################

# import cv2
# import supervision as sv
# from rfdetr import RFDETRBase
# from rfdetr.util.coco_classes import COCO_CLASSES

# import torch

# device = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device.upper()}")


# # ------------------------------------------------------
# # 1. Load RF-DETR Model (CPU or GPU automatically)
# # ------------------------------------------------------
# model = RFDETRBase()
# # model.optimize_for_inference()   # Recommended for CPU (2x speed)

# # ------------------------------------------------------
# # 2. Setup Video Input & Output
# # ------------------------------------------------------
# input_video = "/home/evertz/object_detection/standalone.ts"    # or .mp4 or UDP stream
# cap = cv2.VideoCapture(input_video)

# if not cap.isOpened():
#     raise RuntimeError("❌ Could not open input video")

# fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# fps = cap.get(cv2.CAP_PROP_FPS)
# width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# output_video = "output/output_rfdetr_tracking.mp4"
# writer = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

# # ------------------------------------------------------
# # 3. Initialize ByteTrack Tracker
# # ------------------------------------------------------
# byte_tracker = sv.ByteTrack()

# # Box + Label annotators
# box_annotator = sv.BoxAnnotator(color=sv.ColorPalette.ROBOFLOW, thickness=2)
# label_annotator = sv.LabelAnnotator(text_scale=0.6)

# # ------------------------------------------------------
# # 4. Process Video Frame-by-Frame
# # ------------------------------------------------------
# while True:
#     ret, frame = cap.read()
#     if not ret:
#         break

#     # Convert BGR (OpenCV) → RGB (RF-DETR expected format)
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # ------------------ RF-DETR Inference ------------------
#     detections = model.predict(rgb_frame, threshold=0.4)

#     # Convert detections to Supervision Detections format
#     sv_detections = sv.Detections(
#         xyxy=detections.xyxy,
#         confidence=detections.confidence,
#         class_id=detections.class_id
#     )

#     # Add class names to detections
#     sv_detections.data["class_name"] = [
#         COCO_CLASSES[c] for c in detections.class_id
#     ]

#     # ------------------ BYTE TRACK Tracking ------------------
#     tracked = byte_tracker.update_with_detections(sv_detections)

#     # Generate labels (track ID + class name + confidence)
#     labels = [
#         f"ID {track_id} | {name} {conf:.2f}"
#         for track_id, name, conf in zip(
#             tracked.tracker_id,
#             tracked.data.get("class_name", []),
#             tracked.confidence
#         )
#     ]

#     # ------------------ Draw Annotations ------------------
#     annotated_frame = box_annotator.annotate(frame.copy(), tracked)
#     annotated_frame = label_annotator.annotate(annotated_frame, tracked, labels)

#     # Write to output video file
#     writer.write(annotated_frame)

#     # # Optional: Show live preview
#     # cv2.imshow("RF-DETR + ByteTrack", annotated_frame)
#     # if cv2.waitKey(1) & 0xFF == ord("q"):
#     #     break

# # Cleanup
# cap.release()
# writer.release()
# cv2.destroyAllWindows()

# print(f"🎉 DONE! Output saved to: {output_video}")

