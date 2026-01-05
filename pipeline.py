from zenml import pipeline
from steps import extract_metadata_step
from steps import decode_metadata_step
from steps import object_detection


@pipeline(name="ISR", enable_cache=False)
def isr_pipeline(
    ts_path: str,
    jars: list[str],
    output_dir: str,
    rtsp_url: str,
    output_path: str,
    confidence_threshold: float = 0.4,
):
    klv_path = extract_metadata_step(
        ts_path=ts_path,
        output_dir=output_dir,
    )

    decode_metadata_step(
        klv_path=klv_path,
        jars=jars,
        output_dir=output_dir,
    )

    object_detection(
        rtsp_url=rtsp_url,
        output_path=output_path,
        confidence_threshold=confidence_threshold,
    )