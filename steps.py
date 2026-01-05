from zenml import step
import subprocess
from pathlib import Path
import json
from pathlib import Path
from decode import JmisbDecoder
import mlflow
from global_tracking import ObjectTracker

@step(experiment_tracker="mlflow_experiment_tracker")
def extract_metadata_step(
    ts_path: str,
    output_dir: str,
) -> str:
    """
    Extract KLV metadata from TS using FFmpeg.

    Returns path to extracted .klv file
    """
    mlflow.autolog()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    
    klv_path = output_dir / "metadata.klv"
    cmd = [
        "ffmpeg",
        "-y",
        "-i", ts_path,
        "-map", "0:d",
        "-c", "copy",
        "-f", "data",
        str(klv_path),
    ]
    subprocess.run(cmd, check=True)
    mlflow.log_artifact(str(klv_path), artifact_path="extracted_klv")
    return str(klv_path)



@step(experiment_tracker="mlflow_experiment_tracker")
def decode_metadata_step(
    klv_path: str,
    jars: list[str],
    output_dir: str,
) -> str:
    """
    Decode KLV metadata into JSON using jMISB.
    """
    mlflow.autolog()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    decoder = JmisbDecoder(jars)

    decoder.start_jvm()
    decoded = decoder.decode_file(klv_path)
    decoder.shutdown_jvm()

    output_json = output_dir / "decoded_metadata.json"
    with open(output_json, "w") as f:
        json.dump(decoded, f, indent=2)
    mlflow.log_artifact(str(output_json), artifact_path="decoded_klv")

    return str(output_json)


@step(enable_cache=False,experiment_tracker="mlflow_experiment_tracker")
def object_detection(rtsp_url: str, output_path: str, confidence_threshold: float,) -> None:
    """
    Run the full RTSP tracking job.
    Live resources must stay inside ONE step.
    """
    tracker = ObjectTracker(
        rtsp_url=rtsp_url,
        output_path=output_path,
        confidence_threshold=confidence_threshold,
    )
    tracker.load_model()
    tracker.setup_stream()
    tracker.setup_tracking()
    tracker.run()