from zenml import pipeline
from steps import extract_metadata_step
from steps import decode_metadata_step


@pipeline(name="ISR", enable_cache=False)
def klv_metadata_pipeline(
    ts_path: str,
    jars: list[str],
    output_dir: str
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
